# CODEX ATTACK VERDICT — Sprint COMP-CORRECT S0+S2
### 2026-07-19 · Repo: `/Users/davidusa/REPOS/Image_Tagger_dk_latest` · Branch: `cnfa-algs-2026-07-14`

Role: adversarial verifier. Scope: commits `6e0050b9`, `66d6ec1e`; no batch files modified. Verdict: **CHANGES REQUIRED**. The pure cores mostly pass their stated tests, but the full socket is not yet correct for street-noise declared inputs, and the signal-undefined path can reject honest featureless images as RED rather than recording a legitimate abstention.

## Run-First Evidence

```text
CMD: PYTHONPATH=. python3 annotation_socket/tests/test_m1_prime.py
OUT: M1' TESTS PASSED
DETAIL: 5 audit classes roundtrip + tamper + diff-image OK; canon boundary OK; bindings OK; abstention path OK; scalar/stat verdicts OK.
```

```text
CMD: PYTHONPATH=. python3 annotation_socket/tests/test_c01_triangulation.py
OUT: ALL C01 CORE TESTS PASSED
CMD: PYTHONPATH=. python3 annotation_socket/tests/test_c29_stranded.py
OUT: ALL C29 CORE TESTS PASSED
CMD: PYTHONPATH=. python3 annotation_socket/tests/test_f7_ridge_boundary.py
OUT: F7 RIDGE BOUNDARY TESTS PASSED
CMD: PYTHONPATH=. python3 annotation_socket/tests/test_reliable_attrs.py
OUT: ALL RELIABLE-ATTR CORE TESTS PASSED (V2, V13, V1, V6, V7)
CMD: PYTHONPATH=. python3 annotation_socket/tests/test_v9_fractal_band.py
OUT: ALL V9 CORE TESTS PASSED
```

```text
CMD: PYTHONPATH=. python3 -m cnfa_algs.wave1_ops
OUT: wave1_ops self-test: PASS
CMD: PYTHONPATH=. python3 -m cnfa_algs.street_noise
OUT: street_noise self-test: PASS
```

```text
CMD: PYTHONPATH=. python3 -m annotation_socket.run_stage /tmp/codex_attack_s0s2 \
     'Example Images/korridor.jpg' \
     'Example Images/50-day-street-offices-norwalk-1200x1165-compact.jpg' \
     'Example Images/Industrial-open-concept-office-project-by-Decorilla-1024x819.jpeg'
OUT: checker verdicts: GREEN=0 AMBER=2 RED=1
OUT: AMBER units scored=36/36 applicable, abstained=19, unknown=0; street-noise abstained missing ['facade_spec', 'outdoor_leq'].
OUT: negative control defaulted-C14 + constant-C8 -> RED with both FABRICATION problems.
OUT: run2 processed=0 skipped_content_addressed=3.
VERDICT: smoke mostly passes, but the prompt's expected all-AMBER 36/36 outcome did not hold; one genuine image went RED.
```

## Findings

### HIGH — Street-noise is registered as applicable with declared inputs, but the annotator has no binding and emits UNKNOWN/RED

`annotation_socket/registry.py:108-110` declares `cnfa.acoustic.street_noise_intrusion` as requiring only `{"outdoor_leq", "facade_spec"}`. But `annotation_socket/annotator.py:144-186` has no `plan_fns`, `compound_fns`, or other binding for it. When those two inputs are supplied, the registry deems it applicable, and the worker falls to `UNKNOWN:no_binding_for_supplied_inputs`.

Evidence:

```text
CMD: PYTHONPATH=. python3 - <<'PY'
from annotation_socket.annotator import annotate_image
from annotation_socket.verify import verify_record
rec=annotate_image('Example Images/korridor.jpg', frozenset({'outdoor_leq','facade_spec'}))
print('coverage', rec['coverage'])
print([s for s in rec['scores'] if s['predicate']=='cnfa.acoustic.street_noise_intrusion'])
tier,ev=verify_record(rec,replay=True)
print('tier',tier)
print('problems',ev['problems'][:8])
PY
OUT:
coverage {'applicable': 37, 'scored': 36, 'abstained': 18, 'unknown': 1, 'total_registry': 55}
[{'predicate': 'cnfa.acoustic.street_noise_intrusion', 'status': 'UNKNOWN', 'reason': 'no_binding_for_supplied_inputs', 'value': None, 'evidence': None}]
tier RED
problems ['UNKNOWN:cnfa.acoustic.street_noise_intrusion reason=no_binding_for_supplied_inputs']
```

