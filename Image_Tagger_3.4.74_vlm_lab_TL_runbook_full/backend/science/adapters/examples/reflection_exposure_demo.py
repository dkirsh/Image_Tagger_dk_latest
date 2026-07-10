#!/usr/bin/env python3
"""Where does a foyer show you yourself? Self-exposure topography, two claddings.

Same room, same person. One arm walls it in dark reflective glass; the other in
matte plaster. The map is the *self-exposure index*: how strongly, at each floor
position, the person sees their own reflection (mirror-image construction over
the reflective walls, weighted by each surface's optical reflectance and by the
1/(2d) shrink of the reflected image). The reflective arm lights up in a band
along the glass and in the corners where two glass walls both return an image;
the matte arm stays dark everywhere.

    python examples/reflection_exposure_demo.py [out.png]
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cnfa_adapters.spatial.reflection_exposure import self_exposure_field  # noqa: E402


def main() -> None:
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__),
                                                             "reflection_exposure_demo.png")
    W, H = 12.0, 8.0
    corners = [(0, 0), (W, 0), (W, H), (0, H)]

    # Per-edge materials, edge order = [bottom, right, top, left].
    # Reflective arm: two adjacent glass walls (bottom + left) create a corner
    # where the person is caught in two reflections at once.
    arms = [
        ("Dark reflective glass (bottom + left walls)",
         ["dark_glass", "plaster_matte", "plaster_matte", "dark_glass"]),
        ("Matte plaster (all walls)",
         ["plaster_matte"] * 4),
    ]

    results = []
    for title, mats in arms:
        field, xs, ys, surfaces = self_exposure_field(corners, mats, step=0.4)
        grid = field.reshape(len(ys), len(xs))
        results.append((title, grid, xs, ys))
        finite = field[np.isfinite(field)]
        print(f"{title}: mean self-exposure {np.nanmean(finite):.3f}, "
              f"max {np.nanmax(finite):.3f}, "
              f"{(finite > 0.3).mean() * 100:.0f}% of floor above 0.3")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(14, 6.2))
        levels = np.linspace(0.0, 0.7, 15)
        for ax, (title, grid, xs, ys) in zip(axes, results):
            cf = ax.contourf(xs, ys, grid, levels=levels, cmap="magma", extend="max")
            ax.add_patch(plt.Rectangle((0, 0), W, H, fill=False, edgecolor="w", linewidth=1.5))
            # mark the reflective walls
            if "glass" in title:
                ax.plot([0, W], [0, 0], color="#66ccff", linewidth=4, solid_capstyle="butt")
                ax.plot([0, 0], [0, H], color="#66ccff", linewidth=4, solid_capstyle="butt")
            ax.set_aspect("equal"); ax.set_xlim(-0.5, W + 0.5); ax.set_ylim(-0.5, H + 0.5)
            ax.set_title(title); ax.set_xlabel("m")
        axes[0].set_ylabel("m")
        cb = fig.colorbar(cf, ax=axes, fraction=0.025, pad=0.02)
        cb.set_label("self-exposure index (0 = never see yourself, 1 = looming reflection)")
        fig.suptitle("Reflective cladding shows you yourself (same room, same person)", fontsize=13)
        fig.savefig(out, dpi=115, bbox_inches="tight")
        print("saved", out)
    except Exception as exc:
        print("plot skipped:", repr(exc))


if __name__ == "__main__":
    main()
