"""vr199_checks/tests/test_pixel_compare.py — the A/B surface-colour comparison, on synthetic image pairs only.

No render, capture or student record is used: every image is built here.

Run:  python3 -m pytest -q vr199_checks/tests/test_pixel_compare.py
"""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from vr199_checks import pixel_compare as pc  # noqa: E402


def wall(seed=0, h=80, w=120):
    """A grey textured wall with a brighter pool of light, like a downlight on a wall."""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w]
    pool = np.exp(-(((xx - 60) / 25.0) ** 2 + ((yy - 50) / 18.0) ** 2))
    lin = 0.25 + 0.35 * pool + rng.normal(0, 0.01, (h, w))
    rgb = np.stack([lin * 1.00, lin * 0.99, lin * 0.97], axis=-1)
    return to_srgb(rgb)


def to_srgb(lin):
    lin = np.clip(lin, 0, 1)
    s = np.where(lin <= 0.0031308, 12.92 * lin, 1.055 * lin ** (1 / 2.4) - 0.055)
    return np.round(s * 255)


MASK = np.ones((80, 120), bool)


def test_identical_images_show_no_measurable_difference():
    a = wall()
    r = pc.compare(a, a.copy(), MASK)
    assert r["verdict"] == "no_measurable_difference"
    assert r["regions"]["lit"]["B_minus_A"]["dE76"] == 0


def test_less_light_on_the_same_material_is_lighting_only():
    a = wall()
    b = to_srgb(pc.srgb_to_linear(a) * 0.80)          # same surface, 20% less light
    r = pc.compare(a, b, MASK)
    d = r["regions"]["lit"]["B_minus_A"]
    assert r["verdict"] == "lighting_only"
    assert d["dL"] < -3 and d["dxy"] < pc.NONE_DXY       # lightness drops, chromaticity holds


def test_a_tinted_surface_is_chroma_differs():
    a = wall()
    lin = pc.srgb_to_linear(a)
    lin[..., 2] *= 0.85                                 # yellower surface
    r = pc.compare(a, to_srgb(lin), MASK)
    assert r["verdict"] == "chroma_differs"
    assert r["regions"]["lit"]["B_minus_A"]["dxy"] >= pc.CHROMA_DXY


def test_a_rougher_texture_with_the_same_colour_is_texture_differs():
    a = wall(seed=1)
    rng = np.random.default_rng(7)
    lin = pc.srgb_to_linear(a)
    grain = rng.normal(0, 0.04, lin.shape[:2])[..., None]
    r = pc.compare(a, to_srgb(lin + grain), MASK, {"whole_wall": (0, 0, 120, 80)})
    assert r["verdict"] == "texture_differs" and r["verdict_basis"] == "patches"


def test_a_moved_dimmer_pool_of_the_same_light_is_lighting_only_on_a_patch():
    """Same surface, the pool shifts and dims (a higher ceiling moves the light away); one light colour, so a
    fixed patch on the pool keeps its chromaticity while its lightness drops. With two lights of different colour
    a fixed patch can shift chromaticity too; pixel_compare's docstring states that limit."""
    h, w = 80, 120
    yy, xx = np.mgrid[0:h, 0:w]
    def render(cx, k):
        pool = k * np.exp(-(((xx - cx) / 20.0) ** 2 + ((yy - 50) / 15.0) ** 2))
        lin = (0.22 + pool)[..., None] * np.array([1.00, 0.97, 0.90])
        return to_srgb(lin)
    a, b = render(60, 0.40), render(66, 0.30)
    r = pc.compare(a, b, MASK, {"on_pool": (40, 35, 80, 65)})
    assert r["verdict"] == "lighting_only" and r["regions"]["on_pool"]["B_minus_A"]["dL"] < -1


def test_patches_and_mask_are_applied_and_bad_sizes_refused():
    a = wall()
    m = MASK.copy(); m[:, 100:] = False
    r = pc.compare(a, a.copy(), m, {"corner": (0, 0, 20, 20)})
    assert r["regions"]["corner"]["A"]["n"] == 400
    with pytest.raises(ValueError):
        pc.compare(a, a[:10], MASK)
    with pytest.raises(ValueError):
        pc.compare(a, a, np.zeros_like(MASK))
