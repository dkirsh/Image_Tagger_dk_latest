# FABLE Disposition Attack Verdict - Reliable-A - Codex

Date: 2026-07-18
Repo: `/Users/davidusa/REPOS/Image_Tagger_dk_latest`
Prompt executed: `docs/FABLE_ATTACK_THE_DISPOSITION_PROMPT_2026-07-17.md`

## Executive Call

The disposition is mostly an honest correction, but it still overclaims in two places.

1. `cnfa_algs/hedonics.py` still consumes `cnfa.fluency.local_congestion_proxy` as a licensed hedonic signal. This conflicts with the disposition's own statement that V6/V7 are proxies and that nothing should be weighted into hedonics until faithful and calibrated.
2. `annotation_socket/predicates/fractal_band.py` still has a stale top docstring calling V9 "GREEN, Tier A" even though the registry and `TIER_HINT` now correctly say AMBER.

Core fixes F1, F2, F3, F6, F8 are confirmed. F7 is materially hardened against the outlier defect, but the ridge threshold still has a sharp boundary and should expose more raw-rank evidence. F4 and F5 need the overclaiming text/consumer path fixed before the disposition is clean.

## Required Run-First Evidence

Literal prompt command:

```text
pytest annotation_socket/tests -q
```

Result in this shell:

```text
4 errors during collection: ModuleNotFoundError for annotation_socket and cnfa_algs
```

The repo requires the root on `PYTHONPATH` in this shell. Re-run with the minimal repo-root import path:

```text
PYTHONPATH=. pytest annotation_socket/tests -q
```

Result:

```text
16 passed in 0.83s
```

Real-interior stage command:

```text
python3 -m annotation_socket.run_stage /tmp/attack \
  'Example Images/BalancedCare-Render-Corridor2-wpeople1_960x530.webp' \
  'Example Images/korridor.jpg' \
  'Example Images/Corridors_of_Classroom_Complex.jpg'
```

Result:

```text
[controller] queue: 3 units
[worker] run1 processed=3 skipped=0
[checker] verdicts: GREEN=0 AMBER=2 RED=1
[negative-control] seeded defaulted-C14 + constant-C8 -> tier=RED
[negative-control] REJECTED (RED), absent from accepted/ - the score_layout bug cannot recur
[worker] run2 processed=0 skipped_content_addressed=3
[idempotency] second run: ZERO work, all units skipped by content address
[authority] worker write to control.jsonl DENIED (BoundaryError)
[authority] worker write to accepted/ DENIED (BoundaryError)
```

The RED real unit appears to be from an applicable predicate becoming UNKNOWN/RED; the prompt asked for verdicts and negative-control behavior, not a repair of that real-image RED.

## Per-Finding Verdict Table

