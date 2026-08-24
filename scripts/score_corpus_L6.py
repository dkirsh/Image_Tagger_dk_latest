#!/usr/bin/env python3
"""scripts/score_corpus_L6.py — Sprint E: run the Tagger over corpus_L6 and emit scores.csv.

The bridge from the annotator (annotation_socket.annotator.annotate_image) to the Sprint A
database (scripts/corpus_db.py). Reads corpus_L6/manifest.csv, resolves each filename to a
local image, annotates it, flattens the record to long-format rows, computes
pctile_in_corpus per attr_id, and writes corpus_L6/scores.csv atomically.

Output columns (exactly scripts/corpus_db.SCORE_COLUMNS, plus honest provenance extras):
  filename,attr_id,value,tier,confidence,abstained,m1p_digest,computed_utc,pctile_in_corpus
  + status,reason,model_version   (extras; corpus_db ignores unknown columns)

Honesty contract (Sprint E §10/§11/§20):
  * This script NEVER fabricates a score. If the annotator cannot be imported it refuses to
    write scores.csv and reports the exact import failure.
  * A fake annotator can only be supplied programmatically (run(..., annotate_fn=...)), which
    is how the tests exercise the pipeline. There is no CLI flag that fakes production scores.
  * m1p_digest is written only when the record actually carries one. No digest -> empty.

Determinism: single-threaded BLAS/OMP + cv2.setNumThreads(1), fixed row ordering
(filename, attr_id), midpoint-rank percentiles with deterministic tie handling.

Run:
  PYTHONPATH=. python3 scripts/score_corpus_L6.py --corpus-dir corpus_L6 \
      --out corpus_L6/scores.csv --limit 10 --dry-run
  PYTHONPATH=. python3 scripts/score_corpus_L6.py --corpus-dir corpus_L6 \
      --out corpus_L6/scores.csv --limit 10 --resume --rebuild-db
"""
from __future__ import annotations

# --- determinism: pin thread counts BEFORE numpy/cv2/cnfa_algs are imported anywhere ------
import os as _os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    _os.environ.setdefault(_v, "1")

import argparse
import csv
import hashlib
import json
import math
import os
import platform
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CORPUS_DIR = ROOT / "corpus_L6"
DEFAULT_SCORES_NAME = "scores.csv"

# The required schema, in order. Kept identical to corpus_db.SCORE_COLUMNS; verified at
# runtime by _assert_schema_matches_corpus_db() so the two files cannot silently drift.
SCORE_COLUMNS: Tuple[str, ...] = (
    "filename", "attr_id", "value", "tier", "confidence", "abstained",
    "m1p_digest", "computed_utc", "pctile_in_corpus",
)
# Honest provenance extras (corpus_db ignores columns it does not know).
EXTRA_COLUMNS: Tuple[str, ...] = (
    "status", "reason", "model_version", "image_complete",
    "image_score_count", "image_attr_ids_sha256",
)
OUT_COLUMNS: Tuple[str, ...] = SCORE_COLUMNS + EXTRA_COLUMNS

# manifest filename aliases (Sprint E §9)
FILENAME_KEYS: Tuple[str, ...] = ("filename", "path", "image", "file", "rel_path")

# record-flattening aliases (Sprint E §11)
ATTR_KEYS = ("attr_id", "predicate", "key", "name", "id")
VALUE_KEYS = ("value", "score", "scalar", "result")
TIER_KEYS = ("tier", "tier_hint", "level")
CONF_KEYS = ("confidence", "conf")
ABSTAIN_KEYS = ("abstained", "abstain", "is_abstained")
DIGEST_KEYS = ("m1p_digest", "digest", "m1_digest", "audit_digest", "signature")
# containers that may hold the per-attribute list/dict inside a record
SCORE_CONTAINER_KEYS = ("scores", "predicates", "attributes", "results", "values")


