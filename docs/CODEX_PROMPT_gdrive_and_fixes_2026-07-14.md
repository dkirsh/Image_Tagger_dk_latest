# CODEX TASK — GDrive dataset offload + collector fixes + git hygiene (2026-07-14)

Paste everything below this line to Codex.

---

You are working in `/Users/davidusa/REPOS/Image_Tagger_dk_latest` (cd there first;
ALL relative paths below are relative to that directory). Absolute paths of the
key files, verified 2026-07-14:
- this prompt:      /Users/davidusa/REPOS/Image_Tagger_dk_latest/docs/CODEX_PROMPT_gdrive_and_fixes_2026-07-14.md
- gdrive script:    /Users/davidusa/REPOS/Image_Tagger_dk_latest/cnfa_external_collect/collect_datasets_to_gdrive.sh
- model collector:  /Users/davidusa/REPOS/Image_Tagger_dk_latest/cnfa_external_collect/collect_external.sh
- acoustics module: /Users/davidusa/REPOS/Image_Tagger_dk_latest/cnfa_algs/adapters/acoustics_sim.py
- handoff doc:      /Users/davidusa/REPOS/Image_Tagger_dk_latest/docs/CNFA_SESSION_HANDOFF_2026-07-14.md

Work through the four parts IN ORDER. Rails: LOCAL machine only; no sudo; never `git add -A`;
NEVER perform Google OAuth or enter David's credentials — if auth is missing,
STOP that part and report; do not delete any downloaded data except at the one
explicitly specified step after verification. Report progress per part.

## PART 0 — Preconditions
1. `rclone version` — if rclone is not installed: `brew install rclone` (no sudo).
2. `rclone lsd gdrive:` — if this errors, STOP Part 2 and report exactly:
   "NEEDS DAVID: run `rclone config` -> new remote, name `gdrive`, type `drive`,
   accept defaults, sign in via browser." Continue with Parts 1, 3, 4.

## PART 1 — Git hygiene (do this FIRST so later parts can't pollute the repo)
1. Create/append `.gitignore` in the repo root with EXACTLY these entries if absent:
   ```
   cnfa_external_collect/cnfa_external/
   cnfa_external_collect/datasets_local/
   cnfa_external_collect/.venv/
   structured3d/*.zip
   *.pyc
   __pycache__/
   .DS_Store
   ```
2. Stage ONLY these paths (never `git add -A`):
   `cnfa_algs/ cnfa_demo/ cnfa_algs_demo_outputs/ cnfa_external_collect/*.sh
    structured3d/*.sh docs/CNFA_* docs/CODEX_PROMPT_gdrive_and_fixes_2026-07-14.md
    .gitignore`
   (NOTE: `Reading_Rooms_as_Behavior.docx` is at /Users/davidusa/REPOS/ — the
   PARENT folder, OUTSIDE this repo. Do not try to stage it here.)
3. Verify with `git status --short` that NO weights/zips/venv are staged. If any
   large binary (>25MB) is staged, unstage it and add to .gitignore instead —
   EXCEPT the two .docx and the demo-output PNGs/CSVs, which are wanted.
4. Commit locally:
   `git commit -m "cnfa: attribute algorithms v0.1, validation harness, adapters, collectors (2026-07-13/14 Fable session)"`
5. PUSH POLICY: run `git remote -v`.
   - If NO remote: report "no remote configured" and stop Part 1 here.
   - If a remote exists AND its URL is under David's own account
     (github.com/<something clearly David's>): create branch
     `cnfa-algs-2026-07-14`, push ONLY that branch
     (`git push -u origin cnfa-algs-2026-07-14`). NEVER push to main/master.
   - If the remote URL is anything else or you are unsure: do not push; report
     the URL and wait.

## PART 2 — Datasets to Google Drive (the reliable method: rclone, copy->verify->delete)
Precondition: Part 0 step 2 passed.
1. Run the prepared script:
   `bash cnfa_external_collect/collect_datasets_to_gdrive.sh`
   (defaults: MODE=rclone, REMOTE=gdrive:Structured3D). It:
   - streams every missing Structured3D shard (annotation, bbox, perspective_full
     00-17 minus corrupted 09) DIRECTLY to Drive via `rclone copyurl` (no local disk),
   - size-verifies each against the server Content-Length, skips verified ones,
   - keeps annotation_3d + bbox LOCALLY in `cnfa_external_collect/datasets_local/`
     (working copies for analysis).
2. The ~13G ALREADY DOWNLOADED locally (from the earlier run — locate the zips,
   likely `structured3d/` or `cnfa_external_collect/cnfa_external/datasets/`):
   upload them rather than re-downloading, in this exact RULE-0 order per file:
   a. `rclone copy <local.zip> gdrive:Structured3D/ -P`
   b. `rclone check <dir-with-file> gdrive:Structured3D/ --one-way --size-only
       --include <file>` — must report 0 differences
   c. ONLY THEN delete the local copy — EXCEPT keep
      `Structured3D_annotation_3d.zip` and `Structured3D_bbox.zip` local
      (move them into `cnfa_external_collect/datasets_local/`).
   If any check fails, keep the local file and report.
3. Finish: `rclone lsl gdrive:Structured3D` — paste the listing + local
   `du -sh` of what remains into your report.

## PART 3 — Fix collector failure #1: missing depth ONNX
1. `source cnfa_external_collect/.venv/bin/activate`
2. Re-download without the include filter:
   `hf download onnx-community/depth-anything-v2-small --local-dir cnfa_external_collect/cnfa_external/weights/depth-anything-v2-small`
   (use `huggingface-cli` if `hf` is absent).
3. `find cnfa_external_collect/cnfa_external/weights/depth-anything-v2-small -name "*.onnx"`
   — report every hit. Pick the plain `model.onnx` (not *_fp16/quantized) and verify:
   `python -c "import onnxruntime as o; s=o.InferenceSession('<PATH>',providers=['CPUExecutionProvider']); print([i.name for i in s.get_inputs()])"`
4. Append to a new file `cnfa_external_collect/env.sh`:
   `export DEPTH_ANYTHING_ONNX_PATH=<ABSOLUTE PATH>` and report the line.

## PART 4 — Fix collector failure #2: acoustics self-test
The cause was found and patched by Fable (image-source max_order=6 truncated the
decay, making hard and soft rooms measure identically; now max_order=24 + T20).
1. `source cnfa_external_collect/.venv/bin/activate`
2. `cd /Users/davidusa/REPOS/Image_Tagger_dk_latest && PYTHONPATH=. python -m cnfa_algs.adapters.acoustics_sim`
3. Expected: hard-room RT60 clearly larger than soft (roughly: hard > 1s, soft
   well under half of hard) and final line `acoustics_sim self-test: PASS`.
   Report the two RT60 numbers verbatim. If it still fails, report the full
   output — do NOT edit the module yourself.

## REPORT FORMAT (return to David)
Per part: OK/FAIL/NEEDS-DAVID + the key evidence (git status summary, branch
pushed or not + remote URL, rclone listing, ONNX path, RT60 numbers). No
fabricated successes; a FAIL with detail beats a fake OK.
