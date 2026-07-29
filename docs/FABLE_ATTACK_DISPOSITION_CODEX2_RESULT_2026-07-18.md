# FABLE ATTACK DISPOSITION RESULT - Codex 2

Date: 2026-07-18

Scope: Adversarial verification of `FABLE_REVIEW_DISPOSITION_RELIABLE_A_2026-07-17.md` against the prompt in `FABLE_ATTACK_THE_DISPOSITION_PROMPT_2026-07-17.md`.

## Executive Verdict

No. The disposition is not certifiable as written.

I treated this as a fresh adversarial review. I did not edit implementation files.

## Run Evidence

Literal command:

```bash
pytest annotation_socket/tests -q
```

Result: failed during collection with 4 errors:

- `ModuleNotFoundError: No module named 'annotation_socket'`
- `ModuleNotFoundError: No module named 'cnfa_algs'`

With the necessary import path:

```bash
PYTHONPATH=. pytest annotation_socket/tests -q
```

Result:

```text
16 passed in 0.78s
```

Stage command:

```bash
PYTHONPATH=. python3 -m annotation_socket.run_stage /tmp/attack_codex2_20260717 \
  'Example Images/BalancedCare-Render-Corridor2-wpeople1_960x530.webp' \
  'Example Images/korridor.jpg' \
  'Example Images/Industrial-open-concept-office-project-by-Decorilla-1024x819.jpeg'
```

Result:

```text
[controller] queue: 3 units
[worker] run1 processed=3 skipped=0
[checker] verdicts: GREEN=0 AMBER=0 RED=3
IndexError: list index out of range
```

The crash occurs at `annotation_socket/run_stage.py:90`, where the driver assumes at least one AMBER/GREEN record:

```python
base_uid = (gate["AMBER"] + gate["GREEN"])[0]
```

Real-image RED causes:

- `korridor.jpg`: scored `26/27`, unknown `1`: `cnfa.fluency.symmetry_score_horizontal compute_failed:ModuleNotFoundError`
- `Industrial-open-concept-office-project-by-Decorilla-1024x819.jpeg`: scored `26/27`, unknown `1`: same symmetry failure
- `BalancedCare-Render-Corridor2-wpeople1_960x530.webp`: scored `24/27`, unknown `3`: symmetry plus C01/C29 `anchor_registration_unconfident`

Manual negative control still works. Fabricated C8/C14 was RED with both `FABRICATION` problems detected.

## Per-Finding Verdicts

| Finding | Fix Claim | Verdict | Executed Evidence | Residual Risk |
|---|---|---|---|---|
| F1 V13 | Blank/low-edge images abstain | FIXED-CONFIRMED | blank `scalar=None`, `edge_px=0`; 40-edge line scored `0.2827`, not fake max entropy; real interiors had large edge counts | Still only first-neighbour second-order proxy |
| F2 V2 | FOV dropped, AMBER rename | STILL-BROKEN | `cnfa_algs/reliable_attrs.py:42` keeps `FOV_DEG=65.0`; emitted method says `FOV=65.0deg` at line 112; failure mode still says "absolute discomfort assumes FOV" at line 116 | Registry says no FOV, output says FOV |
| F3 V6 | Renamed proxy, AMBER | RELABEL-ONLY (still-misleading) | Key is now `cnfa.fluency.grayscale_gabor_entropy_proxy`; checkerboard still `0.0`; method still says "Rosenholtz 2007" at `reliable_attrs.py:267` | Registry is honest; emitted evidence is not honest enough |
| F4 V7 | Renamed proxy, AMBER | RELABEL-ONLY (still-misleading) | Key is now `cnfa.fluency.local_congestion_proxy`; method still says "Feature Congestion" at `reliable_attrs.py:301`; checkerboard `0.8844`, noise `0.7143` | Still looks like the published metric to consumers reading score evidence |
| F5 V9 | Demoted to AMBER | NEW-DEFECT-INTRODUCED | Registry says AMBER at `annotation_socket/registry.py:52`, but producer still has `TIER_HINT = "GREEN"` at `annotation_socket/predicates/fractal_band.py:29`. Real records emitted V9 `tier_hint GREEN` with score `1.0` | Gate uses registry, but the score record itself overclaims |
| F6 C29 | Seat proxy unchanged, AMBER disclosed | RELABEL-ONLY (honest) | Synthetic wall box with bottom 25% floor overlap still returns `seat_affordance01=0.25` from `stranded_amenity.py:42` | Honest but crude |
| F7 C01/C29 ridge | Raw-CV guard fixes degenerate ridge | NEW-DEFECT-INTRODUCED | CV sweep: `0.049` degenerate, `0.050` passes. Flat field plus one `1e6` outlier: CV `9.9489`, guard passes, ridge count `100/100`. Guard is at `triangulation.py:76`; ridge uses `>= p85` at `triangulation.py:95` | A clipped outlier can defeat the degeneracy guard |
| F8 V1 | Dead lens flag removed, AMBER | FIXED-CONFIRMED | No `lens_bow_flag` reference found; random noise still scores angular `0.2335`, but failure modes disclose object-contour and lens limits at `reliable_attrs.py:230` | Honest experimental statistic, not architectural valence |

## New Defects

1. Full `run_stage` no longer achieves the claimed `AMBER=3 RED=0`. It returns `RED=3` here because symmetry imports `skimage.metrics.ssim` at `cnfa_algs/attributes.py:50`, and `skimage` is absent in this environment.

2. `run_stage.py` crashes after all-RED output because it indexes `(gate["AMBER"] + gate["GREEN"])[0]` at `annotation_socket/run_stage.py:90`.

3. V9 tier demotion is split-brained: registry AMBER, emitted score GREEN.

4. F7 raw-CV guard is outlier-vulnerable. A single clipped cell can make a flat field look non-degenerate.

## Tier Audit

Registry audit: V1, V2, V6, V7, V9, V13, C01, and C29 are AMBER in `annotation_socket/registry.py`.

Emitted-score audit: V9 still emits GREEN from `annotation_socket/predicates/fractal_band.py:29`. That is the important contradiction.

## Final Call

The disposition is partly honest, but not complete. F1 and F8 are confirmed. F6 is honestly unchanged. F2, F3, F4, F5, and F7 still overclaim or introduce defects.

Highest-severity surviving issues:

1. F7 outlier ridge failure.
2. Full-stage RED/crash.
3. V9 emitted GREEN despite registry AMBER.
4. V2's continued FOV contradiction.

## Sources Refreshed

- Penacchio-Wilkins visual discomfort: https://openacchio.github.io/assets/pdf/visual%20discomfort%20and%20the%20spatial%20distribution%20of%20Fourier%20energy%20Penacchio%20Wilkins%20VR%202015.pdf
- Rosenholtz clutter: https://doi.org/10.1167/7.2.17
- Grebenkina edge entropy: https://livrepository.liverpool.ac.uk/3027759/1/GrebenkinaBrachmannBertaminiKaduhmRedies2018.pdf
- Field natural spectra: https://inc.ucsd.edu/~marni/Igert/Field_1987.pdf