The pure function also needs more than the registry names: `street_noise_fields(pg, facade_row, Rp, alpha, outdoor_leq, ...)` at `cnfa_algs/street_noise.py:51-68` needs a facade row, per-column R' vector, and absorption map/scalar. A single `facade_spec` token may be acceptable as a bundle, but the binding must unpack it and fail closed when bundle members are missing. Current state: image-only units abstain correctly; supplied-input units go RED.

Recommendation: add an explicit annotator binding that reads a structured `facade_spec` bundle with `facade_row`, `Rp`, and `alpha`, or narrow the registry requirements to the exact declared input tokens. Add a full socket fixture with supplied street-noise inputs.

### HIGH — Legitimate signal-undefined Wave-1 cases become UNKNOWN, making the whole unit RED

`annotation_socket/annotator.py:171-176` converts any `AttributeResult.scalar is None` from image attributes into `UNKNOWN(signal_undefined:...)`. `verify.py` treats UNKNOWN as RED. On a blank/featureless image, several operators are legitimately undefined and explicitly say ABSTAIN in their method strings, but the socket still marks the unit RED.

Evidence:

```text
CMD: PYTHONPATH=. python3 - <<'PY'
import numpy as np, cv2
from annotation_socket.annotator import annotate_image
from annotation_socket.verify import verify_record
p='/tmp/cnfa_blank_wall_20260719.png'
cv2.imwrite(p, np.full((240,320,3), 128, np.uint8))
rec=annotate_image(p)
print('coverage', rec['coverage'])
tier,ev=verify_record(rec,replay=True)
print('tier',tier)
print('problems',ev['problems'][:10])
PY
OUT:
coverage {'applicable': 36, 'scored': 29, 'abstained': 19, 'unknown': 7, 'total_registry': 55}
tier RED
problems [
 'UNKNOWN:cnfa.fluency.edge_orientation_entropy reason=signal_undefined:orientation entropy undefined: <40 edge px (M1)',
 'UNKNOWN:cnfa.geometry.contour_angularity reason=signal_undefined:insufficient contour (M1)',
 'UNKNOWN:cnfa.light.luminance_gradient_contrast reason=signal_undefined:ABSTAIN: near-blank image (std<2DN)',
 'UNKNOWN:cnfa.light.shadow_softness reason=signal_undefined:ABSTAIN: 0 accepted illumination edges < 25',
 'UNKNOWN:cnfa.light.temperature_mismatch reason=signal_undefined:ABSTAIN: mean saturation < 0.05 (chromaticity uninformative)',
 'UNKNOWN:cnfa.material.texture_density reason=signal_undefined:ABSTAIN: near-blank image',
 'UNKNOWN:cnfa.geometry.orderliness_alignment reason=signal_undefined:ABSTAIN: 0 segments < 20'
]
```

This is too blunt. It is right that an applicable predicate must not silently vanish, but "no signal exists in this image" is not the same as "worker failed" or "fabricated nothing." A blank wall photo is a valid negative control for shadow, line-order, texture, contour, and orientation operators.

Recommendation: introduce a distinct result state or abstention subtype for `signal_absent` / `not_applicable_on_this_image`, with verifier rules requiring the algorithm-specific absence evidence. Keep compute failures and unbound predicates RED.

### MED — Missing M1′ blocks demote to AMBER rather than RED for bound predicates

`verify.py:120-127` treats a missing or failed M1′ block as AMBER for all currently bound predicates. That is consistent with the written compatibility rule, but it is not fail-closed. An attacker can strip all M1′ blocks from a legitimate AMBER record and receive the same overall tier as a record with complete M1′.

Evidence:

```text
CMD: PYTHONPATH=. python3 - <<'PY'
from annotation_socket.annotator import annotate_image
from annotation_socket.verify import verify_record
import copy
rec=annotate_image('Example Images/korridor.jpg')
print('orig m1p count', sum(1 for s in rec['scores'] if 'm1p' in s))
stripped=copy.deepcopy(rec)
for s in stripped['scores']:
    s.pop('m1p', None)
tier, ev=verify_record(stripped, replay=True)
print('stripped tier', tier)
print('stripped problems', ev['problems'][:5])
print('stripped amber includes bound', [p for p in ev['amber_predicates'] if p in ('cnfa.light.brightness_variance','cnfa.fluency.color_palette_entropy','cnfa.fractal_dimension')])
PY
OUT:
orig m1p count 5
stripped tier AMBER
stripped problems []
stripped amber includes bound ['cnfa.light.brightness_variance', 'cnfa.fluency.color_palette_entropy', 'cnfa.fractal_dimension']
```

