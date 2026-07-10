"""Golden tests for the isovist engine — directional ground truth that must
hold for any correct implementation.

  * a square room seen from its centre: isovist ~= the room, high compactness,
    ~zero drift, closed;
  * a long corridor: high elongation, low compactness;
  * a room with a pillar: non-zero occlusivity and reduced area vs the empty room;
  * space syntax: a connecting corridor cell has lower visual mean depth (=more
    integrated) than a dead-end room corner.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cnfa_adapters.spatial import Plan, isovist_measures, visibility_graph  # noqa: E402


def _empty_room(n=50, b=5):
    free = np.zeros((n, n), bool)
    free[b:n - b, b:n - b] = True
    return Plan(free)


def test_square_room_from_centre():
    plan = _empty_room(50, 5)
    m = isovist_measures(plan, (25, 25), n_rays=360)
    # area ~ 40x40 = 1600 (discretised)
    assert 1200 < m["area"] < 1800, m["area"]
    assert m["closed"] == 1.0                      # bordered: every ray hits a wall
    assert m["compactness"] > 0.55                 # square from centre is compact
    assert m["drift_magnitude"] < 3.0              # centred -> little drift


def test_corridor_is_elongated():
    free = np.zeros((50, 50), bool)
    free[23:27, 5:45] = True                       # long thin corridor
    plan = Plan(free)
    m = isovist_measures(plan, (25, 25), n_rays=360)
    assert m["elongation"] > 3.0, m["elongation"]
    assert m["compactness"] < 0.4, m["compactness"]


def test_pillar_creates_occlusion():
    empty = _empty_room(50, 5)
    m_empty = isovist_measures(empty, (12, 12), n_rays=360)

    free = np.zeros((50, 50), bool)
    free[5:45, 5:45] = True
    free[20:30, 20:30] = False                     # a pillar in the middle
    plan = Plan(free)
    m = isovist_measures(plan, (12, 12), n_rays=360)

    assert m["occlusivity"] > 0.0                  # the pillar hides area
    assert m["area"] < m_empty["area"]             # less is visible than empty room


def test_corridor_more_integrated_than_deadend():
    # two rooms joined by a corridor: A (top-left), corridor, B (bottom-right)
    free = np.zeros((60, 60), bool)
    free[5:25, 5:25] = True        # room A
    free[35:55, 35:55] = True      # room B
    free[14:16, 5:55] = True       # horizontal corridor
    free[5:55, 44:46] = True       # vertical corridor linking to B
    plan = Plan(free)
    vg = visibility_graph(plan, stride=3, max_nodes=400)

    def nearest(pt):
        return min(vg.mean_depth.keys(), key=lambda p: (p[0]-pt[0])**2 + (p[1]-pt[1])**2)

    corridor_cell = nearest((30, 15))     # on the connecting corridor
    deadend_cell = nearest((6, 6))        # a corner of room A
    assert vg.mean_depth[corridor_cell] < vg.mean_depth[deadend_cell]


if __name__ == "__main__":
    for fn in list(globals().values()):
        if callable(fn) and getattr(fn, "__name__", "").startswith("test_"):
            fn()
            print("PASS", fn.__name__)
    print("isovist tests OK")