class AnnotatorUnavailable(RuntimeError):
    """The real annotator cannot be imported/run in this environment.

    Carries the precise failure so the run report and the operator get an actionable
    blocker rather than a stack trace or, worse, a silently empty scores.csv."""

    def __init__(self, reason: str, detail: str = "", hint: str = ""):
        self.reason, self.detail, self.hint = reason, detail, hint
        super().__init__(reason if not detail else f"{reason}: {detail}")

    def as_dict(self) -> Dict[str, str]:
        return {"reason": self.reason, "detail": self.detail, "hint": self.hint}


# --------------------------------------------------------------------------- small helpers
def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def first_present(row: Dict[str, str], keys: Sequence[str]) -> Optional[str]:
    """First non-empty value among `keys`, matched case-insensitively."""
    lowered = {(k or "").strip().lower(): v for k, v in row.items()}
    for k in keys:
        v = lowered.get(k)
        if v is not None and str(v).strip() != "":
            return str(v).strip()
    return None


def float_or_none(v) -> Optional[float]:
    if v is None or (isinstance(v, str) and not v.strip()):
        return None
    if isinstance(v, bool):
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return None if (math.isnan(f) or math.isinf(f)) else f


def _get(obj, key):
    """Read `key` from a dict or an object attribute; None if absent."""
    if isinstance(obj, dict):
        return obj.get(key)
    return getattr(obj, key, None)


def _first_attr(obj, keys: Sequence[str]):
    for k in keys:
        v = _get(obj, k)
        if v is not None and not (isinstance(v, str) and not v.strip()):
            return v
    return None


def _truthy_int(v) -> int:
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, (int, float)):
        return int(bool(v))
    if isinstance(v, str):
        return int(v.strip().lower() in ("1", "true", "yes", "y", "t"))
    return 0


# --------------------------------------------------------------------------- manifest / paths
def read_manifest(manifest_path: Path) -> List[Dict[str, str]]:
    if not manifest_path.exists():
        raise FileNotFoundError(f"manifest not found: {manifest_path}")
    with manifest_path.open(newline="", encoding="utf-8") as fh:
        return [dict(r) for r in csv.DictReader(fh)]


def manifest_filenames(rows: Iterable[Dict[str, str]]) -> List[str]:
    """Manifest filenames in file order, de-duplicated, preserving first occurrence."""
    out, seen = [], set()
    for r in rows:
        fn = first_present(r, FILENAME_KEYS)
        if fn and fn not in seen:
            seen.add(fn)
            out.append(fn)
    return out


def resolve_image_path(filename: str, corpus_dir: Path,
                       repo_root: Path = ROOT) -> Optional[Path]:
    """Resolve a manifest filename to a local file (Sprint E §9).

    1. absolute path that exists
    2. corpus_dir / filename
    3. repo_root / filename
    4. corpus_dir / basename  (flat layouts)
    Returns None if nothing exists on disk."""
    if not filename:
        return None
    raw = filename.strip()
    p = Path(raw)
    if p.is_absolute():
        return p if p.exists() else None

    # normalize './x' and a leading 'corpus_L6/' that duplicates corpus_dir
    rel = Path(os.path.normpath(raw))
    candidates = [corpus_dir / rel, repo_root / rel]
    parts = rel.parts
    if parts and parts[0] == corpus_dir.name:
        stripped = Path(*parts[1:]) if len(parts) > 1 else None
        if stripped is not None:
            candidates.insert(0, corpus_dir / stripped)
    candidates.append(corpus_dir / rel.name)

    for c in candidates:
        if c.exists() and c.is_file():
            return c
    return None


# --------------------------------------------------------------------------- the annotator
def load_annotator() -> Callable[[str], Dict]:
    """Import the repo's single-image annotator, or raise AnnotatorUnavailable.

    We import lazily and translate ImportError into a structured blocker: annotator.py
    imports `cpp.stage` (the external CPP control library) at module scope, which is not
    vendored in this checkout."""
    try:
        sys.path.insert(0, str(ROOT))
        from annotation_socket.annotator import annotate_image  # type: ignore
    except ImportError as e:
        missing = getattr(e, "name", None) or str(e)
        raise AnnotatorUnavailable(
            reason=f"cannot import annotation_socket.annotator (missing module: {missing})",
            detail=f"{type(e).__name__}: {e}",
            hint=("annotation_socket/annotator.py imports the external CPP control library "
                  "(`from cpp import stage`, expected at /Users/davidusa/REPOS/_control/cpp). "
                  "It is not present in this checkout. Vendor or path-add that library to "
                  "enable real scoring; do not stub it — it enforces the [W:] write boundary."),
        ) from e
    except Exception as e:                    # pragma: no cover - defensive
        raise AnnotatorUnavailable(
            reason="annotation_socket.annotator failed to import",
            detail=f"{type(e).__name__}: {e}") from e
    return annotate_image


