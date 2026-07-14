# CNfA SESSION HANDOFF — 2026-07-14 (live; overwrite in place)

**TO RESUME:** open a Cowork session, connect `/Users/davidusa/REPOS`, and paste:
`Read /Users/davidusa/REPOS/Image_Tagger_dk_latest/docs/CNFA_SESSION_HANDOFF_2026-07-14.md and continue.`
(Chat transcripts don't survive account/session switches; this file + the repo do.)

## What this workstream is
Operationalizing CNfA visual attributes (wayfinding + social affordance) as running
algorithms over interior images / inferred floor plans / real plans, with a
validation harness. All work lives in `Image_Tagger_dk_latest/`. Fable (Opus red-team
persona) wrote and tested everything below on 2026-07-13/14.

## Artifact map (all inside Image_Tagger_dk_latest/)
- `Reading_Rooms_as_Behavior.docx` — 34-pp research essay (in REPOS root, not here)
- `docs/CNFA_ATTRIBUTE_INVENTORY_AND_ALGORITHMS_2026-07-13.md` (+.docx) — attribute
  inventory: simple/complex, algorithm status, localizability, display, reliability
- `cnfa_algs/` — the package (core, geometry, attributes, plan) + `validation/`
  (probes, vlm_judge, stats, AG_GEMINI_PROMPTS.md) + `adapters/`
  (segmentation SegFormer, spatiallm, structured3d, acoustics_sim, EXTERNAL_MODELS_CATALOG.md)
- `cnfa_demo/run_batch.py` etc.; outputs in `cnfa_algs_demo_outputs/`
  (batch_contact_sheet.png, batch_scalar_matrix.csv, fable_judge_convergence.json)
- `cnfa_external_collect/collect_external.sh` (models; RUN by Codex 2026-07-14)
  and `collect_datasets_to_gdrive.sh` (datasets -> GDrive; NOT yet run)
- `structured3d/download_structured3d.sh` (superseded by the gdrive script)
- Codex prompt for next run: `docs/CODEX_PROMPT_gdrive_and_fixes_2026-07-14.md`

## State (verified)
1. Tier A/B/C pipeline RUNS: 16 real photos batch-processed; matched-pair and
   corridor/glass-box/office contrasts behave correctly (see scalar matrix).
2. Validation harness RUN once (Fable as stand-in judge, N=8):
   load rho=.93, enclosure .81 CONVERGING; acoustic .34 WEAK; landmark −.30,
   cross-image prospect, warm/cool, glare FAILING — causes identified, fixes =
   the adapters below. Clean judge = Gemini via `validation/vlm_judge.py`
   (prompts in AG_GEMINI_PROMPTS.md; blind protocol, canaries, receipts).
3. Codex collector run 2026-07-14: 9.0G weights + 346M repos OK (SegFormer,
   Mask2Former, DepthAnything, ZoeDepth, GroundingDINO, OWLv2, CLIP, SpatialLM,
   GeoCalib, PerspectiveFields, HorizonNet, MASt3R, depthmapX). Structured3D
   ~13G local (annotation_3d + bbox + perspective_full_00 presumed — verify).

## Open items (exact next actions)
A. **Two collector failures** (fix spec in the Codex prompt doc):
   1. "No depth ONNX under weights/" — re-download onnx-community/
      depth-anything-v2-small WITHOUT the include filter; locate model.onnx;
      export DEPTH_ANYTHING_ONNX_PATH.
   2. Acoustics self-test hard==soft 0.13s — CAUSE: max_order=6 truncation.
      FIXED in `cnfa_algs/adapters/acoustics_sim.py` (now max_order=24, T20);
      re-run `python -m cnfa_algs.adapters.acoustics_sim` to confirm PASS.
B. **GDrive dataset offload** — run `cnfa_external_collect/collect_datasets_to_gdrive.sh`
   via Codex AFTER David does the one-time `rclone config` OAuth (Codex must
   never do the OAuth). Method: rclone copy->verify->delete (RULE 0 order).
C. **Git hygiene** — commit the cnfa_* work locally per the spec in the Codex
   prompt (gitignore weights/datasets first!); push only per that spec.
D. **L0 ground-truth run** (Claude, next session): unzip annotation_3d, parse
   first scenes with `adapters/structured3d_adapter.py` (best-effort parser —
   VERIFY field wiring on real data), score Tier-B inferred plans vs truth
   with `plan_iou()`; render → attribute → compare.
E. **Upgraded batch rerun**: wire SegFormer + depth ONNX paths into the
   pipeline (hooks exist: `segment_planes(provided=)`, DEPTH_ANYTHING_ONNX_PATH),
   rerun the 16-image batch, compare scalar matrix + validation verdicts vs v0.1.
F. **Gemini judge run**: AG prompt ready in validation/AG_GEMINI_PROMPTS.md.

## Safety rails in force
Codex: local commits only unless push explicitly authorized per the prompt
spec; never `git add -A`; NEVER commit `cnfa_external/`, `datasets_local/`,
`structured3d/*.zip`, `.venv` (gitignore them); RULE 0: no deletion of
downloaded data until size-verified on Drive; Codex never performs Google
OAuth; Structured3D is research-only — private Drive, no public shares.
