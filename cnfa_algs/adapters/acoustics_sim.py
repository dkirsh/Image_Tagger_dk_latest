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
from typing import Dict, List, Optional, Sequence
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
                  mic: Optional[Sequence[float]] = None) -> Dict:
    """Image-source simulation of a polygonal room extruded to height_m.
    alpha: single mean absorption or per-wall list (len = #polygon edges).
    Returns measured RT60, Sabine estimate, and diagnostics."""
    try:
        import pyroomacoustics as pra
    except ImportError as e:
        raise ImportError("pip install pyroomacoustics (see collect_external.sh)") from e

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
    room.compute_rir()
    rir = room.rir[0][0]

    # decay_db=20 (T20 extrapolated) is robust to truncated tails; max_order
    # must be high enough that truncation, not absorption, is never the
    # dominant decay (the 2026-07-14 collector run caught max_order=6 making
    # hard and soft rooms measure identically at 0.13s).
    rt60_meas = float(pra.experimental.rt60.measure_rt60(rir, fs=fs, decay_db=20))

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
    # shoebox self-test: 6x4x2.8 m, hard room vs soft room
    box = np.array([[0, 0], [6, 0], [6, 4], [0, 4]], float)
    hard = simulate_rt60(box, alpha=0.05, max_order=24)
    soft = simulate_rt60(box, alpha=0.40, max_order=24)
    print("hard room:", hard)
    print("soft room:", soft)
    assert hard["rt60_simulated_s"] > 1.5 * soft["rt60_simulated_s"], \
        "sanity: hard room must ring clearly longer than soft"
    print("acoustics_sim self-test: PASS")
