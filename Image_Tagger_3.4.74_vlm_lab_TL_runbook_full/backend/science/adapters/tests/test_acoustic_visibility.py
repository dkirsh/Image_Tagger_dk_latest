"""Golden tests for the acoustic-visibility / eavesdropping module.

  * audibility falls off with (geodesic) distance;
  * an open room has ~no eavesdropping (everything audible is also visible);
  * two rooms joined by a doorway create a real eavesdropping zone (hidden from
    the speaker but within earshot).
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cnfa_adapters.spatial import Plan  # noqa: E402
from cnfa_adapters.spatial.acoustic_visibility import (  # noqa: E402
    audibility_field,
    eavesdropping_zones,
)


def _open_room(n=50, b=5):
    free = np.zeros((n, n), bool)
    free[b:n - b, b:n - b] = True
    return Plan(free)


def test_audibility_falls_with_distance():
    plan = _open_room()
    level = audibility_field(plan, (25, 25), source_db=70.0)
    assert level[25, 26] > level[25, 40]      # nearer is louder
    assert np.isfinite(level[25, 40])


def test_open_room_has_no_eavesdropping():
    plan = _open_room()
    eavesdrop, vis, level = eavesdropping_zones(plan, (25, 25), source_db=70.0, background_db=40.0)
    # convex room: everything audible is also visible -> no hidden-but-audible cells
    assert eavesdrop.sum() == 0


def test_two_rooms_have_eavesdrop_zone():
    free = np.zeros((70, 70), bool)
    free[8:33, 8:62] = True
    free[37:62, 8:62] = True
    free[33:37, 30:36] = True          # doorway
    plan = Plan(free)
    eavesdrop, vis, level = eavesdropping_zones(plan, (31, 31), source_db=68.0, background_db=40.0)
    assert eavesdrop.sum() > 0          # hidden-but-audible cells exist behind the wall
    # and those cells are genuinely not visible from the speaker
    assert not (eavesdrop & vis).any()


if __name__ == "__main__":
    for fn in list(globals().values()):
        if callable(fn) and getattr(fn, "__name__", "").startswith("test_"):
            fn()
            print("PASS", fn.__name__)
    print("acoustic-visibility tests OK")


def test_reverberant_floor_monotonic_in_absorption():
    from cnfa_adapters.spatial.acoustic_visibility import reverberant_floor_db
    hard = reverberant_floor_db(68.0, 0.1)
    soft = reverberant_floor_db(68.0, 0.6)
    assert hard > soft          # hard (low-absorption) room has a higher reverberant floor


def test_hard_room_less_intelligible_than_soft():
    from cnfa_adapters.spatial.acoustic_visibility import acoustic_eavesdrop
    free = np.zeros((70, 70), bool)
    free[8:33, 8:62] = True; free[37:62, 8:62] = True; free[33:37, 30:36] = True
    plan = Plan(free)
    ez_hard, *_ = acoustic_eavesdrop(plan, (31, 31), 68, 40, absorption=0.12, mode="intelligible")
    ez_soft, *_ = acoustic_eavesdrop(plan, (31, 31), 68, 40, absorption=0.6, mode="intelligible")
    # reverberation smears speech: the hard room yields no MORE intelligible eavesdrop area
    assert ez_hard.sum() <= ez_soft.sum()
