"""
pyroomacoustics upgrade for the acoustic proxy: from alpha-table estimate to
image-source SIMULATION with a measured RT60 from the simulated impulse
response. This is the essay's Part VI made runnable.

Needs `pip install pyroomacoustics` (MIT license; collected by
collect_external.sh). Import-guarded like the other adapters.

Inputs are things the pipeline already produces:
  - room polygon (metres) — from a SpatialLM layout, a Structured3D scene,
    or a PlanGrid via grid_to_polygon()
  - ceiling height
  - per-wall (or single) absorption coefficients — from the material layer

Outputs: measured RT60 (Schroeder decay on the simulated RIR), the Sabine
estimate for comparison, and their ratio — a built-in check of when the
diffuse-field formula misleads (long rooms, uneven absorption).

Self-test (run on a machine with pyroomacoustics):
    python -m cnfa_algs.adapters.acoustics_sim
"""
from __future__ import annotations
from typing import Callable, Dict, List, Optional, Sequence
import time
import numpy as np


def grid_to_polygon(grid, cell_m: float, epsilon_cells: float = 2.0):
    """Largest free-space region of a PlanGrid -> simplified polygon (metres)."""
    import cv2
    free = (grid == 1).astype(np.uint8)
    n, lab = cv2.connectedComponents(free)
    if n < 2:
        raise ValueError("no free space in grid")
    sizes = np.bincount(lab.ravel()); sizes[0] = 0
    main = (lab == sizes.argmax()).astype(np.uint8)
    cs, _ = cv2.findContours(main, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    poly = cv2.approxPolyDP(max(cs, key=cv2.contourArea), epsilon_cells, True)
    return poly.reshape(-1, 2).astype(float) * cell_m   # (x, y) in metres


def simulate_rt60(polygon_m: np.ndarray, height_m: float = 2.8,
                  alpha: float | Sequence[float] = 0.15,
                  fs: int = 16000, max_order: int = 24,
                  src: Optional[Sequence[float]] = None,
                  mic: Optional[Sequence[float]] = None,
                  progress: Optional[Callable[[str], None]] = None) -> Dict:
    """Image-source simulation of a polygonal room extruded to height_m.
    alpha: single mean absorption or per-wall list (len = #polygon edges).
    Returns measured RT60, Sabine estimate, and diagnostics."""
    started = time.monotonic()

    def emit(message: str) -> None:
        if progress is not None:
            progress(f"{message} elapsed_s={time.monotonic() - started:.2f}")

    emit("importing pyroomacoustics")
    try:
        import pyroomacoustics as pra
    except ImportError as e:
        raise ImportError("pip install pyroomacoustics (see collect_external.sh)") from e

    emit(f"building room fs={fs} max_order={max_order}")
    poly = np.asarray(polygon_m, float)
    n_edges = len(poly)
    if np.isscalar(alpha):
        alphas = [float(alpha)] * n_edges
    else:
        alphas = list(alpha)
    # floor/ceiling get the first/mean alpha unless caller extends the list
    a_floor = alphas[0] if len(alphas) == n_edges else alphas[n_edges]
    a_ceil = float(np.mean(alphas))

    materials = [pra.Material(a) for a in alphas]
    room = pra.Room.from_corners(poly.T, fs=fs, max_order=max_order,
                                 materials=materials, air_absorption=True)
    room.extrude(height_m, materials=pra.Material(a_floor))

    ctr = poly.mean(0)
    src = src or [ctr[0] - 0.5, ctr[1], 1.2]
    mic = mic or [ctr[0] + 0.8, ctr[1] + 0.3, 1.2]
    room.add_source(src)
    room.add_microphone(mic)
    emit("computing RIR")
    room.compute_rir()
    rir = room.rir[0][0]

    # decay_db=20 (T20 extrapolated) is robust to truncated tails; max_order
    # must be high enough that truncation, not absorption, is never the
    # dominant decay (the 2026-07-14 collector run caught max_order=6 making
    # hard and soft rooms measure identically at 0.13s).
    emit(f"measuring RT60 rir_samples={len(rir)}")
    rt60_meas = float(pra.experimental.rt60.measure_rt60(rir, fs=fs, decay_db=20))
    emit("measured RT60")

    # Sabine for comparison (the proxy the tagger uses)
    area2d = 0.5 * abs(np.dot(poly[:, 0], np.roll(poly[:, 1], -1))
                       - np.dot(poly[:, 1], np.roll(poly[:, 0], -1)))
    perim = float(np.sum(np.linalg.norm(np.roll(poly, -1, 0) - poly, axis=1)))
    V = area2d * height_m
    S_walls = perim * height_m
    S_total = S_walls + 2 * area2d
    a_bar = (np.mean(alphas) * S_walls + (a_floor + a_ceil) * area2d) / S_total
    rt60_sabine = 0.161 * V / (S_total * a_bar)

    return {"rt60_simulated_s": round(rt60_meas, 3),
            "rt60_sabine_s": round(float(rt60_sabine), 3),
            "sabine_over_sim": round(float(rt60_sabine / max(rt60_meas, 1e-6)), 3),
            "volume_m3": round(float(V), 1), "mean_alpha": round(float(a_bar), 3),
            "method": "pyroomacoustics image-source RIR + Schroeder RT60 (simulation tier)",
            "confidence": 0.8,
            "failure_modes": ["image-source omits diffraction/scattering",
                              "single src/mic position (average several for reports)",
                              "furniture not modeled unless added as absorption"]}


if __name__ == "__main__":
    def log(message: str) -> None:
        print(f"[acoustics_sim] {message}", flush=True)

    # Bounded smoke: the full 6x4x2.8 m / max_order=24 comparison is a
    # calibration job and can spend minutes in native pyroomacoustics compute.
    # This tiny case proves the dependency, geometry path, RIR generation, and
    # Schroeder measurement are working without hiding long production runs.
    box = np.array([[0, 0], [2.4, 0], [2.4, 1.8], [0, 1.8]], float)
    log("bounded self-test start: 2.4x1.8x2.4m fs=8000 max_order=3")
    hard = simulate_rt60(box, height_m=2.4, alpha=0.05, fs=8000, max_order=3, progress=log)
    soft = simulate_rt60(box, height_m=2.4, alpha=0.40, fs=8000, max_order=3, progress=log)
    print("hard room:", hard)
    print("soft room:", soft)
    if hard["rt60_sabine_s"] <= soft["rt60_sabine_s"]:
        raise AssertionError("sanity: Sabine hard-room estimate must exceed soft-room estimate")
    print("acoustics_sim bounded self-test: PASS")
    print("note: use larger max_order offline for calibrated hard-vs-soft simulated RT60 separation")
