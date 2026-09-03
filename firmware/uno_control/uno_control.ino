/* uno_control — the actuation firmware. Implements firmware/SERIAL_PROTOCOL.md.
 *
 * Written 2026-09-02 (Appendix BO). This is the first firmware that drives
 * anything; uno_bringup/uno_memtest/uno_echo were measurements and
 * uno_packguard was one safety subsystem.
 *
 * VERIFIED ON THE BOARD, ACTUATORS UNWIRED. SELFTEST 49/49 on a real Uno;
 * firmware/host_test.py is the Pi-side gate (2026-09-02). The LINK and the
 * STATE MACHINE are tested; no motor, servo, encoder, LED or pack exists —
 * nothing in docs/BOM.md is ordered — so every actuator path is verified only
 * as a DECISION this firmware made, never as something that physically moved.
 *
 * DEFECT FIXED 2026-09-02 (found by the scheduled daily-audit, Appendix BY;
 * fix recorded in Appendix CA): loop() sampled millis() once at the top, then
 * handed handleFrame() a SECOND, later millis(); the watchdog compared the
 * stale sample against the fresher stamp, the unsigned subtraction wrapped,
 * and the watchdog tripped in the SAME iteration as every good frame — after
 * the reply had already been sent, so no status byte ever showed it. Effect
 * with a motor wired: drive ~2 ms, brake ~48 ms, repeat. Both timestamps now
 * come from the one sample. The test that catches it probes `armed` inside
 * the watchdog window (host_test.py); the status-bit check that seemed
 * obvious PASSES on the broken build, which is its own lesson.
 *
 * THE SAFETY MODEL, which is the point of this file:
 *   Four independent things can stop the car, and they do NOT share one code
 *   path. That was the defect in the design before 2026-09-02 — ARMED, the
 *   watchdog and the pack cutoff all acted by writing D11, so one stuck timer
 *   register defeated all three at once.
 *     1. ARMED bit, required in EVERY command frame (not a latched mode)
 *     2. 150 ms watchdog on command arrival
 *     3. pack low-voltage cutoff, latched (packguard.h)
 *     4. D10 -> TB6612 STBY, which removes the bridge outputs in HARDWARE
 *        regardless of what the PWM and DIR pins are doing
 *
 * BRAKE THEN COAST, and the order is forced by the TB6612 truth table:
 *   IN1=H IN2=H            -> short brake  (stops the car)
 *   IN1=L IN2=L, PWM=H     -> outputs OFF  (coasts)
 *   STBY=L                 -> outputs OFF  (coasts, whatever DIR says)
 * So STBY LOW IS A COAST, NOT A STOP. Dropping STBY as the safety action would
 * leave the car rolling. Entering any unsafe state therefore brakes with STBY
 * still high for BRAKE_MS, and only then drops STBY. See SERIAL_PROTOCOL.md 1a.
 *
 * BOOT STATE IS OFF, and it is free: Uno pins are high-Z until setup() runs and
 * the Pololu #713 pulls STBY low internally, so the driver is disabled through
 * every reset — including the reset caused by the Pi OPENING THE SERIAL PORT.
 * D10 is therefore raised only after the first valid ARMED frame, never in
 * setup(). Do not "helpfully" enable it earlier.
 *
 * Serial 115200, binary frames. A lone '?' outside a frame prints a
 * human-readable status line; 'T' runs SELFTEST; 'B' toggles bench-quiet (LED
 * only -- see benchQuiet). None is a valid sync byte.
 */
#include <Arduino.h>
#include <Servo.h>
#include "packguard.h"

// ---- pin map: firmware/SERIAL_PROTOCOL.md section 1 ------------------------
const uint8_t PIN_ENC_A  = 2;    // INT0
const uint8_t PIN_ENC_B  = 3;    // INT1 — nothing else may use D3
const uint8_t PIN_IND_L  = 4;
const uint8_t PIN_HEAD   = 5;    // Timer0 PWM
const uint8_t PIN_TAIL   = 6;    // Timer0 PWM
const uint8_t PIN_IND_R  = 7;
const uint8_t PIN_DIR_A  = 8;    // TB6612 AIN1+BIN1 (bridged: zero spare PWM)
const uint8_t PIN_SERVO  = 9;    // Servo claims Timer1
const uint8_t PIN_STBY   = 10;   // TB6612 STBY — master enable
const uint8_t PIN_MOTOR  = 11;   // Timer2 PWM
const uint8_t PIN_DIR_B  = 12;   // TB6612 AIN2+BIN2
const uint8_t PIN_STATUS = 13;

