# Sprint E — Corpus Scoring Pipeline (progress)

**Date:** 2026-08-09
**Branch:** `tanishq-sprint-a-corpus-db-v2`
**Base commit:** `fb85ee1b` (Sprint A) on top of `084b3f3d` (`origin/cnfa-algs-2026-07-14`)
**Author:** Tanishq Rathore
**Outcome:** **B — scoring wrapper implemented and tested; real annotator blocked locally.**

---

## 1. Purpose

Sprint E is the bridge from the Tagger to the Sprint A database. It runs the annotator over
`corpus_L6`, emits `corpus_L6/scores.csv` in the long format Sprint A already expects, computes
`pctile_in_corpus` per attribute, and optionally rebuilds `corpus_L6/corpus.db` so the `scores`
table populates.

Sprint A left the DB with 538 images, 68 attributes and **0 scores**, because `scores.csv` did
not exist. Sprint E is the step that produces it.

## 2. Files created

| File | Purpose |
| --- | --- |
| `scripts/score_corpus_L6.py` | Batch scorer: CLI + importable module (~560 lines) |
| `tests/test_score_corpus_L6.py` | 14 tests, fixture-only, no real corpus or annotator needed |
| `reports/SPRINT_E_CORPUS_SCORING_PROGRESS_2026-08-09.md` | This report |
| `reports/SPRINT_E_CORPUS_SCORING_RUN_20260809_DRYRUN.json` | Dry-run summary artifact |
| `reports/SPRINT_E_CORPUS_SCORING_RUN_20260809_BLOCKED.json` | Blocked-run summary artifact |

**No existing file was modified.** In particular `scripts/corpus_db.py` needed no change: it
already exports `SCORE_COLUMNS` and `build_database()`, which the scorer imports and reuses.

## 3. How the scorer works

1. Read `manifest.csv` (filename aliases: `filename`, `path`, `image`, `file`, `rel_path`).
2. Resolve each filename to a local file: absolute → `corpus_dir/filename` →
   `repo_root/filename` → `corpus_dir/basename`. Unresolvable names are counted and sampled,
   never fatal.
3. Import the annotator (`annotation_socket.annotator.annotate_image`). Import failure is
   translated into a structured `AnnotatorUnavailable` blocker, not a stack trace.
4. Annotate each image, flatten the record to long-format rows.
5. Compute `pctile_in_corpus` per `attr_id` over non-abstained numeric rows.
6. Write `scores.csv` atomically (temp file in the same directory → `os.fsync` → `os.replace`).
7. Optionally rebuild the DB via `corpus_db.build_database(corpus_dir, rebuild=True)`.
8. Write a JSON run summary to `reports/`.

### Output schema

`filename, attr_id, value, tier, confidence, abstained, m1p_digest, computed_utc, pctile_in_corpus`
plus three honest extras: `status`, `reason`, `model_version`. The first nine are asserted at
runtime to equal `corpus_db.SCORE_COLUMNS`, so the two files cannot silently drift
(`schema_warning` in the run report is `null` when they agree). `corpus_db` ignores the extras.

### Flattening rules

Reads the repo's real record shape (`record["scores"]` → entries with `predicate`, `status`,
`value`, `tier_hint`, `evidence.confidence`, `m1p.digest`) and also tolerates generic shapes
(dict containers, bare lists, alias keys) per the Sprint E spec.

Truth rules:

- finite numeric value + non-abstained status → scored row, `abstained=0`
- `ABSTAINED` / `UNKNOWN` / non-numeric / missing value → **explicit abstention row**,
  `abstained=1`, empty `value`, `reason` recorded (e.g. `missing_inputs:depth_map`,
  `no_numeric_value`). Rows are emitted rather than dropped so coverage gaps stay visible.
- `m1p_digest` is written **only** when the record genuinely carries one. An `m1p` block that
  contains only `{"error": "emit_failed:..."}` yields an empty digest — the pipeline never
  claims a score is M1′-signed when it is not.

### Percentiles

Per `attr_id`, over non-abstained numeric rows only:
`pctile = 100 * midpoint_rank / (n - 1)`; `n == 1 → 50.0`; ties share the midpoint rank.
Abstained/non-numeric rows keep an empty percentile. Percentiles are recomputed across the
**whole** merged set on every write, so a resumed run never leaves stale percentiles from a
smaller sample.

### Determinism

- `OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS`, `MKL_NUM_THREADS`, `NUMEXPR_NUM_THREADS`,
  `VECLIB_MAXIMUM_THREADS` pinned to `1` **before** numpy/cv2 import.
- `cv2.setNumThreads(1)` when cv2 is importable (it is: 4.11.0).
- Output rows sorted by `(filename, attr_id)`; deterministic tie handling in percentiles.
- Every run records an environment fingerprint: python version, platform, cwd, git commit,
  git branch, cv2 version, argv.

## 4. CLI

```
# resolve manifest + images, write nothing
PYTHONPATH=. python3 scripts/score_corpus_L6.py --corpus-dir corpus_L6 \
    --out corpus_L6/scores.csv --limit 10 --dry-run

# score, preserving anything already in scores.csv
PYTHONPATH=. python3 scripts/score_corpus_L6.py --corpus-dir corpus_L6 \
    --out corpus_L6/scores.csv --limit 10 --resume

# score only images absent from scores.csv, then rebuild the DB
PYTHONPATH=. python3 scripts/score_corpus_L6.py --corpus-dir corpus_L6 \
    --out corpus_L6/scores.csv --only-missing --rebuild-db
```

