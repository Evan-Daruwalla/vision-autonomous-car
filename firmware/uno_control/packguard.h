/* packguard.h — pack low-voltage state machine, extracted for uno_control.
 *
 * shortcut: THIS IS A COPY of the logic in firmware/uno_packguard/uno_packguard.ino,
 * which passed SELFTEST 27/27 on the real board on 2026-09-02 (Appendix BJ).
 * Arduino sketches cannot include across sketch folders without installing a
 * library, so the tested logic is duplicated here rather than shared.
 * CEILING: the two copies WILL drift, and the tested one is the other file.
 * UPGRADE TRIGGER: the moment either copy's thresholds or transitions change,
 * promote this to a real Arduino library under firmware/libraries/PackGuard/
 * and make BOTH sketches include it. Until then, any edit here must be mirrored.
 *
 * Rationale for every constant and for the FAULT band is in the header comment
 * of uno_packguard.ino and is NOT repeated here. The two facts most easily got
 * backwards: a floating A0 reads NEAR FULL SCALE (10248 mV measured), so the
 * fault band needs an upper limit; and the reference must be the internal
 * 1.1 V band gap, never the 5 V rail, which sags with the pack.
 */
#ifndef PACKGUARD_H
#define PACKGUARD_H

#include <Arduino.h>

const uint8_t  PG_PIN      = A0;
const uint32_t PG_R_TOP    = 100000UL;
const uint32_t PG_R_BOT    = 12000UL;
const uint32_t PG_VREF_MV  = 1100UL;

const uint16_t PG_WARN_MV     = 6400;   // 3.20 V/cell — report only
const uint16_t PG_CUTOFF_MV   = 6000;   // 3.00 V/cell — cut, latched
const uint16_t PG_RECOVER_MV  = 6800;   // 3.40 V/cell — needed to CLEAR
const uint16_t PG_FAULT_MV    = 4000;   // implausibly LOW
const uint16_t PG_FAULT_HI_MV = 8800;   // implausibly HIGH — unwired divider
const uint16_t PG_HOLD_MS     = 500;

enum PackState { PACK_OK = 0, PACK_WARN = 1, PACK_CUTOFF = 2, PACK_FAULT = 3 };

struct PackGuard {
  PackState state = PACK_OK;
  bool      latched = false;
  uint32_t  belowSince = 0;
  bool      simMode = false;
  uint16_t  simMv = 7400;

  uint16_t readMv() const {
    if (simMode) return simMv;
    uint32_t acc = 0;
    for (uint8_t i = 0; i < 16; i++) acc += analogRead(PG_PIN);
    uint32_t adcMv = ((acc / 16) * PG_VREF_MV) / 1023UL;
    return (uint16_t)((adcMv * (PG_R_TOP + PG_R_BOT)) / PG_R_BOT);
  }

  // Pure transition, so SELFTEST exercises exactly the shipping logic.
  PackState step(uint16_t mv, uint32_t now) {
    if (mv < PG_FAULT_MV || mv > PG_FAULT_HI_MV) { belowSince = 0; return PACK_FAULT; }
    if (latched) return PACK_CUTOFF;
    if (mv < PG_CUTOFF_MV) {
      if (belowSince == 0) belowSince = now;
      if (now - belowSince >= PG_HOLD_MS) { latched = true; return PACK_CUTOFF; }
      return PACK_WARN;
    }
    belowSince = 0;
    return (mv < PG_WARN_MV) ? PACK_WARN : PACK_OK;
  }

  bool inhibits() const { return state == PACK_CUTOFF || state == PACK_FAULT; }

  /* Has a plausible 2S reading EVER been seen since boot?
   *
   * This is what separates "no sensor has ever been wired to this board"
   * from "the sense wire fell off". Both read ~10,248 mV on a floating pin
   * and are indistinguishable in the instant -- but they differ in HISTORY,
   * and history is free to record. A bench board never sees a real pack; a
   * car whose wire drops has seen one. Consumers use it to decide how loudly
   * to complain, NEVER whether to inhibit throttle. (2026-09-02.)
   */
  bool everPlausible = false;

  void poll(uint32_t now) {
    uint16_t mv = readMv();
    if (mv >= PG_FAULT_MV && mv <= PG_FAULT_HI_MV) everPlausible = true;
    state = step(mv, now);
  }

  bool clearLatch() {
    if (readMv() < PG_RECOVER_MV) return false;
    latched = false; belowSince = 0; state = PACK_OK; return true;
  }
};

#endif
