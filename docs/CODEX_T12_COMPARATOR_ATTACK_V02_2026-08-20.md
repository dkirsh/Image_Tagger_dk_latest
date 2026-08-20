VERDICT: BROKEN

## 2. Regression results for A1 and A2

Executed:

```sh
cd /Users/tanishqsingh/Documents/GitHub/Image_Tagger_dk_latest && PYTHONPATH=. python3 /tmp/codex_v02_regression.py
```

### A1: swapped same-kind aperture identities

Exact target input:

```json
{"image_id":"codex-two-window-swap-v02","objects":[],"openings":[{"bbox_xywh":[0.1,0.5,0.1,0.3],"kind":"window"},{"bbox_xywh":[0.9,0.5,0.1,0.3],"kind":"window"}],"primary_room_type":"reception"}
```

Exact rendered room input:

```json
{"apertures":[{"height_m":1.0,"id":"ap0","kind":"window","sill_m":1.0,"u_m":0.0,"wall":"east","width_m":1.0},{"height_m":1.0,"id":"ap1","kind":"window","sill_m":1.0,"u_m":0.0,"wall":"west","width_m":1.0}],"furniture":[],"schema_version":"0.3"}
```

Observed output:

```text
EXIT: 0
STDOUT: verdict CONTINUE score=0.25 opening_mismatches=2 extra_apertures=0 identity=exact sha256=9064015a443e5d489e770672db5f6eef98bb4a15b11ecb522381c0d73927e825 -> /tmp/codex_v02_regression_A1_swapped_same_kind_ap_ids_00be1o1n/verdict/verdict.json
STDERR:
VERDICT_JSON: {"built_against":"render-verdict/v0.2","contract_version":"render-verdict/v0.2","discrepancy":{"calibration":"exploratory_uncalibrated","components":{"extra_aperture_frac":0.0,"object_extra_frac":0.0,"object_missing_frac":0.0,"opening_wall_mismatch_frac":1.0},"score":0.25},"identity":{"mode":"exact","unverifiable_kinds":[]},"input_sha256":{"camera_json":"b1d3102fbc2e51cddaa718cc415c867b449999ddc83198ab8bf6b5aee4707875","render_png":"a32cd5a504708a94b5aa9ff343649b1873350fc06ad9691e757ed6f8fa44377b","room_json":"921e272ab651dafbd2bcd6beb954fbc3c42b36d730b136ecb0f4033ef9af621b"},"iter":0,"object_diff":{"extra_in_render":[],"matched":[],"missing_in_render":[],"moved":[]},"run_id":"codex-v02-A1_swapped_same_kind_ap_ids","target_image_id":"codex-two-window-swap-v02","verdict":"CONTINUE","wall_layout_diff":{"extra_render_apertures":[],"opening_mismatches":[{"expected_kind":"window","expected_wall":"west","opening_id":"target_opening_0_window","rendered_kind":"window","rendered_wall":"east"},{"expected_kind":"window","expected_wall":"east","opening_id":"target_opening_1_window","rendered_kind":"window","rendered_wall":"west"}],"render_apertures":2,"target_openings":2}}
```

Result: the v0.1 A1 false agreement no longer succeeds. v0.2 detects both swapped apertures and returns `CONTINUE`.

### A2: invented extra aperture

Exact target input:

```json
{"image_id":"codex-extra-aperture-v02","objects":[],"openings":[{"bbox_xywh":[0.1,0.5,0.1,0.3],"kind":"window"}],"primary_room_type":"reception"}
```

Exact rendered room input:

```json
{"apertures":[{"id":"ap0","kind":"window","wall":"west"},{"id":"ap_extra","kind":"window","wall":"east"}],"furniture":[],"schema_version":"0.3"}
```

Observed output:

```text
EXIT: 0
STDOUT: verdict CONTINUE score=0.125 opening_mismatches=0 extra_apertures=1 identity=multiset_fallback sha256=2d3ae3ed74fa8cdac349cdc658324ee109bdcb532fc7a04b04ac308a1ace1ddb -> /tmp/codex_v02_regression_A2_extra_aperture_malformed_extra_id_s6sw7p6i/verdict/verdict.json
STDERR:
VERDICT_JSON: {"built_against":"render-verdict/v0.2","contract_version":"render-verdict/v0.2","discrepancy":{"calibration":"exploratory_uncalibrated","components":{"extra_aperture_frac":0.5,"object_extra_frac":0.0,"object_missing_frac":0.0,"opening_wall_mismatch_frac":0.0},"score":0.125},"identity":{"mode":"multiset_fallback","unverifiable_kinds":[]},"input_sha256":{"camera_json":"b1d3102fbc2e51cddaa718cc415c867b449999ddc83198ab8bf6b5aee4707875","render_png":"a32cd5a504708a94b5aa9ff343649b1873350fc06ad9691e757ed6f8fa44377b","room_json":"caa167a88f605bd0041a47813e39d9e1f7e64b0fc296919f95fe6b73e48424e3"},"iter":0,"object_diff":{"extra_in_render":[],"matched":[],"missing_in_render":[],"moved":[]},"run_id":"codex-v02-A2_extra_aperture_malformed_extra_id","target_image_id":"codex-extra-aperture-v02","verdict":"CONTINUE","wall_layout_diff":{"extra_render_apertures":["window->east"],"opening_mismatches":[],"render_apertures":2,"target_openings":1}}
```

Result: the v0.1 A2 false agreement no longer succeeds. The extra aperture now costs `extra_aperture_frac=0.5` and the verdict is `CONTINUE`.

## 3. Malformed sweep results

Executed:

```sh
cd /Users/tanishqsingh/Documents/GitHub/Image_Tagger_dk_latest && PYTHONPATH=. python3 /tmp/codex_v02_malformed.py
```

No case produced a Python traceback. Nine of the ten old crash cases refused with exit 2. One old crash case, `target_bbox_bad_scalar`, now exits 0 because v0.2 mirrors the platform's malformed-bbox fallback path.

| Case | Exact input | Exit code observed | Observed output |
| --- | --- | ---: | --- |
| `packet_sha256_not_object` | target `{"image_id":"codex-crash-v02","objects":[],"openings":[{"bbox_xywh":[0.5,0.5,0.2,0.2],"kind":"window"}]}` room `{"apertures":[{"id":"ap0","kind":"window","wall":"north"}],"furniture":[],"schema_version":"0.3"}` manifest override `{"sha256":"not-an-object"}` | 2 | `STDERR: REFUSED: packet.json sha256 must be an object of name->hex digest`; verdict absent |
| `target_openings_not_array` | target `{"image_id":"codex-crash-v02","objects":[],"openings":{"kind":"window"}}` room `{"apertures":[{"id":"ap0","kind":"window","wall":"north"}],"furniture":[],"schema_version":"0.3"}` | 2 | `STDERR: REFUSED: target scene openings must be a list of objects`; verdict absent |
| `target_bbox_bad_scalar` | target `{"image_id":"codex-crash-v02","objects":[],"openings":[{"bbox_xywh":"bad","kind":"window"}]}` room `{"apertures":[{"id":"ap0","kind":"window","wall":"north"}],"furniture":[],"schema_version":"0.3"}` | 0 | `STDOUT: verdict BELOW_THRESHOLD score=0.0 opening_mismatches=0 extra_apertures=0 identity=exact sha256=77effa332f10363ecd0de1261ffe46270ff0fa44a09cbe203e94df5c57e1b939 -> /tmp/codex_v02_malformed_target_bbox_bad_scalar_bbnr45n8/verdict/verdict.json` |
| `room_apertures_not_array` | target `{"image_id":"codex-crash-v02","objects":[],"openings":[{"bbox_xywh":[0.5,0.5,0.2,0.2],"kind":"window"}]}` room `{"apertures":{"kind":"window","wall":"north"},"furniture":[],"schema_version":"0.3"}` | 2 | `STDERR: REFUSED: room.json apertures must be a list of objects`; verdict absent |
| `target_top_level_list_with_openings` | target `["openings"]` room `{"apertures":[{"id":"ap0","kind":"window","wall":"north"}],"furniture":[],"schema_version":"0.3"}` | 2 | `STDERR: REFUSED: target scene must be a JSON object`; verdict absent |
| `target_opening_item_scalar` | target `{"image_id":"codex-crash-v02","objects":[],"openings":["window"]}` room `{"apertures":[{"id":"ap0","kind":"window","wall":"north"}],"furniture":[],"schema_version":"0.3"}` | 2 | `STDERR: REFUSED: target scene openings must be a list of objects`; verdict absent |
| `target_objects_not_array` | target `{"image_id":"codex-crash-v02","objects":{"category":"chair"}}` room `{"apertures":[{"id":"ap0","kind":"window","wall":"north"}],"furniture":[],"schema_version":"0.3"}` | 2 | `STDERR: REFUSED: target scene objects must be a list of objects`; verdict absent |
| `room_top_level_list` | target `{"image_id":"codex-crash-v02","objects":[],"openings":[{"bbox_xywh":[0.5,0.5,0.2,0.2],"kind":"window"}]}` room `["apertures"]` | 2 | `STDERR: REFUSED: room.json must be a JSON object`; verdict absent |
| `room_aperture_item_scalar` | target `{"image_id":"codex-crash-v02","objects":[],"openings":[{"bbox_xywh":[0.5,0.5,0.2,0.2],"kind":"window"}]}` room `{"apertures":["window"],"furniture":[],"schema_version":"0.3"}` | 2 | `STDERR: REFUSED: room.json apertures must be a list of objects`; verdict absent |
| `room_furniture_not_array` | target `{"image_id":"codex-crash-v02","objects":[],"openings":[{"bbox_xywh":[0.5,0.5,0.2,0.2],"kind":"window"}]}` room `{"apertures":[{"id":"ap0","kind":"window","wall":"north"}],"furniture":{"category":"chair"},"schema_version":"0.3"}` | 2 | `STDERR: REFUSED: room.json furniture must be a list of objects`; verdict absent |