Flags: `--corpus-dir --out --manifest --provenance --limit --resume --only-missing
--skip-existing --force --dry-run --rebuild-db --fail-fast --max-failures --image-glob
--report-path --no-report`.

Exit codes: `0` success, `1` failures with `--fail-fast`, `2` annotator blocked.

## 5. Tests

`PYTHONPATH=. python3 tests/test_score_corpus_L6.py` → **14/14 passed.**

pytest is **not installed** in this environment and there is no `.venv`, so the stdlib fallback
runner (same pattern as `tests/test_corpus_db.py`) was used.

Coverage: filename resolution incl. aliases and prefix forms; missing-image handling; fake
annotator flattening; alternate record shapes; required columns + Sprint A schema equality;
percentiles incl. ties, `n == 1`, and abstained exclusion; resume preserves rows and recomputes
percentiles; `--only-missing` equivalence; dry-run writes nothing and leaves an existing file
byte-identical; `--rebuild-db` not called unless asked (monkeypatched); non-numeric → honest
abstention; **blocked annotator writes no file**; deterministic ordering and reproducibility;
atomic write leaves no temp files.

Sprint A regression check: `tests/test_corpus_db.py` → **10/10 still passing.**

## 6. Blockers — why real scoring did not run

**Two independent blockers. Either alone prevents real scoring.**

### Blocker 1 — no corpus images exist in this checkout (primary)

`corpus_L6/` contains only `manifest.csv`, `_provenance.csv` and `corpus.db`. There are
**0 PNG files for 538 manifest rows**. `.gitignore:53` (`corpus_L6/*`, with exceptions only for
the two CSVs) deliberately keeps the canonical PNGs out of git, and `_provenance.csv` records
`orig_url` values under `/Users/davidusa/.cache/l6_kaggle/...`, a path that does not exist on
this machine. 169 of 369 provenance rows carry a `gdrive_path`.

Dry-run evidence (`--limit 5`): `images_seen: 5`, `images_missing_file: 5`, e.g.
`interiors/industrial_open_office.png`, `nature_glass/farnsworth_foliage_through_glazing.png`.

### Blocker 2 — the `cpp` control library is missing

`annotation_socket/annotator.py:22` executes `from cpp import stage` at **module import time**.
The module inserts `/Users/davidusa/REPOS/_control` (and a sandbox path) into `sys.path`;
neither exists here, so `import annotation_socket.annotator` fails with
`ModuleNotFoundError: No module named 'cpp'`.

Notably the blocker is narrow — everything else imports cleanly:

| Module | Status |
| --- | --- |
| `cv2` | OK 4.11.0 |
| `numpy` | OK 2.2.5 |
| `cnfa_algs` | OK |
| `annotation_socket.registry` | OK — 68 predicates |
| `annotation_socket.m1_prime` | OK — 28 M1′ bindings |
| `annotation_socket.annotator` | **FAILS** — `from cpp import stage` |

`cpp.stage` is not incidental: it enforces the CPP `[W:]` write boundary
(`stage.assert_can_write`) that stops the worker writing `accepted/`, `control.jsonl` or
`verdicts.jsonl`. **It was deliberately not stubbed** — a shim would bypass a real safety
boundary of the M1′ audit design. `annotate_image` itself does not call `stage`, so vendoring or
path-adding the genuine library should be sufficient.

### What was explicitly NOT done

No fake `scores.csv` was written for the real corpus. The blocked run exits `2`, prints the
precise failing import and hint, and leaves `corpus_L6/scores.csv` non-existent. Fake annotators
exist only inside the test file, injected programmatically via `run(..., annotate_fn=...)`;
there is **no CLI flag** that can fabricate production scores.

## 7. Current state

- `corpus_L6/scores.csv` — **does not exist** (correct for Outcome B)
- `corpus_L6/corpus.db` — unchanged, still `scores: 0`
- `corpus_L6/manifest.csv`, `corpus_L6/_provenance.csv` — unchanged (checksums verified)
- `annotation_socket/` — unchanged
- `scripts/corpus_db.py` — unchanged

## 8. Known limitations

- The scorer has never executed against a real annotation record. The flattening adapter is
  written against the record shape read from `annotator.py` and `derivation.py`, and is tested
  against a fixture built to that shape, but the first real run may still surface mismatches.
- Percentiles computed on a partial corpus are only meaningful relative to the rows present;
  they are recomputed on every write, so a full run corrects them.
- The spot-check against a single-image `annotate` run (Sprint E done-when) is **not yet done** —
  it needs a working annotator.
- Non-PNG manifest entries are skipped by default (`--image-glob`); currently moot at 0 images.

## 9. Next steps

1. **Unblock images.** Confirm with Prof. Kirsh how the L6 PNGs should reach a student checkout
   (Drive sync via the 169 `gdrive_path` entries, or a local rebuild through
   `scripts/collect_corpus_L6.py`). `_provenance.csv` carries `sha256` for all 369 rows, so
   integrity can be verified after transfer.
2. **Unblock the annotator.** Obtain the genuine `cpp` control library, or confirm whether the
   student workflow is meant to call the tagger through a different entry point.
3. Re-run `--limit 5 --resume --rebuild-db`, then spot-check one image against a direct
   `annotate_image` call.
4. Only after that spot-check matches, request approval for a full 538-image run.
5. Query the populated DB:
   `python3 scripts/corpus_db.py query --db corpus_L6/corpus.db --attr-id <attr> --limit 5`.

---

**Summary:** the batch runner and its tests are implemented and passing, but real scoring cannot
run locally because (1) the corpus PNGs are not in this checkout and (2) the `cpp` control
library that `annotation_socket/annotator.py` imports is missing. No fake production scores were
written.
