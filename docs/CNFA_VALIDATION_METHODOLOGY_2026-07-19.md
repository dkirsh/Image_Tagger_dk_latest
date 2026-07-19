# CNfA VALIDATION METHODOLOGY — how every attribute earns (and keeps) its number
### Image_Tagger / CNfA · 2026-07-19 (Cowork/Fable) · companion to SPRINT_COMPCORRECT_ALGORITHMS_2026-07-19
### Status: S0 + S2 BUILT AND RUN this session; this doc records both the methodology and what already passes

*Extends Codex's `CNFA_TESTING_PLAN_2026-07-18.md`. The change since that plan: **M1′ is no longer a
TODO** — it is implemented (`annotation_socket/m1_prime.py`) and wired (annotator emits, verify.py
replays), so every row Codex marked "BLOCKED until M1' implemented" for the five covered audit classes
is now unblocked and RUN. This doc gives the validation ladder every operator climbs, the per-operator
test matrix as it stands TONIGHT, and the exact protocol for the stages that remain.*

---

## 1. The validation ladder (six rungs; an operator's tier = the highest rung it has PASSED)

| Rung | Question it answers | Mechanism | Cost |
|---|---|---|---|
| **L1 pure-core** | Does the math do what the docstring says on inputs with known answers? | synthetic fixtures with analytic/ordering ground truth, run in-module (`python3 -m cnfa_algs.<mod>`) | minutes |
| **L2 negative control** | Does it REFUSE degenerate/fabricated input rather than emit a number? | blank/saturated/grayscale/missing-input fixtures asserting `scalar is None` or ABSTAINED/UNKNOWN | minutes |
| **L3 boundary** | Are the constants locked so a silent change is caught? | one test per declared threshold straddling it (the `test_f7_ridge_boundary.py` pattern) | minutes |
| **L4 replay (M1+M1′)** | Is the number reproducible AND produced by the claimed METHOD? | verify.py: scalar replay + sufficient-statistic digest replay from image bytes | automatic per unit |
| **L5 cross-environment** | Same bytes, same digest on Mac and sandbox? | run the M1′ emit on both machines over ≥5 byte-identical images; compare digests (the canonical 6-decimal rounding grid is designed to absorb BLAS jitter) | one session |
| **L6 construct** | Does the number track the human/architectural outcome? | labeled corpus: global labels + A-vs-B region pairs; report false-pos/false-neg RATES, not examples | corpus-blocked |

**Tier rule:** L1–L4 passed → honest AMBER. GREEN requires L5 + L6 + no proxy in the method chain.
Nothing in tonight's build claims GREEN.

## 2. What was RUN tonight (evidence, not intention)

- **M1′ (S0):** 5 audit classes (`luminance_field`, `radial_fft`, `orientation_hist`, `box_count`,
  `color_palette`), each proven: genuine→MATCH; tampered statistic **with re-forged digest**→caught;
  different image→caught; stats-ok/scalar-off→RED; blank→abstained-stats still replayable. The
  `_canon` rounding boundary is itself boundary-tested (1e-5 distinguishes, 1e-7 collapses).
  Wired end-to-end: annotator emits on 5 predicates; verify.py REDs a stats-tampered real record and
  demotes missing blocks to AMBER. Test file: `annotation_socket/tests/test_m1_prime.py` (PASSES).
- **Wave-1 (S2):** 9 operators in `cnfa_algs/wave1_ops.py`, L1+L2 fixtures ALL PASS, determinism ×2,
  9-interior real-image smoke with **zero errors and zero saturated operators** after calibration
  (spreads 0.14–1.00). Registered in the socket (registry + annotator): full `run_stage` now scores
  **36/36 applicable** with the negative control still RED and idempotency intact; all 6 suite files pass.
- **Street-noise:** `cnfa_algs/street_noise.py` (ports the verified prototype). L1 invariants PASS:
  +Leq raises every cell; +R′ lowers every cell; a screen strictly shields; the inverted-U holds
  (best-huddle noise strictly between quietest and loudest; huddle(best) > huddle(quietest));
  missing Leq/R′ → ABSTAINED naming both; determinism ×3 exact. Registered (abstains on image-only units).
