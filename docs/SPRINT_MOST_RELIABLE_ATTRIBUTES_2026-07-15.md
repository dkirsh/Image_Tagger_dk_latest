# SPRINT PLAN — the MOST RELIABLE attributes
### Image_Tagger CNfA · Sprint "Reliable-A" · drafted 2026-07-15

## 0. The honest framing (why this sprint is NOT the compounds)

Two different questions have two different answers:
- **Highest social VALUE** → the compounds (C01 triangulation, C04 huddle, C29 stranded …).
  But **all 46 compounds are AMBER** — they ride the heuristic inferred plan + cross-tier
  registration, so they can never self-certify and always await the ≠-mind.
- **Highest RELIABILITY** → the **8 GREEN Tier-A primitives**: pure-image, deterministic
  (exact-replay), no plan/registration dependency, settled literature. These can **earn GREEN
  verdicts** in the socket today. **This sprint builds those.** C01/C29 are already built (AMBER)
  and get a separate *reliability-raising* workstream (§5), not a rebuild.

**Reliability = construct-confidence × GREEN-ceiling × deterministic-exact-replay ×
no-inferred-plan-dependency.** By that measure, ranked (committee rank in parens):

| Rank | Attribute | Code | Evidence anchor | Effort | Why reliable |
|---|---|---|---|---|---|
| 1 | **V9 fractal_mid_d_band_score** (8.3) | SHARED | Spehar/Taylor 2003; Hagerhall 2004 | **XS** | response kernel over the *existing* fractal_dimension output — almost no new code |
| 2 | **V2 spectral_discomfort_deviation** (9.2) | WB | Penacchio & Wilkins 2015 (a published *computational model*) | S | pure FFT/numpy; author sandbox-verified slope recovery; best-evidenced discomfort mechanism we lack |
| 3 | **V13 edge_orientation_entropy** (7.8) | SHARED | Grebenkina et al. 2018 (Redies lab) | S | deterministic Sobel orientation-histogram entropy; no segmentation |
| 4 | **V1 contour_angularity_index** (9.5) | SHARED | Bar & Neta 2006; Vartanian 2013 | M | 4-seat convergence; biggest missing valence signal; classical CV (Canny+turning-angle) |
| 5 | **V6+V7 Rosenholtz clutter pair** (8.5) | SHARED/COG | Rosenholtz 2005/2007 (field standard) | M | validated measures — but must **cross-calibrate & retire the legacy tiled proxy** (no double clutter) |
| — | *V10 landmark_differentiation, V17 popout_margin* | COG | Lynch 1960; Rosenholtz 1999 | — | **stretch** — GREEN only if the upstream saliency module is classical; verify first |

## 1. Sprint goal & scope

**Goal:** land **V9, V2, V13, V1** as GREEN, exact-replay socket predicates that pass the fail-
closed gate at GREEN (not AMBER), each grounded and correctness-panel-checked; plus the **V6/V7
clutter consolidation** (ship the validated measure, retire the ad-hoc one). Stretch: V10/V17.

**Out of scope:** rebuilding C01/C29 (done); anything needing the inferred plan (that's the AMBER
track). **Definition of the sprint's success:** ≥4 new predicates reach `accepted/` at **GREEN**
on ≥5 real interiors, with exact-replay verified across 3 runs and Article_Eater anchor grounding
complete.

## 2. The per-predicate recipe (proven on C01/C29 — reuse verbatim)

Every ticket is the same six steps; this is what made C01/C29 trustworthy:
1. **`cnfa_algs/<module>.py` function** — pure numpy/OpenCV, **deterministic** (seed any
   kmeans/random; restrict FFT bands away from Nyquist). Returns an `AttributeResult` with
   `scalar`, `field` (if localizable), `method`, `confidence`, declared constants.
2. **Registry entry** — `_spec("<id>", "image_attr", IMAGE_ONLY, "replayable"|"replayable_tol",
   "GREEN")`. GREEN is allowed here because there is no heuristic-geometry ceiling.
3. **Route through the `derivation` chokepoint** — `scored`/`abstain`/`unknown`; a value with no
   evidence is structurally impossible.
4. **Pure-core unit test + M1 exact-replay + a negative control** — and **run it** (no ship
   untested). GREEN demands `replayable` = *exact* match (tol 0 for pure int/deterministic ops;
   `replayable_tol` only where float accumulation forces it).
5. **Annotator binding** (Tier-A attrs use the existing `attr_fns` dict — one line).
6. **`run_stage` on ≥3 real interiors** → confirm SCORED + **GREEN verdict** + traceable; then
   Article_Eater anchor grounding + correctness-panel pass before "trusted."

## 3. Sprint backlog (tickets, tasks, acceptance)

### T-R1 — V9 fractal_mid_d_band_score  (XS, do first)
- **Tasks:** read the *existing* global+local fractal_dimension outputs (do NOT recompute);
  apply the declared asymmetric-trapezoid response kernel peaked on D∈[1.3,1.5] + band-coverage
  fraction; emit a low-confidence flag when the box-count fit R²<0.98 (broken scaling).
- **Acceptance:** exact-replay (tol 0) across 3 runs; unit test asserts the response curve
  peaks in-band and falls off outside; **metadata labels the stress-reduction leg "preliminary"**
  (skeptic citation caveat); reuses fractal_dimension — verify no recompute (M3 dependency).

### T-R2 — V2 spectral_discomfort_deviation  (S)
- **Tasks:** grayscale → Hann window → 2D FFT → radial power spectrum over ≥4 octaves → OLS
  log-log slope α (with R²); (a) naturalness = closeness of α to the natural value; (b) CSF-
  weighted positive mid-band residual (Penacchio–Wilkins); (c) orientation-resolved stripe-peak
  detector for periodic louvers/grids. **Emit the declared FOV/viewing-distance assumption** with
  every score (cycles/degree calibration).