## 4. Identity fallback path

Executed:

```sh
cd /Users/tanishqsingh/Documents/GitHub/Image_Tagger_dk_latest && PYTHONPATH=. python3 /tmp/codex_v02_identity.py
```

Finding: the prime claim does not hold as stated. In `multiset_fallback`, v0.2 can still return `BELOW_THRESHOLD` whenever `unverifiable_kinds` is empty. That happened with all ids absent, mixed present/missing ids, negative ids, and non-`ap<i>` ids. This is not the old A1 same-kind false agreement, but it is agreement without platform aperture identity.

| Attack | Exact input | Exact observed output |
| --- | --- | --- |
| `fallback_single_opening_no_id_below_threshold` | target `{"image_id":"identity-one-window","objects":[],"openings":[{"bbox_xywh":[0.1,0.5,0.1,0.3],"kind":"window"}]}` room `{"apertures":[{"kind":"window","wall":"west"}],"furniture":[],"schema_version":"0.3"}` | `EXIT: 0`; `STDOUT: verdict BELOW_THRESHOLD score=0.0 opening_mismatches=0 extra_apertures=0 identity=multiset_fallback sha256=c2da3b25cd056e8cbb3138b2ee409b579fd031f9153fad9e35d5c695ba8607ba -> /tmp/codex_v02_identity_fallback_single_opening_no_id_below_threshold_pxb22mwg/verdict/verdict.json`; verdict `{"identity":{"mode":"multiset_fallback","unverifiable_kinds":[]},"verdict":"BELOW_THRESHOLD","wall_layout_diff":{"opening_mismatches":[],"extra_render_apertures":[],"render_apertures":1,"target_openings":1},"discrepancy":{"score":0.0}}` |
| `fallback_a1_no_ids_empty_mismatches_continue` | target `{"image_id":"identity-two-windows","objects":[],"openings":[{"bbox_xywh":[0.1,0.5,0.1,0.3],"kind":"window"},{"bbox_xywh":[0.9,0.5,0.1,0.3],"kind":"window"}]}` room `{"apertures":[{"kind":"window","wall":"east"},{"kind":"window","wall":"west"}],"furniture":[],"schema_version":"0.3"}` | `EXIT: 0`; `STDOUT: verdict CONTINUE score=0.0 opening_mismatches=0 extra_apertures=0 identity=multiset_fallback sha256=9ac23a0dd161203041585885e8e5e2b0656ac8edcdf95285f74b90c72dc5cd0e -> /tmp/codex_v02_identity_fallback_a1_no_ids_empty_mismatches_continue_c7s0ixpz/verdict/verdict.json`; verdict has `unverifiable_kinds:["window"]`, empty mismatches, and `CONTINUE` |
| `fallback_multiple_ambiguous_kinds_listed` | target `{"image_id":"identity-two-doors-two-windows","objects":[],"openings":[{"bbox_xywh":[0.1,0.5,0.1,0.3],"kind":"window"},{"bbox_xywh":[0.5,0.5,0.1,0.3],"kind":"door"},{"bbox_xywh":[0.9,0.5,0.1,0.3],"kind":"window"},{"bbox_xywh":[0.5,0.6,0.1,0.3],"kind":"door"}]}` room `{"apertures":[{"kind":"window","wall":"east"},{"kind":"door","wall":"north"},{"kind":"window","wall":"west"},{"kind":"door","wall":"north"}],"furniture":[],"schema_version":"0.3"}` | `EXIT: 0`; `STDOUT: verdict CONTINUE score=0.0 opening_mismatches=0 extra_apertures=0 identity=multiset_fallback sha256=8acf2dd1d33e79c68e0e3e54de55a4cc3a24dd8c8f6abed26efadb8216f7e48b -> /tmp/codex_v02_identity_fallback_multiple_ambiguous_kinds_listed_xler4tf0/verdict/verdict.json`; both `door` and `window` appear in `unverifiable_kinds` |
| `malformed_negative_id_fallback` | target `{"image_id":"identity-one-window","objects":[],"openings":[{"bbox_xywh":[0.1,0.5,0.1,0.3],"kind":"window"}]}` room `{"apertures":[{"id":"ap-1","kind":"window","wall":"west"}],"furniture":[],"schema_version":"0.3"}` | `EXIT: 0`; `STDOUT: verdict BELOW_THRESHOLD score=0.0 opening_mismatches=0 extra_apertures=0 identity=multiset_fallback sha256=62ab004dd63e7e4785af3e8459e6c84a0384ad30d97979fd5fc8047313704e06 -> /tmp/codex_v02_identity_malformed_negative_id_fallback_ln3g0_du/verdict/verdict.json`; malformed id did not refuse and still agreed |
| `malformed_not_ap_form_fallback` | target `{"image_id":"identity-one-window","objects":[],"openings":[{"bbox_xywh":[0.1,0.5,0.1,0.3],"kind":"window"}]}` room `{"apertures":[{"id":"door0","kind":"window","wall":"west"}],"furniture":[],"schema_version":"0.3"}` | `EXIT: 0`; `STDOUT: verdict BELOW_THRESHOLD score=0.0 opening_mismatches=0 extra_apertures=0 identity=multiset_fallback sha256=83d3cef87bb18348b01256834a1aa3f59ee1149c7068c470d9d34fc8533ed65c -> /tmp/codex_v02_identity_malformed_not_ap_form_fallback_6gg_tk14/verdict/verdict.json`; malformed id did not refuse and still agreed |
| `mixed_some_ids_some_missing_fallback` | target `{"image_id":"identity-two-windows","objects":[],"openings":[{"bbox_xywh":[0.1,0.5,0.1,0.3],"kind":"window"},{"bbox_xywh":[0.9,0.5,0.1,0.3],"kind":"window"}]}` room `{"apertures":[{"id":"ap0","kind":"window","wall":"west"},{"kind":"window","wall":"east"}],"furniture":[],"schema_version":"0.3"}` | `EXIT: 0`; `STDOUT: verdict CONTINUE score=0.0 opening_mismatches=0 extra_apertures=0 identity=multiset_fallback sha256=e6b391ce4f6d728c81d6dc9ef42491fef2e0b97625ca04d8523f706609edf18d -> /tmp/codex_v02_identity_mixed_some_ids_some_missing_fallback_ojrd3uft/verdict/verdict.json`; `unverifiable_kinds:["window"]`; no `BELOW_THRESHOLD` |
| `mixed_unique_kinds_some_ids_below_threshold` | target `{"image_id":"identity-window-door","objects":[],"openings":[{"bbox_xywh":[0.1,0.5,0.1,0.3],"kind":"window"},{"bbox_xywh":[0.5,0.5,0.1,0.3],"kind":"door"}]}` room `{"apertures":[{"id":"ap0","kind":"window","wall":"west"},{"kind":"door","wall":"north"}],"furniture":[],"schema_version":"0.3"}` | `EXIT: 0`; `STDOUT: verdict BELOW_THRESHOLD score=0.0 opening_mismatches=0 extra_apertures=0 identity=multiset_fallback sha256=247d4d971bd906b07b2c6381659f4e503ee2e5e5c82ff08465522d078f58b793 -> /tmp/codex_v02_identity_mixed_unique_kinds_some_ids_below_threshold_a3uofrd0/verdict/verdict.json`; mixed ids forced fallback but still agreed |
| `duplicate_ids_refused` | target `{"image_id":"identity-two-windows","objects":[],"openings":[{"bbox_xywh":[0.1,0.5,0.1,0.3],"kind":"window"},{"bbox_xywh":[0.9,0.5,0.1,0.3],"kind":"window"}]}` room `{"apertures":[{"id":"ap0","kind":"window","wall":"west"},{"id":"ap0","kind":"window","wall":"east"}],"furniture":[],"schema_version":"0.3"}` | `EXIT: 2`; `STDERR: REFUSED: duplicate aperture id ap0 — malformed render packet`; verdict absent |
| `out_of_range_id_claims_exact` | target `{"image_id":"identity-one-window","objects":[],"openings":[{"bbox_xywh":[0.1,0.5,0.1,0.3],"kind":"window"}]}` room `{"apertures":[{"id":"ap7","kind":"window","wall":"west"}],"furniture":[],"schema_version":"0.3"}` | `EXIT: 0`; `STDOUT: verdict CONTINUE score=0.5 opening_mismatches=1 extra_apertures=1 identity=exact sha256=73810e1a6fb4e0eaac2b5db3f84175984d632433cddd2d1769e1ac0eafc99118 -> /tmp/codex_v02_identity_out_of_range_id_claims_exact_gg5ohw5g/verdict/verdict.json`; it reports `identity.mode="exact"` for an id outside the target index set, but does not agree |
| `non_contiguous_id_claims_exact` | target `{"image_id":"identity-two-windows","objects":[],"openings":[{"bbox_xywh":[0.1,0.5,0.1,0.3],"kind":"window"},{"bbox_xywh":[0.9,0.5,0.1,0.3],"kind":"window"}]}` room `{"apertures":[{"id":"ap0","kind":"window","wall":"west"},{"id":"ap2","kind":"window","wall":"east"}],"furniture":[],"schema_version":"0.3"}` | `EXIT: 0`; `STDOUT: verdict CONTINUE score=0.25 opening_mismatches=1 extra_apertures=1 identity=exact sha256=10d602a04801012c9bc0d843d152969fbb1f99983ecbdc03db51b141ed6a0e4f -> /tmp/codex_v02_identity_non_contiguous_id_claims_exact_3gkkt6xs/verdict/verdict.json`; it reports `identity.mode="exact"` for a gap not justified by this target, but does not agree |
| `leading_zero_id_claims_exact_and_agrees` | target `{"image_id":"identity-one-window","objects":[],"openings":[{"bbox_xywh":[0.1,0.5,0.1,0.3],"kind":"window"}]}` room `{"apertures":[{"id":"ap00","kind":"window","wall":"west"}],"furniture":[],"schema_version":"0.3"}` | `EXIT: 0`; `STDOUT: verdict BELOW_THRESHOLD score=0.0 opening_mismatches=0 extra_apertures=0 identity=exact sha256=709ce8a36656661ef9b52a9029116312b02d313e44fb50a5095353d6b8d79d45 -> /tmp/codex_v02_identity_leading_zero_id_claims_exact_and_agrees_z5zqv6je/verdict/verdict.json`; `ap00` is not the platform-emitted `f"ap{i}"` spelling for index 0, but is treated as exact `ap0` and accepted |
| `nonstructural_gap_ap2_valid_exact` | target `{"image_id":"identity-nonstructural-gap","objects":[],"openings":[{"bbox_xywh":[0.1,0.5,0.1,0.3],"kind":"window"},{"bbox_xywh":[0.5,0.5,0.1,0.3],"kind":"artwork"},{"bbox_xywh":[0.9,0.5,0.1,0.3],"kind":"door"}]}` room `{"apertures":[{"id":"ap0","kind":"window","wall":"west"},{"id":"ap2","kind":"door","wall":"east"}],"furniture":[],"schema_version":"0.3"}` | `EXIT: 0`; `STDOUT: verdict BELOW_THRESHOLD score=0.0 opening_mismatches=0 extra_apertures=0 identity=exact sha256=ed4b4c95008ef76f801d538524164b3a8d44606c79cd7f851acb0ebb88e413e5 -> /tmp/codex_v02_identity_nonstructural_gap_ap2_valid_exact_6o26iilf/verdict/verdict.json`; this non-contiguous id set is valid because frozen `reconstruct.py` preserves source opening indexes while skipping non-structural kinds |
| `spoofed_ids_to_match_swapped_order` | target `{"image_id":"identity-two-windows","objects":[],"openings":[{"bbox_xywh":[0.1,0.5,0.1,0.3],"kind":"window"},{"bbox_xywh":[0.9,0.5,0.1,0.3],"kind":"window"}]}` room `{"apertures":[{"id":"ap1","kind":"window","wall":"east"},{"id":"ap0","kind":"window","wall":"west"}],"furniture":[],"schema_version":"0.3"}` | `EXIT: 0`; `STDOUT: verdict BELOW_THRESHOLD score=0.0 opening_mismatches=0 extra_apertures=0 identity=exact sha256=b3a4a4e66458aac5100d27a638b2a9be6acf7e95449ab16db01733385531b620 -> /tmp/codex_v02_identity_spoofed_ids_to_match_swapped_order_8p2qyrkh/verdict/verdict.json`; I do not count array order alone as a break, because exact mode is explicitly id-keyed |