// ---- protocol --------------------------------------------------------------
const uint8_t SYNC_CMD = 0xA5;
const uint8_t SYNC_RPL = 0x5A;
const uint8_t CMD_LEN  = 7;
const uint8_t RPL_LEN  = 9;

// Declared HERE, above every function, and it must stay here. The Arduino
// preprocessor auto-generates function prototypes and inserts them near the top
// of the .ino, ABOVE anything you declare mid-file — so a function taking or
// returning a mid-file enum fails to compile with "'OutMode' does not name a
// type". Hit while compiling this file on 2026-09-02.
enum OutMode { OUT_DRIVE = 0, OUT_BRAKE = 1, OUT_OFF = 2 };

const uint16_t WATCHDOG_MS = 150;   // three missed frames at 20 Hz
const uint16_t BRAKE_MS    = 500;   // brake before coasting; see header

// Status bits. 0-3 are SERIAL_PROTOCOL.md v0.1; 4-5 are a v0.2 EXTENSION so the
// Pi can tell "throttle dead because the pack is flat" from "throttle dead
// because I stopped sending". Without it a cutoff is indistinguishable from a
// link fault, and the operator debugs the wrong thing.
const uint8_t ST_ARMED    = 0x01;
const uint8_t ST_WATCHDOG = 0x02;
const uint8_t ST_CRC_BAD  = 0x04;
const uint8_t ST_DROPPED  = 0x08;
const uint8_t ST_PACK_SHIFT = 4;    // 2 bits: PackState

// ---- actuator calibration --------------------------------------------------
/* THE PINION SWEEP IS MEASURED: ~180 degrees full-left to full-right (Evan,
 * 2026-09-02). That makes the span derivable instead of guessed.
 *
 * A standard hobby servo maps 1000-2000 us onto 180 degrees, i.e. 500 us per
 * 90 degrees. Centre-to-full-lock is half the sweep = 90 degrees = 500 us, so
 * the GEOMETRIC maximum is SERVO_US_SPAN = 500, and an MG90S at 180 degrees is
 * a 1:1 match to this rack with no gearing at all.
 *
 * THE OLD VALUE OF 300 WAS A REAL DEFECT, not just conservative: it reached
 * 54 of the 90 available degrees (60% of lock), giving ~19.2 degrees at the
 * road wheel against the measured 32, which is a turn radius 1.79x LARGER than
 * the mechanism can actually achieve. The car would have failed corners it is
 * geometrically capable of, and nothing would have said why.
 *
 * WHY 450 AND NOT 500. Servo centre and rack centre are aligned by hand at
 * assembly, and that alignment is unmeasured. At the full 500 any centring
 * error drives one side into a Lego hard stop, which stalls the servo and cooks
 * it. 450 keeps 10% of margin per side (81 of 90 degrees, ~28.8 degrees at the
 * road wheel, R = 1.819 x wheelbase).
 * shortcut: one symmetric span, no per-side trim. CEILING: it wastes lock on
 * whichever side has more clearance. UPGRADE TRIGGER: if bench centring cannot
 * get both stops within ~5 degrees, split this into LEFT and RIGHT limits.
 *
 * STILL UNVERIFIED: MG90S pulse range varies by unit (some are 500-2400 us for
 * 180 degrees, not 1000-2000). Confirm the real endpoints on the bench before
 * trusting 450, and never command full lock until you have. */
const uint16_t SERVO_US_CENTRE = 1500;
const uint16_t SERVO_US_SPAN   = 450;   // +/- from centre; 90% of measured lock
const uint16_t SERVO_US_SPAN_GEOMETRIC = 500;  // 100% of lock, for SELFTEST