It did **not** reach accepted:

```text
CMD: stripped-record run_checker stage
OUT: checker {'GREEN': [], 'AMBER': ['ae70d9cd6ff028f6'], 'RED': []}
OUT: accepted_units set()
```

So this is not an acceptance bypass today. It is still a downgrade in audit strength: the presence of M1′ does not affect the final tier whenever the unit is already AMBER for other reasons. Recommendation: for new M1′-bound predicates after the compatibility window, missing M1′ should be RED, or the verdict should carry an explicit `M1P_MISSING` gate separate from ordinary AMBER.

### MED — M1′ loader is not actually shared by the annotator, despite the comment saying it is

`m1_prime.py:276-289` defines `load_for_m1p()` and says it is "EXACTLY the annotator's load+resize pipeline." But the annotator duplicates the same `cv2.imread` and resize sequence inline at `annotation_socket/annotator.py:63-68` instead of calling the shared loader. This is a drift hazard: a future resize/interpolation/color-loading change in one place can create either false M1′ failures or silent production/checker disagreement.

Evidence:

```text
annotation_socket/annotator.py:63-68
img = cv2.imread(image_path)
scale = 900 / max(img.shape[:2])
if scale < 1:
    img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

annotation_socket/m1_prime.py:282-289
img = cv2.imread(image_path)
scale = 900 / max(img.shape[:2])
if scale < 1:
    img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
```

Recommendation: make `annotate_image()` call `MP.load_for_m1p()` for the image bytes, or move the shared loader to a neutral module used by both annotator and M1′. Add a test that monkeypatches one path and proves drift is caught.

### MED — `texture_density` masks periodic wallpaper-like texture as "structure" and abstains

The method string says "micro-texture after structure removal", and the code masks Canny edges dilated by 7 px (`cnfa_algs/wave1_ops.py:397-400`). On a periodic stripe/wallpaper-like synthetic texture, nearly the whole image is treated as structure, so the operator abstains rather than reporting high texture density.

Evidence:

```text
CMD: periodic 8px sinusoidal wallpaper probe
OUT: texture_periodic scalar None method ABSTAIN: <20% of image left after structure removal extras {'structure_frac': 0.997}
```

This may be defensible if the operator explicitly excludes structured pattern, but the candidate `v2a_088 texture density` is likely expected to include wallpaper, ribbing, textile weave, and fine periodic finishes. Recommendation: either rename/scope it to "residual microtexture excluding structured pattern", or add a second pattern-texture statistic for periodic architectural textures.

### LOW — Adjacent-bimodal orderliness can report perfect two-mode alignment

`orderliness_alignment()` zeroes +/-2 bins around the first dominant mode before selecting the second mode (`cnfa_algs/wave1_ops.py:445-449`). In an adjacent-bimodal line field, it selected adjacent bins `[1, 0]` and reported `alignment_2mode=1.0`.

Evidence:

```text
CMD: adjacent 0°/10° line-field probe
OUT: order_adjacent_modes scalar 0.6563411104451666 extras {'n_segments': 203, 'alignment_2mode': 1.0, 'entropy_norm': 0.3437, 'nbins': 36, 'mode_bins': [1, 0], 'total_length_px': 10096.8}
```

This is not a catastrophic bug: the scene is ordered. But "two-mode alignment" may imply two distinct axes, not one broadened axis. Recommendation: report whether the two modes are separated by a minimum angular distance, or rename the field to "dominant-axis coverage" when modes are adjacent.

### LOW — Shadow chromaticity heuristic accepts a colored boundary as illumination

The shadow operator says it uses chromaticity-stable luminance edges to separate illumination from material edges. A synthetic colored-light/luminance boundary was accepted as hard shadow with `n_rejected_material=0`.

Evidence:

```text
CMD: colored boundary probe
OUT: shadow_colored_boundary scalar 0.02439024390243903
OUT: extras {'penumbra_frac_diag': 0.005, 'n_edges': 480, 'n_rejected_material': 0, 'daylight_hard': True, ...}
```