def configure_determinism() -> Dict[str, object]:
    """Pin thread counts where we safely can; report what we actually did."""
    info: Dict[str, object] = {
        "env": {v: os.environ.get(v) for v in
                ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                 "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")},
        "cv2_imported": False, "cv2_version": None, "cv2_threads_set": False,
    }
    try:
        import cv2  # noqa: F401
    except Exception:
        return info
    info["cv2_imported"] = True
    info["cv2_version"] = getattr(cv2, "__version__", None)
    try:
        cv2.setNumThreads(1)
        info["cv2_threads_set"] = True
    except Exception:                          # pragma: no cover - defensive
        pass
    return info


# --------------------------------------------------------------------------- flattening
def _iter_score_entries(record) -> List:
    """Yield the per-attribute entries from a record of unknown shape (Sprint E §11).

    Handles: {"scores": [ ... ]}, {"predicates": {...}}, a bare list, or a mapping of
    attr_id -> value/dict."""
    if record is None:
        return []
    if isinstance(record, (list, tuple)):
        return list(record)

    for key in SCORE_CONTAINER_KEYS:
        container = _get(record, key)
        if container is None:
            continue
        if isinstance(container, (list, tuple)):
            return list(container)
        if isinstance(container, dict):
            out = []
            for attr_id, v in container.items():
                if isinstance(v, dict):
                    e = dict(v)
                    e.setdefault("attr_id", attr_id)
                    out.append(e)
                else:
                    out.append({"attr_id": attr_id, "value": v})
            return out
    # a bare mapping of attr -> scalar, as a last resort
    if isinstance(record, dict) and record and all(
            not isinstance(v, (dict, list)) for v in record.values()):
        return [{"attr_id": k, "value": v} for k, v in record.items()]
    return []


def _extract_digest(entry) -> str:
    """m1p digest, if the entry genuinely carries one. Never invented."""
    m1p = _get(entry, "m1p")
    if isinstance(m1p, dict):
        for k in DIGEST_KEYS:
            v = m1p.get(k)
            if isinstance(v, str) and v.strip():
                return v.strip()
        return ""            # e.g. {"error": "emit_failed:..."} — no digest to claim
    v = _first_attr(entry, DIGEST_KEYS)
    return str(v).strip() if isinstance(v, str) and v.strip() else ""


def _extract_confidence(entry) -> Optional[float]:
    c = float_or_none(_first_attr(entry, CONF_KEYS))
    if c is not None:
        return c
    ev = _get(entry, "evidence")
    if isinstance(ev, dict):
        return float_or_none(ev.get("confidence"))
    return None