// Duty cap: the N20 is a 6 V motor on a pack that reaches 8.4 V. 71% of full
// scale keeps mean voltage at ~6 V (docs/BOM.md row 5 reasoning).
const uint8_t MOTOR_DUTY_MAX = 181;     // 0.71 * 255

const uint8_t LIGHT_FULL = 255;
const uint8_t LIGHT_DIM  = 60;
const uint16_t BLINK_MS  = 340;         // ~1.5 Hz, each half

// ---- state -----------------------------------------------------------------
Servo    steerServo;
PackGuard pack;

volatile int32_t encTicks = 0;
volatile uint8_t encPrev  = 0;

uint8_t  rxBuf[CMD_LEN];
uint8_t  rxLen = 0;
uint32_t lastFrameMs = 0;
bool     everArmed   = false;      // gates the FIRST rise of STBY
bool     armed       = false;
uint32_t unsafeSince = 0;          // 0 = currently safe/driving
int8_t   lastSteer   = 0;          // watchdog HOLDS steering, does not centre
uint8_t  lastSeq     = 0;
uint8_t  statusBits  = 0;
uint8_t  loopDt      = 0;

/* QUIET STATUS LED ON A BENCH BOARD -- and why it is not just "stop flashing".
 *
 * A floating A0 reads ~10,248 mV (measured, Appendix BJ) and so does a sense
 * wire that has FALLEN OFF. In the instant those are the same reading, which
 * is the whole reason the upper fault band exists. Going quiet on sight of a
 * floating pin would also go quiet when the wire drops off a moving car --
 * the case the indicator exists for.
 *
 * They differ in HISTORY, though, and history is free: a board that has NEVER
 * seen a plausible pack was never wired (a bench), while a car whose wire
 * drops has seen one. pack.everPlausible carries that, so the common case --
 * this board, on a desk, with nothing attached -- is quiet automatically and
 * every power cycle, with no command to remember.
 *
 * 'B' remains as a manual override for the case history cannot cover: a board
 * that HAS seen a real pack and is now deliberately being benched.
 *
 * NEITHER PATH TOUCHES SAFETY. Throttle inhibit, STBY and outputModeFor() are
 * untouched -- the car stays exactly as disabled as it was, and SELFTEST
 * asserts that. Only PACK_FAULT (no sensor) is ever silenced; a latched
 * PACK_CUTOFF is a genuinely flat battery and keeps flashing regardless.
 * Neither is persisted: any reset clears both, and the Pi opening the serial
 * port resets the board.
 */
bool     benchQuiet  = false;

// ---- pure helpers: everything SELFTEST can check ---------------------------

uint8_t crc8(const uint8_t *d, uint8_t n) {
  // Bitwise, not a 256-byte table: at 20 Hz this costs microseconds, and the
  // Uno has 2048 B of SRAM to protect.
  uint8_t c = 0;
  while (n--) {
    c ^= *d++;
    for (uint8_t i = 0; i < 8; i++) c = (c & 0x80) ? (uint8_t)((c << 1) ^ 0x07) : (uint8_t)(c << 1);
  }
  return c;
}

uint16_t steerToUs(int8_t steer) {
  if (steer > 100) steer = 100;
  if (steer < -100) steer = -100;
  return (uint16_t)(SERVO_US_CENTRE + ((int32_t)steer * SERVO_US_SPAN) / 100);
}

uint8_t throttleToDuty(int8_t t) {
  int16_t a = t < 0 ? -(int16_t)t : (int16_t)t;
  if (a > 100) a = 100;
  return (uint8_t)((a * (int16_t)MOTOR_DUTY_MAX) / 100);
}

/* The whole safety decision, as a pure function of the four inputs, so
 * SELFTEST exercises the shipping logic rather than a copy of it — the same
 * discipline that made uno_packguard testable without a battery. */
OutMode outputModeFor(bool isArmed, bool packInhibit, bool wdTripped,
                      bool hasEverArmed, uint32_t msUnsafe) {
  if (!hasEverArmed) return OUT_OFF;                 // never enabled since boot
  if (isArmed && !packInhibit && !wdTripped) return OUT_DRIVE;
  return (msUnsafe < BRAKE_MS) ? OUT_BRAKE : OUT_OFF;
}

