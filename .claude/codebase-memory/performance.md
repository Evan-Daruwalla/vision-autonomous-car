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
- **Serial round-trip is now on the critical path** and is UNMEASURED. At 20 Hz
  the budget is 50 ms per control step; a 115200-baud command of a few bytes is
  well under 1 ms of wire time, but USB latency on the FTDI bridge is set by its
  latency timer (default 16 ms) and has not been measured here. Measure it
  before trusting the loop rate, and consider lowering the timer.
