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

- **2026-10-30: M3 control-loop budget, what is measured and what is not.**
  Budget: 50 ms per 20 Hz tick (camera-paced loop in pi/teleop.py). Measured: the
  serial round trip above (PC host, 2026-09-02). NOT yet measured on the Pi: camera
  fps (Camera Module 3 Wide at 160x120 via picamera2), the end-to-end autopilot
  predict() time (preprocess + onnxruntime), and the frame-gap % of a recorded
  episode. All three are steps of the planned off-car Pi session
  (pi/autopilot.py --bench, ml/verify_real.py gap %); quote nothing until then.
- Recorder RAM, computed not measured: 160x120x3 bytes x 20 Hz = ~1.15 MB/s
  (~70 MB/min); episodes are buffered in RAM and written once, on a worker thread
  (Recorder.stop_background) so the save never blocks the tick past the Uno's
  150 ms watchdog.
- **2026-10-30 MEASURED ON THE PI (record LR)** - supersedes "NOT yet measured" above for these two: camera at 160x120 runs 20 fps on the teleop page (loop_dt_ms 1.2), and recorded frame gaps were exactly 50.0 ms - but over only 25 frames, so the long-run frame-gap % is still unmeasured. End-to-end autopilot predict (preprocess + onnxruntime, BCNet-size, untrained weights): p95 1.40 ms, mean 0.82 ms over 3 x 500 iters = ~3% of the 50 ms tick.
