# SESSION RESUME — 2026-07-21 (paste-ready handoff)

**Mission:** continue the Image_Tagger / CNfA work toward "every viz attribute computationally
correct." The near-term front line is the **L6 corpus** (assembly + integrity), which gates the
construct-validation that de-AMBERs most of the 68 registry predicates.

**Repo:** `/Users/davidusa/REPOS/Image_Tagger_dk_latest`, branch `cnfa-algs-2026-07-14`,
HEAD `ee1cec72` (run `git --no-optional-locks log --oneline -12` to confirm). Many local commits are
**ahead of `latest`** — David pushes with `git push latest cnfa-algs-2026-07-14` (sandbox can't push
over SSH).

## First moves for the new session
1. If on the device bridge: request folder access to `/Users/davidusa/REPOS`. If the UCSD VPN bridge
   flaps (it did repeatedly on 07-20), use the **one-shot-tarball** strategy: in a single `device_bash`
   tar the working tree + `/Users/davidusa/REPOS/_control/{cpp,supervisor}` + a few `Example Images`
   into a lean tarball under the repo, `device_stage_files` it once, then do ALL compute in the cloud
   sandbox (`pip install scikit-image scipy opencv-python-headless`), reconnecting only to commit.
2. **Read (committed):** `docs/L6_CORRECTNESS_PROGRAM_2026-07-21.md` (the plan of record),
   `docs/DK1_CORPUS_BUILD_RUNBOOK_2026-07-20.md`, `TASKS.md`, `CLAUDE.md` (lock-sweep + artifact
   contract), `scripts/collect_corpus_L6.py`, `scripts/../verify_collector_fix.sh` if present.
   Project docs (claude.ai): `claude/L6_CORPUS_TOOLING_2026-07-20.md`,
   `claude/SESSION_FINDINGS_2026-07-20_CNfA_resume.md`.

## Done this session (all committed)
- **Sprint tasks:** reconciled the stranded reliable-A 07-18 batch (HEAD had been inconsistent);
  re-ran the 3-image stage smoke with scikit-image → FC/SE RED cleared; **CC-4** wave-2 geometry
  (W2.2 ceiling_openness_relative, W2.3 double_height, W2.4 blind_corner_index, W2.5
  barrier_permeability, W2.8 threshold_emphasized + registered W2.1/W2.6; registry now **68 preds**);
  **VIEW-3** question-driven composer (advisory-only, score-separated; "street noise on foyer" passes).
- **L6 collector** `scripts/collect_corpus_L6.py`: web (openverse/unsplash/pexels) + academic
  (mit_indoor via Kaggle, from-dir, hf presets **places365/sun397/ade20k**) + Google-Drive storage
  (`--gdrive/--offload/--rehydrate`) + photometric A/B (`--gen-ab`, `--gen-ab-batch`) + `--status`
  + `--seed-all`. David's **filename-digest fix** (sha1(source:id) in the name) is IN the file —
  preserve it. SUN397 preset routes indoor→niches, skips the ~200 outdoor classes.
- **Program doc** `docs/L6_CORRECTNESS_PROGRAM_2026-07-21.md`: A1–A6 checklist → sprints S0–S5 →
  HITL/GUI (2AFC console) → crowdsourcing spec (Prolific primary, ~$1–1.5k, K=15).

## IN FLIGHT / immediate next action — S0 corpus integrity (BLOCKER)
`--status` on 07-20 showed **two problems to clear before the corpus can anchor validation**:
1. **Manifest rows (401) ≫ provenance (232):** ~169 manifest rows have no provenance — almost
   certainly **stale orphans from the pre-fix collision run** (the bug collided filenames *per
   category*, so more than the 26 David removed remain). Run `verify_collector_fix.sh` (audit half)
   + the diagnostic python block in the 07-20 chat; purge orphan rows (manifest AND, if any, the
   derived pairs). True collected count ≈ 232, not 401 — so the category "still needed" counts are
   currently inflated.
2. **Only 32/232 payloads on Drive:** most `gdrive_path` are empty → uploads failed or `--gdrive`
   was dropped. Likely the **retiring rclone shared client_id** (same thing that broke Structured3D).
   Fix: create own Google client_id (rclone.org/drive/#making-your-own-client-id), then re-collect
   idempotently to backfill uploads.
Then finish collection to targets (SUN397 primary high-res academic; MIT Indoor67 only with
`--min-px 512`, it's a low-res 2009 set; Unsplash for niches) and run `--status` until targets met.

## Then (per the program doc)
- S1 (engineering, parallel, no HITL): faithful V2 2-D Penacchio–Wilkins, FC ×4 gain (CC-7), V6/V7
  retirement (CC-6/DEC-3), and **M1′ bindings for the 53 uncovered predicates**.
- S2: DEC-1 model choice → Wave-3 detector (real biophilia/material/water masks) → W2.7 scale anchor
  → calibrate W2.2/W2.3.
- S3/S4: build the 2AFC labeling console (Part C of the program doc), pilot on Prolific, then the full
  validation campaign → `corpus_L6/human_labels.csv` → calibration → tier promotions.
- S5: robustness (CC-9 jitter) + Mac↔sandbox exact-digest replay (L5) + GREEN promotions.

## Gotchas (do not relearn)
- **datasets 5.0.0 dropped loading-script datasets** → ADE20K (`zhoubolei/scene_parse_150`) fails;
  SUN397 (`tanganke/sun397`) is parquet and works; Places365 is 256px (use `--min-px 256`). Always
  `--limit 5 --dry-run` a new HF source first.
- **Kaggle** uses the new `KGAT_` access token (`~/.kaggle/access_token`, chmod 600), not `kaggle.json`.
- **Never overwrite David's working file blind** — he edits `collect_corpus_L6.py` on the Mac. Pull
  his version, merge, and ship with an `expectedMtimeMs` guard (that's how SUN397 was added safely).
- **Ship protocol (CLAUDE.md):** SendUserFile → device_commit_files → git commit with the lock-sweep
  (`mv` stale `.git/*.lock` + `objects/*/tmp_obj_*` to `_to_delete/`, `git --no-optional-locks`, add
  named files only). Corpus PNGs are gitignored — commit only `manifest.csv`.
- **Corpus must be PNG** (L5 JPEG-decode divergence). `--min-px` is per-source: 1024 for stock, 512
  for MIT Indoor67, 256 for Places365.