## 5. New false agreement, determinism, mirror divergence, and test overclaim

### New false agreement outside apertures: object movement is never scored

Executed:

```sh
cd /Users/tanishqsingh/Documents/GitHub/Image_Tagger_dk_latest && PYTHONPATH=. python3 /tmp/codex_v02_extra_contract.py
```

Exact target input:

```json
{"image_id":"object-moved-not-scored","objects":[{"bbox_xywh":[0.1,0.5,0.2,0.2],"category":"chair","id":"chair-1"}],"openings":[]}
```

Exact rendered room input:

```json
{"apertures":[],"furniture":[{"bbox_xywh":[0.9,0.5,0.2,0.2],"category":"chair","id":"chair-1"}],"schema_version":"0.3"}
```

Observed output:

```text
EXIT: 0
STDOUT: verdict BELOW_THRESHOLD score=0.0 opening_mismatches=0 extra_apertures=0 identity=exact sha256=e1c0c8a69c4267cf7f4050fd5bacb24cdb6df82701a8d84f762c8e2cfa927efa -> /tmp/codex_v02_extra_contract_object_moved_same_category_below_threshold_tifj2rey/verdict/verdict.json
VERDICT_JSON: {"built_against":"render-verdict/v0.2","contract_version":"render-verdict/v0.2","discrepancy":{"calibration":"exploratory_uncalibrated","components":{"extra_aperture_frac":0.0,"object_extra_frac":0.0,"object_missing_frac":0.0,"opening_wall_mismatch_frac":0.0},"score":0.0},"identity":{"mode":"exact","unverifiable_kinds":[]},"input_sha256":{"camera_json":"b1d3102fbc2e51cddaa718cc415c867b449999ddc83198ab8bf6b5aee4707875","render_png":"a32cd5a504708a94b5aa9ff343649b1873350fc06ad9691e757ed6f8fa44377b","room_json":"c0b4eeab8921e0fdecebe018674c1ec352902b2124f655cbd2fcf4969878f222"},"iter":0,"object_diff":{"extra_in_render":[],"matched":["chair"],"missing_in_render":[],"moved":[]},"run_id":"codex-v02-extra-object_moved_same_category_below_threshold","target_image_id":"object-moved-not-scored","verdict":"BELOW_THRESHOLD","wall_layout_diff":{"extra_render_apertures":[],"opening_mismatches":[],"render_apertures":0,"target_openings":0}}
```