// ---- encoder ---------------------------------------------------------------
// 4x quadrature. Raw counts only: SERIAL_PROTOCOL.md section 6 makes converting
// ticks to distance the Pi's job, and counts-per-rev is unverified until the
// motor is in hand (#5159 is spec'd 12 CPR at the motor shaft, 29.86:1).
const int8_t QTAB[16] = { 0, -1, 1, 0,  1, 0, 0, -1,  -1, 0, 0, 1,  0, 1, -1, 0 };

/* OPEN: the SIGN is a convention, not a measurement. This table happens to
 * count the 00->01->11->10 cycle as NEGATIVE. Whether that is "forwards" for
 * this car depends on how the encoder sits on the motor and how the motor sits
 * in the drivetrain -- none of which exists yet. Flip this to -1 once the car
 * rolls forward and ticks go down. Discovered 2026-09-02 by a SELFTEST that
 * asserted a sign it could not know. */
const int8_t ENCODER_SIGN = +1;

void encISR() {
  uint8_t s = (uint8_t)((digitalRead(PIN_ENC_A) << 1) | digitalRead(PIN_ENC_B));
  encTicks += (int32_t)ENCODER_SIGN * QTAB[((encPrev << 2) | s) & 0x0F];
  encPrev = s;
}

int32_t readTicks() {
  noInterrupts();                 // int32 is four non-atomic bytes on an AVR
  int32_t t = encTicks;
  interrupts();
  return t;
}

// ---- actuator writes -------------------------------------------------------
void applyOutputs(OutMode mode, int8_t steer, int8_t throttle) {
  switch (mode) {
    case OUT_DRIVE:
      digitalWrite(PIN_STBY, HIGH);
      if (throttle == 0) {                       // explicit short brake
        digitalWrite(PIN_DIR_A, HIGH); digitalWrite(PIN_DIR_B, HIGH);
        analogWrite(PIN_MOTOR, 0);
      } else {
        digitalWrite(PIN_DIR_A, throttle > 0 ? HIGH : LOW);
        digitalWrite(PIN_DIR_B, throttle > 0 ? LOW  : HIGH);
        analogWrite(PIN_MOTOR, throttleToDuty(throttle));
      }
      break;
    case OUT_BRAKE:                              // STBY stays HIGH or it coasts
      digitalWrite(PIN_STBY, HIGH);
      digitalWrite(PIN_DIR_A, HIGH); digitalWrite(PIN_DIR_B, HIGH);
      analogWrite(PIN_MOTOR, 0);
      break;
    case OUT_OFF:
      analogWrite(PIN_MOTOR, 0);
      digitalWrite(PIN_DIR_A, LOW); digitalWrite(PIN_DIR_B, LOW);
      digitalWrite(PIN_STBY, LOW);               // hardware disable
      break;
  }
  steerServo.writeMicroseconds(steerToUs(steer));
}

void applyLights(uint8_t bits, bool hazard, uint32_t now) {
  bool dim = bits & 0x10;
  analogWrite(PIN_HEAD, (bits & 0x01) ? (dim ? LIGHT_DIM : LIGHT_FULL) : 0);
  analogWrite(PIN_TAIL, (bits & 0x02) ? (dim ? LIGHT_DIM : LIGHT_FULL) : 0);
  bool phase = (now / BLINK_MS) & 1;
  bool l = hazard ? phase : ((bits & 0x04) && phase);
  bool r = hazard ? phase : ((bits & 0x08) && phase);
  digitalWrite(PIN_IND_L, l);
  digitalWrite(PIN_IND_R, r);
}

// ---- reply -----------------------------------------------------------------
void sendReply(uint8_t seq, int32_t ticks, uint8_t status, uint8_t dt) {
  uint8_t r[RPL_LEN];
  r[0] = SYNC_RPL;
  r[1] = seq;
  r[2] = (uint8_t)(ticks      );
  r[3] = (uint8_t)(ticks >>  8);
  r[4] = (uint8_t)(ticks >> 16);
  r[5] = (uint8_t)(ticks >> 24);
  r[6] = status;
  r[7] = dt;
  r[8] = crc8(r, RPL_LEN - 1);
  Serial.write(r, RPL_LEN);
}

