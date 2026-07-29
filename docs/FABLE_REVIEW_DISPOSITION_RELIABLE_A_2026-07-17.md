# DISPOSITION of the Fable review — Sprint Reliable-A
### 2026-07-17 (Cowork). Response to `FABLE_REVIEW_RESULT_RELIABLE_A_2026-07-17.md`

**Verdict accepted in full.** The review was correct: the mechanical suite proved determinism and
selected orderings, not construct fidelity. Every finding below was acted on. No finding was
disputed. Two of the fixes revealed *further* real defects — including one in my own first F7 patch
— which is exactly what the two-layer review was for.

## Per-finding actions (all applied + re-tested in sandbox)

| # | Finding | Severity | Action taken | Status |
|---|---|---|---|---|
| **F1** | V13 blank image → max entropy (uniform histogram imputed from no edges) | CRITICAL | `_orientation_hist` now returns `None` below 40 edge px; `edge_orientation_entropy` ABSTAINS (scalar=None, reason=insufficient_edges). Second-order now samples only valid edge pairs. Locked with a blank→None test. | **FIXED + tested** |
| **F2** | V2 FOV unused; radial averaging ≠ Penacchio–Wilkins 2-D metric | HIGH | Renamed `spectral_discomfort_deviation` → `spectral_slope_deviation`; **demoted to AMBER**; registry note states it is NOT the 2-D metric and does not use FOV. | **RELABELLED + demoted** |
| **F3** | V6 ≠ published Subband Entropy (grayscale, no pyramid, invented divisor) | HIGH | Renamed → `grayscale_gabor_entropy_proxy`; **AMBER**; note says "PROXY, not Rosenholtz." | **RENAMED + demoted** |
| **F4** | V7 ≠ published Feature Congestion (arbitrary weights/K) | HIGH | Renamed → `local_congestion_proxy`; **AMBER**; note says "PROXY, not Feature Congestion." | **RENAMED + demoted** |
| **F5** | V9 R² does not prove scaling validity | HIGH | **Demoted to AMBER**; note: R² doesn't establish a valid scale range; constants are engineering; labeled calibration owed. | **Demoted** |
| **F6** | C29 seat proxy misclassifies wall/floor overlap | HIGH | Already AMBER; failure mode kept; calibration deferred (labeled amenities). | **Acknowledged (AMBER)** |
| **F7** | C01 tied-ridge erases discrimination | MEDIUM | Added `ridge_is_degenerate` → C01/C29 UNKNOWN on a uniform field. **My first patch tested std on the *compressed* score01 and wrongly killed EVERY real image**; corrected to coefficient-of-variation on RAW Turner integration (real structure: CV≈11.7). C01/C29 now score on real images and fail closed only on genuinely uniform fields (both cases tested). | **FIXED (twice) + tested** |
| **F8** | V1 whole-image contour; `lens_bow_flag` is dead (`*0.0`) | MEDIUM | Removed the dead flag entirely; **demoted V1 to AMBER**; note: image-contour statistic, NOT validated architectural valence. | **FIXED + demoted** |

**Net tier change:** every sprint primitive (V1,V2,V6,V7,V9,V13) is now **AMBER**. Nothing in this
sprint claims GREEN. C01/C29 remain AMBER. The pre-existing Tier-A attrs (brightness_variance,
edge_clarity, symmetry, palette_entropy, processing_load, fractal_dimension, glare, warmth) keep
their prior GREEN.

## Layer-2 point on M1 (accepted, deferred as a design change)
Replay proves reproducibility, not provenance or construct validity: a different procedure that
happens to equal the clipped pipeline output survives. **Accepted.** The proper repair is to
replay **intermediate sufficient statistics** (spectrum hash, edge count + histogram, pyramid-band
entropies) and test them against independent reference implementations + labeled data — not a more
elaborate scalar replay. Logged as **TODO M1′** (socket-wide verify upgrade), not done here.

## Decision updates
- **D1** → adopt the review's language: the socket's GREEN means **mechanically-GREEN** (replay +
  self-confidence), NOT construct-validated. `tier_a_view` docstring + disposition say so; a full
  schema split (mechanical-tier vs construct-tier) is logged as TODO.
- **D3** → **REJECTED as the review advised.** FOV removed from the claim; only the named radial
  spectral slope/residual ships (AMBER).
- **D4** → **changed to demote** (V1 AMBER).
- **D2** → unchanged in principle (keep legacy, don't aggregate) — reinforced: V6/V7 are proxies,
  not validated replacements; nothing may be weighted into hedonics until faithful + calibrated.
- **D5** → implementation was defective (dead flag); flag removed; a real bow diagnostic is TODO.
- **D7** → MODEL_VERSION bumped again for this corrective epoch (`+reviewfix`).

## Still owed (not claimed done — the next batch)
1. **Faithful reimplementations** of V6/V7 (CIELab steerable pyramid + published weights) and V2
   (2-D Fourier-energy discomfort with real angular subtense) — or keep them as named proxies.
2. **M1′ sufficient-statistic replay** across the socket.
3. **Mac↔sandbox** exact-replay comparison of fixtures + intermediate statistics.
4. **Article_Eater / Knowledge-Atlas grounding** of every anchor (the review did a literature audit,
   not ingestion).
5. **Labeled A-vs-B interior corpus** to calibrate C01/C29 thresholds (D0, percentile, dE, floors)
   and V9's response constants — currently declared engineering defaults.
6. **V13 second-order**: implement the true Grebenkina pairwise-over-distances measure, or keep the
   first-neighbour proxy under its honest name.

## Re-test evidence (sandbox, 2026-07-17)
- All core suites PASS: C01, C29, V9, and reliable-attrs (V2/V13/V1/V6/V7) incl. the new V13
  blank→abstain lock and the F7 uniform-vs-structured guard.
- Full gate `run_stage` on 3 interiors: AMBER=3 RED=0, negative control REJECTED (RED), idempotent
  re-run, worker boundary writes DENIED.
- C01/C29 score on real images (0.484 / 0.229) via the corrected raw-integration ridge; UNKNOWN
  only on a genuinely uniform field.
