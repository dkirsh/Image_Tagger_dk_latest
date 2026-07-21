# QA round 2 — adversarial review of tonight's build + fixes applied (2026-07-21, Cowork/Opus)

Two critical QA reviewers adversarially reviewed what was built this session (the 2AFC console, the
S1/A5 M1′ batch, the corpus index). Both confirmed the cores are sound — **0 same-machine M1′ false
REDs, perfect index join integrity, correct BT/tie schema + gold-through-flip grading** — and found
fixable issues. The high/medium ones are **fixed and re-verified** below; the rest are logged.

## Fixed + re-verified this session
**Labeling console (`viz/labeling_console.html`)** — re-verified headless (correct→rating,
wrong→rejected, PROLIFIC_PID captured, new columns present, 0 JS errors):
- **H1 gameable gold gate** → qual trials now **counterbalance display (random flip)**, grade through
  the flip, and require **all golds correct** (identical-image "can't tell" catch mandatory). An
  always-one-side clicker no longer passes.
- **H3 no worker/platform identity** → reads `PROLIFIC_PID` / `participant_id` / `STUDY_ID` / `platform`
  from the URL; real participant id becomes `worker_id` (needed for cluster-bootstrap over workers +
  platform-as-covariate). New CSV columns: `platform, study_id, display_flip, fast_attempts, too_slow`.
- **H4 under-anchoring** → each construct's **definition is shown persistently** during rating
  (highlighted on first appearance) — mystery/refuge/restorative no longer judged cold.
- **H2 no max-time / dropped fast clicks** → sub-min-time clicks are **counted** (`fast_attempts`), a
  `too_slow` flag is recorded; `maxMs` now used.
- **M1 deterministic counterbalancing** → randomized **per trial** (was index-parity, confounded with
  order); `display_flip` recorded; golds excluded from the side-bias metric.
- **M4** → clicking a photo now registers the choice (handlers wired to `.opt`).

**M1′ (`annotation_socket/m1_prime.py` + test)** — suite re-run green:
- **A1 weak regression guard** → `test_operator_extract_bindings` now does a **real field-mutation
  tamper** (perturb a stats value + re-forge the digest → must be `STATS_MISMATCH`), on **two fixtures**
  (synth + a line-structured image). Proves the per-key pre-scalar signature is load-bearing, not just
  the digest string (18/20 ops exercise a real numeric field).
- **A2 LSD ops never scored under test** → added a line fixture so `orderliness_alignment` /
  `verticality_cues` **SCORE** (don't abstain) and their `n_segments`/alignment signature is tamper-tested.
- **A3 `temperature_mismatch` cross-env-fragile** → k-means clusters were emitted in **label order**
  (BLAS/PP-init-dependent) with integer-K CCT. Now **sorted by CCT + coarsened to 50 K** (proportions
  co-reordered, worst-pair sorted) → order-invariant digest, same tamper power.

**Corpus index (`scripts/build_corpus_index.py`)** — re-run:
- **B1 family mis-classification** → `arch_type` is space-normalized; `family_of` does exact-then-
  **token-boundary** matching (so `coffee_shop` no longer → retail via "shop"); added
  conference_center/computer_room/dinette. **"other" dropped 196 → 32.**
- **B2 HTML/JS injection** → the embedded JSON now escapes `< > &` (a `</script>` in a note/filename
  can't break out).
- **B3 placeholder clobber** → single-pass substitution.
- **B4 pair-variant pollution** → curated A/B images map to `arch_type="(pair variant)"` /
  `space_family="pairs"` (164 rows no longer masquerade as room classes).

## Logged, not yet done (console pilot-hardening — deferred, low urgency: needs Drive+Prolific first)
- Preload both images + reveal simultaneously + prefetch n+1 (RT/latency-bias hygiene for real images).
- Add PRS extent/compatibility Likert items; consider restoring fascination as a comparative construct.
- ~5% within-worker repeat pairs (intra-rater reliability); anti-automation (copy-paste disable, UA
  fingerprint); hide confidence toggle on anchor screens; CSV meta as sidecar (not a `#` line).
- Gold answers currently readable via a flag-guarded `window.__correct` test seam — remove/gate for a
  real study (don't expose gold answers in the DOM).
- Index long tail: ~32 SUN one-word classes still "other"; A4 pre-existing tiny-image raises in
  feature_congestion/subband_entropy (unreachable at corpus resolutions).
