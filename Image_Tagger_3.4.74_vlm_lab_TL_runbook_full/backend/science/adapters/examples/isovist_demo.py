#!/usr/bin/env python3
"""Isovist demo: build a small gallery plan, draw the isovist from a viewpoint,
and render the visual-integration map. Saves isovist_demo.png.

    python examples/isovist_demo.py [out.png]
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cnfa_adapters.spatial import Plan, cast_rays, isovist_measures, visibility_graph  # noqa: E402


def gallery_plan(n=80):
    """A three-space gallery: two rooms joined by a corridor, with a pillar."""
    free = np.zeros((n, n), bool)
    free[8:36, 8:40] = True          # room A (left)
    free[44:72, 40:72] = True        # room B (lower-right)
    free[20:26, 8:72] = True         # horizontal corridor
    free[20:72, 52:58] = True        # vertical corridor into B
    free[16:22, 20:28] = False       # a pillar in room A
    return Plan(free)


def main() -> None:
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "isovist_demo.png")
    plan = gallery_plan()
    viewpoint = (14, 30)             # standing in room A, looking across

    m = isovist_measures(plan, viewpoint, n_rays=720)
    print("Isovist measures at viewpoint", viewpoint)
    for k in ("area", "perimeter", "occlusivity", "compactness", "elongation",
              "jaggedness", "drift_magnitude", "min_radial", "max_radial"):
        print(f"  {k:16s} {m[k]:.3f}")

    _, r, pts, _ = cast_rays(plan, viewpoint, n_rays=720)

    vg = visibility_graph(plan, stride=2, max_nodes=600)
    integ = np.full(plan.free.shape, np.nan)
    for (x, y), v in vg.integration.items():
        integ[y, x] = v
    print(f"  intelligibility  {vg.intelligibility:.3f}   mean_integration {vg.mean_integration:.3f}")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(1, 2, figsize=(13, 6))
        # (a) isovist polygon over the plan
        ax[0].imshow(plan.free, cmap="Greys_r", origin="upper")
        poly = plt.Polygon(pts, closed=True, facecolor=(1, 0.7, 0.1, 0.45),
                           edgecolor="orange", linewidth=1.2)
        ax[0].add_patch(poly)
        ax[0].plot(viewpoint[0], viewpoint[1], "o", color="red", markersize=8)
        ax[0].set_title(f"Isovist from {viewpoint}\narea={m['area']:.0f}, "
                        f"occlusivity={m['occlusivity']:.0f}, compactness={m['compactness']:.2f}")
        ax[0].axis("off")
        # (b) visual integration map
        im = ax[1].imshow(integ, cmap="inferno", origin="upper")
        ax[1].set_title(f"Visual integration (Hillier)\nintelligibility={vg.intelligibility:.2f}")
        ax[1].axis("off")
        fig.colorbar(im, ax=ax[1], fraction=0.046, pad=0.04, label="integration")
        fig.tight_layout()
        fig.savefig(out, dpi=110)
        print("saved", out)
    except Exception as exc:
        print("plot skipped:", repr(exc))


if __name__ == "__main__":
    main()
