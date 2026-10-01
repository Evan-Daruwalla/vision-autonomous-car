# performance.md — Autonomous Car Project

- empty, no perf work yet (2026-07-23). Becomes live at M3 (onboard inference
  loop Hz, camera pipeline latency).

- **Real-time actuation moves OFF the Pi (2026-09-02).** With the Arduino Uno
  owning PWM and encoder counting, the Pi's only deadline is the 20 Hz vision
  loop; jitter in Linux scheduling stops being able to corrupt a servo pulse or
  drop an encoder count. The specific failure this avoids: Linux guarantees no
  interrupt latency, so a Pi counting quadrature pulses silently undercounts at
  speed, and the symptom looks like "the model is bad" rather than "the odometry
  is wrong".
- **Serial round-trip MEASURED 2026-09-02 and it is NOT a problem.** At 20 Hz the
  budget is 50 ms per control step. Real round trip at the control shape (4-byte
  command -> 4-byte reply, 400 exchanges paced at 20 Hz): **p50 0.869 ms, p95
  0.956 ms, p99 1.069 ms, max 5.753 ms, 0 failures.** Nothing above 10 ms, so
  **~2% of the budget at p99** and ~12% in the worst single sample.
- **The 16 ms FTDI latency timer did NOT materialise as a 16 ms delay**, and the
  mechanism is NOT established — the registry value really is 16. Measured, not
  explained. Consequence: do not budget 16 ms for it, but do not assume 0.9 ms
  on a different host or driver either. If it ever does bite, lowering
  `HKLM\SYSTEM\CurrentControlSet\Enum\FTDIBUS\...\Device Parameters\LatencyTimer`
  is the known lever, and the firmware watchdog covers the failure anyway.
