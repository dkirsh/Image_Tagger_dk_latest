# Morning summary — overnight run 2026-07-21 (Cowork/Opus)

**TL;DR:** S0's "orphan purge" was a non-issue (corpus is clean); the real S0 gap is the Drive backfill,
which is unblocked the moment your rclone own-client_id is live. I shipped four substantial commits of
engineering + a full expert-panel review that reshaped the plan. Two things need you.

## What needs YOU (David-gated)
1. **Finish the rclone own-client_id** (you were mid-flow in Google Console → project "KA Atlas").
   App name "Visual Tagger", your gmail as support email; then Credentials → OAuth client ID → Desktop
   app → put client_id/secret into the `gdrive` rclone remote → `rclone config reconnect gdrive:`.
   Then paste me: `rclone lsf gdrive:corpus_L6 -R --files-only | grep -c '\.png$'` — I'll reconcile it
   against the manifest and drive the idempotent backfill (200 rows still have no `gdrive_path`;
   161/530 currently on Drive).
2. **Confirm SUN397 collection is done** so I can commit the manifest (it grew 488→530 overnight — still
   running, so I held the commit). Niches still owed: nature_glass +17, materials +15 (Unsplash).
3. Optional: **connect Consensus / alphaXiv / Scholar Gateway** (I suggested them in the app) so future
   sessions pull primary sources directly.

## What shipped (6 commits on `cnfa-algs-2026-07-14`, ahead of `latest` — push is yours)
- `a0362d45` **S1/A5 M1′ tranche-1** — 13 image-only operators bound; audit coverage 15→28/68. Fully
  tested (determinism, tamper-caught, real annotate emits 13/13, checker replays 13/13).
- `35126878` **Panel findings** — 4 super-expert reviews (vision psychophysics / env-psych / psychometrics
  / verification) + ~40 primary citations. `docs/PANEL_FINDINGS_L6_2026-07-21.md`.
- `e954de13` **S3 2AFC labeling console** (`viz/labeling_console.html`, verified headless, 0 JS errors) +
  **corpus retrieval index** (`scripts/build_corpus_index.py` → browsable index.html; your explicit ask).
- `f88f992b` **Program revisions v2** — panel feedback folded into the sprint plan + implementation specs
  for the deferred engineering. `docs/L6_PROGRAM_REVISIONS_v2_2026-07-21.md`.
- `a619d0f3` **QA round-2 fixes** — a second adversarial panel reviewed *what I built tonight* and I
  fixed the findings: console gold-gate was gameable (now counterbalanced + all-correct), no worker/
  platform id capture, under-anchoring, no max-time; M1′ regression test was weak (now real
  field-mutation tamper on 2 fixtures) + `temperature_mismatch` digest made cross-env-order-invariant;
  index family-classifier mis-binned via substrings ("other" 196→32) + an HTML-injection hole closed.
  All re-verified. `docs/QA_ROUND2_FIXES_2026-07-21.md`.

**Panels ran twice** (as you asked — at intervals): round 1 reviewed the *plan* (reshaped it), round 2
adversarially reviewed *tonight's build* (caught the bugs above). Both cores were confirmed sound:
0 same-machine M1′ false REDs, perfect index join integrity, correct 2AFC/Bradley-Terry schema.

## Biggest things the panels caught (act on before the campaign)
- **Prospect** is coded as floor-depth P95 but the construct is **isovist openness**; **refuge is
  missing** → prospect-refuge can't validate as-is (CC-11).
- **Rating budget was inverted** (90% on between-worker Likert); **promotion rule had no CIs**. Both
  fixed in the revised design + the console (pairwise-dominant, mystery+refuge added, wayfinding dropped,
  PRS/Russell anchoring; promotion → CI-lower-bound + held-out + MTMM + FDR).
- **M1′ 6-decimal digest is a same-machine tamper control, not the cross-env guarantee the docstring
  claims** — spec'd the per-field tolerance schema fix (CC-9b). **#1 corpus confound = brightness** —
  audit `--gen-ab` for exposure leakage.
- **Penacchio-Wilkins faithful recipe recovered** (Mannos-Sakrison CSF etc.) — the reference cone is
  still an acquisition target (ViStA / Dryad).

## Deferred on purpose (specs in the revisions doc, not shipped under-verified)
M1′ tranche-2 (geometry/plan `plan_ref` bindings) + the cross-env tolerance schema touch the
audit-critical layer and need annotator changes + on-device verification — too risky to ship unattended.
Full implementation specs are in `docs/L6_PROGRAM_REVISIONS_v2_2026-07-21.md §4`.

## New task on the board
Corpus retrieval index — spec DONE + prototype DONE; next steps are the score-join (needs an annotate
pass over the stable corpus) and public thumbnails (needs the Drive backfill).