void printStatus() {
  Serial.print(F("? armed=")); Serial.print(armed);
  Serial.print(F(" everArmed=")); Serial.print(everArmed);
  Serial.print(F(" pack=")); Serial.print((int)pack.state);
  Serial.print(F(" mv=")); Serial.print(pack.readMv());
  Serial.print(F(" ticks=")); Serial.print(readTicks());
  Serial.print(F(" status=0x")); Serial.print(statusBits, HEX);
  Serial.print(F(" dt=")); Serial.print(loopDt);
  Serial.print(F(" stby=")); Serial.print(digitalRead(PIN_STBY));
  Serial.print(F(" benchQuiet=")); Serial.print(benchQuiet);
  Serial.print(F(" everPlausible=")); Serial.println(pack.everPlausible);
}

// ---- selftest --------------------------------------------------------------
void selftest() {
  uint8_t pass = 0, fail = 0;
  #define CHECK(c, d) do { if (c) pass++; else { fail++; \
      Serial.print(F("  FAIL: ")); Serial.println(F(d)); } } while (0)

  // CRC8/ATM, poly 0x07, init 0. Reference vector: "123456789" -> 0xF4.
  const uint8_t v[9] = {'1','2','3','4','5','6','7','8','9'};
  CHECK(crc8(v, 9) == 0xF4, "crc8 check vector 123456789 = 0xF4");
  uint8_t f[CMD_LEN] = { SYNC_CMD, 1, 0, 0, 0, 1, 0 };
  f[6] = crc8(f, CMD_LEN - 1);
  CHECK(crc8(f, CMD_LEN) == 0, "crc over a whole valid frame is 0");
  f[3] ^= 0xFF;
  CHECK(crc8(f, CMD_LEN) != 0, "a corrupted frame fails crc");

  // steering map
  CHECK(steerToUs(0)    == SERVO_US_CENTRE, "steer 0 is centre");
  CHECK(steerToUs(100)  == SERVO_US_CENTRE + SERVO_US_SPAN, "steer +100 is full right");
  CHECK(steerToUs(-100) == SERVO_US_CENTRE - SERVO_US_SPAN, "steer -100 is full left");
  CHECK(steerToUs(127)  == steerToUs(100),  "over-range steer clamps");
  /* Guards the defect fixed 2026-09-02: a span far under the measured lock
   * silently caps steering. The pinion sweeps 180 deg, so centre-to-lock is
   * 500 us; anything below ~85% of that is throwing away turning circle. */
  CHECK(SERVO_US_SPAN <= SERVO_US_SPAN_GEOMETRIC,
        "span must not exceed the measured mechanical lock");
  CHECK(SERVO_US_SPAN * 100 / SERVO_US_SPAN_GEOMETRIC >= 85,
        "span must reach >=85% of lock, or the car loses turning circle");
  CHECK(steerToUs(-128) == steerToUs(-100), "under-range steer clamps");

  // throttle map, including the duty cap that protects a 6V motor on 8.4V
  CHECK(throttleToDuty(0)    == 0,               "throttle 0 is zero duty");
  CHECK(throttleToDuty(100)  == MOTOR_DUTY_MAX,  "throttle 100 is the CAP, not 255");
  CHECK(throttleToDuty(-100) == MOTOR_DUTY_MAX,  "reverse uses magnitude");
  CHECK(throttleToDuty(127)  == MOTOR_DUTY_MAX,  "over-range throttle clamps");
  CHECK(MOTOR_DUTY_MAX < 255,                    "duty MUST be capped below full scale");

  // the safety decision
  CHECK(outputModeFor(true,  false, false, false, 0) == OUT_OFF,
        "before the first ARMED frame the driver stays OFF");
  CHECK(outputModeFor(true,  false, false, true,  0) == OUT_DRIVE,
        "armed, healthy, fed -> DRIVE");
  CHECK(outputModeFor(false, false, false, true,  0) == OUT_BRAKE,
        "disarm brakes FIRST");
  CHECK(outputModeFor(false, false, false, true,  BRAKE_MS) == OUT_OFF,
        "and coasts only after BRAKE_MS");
  CHECK(outputModeFor(true,  true,  false, true,  0) == OUT_BRAKE,
        "pack cutoff brakes even while armed");
  CHECK(outputModeFor(true,  false, true,  true,  0) == OUT_BRAKE,
        "watchdog brakes even while armed");
  CHECK(outputModeFor(true,  true,  false, true,  BRAKE_MS + 1) == OUT_OFF,
        "a sustained cutoff ends in hardware disable");
  CHECK(outputModeFor(true,  false, false, true,  9999) == OUT_DRIVE,
        "a healthy armed frame overrides a stale unsafe timer");

  // everPlausible: false until a sane 2S reading is seen, then sticky.
  PackGuard q; q.simMode = true;
  CHECK(!q.everPlausible,                 "everPlausible starts false");
  q.simMv = 10248; q.poll(1000);
  CHECK(!q.everPlausible,                 "a floating-pin reading is NOT plausible");
  CHECK(q.state == PACK_FAULT,            "...and still faults");
  q.simMv = 7400;  q.poll(2000);
  CHECK(q.everPlausible,                  "a real 2S reading sets it");
  q.simMv = 10248; q.poll(3000);
  CHECK(q.everPlausible,                  "it STAYS set - a wire that falls off after "
                                          "a good reading must still be loud");
  CHECK(q.state == PACK_FAULT,            "...and faults again");

  // bench-quiet is an LED concession and must never be a safety one.
  bool savedQuiet = benchQuiet;
  benchQuiet = true;
  CHECK(outputModeFor(true, true, false, true, 0) == OUT_BRAKE,
        "bench-quiet must NOT re-enable drive while the pack inhibits");
  CHECK(outputModeFor(true, true, false, true, BRAKE_MS + 1) == OUT_OFF,
        "bench-quiet must NOT keep STBY up through a sustained inhibit");
  // Silencing the watchdog BLINK must not silence the watchdog itself.
  CHECK(outputModeFor(false, false, true, true, 0) == OUT_BRAKE,
        "a watchdog trip still brakes even when its blink is suppressed");
  CHECK(outputModeFor(false, false, true, false, 0) == OUT_OFF,
        "...and before anything ever armed, the driver stays OFF");
  benchQuiet = savedQuiet;

  // pack guard — the transitions that matter, against the copied logic
  PackGuard g; g.simMode = true;
  CHECK(g.step(7400, 1000) == PACK_OK,     "7.4V is OK");
  CHECK(g.step(6300, 1000) == PACK_WARN,   "below warn is WARN");
  CHECK(g.step(5900, 10000) == PACK_WARN,  "brief dip is not a cut");
  CHECK(g.step(5900, 10500) == PACK_CUTOFF, "sustained 500ms latches");
  CHECK(g.step(8400, 12000) == PACK_CUTOFF, "latch survives a full pack");
  CHECK(g.step(10248, 13000) == PACK_FAULT, "a fault reading outranks the latch: FAULT names the real problem");
  CHECK(g.latched,                          "...but the latch SURVIVES underneath it");
  CHECK(g.step(7400, 14000) == PACK_CUTOFF, "so a sane reading returns to CUTOFF, not OK");
  PackGuard h; h.simMode = true;
  CHECK(h.step(10248, 100) == PACK_FAULT,  "floating A0 (10248mV measured) is FAULT");
  CHECK(!h.latched,                         "FAULT must not set the cutoff latch");
  h.state = PACK_FAULT; CHECK(h.inhibits(), "FAULT inhibits throttle");
  h.state = PACK_WARN;  CHECK(!h.inhibits(),"WARN does NOT inhibit");

  /* Quadrature. WHICH direction is "forward" is NOT knowable until the encoder
   * is on a motor and the motor is on the car, so asserting a sign here would be
   * asserting something unverifiable. Assert only what is true either way. */
  int8_t oneWay = 0, other = 0;
  const uint8_t seqf[5] = { 0, 1, 3, 2, 0 };          // the Gray cycle
  for (uint8_t i = 0; i < 4; i++) oneWay += QTAB[((seqf[i] << 2) | seqf[i + 1]) & 0x0F];
  for (uint8_t i = 4; i > 0; i--) other  += QTAB[((seqf[i] << 2) | seqf[i - 1]) & 0x0F];
  CHECK(oneWay == -other,        "the two directions are exact opposites");
  CHECK(oneWay == 4 || oneWay == -4, "one full cycle is 4 counts (4x decoding)");
  CHECK(QTAB[(0 << 2) | 3] == 0, "an illegal 2-bit jump counts 0, not a guess");
  bool antisym = true;                                 // the property, over ALL 16
  for (uint8_t a = 0; a < 4; a++)
    for (uint8_t b = 0; b < 4; b++)
      if (QTAB[(a << 2) | b] != -QTAB[(b << 2) | a]) antisym = false;
  CHECK(antisym, "QTAB is antisymmetric: reversing any transition negates it");

  Serial.print(F("SELFTEST ")); Serial.print(fail ? F("FAIL ") : F("PASS "));
  Serial.print(pass); Serial.print('/'); Serial.println(pass + fail);
  #undef CHECK
}