- **Acceptance:** slope-recovery self-test on synthetic 1/f² noise returns ≈−2.0 (the author's
  own check); fitted band excluded from the Nyquist end (image-quality caveat emitted);
  `replayable_tol` exact within tol; negative control: a flat/degenerate spectrum → abstain not
  a fabricated number.

### T-R3 — V13 edge_orientation_entropy  (S)
- **Tasks:** Sobel orientation histogram entropy (first-order) + Redies-lab pairwise second-order
  orientation entropy; pure pixel arithmetic, no segmentation.
- **Acceptance:** exact-replay; unit test on a synthetic grid (low entropy) vs isotropic noise
  (high entropy); anchors verified (Grebenkina 2018).

### T-R4 — V1 contour_angularity_index  (M)
- **Tasks:** Canny → linked contour chains ≥ min length → Douglas-Peucker/turning-angle + local
  circle fits → decompose arclength into straight/arc/sharp-corner; output curve-fraction and a
  separate corner-density threat subscore; optional eye-level-band weighting. Feeds the hedonics
  layer as a **signed** valence input.
- **Acceptance:** **strip the misremembered Vartanian "approach decisions" clause** (skeptic
  citation fix) — anchor only on curvature-preference (Bar&Neta, Dazkir&Read, Chuquichambi);
  undistort/flag lens barrel (else straight walls read as curves); person/plant-contour variant
  drops to AMBER and is labeled so; base variant exact-replay GREEN.

### T-R5 — V6+V7 Rosenholtz clutter consolidation  (M)
- **Tasks:** implement Feature Congestion (V7, Lab covariance ellipsoids) + Subband Entropy (V6,
  steerable-pyramid coefficient entropy) with the **published** pooling weights (verify against
  the 2007 paper — the candidate said "luminance-dominant"; confirm before hard-coding).
- **Acceptance (the reliability crux):** run BOTH against the legacy tiled processing-load proxy
  on the corpus; if they agree, **retire the legacy proxy** (don't ship 3 clutter numbers into
  hedonics — that is the double-count the skeptic flagged); corpus-percentile normalization
  assumption stated; exact-replay.

### T-R6 (stretch) — V10 landmark_differentiation / V17 popout_margin
- **Gate first:** confirm the upstream landmark-salience/saliency module is classical (it is —
  spectral residual). If any frozen model rides underneath, these inherit AMBER — label and defer.

## 4. Sequencing & cadence
```
Day 1     T-R1 (V9)  land + test + run_stage  ← quickest GREEN win, validates the recipe end-to-end
Day 2-3   T-R2 (V2)  + slope self-test
Day 3-4   T-R3 (V13)
Day 4-6   T-R4 (V1)  + citation fix + lens caveat
Day 6-8   T-R5 (V6/V7) + legacy-proxy retirement decision (needs corpus run)
Day 8-9   T-R6 gate check (stretch)
Day 9-10  Verification stream (§6): 5-image GREEN run, Article_Eater grounding, correctness panel
```

## 5. Parallel workstream — RAISE the reliability of the AMBER compounds (C01/C29 already built)
Not a rebuild; three moves that move them toward trust:
1. **Labeled A-vs-B set** — assemble ~20 interior pairs with known outcomes (cross-path anchor vs
   dead-alcove anchor; stranded vs live amenity). Calibrate the gate `D0_M`, `RIDGE_PCTL`,
   `REG_FLOOR` against them instead of the current declared defaults.
2. **≠-mind inference judge** — a VLM/AG pass on the AMBER units: "does the score follow from the
   cited region+cell?" This is the owed step that lets an AMBER unit be accepted.
3. **Cross-tier registration audit** — spot-check `pixel_to_plan_cell` mapped cells against the
   plan; if error is high, widen to abstain more aggressively (fail-closed is cheap, wrong-scored
   is expensive).

## 6. Verification stream (definition of done for the sprint)
- Each predicate: unit test PASSES (run, not asserted); `run_stage` shows **GREEN** verdict on
  ≥3 interiors; exact-replay across 3 runs; negative control REJECTED.
- **Cross-environment (lesson L10):** run the whole harness once **on the Mac** — GREEN exact-
  replay must hold across sandbox↔Mac OpenCV/numpy, or the affected predicate widens to
  `replayable_tol`. Do this before trusting content-addressed skip.
- **Grounding:** every literature anchor cleared through Article_Eater/Knowledge Atlas (the V1
  Vartanian and V9 stress-leg caveats are pre-flagged).
- **Correctness panel:** the 9-seat Fable panel runs the code and confirms each computes what it
  claims (as it did for C1–C24) before any predicate is marked trusted.

## 7. Risks / mitigations
- **Photographic-style confounds** (exposure, JPEG, defocus shift FFT/fractal/clutter) → each
  predicate emits an image-quality caveat; corpus-percentile normalization assumes homogeneous
  capture — state it.
- **Double-counting into hedonics** (V6/V7 vs legacy; V9 reuses fractal_dimension) → T-R5 retires
  the legacy proxy; V9 reads, never recomputes.
- **GREEN over-claim** → GREEN is *earned* by exact cross-environment replay, not assigned; any
  seed drift or Mac↔sandbox divergence demotes to AMBER automatically.

*The whole sprint reuses the C01/C29 machinery and discipline already committed; these Tier-A
predicates are simpler (no plan, no registration), so the recipe runs faster per ticket.*
