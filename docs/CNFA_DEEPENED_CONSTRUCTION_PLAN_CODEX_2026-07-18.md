# CNfA Deepened Construction Plan
### Codex execution of `CODEX_DEEPEN_PLAN_AND_TESTPLAN_PROMPT_2026-07-18.md`

This document deepens `CNFA_CONSTRUCTION_SPEC_2026-07-18.md`. It does not close the still-owed items. The faithful V2/V6/V7 reimplementations, M1' replay, Mac-sandbox replay, grounding, and labeled calibration corpus remain open until implemented and independently verified.

## Baseline Run

Executed from `/Users/davidusa/REPOS/Image_Tagger_dk_latest` with `PYTHONPATH=.`.

```text
CMD: PYTHONDONTWRITEBYTECODE=1 PYTEST_ADDOPTS='-p no:cacheprovider' PYTHONPATH=. pytest annotation_socket/tests -q
OUT: 19 passed in 0.86s
VERDICT: current annotation_socket tests pass.
```

```text
CMD: PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 -m annotation_socket.run_stage /tmp/cnfa_codex_stage_20260718 \
     'Example Images/50-day-street-offices-norwalk-1200x1165-compact.jpg' \
     'Example Images/BalancedCare-Render-Corridor2-wpeople1_960x530.webp' \
     'Example Images/Industrial-open-concept-office-project-by-Decorilla-1024x819.jpeg'
OUT: queue=3; worker run1 processed=3 skipped=0; checker GREEN=0 AMBER=1 RED=2.
OUT: the AMBER unit scored 27/27 applicable predicates, abstained 18, unknown 0.
OUT: seeded defaulted C14 plus constant C8 negative control -> RED with both FABRICATION problems.
OUT: run2 processed=0, skipped_content_addressed=3.
OUT: worker writes to control.jsonl and accepted/ denied by BoundaryError.
VERDICT: current state is mechanically alive but not GREEN overall; AMBER units still need the distinct inference judge.
```

## M1' Sufficient-Statistic Replay

The present `annotation_socket/verify.py` M1 replays final scalar values. That catches fabrication, but it is too coarse for faithful-method adequacy. M1' should replay the sufficient statistics that make the scalar defensible. The auditor must compare both scalar and pre-scalar signatures.

### Proposed Record Shape

Each `AttributeResult.extras` should include an `m1_prime` object:

```json
{
  "audit_class": "fft_2d | radial_fft | orientation_hist | steerable_pyramid | feature_congestion | box_count | geometry_plan | segmentation_mask | color_palette | luminance_field",
  "stats_version": "cnfa-m1p-2026-07-18",
  "stats": {},
  "digest": "sha256 canonical-json(stats)"
}
```

`verify.py` should recompute the same stats from the image bytes, canonicalize numeric arrays by explicit rounding rules, compare the digest, and then compare the scalar. A scalar match with a stats mismatch is AMBER or RED depending on whether the mismatch changes the interpretive claim. A stats match with a scalar mismatch is RED.

### Audit Classes And Required Stats

| audit_class | Required emitted stats | Re-derivation rule in `verify.py` | Pass criterion |
|---|---|---|---|
| `luminance_field` | grayscale conversion tag, local-window size, global mean/std, local SD quantiles P5/P50/P95/P99, bright-pixel fraction, optional wall-mask digest | Recompute from decoded image with the declared kernel and mask. | Scalar exact for replayable or within tolerance; quantiles within 1e-4 after rounding. |
| `color_palette` | color space, k, seed, cluster centers in Lab and RGB hex, cluster proportions, entropy | Re-run deterministic k-means with `cv2.setRNGSeed(1234)` and declared attempts. | Center ordering canonicalized by L,a,b; entropy within 0.005; proportions within 0.01. |
| `radial_fft` | image size, window function, radial-bin power vector digest, fit band, slope, intercept, R2, residual rule | Recompute Hann-windowed FFT and radial profile. | Fit-band and slope/residual match within tolerance; digest over rounded profile matches. |
| `fft_2d` | angular calibration parameters, pixels-per-degree or FOV source, 2D frequency grid digest, discomfort-energy integration mask | Recompute unaveraged 2D Fourier energy. | Required for faithful V2. Absence keeps V2 AMBER proxy. |
| `orientation_hist` | edge detector parameters, min edge px, bin count, first-order hist, co-occurrence offset set, second-order matrix digest | Recompute Sobel/Canny orientations. | Edge count, histograms, and scalar agree; near-blank images abstain, never impute uniform entropy. |
| `steerable_pyramid` | color space, pyramid family, scales, orientations, subband coefficient entropy per channel/subband, pooling formula | Recompute the exact pyramid. | Required for faithful V6. Gabor-only stats must be named proxy. |
| `feature_congestion` | Lab covariance windows, contrast-bandpass responses, oriented-energy covariance, local feature covariance summaries, Minkowski exponent, published weights | Recompute local congestion map. | Required for faithful V7. Arbitrary weights keep AMBER proxy. |
| `box_count` | edge detector parameters, image crop divisibility, box sizes, counts per size, fitted D, R2, valid-scale mask | Recompute edge map and counts. | Counts exact; D/R2 within tolerance; low R2 cannot claim fractal validity. |
| `geometry_plan` | segmentation version, plane-label mask digest, depth map digest, grid construction parameters, grid hash, upstream step list | Re-run image->planes/depth->PlanGrid->metric. | Grid hash and upstream hashes match; AMBER ceiling remains unless real plan/depth is supplied. |
| `segmentation_mask` | model/source id, class map digest, class palette, confidence quantiles, abstention thresholds | Re-run or verify declared external mask provenance. | If model is nondeterministic or unavailable, M1' becomes provenance replay only and tier caps AMBER. |

