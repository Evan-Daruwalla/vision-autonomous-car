/* Pack low-voltage cutoff — closes the safety gap found in Appendix BI.
 *
 * WHY THIS EXISTS. docs/BOM.md row 11's board is titled "BMS" but Adeept
 * documents only over-VOLTAGE and short-circuit protection; over-discharge is
 * not listed, and the EVE 25P cells in row 9 are bare. So nothing in the BOM
 * stops the 2S pack being run flat under motor load. Below ~2.5 V/cell lithium
 * takes permanent capacity loss and can grow internal copper shunts that become
 * a fire risk on the NEXT charge. This is the firmware half of Verify item 6.
 *
 * MEASUREMENT
 *   Divider R1=100k (pack+ to A0), R2=12k (A0 to GND), ratio 0.10714.
 *   Reference: INTERNAL 1.1 V band gap, NOT the 5 V rail.
 *   ^ This is the load-bearing choice. The Uno's 5 V comes from the LM2596,
 *     which is the same supply that sags when the pack sags — measuring the
 *     pack against a reference that moves with it gives a meter that lies
 *     exactly when it matters. The band gap is supply-independent.
 *   8.4 V (full) -> 0.900 V -> 837 counts, 18% under the 1.1 V ceiling, which
 *   survives 5% resistor tolerance (worst case 0.984 V). 10.0 mV of pack per
 *   count, against thresholds 400 mV apart.
 *   Divider drain 75 uA = 1.8 mAh/day against a 2500 mAh cell.
 *
 * STATES
 *   OK        >= WARN_MV
 *   WARN      < WARN_MV      — report it, do not cut. Voltage sags under motor
 *                              stall; cutting on a transient makes the car
 *                              undriveable for no safety gain.
 *   CUTOFF    < CUTOFF_MV sustained for CUTOFF_HOLD_MS. **LATCHED.**
 *   FAULT     < FAULT_MV **or > FAULT_HI_MV** — implausible for a connected 2S
 *                          pack either way, so this is a wiring fault, not a
 *                          battery reading.
 *
 * WHY FAULT IS A SEPARATE STATE. A floating A0 does not read zero. If low
 * readings simply meant "cut", an unwired divider would latch cutoff and the car
 * would never drive, with no way to tell that from a genuinely dead pack. A
 * guard that cannot tell "broken" from "triggered" is not a guard. FAULT also
 * inhibits throttle — it is not safe to drive blind — but reports differently
 * so it is diagnosable.
 *
 * WHY THERE IS AN UPPER FAULT BAND, found by testing rather than by design:
 * with nothing wired to A0 the first build of this reported **10248 mV** — the
 * floating pin sits near full scale (1.1 V / 0.10714 = 10.27 V max readable).
 * That is ABOVE a full 2S pack (8.4 V), so it sailed past a low-only fault check
 * and read as a healthy battery: the guard would have allowed throttle with no
 * sensor attached. Anything above 8.8 V means an unwired or miswired divider,
 * the wrong resistors, or a pack that is not 2S. All are faults.
 *
 * WHY THE LATCH NEVER CLEARS ITSELF. With throttle cut, the pack recovers a few
 * hundred mV and would cross back above the threshold, re-enable, sag, and
 * oscillate — cycling the motor on a pack that is already too flat. Clearing
 * requires an explicit `CLEAR` command AND the pack above RECOVER_MV.
 *
 * NOT TESTED ON A REAL PACK. Nothing is ordered; no battery exists. The state
 * machine is verified on the real board by INJECTING voltages over serial
 * (`SIM <mv>`), which exercises every transition. The divider itself, and the
 * ADC's real behaviour, are UNVERIFIED until hardware exists.
 *
 * Serial 115200. Commands: SIM <mv> | REAL | CLEAR | STATUS | SELFTEST
 */
#include <Arduino.h>

const uint8_t  PIN_PACK   = A0;
const uint8_t  PIN_LED    = LED_BUILTIN;

// Divider and reference, as computed above.
const uint32_t R_TOP_OHM  = 100000UL;
const uint32_t R_BOT_OHM  = 12000UL;
const uint32_t VREF_MV    = 1100UL;      // internal band gap, nominal