def flatten_record(filename: str, record, computed_utc: str) -> List[Dict[str, object]]:
    """Flatten one annotation record into long-format score rows.

    Truth rules:
      * a finite numeric value with a non-abstained status -> a scored row (abstained=0)
      * anything else (ABSTAINED / UNKNOWN / non-numeric / missing value) -> an explicit
        abstention row (abstained=1, value empty). We emit the row rather than dropping it,
        so coverage gaps are visible in the DB instead of invisible.
    """
    rows: List[Dict[str, object]] = []
    model_version = str(_get(record, "model_version") or "")

    for entry in _iter_score_entries(record):
        attr_id = _first_attr(entry, ATTR_KEYS)
        if attr_id is None:
            continue
        attr_id = str(attr_id).strip()
        if not attr_id:
            continue

        status = str(_get(entry, "status") or "").strip()
        value = float_or_none(_first_attr(entry, VALUE_KEYS))
        declared_abstain = _first_attr(entry, ABSTAIN_KEYS)

        abstained = 0
        reason = ""
        if declared_abstain is not None and _truthy_int(declared_abstain):
            abstained, reason = 1, (str(_get(entry, "reason") or "").strip() or "declared_abstained")
        elif status.upper() == "ABSTAINED":
            missing = _get(entry, "missing_inputs")
            reason = (str(_get(entry, "reason") or "").strip()
                      or (f"missing_inputs:{','.join(missing)}" if missing else "abstained"))
            abstained = 1
        elif status.upper() == "UNKNOWN":
            abstained = 1
            reason = str(_get(entry, "reason") or "").strip() or "unknown"
        elif value is None:
            abstained = 1
            reason = "no_numeric_value"

        if abstained:
            value = None

        rows.append({
            "filename": filename,
            "attr_id": attr_id,
            "value": "" if value is None else round(float(value), 6),
            "tier": str(_first_attr(entry, TIER_KEYS) or ""),
            "confidence": ("" if _extract_confidence(entry) is None
                           else round(float(_extract_confidence(entry)), 6)),
            "abstained": abstained,
            "m1p_digest": _extract_digest(entry),
            "computed_utc": computed_utc,
            "pctile_in_corpus": "",          # filled in by compute_percentiles()
            "status": status,
            "reason": reason[:200],
            "model_version": model_version,
        })
    return rows


# --------------------------------------------------------------------------- percentiles
def compute_percentiles(rows: List[Dict[str, object]]) -> List[Dict[str, object]]:
    """Fill pctile_in_corpus per attr_id, in place, deterministically (Sprint E §12).

    Only non-abstained numeric rows participate. Midpoint rank for ties:
      pctile = 100 * mean(rank of tied group) / (n - 1);  n == 1 -> 50.0
    Abstained / non-numeric rows keep an empty percentile."""
    by_attr: Dict[str, List[Dict[str, object]]] = {}
    for r in rows:
        if _truthy_int(r.get("abstained")):
            r["pctile_in_corpus"] = ""
            continue
        v = float_or_none(r.get("value"))
        if v is None:
            r["pctile_in_corpus"] = ""
            continue
        by_attr.setdefault(str(r["attr_id"]), []).append(r)

    for _attr, group in by_attr.items():
        n = len(group)
        if n == 1:
            group[0]["pctile_in_corpus"] = 50.0
            continue
        # deterministic order: value, then filename (stable for identical values)
        ordered = sorted(group, key=lambda r: (float(r["value"]), str(r["filename"])))
        i = 0
        while i < n:
            j = i
            while j + 1 < n and float(ordered[j + 1]["value"]) == float(ordered[i]["value"]):
                j += 1
            midpoint = (i + j) / 2.0
            pct = round(100.0 * midpoint / (n - 1), 6)
            for k in range(i, j + 1):
                ordered[k]["pctile_in_corpus"] = pct
            i = j + 1
    return rows


# --------------------------------------------------------------------------- csv io
def sort_rows(rows: List[Dict[str, object]]) -> List[Dict[str, object]]:
    """Deterministic output ordering."""
    return sorted(rows, key=lambda r: (str(r.get("filename", "")), str(r.get("attr_id", ""))))


def _attr_ids_sha256(attr_ids: Iterable[str]) -> str:
    payload = "\n".join(sorted(attr_ids)) + "\n"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def seal_complete_image_rows(
        rows: List[Dict[str, object]], expected_attr_ids: Optional[Iterable[str]] = None,
        expected_model_version: Optional[str] = None) -> bool:
    """Seal rows only against a frozen attribute universe and model version."""
    attr_ids = [str(r.get("attr_id", "")) for r in rows]
    if not attr_ids or any(not attr_id for attr_id in attr_ids):
        raise ValueError("cannot seal image rows without attribute identities")
    if len(set(attr_ids)) != len(attr_ids):
        raise ValueError("annotator returned duplicate attr_id values for one image")
    digest = _attr_ids_sha256(attr_ids)
    for row in rows:
        row["image_complete"] = 0
        row["image_score_count"] = len(rows)
        row["image_attr_ids_sha256"] = digest
    if expected_attr_ids is None or not expected_model_version:
        return False
    expected = {str(attr_id) for attr_id in expected_attr_ids if str(attr_id)}
    if set(attr_ids) != expected:
        missing = sorted(expected - set(attr_ids))
        extra = sorted(set(attr_ids) - expected)
        raise ValueError(
            f"annotator attribute coverage mismatch: missing={missing[:10]!r} extra={extra[:10]!r}")
    if any(str(row.get("model_version", "")) != expected_model_version for row in rows):
        raise ValueError("annotator model_version does not match the frozen resume contract")
    for row in rows:
        row["image_complete"] = 1
    return True