// ---- frame handling --------------------------------------------------------
void handleFrame(const uint8_t *f, uint32_t now) {
  uint8_t seq = f[1];
  if ((uint8_t)(seq - lastSeq) != 1 && lastFrameMs != 0) statusBits |= ST_DROPPED;
  lastSeq = seq;
  lastFrameMs = now;
  statusBits &= (uint8_t)~ST_CRC_BAD;

  int8_t  steer    = (int8_t)f[2];
  int8_t  throttle = (int8_t)f[3];
  uint8_t lights   = f[4];
  armed = f[5] & 0x01;
  if (armed && !pack.inhibits()) everArmed = true;   // first rise of STBY
  lastSteer = steer;

  bool wd = false;                                  // a fresh frame is not late
  OutMode mode = outputModeFor(armed, pack.inhibits(), wd, everArmed,
                               unsafeSince ? now - unsafeSince : 0);
  if (mode == OUT_DRIVE) unsafeSince = 0;
  else if (!unsafeSince) unsafeSince = now;

  applyOutputs(mode, steer, mode == OUT_DRIVE ? throttle : 0);
  applyLights(lights, false, now);

  statusBits = (uint8_t)((statusBits & 0x0E) | (armed ? ST_ARMED : 0) |
                         ((uint8_t)pack.state << ST_PACK_SHIFT));
  sendReply(seq, readTicks(), statusBits, loopDt);
}

