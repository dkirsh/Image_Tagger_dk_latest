VERDICT: BROKEN

## Attack A: FALSE AGREEMENT

### A1: swapped same-kind aperture identities

Executed:

```sh
cd /Users/tanishqsingh/Documents/GitHub/Image_Tagger_dk_latest && PYTHONPATH=. python3 /tmp/codex_t12_attack_a.py
```

Exact target input:

```json
{"image_id":"codex-two-window-swap","objects":[],"openings":[{"bbox_xywh":[0.1,0.5,0.1,0.3],"kind":"window"},{"bbox_xywh":[0.9,0.5,0.1,0.3],"kind":"window"}],"primary_room_type":"reception"}
```

Exact rendered room input:

```json
{"apertures":[{"height_m":1.0,"id":"ap0","kind":"window","sill_m":1.0,"u_m":0.0,"wall":"east","width_m":1.0},{"height_m":1.0,"id":"ap1","kind":"window","sill_m":1.0,"u_m":0.0,"wall":"west","width_m":1.0}],"furniture":[],"geometry":{"ceiling_height_m":3.2,"depth_m":12.0,"floor_elevation_m":0.0,"wall_thickness_m":0.15,"width_m":8.0},"room":{"archetype":"gallery","id":"codex-two-window-swap","seed":1},"schema_version":"0.3"}
```

Why this render is wrong: frozen `reconstruct.py` emits aperture IDs as `ap{i}` in target opening order. Opening 0 has `cx=0.10`, so `ap0` should be west; opening 1 has `cx=0.90`, so `ap1` should be east. The packet swaps them.

Observed output:

```text
EXIT: 0
STDOUT: verdict BELOW_THRESHOLD score=0.0 opening_mismatches=0 sha256=a873f0a6373456dd63e07be1efef50eba3145fc6dcc8da541821e1e89d064e8b -> /var/folders/k7/mmnyfjh16vj74m2rfzds86pr0000gn/T/codex_t12_attack_a_cd2nm1j7/verdict/verdict.json
STDERR:
VERDICT_JSON: {"built_against":"render-verdict/v0.1","contract_version":"render-verdict/v0.1","discrepancy":{"calibration":"exploratory_uncalibrated","components":{"object_extra_frac":0.0,"object_missing_frac":0.0,"opening_wall_mismatch_frac":0.0},"score":0.0},"input_sha256":{"camera_json":"642d014a7711c16090343336644dc84bb879f71e3d36b1e29935a96d12d8d3d5","render_png":"61fc0e695552b58aa3e02fd12c7b3cab12987aa04878ecfd7723b3c6461aa5d1","room_json":"e4e67d95eda058b6e41595f41ae607e3af934b8695fa5fd3aff0304d90ee10e3"},"iter":0,"object_diff":{"extra_in_render":[],"matched":[],"missing_in_render":[],"moved":[]},"run_id":"codex-attack-a","target_image_id":"codex-two-window-swap","verdict":"BELOW_THRESHOLD","wall_layout_diff":{"extra_render_apertures":[],"opening_mismatches":[],"render_apertures":2,"target_openings":2}}
```

Result: SUCCEEDED. The comparator matches by `kind` plus wall multiset and ignores aperture identity/order, so a genuinely swapped render reports agreement: empty `opening_mismatches`, `score=0.0`, and `BELOW_THRESHOLD`.

### A2: extra aperture not counted in score

Executed:

```sh
cd /Users/tanishqsingh/Documents/GitHub/Image_Tagger_dk_latest && PYTHONPATH=. python3 /tmp/codex_t12_attack_a_extra.py
```

Exact target input:

```json
{"image_id":"codex-extra-aperture","objects":[],"openings":[{"bbox_xywh":[0.1,0.5,0.1,0.3],"kind":"window"}],"primary_room_type":"reception"}
```

Exact rendered room input:

```json
{"apertures":[{"id":"ap0","kind":"window","wall":"west"},{"id":"ap_extra","kind":"window","wall":"east"}],"furniture":[],"schema_version":"0.3"}
```

Observed output:

```text
EXIT: 0
STDOUT: verdict BELOW_THRESHOLD score=0.0 opening_mismatches=0 sha256=f99736ff25148747da79fdcb0cadd70f56a73430936f0d159abb962aa6a447a8 -> /var/folders/k7/mmnyfjh16vj74m2rfzds86pr0000gn/T/codex_t12_attack_a_extra_fkhsw8kl/verdict/verdict.json
STDERR:
VERDICT_JSON: {"built_against":"render-verdict/v0.1","contract_version":"render-verdict/v0.1","discrepancy":{"calibration":"exploratory_uncalibrated","components":{"object_extra_frac":0.0,"object_missing_frac":0.0,"opening_wall_mismatch_frac":0.0},"score":0.0},"input_sha256":{"camera_json":"642d014a7711c16090343336644dc84bb879f71e3d36b1e29935a96d12d8d3d5","render_png":"3986b5305a2e8b7ccb82765467a9858a77a5dec78b43d7ec3f766ca267d245ec","room_json":"deb6d716637fbcce16ade5da05ac38338dd3fa4520aa4019333836a8b47a1e48"},"iter":0,"object_diff":{"extra_in_render":[],"matched":[],"missing_in_render":[],"moved":[]},"run_id":"codex-attack-a-extra","target_image_id":"codex-extra-aperture","verdict":"BELOW_THRESHOLD","wall_layout_diff":{"extra_render_apertures":["window->east"],"opening_mismatches":[],"render_apertures":2,"target_openings":1}}
```

Result: SUCCEEDED. The render has an extra east window, so it does not match the target. The comparator records `extra_render_apertures` but leaves `score=0.0` and emits `BELOW_THRESHOLD` at threshold 0.0.

## Attack B: NONDETERMINISM

Executed:

```sh
cd /Users/tanishqsingh/Documents/GitHub/Image_Tagger_dk_latest && PYTHONPATH=. python3 /tmp/codex_t12_attack_b.py
```

Exact target input:

```json
{"image_id":"codex-nondeterminism","objects":[{"category":"chair"},{"category":"desk"}],"openings":[{"bbox_xywh":[0.86,0.5,0.26,0.92],"kind":"glazed_wall"},{"bbox_xywh":[0.5,0.55,0.06,0.35],"kind":"door"}],"primary_room_type":"reception"}
```

Exact rendered room input:

```json
{"apertures":[{"kind":"glazed_wall","wall":"north"},{"kind":"door","wall":"north"},{"kind":"window","wall":"west"}],"furniture":[{"category":"desk"},{"category":"plant"}],"schema_version":"0.3"}
```

Observed output:

```text
EXIT_1: 0
STDOUT_1: verdict CONTINUE score=0.5 opening_mismatches=1 sha256=eabc675a709f9144489d702f4bc18bb696f9feeb0798a897f097176036283435 -> /var/folders/k7/mmnyfjh16vj74m2rfzds86pr0000gn/T/codex_t12_attack_b_x7sui5rf/verdict1/verdict.json
EXIT_2: 0
STDOUT_2: verdict CONTINUE score=0.5 opening_mismatches=1 sha256=eabc675a709f9144489d702f4bc18bb696f9feeb0798a897f097176036283435 -> /var/folders/k7/mmnyfjh16vj74m2rfzds86pr0000gn/T/codex_t12_attack_b_x7sui5rf/verdict2/verdict.json
SHA256_1: eabc675a709f9144489d702f4bc18bb696f9feeb0798a897f097176036283435
SHA256_2: eabc675a709f9144489d702f4bc18bb696f9feeb0798a897f097176036283435
BYTES_EQUAL: True
```

Result: DID NOT SUCCEED. I did not find nondeterministic verdict bytes under this executed synthetic stress case.

## Findings C, D, E with severity

### C. Fail-closed crash cases - HIGH

Executed:

```sh
cd /Users/tanishqsingh/Documents/GitHub/Image_Tagger_dk_latest && PYTHONPATH=. python3 /tmp/codex_t12_attack_c.py
```

All cases below exited 1 with a Python traceback and no verdict file. They should be refused with exit code 2 if the fail-closed claim is true.

