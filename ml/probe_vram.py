"""Measure the real VRAM ceiling on this machine, and prove whether NVIDIA's
Sysmem Fallback is active.

Why this exists: SIM-POC P4's done-check is "a trained model OR a documented
OOM boundary with the measured number". That second option is only meaningful
if an OOM can actually happen. With driver-level Sysmem Fallback ENABLED, an
over-allocation does not raise OutOfMemoryError -- CUDA silently backs the
allocation with host RAM over PCIe, and the run just gets ~3x slower. A P4
that trains "successfully" under fallback has measured nothing.

The probe does not read a registry key or a control-panel setting (the driver
does not expose those reliably). It allocates until something gives, and lets
the OUTCOME classify the policy:

    allocation fails below total VRAM  -> fallback OFF (a real ceiling exists)
    allocation passes total VRAM       -> fallback ON  (spilling to host RAM)

Read-only with respect to system settings: this reports the policy, it never
changes it. Changing it is a driver setting and therefore Evan's call.

Run:  .venv\\Scripts\\python.exe ml/probe_vram.py
Exit: 0 if fallback is OFF (P4 measurements are valid)
      1 if fallback is ON, or no CUDA device
"""

import sys

import torch

CHUNK_MB = 256
# Stop before the host starts swapping if fallback turns out to be on. Two GB
# past the card is far enough to be unambiguous and small enough to be safe.
OVERSHOOT_GB = 2.0


def main() -> int:
    if not torch.cuda.is_available():
        print("FAIL: no CUDA device")
        return 1

    props = torch.cuda.get_device_properties(0)
    total_b = props.total_memory
    free_b, _ = torch.cuda.mem_get_info(0)
    used_by_others_b = total_b - free_b

    print(f"device            : {props.name}")
    print(f"total VRAM        : {total_b / 1024**3:.3f} GB")
    print(f"used by others    : {used_by_others_b / 1024**3:.3f} GB")
    print(f"free for us       : {free_b / 1024**3:.3f} GB")
    print()

    limit_b = total_b + int(OVERSHOOT_GB * 1024**3)
    chunk_b = CHUNK_MB * 1024**2
    held = []
    allocated_b = 0
    oom = False

    try:
        while allocated_b < limit_b:
            try:
                held.append(torch.empty(chunk_b, dtype=torch.uint8, device="cuda"))
            except torch.cuda.OutOfMemoryError:
                oom = True
                break
            allocated_b += chunk_b
    finally:
        del held
        torch.cuda.empty_cache()

    print(f"allocated before failure : {allocated_b / 1024**3:.3f} GB")
    print(f"raised OutOfMemoryError  : {oom}")
    print()

    # Classify. The comparison is against TOTAL, not free: a process that gets
    # past the physical card size is provably not sitting in VRAM.
    if oom and allocated_b <= total_b:
        print("VERDICT: Sysmem Fallback is OFF -- a real OOM ceiling exists.")
        print(f"         Usable ceiling for this run: {allocated_b / 1024**3:.3f} GB")
        print("         P4 memory measurements are VALID.")
        return 0

    print("VERDICT: Sysmem Fallback appears to be ON -- allocation exceeded the")
    print("         physical card without an OOM, so CUDA is spilling to host RAM.")
    print("         P4 memory measurements would be INVALID: an over-budget run")
    print("         will silently slow down instead of failing.")
    print()
    print("         FIX (Evan's call -- a driver setting, not changed by this script):")
    print("         NVIDIA Control Panel -> Manage 3D Settings -> CUDA - Sysmem")
    print("         Fallback Policy -> 'Prefer No Sysmem Fallback'.")
    print()
    print("         WORKAROUND, tested below: cap PyTorch's own allocator instead.")
    check_allocator_cap(total_b)
    return 1


def check_allocator_cap(total_b: int) -> None:
    """Can we get a hard OOM ceiling WITHOUT touching the driver setting?

    `set_per_process_memory_fraction` caps PyTorch's caching allocator. The
    open question is whether that cap still bites when the driver is willing
    to satisfy the underlying cudaMalloc from host RAM -- if PyTorch counts
    spilled memory against its own budget, the cap holds and gives us a
    reproducible, in-code ceiling that beats a control-panel setting. Asserted
    by measurement, not by reading the docs.
    """
    fraction = 0.25
    cap_b = int(total_b * fraction)
    print(f"         probing a {fraction:.0%} cap ({cap_b / 1024**3:.3f} GB)...")

    torch.cuda.empty_cache()
    torch.cuda.set_per_process_memory_fraction(fraction, 0)

    chunk_b = CHUNK_MB * 1024**2
    held = []
    allocated_b = 0
    oom = False
    try:
        # Aim well past the cap; if the cap is real we stop long before this.
        while allocated_b < total_b:
            try:
                held.append(torch.empty(chunk_b, dtype=torch.uint8, device="cuda"))
            except torch.cuda.OutOfMemoryError:
                oom = True
                break
            allocated_b += chunk_b
    finally:
        del held
        torch.cuda.empty_cache()
        torch.cuda.set_per_process_memory_fraction(1.0, 0)

    print(f"         allocated under cap : {allocated_b / 1024**3:.3f} GB")
    print(f"         raised OOM          : {oom}")
    if oom and allocated_b <= cap_b:
        print("         RESULT: the allocator cap HOLDS under Sysmem Fallback.")
        print("                 P4 can measure a reproducible boundary in code.")
    else:
        print("         RESULT: the cap did NOT hold. The driver setting is the")
        print("                 only way to make P4's boundary measurable.")


if __name__ == "__main__":
    sys.exit(main())