Reason this is a false agreement: docs/PHOTO_VR_LOOP_DECOMPOSITION_2026-08-15.md section 5 defines `object_diff.moved` with target/render bboxes and offsets. v0.2 always emits `"moved":[]` and compares object categories only. The chair moved from left to right, but the comparator reports `score=0.0` and `BELOW_THRESHOLD`.

### Additional schema/contract acceptance gaps

These are not wall-layout false agreements, but they show the code does not fully enforce `render-packet.schema.json` or canonical JSON:

| Case | Exact manifest issue | Observed output |
| --- | --- | --- |
| `packet_produced_utc_null_accepted` | `produced_utc` present as `null`; schema says string | exit 0, `BELOW_THRESHOLD`, verdict sha `76061d8455523a8227b7ce988f55b4a60f2b4876cd167b4934d7525059de4932` |
| `packet_produced_utc_missing_accepted` | `produced_utc` deleted; schema requires it | exit 0, `BELOW_THRESHOLD`, verdict sha `53a58bb3081b35c489a72ed283a47f23f27283e12f71818f8340c740d02f49bd` |
| `packet_iter_string_accepted` | `iter:"zero"`; schema says integer | exit 0, `BELOW_THRESHOLD`, verdict contains `"iter":"zero"` |
| `packet_iter_nan_accepted` | `iter:NaN`; not valid JSON under the schema | exit 0, `BELOW_THRESHOLD`, verdict contains `"iter":NaN`, so the output is not strict canonical JSON |