- **Fixture-caught bugs tonight** (why L1 exists): Canny-based penumbra sampling had a survivorship
  bias against soft shadows; the candidate-blur contaminated width measurement; the McCamy CCT
  denominator was sign-flipped (warm/cool inverted); the top-hat element was smaller than the pools
  it had to keep; a percentile threshold swallowed patches larger than (100−pctl)% of the frame.
  Every one was caught by a fixture BEFORE any real image was scored.
- **Also fixed:** the V7 hedonics delicensing had silently regressed on the Mac (yesterday's device
  write pushed the unfixed copy; verification had happened only in the sandbox). Re-fixed and this
  time sealed in git (`66d6ec1e`). Methodology lesson → L5 exists precisely for verified-here-not-there.

## 3. Per-operator matrix (current state; ✔=RUN+PASS tonight or previously, ◐=partial, ✗=not yet, — =N/A)

### 3a. Pixel operators (image_attr)
| Operator | L1 | L2 | L3 | L4 M1 | L4 M1′ | L5 | L6 |
|---|---|---|---|---|---|---|---|
| brightness_variance | ✔ | ◐ | ✗ | ✔ | ✔ emitted+replayed | ✗ | ✗ |
| edge_clarity_mean | ✔ | ✔ | ✗ | ✔ | ✗ (audit class TBD: edge_stats) | ✗ | ✗ |
| symmetry_score_horizontal | ✔ | ✔ | ✗ | ✔ | ✗ (ssim_map) | ✗ | ✗ |
| color_palette_entropy | ✔ | ✔ | ✗ | ✔ | ✔ | ✗ | ✗ |
| processing_load_proxy | ✔ | ◐ | ✗ | ✔ | ✗ (jpeg_tiles) | ✗ | ✗ |
| fractal_dimension | ✔ | ◐ | ✗ | ✔ | ✔ (box_count) | ✗ | ✗ |
| fractal_mid_d_band V9 | ✔ | ✔ | ✔ | ✔ | ✔ (reads box_count) | ✗ | ✗ |
| spectral_slope_deviation V2-proxy | ✔ | ◐ | ✗ | ✔ | ✔ (radial_fft) | ✗ | blocked: faithful V2 |
| edge_orientation_entropy V13 | ✔ | ✔ (F1) | ✗ | ✔ | ✔ (orientation_hist) | ✗ | ✗ |
| contour_angularity V1 | ✔ | ✔ | ✗ | ✔ | ✗ (contour_stats) | ✗ | ✗ |
| gabor_entropy_proxy V6-proxy | ✔ | ✔ | ✗ | ✔ | ✗ → S1 replaces | ✗ | blocked: faithful V6 |
| local_congestion_proxy V7-proxy | ✔ | ✔ | ✔ (F7 suite) | ✔ | ✗ → S1 replaces | ✗ | blocked: faithful V7 |
| glare-risk, warmth, landmark_salience | ✔ | ◐ | ✗ | ✔ | ✗ (luminance_field ext.) | ✗ | ✗ |
| enclosure/prospect/acoustic-proxy/vert-illum | ✔ | ✔ | ✗ | ✔ | ✗ (geometry_plan) | ✗ | ✗ |
| **W1.1 luminance_gradient_contrast** | ✔ | ✔ | ✗ | ✔ | ✗ (luminance_field ext.) | ✗ | ✗ |
| **W1.2 shadow_softness (+hard/soft)** | ✔ | ✔ | ◐ (px-floor declared) | ✔ | ✗ (penumbra_stats) | ✗ | ✗ |
| **W1.3 sun_patch_geometry** | ✔ | ✔ | ✗ | ✔ | ✗ | ✗ | ✗ |
| **W1.4 evening_ambience** | ✔ | ✔ | ✗ | ✔ | ✗ (color_palette ext.) | ✗ | ✗ |
| **W1.5 temperature_mismatch** | ✔ | ✔ | ✗ | ✔ | ✗ | ✗ | ✗ |
| **W1.6 spotlight_pool_geometry** | ✔ | ✔ | ✗ | ✔ | ✗ | ✗ | — (claim deferred) |
| **W1.7 dark_zone_map** | ✔ | ✔ | ✗ | ✔ | ✗ | ✗ | — (claim deferred) |
| **W1.8 texture_density** | ✔ | ✔ (edge-saturated abstains) | ✗ | ✔ | ✗ (texture_stats) | ✗ | ✗ |
| **W1.9 orderliness_alignment** | ✔ | ✔ | ✗ | ✔ | ✗ (orientation_hist ext.) | ✗ | ✗ |

