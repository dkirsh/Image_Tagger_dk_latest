# SPRINT COMP-CORRECT — computationally correct algorithms for the full attribute collection
### Image_Tagger / CNfA · 2026-07-19 (Cowork) · builds on Codex's triage + deepened plan (2026-07-18)

*The goal of this sprint is not more operators — it is CORRECT operators. "Computationally correct" here
means three things, in order: (1) the math is the right math (the published measure or an honestly-named
proxy, never an invented formula wearing a citation), (2) the constants are the paper's constants or are
declared engineering choices locked by boundary tests, and (3) the operator abstains rather than fabricates
when its inputs are missing. Every stage ends with an external adversarial attack before the next begins —
that cadence is what caught F1–F8, the V9 split-brain, and the V7 hedonics licensing; it stays.*

**Scope** = the entire current collection: the 27 image-applicable built predicates, the 18 declared-input
plan predicates, the faithful V2/V6/V7 debt, the 19 Codex-kept Wave-1/2 candidates, the 5 detector-backed
Wave-3 keeps, and the street-noise acoustic operator (spec committed 2026-07-19). Rejected/merged/deferred
candidates from `CNFA_SECTION_D_TRIAGE_AND_IMAGE_REQUEST_CODEX_2026-07-18.md` are OUT and stay out.

**Algorithm hints below are graded:** `[FULL]` = the algorithm is specified here to implementation level;
`[SKETCH]` = the approach is right but constants/details must be pulled from the named source at build time;
`[PORT]` = do not derive — port the authors' released reference code and validate against it. A `[PORT]`
built from memory instead of the reference is a correctness failure by definition.

---

## 1. Sprint map

| Stage | Content | Exit gate |
|---|---|---|
| **S0** | M1′ wired into verify.py + audit classes for every EXISTING operator | verify.py rejects a stats-tampered record on a real image; all existing predicates emit `m1_prime` |
| **S1** | Faithful V6, V7, V2 (the reimplementation debt) | match reference implementation on fixtures OR documented decision to keep named proxy |
| **S2** | Wave-1 classical-CV candidates + street-noise operator build | each: pure-core test + negative control + smoke on real images + M1′ digest |
| **S3** | Wave-2 geometry candidates (AMBER ceiling) | same + explicit capture-quality abstentions (fisheye/wide-angle flags) |
| **S4** | Wave-3 detector-backed candidates (AMBER by rule) | pinned model + mask digest provenance + negative controls firing |
| **X** | After every stage: external attack (Codex/Fable) + disposition doc + commit | attack survived or findings fixed before next stage |

Corpus note: the Drive corpus (120 interiors + 80 A/B pairs minimum) gates CONSTRUCT validity, not this
sprint. This sprint gets every operator to *computationally correct + mechanically verified + honestly
tiered*. GREEN promotion is a separate, later act.

---

## 2. Stage S0 — M1′ everywhere (infrastructure first)

The pure core exists (`annotation_socket/m1_prime.py`, committed `7dcecdb5`, self-test proves
tamper-catch). S0 finishes the job:

