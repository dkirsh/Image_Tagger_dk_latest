# Sprint A — Corpus Database: progress report

*Date: 2026-08-09 (filename per sprint brief). Author: Tanishq (with Claude). Branch:
`cnfa-algs-2026-07-14` (HEAD `084b3f3d`; contains `02159eef` "Morning summary 2026-07-21").*

## What was implemented

Sprint A first deliverable: a dependency-light SQLite database that turns `corpus_L6/`
("a folder of PNGs + two CSVs") into a real queryable image database, joining curation
(`manifest.csv`), provenance (`_provenance.csv`), the live 68-attribute registry, and
(optional, Sprint E) computed scores.

**Files added (nothing else touched):**

- `scripts/corpus_db.py` — builder + query tool + Python API (stdlib only: sqlite3, csv,
  argparse, json, pathlib, dataclasses; no pandas, no SQLAlchemy, no new dependencies)
- `tests/test_corpus_db.py` — 10 deterministic tests on tmp-path fixture corpora
- `reports/SPRINT_A_CORPUS_DB_PROGRESS_2026-08-06.md` — this report

**Read-only guarantees held:** corpus CSVs never modified (regression-tested);
`annotation_socket/` imported but never edited; no MPIB/Hough/M1′ code touched;
`collect_corpus_L6.py` and `build_corpus_index.py` unmodified.

## Schema (corpus_L6/corpus.db)

- `images` — one row per image (PK `filename`). Identity/provenance: sha256, source,
  source_id, creator, license, license_url, orig_url, collected_utc, gdrive_path, width,
  height, px_bucket. Taxonomy: category, arch_type, space_family. A/B pairing: pair_id,
  pair_role, pair_expected_better, manipulation, notes.
- `attributes` — the 68 registry terms (PK `attr_id`): family, human_label, tier_hint,
  m1p_audited, atlas_node_ids, unit, range, definition.
- `scores` — image × attribute join (PK filename+attr_id, FKs to both): value, tier,
  confidence, abstained, m1p_digest, computed_utc, pctile_in_corpus.
- `human_labels` — empty until the 2AFC campaign (PK filename+construct): human_score,
  ci_low, ci_high, n_judgments, agreement.
- `images_fts` — FTS5 full-text over filename, source, category, arch_type, space_family,
  manipulation, notes (graceful LIKE fallback if a local SQLite lacks FTS5).
- Indexes on scores(attr_id,value), scores(attr_id,pctile_in_corpus), images(space_family),
  images(arch_type), images(category).

## Key design decisions

- **Attribute seeding** is from the live registry (`annotation_socket.registry.PREDICATES`,
  read-only import; robust adapter handles dict/list/object/string predicate shapes). In this
  repo it loads exactly **68 rows**. `m1p_audited` is seeded from the read-only
  `M1P_BINDINGS` table in `annotation_socket/m1_prime.py` — exactly **28** flagged, matching
  the sprint list; if that module can't import (it needs numpy/cv2), the flag stays NULL
  (= unknown), never a guessed 0. If the registry itself is unimportable (bare test env),
  build still succeeds and reports `attributes_source: unavailable(...)`.
- **CSV merging**: union of manifest + provenance filenames (manifest curation fields win),
  sorted by filename — deterministic. Header aliases supported per the brief (path/image/file/
  rel_path, w/h, licence, original_url/url, caption/description, dataset/source_name, ...).
- **Taxonomy derivation**: `arch_type`/`space_family` are not columns in the current CSVs, so
  they are derived by importing the pure functions `arch_type()`/`family_of()` from
  `scripts/build_corpus_index.py` — single source of truth for the room-class taxonomy, no
  duplication. Explicit CSV columns, if ever added, take precedence.
- **px_bucket** uses **max(width, height)** per the Sprint A brief. NOTE: this intentionally
  differs from `build_corpus_index.py`, which buckets on the short side (min). Flagged for a
  David/pair-review decision on which convention the project standardizes on.
- **Scores robustness (§19 option B)**: a score whose attr_id is missing from the registry
  gets a minimal placeholder attribute row (counted as `score_attrs_added` in the build
  summary) — a Sprint E run producing a new attribute cannot crash the build. A score for an
  image we don't have is skipped and counted (`scores_skipped_unknown_image`) — we don't
  invent provenance. Both long format (`filename,attr_id,value,...`) and the wide format
  documented in `build_corpus_index.py` (`filename,<attr>=value,...`) are accepted.
- **Idempotency**: every build fully re-derives images/attributes/scores (DELETE + reload
  inside one transaction, FK checks deferred to commit); `--rebuild` deletes the DB file.
  `human_labels` is preserved across non-rebuild refreshes (it will be filled by the 2AFC
  campaign, not by this loader). Building twice yields identical row counts (tested).
