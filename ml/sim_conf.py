"""Single source of truth for the gym-donkeycar launch conf's camera geometry.

Record AG.4 / AI: `donkey_sim.py` only sends a camera config when `cam_config`
is present in the conf dict, and until 2026-08-16 nothing outside the one
diagnostic script ever put one there -- so every frame the corpus, every eval,
and every number in `docs/SIM_TRANSFER_SPEC.md` was shot at whatever FOV the
Unity binary defaults to. That default was identified only by comparison
(`diag_camera_fov.py`, record AI): fov=90, matching the Camera Module 3 Wide
within 2-4 degrees. It was never asserted anywhere a version bump could not
silently move it.

Audit finding 2026-08-16: 9 of the 10 modules that launch the sim built their
own conf dict by hand, none of them setting cam_config. This module is the
chokepoint fix -- every launcher should build its conf through
`base_sim_conf()` instead.

`diag_camera_fov.py` is the deliberate exception: its whole job is sweeping
explicit FOV values (including "no cam_config sent" via fov=None) to IDENTIFY
this constant, so it must not import it.
"""
from __future__ import annotations

# Identified by comparison, record AI (2026-08-13): the Unity sim's default
# FOV, matched by the Camera Module 3 Wide within 2-4 degrees.
DEFAULT_FOV = 90

CAM_CONFIG = {
    "img_w": 160, "img_h": 120, "img_d": 3,
    "fov": DEFAULT_FOV, "fish_eye_x": 0.0, "fish_eye_y": 0.0,
    "offset_x": 0.0, "offset_y": 0.0, "offset_z": 0.0,
    "rot_x": 0.0, "rot_y": 0.0, "rot_z": 0.0,
}


def base_sim_conf(exe_path: str, port: int, car_name: str, **overrides) -> dict:
    """The shared launch conf every sim-launching module should build from.

    `exe_path` / `port` / `car_name` stay required positional-ish args so
    each call site's own concerns (which binary, which port, which run's
    name) stay visible there. Everything else -- including cam_config -- is
    a pinned default; pass a keyword to override or add one
    (e.g. max_cte=4.0, font_size=40).
    """
    conf = {
        "exe_path": exe_path,
        "host": "127.0.0.1",
        "port": port,
        "start_delay": 10.0,
        "car_name": car_name,
        "cam_config": dict(CAM_CONFIG),
    }
    conf.update(overrides)
    return conf