| Finding | Fix claim | Verdict | Executed evidence | Residual risk |
|---|---|---|---|---|
| F1 V13 blank -> abstain | `<40` edge px returns `scalar=None`; no uniform histogram | FIXED-CONFIRMED | Blank: `scalar=None`, `edge_px=0`, reason `insufficient_edges`. Boundary: 38 edge px abstains; 42 edge px scores `0.271`, then falls to `0.141` by 78 edge px. Real images had 360k-446k edge px; low-contrast versions still had 604k-661k edge px and did not abstain. | Threshold is arbitrary, but I did not find the old max-entropy bug above the threshold. |
| F2 V2 rename/demote | `spectral_slope_deviation`, AMBER, no FOV claim | RELABEL-ONLY (honest) | `rg` finds no `FOV_DEG` in the computed path. Stripe probe remains scale dependent: 128=`0.8344`, 256=`1.0`, 512=`0.9539`. Method says "PROXY, NOT the 2-D Penacchio-Wilkins discomfort metric; no angular calibration"; registry says AMBER and scale-dependent. | The number remains useful only as a proxy. The scale dependence is disclosed where consumers can see it. |
| F3 V6 proxy rename | socket id, annotator key, AttributeResult key all renamed to `grayscale_gabor_entropy_proxy`; AMBER | RELABEL-ONLY (honest) | Registry has new id and not old id; annotator maps new id; `AttributeResult.key` is `cnfa.fluency.grayscale_gabor_entropy_proxy`. One-pixel checkerboard still aliases to `0.0`; noise=`0.6541`. | Aliasing remains, but it is now a declared proxy, not a faithful Rosenholtz claim. |
| F4 V7 proxy rename | socket id, annotator key, AttributeResult key all renamed to `local_congestion_proxy`; AMBER | STILL-BROKEN | Registry/id/key are consistent and AMBER. But `cnfa_algs/hedonics.py` still registers `cnfa.fluency.local_congestion_proxy` as a licensed hedonic signal: response at `0.4` returns `value=1.0`, `licensed=true`, note "DESIGNATED hedonic clutter signal ... Replaces legacy processing_load_proxy for hedonics." | This contradicts the disposition's "nothing may be weighted into hedonics until faithful + calibrated." It is a consumed path, not merely a label. |
| F5 V9 demote | AMBER, R2 caveat, reads upstream fractal result | STILL-BROKEN, LOW-SEVERITY DOCUMENTATION | Registry and `TIER_HINT` are AMBER. `compute()` reads supplied fractal extras and returns UNKNOWN if extras are absent. But the file docstring still says "GREEN, Tier A" and "preferred/calming" at the top of `annotation_socket/predicates/fractal_band.py`. | Code behavior is fixed. The stale docstring violates "nothing in this sprint claims GREEN" and can mislead the next reviewer. |
| F6 C29 seat proxy | remains AMBER; wall/floor overlap disclosed | RELABEL-ONLY (honest) | Synthetic wall box overlapping bottom floor band gives `seat_affordance01=0.375`; registry says AMBER. | Failure mode is unchanged. It is disclosed, not repaired. |
| F7 C01/C29 ridge guard | raw integration robust spread, not compressed score; outlier defect fixed | FIXED-CONFIRMED with boundary risk | The code now uses `RIDGE_MIN_RELIQR=0.05` on raw Turner integration. Flat + one `1e6` outlier: degenerate `true`, ridge_count `0`. Near-flat + outlier also degenerate. Sweep: RELIQR `0.048` degenerate, `0.052` passes with ridge_count `50/100`. On `Corridors_of_Classroom_Complex.jpg`, C01 scored `0.1931`, anchor cell `[3,145]`, ridge_count `75/500`, dist `1.647m`, gate `0.6478`. | The outlier bug is fixed. The boundary remains sharp: a barely above-threshold two-valued field passes and makes half the cells ridge. Evidence should expose raw ridge set/rank, not only distance/gate. |
| F8 V1 dead flag removed/demoted | no `lens_bow_flag`; AMBER; honest note | FIXED-CONFIRMED | `rg` finds no residual computed `lens_bow_flag`. Random noise still gives a strong angular statistic: scalar `0.2166`, corner_density `0.6397`; failure modes explicitly say image-contour statistic, not validated architectural valence, and no lens intrinsics. | Object-contour confound remains, but is disclosed. |

## New Defects Or Surviving Overclaims

1. **V7 hedonic-consumer contradiction.** `local_congestion_proxy` is AMBER in the registry, but is still a licensed hedonic response in `cnfa_algs/hedonics.py`. Evidence:

```json
{
  "shape": "inverted_u",
  "evidence": "CONTESTED",
  "peak": 0.4,
  "licensed_response_at_0.4": {
    "value": 1.0,
    "licensed": true,
    "grade": "promising-import"
  }
}
```

2. **V9 stale GREEN docstring.** The registry and `TIER_HINT` are AMBER, but `annotation_socket/predicates/fractal_band.py` still describes V9 as "GREEN, Tier A" in the module docstring.