### Concrete `verify.py` Change

Add a `replay_sufficient_stats(record, spec)` call after the existing scalar replay:

1. Inspect each scored predicate's `evidence.audit_class` or `extras.m1_prime.audit_class`.
2. Recompute stats by dispatching to pure functions in `annotation_socket/m1_prime.py`.
3. Canonicalize arrays by fixed rounding and shape metadata.
4. Compare emitted digest to recomputed digest.
5. Emit `M1_PRIME:<predicate>:stats_mismatch` on mismatch.
6. Treat missing `m1_prime` as:
   - allowed but AMBER for legacy deterministic predicates;
   - RED for any predicate claiming faithful V2, V6, V7, detector, segmentation, or geometry GREEN.

This is a narrow change. It does not replace the controller, the queue, or the existing M1 scalar replay.

## Faithful Reimplementations

### V2: Faithful 2D Spectral Discomfort

Current code: `cnfa.fluency.spectral_slope_deviation` in `cnfa_algs/reliable_attrs.py` is a radial 1/f slope plus residual. It is explicitly not the Penacchio-Wilkins 2D discomfort metric.

Faithful plan:

1. Require angular calibration: source FOV or pixels-per-degree. If missing, score only the existing AMBER proxy.
2. Convert image to luminance, linearized if possible. Record gamma assumption if using sRGB.
3. Window image, compute 2D FFT power.
4. Preserve the 2D energy distribution, not radial average only.
5. Apply spatial-frequency band limits in cycles/degree, using the calibration.
6. Compare energy distribution against the natural 1/f expectation in the relevant 2D bands.
7. Compute the published discomfort statistic and emit `fft_2d` M1' stats.
8. Validate against synthetic gratings/checkerboards and against real images with known high/low pattern glare.

Validation target: known ordering of high-contrast repetitive stripes/checkerboards over naturalistic or low-contrast interiors, plus agreement with a reference implementation on the same calibrated raster. Without angular calibration, GREEN is impossible in principle.

### V6: Faithful Rosenholtz Subband Entropy

Current code: `cnfa.fluency.grayscale_gabor_entropy_proxy`; it uses grayscale Gabor magnitude entropy and is rightly named proxy.

Faithful plan:

1. Convert image to CIELab, retaining L, a, b channels.
2. Build the specified steerable pyramid: at least 3 scales x 4 orientations unless the paper's exact implementation says otherwise.
3. For each channel and subband, compute coefficient distributions and entropy by the published binning/smoothing rule.
4. Pool subband entropies using the published weights, not an invented divisor.
5. Emit per-channel and per-subband entropy table under `steerable_pyramid` M1'.
6. Add a reference implementation fixture: blank image, simple gradient, periodic texture, cluttered object field.
7. Report the existing processing-load proxy and V7 separately; do not average clutter measures unless a downstream construct model explicitly asks for a chosen clutter family member.

Validation target: match the reference implementation's subband entropy values on canonical synthetic images and preserve real-image ordering: minimal room < ordinary office < dense retail/storage.

### V7: Faithful Rosenholtz Feature Congestion

