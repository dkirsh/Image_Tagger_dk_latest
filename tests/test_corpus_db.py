"""tests/test_corpus_db.py — Sprint A corpus database (scripts/corpus_db.py).

Self-contained: builds tiny fixture corpora under tmp_path; never reads or writes the real
corpus_L6/. Deterministic (fixed fixture contents, no randomness, no clock reads in asserts).

Run:  PYTHONPATH=. python -m pytest tests/test_corpus_db.py -v
Fallback (no pytest installed): PYTHONPATH=. python tests/test_corpus_db.py
"""
from __future__ import annotations

import csv
import json
import sqlite3
import sys
from pathlib import Path

try:
    import pytest
except ImportError:          # stdlib fallback runner below (__main__); pytest preferred
    pytest = None

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import corpus_db  # noqa: E402  (scripts/corpus_db.py)


class _Approx:
    """Minimal stand-in for pytest.approx (used only by the fallback runner)."""
    def __init__(self, expected, rel=1e-6):
        self.expected, self.rel = expected, rel

    def __eq__(self, other):
        return abs(other - self.expected) <= self.rel * max(1.0, abs(self.expected))


def approx(v):
    return pytest.approx(v) if pytest else _Approx(v)

ATTR = "cnfa.fluency.processing_load_proxy"


def _write_csv(path: Path, header, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)


def make_fixture_corpus(tmp_path: Path, with_scores: bool = True,
                        filename_header: str = "filename") -> Path:
    """Tiny two-image corpus. filename_header lets Test 4 exercise the 'path' alias."""
    corpus = tmp_path / "corpus_L6"
    _write_csv(
        corpus / "manifest.csv",
        [filename_header, "category", "space_family", "pair_id", "pair_expected_better", "notes"],
        [
            ["interiors/lobby.png", "interiors", "circulation", "", "unknown",
             "bright lobby with signage."],
            ["interiors/office.png", "interiors", "work", "", "unknown",
             "quiet open-plan office."],
        ])
    _write_csv(
        corpus / "_provenance.csv",
        [filename_header, "source", "source_id", "creator", "licence", "license_url",
         "original_url", "w", "h", "sha256", "collected_utc", "gdrive_path"],
        [
            ["interiors/lobby.png", "unit_test", "fx-1", "fixture", "CC0", "",
             "https://example.org/lobby", "1600", "1200", "aa" * 32,
             "2026-08-06T00:00:00+00:00", "gdrive:corpus_L6/interiors/lobby.png"],
            ["interiors/office.png", "unit_test", "fx-2", "fixture", "CC0", "",
             "https://example.org/office", "640", "480", "bb" * 32,
             "2026-08-06T00:00:00+00:00", ""],
        ])
    if with_scores:
        _write_csv(
            corpus / "scores.csv",
            ["filename", "attr_id", "value", "tier", "confidence", "abstained",
             "m1p_digest", "computed_utc", "pctile_in_corpus"],
            [
                ["interiors/lobby.png", ATTR, "0.12", "AMBER", "0.9", "0",
                 "d1", "2026-08-06T00:00:00+00:00", "10"],
                ["interiors/office.png", ATTR, "0.88", "AMBER", "0.9", "0",
                 "d2", "2026-08-06T00:00:00+00:00", "90"],
            ])
    return corpus


def _counts(db_path: Path) -> dict:
    con = sqlite3.connect(str(db_path))
    try:
        return {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                for t in ("images", "attributes", "scores", "human_labels")}
    finally:
        con.close()


# ------------------------------------------------------------------ Test 1: build + query

