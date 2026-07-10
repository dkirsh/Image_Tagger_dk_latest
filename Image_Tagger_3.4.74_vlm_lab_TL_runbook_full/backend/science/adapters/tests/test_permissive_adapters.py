"""Golden-value tests for the permissive adapters on synthetic images.

These assert *directional* ground truth that must hold for any correct
implementation, rather than brittle exact numbers:

  * a uniform field has near-zero colour entropy; white noise has high entropy;
  * a warm (reddish) light reads warmer than a cool (bluish) one;
  * a grayscale image is far less colourful than a saturated one;
  * white noise is more cluttered than a flat field;
  * a checkerboard has higher GLCM contrast than a flat field.

Each test skips cleanly if its adapter's upstream package is not installed, so
the suite is safe to run in a minimal environment.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cnfa_adapters import StandaloneFrame  # noqa: E402
from cnfa_adapters.permissive import (  # noqa: E402
    AestheticsToolboxAdapter,
    ColourAdapter,
    SkimageTextureAdapter,
    VisualClutterAdapter,
)
from cnfa_adapters.permissive.colour_opponent_adapter import ColourOpponentAdapter  # noqa: E402
from cnfa_adapters.permissive.mahotas_texture_adapter import MahotasTextureAdapter  # noqa: E402
from cnfa_adapters.permissive.proximal_stats_adapter import ProximalStatsAdapter  # noqa: E402

RNG = np.random.default_rng(0)


def _uniform(v=128, size=96):
    return np.full((size, size, 3), v, np.uint8)


def _noise(size=96):
    return (RNG.random((size, size, 3)) * 255).astype(np.uint8)


def _checkerboard(size=96, cell=12):
    a = np.zeros((size, size), np.uint8)
    for i in range(0, size, cell):
        for j in range(0, size, cell):
            if ((i // cell) + (j // cell)) % 2 == 0:
                a[i:i + cell, j:j + cell] = 255
    return np.stack([a, a, a], axis=2)


def _tinted(r, g, b, size=96):
    img = np.zeros((size, size, 3), np.uint8)
    img[..., 0], img[..., 1], img[..., 2] = r, g, b
    return img


def _run(adapter, rgb):
    frame = StandaloneFrame(rgb)
    adapter.analyze(frame)
    return frame.as_dict()


def _skip_if_unavailable(cls):
    if not cls.available():
        print("SKIP", cls.__name__, "(dependency not installed)")
        return True
    return False


def test_aesthetics_entropy_orders():
    if _skip_if_unavailable(AestheticsToolboxAdapter):
        return
    a = AestheticsToolboxAdapter()
    uni = _run(a, _uniform())
    noi = _run(a, _noise())
    # colour-palette entropy: uniform ~0, noise high
    assert uni.get("cnfa.fluency.color_palette_entropy", 0) < 1.0
    assert noi.get("cnfa.fluency.color_palette_entropy", 0) > uni.get(
        "cnfa.fluency.color_palette_entropy", 0)
    # fractal dimension of noise should be high (near 2)
    assert noi.get("cnfa.fractal_dimension", 0) > 1.6


def test_colour_warm_vs_cool_direction():
    if _skip_if_unavailable(ColourAdapter):
        return
    a = ColourAdapter()
    warm = _run(a, _tinted(230, 150, 90))   # incandescent-ish
    cool = _run(a, _tinted(150, 190, 240))  # daylight/blue-ish
    assert warm["cnfa.light.warm_vs_cool_ratio"] > cool["cnfa.light.warm_vs_cool_ratio"]
    assert warm["cnfa.light.cct_kelvin"] < cool["cnfa.light.cct_kelvin"]


def test_colourfulness_grayscale_low():
    if _skip_if_unavailable(ColourAdapter):
        return
    a = ColourAdapter()
    gray = _run(a, _uniform(128))
    colourful = _run(a, _tinted(240, 30, 30))
    assert gray["cnfa.fluency.colorfulness"] < colourful["cnfa.fluency.colorfulness"]


def test_clutter_noise_gt_uniform():
    if _skip_if_unavailable(VisualClutterAdapter):
        return
    a = VisualClutterAdapter()
    uni = _run(a, _uniform())
    noi = _run(a, _noise())
    assert noi["cnfa.fluency.clutter_density_count"] > uni["cnfa.fluency.clutter_density_count"]


def test_glcm_contrast_checkerboard_gt_uniform():
    if _skip_if_unavailable(SkimageTextureAdapter):
        return
    a = SkimageTextureAdapter()
    uni = _run(a, _uniform())
    chk = _run(a, _checkerboard())
    assert chk["cnfa.haptic.texture_variation_index"] > uni["cnfa.haptic.texture_variation_index"]


def test_proximal_subband_skew_highlight():
    if _skip_if_unavailable(ProximalStatsAdapter):
        return
    a = ProximalStatsAdapter()
    flat = _uniform(120)
    hi = _uniform(120).copy()
    hi[40:56, 40:56, :] = 255  # a bright specular blob -> positive skew
    d_flat = _run(a, flat)
    d_hi = _run(a, hi)
    assert d_hi["cnfa.material.subband_skew"] > d_flat.get("cnfa.material.subband_skew", 0)


def test_colour_opponent_rg_direction():
    if _skip_if_unavailable(ColourOpponentAdapter):
        return
    a = ColourOpponentAdapter()
    red = _run(a, _tinted(220, 40, 40))
    green = _run(a, _tinted(40, 200, 40))
    # a* > 0 for red, < 0 for green
    assert red["cnfa.color.opponent_rg_mean"] > 0 > green["cnfa.color.opponent_rg_mean"]


def test_mahotas_contrast_checkerboard():
    if _skip_if_unavailable(MahotasTextureAdapter):
        return
    a = MahotasTextureAdapter()
    uni = _run(a, _uniform())
    chk = _run(a, _checkerboard())
    assert chk["cnfa.haptic.haralick_contrast"] > uni["cnfa.haptic.haralick_contrast"]


if __name__ == "__main__":
    for fn in list(globals().values()):
        if callable(fn) and getattr(fn, "__name__", "").startswith("test_"):
            fn()
            print("PASS", fn.__name__)
    print("permissive adapter tests OK")
