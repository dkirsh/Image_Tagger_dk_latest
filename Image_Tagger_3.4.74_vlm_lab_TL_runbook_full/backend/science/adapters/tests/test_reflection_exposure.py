"""Tests for the specular self-visibility / seen-via-reflection optics.

Pure geometry (NumPy only), so these run everywhere — no heavy deps, no skips.
They pin the physics: the mirror-image construction, the reflective-side gate,
occlusion, the reflective-vs-matte contrast, and the 1/(2d) fall-off.
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cnfa_adapters.spatial.reflection_exposure import (  # noqa: E402
    Surface,
    annotate_reflection,
    optical_reflectance,
    seen_via_reflection,
    self_exposure,
    self_images,
    surfaces_from_corners,
)

# A 10 x 6 room. The left wall (x = 0) is the one we make reflective.
CORNERS = [(0, 0), (10, 0), (10, 6), (0, 6)]
INTERIOR = (5.0, 3.0)


def _left_wall(reflectance):
    return Surface((0, 0), (0, 6), reflectance, "left")


def test_optical_table_separates_mirror_from_matte():
    assert optical_reflectance("dark_glass") > 0.6
    assert optical_reflectance("plaster_matte") < 0.1
    assert optical_reflectance(0.42) == 0.42          # floats pass through
    assert optical_reflectance("mirror_glass") == optical_reflectance("dark_glass")  # preset


def test_self_image_exists_facing_a_mirror():
    surfaces = [_left_wall(0.8)]
    imgs = self_images((2.0, 3.0), surfaces, INTERIOR)
    assert len(imgs) == 1
    # round-trip distance is twice the perpendicular distance (2 m -> 4 m)
    assert abs(imgs[0]["image_distance"] - 4.0) < 1e-6
    assert abs(imgs[0]["foot"][0] - 0.0) < 1e-6      # foot lands on the glass plane


def test_matte_wall_gives_no_self_image():
    surfaces = [_left_wall(0.03)]                     # plaster
    imgs = self_images((2.0, 3.0), surfaces, INTERIOR)
    assert imgs == []


def test_reflective_arm_exceeds_matte_arm():
    glass = self_exposure((2.0, 3.0), [_left_wall(0.8)], INTERIOR)
    matte = self_exposure((2.0, 3.0), [_left_wall(0.03)], INTERIOR)
    assert glass["self_exposure_index"] > matte["self_exposure_index"]
    assert glass["n_self_images"] == 1 and matte["n_self_images"] == 0


def test_closer_reflection_looms_larger():
    surfaces = [_left_wall(0.8)]
    near = self_exposure((1.0, 3.0), surfaces, INTERIOR)   # 1 m from glass
    far = self_exposure((4.0, 3.0), surfaces, INTERIOR)    # 4 m from glass
    assert near["self_exposure"] > far["self_exposure"]    # 1/(2d) fall-off
    assert near["nearest_image_distance"] < far["nearest_image_distance"]


def test_occluder_blocks_self_image():
    surfaces = [_left_wall(0.8)]
    # a partition between the eye (x=2) and the glass (x=0), spanning the sightline
    partition = Surface((1.0, 0.0), (1.0, 6.0), 0.0, "partition")
    imgs = self_images((2.0, 3.0), surfaces, INTERIOR, occluders=surfaces + [partition])
    assert imgs == []


def test_seen_via_reflection_around_a_partition():
    # Glass back wall at y = 6. Target and observer are on opposite sides of a
    # partition that blocks the DIRECT line, but a bounce off the glass connects
    # them. The mirror path should be found.
    corners = [(0, 0), (10, 0), (10, 6), (0, 6)]
    glass_back = Surface((10, 6), (0, 6), 0.8, "back_glass")   # y = 6 wall, reflective
    partition = Surface((5, 0), (5, 4.0), 0.0, "partition")     # gap near the glass
    target = (3.0, 5.0)
    observers = [(7.0, 5.0)]
    interior = (5.0, 3.0)
    rv = seen_via_reflection(target, observers, [glass_back], interior,
                             occluders=[glass_back, partition])
    assert rv["n_reflected"] == 1


def test_annotate_bundle_keys():
    out = annotate_reflection(CORNERS, (2.0, 3.0), materials="dark_glass")
    assert "cnfa.reflection.self_exposure_index" in out
    assert "cnfa.reflection.self_image_count" in out
    assert out["cnfa.reflection.self_exposure_index"] > 0.0


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print("PASS", name)
    print("reflection_exposure tests OK")
