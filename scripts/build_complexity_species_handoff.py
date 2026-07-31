#!/usr/bin/env python3
"""Build a durable complexity-species hypothesis and selection-queue handoff."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import cv2

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from cnfa_algs.complexity_species import (  # noqa: E402
    ComplexityContractError,
    hypothesize_complexity_species,
    write_handoff,
)

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp"}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build file-first complexity-species hypotheses and active-learning queues."
    )
    parser.add_argument("--corpus-root", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument(
        "--identify-jsonl",
        type=Path,
        help="Optional HITL identify rows used to populate disagreement.jsonl.",
    )
    return parser.parse_args()


def _load_identify_rows(path: Path | None) -> list[dict]:
    if path is None:
        return []
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ComplexityContractError(
                    f"{path}:{line_number}: invalid JSON: {exc.msg}"
                ) from exc
            rows.append(row)
    return rows


def build(corpus_root: Path, output_dir: Path, identify_jsonl: Path | None = None) -> dict:
    corpus_root = corpus_root.resolve()
    output_dir = output_dir.resolve()
    if not corpus_root.is_dir():
        raise ComplexityContractError(f"corpus root is not a directory: {corpus_root}")
    try:
        output_dir.relative_to(corpus_root)
    except ValueError:
        pass
    else:
        raise ComplexityContractError("--out must not be inside --corpus-root")

    image_paths = sorted(
        path
        for path in corpus_root.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    )
    if not image_paths:
        raise ComplexityContractError(f"no supported images under {corpus_root}")

    hypotheses = []
    for path in image_paths:
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        image = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if image is None:
            raise ComplexityContractError(f"OpenCV could not decode {path}")
        source_ref = path.relative_to(corpus_root).as_posix()
        hypotheses.append(
            hypothesize_complexity_species(
                image,
                image_id=digest,
                image_sha256=digest,
                source_ref=source_ref,
            )
        )
    return write_handoff(output_dir, hypotheses, _load_identify_rows(identify_jsonl))


def main() -> int:
    args = _parse_args()
    try:
        manifest = build(args.corpus_root, args.out, args.identify_jsonl)
    except ComplexityContractError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