**S0.1 Wire `replay_sufficient_stats` into `verify.py`** after M1 scalar replay, dispatching on
`extras.m1_prime.audit_class`. Verdict mapping (per Codex's table): stats-mismatch + scalar-match →
AMBER (legacy) or RED (any predicate claiming faithful V2/V6/V7/detector GREEN); scalar-mismatch → RED;
missing block → allowed-but-AMBER for legacy, RED for faithful claims. *Coordination: verify.py is a
modified file in the working tree — check the Mac copy is the newest before editing (the hedonics.py
lesson).*

**S0.2 Emit blocks from the two already-covered operators** — `brightness_variance` (luminance_field) and
`spectral_slope_deviation` (radial_fft).

**S0.3 New audit-class computers** (pure numpy, same emit/replay pattern), covering every remaining
existing operator:

- `orientation_hist` `[FULL]`: Sobel gx,gy → θ=atan2(gy,gx) mod π, magnitude-weighted 18-bin histogram
  over pixels with magnitude > τ (declare τ); emit edge_count, hist, and the entropy. Serves V13 + W1.9.
- `box_count` `[FULL]`: Canny (declared thresholds) → crop to largest dimensions divisible by the box
  series → counts for box sizes {2,4,8,…,min(H,W)/4} → emit the (size,count) series + fitted D + R². Serves
  fractal_dimension, V9.
- `color_palette` `[FULL]`: Lab conversion tag, k=8, `cv2.setRNGSeed(1234)`, kmeans attempts declared;
  canonicalize centers by sorting on (L,a,b); emit centers, proportions, entropy. Serves palette entropy,
  warmth (plus HSV warm/cool mask fraction).
- `luminance_field` extensions: glare (bright-mask fraction + top-hat energy), vertical-illuminance proxy
  (wall-mask mean), brightness — one class, per-operator param sets.
- `geometry_plan` `[SKETCH]`: grid_hash + upstream chain hashes already exist in plan_chain evidence;
  M1′ adds the derived-metric re-computation on the hashed grid (VGA integration vector digest, path-graph
  edge count). Serves C1–C4, C13, C24, C01, C29.

**S0.4 Boundary tests** for every rounding rule in `_canon` (the 6-decimal grid is itself a threshold —
lock it: a value differing at 1e-5 must produce a different digest; at 1e-7 the same).

---

## 3. Stage S1 — the faithful reimplementations (the debt with the highest adequacy value)

**S1.1 V6 subband entropy — Rosenholtz, Li & Nakano 2007** `[PORT]`
1. sRGB → CIELab (declare white point D65, the standard matrix).
2. Steerable pyramid on each channel, 3 scales × 4 orientations (Simoncelli construction, frequency-domain;
   a pure-numpy port is ~150 lines and deterministic).
3. Per subband: bin coefficients, Shannon entropy — **the binning rule and the luminance/chrominance
   pooling weights come from the authors' released MATLAB (`entropy.m`/`band_entropy.m` in the clutter
   toolbox). Do not invent them.**
4. Fixtures: blank < gradient < periodic texture < cluttered object field, PLUS numeric match to the
   reference implementation on ≥3 canonical images before the proxy name is dropped.
5. The existing `grayscale_gabor_entropy_proxy` stays registered under its proxy name until step 4 passes;
   then it is retired from scoring (kept in code for comparison), never silently aliased.

**S1.2 V7 feature congestion — Rosenholtz et al. 2005/2007** `[PORT]`
1. Gaussian pyramid; at each scale: (a) color clutter = volume of the local covariance ellipsoid of (a,b)
   under a Gaussian window; (b) contrast clutter = local variance of bandpassed luminance; (c) orientation
   clutter = covariance of oriented opponent-energy across 4 orientations.
2. Combine across scales, then across features, with **the toolbox's constants — the feature weights and
   Minkowski pooling exponent are exactly the thing an invented reimplementation gets wrong. Port them.**