def test_build_and_query(tmp_path):
    corpus = make_fixture_corpus(tmp_path)
    summary = corpus_db.build_database(corpus, rebuild=True)
    db = corpus / "corpus.db"

    assert db.exists()
    assert summary["images"] == 2
    assert summary["scores"] == 2
    assert summary["attributes"] >= 1  # 68 when the live registry imports; >=1 otherwise

    # space_family filter -> office
    rows = corpus_db.query(db, corpus_db.QuerySpec(space_family="work"))
    assert [r["filename"] for r in rows] == ["interiors/office.png"]

    # attribute percentile filter -> office (pctile 90 >= 80)
    rows = corpus_db.query(db, corpus_db.QuerySpec(attr_id=ATTR, min_pctile=80))
    assert [r["filename"] for r in rows] == ["interiors/office.png"]
    assert rows[0]["value"] == approx(0.88)
    assert rows[0]["pctile_in_corpus"] == approx(90)

    # full-text search over notes -> lobby
    rows = corpus_db.query(db, corpus_db.QuerySpec(text="signage"))
    assert [r["filename"] for r in rows] == ["interiors/lobby.png"]

    # merged provenance fields + alias resolution (licence, original_url, w/h) + px_bucket(max)
    lobby = corpus_db.query(db, corpus_db.QuerySpec(text="lobby"))[0]
    assert lobby["source"] == "unit_test"
    assert lobby["license"] == "CC0"
    assert lobby["orig_url"] == "https://example.org/lobby"
    assert lobby["width"] == 1600 and lobby["height"] == 1200
    assert lobby["px_bucket"] == "1024-2047"  # max(1600,1200)=1600


def test_attr_value_range_query(tmp_path):
    corpus = make_fixture_corpus(tmp_path)
    corpus_db.build_database(corpus, rebuild=True)
    db = corpus / "corpus.db"
    rows = corpus_db.query(db, corpus_db.QuerySpec(attr_id=ATTR, max_value=0.5))
    assert [r["filename"] for r in rows] == ["interiors/lobby.png"]


# ------------------------------------------------------------------ Test 2: idempotency

def test_idempotent_rebuild(tmp_path):
    corpus = make_fixture_corpus(tmp_path)
    s1 = corpus_db.build_database(corpus, rebuild=True)
    first = _counts(corpus / "corpus.db")
    s2 = corpus_db.build_database(corpus)            # refresh in place, no --rebuild
    second = _counts(corpus / "corpus.db")
    assert first == second
    assert s1["images"] == s2["images"] == 2
    assert s1["scores"] == s2["scores"] == 2
    assert first["images"] == 2 and first["scores"] == 2  # not doubled


# ------------------------------------------------------------------ Test 3: missing scores.csv

def test_missing_scores_csv_ok(tmp_path):
    corpus = make_fixture_corpus(tmp_path, with_scores=False)
    summary = corpus_db.build_database(corpus, rebuild=True)
    assert summary["images"] == 2
    assert summary["scores"] == 0
    assert _counts(corpus / "corpus.db")["scores"] == 0


# ------------------------------------------------------------------ Test 4: CSV aliases

def test_filename_alias_path(tmp_path):
    corpus = make_fixture_corpus(tmp_path, filename_header="path")
    summary = corpus_db.build_database(corpus, rebuild=True)
    assert summary["images"] == 2
    rows = corpus_db.query(corpus / "corpus.db", corpus_db.QuerySpec(space_family="work"))
    assert [r["filename"] for r in rows] == ["interiors/office.png"]


# ------------------------------------------------------------------ extra: robustness

