# CODEX S0/S2 VERIFY2 — commit 916bdb90

Verifier: Codex 2  
Repo: `/Users/davidusa/REPOS/Image_Tagger_dk_latest`  
HEAD: `916bdb909db0dbb51436aac95375565899cc097b`  
Time: `2026-07-19 03:38:28 PDT`  
Scope: verify fixes claimed in `docs/CODEX_S0S2_ATTACK_DISPOSITION_2026-07-19.md` against the five priority probes plus six-file test suite and three-image `run_stage`.

Important boundary: the checkout had unrelated dirty paths, but the S0/S2 disposition files inspected here (`annotation_socket/annotator.py`, `annotation_socket/derivation.py`, `annotation_socket/registry.py`, `annotation_socket/verify.py`, `cnfa_algs/street_noise.py`, `cnfa_algs/wave1_ops.py`) had no staged or unstaged diff from `916bdb90`.

## Verdict

**CONTESTED.** Four priority fixes pass as claimed, and the scoping notes are visible. The three-image stage-smoke row does **not** pass literally: actual output was `GREEN=0 AMBER=2 RED=1`, with the BalancedCare image RED because C01/C29 were `anchor_registration_unconfident`, leaving `34/36` applicable predicates scored. The disposition's global claim of `AMBER=3 RED=0, 36/36` is therefore false for this run.

## Evidence

### 1. Blank-wall unit

CMD:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 - <<'PY'
import json
from pathlib import Path
import numpy as np, cv2
from annotation_socket.annotator import annotate_image
from annotation_socket.verify import verify_record

root=Path('/tmp/codex_s0s2_verify2_probes')
root.mkdir(exist_ok=True)
blank=root/'blank_wall.png'
cv2.imwrite(str(blank), np.full((240,320,3), 128, np.uint8))
rec=annotate_image(str(blank))
tier, ev = verify_record(rec)
sa=[s for s in rec['scores'] if s.get('signal_absent')]
print('tier', tier)
print('coverage', rec['coverage'])
print('signal_absent_count', len(sa))
for s in sa:
    print(s['predicate'], s['status'], json.dumps(s.get('absence_evidence',{}), sort_keys=True), s.get('reason'))
print('problems', ev['problems'])
PY
```

OUT:

```text
tier AMBER
coverage {'applicable': 29, 'scored': 29, 'abstained': 26, 'unknown': 0, 'total_registry': 55}
signal_absent_count 7
cnfa.fluency.edge_orientation_entropy ABSTAINED {"edge_px": 0, "reason": "insufficient_edges"} orientation entropy undefined: <40 edge px (M1)
cnfa.geometry.contour_angularity ABSTAINED {"reason": "no_contour"} insufficient contour (M1)
cnfa.light.luminance_gradient_contrast ABSTAINED {"std_dn": 0.0} ABSTAIN: near-blank image (std<2DN)
cnfa.light.shadow_softness ABSTAINED {"n_candidates": 0, "n_rejected_material": 0} ABSTAIN: 0 accepted illumination edges < 25
cnfa.light.temperature_mismatch ABSTAINED {"mean_saturation": 0.0} ABSTAIN: mean saturation < 0.05 (chromaticity uninformative)
cnfa.material.texture_density ABSTAINED {"std_dn": 0.0} ABSTAIN: near-blank image
cnfa.geometry.orderliness_alignment ABSTAINED {"n_segments": 0} ABSTAIN: 0 segments < 20
problems []
```

VERDICT: **CONFIRMED.** Blank-wall unit is AMBER with exactly seven evidenced `signal_absent` abstentions.

### 2. Street-noise declared inputs

CMD:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 - <<'PY'
from annotation_socket.annotator import annotate_image
from annotation_socket.verify import verify_record

img='Example Images/korridor.jpg'
vals={'outdoor_leq':68.0,'facade_spec':{'facade_row':0,'Rp':33.0,'alpha':0.10}}
rec=annotate_image(img, frozenset({'outdoor_leq','facade_spec'}), input_values=vals)
tier, ev=verify_record(rec)
street=[s for s in rec['scores'] if s['predicate']=='cnfa.acoustic.street_noise_intrusion'][0]
print('with_values_tier', tier)
print('with_values_coverage', rec['coverage'])
print('with_values_street', street['status'], street.get('value'), street.get('extras',{}).get('L_rev_dBA'))
print('with_values_problems', ev['problems'])

rec2=annotate_image(img, frozenset({'outdoor_leq','facade_spec'}))
tier2, ev2=verify_record(rec2)
street2=[s for s in rec2['scores'] if s['predicate']=='cnfa.acoustic.street_noise_intrusion'][0]
print('tokens_without_values_tier', tier2)
print('tokens_without_values_street', street2['status'], street2.get('reason'))
print('tokens_without_values_problems', ev2['problems'])
PY
```

