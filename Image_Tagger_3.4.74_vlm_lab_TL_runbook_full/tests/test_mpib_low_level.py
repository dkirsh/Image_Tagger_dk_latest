from __future__ import annotations

import math
from pathlib import Path

import numpy as np

from backend.science.math.mpib_low_level import (
    MPIB_FEATURE_KEYS,
    MPIBLowLevelAnalyzer,
    extract_mpib_features,
)


ROOT = Path(__file__).resolve().parents[1]


def _synthetic_room_like_image() -> np.ndarray:
    image = np.zeros((96, 128, 3), dtype=np.uint8)
    image[:, :] = [180, 175, 160]
    image[12:72, 18:58] = [120, 95, 70]
    image[20:62, 72:116] = [210, 225, 240]
    image[75:92, :] = [90, 80, 70]
    return image


class _DummyFrame:
    def __init__(self, image: np.ndarray) -> None:
        self.original_image = image
        self.metadata = {}


def test_extract_mpib_features_emits_full_key_set() -> None:
    features = extract_mpib_features(_synthetic_room_like_image())

    assert set(features) == set(MPIB_FEATURE_KEYS)
    assert len(features) == 20
    finite_count = sum(math.isfinite(float(value)) for value in features.values())
    assert finite_count >= 18
    assert 0.0 <= features["brightness_mean"] <= 1.0
    assert 0.0 <= features["color_pct_neutral"] <= 1.0


def test_mpib_analyzer_writes_pipeline_metadata() -> None:
    frame = _DummyFrame(_synthetic_room_like_image())
    MPIBLowLevelAnalyzer().analyze(frame)

    artifact = frame.metadata["mpib_low_level"]
    assert artifact["method"] == "mpib_low_level_python_subset_v1"
    assert artifact["feature_count"] == 20
    assert set(artifact["features"]) == set(MPIB_FEATURE_KEYS)


def test_canonical_config_enables_mpib_by_default() -> None:
    service_text = (ROOT / "backend" / "services" / "science_runs.py").read_text()
    pipeline_text = (ROOT / "backend" / "science" / "pipeline.py").read_text()

    assert 'ACTIVE_SCIENCE_VERSION = "3.4.75-canonical-mpib-v1"' in service_text
    assert '"enable_mpib_low_level": True' in service_text
    assert "self.enable_mpib_low_level = enable_all" in pipeline_text
    assert "self.mpib_low_level.analyze(frame)" in pipeline_text
    assert 'artifact_type="mpib_low_level_json"' in pipeline_text
