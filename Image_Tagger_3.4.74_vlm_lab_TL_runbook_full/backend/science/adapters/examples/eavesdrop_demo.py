#!/usr/bin/env python3
"""Eavesdropping-zone map: where a hidden listener can hear a speaker.

Two rooms joined by a doorway. A speaker stands in room 1. The left panel shows
what the speaker can SEE (visual isovist) — most of room 2 is out of sight. The
right panel shows the acoustic audibility field and highlights the
EAVESDROPPING ZONES: cells the speaker cannot see but where a listener can hear
them (visual dead ground x acoustic audibility).

    python examples/eavesdrop_demo.py [out.png]
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cnfa_adapters.spatial import Plan  # noqa: E402
from cnfa_adapters.spatial.acoustic_visibility import eavesdrop_exposure, eavesdropping_zones  # noqa: E402


def two_room_plan(n=70):
    free = np.zeros((n, n), bool)
    free[8:33, 8:62] = True       # room 1 (upper)
    free[37:62, 8:62] = True      # room 2 (lower)
    free[33:37, 30:36] = True     # doorway through the party wall
    return Plan(free)


def main() -> None:
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "eavesdrop_demo.png")
    plan = two_room_plan()
    speaker = (31, 31)          # standing near the doorway
    SRC_DB, BG_DB = 68.0, 40.0  # a normal-to-raised voice vs a quiet room

    eavesdrop, vis, level = eavesdropping_zones(plan, speaker, source_db=SRC_DB, background_db=BG_DB)
    scal = eavesdrop_exposure(plan, speaker, source_db=SRC_DB, background_db=BG_DB)
    print("speaker at", speaker)
    for k, v in scal.items():
        print(f"  {k} = {v:.3f}")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(1, 2, figsize=(14, 6.5))
        # panel 1: what the speaker can see
        base = plan.free.astype(float)
        ax[0].imshow(base, cmap="Greys_r", origin="upper")
        seen = np.ma.masked_where(~vis, np.ones_like(base))
        ax[0].imshow(seen, cmap="autumn", alpha=0.35, origin="upper")
        ax[0].plot(*speaker, "o", color="red", ms=9)
        ax[0].set_title("What the speaker SEES (visual isovist)\nmost of the far room is out of sight")
        ax[0].axis("off")
        # panel 2: audibility + eavesdropping zones
        lv = np.ma.masked_where(~np.isfinite(level), level)
        im = ax[1].imshow(lv, cmap="viridis", origin="upper")
        ez = np.ma.masked_where(~eavesdrop, np.ones_like(base))
        ax[1].imshow(ez, cmap="autumn", alpha=0.9, origin="upper")
        ax[1].plot(*speaker, "o", color="red", ms=9)
        ax[1].set_title("Acoustic audibility (dB) + EAVESDROPPING ZONES (red)\n"
                        f"hidden-but-audible = {scal['cnfa.acoustic.eavesdrop_of_deadground']*100:.0f}% "
                        "of the speaker's blind area")
        ax[1].axis("off")
        fig.colorbar(im, ax=ax[1], fraction=0.046, pad=0.04, label="level (dB)")
        fig.tight_layout()
        fig.savefig(out, dpi=110)
        print("saved", out)
    except Exception as exc:
        print("plot skipped:", repr(exc))


if __name__ == "__main__":
    main()