### Determinism

Executed:

```sh
cd /Users/tanishqsingh/Documents/GitHub/Image_Tagger_dk_latest && PYTHONPATH=. python3 /tmp/codex_v02_determinism.py
```

Exact target input:

```json
{"image_id":"codex-v02-determinism","objects":[{"category":"chair"},{"category":"desk"},{"category":"chair"}],"openings":[{"bbox_xywh":[0.86,0.5,0.26,0.92],"kind":"glazed_wall"},{"bbox_xywh":[0.5,0.55,0.06,0.35],"kind":"door"},{"bbox_xywh":[0.1,0.55,0.2,0.25],"kind":"window"}]}
```

Exact rendered room input:

```json
{"apertures":[{"id":"ap2","kind":"window","wall":"west"},{"id":"ap0","kind":"glazed_wall","wall":"east"},{"id":"ap9","kind":"skylight","wall":"north"},{"id":"ap1","kind":"door","wall":"west"}],"furniture":[{"category":"chair"},{"category":"plant"},{"category":"chair"}],"schema_version":"0.3"}
```

Observed output:

```text
EXIT_1: 0
STDOUT_1: verdict CONTINUE score=0.3125 opening_mismatches=1 extra_apertures=1 identity=exact sha256=e21879687c60aa67654a2659554567cc6e9412641d2f910bd5188d2bbbbecdab -> /tmp/codex_v02_determinism__7cv30t1/verdict1/verdict.json
EXIT_2: 0
STDOUT_2: verdict CONTINUE score=0.3125 opening_mismatches=1 extra_apertures=1 identity=exact sha256=e21879687c60aa67654a2659554567cc6e9412641d2f910bd5188d2bbbbecdab -> /tmp/codex_v02_determinism__7cv30t1/verdict2/verdict.json
VERDICT_SHA256_1: e21879687c60aa67654a2659554567cc6e9412641d2f910bd5188d2bbbbecdab
VERDICT_SHA256_2: e21879687c60aa67654a2659554567cc6e9412641d2f910bd5188d2bbbbecdab
BYTES_EQUAL: True
```

