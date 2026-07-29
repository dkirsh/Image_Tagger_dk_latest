# FABLE REVIEW RESULT — Sprint Reliable-A

**Date:** 2026-07-17  
**Scope:** C01, C29, V9, V2, V13, V1, V6, V7, Tier-A view, and Decisions D1–D7  
**Method:** two-layer adversarial review specified by `FABLE_REVIEW_BATCH_RELIABLE_A_2026-07-15.md`

## Executive verdict

The batch is **not ready for certification as stated**. The mechanical test suite is deterministic and passes
(16/16), but it tests selected orderings rather than faithful implementation of the cited constructs. V13 has a
decisive degenerate-input defect (a blank image scores maximum entropy). V2 does not use its declared FOV and does
not implement the cited two-dimensional Fourier-energy discomfort measure. V6 and V7 are approximations, not the
published Rosenholtz measures. V1 is a useful experimental edge-contour statistic, but its architectural-valence
interpretation remains confounded. V9 correctly evaluates its declared trapezoid, but the whole-interior edge-map
construct and its response constants are not validated sufficiently for GREEN. C01 and C29 correctly evaluate their
declared products, but the product inputs do not establish the social constructs; AMBER is the proper ceiling.

Recommended disposition: retain all eight as experimental outputs; keep C01/C29 AMBER; demote V9, V2, V13, V1,
V6, and V7 to AMBER until the defects and validation gaps below are resolved. A fixed V13 could return to GREEN
quickly as an image statistic, provided it is renamed or made faithful to the cited second-order measure.

## Evidence actually obtained

- `pytest` result on the Mac environment: **16 passed in 2.30 s**.
- V2, identical stripe construction at different raster sizes: 128 px = `0.8344`; 256 px = `1.0000`;
  512 px = `0.9539`. The declared `FOV_DEG=65` is not referenced by the computation.
- V13: uniform blank = `1.0000`; one-pixel checkerboard = `1.0000`; isotropic noise = `0.9982`.
- V1: blank and checkerboard abstain (`scalar=None`); random noise = `0.2221`, with corner density `0.6237`.
- V6: blank = `0.0000`; one-pixel checkerboard = `0.0000`; random noise = `0.7311`.
- V7: blank = `0.0000`; one-pixel checkerboard = `0.8844`; random noise = `0.7167`.
- V9 upstream box count: checkerboard D = `-0.0000`, R² = `1.0000`, score `0.0000`; noise D =
  `1.9377`, R² = `0.9993`, score `0.2043`.
- C01: a tied integration field makes every cell part of the 85th-percentile ridge. Gate values at 0, 2.5,
  5, and 8 m are `1.0000`, `0.3679`, `0.0183`, and approximately `0.0000`.
- C29: a wall-object bounding box whose bottom 25% overlaps the inferred floor receives seat affordance `0.25`.

These probes establish local behavior only. No labeled A/B interior corpus was available, and no Mac↔sandbox
comparison was possible in this run.

## Layer 1 — per-predicate verdicts

| Predicate | Computes declared formula? | Evidence anchor | Ceiling honest? | Register certification |
|---|---|---|---|---|
| C01 triangulation | Yes for the product; no for the claimed social construct | Whyte/Hillier are real but do not validate this product, thresholds, or photo-to-plan registration | **AMBER honest** | No; experimental diagnostic only |
| C29 stranded amenity | Yes for the product; seat proxy can misclassify wall/floor overlap | Whyte is relevant qualitatively; the inverse formula is an engineering invention | **AMBER honest** | No; experimental diagnostic only |
| V9 fractal band | Yes for the declared trapezoid | Preference/fractal literature is real; whole-interior Canny D and the exact plateau/falloff are not established | GREEN too high | Demote to AMBER |
| V2 spectral discomfort | No: FOV unused; radial 1-D residual substitutes for cited 2-D energy distribution | Field and Penacchio–Wilkins are real but incorrectly operationalized | GREEN not honest | Demote; ship slope separately only after validation |
| V13 orientation entropy | No on low-edge inputs; second-order algorithm is not the cited pairwise measure | Grebenkina et al. is real but only loosely used | GREEN not honest | Demote; fix blank/low-edge abstention and formula |
| V1 contour angularity | Computes its own edge-chain statistic; not architectural contour valence | Curvature-preference papers are real; object-to-room transfer is unvalidated | GREEN too high | Demote to AMBER |
| V6 subband entropy | No: grayscale Gabor entropy omits CIELab channels, steerable pyramid, and published weighting | Rosenholtz et al. is real but implementation is materially different | GREEN not honest | Rename as proxy or implement paper |
| V7 feature congestion | No: simplified local-variance mixture with declared arbitrary weights and scale | Rosenholtz et al. is real but implementation is materially different | GREEN not honest | Rename as proxy or implement paper |