Current code: `cnfa.fluency.local_congestion_proxy`; it uses local variance in color/contrast/orientation with arbitrary weights.

Faithful plan:

1. Compute local color covariance in Lab over the paper's window schedule.
2. Compute bandpassed luminance contrast covariance.
3. Compute oriented-energy covariance across orientations/scales.
4. Pool local feature covariance by the published Minkowski rule and weights.
5. Emit local maps for color congestion, luminance congestion, orientation congestion, and the pooled feature congestion.
6. Emit `feature_congestion` M1' stats: window sizes, covariance summaries, pooling exponent, weights.
7. Validate against images where clutter is local but not global: a clean room with one dense shelf must localize the shelf.

Validation target: match a reference implementation or a frozen independent reimplementation on synthetic and real clutter gradients. If no paper-faithful reference can be obtained, keep the present proxy name and AMBER tier.

## Calibration Corpus Schema

The corpus must be pairwise and region-aware. Single global labels are insufficient for ridge fields, prospect, clutter localization, and A-vs-B claims.

### Image Table

| field | requirement |
|---|---|
| `image_id` | Stable id, no spaces. |
| `source_db` | `Example Images`, `Post_Occupancy_Evals`, `Drive`, `Zotero-derived`, or other. |
| `source_path_or_uri` | Absolute local path or Drive export id. |
| `license_status` | cleared / internal-only / unknown. |
| `environment_type` | office_open_plan, office_cellular, corridor, atrium_lobby, classroom, healthcare, hospitality, residential, retail, exterior_view. |
| `capture_type` | photo, render, diagram, fisheye, panorama, screenshot. |
| `usable_for_cnfa` | yes/no with reason. |
| `width`, `height` | Pixel dimensions. |
| `camera_quality` | normal, wide_angle, fisheye, low_res, hdr/blown, render. |
| `time_light` | daylit, evening_electric, mixed, unknown. |
| `region_annotations` | list of region ids with boxes/polygons. |
| `global_labels` | sparse construct labels, never required to cover all attributes. |

### Region Pair Table

| field | requirement |
|---|---|
| `pair_id` | Stable id. |
| `image_id` | Parent image. |
| `region_a`, `region_b` | Boxes or polygons in normalized coordinates. |
| `pair_type` | same_image_A_vs_B, cross_image_A_vs_B. |
| `target_attributes` | Attributes this pair tests. |
| `expected_direction` | A>B, B>A, equal, abstain. |
| `rater_instruction` | One visual question, e.g. "Which region is more visually cluttered?" |
| `labels` | per-rater ordinal/pairwise labels with confidence. |
| `quality_flags` | occluded, people_present, overexposed, low_resolution, wide_angle, cropped. |

### Minimum Labels

Each attribute moving toward GREEN needs:

- at least 30 real interiors with global labels;
- at least 30 A-vs-B pairs for attributes that localize or compare regions;
- at least 10 negative controls where the attribute should abstain or score near zero;
- at least 5 cross-environment replay images run on both Mac and sandbox with identical image bytes.

## GREEN Impossible From A Single Photo

The following cannot honestly be GREEN from one ordinary photograph alone:

- physical-code measurements: lux, CO2, TVOC, RT60, STI, temperature, humidity, melanopic EDI;
- temporal phenomena: flicker, waiting time, movement patterns, soundscape over time;
- behavior or policy: actual local control, privacy rules, personalization permissions;
- certified daylight/circadian exposure: needs sky, orientation, time, glazing, spectral assumptions;
- true acoustic privacy or distraction distance: needs geometry plus material/acoustic parameters;
- true distance-to-others/crowding by area: needs plan scale or calibrated depth plus seat/people detection;
- faithful V2 discomfort if angular calibration is absent;
- faithful V6/V7 if the published algorithm is not implemented and reference-checked.

These may still be AMBER proxies when the claim is carefully named and the missing substrate is recorded.

## Highest-Adequacy Work Order

1. Implement M1' stats and verifier dispatch for existing predicates.
2. Reimplement faithful V6 and V7, because the clutter family is central and currently proxy-only.
3. Reimplement V2 with angular calibration gates; keep proxy when calibration is missing.
4. Build the calibration corpus with A-vs-B pairs.
5. Add vegetation/window/material detector-backed candidates only after the corpus can test them.
6. Defer style, semantic object, policy, and sensor-only candidates until the substrate exists.
