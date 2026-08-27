"""tests/test_score_corpus_L6.py — Sprint E corpus scoring (scripts/score_corpus_L6.py).

Self-contained: builds tiny fixture corpora under tmp_path and injects a FAKE annotator.
Never reads or writes the real corpus_L6/, never requires the real annotator, never
requires real images. Deterministic (fixed fixture contents, no randomness).

Run:  PYTHONPATH=. python -m pytest tests/test_score_corpus_L6.py -v
Fallback (no pytest installed): PYTHONPATH=. python tests/test_score_corpus_L6.py
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

try:
    import pytest
except ImportError:          # stdlib fallback runner below (__main__); pytest preferred
    pytest = None

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import score_corpus_L6 as S  # noqa: E402  (scripts/score_corpus_L6.py)


# --------------------------------------------------------------------------- fixtures
def make_corpus(tmp_path: Path, filenames, subdir="interiors") -> Path:
    """A minimal corpus: manifest.csv + real (tiny) files at the manifest paths."""
    corpus = tmp_path / "corpus_L6"
    (corpus / subdir).mkdir(parents=True, exist_ok=True)
    with (corpus / "manifest.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["filename", "category", "pair_id", "pair_expected_better", "notes"])
        for fn in filenames:
            w.writerow([fn, "interiors", "", "unknown", "fixture"])
    for fn in filenames:
        p = corpus / fn
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b"\x89PNG\r\n\x1a\n" + fn.encode())   # not a real PNG; never decoded
    return corpus


def fake_annotator(values_by_file):
    """A fixture annotator returning records shaped like the real annotate_image()."""
    def _annotate(image_path):
        name = Path(image_path).name
        entries = []
        for attr_id, value in values_by_file[name].items():
            if value is None:
                entries.append({"predicate": attr_id, "status": "ABSTAINED",
                                "missing_inputs": ["depth_map"], "value": None,
                                "evidence": None})
            elif isinstance(value, str):
                entries.append({"predicate": attr_id, "status": "SCORED", "value": value,
                                "tier_hint": "GREEN",
                                "evidence": {"kind": "global_image", "signal": "fx",
                                             "confidence": 0.5}})
            else:
                entries.append({"predicate": attr_id, "status": "SCORED", "value": value,
                                "tier_hint": "GREEN",
                                "evidence": {"kind": "global_image", "signal": "fx",
                                             "confidence": 0.9},
                                "m1p": {"audit_class": "replayable",
                                        "digest": "sha256:" + "a" * 8}})
        return {"unit_id": "u", "image_path": image_path, "model_version": "fixture-1",
                "scores": entries, "coverage": {}}
    return _annotate


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


# --------------------------------------------------------------------------- 1. resolution
def test_manifest_filename_resolution(tmp_path):
    corpus = make_corpus(tmp_path, ["interiors/a.png"])
    # plain relative
    assert S.resolve_image_path("interiors/a.png", corpus) == corpus / "interiors/a.png"
    # leading './'
    assert S.resolve_image_path("./interiors/a.png", corpus) == corpus / "interiors/a.png"
    # duplicated corpus dir prefix
    assert S.resolve_image_path("corpus_L6/interiors/a.png", corpus) == corpus / "interiors/a.png"
    # absolute
    absolute = str((corpus / "interiors/a.png").resolve())
    assert S.resolve_image_path(absolute, corpus) == Path(absolute)
    # filename aliases in the manifest
    rows = [{"path": "interiors/a.png"}, {"image": "interiors/b.png"}, {"rel_path": "c.png"}]
    assert S.manifest_filenames(rows) == ["interiors/a.png", "interiors/b.png", "c.png"]


# --------------------------------------------------------------------------- 2. missing image
def test_missing_image_is_counted_not_fatal(tmp_path):
    corpus = make_corpus(tmp_path, ["interiors/a.png"])
    # manifest names a second image that does not exist on disk
    with (corpus / "manifest.csv").open("a", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerow(["interiors/gone.png", "interiors", "", "unknown", ""])

    out = corpus / "scores.csv"
    summary = S.run(corpus, out, annotate_fn=fake_annotator({"a.png": {"attr.x": 1.0}}))

    assert summary["images_missing_file"] == 1
    assert "interiors/gone.png" in summary["missing_files_sample"]
    assert summary["images_scored"] == 1
    assert S.resolve_image_path("interiors/gone.png", corpus) is None


# --------------------------------------------------------------------------- 3. flattening
def test_fake_annotator_output_flattening(tmp_path):
    record = fake_annotator({"a.png": {"attr.scored": 2.5, "attr.abstained": None}})("/x/a.png")
    rows = S.flatten_record("interiors/a.png", record, "2026-08-09T00:00:00+00:00")
    by_attr = {r["attr_id"]: r for r in rows}

    scored = by_attr["attr.scored"]
    assert scored["value"] == 2.5
    assert scored["abstained"] == 0
    assert scored["tier"] == "GREEN"
    assert scored["confidence"] == 0.9
    assert scored["m1p_digest"].startswith("sha256:")
    assert scored["model_version"] == "fixture-1"

    abst = by_attr["attr.abstained"]
    assert abst["abstained"] == 1
    assert abst["value"] == ""
    assert abst["m1p_digest"] == ""          # never invented
    assert "depth_map" in abst["reason"]


def test_flattening_handles_alternate_record_shapes():
    ts = "2026-08-09T00:00:00+00:00"
    # dict container keyed by attr id
    rows = S.flatten_record("f.png", {"attributes": {"a.b": 1.0}}, ts)
    assert rows[0]["attr_id"] == "a.b" and rows[0]["value"] == 1.0
    # bare list of predicate dicts with alias keys
    rows = S.flatten_record("f.png", [{"key": "a.c", "score": 3.0, "conf": 0.25}], ts)
    assert rows[0]["attr_id"] == "a.c" and rows[0]["value"] == 3.0
    assert rows[0]["confidence"] == 0.25
    # explicit abstain flag via alias
    rows = S.flatten_record("f.png", [{"name": "a.d", "value": 1.0, "abstain": True}], ts)
    assert rows[0]["abstained"] == 1 and rows[0]["value"] == ""


# --------------------------------------------------------------------------- 4. columns
def test_scores_csv_required_columns(tmp_path):
    corpus = make_corpus(tmp_path, ["interiors/a.png"])
    out = corpus / "scores.csv"
    S.run(corpus, out, annotate_fn=fake_annotator({"a.png": {"attr.x": 1.0}}))

    with out.open(newline="", encoding="utf-8") as fh:
        header = next(csv.reader(fh))
    for col in ("filename", "attr_id", "value", "tier", "confidence", "abstained",
                "m1p_digest", "computed_utc", "pctile_in_corpus"):
        assert col in header, f"missing required column {col}"
    # and the schema matches Sprint A's contract exactly
    assert tuple(header[:len(S.SCORE_COLUMNS)]) == S.SCORE_COLUMNS


# --------------------------------------------------------------------------- 5. percentiles
def test_percentile_computation_including_ties():
    ts = "2026-08-09T00:00:00+00:00"
    rows = [{"filename": f"f{i}.png", "attr_id": "a", "value": v, "abstained": 0,
             "pctile_in_corpus": "", "computed_utc": ts}
            for i, v in enumerate([1.0, 2.0, 2.0, 4.0])]
    S.compute_percentiles(rows)
    pct = {r["filename"]: r["pctile_in_corpus"] for r in rows}
    assert pct["f0.png"] == 0.0                       # rank 0 of 3
    assert pct["f3.png"] == 100.0                     # rank 3 of 3
    # tied pair occupies ranks 1 and 2 -> midpoint 1.5 -> 50.0
    assert pct["f1.png"] == pct["f2.png"] == 50.0

    # n == 1 -> 50.0
    single = [{"filename": "s.png", "attr_id": "b", "value": 7.0, "abstained": 0,
               "pctile_in_corpus": ""}]
    S.compute_percentiles(single)
    assert single[0]["pctile_in_corpus"] == 50.0

    # abstained rows never receive a percentile
    ab = [{"filename": "x.png", "attr_id": "c", "value": "", "abstained": 1,
           "pctile_in_corpus": ""},
          {"filename": "y.png", "attr_id": "c", "value": 5.0, "abstained": 0,
           "pctile_in_corpus": ""}]
    S.compute_percentiles(ab)
    assert ab[0]["pctile_in_corpus"] == ""
    assert ab[1]["pctile_in_corpus"] == 50.0


# --------------------------------------------------------------------------- 6. resume
def test_resume_preserves_existing_rows_and_scores_only_missing(tmp_path):
    corpus = make_corpus(tmp_path, ["interiors/a.png", "interiors/b.png"])
    out = corpus / "scores.csv"
    vals = {"a.png": {"attr.x": 1.0}, "b.png": {"attr.x": 3.0}}

    contract = {"expected_attr_ids": {"attr.x"}, "expected_model_version": "fixture-1"}
    first = S.run(corpus, out, limit=1, annotate_fn=fake_annotator(vals), **contract)
    assert first["images_scored"] == 1
    rows1 = read_csv(out)
    assert {r["filename"] for r in rows1} == {"interiors/a.png"}

    second = S.run(corpus, out, resume=True, annotate_fn=fake_annotator(vals), **contract)
    assert second["images_skipped_existing"] == 1
    assert second["images_scored"] == 1
    rows2 = read_csv(out)
    assert {r["filename"] for r in rows2} == {"interiors/a.png", "interiors/b.png"}
    # percentiles recomputed across the merged set, not stale from the 1-image run
    pct = {r["filename"]: r["pctile_in_corpus"] for r in rows2}
    assert pct["interiors/a.png"] == "0.0" and pct["interiors/b.png"] == "100.0"


def test_only_missing_is_equivalent_to_resume(tmp_path):
    corpus = make_corpus(tmp_path, ["interiors/a.png", "interiors/b.png"])
    out = corpus / "scores.csv"
    vals = {"a.png": {"attr.x": 1.0}, "b.png": {"attr.x": 3.0}}
    contract = {"expected_attr_ids": {"attr.x"}, "expected_model_version": "fixture-1"}
    S.run(corpus, out, limit=1, annotate_fn=fake_annotator(vals), **contract)
    s = S.run(corpus, out, only_missing=True, annotate_fn=fake_annotator(vals), **contract)
    assert s["images_skipped_existing"] == 1 and s["images_scored"] == 1


def test_resume_rescores_unsealed_partial_image_and_replaces_rows(tmp_path):
    corpus = make_corpus(tmp_path, ["interiors/a.png"])
    out = corpus / "scores.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(S.OUT_COLUMNS))
        writer.writeheader()
        writer.writerow({"filename": "interiors/a.png", "attr_id": "old.only",
                         "value": "1", "abstained": "0"})

    summary = S.run(
        corpus, out, resume=True,
        annotate_fn=fake_annotator({"a.png": {"old.only": 1.0, "new.required": 2.0}}),
        expected_attr_ids={"old.only", "new.required"},
        expected_model_version="fixture-1")
    rows = read_csv(out)
    assert summary["images_incomplete_existing"] == 1
    assert summary["images_skipped_existing"] == 0 and summary["images_scored"] == 1
    assert {r["attr_id"] for r in rows} == {"old.only", "new.required"}
    assert all(r["image_complete"] == "1" and r["image_score_count"] == "2"
               for r in rows)


def test_resume_contract_change_forces_rescore(tmp_path):
    corpus = make_corpus(tmp_path, ["interiors/a.png"])
    out = corpus / "scores.csv"
    S.run(corpus, out, annotate_fn=fake_annotator({"a.png": {"old": 1.0}}),
          expected_attr_ids={"old"}, expected_model_version="fixture-1")
    changed = fake_annotator({"a.png": {"old": 2.0, "new": 3.0}})
    def changed_model(path):
        record = changed(path)
        record["model_version"] = "fixture-2"
        return record
    summary = S.run(
        corpus, out, resume=True, annotate_fn=changed_model,
        expected_attr_ids={"old", "new"}, expected_model_version="fixture-2")
    assert summary["images_skipped_existing"] == 0
    assert summary["images_scored"] == 1
    assert {r["attr_id"] for r in read_csv(out)} == {"old", "new"}


def test_completion_seal_requires_frozen_attribute_and_model_contract():
    rows = S.flatten_record(
        "a.png", fake_annotator({"a.png": {"only": 1.0}})("/x/a.png"),
        "2026-08-09T00:00:00+00:00")
    assert S.seal_complete_image_rows(rows) is False
    assert rows[0]["image_complete"] == 0
    assert S.complete_existing_filenames(rows) == set()


def test_live_registry_exposes_resume_contract():
    attr_ids, model_version = S.load_registry_resume_contract()
    assert len(attr_ids) >= 1
    assert all(isinstance(attr_id, str) and attr_id for attr_id in attr_ids)
    assert isinstance(model_version, str) and model_version


# --------------------------------------------------------------------------- 7. dry run
def test_dry_run_does_not_write_scores(tmp_path):
    corpus = make_corpus(tmp_path, ["interiors/a.png"])
    out = corpus / "scores.csv"
    summary = S.run(corpus, out, dry_run=True,
                    annotate_fn=fake_annotator({"a.png": {"attr.x": 1.0}}))
    assert not out.exists()
    assert summary["images_seen"] == 1
    assert summary["score_rows_written"] == 0

    # and an existing scores.csv is left byte-identical
    out.write_text("filename,attr_id\nkeep,me\n", encoding="utf-8")
    before = out.read_bytes()
    S.run(corpus, out, dry_run=True, annotate_fn=fake_annotator({"a.png": {"attr.x": 1.0}}))
    assert out.read_bytes() == before


# --------------------------------------------------------------------------- 8. rebuild-db
def test_rebuild_db_is_optional_and_not_called_by_default(tmp_path):
    corpus = make_corpus(tmp_path, ["interiors/a.png"])
    out = corpus / "scores.csv"
    summary = S.run(corpus, out, annotate_fn=fake_annotator({"a.png": {"attr.x": 1.0}}))
    assert summary["rebuild_db"] is None          # not invoked unless asked

    calls = []
    original = S.rebuild_db
    S.rebuild_db = lambda cd: (calls.append(cd) or {"images": 1})   # monkeypatch
    try:
        s2 = S.run(corpus, corpus / "scores2.csv", do_rebuild_db=True,
                   annotate_fn=fake_annotator({"a.png": {"attr.x": 1.0}}))
    finally:
        S.rebuild_db = original
    assert calls == [corpus]
    assert s2["rebuild_db"] == {"images": 1}


# --------------------------------------------------------------------------- 9. honesty
def test_non_numeric_value_becomes_abstained_not_invented(tmp_path):
    corpus = make_corpus(tmp_path, ["interiors/a.png"])
    out = corpus / "scores.csv"
    S.run(corpus, out, annotate_fn=fake_annotator({"a.png": {"attr.text": "not_a_number"}}))
    row = read_csv(out)[0]
    assert row["abstained"] == "1"
    assert row["value"] == ""
    assert row["pctile_in_corpus"] == ""
    assert row["reason"] == "no_numeric_value"


def test_missing_annotator_writes_nothing_and_reports_blocker(tmp_path):
    """The Outcome-B guarantee: no annotator -> no scores.csv, no fake rows."""
    corpus = make_corpus(tmp_path, ["interiors/a.png"])
    out = corpus / "scores.csv"

    original = S.load_annotator
    S.load_annotator = lambda: (_ for _ in ()).throw(
        S.AnnotatorUnavailable("no annotator", "ModuleNotFoundError: cpp", "vendor cpp"))
    try:
        summary = S.run(corpus, out)          # annotate_fn=None -> real loader -> blocked
    finally:
        S.load_annotator = original

    assert summary["annotator_available"] is False
    assert summary["annotator_blocker"]["detail"].startswith("ModuleNotFoundError")
    assert summary["score_rows_written"] == 0
    assert not out.exists(), "scores.csv must not be created when the annotator is blocked"


# --------------------------------------------------------------------------- 10. determinism
def test_deterministic_row_ordering(tmp_path):
    corpus = make_corpus(tmp_path, ["interiors/b.png", "interiors/a.png"])
    vals = {"a.png": {"attr.z": 1.0, "attr.a": 2.0},
            "b.png": {"attr.z": 3.0, "attr.a": 4.0}}
    out1, out2 = corpus / "s1.csv", corpus / "s2.csv"
    S.run(corpus, out1, annotate_fn=fake_annotator(vals))
    S.run(corpus, out2, annotate_fn=fake_annotator(vals))

    rows = read_csv(out1)
    keys = [(r["filename"], r["attr_id"]) for r in rows]
    assert keys == sorted(keys), "rows must be sorted by (filename, attr_id)"

    # identical inputs -> identical output, modulo the computed_utc timestamp column
    def strip_ts(path):
        return [{k: v for k, v in r.items() if k != "computed_utc"} for r in read_csv(path)]
    assert strip_ts(out1) == strip_ts(out2)


def test_atomic_write_leaves_no_temp_files(tmp_path):
    corpus = make_corpus(tmp_path, ["interiors/a.png"])
    out = corpus / "scores.csv"
    S.run(corpus, out, annotate_fn=fake_annotator({"a.png": {"attr.x": 1.0}}))
    leftovers = [p.name for p in corpus.iterdir() if p.name.startswith(".scores.")]
    assert leftovers == [], f"temp files left behind: {leftovers}"


# --------------------------------------------------------------------------- fallback runner
def _run_all_without_pytest() -> int:
    import inspect
    import tempfile
    import traceback

    tests = [(n, o) for n, o in sorted(globals().items())
             if n.startswith("test_") and callable(o)]
    failed = 0
    for name, fn in tests:
        with tempfile.TemporaryDirectory() as td:
            kwargs = {}
            if "tmp_path" in inspect.signature(fn).parameters:
                kwargs["tmp_path"] = Path(td)
            try:
                fn(**kwargs)
                print(f"PASS {name}")
            except Exception:
                failed += 1
                print(f"FAIL {name}")
                traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    if pytest is not None:
        raise SystemExit(pytest.main([__file__, "-v"]))
    raise SystemExit(_run_all_without_pytest())