### 3b. Plan/compound operators — unchanged from Codex's plan (C1–C24 ✔ L1/L2, blocked at L6 on
plan/depth ground truth; C01/C29 ✔ L1–L3 incl. the F7 boundary suite) — plus:
| Operator | L1 | L2 | L3 | L4 | L5 | L6 |
|---|---|---|---|---|---|---|
| **street_noise_intrusion** | ✔ 4 invariants | ✔ names missing inputs | ◐ (constants declared, tests owed) | ✗ (m1p: facade vector + L_rev + cell triple) | ✗ | corpus + measured-SPL comparison |

## 4. Protocols for what remains (the exact recipes)

**P1 — M1′ audit classes still owed** (edge_stats, ssim_map, jpeg_tiles, contour_stats, penumbra_stats,
texture_stats, geometry_plan, and extensions of luminance_field/orientation_hist/color_palette for the
operators marked "ext."): follow the S0 pattern exactly — mirror the producer's parameters into a pure
`stats_<class>()`, register in `AUDIT_CLASSES` + `M1P_BINDINGS`, extend `test_m1_prime.py`'s loop (it
iterates ALL registered classes automatically), and prove tamper-catch before commit. `geometry_plan`
is the highest-value one: digest of (grid_hash, VGA integration vector, path-graph edge count).

**P2 — faithful V6/V7 ([PORT] — the no-fake rule).** Obtain the Rosenholtz lab clutter toolbox
(MATLAB). Port; then the acceptance test is NUMERIC AGREEMENT with the reference on ≥3 canonical
images (tolerance declared per-stat), plus the ordering fixture (blank < gradient < periodic <
cluttered) and the localization fixture (clean room + one dense shelf → shelf lights up). Until the
reference run exists, the proxies KEEP their proxy names — a "faithful" module written from memory is
a correctness failure by definition and does not ship. If the toolbox cannot be obtained, the
documented decision is keep-proxy-permanently (allowed by the sprint).

**P3 — faithful V2.** Hard gate: no declared FOV/pixels-per-degree → faithful path ABSTAINS (the
AMBER radial proxy still runs). Acceptance: gratings 0.375–3 cpd rank ≥ naturalistic; checkerboard >
blank; stimulus ordering from Penacchio & Wilkins 2015 reproduced. The 2-D (not radially averaged)
energy distribution must be the M1′ statistic (`fft_2d`).

**P4 — cross-environment replay (L5).** One script, run on both machines over the 7-image smoke set:
emit M1′ for every bound predicate, write digests to JSON, diff. Any digest mismatch = a genuine
environment sensitivity that must be fixed (coarser canonical rounding for that stat) BEFORE any GREEN
conversation. This directly prevents the hedonics-regression class of error (§2, last bullet).

**P5 — construct validation (L6, corpus-blocked).** Per Codex's corpus schema (image table + region-pair
table + minimum labels). Per attribute: ≥30 labeled interiors, ≥30 A-vs-B pairs (for localizing
operators), ≥10 negative controls, ≥5 replay images. Analysis: rank correlation (global labels) or
pairwise accuracy (A-vs-B) with CIs; report FP/FN rates. Passing does NOT flip AMBER→GREEN by itself —
it removes the L6 block; L5 and no-proxy must also hold. Wave-1 constants calibrated tonight on the
9-interior smoke (W1.1 fullscale=60, W1.2 ramp=0.045, W1.6 per-pool cap=2% + soft-sat) are declared
ENGINEERING calibrations and must be re-fit on the corpus (they shape scores, not orderings).

**P6 — external attack cadence.** After each stage: package changed files + this matrix, hand to
Codex/Fable with the standing instruction ("attack adequacy, not just determinism"), fix everything,
publish a disposition doc. S0+S2 (tonight's batch) is now DUE for its attack pass.

## 5. Honest boundary of tonight's verification

Verified: everything in §2, in the sandbox, with the suite passing and run_stage idempotent ×2.
NOT verified: Mac-side execution of tonight's code (committed but not run there — L5 explicitly owed);
any construct claim; M1′ for the operators marked ✗ in §3; the Wave-1 calibration constants beyond the
9 smoke interiors. The street-noise operator's plan-input binding path (run_stage with declared
`outdoor_leq`/`facade_spec` inputs) has its pure core tested but no full-socket fixture yet.