void setup() {
  // Order matters: STBY must be driven LOW before anything else can enable the
  // bridge. Until this line the pin is high-Z and the carrier's internal
  // pull-down holds the driver off — that is the boot fail-safe, not luck.
  pinMode(PIN_STBY, OUTPUT);  digitalWrite(PIN_STBY, LOW);
  pinMode(PIN_DIR_A, OUTPUT); digitalWrite(PIN_DIR_A, LOW);
  pinMode(PIN_DIR_B, OUTPUT); digitalWrite(PIN_DIR_B, LOW);
  pinMode(PIN_MOTOR, OUTPUT); analogWrite(PIN_MOTOR, 0);

  pinMode(PIN_HEAD, OUTPUT);  pinMode(PIN_TAIL, OUTPUT);
  pinMode(PIN_IND_L, OUTPUT); pinMode(PIN_IND_R, OUTPUT);
  pinMode(PIN_STATUS, OUTPUT);

  pinMode(PIN_ENC_A, INPUT);  pinMode(PIN_ENC_B, INPUT);
  // No internal pull-ups: the #5159 encoder already pulls its outputs to Vcc
  // through internal 10k. Enabling ours too would fight nothing, but it would
  // also hide a disconnected encoder, which would then read as "not moving".
  encPrev = (uint8_t)((digitalRead(PIN_ENC_A) << 1) | digitalRead(PIN_ENC_B));
  attachInterrupt(digitalPinToInterrupt(PIN_ENC_A), encISR, CHANGE);
  attachInterrupt(digitalPinToInterrupt(PIN_ENC_B), encISR, CHANGE);

  // Timer2 prescaler 1 -> 31.25 kHz, above the audible band. This is the whole
  // reason motor PWM is on D11: Timer0 also drives millis() and cannot move.
  // Safe for D3, which is a digital interrupt input here, not a PWM output.
  TCCR2B = (uint8_t)((TCCR2B & 0xF8) | 0x01);

  steerServo.attach(PIN_SERVO);
  steerServo.writeMicroseconds(SERVO_US_CENTRE);

  analogReference(INTERNAL);        // 1.1 V band gap — packguard.h
  pinMode(PG_PIN, INPUT);

  Serial.begin(115200);
  delay(200);
  Serial.println(F("== UNO CONTROL == protocol v0.2, ACTUATORS UNWIRED"));
  selftest();
}