Result: I did not find nondeterministic verdict bytes under this executed stress case.

### Remaining divergence from `reconstruct.py` at `3fe1d505`

Executed:

```sh
cd /Users/tanishqsingh/Documents/GitHub/Image_Tagger_dk_latest && PYTHONPATH=. python3 /tmp/codex_v02_mirror.py
```

The five v0.1 mirror divergences were re-run and did not reproduce:

| Case | Expected platform behavior | Observed v0.2 behavior |
| --- | --- | --- |
| `zone_right_without_bbox` | zone `right` -> east | exit 0, `BELOW_THRESHOLD`, no mismatches |
| `missing_bbox_no_zone` | default center 0.5 -> north | exit 0, `BELOW_THRESHOLD`, no mismatches |
| `malformed_bbox_width_no_zone` | nonnumeric width causes bbox fallback -> default north | exit 0, `BELOW_THRESHOLD`, no mismatches |
| `out_of_range_center` | refuse `bad_center` | exit 2, `REFUSED: opening 0 centre-x 1.5 out of [0,1] (platform bad_center)` |
| `nonstructural_kind_skipped` | non-structural `painting` skipped | exit 0, `BELOW_THRESHOLD`, `target_openings=0`, `render_apertures=0` |

I found no remaining wall-rule divergence from `_center_x`, `_wall_for`, structural-kind skipping, out-of-range center refusal, or source-index `ap<i>` emission under JSON inputs.