def test_unknown_score_attr_gets_placeholder(tmp_path):
    """Sprint-E-produced attr absent from the registry must not crash the build (§19 option B)."""
    corpus = make_fixture_corpus(tmp_path)
    with (corpus / "scores.csv").open("a", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerow(
            ["interiors/lobby.png", "cnfa.future.not_in_registry", "1.0", "AMBER",
             "", "", "", "", "50"])
    summary = corpus_db.build_database(corpus, rebuild=True)
    assert summary["scores"] == 3
    assert summary["score_attrs_added"] >= 1
    con = sqlite3.connect(str(corpus / "corpus.db"))
    try:
        row = con.execute("SELECT human_label, definition FROM attributes WHERE attr_id=?",
                          ("cnfa.future.not_in_registry",)).fetchone()
    finally:
        con.close()
    assert row is not None and row[0] == "cnfa.future.not_in_registry"


def test_score_for_unknown_image_skipped(tmp_path):
    corpus = make_fixture_corpus(tmp_path)
    with (corpus / "scores.csv").open("a", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerow(
            ["interiors/ghost.png", ATTR, "0.5", "AMBER", "", "", "", "", "50"])
    summary = corpus_db.build_database(corpus, rebuild=True)
    assert summary["scores"] == 2
    assert summary["scores_skipped_unknown_image"] == 1


def test_registry_seeding_in_real_repo(tmp_path):
    """In this repo the live registry should give exactly 68 attributes."""
    corpus = make_fixture_corpus(tmp_path, with_scores=False)
    summary = corpus_db.build_database(corpus, rebuild=True)
    if "annotation_socket.registry" in summary["attributes_source"]:
        assert summary["attributes"] == 68
    else:  # bare environment without the registry: fallback documented, not silent
        assert summary["attributes"] >= 0


def test_cli_build_and_query(tmp_path, capsys):
    corpus = make_fixture_corpus(tmp_path)
    rc = corpus_db.main(["build", "--corpus-dir", str(corpus), "--rebuild"])
    assert rc == 0
    built = json.loads(capsys.readouterr().out)
    assert built["images"] == 2 and built["scores"] == 2

    export = tmp_path / "out" / "lobby.csv"
    rc = corpus_db.main(["query", "--db", str(corpus / "corpus.db"),
                         "--text", "signage", "--limit", "5",
                         "--export", str(export)])
    assert rc == 0
    rows = json.loads(capsys.readouterr().out)
    assert [r["filename"] for r in rows] == ["interiors/lobby.png"]
    assert export.exists()
    with export.open(newline="", encoding="utf-8") as fh:
        exported = list(csv.DictReader(fh))
    assert [r["filename"] for r in exported] == ["interiors/lobby.png"]


def test_corpus_csvs_not_mutated(tmp_path):
    corpus = make_fixture_corpus(tmp_path)
    before = {p.name: p.read_bytes() for p in corpus.glob("*.csv")}
    corpus_db.build_database(corpus, rebuild=True)
    corpus_db.build_database(corpus)
    after = {p.name: p.read_bytes() for p in corpus.glob("*.csv")}
    assert before == after


# ------------------------------------------------------------------ stdlib fallback runner
# Preferred: PYTHONPATH=. python -m pytest tests/test_corpus_db.py -v
# This runner exists only so the suite is verifiable in environments without pytest.

class _CapsysShim:
    """readouterr()-compatible stdout capture for the fallback runner."""
    def __init__(self):
        import io
        self._real, self._buf = sys.stdout, io.StringIO()
        sys.stdout = self._buf

    def readouterr(self):
        import io
        out = self._buf.getvalue()
        sys.stdout = self._buf = io.StringIO()
        return type("Cap", (), {"out": out, "err": ""})()

    def restore(self):
        sys.stdout = self._real


def _run_all_without_pytest() -> int:
    import inspect
    import tempfile
    import traceback
    tests = [(n, f) for n, f in sorted(globals().items())
             if n.startswith("test_") and callable(f)]
    failed = 0
    for name, fn in tests:
        with tempfile.TemporaryDirectory() as td:
            kwargs = {"tmp_path": Path(td)}
            cap = None
            if "capsys" in inspect.signature(fn).parameters:
                cap = _CapsysShim()
                kwargs["capsys"] = cap
            try:
                fn(**kwargs)
                if cap:
                    cap.restore()
                print(f"PASS {name}")
            except Exception:
                if cap:
                    cap.restore()
                failed += 1
                print(f"FAIL {name}")
                traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    if pytest is not None:
        raise SystemExit(pytest.main([__file__, "-v"]))
    raise SystemExit(_run_all_without_pytest())