This is a small adequacy warning, not a proof of failure. Warm/cool illumination changes are genuinely hard to distinguish from colored material from one photo. The AMBER tier is appropriate. Recommendation: add a colored-light/material-edge negative-control set and expose rejected/accepted chromaticity-edge counts in smoke reports.

## Surfaces That Held

### A1 — Different-image M1′ stats and forged digest tampering are caught

```text
CMD: copy M1′ blocks from korridor.jpg and replay against Industrial-open-concept-office image
OUT:
luminance_field stats_mismatch False True
radial_fft stats_mismatch False True
orientation_hist stats_mismatch False True
box_count stats_mismatch False True
color_palette stats_mismatch False True
```

Color-palette entropy tamper of `+0.05` is catchable:

```text
CMD: mutate color_palette entropy_norm and forge digest
OUT:
delta 0.05 base 0.9047 claimed 0.9547 verdict stats_mismatch fresh==claimed False
```

The stored color centers are rounded to 1 decimal and proportions to 3 decimals before digesting, so un-emitted sub-rounding drift is invisible by design; a 0.05 entropy shift is not invisible.

### A3 — Calibration honesty is mostly visible

The registry and methods declare AMBER status. The validation doc explicitly says the Wave-1 constants were calibrated on the 9-interior smoke and must be refit on the corpus:

```text
docs/CNFA_VALIDATION_METHODOLOGY_2026-07-19.md:
Wave-1 constants calibrated tonight on the 9-interior smoke (W1.1 fullscale=60, W1.2 ramp=0.045,
W1.6 per-pool cap=2% + soft-sat) are declared ENGINEERING calibrations and must be re-fit on the corpus.
```

No finding here beyond making sure corpus refits update tests instead of freezing smoke constants as science.

### A5 — Street-noise pure core states its AMBER physics limits

The pure function and spec declare single-zone Sabine, flat diffraction, A-weighted broadband, and engineering comfort constants. The issue is not the pure-core honesty; it is the socket binding and input contract mismatch described above.

A degenerate quiet configuration showed that huddle can collapse to zero everywhere:

```text
CMD: Rp=80 dB, Leq=45 dBA, alpha=.95 toy room
OUT: range -37.78 -26.38 best [1, 1] 0.0
```

The current invariant test exercises one normal operating band; it does not prove the inverted-U is meaningful across degenerate bands. That is acceptable for AMBER if documented, but construct tests should include too-quiet and too-loud regimes.

### A6 — V7 hedonic delicensing holds in HEAD and working tree

```text
CMD: git show HEAD:cnfa_algs/hedonics.py | grep -c "DESIGNATED hedonic"
OUT: 0
CMD: grep -c "DESIGNATED hedonic" cnfa_algs/hedonics.py
OUT: 0
CMD: git diff -- cnfa_algs/hedonics.py
OUT: no diff
CMD: PYTHONPATH=. python3 - <<'PY'
from cnfa_algs.hedonics import hedonic_response
for key in ['cnfa.fluency.local_congestion_proxy','cnfa.fluency.grayscale_gabor_entropy_proxy','cnfa.fluency.processing_load_proxy']:
    print(key, hedonic_response(key,0.5))
PY
OUT:
cnfa.fluency.local_congestion_proxy {'value': None, 'licensed': False, 'shape': 'unregistered', ...}
cnfa.fluency.grayscale_gabor_entropy_proxy {'value': None, 'licensed': False, 'shape': 'unregistered', ...}
cnfa.fluency.processing_load_proxy {'value': 0.833333333888889, 'licensed': True, 'shape': 'inverted_u', ... 'V6/V7 are AMBER proxies, NOT licensed here.'}
```

## Final Verdict

**CHANGES REQUIRED before this batch should be called full-socket correct.**

Priority fixes:

1. Add the street-noise annotator binding or change the registry contract so supplied declared inputs do not produce UNKNOWN/RED.
2. Resolve `signal_undefined` semantics so honest no-signal cases can be audited without poisoning the whole unit as RED.
3. Stop duplicating the image loader between annotator and M1′.
4. Decide whether missing M1′ remains AMBER only during a migration window, and encode the stricter post-migration gate.
5. Clarify or split `texture_density` so periodic architectural texture is not silently excluded from a candidate named "texture density."