### Ranked findings

#### F1 — V13 manufactures maximum entropy on no evidence

**Severity:** CRITICAL · **Level:** L2/L4 · **Verdict:** WRONG  
**Claim:** edge-orientation entropy measures diversity and independence of detected edge orientations.  
**Defect:** when fewer than 20 edge pixels exist, `_orientation_hist` returns a uniform 18-bin histogram. Uniform
histograms have maximum entropy, so absence of edges is represented as maximum orientation diversity. The
second-order fallback repeats the same error.  
**Evidence:** a uniform 256×256 gray image returns `scalar=1.0`, `first_order=1.0`, `second_order=1.0`.  
**Fix:** abstain or return a separately flagged no-edge state; never impute a uniform distribution. Implement
second-order edge-pair sampling only between valid edges at the distances/angles specified by the reference.

#### F2 — V2's disclosed FOV is ornamental, not computational

**Severity:** HIGH · **Level:** L2/L3 · **Verdict:** WRONG  
**Claim:** a Penacchio–Wilkins/CSF-weighted discomfort magnitude calibrated under a 65° FOV assumption.  
**Defect:** `FOV_DEG` is emitted in metadata but never enters `_csf_weight`, `_mid_band_residual`, or the score.
Frequency is normalized to the selected FFT band, not converted to cycles/degree. The algorithm also radially
averages power before scoring, whereas Penacchio and Wilkins emphasize the two-dimensional distribution of Fourier
energy across spatial frequency and orientation.  
**Evidence:** code trace shows no use of `FOV_DEG`; resizing the same stripe construction changes scores from
`0.8344` to `1.0` to `0.9539`.  
**Fix:** separate and rename the radial power-slope statistic. Reimplement the published 2-D discomfort metric with
true pixel angular subtense, or abstain from absolute discomfort when camera/display geometry is unknown.

#### F3 — V6 is not the cited Subband Entropy algorithm

**Severity:** HIGH · **Level:** L3/L4 · **Verdict:** WRONG  
**Claim:** Rosenholtz–Li–Nakano Subband Entropy clutter.  
**Defect:** the cited algorithm converts to CIELab, decomposes luminance and both chrominance channels with a
steerable pyramid, and combines channel entropies using published weights. This code converts to grayscale and sums
histogram entropy of 12 Gabor-magnitude maps, with an invented divisor of `12*5`.  
**Evidence:** a dense one-pixel checkerboard returns `0.0`, the same as a blank image, while random noise returns
`0.7311`. Aliasing is a counter-case, but the formula discrepancy alone is decisive.  
**Fix:** implement the published multichannel pyramid and weights, or rename to `grayscale_gabor_entropy_proxy`.

#### F4 — V7 is not the cited Feature Congestion algorithm

**Severity:** HIGH · **Level:** L3/L5 · **Verdict:** WRONG  
**Claim:** Rosenholtz Feature Congestion.  
**Defect:** the implementation uses local variances, a Laplacian, Gabor energy, arbitrary `0.5/0.3/0.2` weights,
and arbitrary saturation `K=40`. Its own failure mode says to verify the pooling weights before publication. This
is incompatible with a GREEN-certified claim of implementing the published measure.  
**Evidence:** the code and metadata expressly identify unverified weights; checkerboard `0.8844` and noise `0.7167`
show the proxy moves, not that it is Feature Congestion.  
**Fix:** reproduce the published feature covariance, scale handling, and pooling; validate against the paper's
stimuli or reference implementation. Otherwise rename and demote.

#### F5 — V9 converts a fragile four-scale edge fit into a strong preference claim

**Severity:** HIGH · **Level:** L3/L4 · **Verdict:** CRUDE-BUT-HONEST  
**Claim:** whole-scene preference/calm is high for edge-map D in `[1.3,1.5]`.  
**Defect:** upstream D is fitted at only four box sizes (`2,4,8,16` px) on fixed-threshold Canny edges. R² can be
perfect for a degenerate checkerboard (`D≈0`, `R²=1`) and high for noise (`D=1.9377`, `R²=0.9993`). Fit R² therefore
does not establish that the photograph contains the kind of scale range or fractal stimulus studied. The plateau
and falloff are engineering constants.  
**Fix:** require a defensible scale span, validate D against known fractals at multiple resolutions, and calibrate
the response on labeled interiors. Keep AMBER meanwhile.