| Case | Exact malformed input | Observed final exception |
| --- | --- | --- |
| `packet_sha256_not_object` | packet `sha256`: `"not-an-object"` with target `{"image_id":"codex-crash","objects":[],"openings":[{"bbox_xywh":[0.5,0.5,0.2,0.2],"kind":"window"}]}` and room `{"apertures":[{"kind":"window","wall":"north"}],"furniture":[],"schema_version":"0.3"}` | `AttributeError: 'str' object has no attribute 'get'` at `load_packet`, line 98 |
| `target_openings_not_array` | target `{"image_id":"codex-crash","objects":[],"openings":{"kind":"window"}}` | `AttributeError: 'str' object has no attribute 'get'` at `compare`, line 136 |
| `target_bbox_bad_scalar` | target `{"image_id":"codex-crash","objects":[],"openings":[{"bbox_xywh":"bad","kind":"window"}]}` | `ValueError: could not convert string to float: 'b'` at `expected_wall`, line 51 |
| `room_apertures_not_array` | room `{"apertures":{"kind":"window","wall":"north"},"furniture":[],"schema_version":"0.3"}` | `AttributeError: 'str' object has no attribute 'get'` at `compare`, line 143 |
| `target_top_level_list_with_openings` | target `["openings"]` | `AttributeError: 'list' object has no attribute 'get'` at `compare`, line 132 |
| `target_opening_item_scalar` | target `{"image_id":"codex-crash","objects":[],"openings":["window"]}` | `AttributeError: 'str' object has no attribute 'get'` at `compare`, line 136 |
| `target_objects_not_array` | target `{"image_id":"codex-crash","objects":{"category":"chair"}}` | `AttributeError: 'str' object has no attribute 'get'` at `compare`, line 162 |
| `room_top_level_list` | room `["apertures"]` | `AttributeError: 'list' object has no attribute 'get'` at `compare`, line 133 |
| `room_aperture_item_scalar` | room `{"apertures":["window"],"furniture":[],"schema_version":"0.3"}` | `AttributeError: 'str' object has no attribute 'get'` at `compare`, line 143 |
| `room_furniture_not_array` | room `{"apertures":[{"kind":"window","wall":"north"}],"furniture":{"category":"chair"},"schema_version":"0.3"}` | `AttributeError: 'str' object has no attribute 'get'` at `compare`, line 164 |

Control: `room_json_not_utf8_control` exited 2 with `REFUSED: room.json unparseable: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte`, so that specific malformed input did not crash.

### D. Mirrored wall-rule divergence from `reconstruct.py` at `3fe1d505a64e69c76e110ff8630fdf31aa31197a` - HIGH

The comparator mirrors only `_wall_for(cx)` from frozen `reconstruct.py` line 73. It does not mirror the original assignment path around that line: `_center_x()` uses `bbox_xywh` only when it is a 4-item sequence with numeric `bb[0]` and `bb[2]`, falls back to `zone`, and otherwise defaults to `0.5` (frozen lines 64-69). `reconstruct_room()` also validates opening container/item types, skips non-structural kinds, and refuses out-of-range centers (frozen lines 122-137). Local `expected_wall()` just reads `float(bbox_xywh[0])` (`loop/run_loop_compare.py`, lines 50-52), and `compare()` uses `"unknown"` when bbox is absent (`loop/run_loop_compare.py`, lines 135-139).

Executed:

```sh
cd /Users/tanishqsingh/Documents/GitHub/Image_Tagger_dk_latest && PYTHONPATH=. python3 /tmp/codex_t12_attack_d.py
```

Observed divergences:

| Case | Exact target and room | Original expected behavior | Comparator observed output |
| --- | --- | --- | --- |
| `zone_right_without_bbox` | target `{"image_id":"zone-right","objects":[],"openings":[{"kind":"window","zone":"right"}]}`, room `{"apertures":[{"kind":"window","wall":"east"}],"furniture":[],"schema_version":"0.3"}` | east via `zone` fallback | exit 0, `score=0.333333`, mismatch `expected_wall:"unknown", rendered_wall:"east"` |
| `missing_bbox_no_zone` | target `{"image_id":"default-north","objects":[],"openings":[{"kind":"window"}]}`, room `{"apertures":[{"kind":"window","wall":"north"}],"furniture":[],"schema_version":"0.3"}` | north via default center `0.5` | exit 0, `score=0.333333`, mismatch `expected_wall:"unknown", rendered_wall:"north"` |
| `malformed_bbox_width_no_zone` | target `{"image_id":"bad-width","objects":[],"openings":[{"bbox_xywh":[0.9,0.5,"bad",0.2],"kind":"window"}]}`, room `{"apertures":[{"kind":"window","wall":"north"}],"furniture":[],"schema_version":"0.3"}` | north because original ignores bbox when `bb[2]` is nonnumeric and no zone exists | exit 0, `score=0.333333`, mismatch `expected_wall:"east", rendered_wall:"north"` |
| `out_of_range_center` | target `{"image_id":"bad-center","objects":[],"openings":[{"bbox_xywh":[1.5,0.5,0.2,0.2],"kind":"window"}]}`, room `{"apertures":[{"kind":"window","wall":"east"}],"furniture":[],"schema_version":"0.3"}` | refusal: `bad_center` | exit 0, `score=0.0`, `opening_mismatches=[]`, `verdict BELOW_THRESHOLD` |
| `nonstructural_kind_skipped` | target `{"image_id":"nonstructural","objects":[],"openings":[{"bbox_xywh":[0.1,0.5,0.2,0.2],"kind":"painting"}]}`, room `{"apertures":[],"furniture":[],"schema_version":"0.3"}` | skipped, not a structural aperture | exit 0, `score=0.333333`, mismatch `expected_wall:"west", rendered_wall:"MISSING"` |

### E. Tests whose names overclaim - MEDIUM

`test_wall_rule_matches_frozen_platform_rule` does not test the frozen platform rule. It only calls the local `rlc.expected_wall()` on hard-coded bbox values (`loop/tests/test_run_loop_compare.py`, lines 172-181). It never imports or executes `reconstruct.py` at commit `3fe1d505`, and it misses the original `_center_x()` fallback/refusal behavior that the comparator diverges from. Line 178 is also vacuous: `assert rlc.expected_wall([0.34, 0, 0, 0]) == "east" or True` always passes.

`test_wrong_wall_render_must_not_report_agreement` covers one unique-kind negative control only (`glazed_wall` east rendered north, lines 104-116). Its name and docstring claim to kill `false_agreement`, but it does not exercise duplicate same-kind openings, aperture IDs/order, or extra rendered apertures. Attack A1 and A2 pass through that gap.

`test_byte_identical_reruns` is narrower than its name suggests. It checks two in-process `rlc.run()` calls on the single good fixture (`loop/tests/test_run_loop_compare.py`, lines 134-142), not CLI invocations or malformed/order-stress inputs. I did not break determinism, but the test is not broad evidence for the byte-identical rerun claim.

Additional contract mismatch observed: section 5 of `docs/PHOTO_VR_LOOP_DECOMPOSITION_2026-08-15.md` says verdict `wall_layout_diff` contains `target_walls` and `render_walls` (lines 107-114), while `loop-verdict.schema.json` requires `target_openings`, `render_apertures`, `opening_mismatches`, and `extra_render_apertures` instead (lines 14-19). The implementation follows the schema, not the text contract.

Existing test execution:

```text
cd /Users/tanishqsingh/Documents/GitHub/Image_Tagger_dk_latest && PYTHONPATH=. python3 -m pytest loop/tests/test_run_loop_compare.py -v
-> exit 1: No module named pytest

cd /Users/tanishqsingh/Documents/GitHub/Image_Tagger_dk_latest && PYTHONPATH=. python3 loop/tests/test_run_loop_compare.py
-> exit 0: 8/8 passed
```

## What this review did NOT cover

This review used only synthetic fixtures written under `/tmp`; I did not test a real photo, a real Tagger scene graph, or a real first-cut render. I did not perform exhaustive fuzzing, visual image comparison, JSON Schema validation with an external validator, or end-to-end loop/HITL execution. I compared the wall rule against the frozen source text of `New_VR_Platform/src/vr_condition_audit/reconstruct.py` at `3fe1d505a64e69c76e110ff8630fdf31aa31197a`; I did not execute that package's full reconstruction pipeline.

## Identity and separation level

I am Codex, from OpenAI lineage, reviewing code written by Claude/Fable. This is therefore a different-lineage, non-author review.
