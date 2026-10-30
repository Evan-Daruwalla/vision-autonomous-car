"""Camera sources for the car's Pi-side recorder: a deterministic fake and the real one.

WHY two classes behind one interface: the recorder and control loop must be
testable on a PC with no camera. `FakeCamera` produces paced, deterministic
frames (the frame index is encoded in the pixels, so a test can prove no frame
was dropped or reordered). `PiCamera` wraps picamera2 and is imported lazily
so this module loads on any machine.

Both return `(frame_rgb_uint8[H, W, 3], t_ns)` from `read()`. Frame size is
120x160 because `ml/verify_corpus.py`'s alignment gate is calibrated for it.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import io
import time

import numpy as np


def fake_frame(n: int, width: int = 160, height: int = 120) -> np.ndarray:
    """Deterministic frame n: grey, moving white bar, index in row 0 channel 0."""
    frame = np.full((height, width, 3), 60, np.uint8)
    x = (n * 4) % width
    frame[:, x:x + 8, :] = 255
    # frame index in row 0, channel 0 (overwrites the bar there)
    frame[0, 0, 0] = n & 0xFF
    frame[0, 1, 0] = (n >> 8) & 0xFF
    frame[0, 2, 0] = (n >> 16) & 0xFF
    return frame


class FakeCamera:
    """Paced synthetic camera: grey frame, moving white bar, frame counter in row 0."""

    def __init__(self, width: int = 160, height: int = 120, fps: int = 20):
        self.width = width
        self.height = height
        self.fps = fps
        self._period_ns = int(1e9 / fps)
        self._n = 0
        self._next_ns = 0

    @property
    def config(self) -> dict:
        return {"kind": "fake", "width": self.width, "height": self.height,
                "fps": self.fps}

    def start(self) -> None:
        self._n = 0
        self._next_ns = time.monotonic_ns()

    def stop(self) -> None:
        pass

    def read(self) -> tuple[np.ndarray, int]:
        # Slots are scheduled from start() so sleep jitter never accumulates;
        # if we are late, resync from now instead of bursting to catch up.
        wait_ns = self._next_ns - time.monotonic_ns()
        if wait_ns > 0:
            time.sleep(wait_ns / 1e9)
        self._next_ns += self._period_ns
        now = time.monotonic_ns()
        if now > self._next_ns:
            self._next_ns = now + self._period_ns

        n = self._n
        self._n += 1
        frame = fake_frame(n, self.width, self.height)
        return frame, time.monotonic_ns()


class PiCamera:
    """picamera2-backed camera. picamera2/libcamera are imported in start() only."""

    RAW_SIZE = (2304, 1296)

    def __init__(self, width: int = 160, height: int = 120, fps: int = 20,
                 rotate180: bool = False):
        self.width = width
        self.height = height
        self.fps = fps
        self.rotate180 = rotate180
        self._cam = None

    @property
    def config(self) -> dict:
        return {"kind": "picamera2", "width": self.width, "height": self.height,
                "fps": self.fps, "rotate180": self.rotate180,
                "format": "RGB888->RGB", "raw_size": list(self.RAW_SIZE),
                "scaler_crop": "full"}

    def start(self) -> None:
        from picamera2 import Picamera2
        import libcamera

        dur = int(1e6 / self.fps)
        cam = Picamera2()
        # The frame rate is set ONLY through FrameDurationLimits: the fps=
        # keyword in newer picamera2 docs (record LH) does not exist in the
        # Pi's apt picamera2 0.3.31 (TypeError on the Pi, 2026-10-30).
        # sensor output_size pins the 2304x1296 binned mode.
        cfg = cam.create_video_configuration(
            main={"size": (self.width, self.height), "format": "RGB888"},
            raw={"size": self.RAW_SIZE},
            sensor={"output_size": self.RAW_SIZE},
            controls={"FrameDurationLimits": (dur, dur)},
            transform=libcamera.Transform(hflip=self.rotate180,
                                          vflip=self.rotate180))
        cam.configure(cfg)
        cam.start()
        full = cam.camera_properties.get("ScalerCropMaximum")
        if full is None and "ScalerCrop" in cam.camera_controls:
            full = cam.camera_controls["ScalerCrop"][1]     # (min, max, default)
        if full is not None:
            cam.set_controls({"ScalerCrop": full})
        self._cam = cam
        self._reported = False

    def read(self) -> tuple[np.ndarray, int]:
        # picamera2 "RGB888" is B,G,R in memory (its own request.py maps
        # RGB888 -> "BGR"; checked 2026-10-29), hence the flip below. The
        # full-FOV crop is UNVERIFIED until the bench run: the first frame
        # prints the ScalerCrop the camera actually used.
        request = self._cam.capture_request()
        try:
            arr = request.make_array("main")
            md = request.get_metadata()
        finally:
            request.release()
        if not self._reported:
            self._reported = True
            print(f"camera: ScalerCrop={md.get('ScalerCrop')} "
                  f"SensorTimestamp={'yes' if 'SensorTimestamp' in md else 'NO'} "
                  f"array={arr.shape}")
        frame = np.ascontiguousarray(arr[..., ::-1])
        t_ns = int(md.get("SensorTimestamp", time.monotonic_ns()))
        return np.ascontiguousarray(frame[:, :, :3], dtype=np.uint8), t_ns

    def stop(self) -> None:
        if self._cam is not None:
            self._cam.stop()
            self._cam.close()
            self._cam = None


def encode_jpeg(frame_rgb: np.ndarray, quality: int = 70) -> bytes:
    """JPEG-encode an RGB frame; simplejpeg when installed, else Pillow."""
    try:
        import simplejpeg
        return simplejpeg.encode_jpeg(np.ascontiguousarray(frame_rgb),
                                      quality=quality, colorspace="RGB")
    except ImportError:
        from PIL import Image
        buf = io.BytesIO()
        Image.fromarray(frame_rgb).save(buf, "JPEG", quality=quality)
        return buf.getvalue()


def self_check() -> None:
    cam = FakeCamera()
    cam.start()
    frames = [cam.read() for _ in range(10)]
    cam.stop()
    ts = [t for _, t in frames]
    for i, (f, _) in enumerate(frames):
        assert f.shape == (120, 160, 3), f.shape
        assert f.dtype == np.uint8
        n = int(f[0, 0, 0]) | (int(f[0, 1, 0]) << 8) | (int(f[0, 2, 0]) << 16)
        assert n == i, (n, i)
    assert all(b > a for a, b in zip(ts, ts[1:])), ts
    period = (ts[-1] - ts[0]) / 9 / 1e9
    assert 0.040 <= period <= 0.065, period

    jpg = encode_jpeg(frames[0][0])
    assert jpg[:2] == b"\xff\xd8" and jpg[-2:] == b"\xff\xd9"

    pc = PiCamera(rotate180=True)
    assert pc.config["rotate180"] is True
    assert "picamera2" not in sys.modules  # construction must not import it
    print("camera self_check: PASS")


if __name__ == "__main__":
    self_check()
