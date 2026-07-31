#!/usr/bin/env python3
"""Replay corpus_L6 into the flattened complexity review-pack contract."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics
import subprocess
import sys
from typing import Any, Iterable, Mapping

import cv2

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from cnfa_algs.complexity_species import (  # noqa: E402
    MODEL_VERSION,
    SPECIES_CONTRACT,
    ComplexityContractError,
    build_selection_queues,
    hypothesize_complexity_species,
)


REVIEW_ROW_SCHEMA = "cnfa.complexity-review-row/v1"
REVIEW_QUEUES_SCHEMA = "cnfa.complexity-review-queues/v1"
REPLAY_MANIFEST_SCHEMA = "cnfa.complexity-replay-manifest/v1"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp"}


def _canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def _atomic_write(path: Path, raw: bytes) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(raw)
    temporary.replace(path)


def _jsonl_bytes(rows: Iterable[Mapping[str, Any]]) -> bytes:
    return b"".join(_canonical_bytes(row) for row in rows)


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _percentile(values: list[float], quantile: float) -> float:
    if not values:
        raise ComplexityContractError("cannot take percentile of empty values")
    ordered = sorted(values)
    position = quantile * (len(ordered) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def _git_commit(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout.strip()


def _manifest_paths(corpus_root: Path) -> set[str]:
    manifest_path = corpus_root / "manifest.csv"
    if not manifest_path.is_file():
        raise ComplexityContractError(f"missing corpus manifest: {manifest_path}")
    with manifest_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows or "filename" not in rows[0]:
        raise ComplexityContractError("manifest.csv must contain filename rows")
    paths = [row["filename"] for row in rows]
    if len(paths) != len(set(paths)):
        raise ComplexityContractError("manifest.csv contains duplicate filenames")
    return set(paths)


def _choose_queues(
    hypotheses: list[Mapping[str, Any]],
    *,
    boundary_fraction: float,
    coverage_bins: int,
    coverage_per_bin: int,
) -> dict[str, Any]:
    if not 0.0 < boundary_fraction <= 1.0:
        raise ComplexityContractError("boundary_fraction must be in (0,1]")
    raw = build_selection_queues(hypotheses, severity_bins=coverage_bins)
    boundary_by_species: dict[str, list[dict[str, Any]]] = {}
    for row in raw["boundary"]:
        boundary_by_species.setdefault(row["species"], []).append(row)
    boundary = []
    for species in sorted(boundary_by_species):
        candidates = boundary_by_species[species]
        limit = max(1, math.ceil(len(candidates) * boundary_fraction))
        boundary.extend(candidates[:limit])

    coverage_groups: dict[tuple[str, int], list[dict[str, Any]]] = {}
    for row in raw["coverage"]:
        key = (row["species"], int(row["reason"]["severity_bin"]))
        coverage_groups.setdefault(key, []).append(row)
    coverage = []
    for (species, bin_index), candidates in sorted(coverage_groups.items()):
        center = (bin_index + 0.5) / coverage_bins
        candidates.sort(
            key=lambda row: (
                abs(float(row["reason"]["provisional_severity"]) - center),
                row["image_id"],
            )
        )
        coverage.extend(candidates[:coverage_per_bin])

    def compact(row: Mapping[str, Any]) -> dict[str, Any]:
        reason = row["reason"]
        value = reason.get("provisional_severity")
        if value is None:
            value = next(
                species_row["provisional_severity"]
                for hypothesis in hypotheses
                if hypothesis["image_id"] == row["image_id"]
                for species_row in hypothesis["species"]
                if species_row["species"] == row["species"]
            )
        return {
            "image_id": row["image_id"],
            "species": row["species"],
            "priority": row["priority"],
            "value": value,
        }

    boundary = [compact(row) for row in boundary]
    coverage = [compact(row) for row in coverage]
    boundary.sort(key=lambda row: (-row["priority"], row["species"], row["image_id"]))
    coverage.sort(key=lambda row: (row["species"], row["value"], row["image_id"]))
    return {
        "schema_version": REVIEW_QUEUES_SCHEMA,
        "policy": {
            "boundary": {
                "selection": "highest_uncertainty_near_provisional_presence_boundary",
                "fraction_per_computable_species": boundary_fraction,
            },
            "coverage": {
                "selection": "nearest_to_within_species_severity_bin_center",
                "severity_bins": coverage_bins,
                "maximum_per_occupied_bin": coverage_per_bin,
            },
            "disagreement": "empty_until_human_identification_rows_exist",
        },
        "boundary": boundary,
        "coverage": coverage,
        "disagreement": [],
    }


def _flatten(
    hypotheses: list[Mapping[str, Any]], queues: Mapping[str, Any]
) -> list[dict[str, Any]]:
    membership: dict[tuple[str, str], list[str]] = {}
    for queue_name in ("boundary", "coverage", "disagreement"):
        for row in queues[queue_name]:
            membership.setdefault((row["image_id"], row["species"]), []).append(queue_name)
    rows = []
    for hypothesis in sorted(hypotheses, key=lambda row: row["image_id"]):
        for species_row in hypothesis["species"]:
            severity = species_row["provisional_severity"]
            if species_row["status"] == "delegated":
                presence = "abstain"
            else:
                presence = (
                    "present" if float(species_row["presence_probability"]) >= 0.5 else "absent"
                )
            rows.append(
                {
                    "schema_version": REVIEW_ROW_SCHEMA,
                    "image_id": hypothesis["image_id"],
                    "path": hypothesis["source_ref"],
                    "species": species_row["species"],
                    "value": severity,
                    "presence": presence,
                    "uncertainty": species_row["uncertainty"],
                    "queue": membership.get((hypothesis["image_id"], species_row["species"]), []),
                    "model_version": hypothesis["model_version"],
                    "calibrated": False,
                }
            )
    return rows


def _audit(
    rows: list[Mapping[str, Any]],
    content_hashes: Mapping[str, list[str]],
) -> dict[str, Any]:
    by_species: dict[str, list[Mapping[str, Any]]] = {}
    for row in rows:
        by_species.setdefault(row["species"], []).append(row)
    species_audit = {}
    findings = []
    for species in sorted(by_species):
        species_rows = by_species[species]
        values = [float(row["value"]) for row in species_rows if row["value"] is not None]
        presence_counts = {
            label: sum(row["presence"] == label for row in species_rows)
            for label in ("present", "absent", "abstain")
        }
        if not values:
            species_audit[species] = {
                "status": "delegated",
                "n_rows": len(species_rows),
                "n_values": 0,
                "presence_counts": presence_counts,
            }
            continue
        ranked = sorted(
            ((float(row["value"]), row["image_id"]) for row in species_rows),
            key=lambda item: (item[0], item[1]),
        )
        near_zero = sum(value <= 0.01 for value in values)
        near_one = sum(value >= 0.99 for value in values)
        value_range = max(values) - min(values)
        unique = len({round(value, 6) for value in values})
        status = "ok"
        if unique < 10 or value_range < 0.10:
            status = "degenerate"
            findings.append(f"{species}: degenerate range/uniqueness")
        if near_zero / len(values) >= 0.25 or near_one / len(values) >= 0.25:
            status = "saturated"
            findings.append(f"{species}: >=25% of values saturated near 0 or 1")
        classified = presence_counts["present"] + presence_counts["absent"]
        presence_status = "ok"
        dominant_fraction = (
            max(presence_counts["present"], presence_counts["absent"]) / classified
            if classified
            else 0.0
        )
        if dominant_fraction == 1.0:
            presence_status = "degenerate"
            findings.append(f"{species}: provisional presence classification has one class")
        elif dominant_fraction >= 0.95:
            presence_status = "highly_imbalanced"
            findings.append(
                f"{species}: provisional presence classification is >=95% one class"
            )
        species_audit[species] = {
            "status": status,
            "presence_status": presence_status,
            "n_rows": len(species_rows),
            "n_values": len(values),
            "missing_values": len(species_rows) - len(values),
            "minimum": round(min(values), 6),
            "p05": round(_percentile(values, 0.05), 6),
            "median": round(statistics.median(values), 6),
            "mean": round(statistics.fmean(values), 6),
            "p95": round(_percentile(values, 0.95), 6),
            "maximum": round(max(values), 6),
            "unique_values_6dp": unique,
            "near_zero_count": near_zero,
            "near_one_count": near_one,
            "presence_counts": presence_counts,
            "dominant_presence_fraction": round(dominant_fraction, 6),
            "lowest_five": [image_id for _, image_id in ranked[:5]],
            "highest_five": [image_id for _, image_id in ranked[-5:][::-1]],
        }
    duplicate_groups = [sorted(paths) for paths in content_hashes.values() if len(paths) > 1]
    duplicate_groups.sort()
    duplicate_summary = {
        "source_to_pair_base_reuse": 0,
        "pair_only": 0,
        "other": 0,
    }
    for group in duplicate_groups:
        has_source = any(path.startswith(("interiors/", "collections/")) for path in group)
        has_pair = any(path.startswith("pairs/") for path in group)
        if has_source and has_pair:
            duplicate_summary["source_to_pair_base_reuse"] += 1
        elif all(path.startswith("pairs/") for path in group):
            duplicate_summary["pair_only"] += 1
        else:
            duplicate_summary["other"] += 1
    if duplicate_summary["pair_only"]:
        findings.append(
            f'{duplicate_summary["pair_only"]} pair-only duplicate-content groups require review'
        )
    if duplicate_summary["other"]:
        findings.append(
            f'{duplicate_summary["other"]} uncategorized duplicate-content groups require review'
        )
    return {
        "species": species_audit,
        "duplicate_content_groups": duplicate_groups,
        "duplicate_content_summary": duplicate_summary,
        "findings": findings,
    }


def build_review_pack(
    corpus_root: str | Path,
    output_dir: str | Path,
    *,
    generated_commit: str | None = None,
    boundary_fraction: float = 0.10,
    coverage_bins: int = 5,
    coverage_per_bin: int = 8,
) -> dict[str, Any]:
    corpus = Path(corpus_root).resolve()
    output = Path(output_dir).resolve()
    if not corpus.is_dir():
        raise ComplexityContractError(f"corpus root is not a directory: {corpus}")
    try:
        output.relative_to(corpus)
    except ValueError:
        pass
    else:
        raise ComplexityContractError("output directory must not be inside the corpus")

    listed_paths = _manifest_paths(corpus)
    image_paths = sorted(
        path
        for path in corpus.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    )
    if not image_paths:
        raise ComplexityContractError("corpus contains no supported images")

    hypotheses = []
    content_hashes: dict[str, list[str]] = {}
    for image_path in image_paths:
        relative = image_path.relative_to(corpus).as_posix()
        raw = image_path.read_bytes()
        digest = _sha256(raw)
        content_hashes.setdefault(digest, []).append(relative)
        image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
        if image is None:
            raise ComplexityContractError(f"OpenCV could not decode {relative}")
        hypotheses.append(
            hypothesize_complexity_species(
                image,
                image_id=relative,
                image_sha256=digest,
                source_ref=relative,
            )
        )

    queues = _choose_queues(
        hypotheses,
        boundary_fraction=boundary_fraction,
        coverage_bins=coverage_bins,
        coverage_per_bin=coverage_per_bin,
    )
    rows = _flatten(hypotheses, queues)
    expected_rows = len(image_paths) * len(SPECIES_CONTRACT)
    if len(rows) != expected_rows:
        raise ComplexityContractError(f"expected {expected_rows} rows, produced {len(rows)}")

    output.mkdir(parents=True, exist_ok=True)
    hypotheses_raw = _jsonl_bytes(rows)
    queues_raw = (json.dumps(queues, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    filesystem_only = sorted(
        path.relative_to(corpus).as_posix()
        for path in image_paths
        if path.relative_to(corpus).as_posix() not in listed_paths
    )
    missing_files = sorted(listed_paths - {path.relative_to(corpus).as_posix() for path in image_paths})
    audit = _audit(rows, content_hashes)
    manifest = {
        "schema_version": REPLAY_MANIFEST_SCHEMA,
        "corpus": corpus.name,
        "n_images": len(image_paths),
        "n_manifest_rows": len(listed_paths),
        "n_hypothesis_rows": len(rows),
        "filesystem_only_images": filesystem_only,
        "manifest_missing_files": missing_files,
        "species": list(SPECIES_CONTRACT),
        "generated_commit": generated_commit or _git_commit(REPO_ROOT),
        "model_version": MODEL_VERSION,
        "calibrated": False,
        "files": {
            "hypotheses_corpusL6.jsonl": {
                "rows": len(rows),
                "sha256": _sha256(hypotheses_raw),
            },
            "queues.json": {
                "boundary_rows": len(queues["boundary"]),
                "coverage_rows": len(queues["coverage"]),
                "disagreement_rows": 0,
                "sha256": _sha256(queues_raw),
            },
        },
        "qa": audit,
        "notes": [
            "all filesystem images are included, including images absent from manifest.csv",
            "image_id and path are corpus-relative paths; content duplicates remain distinct corpus items",
            "presence and severity are uncalibrated tagger hypotheses, not answer keys",
            "semantic_incongruity and concealed_order abstain from pixel-only scoring",
        ],
    }
    manifest["manifest_hash"] = _sha256(_canonical_bytes(manifest))
    manifest_raw = (json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()

    _atomic_write(output / "hypotheses_corpusL6.jsonl", hypotheses_raw)
    _atomic_write(output / "queues.json", queues_raw)
    _atomic_write(output / "replay_manifest.json", manifest_raw)
    return manifest


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--generated-commit")
    parser.add_argument("--boundary-fraction", type=float, default=0.10)
    parser.add_argument("--coverage-bins", type=int, default=5)
    parser.add_argument("--coverage-per-bin", type=int, default=8)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    try:
        manifest = build_review_pack(
            args.corpus_root,
            args.out,
            generated_commit=args.generated_commit,
            boundary_fraction=args.boundary_fraction,
            coverage_bins=args.coverage_bins,
            coverage_per_bin=args.coverage_per_bin,
        )
    except (ComplexityContractError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