3. **F7 threshold boundary risk.** The outlier defect is fixed, but `RIDGE_MIN_RELIQR=0.05` creates a hard cliff: `0.048` fails closed; `0.052` passes and makes `50/100` cells ridge in a two-valued field. That may be acceptable as an engineering threshold, but it is not proven by the tests.

## Tier-Hint Audit

All Reliable-A sprint primitives and C01/C29 are AMBER:

```json
{
  "cnfa.fluency.fractal_mid_d_band": "AMBER",
  "cnfa.fluency.spectral_slope_deviation": "AMBER",
  "cnfa.fluency.edge_orientation_entropy": "AMBER",
  "cnfa.geometry.contour_angularity": "AMBER",
  "cnfa.fluency.grayscale_gabor_entropy_proxy": "AMBER",
  "cnfa.fluency.local_congestion_proxy": "AMBER",
  "C01.triangulation_ignition": "AMBER",
  "C29.stranded_amenity_index": "AMBER"
}
```

There are still 19 GREEN registry predicates, but they are not the Reliable-A sprint primitives under attack. Examples include `brightness_variance`, `edge_clarity`, `symmetry`, `palette_entropy`, `processing_load_proxy`, `fractal_dimension`, `glare-risk`, and several input-required plan predicates.

## Cross-Cutting Boundary Checks

### `MIN_EDGE_PX=40`

Probe with weak short lines:

```text
38 edge px -> abstain
42 edge px -> scalar 0.2711
50 edge px -> scalar 0.2053
58 edge px -> scalar 0.1811
78 edge px -> scalar 0.1410
```

This does not reproduce the old blank->maximum-entropy bug.

### `RIDGE_MIN_RELIQR=0.05`

```text
IQR/median 0.048 -> degenerate true, ridge_count 0
IQR/median 0.052 -> degenerate false, ridge_count 50/100
flat + one 1e6 outlier -> degenerate true, ridge_count 0
```

The old outlier problem is fixed. The near-threshold pass remains an engineering risk.

### `FC_K=40`

Noise sweep for `local_congestion_proxy`:

```text
sigma=0 -> 0.000025
sigma=2 -> 0.0718
sigma=5 -> 0.1589
sigma=10 -> 0.2731
sigma=20 -> 0.4271
sigma=40 -> 0.5906
sigma=80 -> 0.7102
```

The score is monotone with sensor noise/texture energy, which supports the disclosed "sensor noise/high ISO inflates contrast clutter" failure mode. It also reinforces that this should not yet be a licensed hedonic signal.

## M1 Prime And Owed-Items Integrity

M1 prime is not implemented. The verifier still replays scalar values; it does not replay sufficient statistics such as spectra, edge histograms, pyramid entropies, or raw feature-covariance summaries. The disposition correctly logs M1 prime as TODO.

The six owed items are still listed as owed in the disposition. I did not find a code path claiming Mac-to-sandbox replay, Article_Eater grounding, labeled-corpus calibration, or faithful V2/V6/V7 implementations as complete. The exception is practical rather than textual: `hedonics.py` still treats V7 as a licensed consumed signal despite the owed faithful/calibrated implementation.

## Ranked Surviving Issues

1. **High:** `local_congestion_proxy` remains consumed by `hedonics.py` as licensed hedonic output. This is the only direct consumed-path contradiction I found.
2. **Medium:** V9 code docstring still claims GREEN/Tier A despite AMBER behavior.
3. **Medium:** F7 ridge threshold has a sharp near-degenerate boundary and evidence does not expose enough raw rank/ridge diagnostics for future audit.
4. **Low:** The literal pytest command fails without `PYTHONPATH=.` in this shell; the suite itself passes once the repo root is on the import path.

## Final Call

The disposition is an honest correction in spirit, and most fixes withstand attack. It still overclaims in the V7 hedonic consumer path and in the stale V9 docstring. I would not certify the disposition as clean until those two are corrected. The core socket/registry demotions are otherwise substantially confirmed.
