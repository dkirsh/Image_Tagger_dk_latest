"""Contract, negative-control, and handoff tests for complexity species."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
import pytest

from cnfa_algs.complexity_species import (
    ComplexityContractError,
    HYPOTHESIS_SCHEMA,
    SPECIES_CONTRACT,
    build_selection_queues,
    hypothesize_complexity_species,
    validate_hypothesis_record,
    write_handoff,
)


def _record(image: np.ndarray, image_id: str = "fixture") -> dict:
    return hypothesize_complexity_species(image, image_id=image_id, source_ref=f"{image_id}.png")


def _species(record: dict, name: str) -> dict:
    return next(row for row in record["species"] if row["species"] == name)


def test_complete_species_contract_and_late_species_abstain():
    image = np.full((160, 240, 3), 128, np.uint8)
    record = _record(image)
    assert record["schema_version"] == HYPOTHESIS_SCHEMA
    assert {row["species"] for row in record["species"]} == set(SPECIES_CONTRACT)

    for name in ("semantic_incongruity", "concealed_order"):
        row = _species(record, name)
        assert row["status"] == "delegated"
        assert row["presence_probability"] is None
        assert row["provisional_severity"] is None
        assert row["confidence"] == 0.0
        assert row["uncertainty"] == 1.0


def test_surface_density_orders_blank_below_dense_and_retains_two_scales():
    blank = np.full((256, 256, 3), 128, np.uint8)
    dense = np.zeros((256, 256, 3), np.uint8)
    dense[::4, :] = 255
    dense[:, ::4] = 255
    low = _species(_record(blank, "blank"), "surface_density")
    high = _species(_record(dense, "dense"), "surface_density")
    assert high["provisional_severity"] > low["provisional_severity"]
    assert set(("coarse", "fine")) <= set(high["components"])
    assert high["calibration"] == "engineering_proxy_uncalibrated"
    assert high["components"]["presence_mapping"]["kind"] == "provisional_logistic"
    assert high["presence_probability"] != high["provisional_severity"]


def test_arrangement_disorder_is_deterministic_and_weak():
    rng = np.random.default_rng(7)
    image = rng.integers(0, 256, size=(256, 256, 3), dtype=np.uint8)
    first = _species(_record(image, "one"), "arrangement_disorder")
    second = _species(_record(image, "two"), "arrangement_disorder")
    assert first["provisional_severity"] == second["provisional_severity"]
    assert first["components"] == second["components"]
    assert first["confidence"] <= 0.25
    assert any("WEAK" in item for item in first["failure_modes"])


def test_arrangement_disorder_orders_regular_below_scattered_same_elements():
    ordered = np.zeros((256, 256, 3), np.uint8)
    for y in range(24, 232, 32):
        for x in range(24, 232, 32):
            ordered[y:y + 8, x:x + 8] = 255
    scattered = np.zeros_like(ordered)
    for y, x in np.random.default_rng(3).integers(0, 248, size=(49, 2)):
        scattered[y:y + 8, x:x + 8] = 255
    regular_score = _species(_record(ordered, "regular"), "arrangement_disorder")
    scattered_score = _species(_record(scattered, "scattered"), "arrangement_disorder")
    assert scattered_score["provisional_severity"] > regular_score["provisional_severity"]


def test_textural_discomfort_preserves_normalized_fraction_without_saturation():
    blank = np.full((256, 256, 3), 128, np.uint8)
    stripes = np.zeros_like(blank)
    stripes[:, ::4] = 255
    blank_row = _species(_record(blank, "blank-texture"), "textural_discomfort")
    stripes_row = _species(_record(stripes, "striped-texture"), "textural_discomfort")
    assert blank_row["provisional_severity"] < stripes_row["provisional_severity"] < 1.0
    assert stripes_row["provisional_severity"] == pytest.approx(
        stripes_row["components"]["spectral_fraction_raw"], abs=1e-6
    )


def test_validator_rejects_fake_late_score_and_out_of_range_probability():
    record = _record(np.zeros((64, 64, 3), np.uint8))
    bad_late = copy.deepcopy(record)
    late = _species(bad_late, "semantic_incongruity")
    late["presence_probability"] = 0.9
    with pytest.raises(ComplexityContractError, match="must abstain"):
        validate_hypothesis_record(bad_late)

    bad_probability = copy.deepcopy(record)
    _species(bad_probability, "surface_density")["presence_probability"] = 1.1
    with pytest.raises(ComplexityContractError, match=r"\[0,1\]"):
        validate_hypothesis_record(bad_probability)


def test_validator_rejects_metadata_drift_and_duplicate_species():
    record = _record(np.zeros((64, 64, 3), np.uint8))
    wrong_metadata = copy.deepcopy(record)
    _species(wrong_metadata, "surface_density")["stage"] = "late"
    with pytest.raises(ComplexityContractError, match="violates"):
        validate_hypothesis_record(wrong_metadata)

    duplicate = copy.deepcopy(record)
    duplicate["species"][-1] = copy.deepcopy(duplicate["species"][0])
    with pytest.raises(ComplexityContractError, match="exactly once"):
        validate_hypothesis_record(duplicate)


def test_boundary_coverage_and_disagreement_queues():
    mid = np.zeros((180, 180, 3), np.uint8)
    cv2.randu(mid, 64, 192)
    records = [_record(mid, "a"), _record(np.full_like(mid, 128), "b")]
    identify = [
        {"type": "identify", "image_id": "a", "species": "surface_density", "present": "no"},
        {"type": "identify", "image_id": "a", "species": "surface_density", "present": "no"},
        {
            "type": "identify",
            "image_id": "a",
            "species": "surface_density",
            "present": "cannot_tell",
        },
    ]
    queues = build_selection_queues(records, identify, severity_bins=4)
    assert queues["boundary"]
    assert queues["coverage"]
    assert len(queues["disagreement"]) == 1
    disagreement = queues["disagreement"][0]
    assert disagreement["reason"]["human_identification_count"] == 2
    assert disagreement["priority"] == pytest.approx(
        _species(records[0], "surface_density")["presence_probability"]
    )
    assert all(row["species"] not in ("semantic_incongruity", "concealed_order")
               for row in queues["boundary"])


def test_bad_identify_row_is_rejected():
    record = _record(np.zeros((64, 64, 3), np.uint8))
    bad = [{"type": "identify", "image_id": "fixture", "species": "surface_density",
            "present": "probably"}]
    with pytest.raises(ComplexityContractError, match="yes, no, or cannot_tell"):
        build_selection_queues([record], bad)


def test_handoff_is_deterministic_and_hashes_match(tmp_path: Path):
    records = [
        _record(np.full((64, 64, 3), 128, np.uint8), "b"),
        _record(np.zeros((64, 64, 3), np.uint8), "a"),
    ]
    first = tmp_path / "first"
    second = tmp_path / "second"
    manifest_one = write_handoff(first, records)
    manifest_two = write_handoff(second, reversed(records))
    assert manifest_one == manifest_two
    assert set(manifest_one["files"]) == {
        "hypotheses.jsonl",
        "boundary.jsonl",
        "coverage.jsonl",
        "disagreement.jsonl",
    }
    for filename, metadata in manifest_one["files"].items():
        raw = (first / filename).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == metadata["sha256"]
        assert raw == (second / filename).read_bytes()
    rows = [json.loads(line) for line in (first / "hypotheses.jsonl").read_text().splitlines()]
    assert [row["image_id"] for row in rows] == ["a", "b"]


def test_source_ref_must_not_leak_absolute_path():
    image = np.zeros((32, 32, 3), np.uint8)
    with pytest.raises(ComplexityContractError, match="corpus-relative"):
        hypothesize_complexity_species(image, image_id="bad", source_ref="/private/corpus/a.png")
