# ATTACK CODEX2FIX RESULT - Codex 2

Date: 2026-07-18

Scope: Fresh adversarial verification of `docs/CODEX2_ATTACK_DISPOSITION_2026-07-18.md` using `docs/ATTACK_CODEX2FIX_PROMPT_2026-07-18.md`.

No implementation files were edited in this run.

## Executive Verdict

The Codex2-fix disposition is materially improved, but not complete.

V9, V2, V6, V7, the skimage portability failure, and the run-stage IndexError are fixed at the emitted-record level. The remaining serious defect is F7: the new IQR-based ridge degeneracy guard fixes the single-outlier case but introduces a top-tail blindness failure. The required 3-image run also does not reproduce the disposition's clean RED=0 claim: it returns AMBER=2, RED=1 because C01/C29 are UNKNOWN on the BalancedCare image.

## Required Run Evidence

Command:

```bash
PYTHONPATH=. pytest annotation_socket/tests -q
```

Output:

```text
................                                                         [100%]
16 passed in 0.97s
```

Command:

```bash
PYTHONPATH=. python3 -m annotation_socket.run_stage /tmp/attack3 \
  'Example Images/korridor.jpg' \
  'Example Images/Industrial-open-concept-office-project-by-Decorilla-1024x819.jpeg' \
  'Example Images/BalancedCare-Render-Corridor2-wpeople1_960x530.webp'
```

Output summary:

```text
[controller] queue: 3 units
[worker] run1 processed=3 skipped=0
[checker] verdicts: GREEN=0 AMBER=2 RED=1
[negative-control] seeded defaulted-C14 + constant-C8 -> tier=RED
FABRICATION:C8.distraction_distance scored but requires ['acoustic_params'] absent from unit
FABRICATION:C14.focus_collab_separation scored but requires ['collab_sources', 'focus_seats'] absent from unit
[worker] run2 processed=0 skipped_content_addressed=3
RUN/TEST RUBRIC: (a)+(b)+(c) demonstrated.
```

There was no crash and no `compute_failed` in the emitted records. The RED unit was:

```text
BalancedCare-Render-Corridor2-wpeople1_960x530.webp:
UNKNOWN:C01.triangulation_ignition reason=anchor_registration_unconfident
UNKNOWN:C29.stranded_amenity_index reason=anchor_registration_unconfident
```

## Per-Fix Verdicts

| Fix | Claim | Verdict | Executed evidence | Residual risk |
|---|---|---|---|---|
| Fix-1 V9 split-brain | `fractal_band.py` emits AMBER matching registry | FIXED-CONFIRMED | Producer constant and registry both AMBER. Real V9 records emitted `tier_hint AMBER`, e.g. `Industrial...jpeg` V9 `value=1.0`, `tier=AMBER` | Stale docstring in `fractal_band.py` still says rank/ceiling GREEN, but emitted JSON is fixed |
| Fix-2 V2 FOV | FOV removed from emitted method/extras; proxy labelled | FIXED-CONFIRMED | Stripe probe: 128=`0.8344`, 256=`1.0`, 512=`0.9539`; method contains no FOV; extras contain no FOV; failure modes explicitly say scale-dependent/no angular calibration | `reliable_attrs.py` comments still contain explanatory "FOV" text, but no computed or emitted FOV claim remains |
| Fix-3 V6 evidence | Method says proxy, not Rosenholtz | FIXED-CONFIRMED | Real emitted method: `grayscale Gabor-magnitude entropy PROXY - NOT Rosenholtz Subband Entropy...`; socket id, annotator key, and `AttributeResult.key` are all `cnfa.fluency.grayscale_gabor_entropy_proxy` | Internal function/docstring names remain older, but emitted evidence is honest |
| Fix-4 V7 evidence | Method says proxy, not Feature Congestion | FIXED-CONFIRMED | Real emitted method: `local-variance colour/contrast/orientation congestion PROXY - NOT Rosenholtz Feature Congestion...`; socket id, annotator key, and `AttributeResult.key` are all `cnfa.fluency.local_congestion_proxy` | Internal function/docstring names remain older, but emitted evidence is honest |
| Fix-5 F7 ridge guard | Robust IQR/median defeats outlier; real images not false-degenerate | NEW-DEFECT-INTRODUCED | Prior killer `[500]*99+[1e6]` now degenerate. Real VGA fields not degenerate: `korridor` IQR/median `0.90243`; `Industrial` `0.43322`; `BalancedCare` `0.58818`. But top-tail ridge cases fail: `[500]*85 + 900..914` has IQR/median `0.0`, p85 `560`, below-p85 `85`, yet `ridge_is_degenerate=True` and `ridge_count=0` | The guard suppresses sparse but real top-tail ridges whenever the middle quartiles are flat |
| Fix-6 portability/run_stage | skimage-free symmetry; no all-RED IndexError | FIXED-CONFIRMED, WITH OVERCLAIM | `skimage` is missing locally, but real records now score symmetry with no `compute_failed`. `_ssim_cv2`: identical=`1.0`, shifted random=`0.00397`, flipped random=`0.02049`. Forced all-RED BalancedCare variants: run_stage exited cleanly, negative control ran, no IndexError | Disposition's clean RED=0 real-image claim is not reproduced by the required command; required run is AMBER=2 RED=1 |

## F7 Detailed Evidence

Synthetic ridge guard attacks:

```text
flat+outlier: median=500, iqr/med=0.0, degenerate=True, ridge_count=0
structured_i2: iqr/med=1.99898, degenerate=False, ridge_count=15
nearflat_4pct: iqr/med=0.03922, degenerate=True
nearflat_6pct: iqr/med=0.05825, degenerate=False, ridge_count=50
85_flat_15_high: iqr/med=0.0, p85=560.0, below=85, degenerate=True, ridge_count=0
84_flat_16_high: iqr/med=0.0, p85=900.15, below=85, degenerate=True, ridge_count=0
80_flat_20_high: iqr/med=0.0, p85=904.15, below=85, degenerate=True, ridge_count=0
70_flat_30_high: iqr/med=0.8085, degenerate=False, ridge_count=15
```

This is the new defect. Since the ridge definition is the top 15 percent, a field with a flat 80-85 percent and a meaningful high-integration top tail should not automatically be called degenerate. IQR ignores exactly that structure.

Real VGA check:

```text
korridor.jpg: degenerate=False, cells=500, ridge_count=75, iqr/med=0.90243, cv=0.74862
Industrial...jpeg: degenerate=False, cells=500, ridge_count=81, iqr/med=0.43322, cv=11.66747
BalancedCare...webp: degenerate=False, cells=334, ridge_count=56, iqr/med=0.58818, cv=0.48572
```

Real C01 discrimination on `Industrial...jpeg`:

```text
anchor_cell=(6,87)
nearest_sample=(8,86)
nearest_raw=753.073
nearest_raw_rank_frac=0.748
dist_to_ridge_m=0.233
gate=0.9914
```

This says the anchor is not itself in the top 15 percent by nearest sampled raw rank, but it is physically very near ridge cells. That is plausible, but still sensitive to inferred-grid noise.

## Portability / Optional Imports

Installed locally:

```text
cv2 OK 4.13.0
numpy OK 2.4.2
scipy OK 1.17.0
skimage MISSING ModuleNotFoundError
sklearn OK 1.8.0
```

Annotate-path grep found no `skimage`/`sklearn` import in `annotation_socket/annotator.py`, `annotation_socket/predicates`, `cnfa_algs/attributes.py`, `cnfa_algs/reliable_attrs.py`, `cnfa_algs/plan.py`, `cnfa_algs/space_syntax.py`, `cnfa_algs/setting_classifier.py`, `cnfa_algs/affordance.py`, or `cnfa_algs/geometry.py`, except comments in `attributes.py`. `scipy` remains on the annotate path and is installed here.

## Determinism / M1

Three repeated annotations of `Example Images/korridor.jpg` produced identical values:

```text
cnfa.fluency.spectral_slope_deviation: 0.7194
cnfa.fluency.grayscale_gabor_entropy_proxy: 0.7383
cnfa.fluency.local_congestion_proxy: 0.1071
cnfa.fluency.fractal_mid_d_band: 1.0
cnfa.fluency.symmetry_score_horizontal: 0.4261
```

All three runs matched exactly. `MODEL_VERSION` is:

```text
cnfa_algs-2026-07-18+seed1234+reliableA+reviewfix+codex2fix
```

## Emitted-Record Tier Audit

For the real records, all scored Reliable-A sprint primitives emit AMBER:

```text
cnfa.fluency.fractal_mid_d_band: AMBER
cnfa.fluency.spectral_slope_deviation: AMBER
cnfa.fluency.edge_orientation_entropy: AMBER
cnfa.geometry.contour_angularity: AMBER
cnfa.fluency.grayscale_gabor_entropy_proxy: AMBER
cnfa.fluency.local_congestion_proxy: AMBER
C01.triangulation_ignition: AMBER when scored
C29.stranded_amenity_index: AMBER when scored
```

On `BalancedCare`, C01 and C29 are UNKNOWN, not AMBER, due to `anchor_registration_unconfident`. That is why the required stage run has RED=1.

No residual GREEN was found among scored sprint primitives. Pre-existing GREEN image attributes still emit GREEN as expected.

## Still-Owed Integrity

The disposition still lists these as owed and does not silently mark them done:

1. Faithful V2/V6/V7 reimplementations or continued proxy status.
2. M1' sufficient-statistic replay.
3. Mac-sandbox exact replay.
4. Article_Eater grounding.
5. Labeled A-vs-B corpus for C01/C29 and V9 constants.
6. V13 true Grebenkina second-order.

## New Defects / Remaining Overclaims

1. F7 IQR guard introduces top-tail blindness. A sparse high-integration ridge can be erased if the middle quartiles are flat.

2. The required 3-image run does not reproduce RED=0. It returns AMBER=2, RED=1 because C01/C29 remain UNKNOWN on `BalancedCare`.

3. Minor stale documentation: `annotation_socket/predicates/fractal_band.py` docstring still says "rank 8.3, GREEN" and "ceiling GREEN", although the producer constant and emitted record are now AMBER.

## Final Call

The codex2fix disposition is an honest partial correction, not a complete correction. It no longer hides the prior V9/V2/V6/V7/SSIM bugs in emitted records, but it still overclaims a clean stage result and the rewritten F7 guard has a real tail-structure failure.

Severity ranking:

1. F7 top-tail ridge blindness.
2. Required stage run still RED=1.
3. Stale V9 GREEN wording in producer docstring.
