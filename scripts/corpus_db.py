#!/usr/bin/env python3
"""corpus_db.py — Sprint A: the L6 corpus as a real, queryable SQLite database.

Turns corpus_L6/ ("a folder of PNGs + two CSVs") into corpus_L6/corpus.db so anyone can ask
"give me interiors high on prospect and low on clutter" and get real images back.

Inputs (READ-ONLY — this tool never mutates the corpus CSVs):
  corpus_L6/manifest.csv      curation: category, A/B pairing, notes
  corpus_L6/_provenance.csv   source, licence, resolution, sha256, gdrive_path, class-query
  corpus_L6/scores.csv        OPTIONAL — computed attribute scores (Sprint E will produce this).
                              Long format (filename,attr_id,value,...) preferred; wide format
                              (filename,<attr>=value,...) as documented in build_corpus_index.py
                              is also accepted.

Schema: images / attributes / scores / human_labels / images_fts (FTS5).
The attributes table is seeded from the LIVE registry (annotation_socket.registry PREDICATES,
imported read-only — never modified here), plus m1p_audited flags from the read-only
M1P_BINDINGS table in annotation_socket.m1_prime when that module is importable.

Usage:
  python scripts/corpus_db.py build --corpus-dir corpus_L6 --rebuild
  python scripts/corpus_db.py query --db corpus_L6/corpus.db --text lobby --limit 10
  python scripts/corpus_db.py query --db corpus_L6/corpus.db --space-family work --limit 20
  python scripts/corpus_db.py query --db corpus_L6/corpus.db \
      --attr-id cnfa.fluency.processing_load_proxy --min-pctile 80 --limit 20
  python scripts/corpus_db.py query --db corpus_L6/corpus.db --text "bright lobby" \
      --export reports/lobby_query.csv

Python API:
  build_database(corpus_dir, db_path=None, rebuild=False) -> dict summary
  query(db_path, spec: QuerySpec) -> list[dict]

Design rules (repo culture): stdlib only (sqlite3/csv/argparse/json/pathlib/dataclasses),
deterministic (same inputs -> same DB contents; ORDER BY everywhere), idempotent (build twice ->
same row counts), read-only on every existing repo file.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sqlite3
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CORPUS_DIR = ROOT / "corpus_L6"
DEFAULT_DB_NAME = "corpus.db"

# ---------------------------------------------------------------- column maps

IMAGE_COLUMNS: Sequence[str] = (
    "filename", "sha256", "source", "source_id", "creator", "license", "license_url",
    "orig_url", "collected_utc", "gdrive_path", "width", "height", "px_bucket",
    "category", "arch_type", "space_family",
    "pair_id", "pair_role", "pair_expected_better", "manipulation", "notes",
)

ATTRIBUTE_COLUMNS: Sequence[str] = (
    "attr_id", "family", "human_label", "tier_hint", "m1p_audited",
    "atlas_node_ids", "unit", "range", "definition",
)

SCORE_COLUMNS: Sequence[str] = (
    "filename", "attr_id", "value", "tier", "confidence", "abstained",
    "m1p_digest", "computed_utc", "pctile_in_corpus",
)

FTS_COLUMNS: Sequence[str] = (
    "filename", "source", "category", "arch_type", "space_family", "manipulation", "notes",
)

# CSV header aliases (first present wins; matching is case-insensitive on the header name)
ALIASES: Dict[str, Sequence[str]] = {
    "filename":      ("filename", "path", "image", "file", "rel_path"),
    "width":         ("width", "w", "image_width"),
    "height":        ("height", "h", "image_height"),
    "source":        ("source", "dataset", "source_name"),
    "orig_url":      ("orig_url", "original_url", "url"),
    "license":       ("license", "licence"),
    "notes":         ("notes", "caption", "description"),
    "attr_id":       ("attr_id", "attr", "attribute", "predicate", "id"),
    "value":         ("value", "score"),
    "pctile_in_corpus": ("pctile_in_corpus", "pctile", "percentile"),
}


# ---------------------------------------------------------------- small helpers

def first_present(row: Dict[str, str], key: str) -> Optional[str]:
    """Value for `key` from `row`, honouring ALIASES; None when absent. Case-insensitive."""
    lowered = {k.strip().lower(): v for k, v in row.items() if k is not None}
    for alias in ALIASES.get(key, (key,)):
        if alias in lowered and lowered[alias] not in (None, ""):
            return lowered[alias]
    return None


def int_or_none(v) -> Optional[int]:
    try:
        return int(float(str(v).strip()))
    except (TypeError, ValueError):
        return None


def float_or_none(v) -> Optional[float]:
    if v is None or not str(v).strip():
        return None
    try:
        value = float(str(v).strip())
    except (TypeError, ValueError):
        raise ValueError(f"invalid numeric value {v!r}")
    if not math.isfinite(value):
        raise ValueError(f"non-finite numeric value {v!r}")
    return value


def bool_int(v) -> Optional[int]:
    """CSV truthiness -> 0/1 (None when blank/unparseable)."""
    if v is None:
        return None
    s = str(v).strip().lower()
    if s in ("1", "true", "t", "yes", "y"):
        return 1
    if s in ("0", "false", "f", "no", "n"):
        return 0
    return None


def px_bucket(width: Optional[int], height: Optional[int]) -> str:
    """Sprint-A bucket on the LONG side, max(width, height). NOTE: build_corpus_index.py
    buckets on the SHORT side (min) — intentionally different, per the Sprint A brief;
    see reports/SPRINT_A_CORPUS_DB_PROGRESS_2026-08-06.md."""
    if not width or not height:
        return "unknown"
    s = max(width, height)
    if s >= 2048:
        return ">=2048"
    if s >= 1024:
        return "1024-2047"
    if s >= 512:
        return "512-1023"
    return "<512"


def read_csv_rows(path: Path) -> List[Dict[str, str]]:
    """DictReader rows in file order (deterministic). Missing file -> []. Never writes."""
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as fh:
        return [dict(r) for r in csv.DictReader(fh)]


# ------------------------------------------------- taxonomy derivation (reuse, read-only)

def _load_index_helpers():
    """Import arch_type()/family_of() from the sibling build_corpus_index.py (single source of
    truth for the room-class taxonomy). Read-only import; None-pair on any failure."""
    try:
        import importlib.util
        p = Path(__file__).resolve().parent / "build_corpus_index.py"
        spec = importlib.util.spec_from_file_location("_l6_index_helpers", p)
        if spec is None or spec.loader is None:
            return None, None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.arch_type, mod.family_of
    except Exception:
        return None, None


# ---------------------------------------------------------------- registry seeding

_FAMILY_BY_EXACT = {
    "glare-risk": "light",
    "acoustic_absorption_proxy": "acoustic",
    "cnfa.fractal_dimension": "fluency-clutter",
}
_FAMILY_BY_PREFIX = (
    ("cnfa.fluency.", "fluency-clutter"),
    ("cnfa.light.", "light"),
    ("cnfa.geometry.", "geometry-space"),
    ("cnfa.spatial.", "geometry-space"),
    ("cnfa.arch.", "geometry-space"),
    ("cnfa.plan.", "geometry-space"),
    ("cnfa.acoustic.", "acoustic"),
    ("cnfa.material.", "material"),
    ("cnfa.cognitive.", "cognitive-salience"),
)


def _attr_family(attr_id: str) -> str:
    if attr_id in _FAMILY_BY_EXACT:
        return _FAMILY_BY_EXACT[attr_id]
    for prefix, fam in _FAMILY_BY_PREFIX:
        if attr_id.startswith(prefix):
            return fam
    # C1.visual_integration, C01.triangulation_ignition, C24.spatial_generosity, ...
    if len(attr_id) > 1 and attr_id[0] == "C" and attr_id[1].isdigit():
        return "layout-wellbeing"
    return ""


def _attr_human_label(attr_id: str) -> str:
    tail = attr_id.rsplit(".", 1)[-1]
    return tail.replace("_", " ").replace("-", " ")


def _predicate_to_attr_row(pred, m1p_ids: Optional[frozenset]) -> Optional[Tuple]:
    """Robust adapter: predicate may be a dict, an object, or a bare string id."""
    if isinstance(pred, str):
        attr_id, tier_hint, note = pred, "", ""
    elif isinstance(pred, dict):
        attr_id = pred.get("id") or pred.get("attr_id") or pred.get("key") or pred.get("name")
        tier_hint = str(pred.get("tier_hint", "") or "")
        note = str(pred.get("note", "") or "")
    else:  # dataclass / arbitrary object
        attr_id = None
        for f_ in ("id", "attr_id", "key", "name"):
            attr_id = getattr(pred, f_, None)
            if attr_id:
                break
        tier_hint = str(getattr(pred, "tier_hint", "") or "")
        note = str(getattr(pred, "note", "") or "")
    if not attr_id:
        return None
    attr_id = str(attr_id)
    m1p = None if m1p_ids is None else (1 if attr_id in m1p_ids else 0)
    return (attr_id, _attr_family(attr_id), _attr_human_label(attr_id), tier_hint,
            m1p, "", "", "", note)


def seed_attributes_from_registry(con: sqlite3.Connection) -> Dict[str, object]:
    """Seed `attributes` from annotation_socket.registry PREDICATES (read-only import).
    m1p_audited comes from annotation_socket.m1_prime.M1P_BINDINGS when importable
    (that module needs numpy/cv2; absence -> m1p_audited stays NULL = unknown).
    Registry unavailable (e.g. bare test env) -> 0 rows seeded, clearly reported;
    score loading will still placeholder-seed any attr_ids it meets."""
    predicates = None
    source = "unavailable"
    try:
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        from annotation_socket.registry import PREDICATES as predicates  # noqa: N811
        source = "annotation_socket.registry.PREDICATES"
    except Exception as exc:  # registry not importable here — honest fallback
        return {"seeded": 0, "source": f"unavailable ({type(exc).__name__}: {exc})"}

    m1p_ids: Optional[frozenset] = None
    try:
        from annotation_socket.m1_prime import M1P_BINDINGS
        m1p_ids = frozenset(M1P_BINDINGS.keys())
    except Exception:
        m1p_ids = None  # NULL = unknown, never a guessed 0

    if isinstance(predicates, dict):
        items = [dict(v, id=v.get("id", k)) if isinstance(v, dict) else v
                 for k, v in sorted(predicates.items())]
    else:
        items = list(predicates)

    rows = []
    for pred in items:
        row = _predicate_to_attr_row(pred, m1p_ids)
        if row is not None:
            rows.append(row)
    con.executemany(
        "INSERT OR REPLACE INTO attributes ({}) VALUES ({})".format(
            ",".join(ATTRIBUTE_COLUMNS), ",".join("?" * len(ATTRIBUTE_COLUMNS))),
        rows)
    return {"seeded": len(rows), "source": source,
            "m1p_flags": "M1P_BINDINGS" if m1p_ids is not None else "unavailable(NULL)"}


# ---------------------------------------------------------------- schema

SCHEMA = """
CREATE TABLE IF NOT EXISTS images (
    filename TEXT PRIMARY KEY,
    sha256 TEXT, source TEXT, source_id TEXT, creator TEXT,
    license TEXT, license_url TEXT, orig_url TEXT, collected_utc TEXT, gdrive_path TEXT,
    width INTEGER, height INTEGER, px_bucket TEXT,
    category TEXT, arch_type TEXT, space_family TEXT,
    pair_id TEXT, pair_role TEXT, pair_expected_better TEXT, manipulation TEXT, notes TEXT
);
CREATE TABLE IF NOT EXISTS attributes (
    attr_id TEXT PRIMARY KEY,
    family TEXT, human_label TEXT, tier_hint TEXT, m1p_audited INTEGER,
    atlas_node_ids TEXT, unit TEXT, range TEXT, definition TEXT
);
CREATE TABLE IF NOT EXISTS scores (
    filename TEXT NOT NULL,
    attr_id TEXT NOT NULL,
    value REAL, tier TEXT, confidence REAL, abstained INTEGER,
    m1p_digest TEXT, computed_utc TEXT, pctile_in_corpus REAL,
    PRIMARY KEY (filename, attr_id),
    FOREIGN KEY (filename) REFERENCES images(filename),
    FOREIGN KEY (attr_id) REFERENCES attributes(attr_id)
);
CREATE TABLE IF NOT EXISTS human_labels (
    filename TEXT NOT NULL,
    construct TEXT NOT NULL,
    human_score REAL, ci_low REAL, ci_high REAL, n_judgments INTEGER, agreement REAL,
    PRIMARY KEY (filename, construct),
    FOREIGN KEY (filename) REFERENCES images(filename)
);
CREATE INDEX IF NOT EXISTS idx_scores_attr ON scores(attr_id, value);
CREATE INDEX IF NOT EXISTS idx_scores_attr_pct ON scores(attr_id, pctile_in_corpus);
CREATE INDEX IF NOT EXISTS idx_images_family ON images(space_family);
CREATE INDEX IF NOT EXISTS idx_images_type ON images(arch_type);
CREATE INDEX IF NOT EXISTS idx_images_category ON images(category);
"""

FTS_SCHEMA = """
CREATE VIRTUAL TABLE IF NOT EXISTS images_fts USING fts5(
    filename, source, category, arch_type, space_family, manipulation, notes
);
"""


def open_db(db_path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def create_schema(con: sqlite3.Connection) -> bool:
    """Create tables. Returns fts_available (FTS5 vtable creation succeeded)."""
    con.executescript(SCHEMA)
    try:
        con.executescript(FTS_SCHEMA)
        return True
    except sqlite3.OperationalError:
        # FTS5 missing from this SQLite build: degrade to LIKE search at query time.
        return False


def _has_fts(con: sqlite3.Connection) -> bool:
    r = con.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='images_fts'").fetchone()
    return r is not None


# ---------------------------------------------------------------- loading

def merge_manifest_and_provenance(corpus_dir: Path) -> List[Dict[str, Optional[str]]]:
    """One merged record per filename (union of both CSVs; manifest curation fields win where
    both name the same field). Deterministic: sorted by filename. CSVs are never modified."""
    man_rows = read_csv_rows(corpus_dir / "manifest.csv")
    prov_rows = read_csv_rows(corpus_dir / "_provenance.csv")

    man: Dict[str, Dict[str, str]] = {}
    for r in man_rows:
        fn = first_present(r, "filename")
        if fn:
            man[fn] = r
    prov: Dict[str, Dict[str, str]] = {}
    for r in prov_rows:
        fn = first_present(r, "filename")
        if fn:
            prov[fn] = r

    d_arch_type, d_family_of = _load_index_helpers()

    merged: List[Dict[str, Optional[str]]] = []
    for fn in sorted(set(man) | set(prov)):
        m = man.get(fn, {})
        p = prov.get(fn, {})

        def pick(key: str) -> Optional[str]:
            return first_present(m, key) if first_present(m, key) is not None \
                else first_present(p, key)

        width = int_or_none(pick("width"))
        height = int_or_none(pick("height"))

        arch = pick("arch_type")
        fam = pick("space_family")
        if arch is None and d_arch_type is not None:
            try:
                arch = d_arch_type({**p, **m, "filename": fn}, p or None)
            except Exception:
                arch = None
        if fam is None and d_family_of is not None and arch is not None:
            try:
                fam = d_family_of(arch)
            except Exception:
                fam = None

        merged.append({
            "filename": fn,
            "sha256": pick("sha256") or "",
            "source": pick("source") or "",
            "source_id": pick("source_id") or "",
            "creator": pick("creator") or "",
            "license": pick("license") or "",
            "license_url": pick("license_url") or "",
            "orig_url": pick("orig_url") or "",
            "collected_utc": pick("collected_utc") or "",
            "gdrive_path": pick("gdrive_path") or "",
            "width": width,
            "height": height,
            "px_bucket": pick("px_bucket") or px_bucket(width, height),
            "category": pick("category") or "",
            "arch_type": arch or "",
            "space_family": fam or "",
            "pair_id": pick("pair_id") or "",
            "pair_role": pick("pair_role") or "",
            "pair_expected_better": pick("pair_expected_better") or "",
            "manipulation": pick("manipulation") or "",
            "notes": pick("notes") or "",
        })
    return merged


def load_images(con: sqlite3.Connection, corpus_dir: Path) -> int:
    records = merge_manifest_and_provenance(corpus_dir)
    con.execute("DELETE FROM scores")       # children first (FK); no-op on fresh build
    con.execute("DELETE FROM images")
    con.executemany(
        "INSERT INTO images ({}) VALUES ({})".format(
            ",".join(IMAGE_COLUMNS), ",".join("?" * len(IMAGE_COLUMNS))),
        [tuple(r[c] for c in IMAGE_COLUMNS) for r in records])
    if _has_fts(con):
        con.execute("DELETE FROM images_fts")
        con.execute(
            "INSERT INTO images_fts ({cols}) SELECT {cols} FROM images ORDER BY filename"
            .format(cols=",".join(FTS_COLUMNS)))
    return len(records)


def _scores_rows_from_csv(path: Path) -> List[Dict[str, Optional[str]]]:
    """Normalize scores.csv to long-format dicts. Accepts:
    LONG:  filename,attr_id,value[,tier,confidence,abstained,m1p_digest,computed_utc,pctile_in_corpus]
    WIDE:  filename,<attr1>,<attr2>,...   (each extra column = one attr value; the format
           build_corpus_index.py documents). Detection: no attr_id-aliased column -> wide."""
    raw = read_csv_rows(path)
    if not raw:
        return []
    is_long = first_present(raw[0], "attr_id") is not None
    out: List[Dict[str, Optional[str]]] = []
    if is_long:
        for r in raw:
            fn = first_present(r, "filename")
            attr = first_present(r, "attr_id")
            if not fn or not attr:
                continue
            lowered = {k.strip().lower(): v for k, v in r.items() if k is not None}
            out.append({
                "filename": fn, "attr_id": attr,
                "value": first_present(r, "value"),
                "tier": lowered.get("tier"),
                "confidence": lowered.get("confidence"),
                "abstained": lowered.get("abstained"),
                "m1p_digest": lowered.get("m1p_digest"),
                "computed_utc": lowered.get("computed_utc"),
                "pctile_in_corpus": first_present(r, "pctile_in_corpus"),
            })
    else:
        for r in raw:
            fn = first_present(r, "filename")
            if not fn:
                continue
            for k in sorted(k for k in r if k is not None):
                kl = k.strip().lower()
                if kl in ALIASES["filename"] or r[k] in (None, ""):
                    continue
                out.append({"filename": fn, "attr_id": k.strip(), "value": r[k],
                            "tier": None, "confidence": None, "abstained": None,
                            "m1p_digest": None, "computed_utc": None,
                            "pctile_in_corpus": None})
    return out


def load_scores(con: sqlite3.Connection, scores_path: Path) -> Dict[str, int]:
    """Load scores.csv if present. Robust-insertion policy (documented, Sprint A §19 option B):
    an attr_id not in `attributes` gets a minimal placeholder row (family='', human_label=attr_id)
    and is counted in score_attrs_added; a filename not in `images` is SKIPPED and counted in
    scores_skipped_unknown_image (we will not invent provenance for an image we don't have)."""
    stats = {"scores": 0, "score_attrs_added": 0, "scores_skipped_unknown_image": 0}
    rows = _scores_rows_from_csv(scores_path)
    if not rows:
        return stats

    known_images = {r[0] for r in con.execute("SELECT filename FROM images")}
    known_attrs = {r[0] for r in con.execute("SELECT attr_id FROM attributes")}

    seen = set()
    for row_number, r in enumerate(rows, 2):
        key = (r["filename"], r["attr_id"])
        if key in seen:
            raise ValueError(
                f"duplicate score identity {key!r} in {scores_path} at data row {row_number}")
        seen.add(key)
        for field in ("value", "confidence", "pctile_in_corpus"):
            float_or_none(r[field])

    for r in rows:
        fn, attr = r["filename"], r["attr_id"]
        if fn not in known_images:
            stats["scores_skipped_unknown_image"] += 1
            continue
        if attr not in known_attrs:
            con.execute(
                "INSERT INTO attributes (attr_id, family, human_label, tier_hint, "
                "atlas_node_ids, unit, range, definition) VALUES (?, '', ?, '', '', '', '', "
                "'placeholder seeded by corpus_db.load_scores (attr absent from registry)')",
                (attr, attr))
            known_attrs.add(attr)
            stats["score_attrs_added"] += 1
        con.execute(
            "INSERT INTO scores ({}) VALUES ({})".format(
                ",".join(SCORE_COLUMNS), ",".join("?" * len(SCORE_COLUMNS))),
            (fn, attr, float_or_none(r["value"]), r["tier"] or None,
             float_or_none(r["confidence"]), bool_int(r["abstained"]),
             r["m1p_digest"] or None, r["computed_utc"] or None,
             float_or_none(r["pctile_in_corpus"])))
        stats["scores"] += 1
    return stats


# ---------------------------------------------------------------- build

def build_database(corpus_dir, db_path=None, rebuild: bool = False) -> dict:
    """Build (or refresh) corpus.db from the corpus CSVs. Idempotent: images/attributes/scores
    are fully re-derived from the CSVs on every build (DELETE + reload), so building twice
    yields identical row counts. human_labels is preserved across non-rebuild builds (it is
    filled by the future 2AFC campaign, not by this loader); --rebuild deletes the DB file."""
    corpus_dir = Path(corpus_dir)
    if not corpus_dir.exists():
        raise FileNotFoundError(f"corpus dir not found: {corpus_dir}")
    manifest = corpus_dir / "manifest.csv"
    if not manifest.exists():
        raise FileNotFoundError(f"manifest.csv not found in {corpus_dir}")

    db_path = Path(db_path) if db_path else corpus_dir / DEFAULT_DB_NAME
    if rebuild and db_path.exists():
        db_path.unlink()

    con = open_db(db_path)
    try:
        # FK checks deferred to COMMIT: the refresh deletes+reloads parent tables in place while
        # human_labels rows (if any) keep referencing filenames that are re-inserted before commit.
        con.execute("PRAGMA defer_foreign_keys = ON")
        fts_ok = create_schema(con)
        # Fully re-derive: children first, then parents (idempotent; no stale registry rows).
        con.execute("DELETE FROM scores")
        con.execute("DELETE FROM attributes")
        attr_info = seed_attributes_from_registry(con)
        n_images = load_images(con, corpus_dir)
        score_stats = load_scores(con, corpus_dir / "scores.csv")
        con.commit()
        n_attrs = con.execute("SELECT COUNT(*) FROM attributes").fetchone()[0]
        summary = {
            "images": n_images,
            "attributes": n_attrs,
            "scores": score_stats["scores"],
            "score_attrs_added": score_stats["score_attrs_added"],
            "scores_skipped_unknown_image": score_stats["scores_skipped_unknown_image"],
            "attributes_source": attr_info.get("source"),
            "fts5": fts_ok,
            "db_path": str(db_path),
        }
        return summary
    finally:
        con.close()


# ---------------------------------------------------------------- query

@dataclass
class QuerySpec:
    category: Optional[str] = None
    arch_type: Optional[str] = None
    space_family: Optional[str] = None
    text: Optional[str] = None
    attr_id: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    min_pctile: Optional[float] = None
    max_pctile: Optional[float] = None
    limit: int = 50
    columns: Sequence[str] = field(default_factory=lambda: list(IMAGE_COLUMNS))


def _fts_escape(text: str) -> str:
    """Treat user text as literal terms: quote each whitespace token (implicit AND)."""
    terms = [t.replace('"', '""') for t in text.split() if t]
    return " ".join(f'"{t}"' for t in terms)


def query(db_path, spec: QuerySpec) -> List[dict]:
    """Run a deterministic query; returns list of dict rows (ORDER BY filename).
    When attr_id is given, joins scores and includes value/tier/pctile_in_corpus."""
    db_path = Path(db_path)
    if not db_path.exists():
        raise FileNotFoundError(f"database not found: {db_path} (run `build` first)")
    con = open_db(db_path)
    try:
        select_cols = ", ".join(f"i.{c}" for c in spec.columns)
        joins, where, params = [], [], []

        if spec.attr_id:
            select_cols += ", s.value AS value, s.tier AS tier, s.pctile_in_corpus AS pctile_in_corpus"
            joins.append("JOIN scores s ON s.filename = i.filename AND s.attr_id = ?")
            params.append(spec.attr_id)
            if spec.min_value is not None:
                where.append("s.value >= ?"); params.append(spec.min_value)
            if spec.max_value is not None:
                where.append("s.value <= ?"); params.append(spec.max_value)
            if spec.min_pctile is not None:
                where.append("s.pctile_in_corpus >= ?"); params.append(spec.min_pctile)
            if spec.max_pctile is not None:
                where.append("s.pctile_in_corpus <= ?"); params.append(spec.max_pctile)

        for col in ("category", "arch_type", "space_family"):
            v = getattr(spec, col)
            if v is not None:
                where.append(f"i.{col} = ?"); params.append(v)

        if spec.text:
            if _has_fts(con):
                joins.append("JOIN images_fts f ON f.filename = i.filename")
                where.append("images_fts MATCH ?")
                params.append(_fts_escape(spec.text))
            else:  # LIKE fallback (FTS5 absent from this SQLite build)
                ors = []
                for c in FTS_COLUMNS:
                    ors.append(f"i.{c} LIKE ?")
                    params.append(f"%{spec.text}%")
                where.append("(" + " OR ".join(ors) + ")")

        sql = f"SELECT {select_cols} FROM images i " + " ".join(joins)
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY i.filename LIMIT ?"
        params.append(int(spec.limit))
        return [dict(r) for r in con.execute(sql, params)]
    finally:
        con.close()


def export_rows(rows: List[dict], out_path: Path) -> None:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        if not rows:
            fh.write("")
            return
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


# ---------------------------------------------------------------- CLI

def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="L6 corpus SQLite database (Sprint A)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="build corpus.db from the corpus CSVs")
    b.add_argument("--corpus-dir", default=str(DEFAULT_CORPUS_DIR))
    b.add_argument("--db", default=None, help="db path (default <corpus-dir>/corpus.db)")
    b.add_argument("--rebuild", action="store_true", help="delete the db file first")

    q = sub.add_parser("query", help="query corpus.db (prints JSON rows)")
    q.add_argument("--db", default=str(DEFAULT_CORPUS_DIR / DEFAULT_DB_NAME))
    q.add_argument("--category")
    q.add_argument("--arch-type", dest="arch_type")
    q.add_argument("--space-family", dest="space_family")
    q.add_argument("--text")
    q.add_argument("--attr-id", dest="attr_id")
    q.add_argument("--min-value", dest="min_value", type=float)
    q.add_argument("--max-value", dest="max_value", type=float)
    q.add_argument("--min-pctile", dest="min_pctile", type=float)
    q.add_argument("--max-pctile", dest="max_pctile", type=float)
    q.add_argument("--limit", type=int, default=50)
    q.add_argument("--export", help="also write results to this CSV path")

    a = ap.parse_args(argv)
    if a.cmd == "build":
        summary = build_database(a.corpus_dir, db_path=a.db, rebuild=a.rebuild)
        print(json.dumps(summary, indent=1))
        return 0
    # query
    spec = QuerySpec(category=a.category, arch_type=a.arch_type, space_family=a.space_family,
                     text=a.text, attr_id=a.attr_id,
                     min_value=a.min_value, max_value=a.max_value,
                     min_pctile=a.min_pctile, max_pctile=a.max_pctile, limit=a.limit)
    rows = query(a.db, spec)
    print(json.dumps(rows, indent=1))
    if a.export:
        export_rows(rows, Path(a.export))
        print(f"exported {len(rows)} rows -> {a.export}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
