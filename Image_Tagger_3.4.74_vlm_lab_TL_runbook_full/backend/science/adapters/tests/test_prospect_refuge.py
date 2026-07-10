"""Golden tests for prospect / refuge / privacy / dead-ground / first-detection.

  * a pillar creates dead ground where an open room has none;
  * a deep alcove has a much shorter first-detection distance than an open
    corridor (you're ambushable — the approach is hidden until the last moment);
  * that same alcove is more private (lower exposure from the corridor).
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cnfa_adapters.spatial import Plan  # noqa: E402
from cnfa_adapters.spatial.prospect_refuge import (  # noqa: E402
    dead_ground_ratio,
    first_detection_distance,
    visual_exposure,
)


def test_pillar_creates_dead_ground():
    free = np.zeros((50, 50), bool)
    free[5:45, 5:45] = True
    open_plan = Plan(free.copy())
    d_open = dead_ground_ratio(open_plan, (15, 15), threat_radius=15)

    with_pillar = free.copy()
    with_pillar[18:24, 18:24] = False        # occluder within the threat radius
    d_pillar = dead_ground_ratio(Plan(with_pillar), (15, 15), threat_radius=15)

    assert d_open < 0.02, d_open
    assert d_pillar > d_open
    assert d_pillar > 0.03, d_pillar


def _corridor_alcove():
    free = np.zeros((50, 50), bool)
    free[24:26, 0:46] = True      # horizontal corridor with a door at x=0
    free[8:26, 44:46] = True      # vertical alcove branching up at the far end
    return Plan(free)


def test_alcove_first_detection_shorter_than_corridor():
    plan = _corridor_alcove()
    entrances = [(0, 24), (0, 25)]
    fdd_corridor = first_detection_distance(plan, (30, 25), entrances)   # standing in the open corridor
    fdd_alcove = first_detection_distance(plan, (45, 12), entrances)     # deep in the alcove
    assert fdd_corridor is not None and fdd_alcove is not None
    # in the open corridor you see the whole approach; in the alcove you don't
    assert fdd_alcove < fdd_corridor, (fdd_alcove, fdd_corridor)


def test_alcove_more_private_than_corridor():
    plan = _corridor_alcove()
    public = [(x, 25) for x in range(2, 40)]     # the public corridor
    exp_corridor = visual_exposure(plan, (30, 25), public)
    exp_alcove = visual_exposure(plan, (45, 12), public)
    assert exp_alcove < exp_corridor
    assert (1 - exp_alcove) > (1 - exp_corridor)   # privacy_index higher in the alcove


if __name__ == "__main__":
    for fn in list(globals().values()):
        if callable(fn) and getattr(fn, "__name__", "").startswith("test_"):
            fn()
            print("PASS", fn.__name__)
    print("prospect/refuge tests OK")