OUT:

```text
with_values_tier AMBER
with_values_coverage {'applicable': 37, 'scored': 37, 'abstained': 18, 'unknown': 0, 'total_registry': 55}
with_values_street SCORED 0.002 27.96
with_values_problems []
tokens_without_values_tier RED
tokens_without_values_street UNKNOWN declared_input_value_missing:outdoor_leq,facade_spec.facade_row,facade_spec.Rp
tokens_without_values_problems ['UNKNOWN:cnfa.acoustic.street_noise_intrusion reason=declared_input_value_missing:outdoor_leq,facade_spec.facade_row,facade_spec.Rp']
```

VERDICT: **CONFIRMED WITH CLARIFICATION.** Supplied values make street-noise `SCORED` and the unit AMBER. Tokens without values produce the required `UNKNOWN declared_input_value_missing:*`; because UNKNOWN is fail-closed, the verified unit tier is RED.

### 3. Strip all M1′ blocks

CMD:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 - <<'PY'
from annotation_socket.annotator import annotate_image
from annotation_socket.verify import verify_record

rec=annotate_image('Example Images/korridor.jpg')
for s in rec['scores']:
    s.pop('m1p', None)
tier, ev=verify_record(rec)
print('tier', tier)
print('missing_stats_count', sum('missing_stats' in p for p in ev['problems']))
for p in ev['problems'][:20]:
    print(p)
PY
```

OUT:

```text
tier RED
missing_stats_count 8
M1_PRIME:cnfa.light.brightness_variance:missing_stats
M1_PRIME:cnfa.fluency.edge_clarity_mean:missing_stats
M1_PRIME:cnfa.fluency.color_palette_entropy:missing_stats
M1_PRIME:cnfa.fluency.processing_load_proxy:missing_stats
M1_PRIME:cnfa.fractal_dimension:missing_stats
M1_PRIME:cnfa.fluency.spectral_slope_deviation:missing_stats
M1_PRIME:cnfa.fluency.edge_orientation_entropy:missing_stats
M1_PRIME:C1.visual_integration:missing_stats
```

VERDICT: **CONFIRMED.** Missing M1′ blocks fail as RED with `missing_stats`.

### 4. Shared M1′ loader

CMD:

```bash
rg -n "cv2\\.imread|resize\\(|load_for_m1p|from \\. import m1_prime|import m1_prime" annotation_socket/annotator.py annotation_socket/m1_prime.py
```

OUT:

```text
annotation_socket/annotator.py:64:    from . import m1_prime as MP
annotation_socket/annotator.py:65:    img = MP.load_for_m1p(image_path)   # SINGLE shared loader (Codex S0S2 MED-4: no inline duplicate)
annotation_socket/annotator.py:224:    from . import m1_prime as MP
annotation_socket/m1_prime.py:349:def load_for_m1p(image_path: str):
annotation_socket/m1_prime.py:355:    img = cv2.imread(image_path)
annotation_socket/m1_prime.py:360:        img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
```

VERDICT: **CONFIRMED.** Annotator uses `MP.load_for_m1p`; the inline `cv2.imread`/resize sequence is not in `annotator.py`.

### 5. Texture/orderliness/shadow scoping notes

CMD:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 - <<'PY'
import numpy as np, cv2, json
from annotation_socket import registry as R
from cnfa_algs.wave1_ops import orderliness_alignment, shadow_softness, texture_density

for pid in ['cnfa.material.texture_density','cnfa.geometry.orderliness_alignment','cnfa.light.shadow_softness']:
    print(pid, R.BY_ID[pid].get('note'))

H,W=240,320
img=np.full((H,W,3),255,np.uint8)
for y in range(20,220,10):
    cv2.line(img,(20,y),(300,y+8),(0,0,0),1)
for y in range(24,224,10):
    cv2.line(img,(20,y),(300,y),(0,0,0),1)
r=orderliness_alignment(img)
print('orderliness_extras', json.dumps(r.extras, sort_keys=True))

base=np.full((H,W),200.0); base[:,W//2:]=90.0
hard=np.clip(np.stack([base]*3,-1),0,255).astype(np.uint8)
r2=shadow_softness(hard)
print('shadow_failure_modes', r2.failure_modes)

periodic=np.full((H,W,3),128,np.uint8)
for x in range(0,W,8): periodic[:,x:x+2]=80
r3=texture_density(periodic)
print('texture_periodic', r3.scalar, r3.method, r3.extras, r3.failure_modes)
PY
```