void loop() {
  uint32_t now = millis();
  static uint32_t lastLoop = 0;
  uint32_t dtUs = (now - lastLoop) * 1000UL;
  loopDt = (uint8_t)(dtUs / 100 > 255 ? 255 : dtUs / 100);
  lastLoop = now;

  pack.poll(now);

  while (Serial.available()) {
    uint8_t c = (uint8_t)Serial.read();
    if (rxLen == 0) {
      if (c == SYNC_CMD) rxBuf[rxLen++] = c;
      else if (c == '?') printStatus();
      else if (c == 'T') selftest();
      else if (c == 'B') {
        benchQuiet = !benchQuiet;
        Serial.print(F("bench-quiet ")); Serial.print(benchQuiet ? F("ON") : F("OFF"));
        Serial.println(F(" - LED only; throttle stays inhibited, cleared on reset"));
      }
      continue;                              // resync: ignore anything else
    }
    rxBuf[rxLen++] = c;
    if (rxLen == CMD_LEN) {
      if (crc8(rxBuf, CMD_LEN) == 0) handleFrame(rxBuf, now);   // ONE clock sample per iteration -- see header
      else {
        // A bad CRC is a DROPPED frame, never a guessed one: no actuator action,
        // and the watchdog keeps running so a stream of corrupt frames still
        // trips it rather than looking like a healthy link.
        statusBits |= ST_CRC_BAD;
        sendReply(rxBuf[1], readTicks(), statusBits, loopDt);
      }
      rxLen = 0;
    }
  }

  bool wd = (lastFrameMs == 0) || (now - lastFrameMs > WATCHDOG_MS);
  if (wd) {
    statusBits |= ST_WATCHDOG;
    armed = false;
    OutMode mode = outputModeFor(false, pack.inhibits(), true, everArmed,
                                 unsafeSince ? now - unsafeSince : 0);
    if (!unsafeSince) unsafeSince = now;
    applyOutputs(mode, lastSteer, 0);        // HOLD steering, do not centre
    applyLights(0x02, everArmed, now);       // hazards, once it has ever driven
  } else {
    statusBits &= (uint8_t)~ST_WATCHDOG;
  }

  // Quiet ONLY the no-sensor case, and only the LED: automatically when no
  // real pack has ever been seen, or on the manual override.
  bool quiet = pack.state == PACK_FAULT && (benchQuiet || !pack.everPlausible);
  // The watchdog blink follows the SAME rule applyLights() already uses for the
  // hazards: a watchdog "trip" before anything has ever armed is not a fault,
  // it is simply no Pi connected yet. Blinking it on a bare bench board is
  // crying wolf, and a light that always cries wolf is not read when it means
  // something. Once everArmed is set -- the car has driven -- silence stops.
  bool wd_alarm = wd && everArmed;
  uint16_t period = (pack.inhibits() && !quiet) ? 150
                    : (wd_alarm ? 400 : (armed ? 1000 : 0));
  digitalWrite(PIN_STATUS, period ? (uint8_t)((now / period) & 1) : LOW);
}