### Test overclaim / coverage gaps

Existing tests run:

```text
cd /Users/tanishqsingh/Documents/GitHub/Image_Tagger_dk_latest && PYTHONPATH=. python3 loop/tests/test_run_loop_compare.py
-> exit 0, 14/14 passed

cd /Users/tanishqsingh/Documents/GitHub/Image_Tagger_dk_latest && python3 -m pytest loop/tests/test_run_loop_compare.py -v
-> exit 1, No module named pytest
```

Overclaims or gaps:

- `loop/tests/test_run_loop_compare.py` lines 3-5 say the negative controls encode the malformed-input fail-closed sweep. The test at lines 244-274 covers only a subset of the ten prior crash cases and does not cover the accepted `target_bbox_bad_scalar` case.
- `test_a1_without_ids_never_claims_agreement` covers the duplicate-kind fallback gate only. It does not cover fallback with one target opening or unique target kinds, where executed probes returned `BELOW_THRESHOLD`.
- `test_wall_rule_and_zone_fallback_match_platform` is a local mirror assertion, not an execution of frozen `reconstruct.py`; that is acceptable as a unit test, but the name/docstring overstate it as platform comparison evidence.
- No test covers malformed ids that fall back and agree (`ap-1`, `door0`), canonical-but-not-platform ids that claim exact (`ap00`), object movement, or manifest type/required-field validation against the schemas.

## 6. What this review did NOT cover

This review used synthetic fixtures only. I did not test a real photo, a real Tagger scene graph, a real render image, the rendering producer, visual PNG-to-room consistency, HITL critique artifacts, end-to-end loop execution, `loop/orchestrate.py`, or `loop/tests/test_orchestrate.py`.

The spoofed-id question is bounded by the file contract: if `room.json` itself lies about `id`, `kind`, or `wall` while `render.png` depicts something else, this comparator does not inspect the pixels and cannot detect that. I only tested what can be represented and executed at the comparator input boundary.

I did not perform exhaustive fuzzing or external JSON Schema validation. The schema gaps above are direct executed examples plus source/schema comparison, not a complete schema-conformance audit.

## 7. Scratch scripts left on disk

- `/tmp/codex_v02_common.py`
- `/tmp/codex_v02_regression.py`
- `/tmp/codex_v02_malformed.py`
- `/tmp/codex_v02_identity.py`
- `/tmp/codex_v02_determinism.py`
- `/tmp/codex_v02_mirror.py`
- `/tmp/codex_v02_extra_contract.py`

## 8. Identity and separation level

I am Codex, OpenAI lineage, acting as a different-lineage non-author reviewer of Claude-written v0.2 comparator code.