OUT:

```text
cnfa.material.texture_density RESIDUAL micro-texture EXCLUDING structured/periodic pattern (wallpaper/ribbing read as structure and mask out — Codex S0S2 MED; periodic-texture stat is future work)
cnfa.geometry.orderliness_alignment LSD segment orientation order (segment-scale; V13 stays pixel-scale); abstains <20 segments
cnfa.light.shadow_softness penumbra 10-90% width over chromaticity-stable edges; hard flag in px; abstains <25 edges
orderliness_extras {"alignment_2mode": 1.0, "entropy_norm": 0.1931, "mode_bin_separation": 0, "mode_bins": [0, 0], "modes_adjacent": true, "n_segments": 200, "nbins": 36, "total_length_px": 15052.6}
shadow_failure_modes ['illumination/material separation is heuristic (AMBER)', 'defocus blur reads as soft shadow', 'requires >=25 accepted edges', 'colored-light boundaries (warm/cool illuminant change) are NOT separable from material edges in one photo (Codex S0S2 LOW) — single-photo limit']
texture_periodic None ABSTAIN: <20% of image left after structure removal {'structure_frac': 0.866} ['edge-dense scene: texture/structure inseparable']
```

VERDICT: **CONFIRMED.** Texture scope is explicit in the registry and periodic texture abstains as structure. Orderliness exposes `modes_adjacent` and `mode_bin_separation`. Shadow exposes the colored-light single-photo limit in `failure_modes`.

### Six Requested Test Files

CMD:

```bash
PYTHONPATH=. pytest annotation_socket/tests/test_m1_prime.py annotation_socket/tests/test_reliable_attrs.py annotation_socket/tests/test_v9_fractal_band.py annotation_socket/tests/test_c01_triangulation.py annotation_socket/tests/test_c29_stranded.py tests/test_spatial_syntax.py -q
```

OUT:

```text
....................................                                     [100%]
=============================== warnings summary ===============================
../../../../opt/homebrew/lib/python3.14/site-packages/_pytest/cacheprovider.py:475
  /opt/homebrew/lib/python3.14/site-packages/_pytest/cacheprovider.py:475: PytestCacheWarning: cache could not write path /Users/davidusa/REPOS/Image_Tagger_dk_latest/.pytest_cache/v/cache/nodeids: [Errno 1] Operation not permitted: '/Users/davidusa/REPOS/Image_Tagger_dk_latest/.pytest_cache/v/cache/nodeids'
    config.cache.set("cache/nodeids", sorted(self.cached_nodeids))

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
36 passed, 1 warning in 2.93s
```

VERDICT: **CONFIRMED.** The warning is a sandbox cache-write limitation, not a test failure.

### Three-Image run_stage

CMD:

```bash
PYTHONPATH=. python3 -m annotation_socket.run_stage /tmp/codex_s0s2_verify2_run_stage \
  'Example Images/korridor.jpg' \
  'Example Images/Industrial-open-concept-office-project-by-Decorilla-1024x819.jpeg' \
  'Example Images/BalancedCare-Render-Corridor2-wpeople1_960x530.webp'
```

OUT:

```text
[controller] queue: 3 units
[worker] run1 processed=3 skipped=0
[checker] verdicts: GREEN=0 AMBER=2 RED=1
  unit 8a0de3ceaf3979fa (Industrial-open-concept-office-project-b): tier=AMBER scored=36/36 applicable, abstained=19, unknown=0  amber_preds=27
    e.g. cnfa.light.brightness_variance=0.2474 <- region [747, 207, 750, 210] signal='local luminance SD, 31px window (M1)'
    e.g. C1.visual_integration=0.995 <- plan_chain grid=22ceaa8150fd2b78 upstream=4 steps
    e.g. ABSTAINED cnfa.acoustic.street_noise_intrusion missing=['facade_spec', 'outdoor_leq']
  unit e215663397ad8158 (korridor.jpg): tier=AMBER scored=36/36 applicable, abstained=19, unknown=0  amber_preds=27
    e.g. cnfa.light.brightness_variance=0.1277 <- region [640, 26, 643, 29] signal='local luminance SD, 31px window (M1)'
    e.g. C1.visual_integration=0.998 <- plan_chain grid=15e772c204446ef5 upstream=4 steps
    e.g. ABSTAINED cnfa.acoustic.street_noise_intrusion missing=['facade_spec', 'outdoor_leq']
[negative-control] seeded defaulted-C14 + constant-C8 -> tier=RED
    FABRICATION:C8.distraction_distance scored but requires ['acoustic_params'] absent from unit
    FABRICATION:C14.focus_collab_separation scored but requires ['collab_sources', 'focus_seats'] absent from unit
[negative-control] REJECTED (RED), absent from accepted/ — the score_layout bug cannot recur
[worker] run2 processed=0 skipped_content_addressed=3
[idempotency] second run: ZERO work, all units skipped by content address
[authority] worker write to control.jsonl DENIED (BoundaryError) — [W:] boundary holds
[authority] worker write to accepted/ DENIED (BoundaryError)

RUN/TEST RUBRIC: (a)+(b)+(c) demonstrated. AMBER units await the ≠-mind judge (not self-certified).
```

Additional rejected-unit inspection:

```text
unit 5f1341425485fa5a tier=RED n_scored=34
problems:
UNKNOWN:C01.triangulation_ignition reason=anchor_registration_unconfident
UNKNOWN:C29.stranded_amenity_index reason=anchor_registration_unconfident
image: Example Images/BalancedCare-Render-Corridor2-wpeople1_960x530.webp
```

VERDICT: **CONTESTED.** The literal expected result `AMBER=3 RED=0, 36/36` did not reproduce. Actual result is `AMBER=2 RED=1`; the failing unit is BalancedCare with C01/C29 UNKNOWN.

## Row-by-row disposition check

| Disposition row | Verify2 result |
|---|---|
| Street-noise UNKNOWN/RED with supplied inputs | **Confirmed with clarification.** Values supplied -> street-noise `SCORED`, unit AMBER. Tokens without values -> `UNKNOWN declared_input_value_missing:*`, verified unit RED by design. |
| Honest no-signal images go RED | **Confirmed.** Blank wall -> AMBER, seven evidenced `signal_absent`, no problems. |
| Missing M1′ demotes instead of failing | **Confirmed.** Stripped M1′ -> RED with `M1_PRIME:*:missing_stats`. |
| Loader duplicated annotator↔M1′ | **Confirmed.** Annotator calls shared `MP.load_for_m1p`; no inline `cv2.imread`/resize in annotator. |
| `texture_density` silently excludes periodic texture | **Confirmed.** Registry note says residual micro-texture excluding structured/periodic patterns; periodic stripes abstain as structure. |
| Adjacent-bimodal orderliness reads as two axes | **Confirmed.** Scored fixture exposes `modes_adjacent: true` and `mode_bin_separation`. |
| Colored-light shadow boundary accepted | **Confirmed as scoped disclosure.** Shadow result failure modes declare the colored-light single-photo limit. |
| A5 degenerate-regime inverted-U untested | **Not independently rerun in this pass.** This verify request specified five priority probes, six test files, and three-image `run_stage`; the street-noise supplied-input probe did run through the street-noise operator successfully. |
| Re-verification summary: all six tests pass, run_stage AMBER=3 RED=0, 36/36 | **Partly confirmed, partly contested.** Six test files pass `36 passed`; three-image `run_stage` is `AMBER=2 RED=1`, not `AMBER=3 RED=0`, because BalancedCare has C01/C29 UNKNOWN. |

## Final

Commit `916bdb90` materially fixes the five attacked S0/S2 surfaces under direct probes, but the disposition document overclaims the three-image stage smoke. The correct verify status is **CONTESTED**, not fully accepted, until BalancedCare either verifies C01/C29 or the expected smoke claim is narrowed.
