"""Replay-contract and negative-control tests for the complexity review pack."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
import pytest

from cnfa_algs.complexity_species import ComplexityContractError, SPECIES_CONTRACT
from scripts.build_complexity_review_pack import build_review_pack


def _write_image(path: Path, image: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    assert cv2.imwrite(str(path), image)


def _make_corpus(root: Path) -> None:
    images = {
        "interiors/blank.png": np.full((96, 128, 3), 128, np.uint8),
        "interiors/grid.png": np.tile(
            ((np.indices((96, 128)).sum(axis=0) % 8) == 0)[:, :, None] * 255,
            (1, 1, 3),
        ).astype(np.uint8),
        "collections/noise.png": np.random.default_rng(4).integers(
            0, 256, size=(96, 128, 3), dtype=np.uint8
        ),
    }
    images["collections/blank_copy.png"] = images["interiors/blank.png"].copy()
    for relative, image in images.items():
        _write_image(root / relative, image)
    with (root / "manifest.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["filename", "category"])
        writer.writeheader()
        for relative in sorted(images):
            if relative == "collections/blank_copy.png":
                continue
            writer.writerow({"filename": relative, "category": "fixture"})


def _verify_manifest_hash(manifest: dict) -> None:
    recorded = manifest.pop("manifest_hash")
    raw = (
        json.dumps(manifest, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
    ).encode()
    assert hashlib.sha256(raw).hexdigest() == recorded


def test_review_pack_contract_counts_hashes_and_abstentions(tmp_path: Path):
    corpus = tmp_path / "corpus_fixture"
    output = tmp_path / "review"
    _make_corpus(corpus)
    manifest = build_review_pack(corpus, output, generated_commit="fixture-commit")

    assert {path.name for path in output.iterdir()} == {
        "hypotheses_corpusL6.jsonl",
        "queues.json",
        "replay_manifest.json",
    }
    assert manifest["n_images"] == 4
    assert manifest["n_manifest_rows"] == 3
    assert manifest["n_hypothesis_rows"] == 4 * len(SPECIES_CONTRACT)
    assert manifest["filesystem_only_images"] == ["collections/blank_copy.png"]
    rows = [
        json.loads(line)
        for line in (output / "hypotheses_corpusL6.jsonl").read_text().splitlines()
    ]
    assert len(rows) == 24
    assert all(not Path(row["path"]).is_absolute() for row in rows)
    assert all(row["image_id"] == row["path"] for row in rows)
    assert all(row["calibrated"] is False for row in rows)
    assert all(isinstance(row["queue"], list) for row in rows)
    late = [row for row in rows if row["species"] in ("semantic_incongruity", "concealed_order")]
    assert all(row["presence"] == "abstain" and row["value"] is None for row in late)

    for filename in ("hypotheses_corpusL6.jsonl", "queues.json"):
        raw = (output / filename).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == manifest["files"][filename]["sha256"]
    _verify_manifest_hash(dict(manifest))


def test_duplicate_content_is_reported_but_items_remain_distinct(tmp_path: Path):
    corpus = tmp_path / "corpus_fixture"
    output = tmp_path / "review"
    _make_corpus(corpus)
    manifest = build_review_pack(corpus, output, generated_commit="fixture-commit")
    groups = manifest["qa"]["duplicate_content_groups"]
    assert any(
        group == ["collections/blank_copy.png", "interiors/blank.png"] for group in groups
    )
    rows = [
        json.loads(line)
        for line in (output / "hypotheses_corpusL6.jsonl").read_text().splitlines()
    ]
    image_ids = {row["image_id"] for row in rows}
    assert "collections/blank_copy.png" in image_ids
    assert "interiors/blank.png" in image_ids
    assert manifest["qa"]["duplicate_content_summary"]["other"] == 1
    assert any("uncategorized duplicate-content" in item for item in manifest["qa"]["findings"])


def test_queue_membership_matches_queue_file(tmp_path: Path):
    corpus = tmp_path / "corpus_fixture"
    output = tmp_path / "review"
    _make_corpus(corpus)
    build_review_pack(
        corpus,
        output,
        generated_commit="fixture-commit",
        boundary_fraction=0.25,
        coverage_bins=3,
        coverage_per_bin=1,
    )
    queues = json.loads((output / "queues.json").read_text())
    rows = [
        json.loads(line)
        for line in (output / "hypotheses_corpusL6.jsonl").read_text().splitlines()
    ]
    membership = {
        (row["image_id"], row["species"], queue_name)
        for queue_name in ("boundary", "coverage")
        for row in queues[queue_name]
    }
    for row in rows:
        for queue_name in row["queue"]:
            assert (row["image_id"], row["species"], queue_name) in membership
    assert queues["disagreement"] == []


def test_review_pack_is_deterministic_for_fixed_commit(tmp_path: Path):
    corpus = tmp_path / "corpus_fixture"
    first = tmp_path / "first"
    second = tmp_path / "second"
    _make_corpus(corpus)
    build_review_pack(corpus, first, generated_commit="fixture-commit")
    build_review_pack(corpus, second, generated_commit="fixture-commit")
    for filename in ("hypotheses_corpusL6.jsonl", "queues.json", "replay_manifest.json"):
        assert (first / filename).read_bytes() == (second / filename).read_bytes()


def test_output_inside_corpus_is_rejected(tmp_path: Path):
    corpus = tmp_path / "corpus_fixture"
    _make_corpus(corpus)
    with pytest.raises(ComplexityContractError, match="must not be inside"):
        build_review_pack(corpus, corpus / "review", generated_commit="fixture-commit")
