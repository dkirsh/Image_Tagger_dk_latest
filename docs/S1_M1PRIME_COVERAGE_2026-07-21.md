# S1 / A5 — M1′ coverage batch 1: the 13 image-only pixel operators (2026-07-21, Cowork/Opus)

**What:** added M1′ sufficient-statistic bindings for the 13 registry predicates that are pure
single-argument image operators (`fn(img) -> AttributeResult`), via the existing generic
`operator_extract` audit class. **M1′ coverage 15 → 28 of 68 predicates.** No annotator change: the
emit loop (`annotator.py` ~L397) already emits for any predicate in `M1P_BINDINGS`, and verify's
checker already replays it — this batch is two table extensions in `annotation_socket/m1_prime.py`
(`_OPX` + `M1P_BINDINGS`) plus a test update.

## Predicates bound
`glare-risk`, `cnfa.cognitive.landmark_salience`, `cnfa.fluency.proto_object_count`,
`cnfa.fluency.multiscale_gradient`, `cnfa.fluency.multiscale_unique_color`,
`cnfa.light.luminance_gradient_contrast`, `cnfa.light.sun_patch_geometry`,
`cnfa.light.evening_ambience`, `cnfa.light.temperature_mismatch`,
`cnfa.light.spotlight_pool_geometry`, `cnfa.light.dark_zone_map`,
`cnfa.geometry.orderliness_alignment`, `cnfa.geometry.verticality_cues`.

Digest keys = each op's declared numeric pre-scalar signature + fixed constants; variable-length
detail lists (patches / pools / zones) are deliberately excluded so the digest is cross-env stable.
`glare-risk` and `landmark_salience` carry no extras → scalar-only digest (still tamper/stale/
abstain-auditable).

## What was verified (data-driven, through the REAL code path)
- **Determinism** (the anti-false-RED guarantee): every op's digest is identical on two emits — no
  LSD / mean-shift / k-means nondeterminism leaks in. This was the gating check: an op whose digest
  jittered would flag genuine records RED, so only deterministic ops were bound.
- **Genuine → MATCH; forged-digest tamper → STATS_MISMATCH** for all 13.
- **Diff-image discrimination:** on the synth fixture, 14 discriminate; 2 abstain (LSD ops, no
  segments on synth); 4 are globally roll-invariant (`sun_patch`, `evening_ambience`,
  `spotlight_pool`, `dark_zone` — whole-frame light summaries whose stats *and scalar* are invariant
  to a circular roll). The 4 are documented on an allowlist (`_M1P_ROLL_INVARIANT`) so the diff-image
  guard stays strict for every spatially-discriminating op. This is within M1′'s stated boundary
  (tamper / stale / wrong-pipeline), not a signature weakness.
- **End-to-end:** a real `annotate_image` run emits 13/13 valid M1′ blocks (SCORED); the checker
  replays 13/13 → MATCH and catches 13/13 tampered blocks.
- **Full `test_m1_prime.py` green** (28 bindings; the stale `test_cc2_operator_extract` count assert
  of "7" was replaced by `test_operator_extract_bindings`, which dynamically covers all 20
  operator_extract+ssim bindings and pins the 13 new ids explicitly so a dropped binding fails).
  All other `annotation_socket/tests/*` green (the one unrelated failure is `test_cc3_layout_inputs`
  → `ModuleNotFoundError: cpp`, a sandbox-path artifact, resolved for the smoke via a symlink).

## Boundary (unchanged, restated)
`operator_extract` digests the operator's own pre-scalar signature: it catches TAMPERED, STALE, and
WRONG-PIPELINE scores. It does NOT catch an algorithmic bug (producer and checker share the operator
code) — that stays the adversarial (Codex / panel) layer's job.

## Remaining M1′ gap (40 uncovered → next batches)
- **9 geometry-chain ops** (`enclosure_index`, `prospect`, `ceiling_openness_relative`,
  `double_height_space`, `blind_corner_index`, `barrier_permeability`, `threshold_emphasized`,
  `vertical_illuminance_proxy`, `acoustic_absorption`): take `planes`/`Z`/`pg`, so they ride the same
  substrate the single `geometry_plan` audit (bound to `C1`) already digests. Decision needed: share
  the substrate audit vs. add a lightweight per-metric digest of each op's own plan-read.
- **~8 plan_metric `req=['plan']`** (C2/C3/C4/C13/C24/C01/C29, `choice_richness`) — same substrate
  question.
- **17 value-input layout criteria** (C5–C23, `street_noise_intrusion`, C8/C16/C17/C18): these are
  the CC-3 declared-input VALUE-bundle predicates; their sufficient statistic is (declared inputs →
  deterministic reduction), so their M1′ needs input fixtures, not just pixels.
- **4 not-simple callables:** `warm_vs_cool_ratio` (bundle key `warmth`), `fractal_mid_d_band`
  (shares the `box_count` substrate already bound to `fractal_dimension`), and the two proxies
  (`grayscale_gabor_entropy_proxy` / `local_congestion_proxy`, retirement-pending under DEC-3/CC-6).