- `corpus_L6/corpus.db` is already covered by the repo's gitignore (verified with
  `git check-ignore`), so the DB artifact never enters the index.

## CLI examples

```bash
python scripts/corpus_db.py build --corpus-dir corpus_L6 --rebuild
python scripts/corpus_db.py query --db corpus_L6/corpus.db --text corridor --limit 10
python scripts/corpus_db.py query --db corpus_L6/corpus.db --space-family work --limit 20
python scripts/corpus_db.py query --db corpus_L6/corpus.db \
    --attr-id cnfa.fluency.processing_load_proxy --min-pctile 80 --limit 20
python scripts/corpus_db.py query --db corpus_L6/corpus.db --text "bright lobby" \
    --export reports/lobby_query.csv
```

Python API: `build_database(corpus_dir, db_path=None, rebuild=False) -> dict` and
`query(db_path, QuerySpec(...)) -> list[dict]`.

## Test command and observed result

```
PYTHONPATH=. python -m pytest tests/test_corpus_db.py -v     # preferred
PYTHONPATH=. python tests/test_corpus_db.py                  # stdlib fallback runner
```

Observed (build sandbox, 2026-08-09): **10/10 passed** — build+query, attr value-range query,
CLI build/query/export, CSV-non-mutation regression, filename-alias (`path`) handling,
idempotent rebuild, missing scores.csv, registry seeding (68), placeholder attr for unknown
score attr, skip-and-count for unknown-image score. (The sandbox used for this report could
not install pytest — its package registries are network-blocked — so the run above used the
fallback runner, which executes the identical test functions. The pytest command is unchanged
and expected to pass on the Mac venv; please run it there once.)

Real-corpus build observed:

```
{"images": 538, "attributes": 68, "scores": 0, "score_attrs_added": 0,
 "scores_skipped_unknown_image": 0,
 "attributes_source": "annotation_socket.registry.PREDICATES", "fts5": true,
 "db_path": "corpus_L6/corpus.db"}
```

Facet sanity on the real DB: m1p_audited=1 for 28 attributes; families = fluency-clutter 16,
light 11, geometry-space 11, layout-wellbeing 26, acoustic 2, material 1, cognitive-salience 1
(Σ=68); space_family = pairs 164, domestic 119, work 90, civic 52, other 33, hospitality 29,
retail 26, circulation 21, learning 4. `--text corridor` → 19 hits; `--text lobby` → 0 because
the corpus currently contains no lobby images (0 in both CSVs), not an FTS failure.

## Known limitations

- `corpus_L6/scores.csv` does not exist until Sprint E runs the Tagger over the corpus; build
  loads zero scores today (by design — this build never computes Tagger scores).
- `human_labels` stays empty until the 2AFC labelling campaign (IRB-gated).
- The attributes table depends on `annotation_socket.registry.PREDICATES` in the real repo;
  outside the repo it falls back (0 seeded, clearly reported) and placeholder-seeds attrs met
  in scores.csv. `unit`/`range`/`atlas_node_ids` are empty until the registry (or Atlas
  binding) supplies them — not invented here.
- `pctile_in_corpus` is stored as given in scores.csv, not computed here; Sprint E should
  emit it (or we add a deterministic percentile pass at that point).
- `manifest.csv` has ~170 rows with no provenance row yet (px_bucket "unknown", empty
  source/sha) — visible honestly in the DB, matching the CSVs.
- px_bucket convention (max vs the index's min) needs a standardization decision.
- `scripts/build_corpus_index.py` HTML is **not** repointed at the DB yet (deliberately — it
  is professor-authored and working; see next steps).

## Next steps

1. Run `PYTHONPATH=. python -m pytest tests/test_corpus_db.py -v` on the Mac venv (pytest
   unavailable in the build sandbox).
2. Claim the Sprint A row in `TASKS.md` per repo protocol (not done here — commit/claim is
   Tanishq's call, and registry-adjacent work is pair-with-review).
3. Minimal `--from-db` option for `scripts/build_corpus_index.py` so the browse HTML reads
   live DB data — deferred to keep this change small and to pair-review edits to a
   professor-authored file.
4. Sprint E: batch-run the Tagger → `corpus_L6/scores.csv` (long format ready), then
   percentile computation and "high prospect, low clutter" compound queries.
5. Decide px_bucket convention; consider indexing Stephan's `datasets_offtheshelf/`
   manifests and, later, ZHA/Metrotopia 2D/3D asset pointers as additional sources.
