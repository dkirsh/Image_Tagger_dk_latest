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
                  fs: int = 16000, max_order: int = 3,
                  ray_tracing: bool = True, n_rays: int = 5000,
                  src: Optional[Sequence[float]] = None,
                  mic: Optional[Sequence[float]] = None) -> Dict:
    """Room-acoustics simulation of a polygonal room extruded to height_m.

    METHOD (fixed 2026-07-14): a LOW image-source order (early specular
    reflections) plus RAY TRACING for the diffuse tail. This is both fast
    (seconds on CPU) and correctly absorption-dependent. The earlier pure
    image-source approach was wrong twice: max_order=6 truncated the decay
    (hard==soft==0.13s), and max_order=24 fixed the physics but exploded the
    image count and pinned the CPU for minutes. Ray tracing gives the tail
    cheaply, so RT60 tracks absorption as it must.

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
                                 materials=materials, air_absorption=True,
                                 ray_tracing=ray_tracing)
    room.extrude(height_m, materials=pra.Material(a_floor))
    if ray_tracing:
        # receiver sphere + ray budget sized for a room this scale; energy
        # threshold sets how deep into the tail we trace (RT60-adequate).
        room.set_ray_tracing(receiver_radius=0.5, n_rays=n_rays,
                             energy_thres=1e-7)

    ctr = poly.mean(0)
    src = src or [ctr[0] - 0.5, ctr[1], 1.2]
    mic = mic or [ctr[0] + 0.8, ctr[1] + 0.3, 1.2]
    room.add_source(src)
    room.add_microphone(mic)
    room.compute_rir()
    rir = room.rir[0][0]

    # T30 (decay_db=30) off the ray-traced RIR: the tail is now long enough
    # that the Schroeder curve is well-conditioned. Falls back to T20 if the
    # RIR is short.
    try:
        rt60_meas = float(pra.experimental.rt60.measure_rt60(rir, fs=fs, decay_db=30))
    except Exception:
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
    # shoebox self-test: 6x4x2.8 m, hard room vs soft room. Ray tracing keeps
    # this to a few seconds on CPU (the point of the 2026-07-14 fix).
    import time
    box = np.array([[0, 0], [6, 0], [6, 4], [0, 4]], float)
    t0 = time.time()
    hard = simulate_rt60(box, alpha=0.05)
    soft = simulate_rt60(box, alpha=0.40)
    dt = time.time() - t0
    print(f"hard room: {hard}")
    print(f"soft room: {soft}")
    print(f"(both simulations took {dt:.1f}s total)")
    assert hard["rt60_simulated_s"] > 1.5 * soft["rt60_simulated_s"], \
        "sanity: hard room must ring clearly longer than soft"
    print("acoustics_sim self-test: PASS")