3. Localization fixture (Codex's): a clean room with one dense shelf must light up the shelf only.
4. Same retirement protocol for `local_congestion_proxy` as V6. Note: V7 stays OUT of hedonics regardless
   (delicensed 2026-07-18; UNRESOLVED pending calibration — that decision is not reopened by this sprint).

**S1.3 V2 2-D spectral discomfort — Penacchio & Wilkins 2015** `[SKETCH]`, gated on calibration
1. HARD GATE: no declared FOV / pixels-per-degree → the faithful path ABSTAINS and only the AMBER radial
   proxy runs. Angular calibration cannot be defaulted — a defaulted FOV is a fabricated claim.
2. With calibration: linearized luminance (declare the sRGB EOTF assumption), Hann window, 2-D FFT
   amplitude — kept as the full 2-D distribution, NOT radially averaged.
3. Deviation-from-naturalness: residual of log-amplitude against the 1/f surface, weighted toward the
   psychophysically potent band (~3 cycles/degree — the paper's weighting, not a guess), integrated over
   the 2-D plane so oriented (stripe) energy is captured — this is precisely what the radial proxy misses.
4. Fixtures: square-wave gratings at 0.375–3 cpd must rank ≥ naturalistic images; checkerboards > blank;
   agreement with the paper's reported stimulus ordering.

---

## 4. Stage S2 — Wave-1 classical-CV candidates (+ street-noise build)

Each follows the §1 recipe of the construction spec (pure fn → registry `_spec` → derivation chokepoint →
tests → annotator binding → run_stage smoke). Hints:

**W1.1 `v2a_004 luminance_gradient_contrast`** `[FULL]` — Gaussian-blur luminance at σ = diag/64 (kills
texture, keeps lighting); emit (a) mean large-scale gradient magnitude, (b) gradient direction coherence
(resultant length of doubled angles, magnitude-weighted), (c) robust contrast ratio p95/p5 of the blurred
field. Abstain: global std < 2 DN. audit: luminance_field. Distinct from brightness_variance (that is
LOCAL 31-px texture; this is the room's light architecture).

**W1.2 `v2a_009 shadow_softness` (+ `daylight_hard`/`daylight_soft` as thresholded ends)** `[SKETCH]` —
1. Candidate shadow edges: Canny edges where chromaticity is stable across the edge (|Δ(R/G)|, |Δ(B/G)|
   small) but luminance ratio is large — the classic illumination-vs-material edge test.
2. At each candidate, sample the luminance profile along the gradient normal (±15 px); fit an erf/sigmoid;
   penumbra width w = the 10–90% transition distance.
3. softness = median(w)/diag; hard flag if median(w) < w_hard AND shadow contrast > c_min; soft flag at the
   other end. Abstain below N=25 accepted shadow edges.
4. Negative control: a painted dark stripe (material edge) must be excluded by the chromaticity test.
   One operator, three registry outputs. AMBER (illumination/material separation is heuristic).

**W1.3 `v2a_014 natural_light_patterns` (sun patches)** `[SKETCH]` — connected components of luminance >
p92 whose interior chromaticity is warmer than their immediate surround (Δ(B/R) test) and whose boundary is
polygon-like: fit dominant Hough segments to the component boundary, straightness = inlier fraction. Score
= Σ area × straightness × warmth-contrast. Cannot prove sun — method string says "sun-patch GEOMETRY
candidate"; AMBER.

**W1.4 `v2a_011 evening_daytime_ambience`** `[FULL]` — CCT proxy of the bright quantile: mean chromaticity
(x,y) of pixels in luminance p60–p95 (excluding clipped) → McCamy: n=(x−0.3320)/(0.1858−y),
CCT = 449n³+3525n²+6823.3n+5520.33. Ambience = f(CCT proxy, mean luminance, luminance skew): evening =
warm (<3500K) + dim + high positive skew (pools of light). Declared confound: white balance — emit the
clipped-pixel fraction and flag `awb_unknown`. AMBER.

**W1.5 `v2a_015 temperature_mismatch`** `[FULL]` — seeded k-means (k=3) on chromaticity of adequately
bright pixels; per-cluster CCT via McCamy; mismatch = max pairwise |Δmired| (mired = 1e6/CCT — use mired,
not kelvin: perceptually even) × min(cluster fractions)·2 (a 2% stray cluster ≠ a mismatch). Abstain:
mean saturation < s_min. AMBER (same AWB confound).

**W1.6 `v2a_013 spotlight_pool_geometry`** `[FULL for geometry, claim deferred]` — morphological top-hat
(disk r=diag/40) on luminance → bright-pool components; emit pool count, area fractions, elongation,
centroid field. The SOCIAL-exposure claim requires seat/person regions → that part is a compound in Wave 3;
Wave 1 ships the honest geometric substrate only.

**W1.7 `v2a_081 dark_zone_map`** `[FULL for field, safety claim deferred]` — blurred luminance < 0.25 ×
global median → connected dark components; emit area fraction, darkest-component depth (median deficit),
adjacency-to-boundary flag. Named `dark_zone_map`, not "safety" — the safety construct needs geometry
(Wave 2 corner localization) + corpus.

**W1.8 `v2a_088 texture_density`** `[FULL]` — fine-scale range filter (5×5 local max−min) on luminance;
mask OUT the dilated Canny long-edge set (structure ≠ texture); density = mean of the masked response,
plus a field. Distinct from V6/V7 by construction (micro-texture after structure removal). Negative
control: JPEG noise at q<50 must be flagged via the existing bytes/pixel artifact check. audit:
texture_stats (new class, S0 pattern).

**W1.9 `v2a_094 orderliness_alignment`** `[FULL]` — cv2 LSD (deterministic, declared params) → segments;
length-weighted orientation histogram folded to [0,π); orderliness = 1 − H(hist)/H_max; alignment = the
fraction of total segment length within ±5° of the two dominant modes. Emit orientation_hist M1′. Abstain
below 20 segments. This is the orderly-vs-chaotic lines construct; V13 (edge-pixel entropy) stays separate
— pixels vs segments measure different scales of order.

**W1.10 `street_noise_intrusion` + `noise_masking_privacy`** `[FULL — prototyped 2026-07-19]` — port
`street_noise_prototype.py` into `cnfa_algs/street_noise.py` per the committed spec: facade transmission
(Leq_out − R′), area-weighted Sabine floor, LOS-blocked direct sum, privacy = 1 − STI(speech@2.5m − noise),
within_ok comfort ramp at 50 dBA, huddle = product. ABSTAIN on missing Leq_out/R′, never default. Ordering
invariants + the inverted-U as a test (best-huddle noise strictly between quietest and loudest). AMBER.

---

## 5. Stage S3 — Wave-2 geometry candidates (AMBER ceiling by rule)

All ride vanishing-point / plane-segmentation / inferred-plan machinery → AMBER, and all must ABSTAIN on
declared capture-quality flags (fisheye, panorama, extreme wide-angle — Codex's boundary images).

**W2.1 `v2a_080 verticality_cues`** `[FULL]` — from W1.9's segments: vertical VP via RANSAC-free grid
search over VP candidates on the unit sphere (deterministic); verticality = length fraction of segments
consistent with the vertical VP × their mean angular extent (long continuous verticals count more).
Build FIRST in S3 — it is the simplest and its VP machinery feeds W2.2/W2.3.

**W2.2 `v2a_067 ceiling_height_openness`** `[SKETCH]` — Manhattan frame from 3 VPs; wall-ceiling boundary
via the plane-seg pipeline; report the RELATIVE quantities only: visible ceiling angular elevation above
horizon, ceiling area fraction after rectification, floor-to-ceiling angular span. NO meters without a
scale anchor (that is W2.7). Honest name: `ceiling_openness_relative`.

**W2.3 `arch.pattern.double_height_space`** `[SKETCH]` — thresholded flag on W2.2's angular span ratio
(calibrate the threshold on the POE high-vs-low-ceiling pair + Drive atria when they arrive; until then
emit the continuous value, flag NEEDS-CALIBRATION).

**W2.4 `v2a_072 blind_corner_index`** `[SKETCH]` — on the inferred PlanGrid (C1–C4 substrate): walk the
circulation skeleton; at each junction compute isovist area before vs after the turn; blind-corner score =
Σ max(0, ΔA/A − τ) over junctions with no transparency evidence on the occluding plane. Reuses existing
VGA/isovist code; new logic is only the junction walk.

**W2.5 `v2a_077 barrier_permeability`** `[SKETCH]` — per detected partition plane: visual permeability =
see-through fraction (aperture + glass area over plane area; glass evidence = behind-plane content
visible with plane-consistent specular sheen — heuristic, declared); physical permeability = gap fraction
at circulation height. Emit both, never average them.

**W2.6 `v2a_118 choice_richness_zones`** `[FULL]` — extend C13: Shannon evenness over the areas of
distinct setting types visible/reachable in the unit (types from the existing setting classifier);
richness = evenness × type count / max_types. Pure reuse.

**W2.7 `v2a_068 room_scale_estimate`** `[SKETCH, straddles Wave 3]` — needs a known-size anchor: door
leaf (2.03 m), seat height (0.43–0.46 m) from the Wave-3 detector; scale = median over anchors; ABSTAIN
if anchor disagreement > 20% or zero anchors. Until the detector lands this operator is dormant — build
the scaffold, register it as abstaining.

**W2.8 `arch.pattern.threshold_emphasized`** `[SKETCH]` — rectangular aperture in a wall plane +
material/luminance change across it + frame edges (parallel segment pairs bounding the aperture);
emphasis = frame contrast × relative aperture height. Defer if plane-seg quality on doorways proves poor
in smoke tests — this one is allowed to die in S3 if the substrate can't carry it.

---

## 6. Stage S4 — Wave-3 detector-backed (AMBER by rule 3, provenance-first)

One frozen, pinned segmentation model serves all five (candidate: an ADE20K-trained model exported to
ONNX, eval-mode, fixed input size, version hash in every record — the model choice is a logged DECISION
with Codex review before download). M1′ = `segmentation_mask` class: model id + class-map digest +
confidence quantiles; nondeterministic or unavailable model → provenance-replay only, AMBER capped,
fail-closed on missing confidence.

- **W3.1 `v2a_096 visible_vegetation`** `[FULL given model]` — plant/tree/flower class fraction +
  dispersion (patch count, largest-patch fraction). Negative control (must pass before shipping): green
  wall paint and a green painting must NOT fire; a photo of a plant IS allowed to fire (declared limit).
- **W3.2 `v2a_097 window_view_content`** `[FULL given model]` — window mask ∩ (sky/greenery/built/water)
  class fractions within the window. Negative control: an indoor plant visible NEAR a window must not
  count as view greenery (mask intersection, not proximity).
- **W3.3 `v2a_099 blue_space_view`** — water∪sky-over-water within window mask; ships with W3.2, no
  separate machinery.
- **W3.4 `v2a_106 sociopetal_seating_detected`** `[SKETCH]` — seat instances + facing normals (backrest
  vs seat-front geometry from the instance mask's principal axes — heuristic, declared); feed the EXISTING
  `sociopetal_seating()` function; emit detector provenance. The pure function is already built and tested;
  only the seat-source changes from declared-input to detected.
- **W3.5 `arch.pattern.corner_window`** `[FULL given model + planes]` — window masks intersecting two
  adjacent wall planes that meet at a detected corner within a gap tolerance.

---

## 7. Cross-cutting: what every operator ships with (unchanged, restated as the checklist)

1. Pure core + unit tests RUN (never shipped untested — Verification Discipline rule 1).
2. Negative control that MUST abstain/reject; boundary test for every new constant.
3. `m1_prime` block with the right audit_class (S0 makes this mechanical).
4. Registry `_spec` with honest tier + proxy-naming in BOTH method string and registry note.
5. run_stage smoke on the 7-image set (Codex's smoke list) — SCORED-or-ABSTAINED, no UNKNOWN, ×3 determinism.
6. A row in the decisions log for every chosen constant (risk level + panelist concern).
7. NEVER summed into hedonics/aggregate without an explicit licensing decision (the V7 lesson).

## 8. Ordering rationale + effort estimate

S0 first because it converts "trust me" into "check me" for everything that follows — every S1–S4 operator
then lands with its audit trail on day one. S1 before S2 because the clutter family is central (three
consumers) and its proxy status caps the most claims. Street-noise rides in S2 because its core is already
prototyped and verified. S3 waits for S2's segment/VP machinery (W1.9 feeds W2.1–W2.3). S4 last because
model selection deserves its own attacked decision, not a rushed download.

Rough shape (working sessions, not promises): S0 ≈ 1–2, S1 ≈ 2–3 (V6+V7 port heavy), S2 ≈ 2, S3 ≈ 2,
S4 ≈ 1–2 + model-decision review. Attack passes between each.

## 9. Commit cadence (per stage, copyable)

```bash
cd /Users/davidusa/REPOS/Image_Tagger_dk_latest
# stage-scoped add ONLY — never git add -A in this tree
git add annotation_socket/m1_prime.py annotation_socket/verify.py \
        annotation_socket/tests/ cnfa_algs/ docs/SPRINT_COMPCORRECT_ALGORITHMS_2026-07-19.md
git commit -m "Sprint COMP-CORRECT stage <N>: <content> (tests run, M1' emitted)"
git push origin cnfa-algs-2026-07-14
```

## 10. Open decisions for the log (need David or panel input, non-blocking to S0–S1)

| Q | Question | Options |
|---|---|---|
| Q1 | Which segmentation model for Wave 3? | ADE20K SegFormer-B0 (small, ONNX-clean) vs B2 (better masks, heavier) — logged decision + Codex review before download |
| Q2 | Does V2-faithful get a DECLARED default viewing condition (e.g., "50° FOV typical phone photo") as a *named assumption*, or hard-abstain without EXIF? | hard-abstain (pure) vs declared-assumption tier (more coverage, weaker claim) |
| Q3 | Retire proxies after faithful V6/V7 land, or run both for one corpus cycle to measure divergence? | retire (clean) vs parallel run (evidence about how wrong the proxies were — recommend this) |