// Thresholds, in millivolts AT THE PACK. 2S lithium.
const uint16_t WARN_MV    = 6400;        // 3.20 V/cell — report only
const uint16_t CUTOFF_MV  = 6000;        // 3.00 V/cell — cut, latched
const uint16_t RECOVER_MV = 6800;        // 3.40 V/cell — needed to CLEAR
const uint16_t FAULT_MV   = 4000;        // 2.00 V/cell — implausibly LOW; unwired
const uint16_t FAULT_HI_MV = 8800;       // above ANY charged 2S pack (8.4 V max)
                                         // — implausibly HIGH; see header
const uint16_t CUTOFF_HOLD_MS = 500;     // must persist; ignores stall dips

enum PackState { PACK_OK = 0, PACK_WARN = 1, PACK_CUTOFF = 2, PACK_FAULT = 3 };
const char *STATE_NAME[] = { "OK", "WARN", "CUTOFF", "FAULT" };

PackState state = PACK_OK;
bool      latched = false;
uint32_t  belowSince = 0;
bool      simMode = false;
uint16_t  simMv = 7400;

uint16_t readPackMv() {
  if (simMode) return simMv;
  uint32_t acc = 0;
  for (uint8_t i = 0; i < 16; i++) acc += analogRead(PIN_PACK);   // 16x average
  uint32_t counts = acc / 16;
  // counts -> mV at ADC -> mV at pack
  uint32_t adcMv = (counts * VREF_MV) / 1023UL;
  return (uint16_t)((adcMv * (R_TOP_OHM + R_BOT_OHM)) / R_BOT_OHM);
}

// Pure state transition, so SELFTEST exercises exactly the shipping logic.
PackState step(uint16_t mv, uint32_t now) {
  if (mv < FAULT_MV || mv > FAULT_HI_MV) { belowSince = 0; return PACK_FAULT; }
  if (latched) return PACK_CUTOFF;
  if (mv < CUTOFF_MV) {
    if (belowSince == 0) belowSince = now;
    if (now - belowSince >= CUTOFF_HOLD_MS) { latched = true; return PACK_CUTOFF; }
    return PACK_WARN;                    // below cutoff but not yet sustained
  }
  belowSince = 0;
  return (mv < WARN_MV) ? PACK_WARN : PACK_OK;
}

bool throttleInhibited() { return state == PACK_CUTOFF || state == PACK_FAULT; }

void report() {
  Serial.print(F("PACK ")); Serial.print(STATE_NAME[state]);
  Serial.print(F(" mv=")); Serial.print(readPackMv());
  Serial.print(F(" latched=")); Serial.print(latched ? 1 : 0);
  Serial.print(F(" throttle=")); Serial.print(throttleInhibited() ? F("INHIBITED") : F("allowed"));
  Serial.print(F(" mode=")); Serial.println(simMode ? F("SIM") : F("REAL"));
}

/* Drive the real state machine through every transition with injected values.
 * Runs on the board, against the shipping code, with no battery. */