def complete_existing_filenames(
        rows: List[Dict[str, object]], expected_attr_ids: Optional[Iterable[str]] = None,
        expected_model_version: Optional[str] = None) -> set:
    """Return only image identities carrying a self-consistent completion seal."""
    if expected_attr_ids is None or not expected_model_version:
        return set()
    expected = {str(attr_id) for attr_id in expected_attr_ids if str(attr_id)}
    expected_digest = _attr_ids_sha256(expected)
    grouped: Dict[str, List[Dict[str, object]]] = {}
    for row in rows:
        filename = str(row.get("filename", ""))
        if filename:
            grouped.setdefault(filename, []).append(row)
    complete = set()
    for filename, group in grouped.items():
        attr_ids = [str(r.get("attr_id", "")) for r in group]
        if not attr_ids or len(set(attr_ids)) != len(attr_ids) or any(not x for x in attr_ids):
            continue
        if set(attr_ids) == expected and all(
            str(r.get("image_complete", "")).strip() == "1"
            and str(r.get("image_score_count", "")).strip() == str(len(group))
            and r.get("image_attr_ids_sha256") == expected_digest
            and str(r.get("model_version", "")) == expected_model_version
            for r in group
        ):
            complete.add(filename)
    return complete


def load_registry_resume_contract() -> Tuple[set, str]:
    """The production attribute universe and model identity used to judge completeness."""
    from annotation_socket.registry import MODEL_VERSION, PREDICATES
    attr_ids = {str(spec["id"]) for spec in PREDICATES
                if isinstance(spec, dict) and spec.get("id")}
    if not attr_ids or not isinstance(MODEL_VERSION, str) or not MODEL_VERSION:
        raise ValueError("registry does not expose a usable resume contract")
    return attr_ids, MODEL_VERSION


