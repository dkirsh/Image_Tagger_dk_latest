from __future__ import annotations

import math
from pathlib import Path

import cv2
import numpy as np

from backend.science.core import AnalysisFrame
from backend.science.math.architectural_primitives import (
    CNFA_DIRECT_STATS_KEYS,
    ArchitecturalPrimitivesAnalyzer,
    compute_direct_stats,
)


FIXTURE_DIR = Path("tests/fixtures/architectural_tags")


def _write_rgb(path: Path, image: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    bgr = cv2.cvtColor(image.astype(np.uint8), cv2.COLOR_RGB2BGR)
    cv2.imwrite(str(path), bgr)


def _make_fixtures() -> dict[str, Path]:
    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)

    flat = np.full((96, 128, 3), 128, dtype=np.uint8)

    high_edge = np.zeros((96, 128, 3), dtype=np.uint8)
    tile = 8
    for y in range(0, high_edge.shape[0], tile):
        for x in range(0, high_edge.shape[1], tile):
            if ((x // tile) + (y // tile)) % 2 == 0:
                high_edge[y : y + tile, x : x + tile] = 255

    high_color = np.zeros((96, 128, 3), dtype=np.uint8)
    yy, xx = np.indices(high_color.shape[:2])
    high_color[..., 0] = (xx * 5) % 256
    high_color[..., 1] = (yy * 7) % 256
    high_color[..., 2] = ((xx + yy) * 3) % 256

    symmetric = np.full((96, 128, 3), 90, dtype=np.uint8)
    symmetric[:, 10:25] = [220, 220, 220]
    symmetric[:, -25:-10] = [220, 220, 220]
    symmetric[30:65, 45:83] = [30, 30, 30]

    asymmetric = np.full((96, 128, 3), 90, dtype=np.uint8)
    asymmetric[10:70, 10:38] = [220, 220, 220]
    asymmetric[35:90, 80:122] = [30, 30, 30]

    low_brightness_variance = np.full((96, 128, 3), 140, dtype=np.uint8)

    high_brightness_variance = np.zeros((96, 128, 3), dtype=np.uint8)
    high_brightness_variance[:, :64] = 20
    high_brightness_variance[:, 64:] = 235

    fixtures = {
        "flat": flat,
        "high_edge": high_edge,
        "high_color": high_color,
        "symmetric": symmetric,
        "asymmetric": asymmetric,
        "low_brightness_variance": low_brightness_variance,
        "high_brightness_variance": high_brightness_variance,
    }

    paths = {}
    for name, image in fixtures.items():
        path = FIXTURE_DIR / f"{name}.png"
        _write_rgb(path, image)
        paths[name] = path

    readme = FIXTURE_DIR / "README.md"
    readme.write_text(
        "# Architectural direct-stat fixtures\n\n"
        "Deterministic synthetic PNG fixtures for Sprint S1 direct-stat tests.\n"
        "They cover flat, high-edge, high-color-variety, symmetric, asymmetric, "
        "and low/high brightness variance cases.\n"
    )

    return paths


def _read_rgb(path: Path) -> np.ndarray:
    bgr = cv2.imread(str(path), cv2.IMREAD_COLOR)
    assert bgr is not None, f"Could not read fixture {path}"
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)


def test_direct_stats_emit_finite_canonical_keys() -> None:
    paths = _make_fixtures()
    image = _read_rgb(paths["high_color"])

    values = compute_direct_stats(image)

    assert set(values) == set(CNFA_DIRECT_STATS_KEYS)
    for key, value in values.items():
        assert math.isfinite(float(value)), key
        assert 0.0 <= float(value) <= 1.0, key


def test_direct_stats_are_deterministic() -> None:
    paths = _make_fixtures()
    image = _read_rgb(paths["high_edge"])

    first = compute_direct_stats(image)
    second = compute_direct_stats(image)

    assert first == second


def test_direct_stats_expected_monotonic_fixture_directions() -> None:
    paths = _make_fixtures()

    flat = compute_direct_stats(_read_rgb(paths["flat"]))
    high_edge = compute_direct_stats(_read_rgb(paths["high_edge"]))
    high_color = compute_direct_stats(_read_rgb(paths["high_color"]))
    symmetric = compute_direct_stats(_read_rgb(paths["symmetric"]))
    asymmetric = compute_direct_stats(_read_rgb(paths["asymmetric"]))
    low_var = compute_direct_stats(_read_rgb(paths["low_brightness_variance"]))
    high_var = compute_direct_stats(_read_rgb(paths["high_brightness_variance"]))

    assert high_var["cnfa.light.brightness_variance"] > low_var["cnfa.light.brightness_variance"]
    assert high_edge["cnfa.fluency.edge_clarity_mean"] > flat["cnfa.fluency.edge_clarity_mean"]
    assert high_color["cnfa.fluency.color_palette_entropy"] > flat["cnfa.fluency.color_palette_entropy"]
    assert symmetric["cnfa.fluency.symmetry_score_horizontal"] > asymmetric["cnfa.fluency.symmetry_score_horizontal"]
    assert high_edge["cnfa.fractal_dimension"] >= flat["cnfa.fractal_dimension"]
    assert high_color["cnfa.fluency.processing_load_proxy"] > flat["cnfa.fluency.processing_load_proxy"]


def test_analyzer_adds_attributes_to_analysis_frame() -> None:
    paths = _make_fixtures()
    image = _read_rgb(paths["high_color"])

    frame = AnalysisFrame(image_id=1, original_image=image)
    ArchitecturalPrimitivesAnalyzer().analyze(frame)

    for key in CNFA_DIRECT_STATS_KEYS:
        assert key in frame.attributes
        assert math.isfinite(float(frame.attributes[key]))
        assert 0.0 <= float(frame.attributes[key]) <= 1.0
        assert frame.metadata[key]["confidence"] == 1.0

    assert frame.metadata["cnfa_direct_stats"]["method"] == "deterministic_opencv_numpy_v1"


def test_direct_stats_blank_image_fails_safely() -> None:
    blank = np.zeros((32, 32, 3), dtype=np.uint8)
    values = compute_direct_stats(blank)

    for key, value in values.items():
        assert math.isfinite(float(value)), key
        assert 0.0 <= float(value) <= 1.0, key