void selftest() {
  uint8_t pass = 0, fail = 0;
  bool savedSim = simMode; uint16_t savedMv = simMv;
  #define CHECK(c, d) do { if (c) pass++; else { fail++; \
      Serial.print(F("  FAIL: ")); Serial.println(F(d)); } } while (0)

  simMode = true;
  latched = false; belowSince = 0;

  CHECK(step(7400, 1000) == PACK_OK,      "7.4V is OK");
  CHECK(step(8400, 1000) == PACK_OK,      "8.4V full is OK");
  CHECK(step(6500, 1000) == PACK_OK,      "just above warn is OK");
  CHECK(step(6300, 1000) == PACK_WARN,    "below warn is WARN");
  CHECK(!latched,                          "WARN must not latch");

  // below cutoff but NOT yet sustained -> WARN, no latch. This is the motor
  // stall dip, and cutting here would be a false trip.
  latched = false; belowSince = 0;
  CHECK(step(5900, 10000) == PACK_WARN,   "brief dip below cutoff is not a cut");
  CHECK(step(5900, 10200) == PACK_WARN,   "still not sustained at 200ms");
  CHECK(!latched,                          "must not latch before hold time");
  CHECK(step(5900, 10500) == PACK_CUTOFF, "sustained 500ms latches CUTOFF");
  CHECK(latched,                           "latch must be set");

  // recovery must NOT be automatic
  CHECK(step(7400, 11000) == PACK_CUTOFF, "recovered voltage must stay latched");
  CHECK(step(8400, 12000) == PACK_CUTOFF, "even a full pack stays latched");

  // a dip that recovers before the hold expires must reset the timer
  latched = false; belowSince = 0;
  step(5900, 20000);
  CHECK(step(7000, 20200) == PACK_OK,     "recovery clears the pending timer");
  CHECK(step(5900, 20400) == PACK_WARN,   "timer restarted, not resumed");
  CHECK(step(5900, 20800) == PACK_WARN,   "400ms since restart is not yet 500");
  CHECK(!latched,                          "must not latch on a restarted timer");

  // FAULT is distinct from CUTOFF and does not latch
  latched = false; belowSince = 0;
  CHECK(step(3000, 30000) == PACK_FAULT,  "implausibly low reads as FAULT");
  CHECK(!latched,                          "FAULT must not set the cutoff latch");
  CHECK(step(0, 30000)    == PACK_FAULT,  "0V is FAULT, not CUTOFF");
  // the case a real board actually produces: floating A0 near full scale
  CHECK(step(10248, 30000) == PACK_FAULT, "floating A0 (10248mV, measured) is FAULT");
  CHECK(step(8900, 30000)  == PACK_FAULT, "above any 2S pack is FAULT");
  CHECK(step(8400, 30000)  == PACK_OK,    "a genuinely full 2S pack is still OK");
  CHECK(step(7400, 30100) == PACK_OK,     "FAULT clears when a sane reading returns");

  // both inhibiting states actually inhibit
  state = PACK_CUTOFF; CHECK(throttleInhibited(),  "CUTOFF inhibits throttle");
  state = PACK_FAULT;  CHECK(throttleInhibited(),  "FAULT inhibits throttle");
  state = PACK_WARN;   CHECK(!throttleInhibited(), "WARN does NOT inhibit");
  state = PACK_OK;     CHECK(!throttleInhibited(), "OK does not inhibit");

  simMode = savedSim; simMv = savedMv; latched = false; belowSince = 0; state = PACK_OK;
  Serial.print(F("SELFTEST ")); Serial.print(fail ? F("FAIL ") : F("PASS "));
  Serial.print(pass); Serial.print('/'); Serial.println(pass + fail);
  #undef CHECK
}

char buf[24];
uint8_t blen = 0;

void handleLine() {
  buf[blen] = 0;
  if (!strncmp(buf, "SIM ", 4))      { simMode = true; simMv = atoi(buf + 4); report(); }
  else if (!strcmp(buf, "REAL"))     { simMode = false; report(); }
  else if (!strcmp(buf, "CLEAR")) {
    uint16_t mv = readPackMv();
    if (mv >= RECOVER_MV) { latched = false; belowSince = 0; state = PACK_OK;
                            Serial.println(F("CLEARED")); }
    else { Serial.print(F("REFUSED: need >= ")); Serial.print(RECOVER_MV);
           Serial.print(F(" mV, have ")); Serial.println(mv); }
  }
  else if (!strcmp(buf, "STATUS"))   report();
  else if (!strcmp(buf, "SELFTEST")) selftest();
  else if (blen)                     Serial.println(F("? SIM <mv>|REAL|CLEAR|STATUS|SELFTEST"));
  blen = 0;
}

void setup() {
  analogReference(INTERNAL);        // 1.1 V band gap — see header
  pinMode(PIN_PACK, INPUT);
  pinMode(PIN_LED, OUTPUT);
  Serial.begin(115200);
  delay(200);
  Serial.println(F("== UNO PACK GUARD =="));
  Serial.print(F("divider 100k/12k  warn=")); Serial.print(WARN_MV);
  Serial.print(F(" cutoff=")); Serial.print(CUTOFF_MV);
  Serial.print(F(" fault<")); Serial.print(FAULT_MV);
  Serial.print(F(" fault>")); Serial.print(FAULT_HI_MV);
  Serial.print(F(" hold=")); Serial.print(CUTOFF_HOLD_MS); Serial.println(F("ms"));
  selftest();
}

uint32_t lastReport = 0;
void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') { if (blen) handleLine(); }
    else if (blen < sizeof(buf) - 1) buf[blen++] = c;
  }
  uint32_t now = millis();
  PackState prev = state;
  state = step(readPackMv(), now);
  if (state != prev) report();

  // CUTOFF/FAULT flash the LED fast; WARN slow; OK steady-off.
  uint16_t period = throttleInhibited() ? 150 : (state == PACK_WARN ? 600 : 0);
  digitalWrite(PIN_LED, period ? ((now / period) & 1) : LOW);

  if (now - lastReport >= 5000) { lastReport = now; report(); }
}