def read_existing_scores(path: Path) -> List[Dict[str, object]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as fh:
        out = []
        for r in csv.DictReader(fh):
            row = {c: r.get(c, "") for c in OUT_COLUMNS}
            row["filename"] = (r.get("filename") or "").strip()
            out.append(row)
        return out


def write_scores_atomic(path: Path, rows: List[Dict[str, object]]) -> None:
    """Write via a temp file in the same directory, then os.replace (Sprint E §7/§13).

    A crash mid-write leaves the previous scores.csv untouched."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".scores.", suffix=".csv.tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(OUT_COLUMNS), extrasaction="ignore")
            w.writeheader()
            for r in rows:
                w.writerow({c: r.get(c, "") for c in OUT_COLUMNS})
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


# --------------------------------------------------------------------------- environment
def _git(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], cwd=str(ROOT), capture_output=True,
                              text=True, timeout=10).stdout.strip()
    except Exception:                          # pragma: no cover - defensive
        return ""


def environment_fingerprint(argv: Sequence[str], determinism: Dict[str, object]) -> Dict:
    return {
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "cwd": os.getcwd(),
        "repo_root": str(ROOT),
        "git_commit": _git("rev-parse", "HEAD"),
        "git_branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
        "argv": list(argv),
        "determinism": determinism,
    }


def _assert_schema_matches_corpus_db() -> Optional[str]:
    """Guard against drift from Sprint A's SCORE_COLUMNS. Returns a warning or None."""
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        import corpus_db  # type: ignore
    except Exception as e:
        return f"could not import corpus_db to verify schema: {type(e).__name__}: {e}"
    theirs = tuple(getattr(corpus_db, "SCORE_COLUMNS", ()))
    if theirs and theirs != SCORE_COLUMNS:
        return f"SCORE_COLUMNS drift: corpus_db={theirs} score_corpus_L6={SCORE_COLUMNS}"
    return None


def rebuild_db(corpus_dir: Path) -> Dict:
    """Rebuild corpus.db via Sprint A's public API (no modification to corpus_db.py)."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import corpus_db  # type: ignore
    return corpus_db.build_database(corpus_dir, rebuild=True)


# --------------------------------------------------------------------------- the run
def run(corpus_dir: Path,
        out_path: Path,
        limit: Optional[int] = None,
        resume: bool = False,
        only_missing: bool = False,
        dry_run: bool = False,
        do_rebuild_db: bool = False,
        fail_fast: bool = False,
        max_failures: Optional[int] = None,
        manifest_path: Optional[Path] = None,
        image_glob: str = "*.png",
        force: bool = False,
        annotate_fn: Optional[Callable[[str], Dict]] = None,
        argv: Optional[Sequence[str]] = None,
        expected_attr_ids: Optional[Iterable[str]] = None,
        expected_model_version: Optional[str] = None) -> Dict:
    """Score the corpus and write scores.csv. Returns the run summary dict.

    annotate_fn is the injection point: production passes None (the real annotator is
    imported and any failure is a hard, reported blocker); tests pass a fixture callable.
    """
    started = utc_now_iso()
    t0 = time.time()
    corpus_dir = Path(corpus_dir)
    out_path = Path(out_path)
    manifest_path = Path(manifest_path) if manifest_path else corpus_dir / "manifest.csv"

    resume_contract_error = None
    if expected_attr_ids is not None:
        expected_attr_ids = {str(attr_id) for attr_id in expected_attr_ids if str(attr_id)}
    elif annotate_fn is None:
        try:
            expected_attr_ids, expected_model_version = load_registry_resume_contract()
        except Exception as exc:
            resume_contract_error = f"{type(exc).__name__}: {exc}"

    determinism = configure_determinism()
    summary: Dict = {
        "sprint": "E",
        "started_utc": started,
        "finished_utc": None,
        "corpus_dir": str(corpus_dir),
        "manifest": str(manifest_path),
        "scores_csv": str(out_path),
        "dry_run": bool(dry_run),
        "resume": bool(resume or only_missing),
        "limit": limit,
        "images_seen": 0,
        "images_scored": 0,
        "images_skipped_existing": 0,
        "images_incomplete_existing": 0,
        "images_missing_file": 0,
        "images_failed": 0,
        "images_not_png": 0,
        "score_rows_written": 0,
        "attributes_scored_count": 0,
        "abstention_rows": 0,
        "failures": [],
        "missing_files_sample": [],
        "annotator_available": None,
        "annotator_blocker": None,
        "rebuild_db": None,
        "schema_warning": _assert_schema_matches_corpus_db(),
        "resume_contract": {
            "attribute_count": len(expected_attr_ids) if expected_attr_ids is not None else None,
            "attribute_ids_sha256": (_attr_ids_sha256(expected_attr_ids)
                                     if expected_attr_ids is not None else None),
            "model_version": expected_model_version,
            "error": resume_contract_error,
        },
        "environment": environment_fingerprint(argv or sys.argv, determinism),
    }

    manifest_rows = read_manifest(manifest_path)
    names = manifest_filenames(manifest_rows)
    summary["manifest_rows"] = len(manifest_rows)

    # ---- resume: which filenames already have rows we must preserve? -------------------
    existing_rows: List[Dict[str, object]] = []
    already: set = set()
    resuming = (resume or only_missing) and out_path.exists() and not force
    if resuming:
        existing_rows = read_existing_scores(out_path)
        already = complete_existing_filenames(
            existing_rows, expected_attr_ids, expected_model_version)
        summary["images_incomplete_existing"] = len({
            str(r["filename"]) for r in existing_rows if r.get("filename")
        } - already)

    # ---- select work ------------------------------------------------------------------
    todo: List[str] = []
    for fn in names:
        if resuming and fn in already:
            summary["images_skipped_existing"] += 1
            continue
        todo.append(fn)
    if limit is not None:
        todo = todo[:limit]
    summary["images_seen"] = len(todo)

    # ---- resolve paths BEFORE requiring the annotator ----------------------------------
    # so a corpus with no local images reports that plainly instead of an import error.
    resolved: List[Tuple[str, Optional[Path]]] = []
    png_suffixes = {".png"}
    if image_glob and image_glob not in ("*.png", "*"):
        png_suffixes.add(Path(image_glob).suffix.lower())
    for fn in todo:
        p = resolve_image_path(fn, corpus_dir)
        if p is None:
            summary["images_missing_file"] += 1
            if len(summary["missing_files_sample"]) < 10:
                summary["missing_files_sample"].append(fn)
            continue
        if image_glob != "*" and p.suffix.lower() not in png_suffixes:
            summary["images_not_png"] += 1
            continue
        resolved.append((fn, p))

    # ---- annotator ---------------------------------------------------------------------
    fn_annotate = annotate_fn
    if fn_annotate is None:
        try:
            fn_annotate = load_annotator()
            summary["annotator_available"] = True
        except AnnotatorUnavailable as e:
            summary["annotator_available"] = False
            summary["annotator_blocker"] = e.as_dict()

    if dry_run:
        summary["finished_utc"] = utc_now_iso()
        summary["elapsed_s"] = round(time.time() - t0, 3)
        summary["note"] = ("dry-run: resolved manifest and image paths only; "
                           "no annotation performed, scores.csv not written")
        return summary

    if fn_annotate is None:
        # Refuse to write anything. An empty or fabricated scores.csv would be worse
        # than no file at all (Sprint E §10/§20: never fake Outcome A).
        summary["finished_utc"] = utc_now_iso()
        summary["elapsed_s"] = round(time.time() - t0, 3)
        summary["note"] = ("BLOCKED: real annotator unavailable; scores.csv NOT written "
                           "and NOT modified. No fake scores were produced.")
        return summary

    # ---- score --------------------------------------------------------------------------
    new_rows: List[Dict[str, object]] = []
    for fn, path in resolved:
        computed_utc = utc_now_iso()
        try:
            record = fn_annotate(str(path))
        except Exception as e:
            summary["images_failed"] += 1
            summary["failures"].append({"filename": fn, "path": str(path),
                                        "error": f"{type(e).__name__}: {e}"[:300]})
            if fail_fast:
                break
            if max_failures is not None and summary["images_failed"] >= max_failures:
                summary["failures"].append({"filename": "<aborted>",
                                            "error": f"max_failures={max_failures} reached"})
                break
            continue
        rows = flatten_record(fn, record, computed_utc)
        if not rows:
            summary["images_failed"] += 1
            summary["failures"].append({"filename": fn, "path": str(path),
                                        "error": "annotator returned no per-attribute entries"})
            if fail_fast:
                break
            continue
        try:
            sealed = seal_complete_image_rows(
                rows, expected_attr_ids, expected_model_version)
        except ValueError as e:
            summary["images_failed"] += 1
            summary["failures"].append({"filename": fn, "path": str(path),
                                        "error": str(e)[:300]})
            if fail_fast:
                break
            continue
        if not sealed:
            summary.setdefault("images_unsealed_no_resume_contract", 0)
            summary["images_unsealed_no_resume_contract"] += 1
        new_rows.extend(rows)
        summary["images_scored"] += 1

    # ---- merge, percentile, write --------------------------------------------------------
    replaced = {str(r["filename"]) for r in new_rows}
    preserved_rows = [r for r in existing_rows if str(r.get("filename", "")) not in replaced]
    all_rows = (preserved_rows + new_rows) if resuming else new_rows
    # percentiles are recomputed across the whole corpus every write, so a resumed run
    # never leaves stale percentiles from a smaller sample.
    compute_percentiles(all_rows)
    all_rows = sort_rows(all_rows)

    summary["score_rows_written"] = len(all_rows)
    summary["abstention_rows"] = sum(1 for r in all_rows if _truthy_int(r.get("abstained")))
    summary["attributes_scored_count"] = len({
        str(r["attr_id"]) for r in all_rows if not _truthy_int(r.get("abstained"))})

    if all_rows:
        write_scores_atomic(out_path, all_rows)
    else:
        summary["note"] = ("no score rows produced; scores.csv left untouched "
                           "(nothing was overwritten)")

    if do_rebuild_db and all_rows:
        try:
            summary["rebuild_db"] = rebuild_db(corpus_dir)
        except Exception as e:
            summary["rebuild_db"] = {"error": f"{type(e).__name__}: {e}"[:300]}

    summary["finished_utc"] = utc_now_iso()
    summary["elapsed_s"] = round(time.time() - t0, 3)
    return summary


def write_report(summary: Dict, report_path: Optional[Path], corpus_dir: Path) -> Path:
    if report_path is None:
        stamp = (summary.get("started_utc") or utc_now_iso())
        stamp = stamp.replace("-", "").replace(":", "").replace("+0000", "").replace("T", "_")[:15]
        report_path = ROOT / "reports" / f"SPRINT_E_CORPUS_SCORING_RUN_{stamp}.json"
    report_path = Path(report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    return report_path


# --------------------------------------------------------------------------- CLI
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="score_corpus_L6.py",
        description="Sprint E: run the Tagger over corpus_L6 and emit scores.csv.")
    p.add_argument("--corpus-dir", default=str(DEFAULT_CORPUS_DIR))
    p.add_argument("--out", default=None,
                   help="output scores.csv (default: <corpus-dir>/scores.csv)")
    p.add_argument("--manifest", default=None)
    p.add_argument("--provenance", default=None,
                   help="accepted for symmetry with corpus_db; not required for scoring")
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--resume", action="store_true",
                   help="preserve completion-sealed image rows; rescore partial/legacy rows")
    p.add_argument("--only-missing", action="store_true",
                   help="alias of --resume")
    p.add_argument("--skip-existing", action="store_true", help="alias of --resume")
    p.add_argument("--force", action="store_true",
                   help="ignore existing scores.csv and rescore from scratch")
    p.add_argument("--dry-run", action="store_true",
                   help="resolve manifest/images and report; never write scores.csv")
    p.add_argument("--rebuild-db", action="store_true",
                   help="rebuild corpus.db via scripts/corpus_db.py after writing scores")
    p.add_argument("--fail-fast", action="store_true")
    p.add_argument("--max-failures", type=int, default=None)
    p.add_argument("--image-glob", default="*.png")
    p.add_argument("--report-path", default=None)
    p.add_argument("--no-report", action="store_true", help="do not write a run report")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    corpus_dir = Path(args.corpus_dir)
    out_path = Path(args.out) if args.out else corpus_dir / DEFAULT_SCORES_NAME

    summary = run(
        corpus_dir=corpus_dir,
        out_path=out_path,
        limit=args.limit,
        resume=args.resume or args.skip_existing,
        only_missing=args.only_missing,
        dry_run=args.dry_run,
        do_rebuild_db=args.rebuild_db,
        fail_fast=args.fail_fast,
        max_failures=args.max_failures,
        manifest_path=Path(args.manifest) if args.manifest else None,
        image_glob=args.image_glob,
        force=args.force,
        argv=list(argv) if argv is not None else sys.argv,
    )

    if not args.no_report:
        summary["report_path"] = str(write_report(
            summary, Path(args.report_path) if args.report_path else None, corpus_dir))

    print(json.dumps(summary, indent=1, sort_keys=True))

    if summary.get("annotator_available") is False and not args.dry_run:
        blocker = summary.get("annotator_blocker") or {}
        print("\nBLOCKED: " + str(blocker.get("reason", "annotator unavailable")),
              file=sys.stderr)
        if blocker.get("hint"):
            print("HINT: " + str(blocker["hint"]), file=sys.stderr)
        print("scores.csv was NOT written and NOT modified; no fake scores produced.",
              file=sys.stderr)
        return 2
    if summary.get("images_failed") and args.fail_fast:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