#### F6 — C29's seat affordance is not an affordance detector

**Severity:** HIGH · **Level:** L1/L4 · **Verdict:** CRUDE-BUT-HONEST  
**Claim:** distinguishes usable dwell amenities from flat wall art.  
**Defect:** it measures the fraction of the saliency bounding box assigned plane label 0 or 1. A wall feature whose
box extends to the floor acquires positive usability without a seat or usable surface. Plane label 0 also means
`furniture/other`, an uncontrolled union.  
**Evidence:** a synthetic wall box overlapping 25% floor returns `seat_affordance01=0.25`.  
**Fix:** require a localized support surface and object/affordance evidence; calibrate on labeled amenities.

#### F7 — C01 ridge ties can erase off-path discrimination

**Severity:** MEDIUM · **Level:** L2/L4 · **Verdict:** CRUDE-BUT-HONEST  
**Claim:** gates salient anchors by distance from the high-integration desire-line ridge.  
**Defect:** percentile thresholding includes every tied cell. In a uniform or quantized integration field, the ridge
becomes the whole free plan, making every anchor on-ridge and C29 incapable of detecting stranded amenities.  
**Evidence:** four cells all at integration `0.5` produce a ridge containing all four cells.  
**Fix:** detect low-variance integration and return UNKNOWN, or define a top-k ridge with stable tie handling.

#### F8 — V1 is an image-contour statistic, not an architectural contour statistic

**Severity:** MEDIUM · **Level:** L1/L4 · **Verdict:** CRUDE-BUT-HONEST  
**Claim:** curvature-versus-angularity supports an architectural valence inference.  
**Defect:** all qualifying Canny contours count, including foliage, textiles, people, graphics, and lens distortion.
The literature supports preference differences for controlled curved/angular objects or interiors; it does not
validate this whole-photograph weighted formula. The `lens_bow_flag` is always zero by construction (`... * 0.0`).  
**Evidence:** random noise returns a strong angular result (`0.2221`, corner density `0.6237`); the promised bow
warning cannot fire.  
**Fix:** remove the nonfunctional flag, segment architectural structure, and validate against human labels.

## Literature audit

The principal papers are real. Their use is narrower than the code documentation suggests:

- Field (1987) supports scale-related regularities of natural-image spectra; it does not certify this discomfort
  scalar: [paper](https://inc.ucsd.edu/~marni/Igert/Field_1987.pdf).
- Penacchio & Wilkins (2015) explicitly make the two-dimensional Fourier-energy distribution central; radial
  averaging discards that contribution: [paper](https://openacchio.github.io/assets/pdf/visual%20discomfort%20and%20the%20spatial%20distribution%20of%20Fourier%20energy%20Penacchio%20Wilkins%20VR%202015.pdf).
- Grebenkina et al. (2018) calculate first- and second-order edge-orientation entropy; the local horizontal roll in
  this code is not shown to be their measure: [paper](https://livrepository.liverpool.ac.uk/3027759/1/GrebenkinaBrachmannBertaminiKaduhmRedies2018.pdf).
- Rosenholtz, Li & Nakano (2007) give concrete Feature Congestion and multichannel Subband Entropy algorithms and
  validation against visual search: [paper](https://doi.org/10.1167/7.2.17).
- Bar & Neta (2006) supports preference effects for controlled curved versus sharp-contoured objects, not automated
  extraction of architectural valence from a room photograph: [paper](https://doi.org/10.1111/j.1467-9280.2006.01759.x).
- Hillier et al. (1993) supports a relation between configurational integration and movement at urban scale; it does
  not validate the C01/C29 product or its thresholds: [paper](https://discovery.ucl.ac.uk/id/eprint/1398/).

The removed Vartanian “approach decisions” clause is indeed absent from the implementation. V9 labels its stress
leg preliminary, which is honest; nevertheless, its registry note still joins “preferred/calming” under GREEN,
which is too strong. Article_Eater/Knowledge-Atlas grounding was not performed here and remains owed.

## Decisions D1–D7

| Decision | Layer-1 recommendation | What would change it? |
|---|---|---|
| D1 Tier-A-only mode | **Keep**, but rename verdict to `mechanically_GREEN` or report construct status separately. Current GREEN conflates replay success with validity. | A schema that reports mechanical tier and construct-validation tier independently |
| D2 retain three clutter measures | **Do not aggregate any yet.** Keep legacy for compatibility, but mark V6/V7 experimental; they are not validated replacements. | Corpus agreement, human/search labels, and faithful reference implementations |
| D3 fixed 65° FOV | **Reject current decision.** The assumption is unused. Ship only a clearly named radial spectral slope/residual until angular calibration exists. | Camera/display angular subtense or a validated scale-invariant discomfort method |
| D4 base V1 GREEN | **Demote to AMBER.** Determinism is not construct validity; object contours remain a material confound. | Architectural segmentation plus labeled human curvature/valence validation |
| D5 warn, do not undistort | **Principle correct; implementation defective.** The flag is multiplied by zero and never warns. | Implement and validate a real bow diagnostic, or remove the claim |
| D6 per-pair review | **Accept for process**, provided review blocks certification when it finds a construct defect. | Evidence that pair batching allowed a shared defect to propagate |
| D7 one version bump | **Accept sprint-level bump**, but bump again after every corrective change arising from this review. | Any deployed record created after algorithm changes without a new model version |

Highest-stakes calls: D3 must change now; D2 should preserve compatibility but forbid weighting or certification
until faithful measures and corpus calibration exist.

## Layer 2 — attack on the Layer-1 reviews

| Target review | Grade | Adversarial result |
|---|---|---|
| C01: AMBER experimental | **CONFIRMED** | Layer 1 could have been harsher: inferred geometry and landmark salience may fail jointly, while a tied ridge eliminates the intended interaction. |
| C29: AMBER experimental | **CONFIRMED** | The seat proxy's wall/floor overlap supplies a concrete missed failure; this is not a generic “needs labels” caveat. |
| V9: demote | **CONFIRMED** | A perfect R² on a degenerate checkerboard refutes reliance on R² as a scaling-validity gate. The response helper itself remains correct. |
| V2: demote | **CONFIRMED** | The unused FOV and radial collapse are direct formula defects. Caution is not excessive. |
| V13: demote | **CONFIRMED** | Blank→1.0 is a decisive counterexample. A narrow fix can restore viability; killing the construct would be excessive. |
| V1: demote | **CONFIRMED** | The architecture/object confound is realized by ordinary foliage and décor, and the bow warning is nonfunctional. The statistic may still be useful under a modest name. |
| V6: demote/rename | **CONFIRMED** | Published steps are absent and checkerboard→0 supplies a counter-case. This does not refute entropy as a clutter family; it refutes the present label. |
| V7: demote/rename | **CONFIRMED** | The source itself admits unverified weights. A proxy can be retained, but certification would be premature. |

### Attack on M1 replay and negative controls

M1 establishes reproducibility of the stored scalar under the pinned pipeline. It does **not** establish how the
stored value was originally obtained, nor that the value has the claimed meaning. A value generated by a different
procedure survives whenever it equals the pipeline result. Clipping and degenerate fallbacks make such collisions
easy, not merely theoretical:

- For V2's 256-px stripes, the pipeline returns exactly `1.0`. A different procedure, “detect periodic stripes and
  return 1,” yields the same scalar and survives replay.
- For V13's blank image, the pipeline returns exactly `1.0`. A fabricated constant-one procedure also survives.
- Any pipeline output at clipped `0` or `1` has a large equivalence class of unrelated generating procedures.

Thus the existing negative controls prove that conspicuously wrong stored values are rejected. They do not prove
provenance, formula fidelity, or construct validity. The repair is not a more elaborate scalar replay. Preserve and
replay intermediate sufficient statistics (spectrum/hash, edge count and histograms, pyramid-band entropies), and
test them against independent reference implementations and labeled data.

## Ground truth still owed

1. **Mac↔sandbox replay:** not completed. This run supplies Mac results only. GREEN must not be justified by a
   cross-environment claim until the same fixtures and intermediate statistics are compared in both environments.
2. **Article_Eater/Knowledge-Atlas grounding:** not completed. Direct primary-source checks above are a literature
   audit, not ingestion into those systems.
3. **Labeled A-vs-B interiors for C01/C29:** not completed. The thresholds `85th percentile`, `D0=2.5 m`,
   `dE=8/40`, and registration/geometry floors remain declared engineering defaults.

## Final advice

Do not discard the sprint. Its reusable derivation and replay machinery is useful, and several functions are
promising experimental measurements. But distinguish three propositions: a number is deterministic; a formula is
faithful to a paper; and a number validly measures a cognitive or architectural construct. The present GREEN label
mostly proves the first proposition. Certification requires all three.
