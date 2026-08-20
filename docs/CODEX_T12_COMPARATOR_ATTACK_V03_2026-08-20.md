VERDICT: BROKEN

## 2. Round-2 Regression Results

Executed:

```sh
cd /Users/tanishqsingh/Documents/GitHub/Image_Tagger_dk_latest && PYTHONPATH=. python3 /tmp/codex_v03_regression.py
```

All packets in this section were rebuilt as `render-verdict/v0.3`. Full `TARGET:`, `ROOM:`, `PACKET:`, `CMD:`, `EXIT:`, `STDOUT:`, `STDERR:`, and `VERDICT_JSON:` lines are in `/tmp/codex_v03_regression.out`; the cases themselves are defined in `/tmp/codex_v03_regression.py`.

| Prior probe | Observed exit code and output | Outcome |
| --- | --- | --- |
| `A1_swapped_same_kind_exact_ids` | exit 0; `verdict CONTINUE score=0.2 opening_mismatches=2 extra_apertures=0 moved_objects=0 identity=exact/exact policy=strict` | Closed. No false agreement. |
| `A1_swapped_same_kind_no_ids` | exit 0; `verdict CONTINUE score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=multiset_fallback/exact policy=strict`; `unverifiable_kinds=["window"]` | Closed under strict. |
| `A2_extra_aperture_valid_ap7` | exit 0; `verdict CONTINUE score=0.1 opening_mismatches=0 extra_apertures=1 moved_objects=0 identity=exact/exact policy=strict` | Closed. Extra aperture is scored. |
| `A2_extra_aperture_malformed_extra_id` | exit 0; `verdict CONTINUE score=0.1 opening_mismatches=0 extra_apertures=1 moved_objects=0 identity=multiset_fallback/exact policy=strict` | Closed. Malformed extra id no longer agrees. |
| `malformed_packet_sha256_not_object` | exit 2; `REFUSED: packet.json sha256 must be an object of name->hex digest` | Closed. |
| `malformed_target_openings_not_array` | exit 2; `REFUSED: target scene openings must be a list of objects` | Closed. |
| `malformed_target_bbox_bad_scalar` | exit 0; `verdict BELOW_THRESHOLD score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=exact/exact policy=strict` | Still accepted, matching the v0.2 conclusion that opening bbox fallback mirrors the platform. Not counted as the v0.3 break. |
| `malformed_room_apertures_not_array` | exit 2; `REFUSED: room.json apertures must be a list of objects` | Closed. |
| `malformed_target_top_level_list_with_openings` | exit 2; `REFUSED: target scene must be a JSON object` | Closed. |
| `malformed_target_opening_item_scalar` | exit 2; `REFUSED: target scene openings must be a list of objects` | Closed. |
| `malformed_target_objects_not_array` | exit 2; `REFUSED: target scene objects must be a list of objects` | Closed. |
| `malformed_room_top_level_list` | exit 2; `REFUSED: room.json must be a JSON object` | Closed. |
| `malformed_room_aperture_item_scalar` | exit 2; `REFUSED: room.json apertures must be a list of objects` | Closed. |
| `malformed_room_furniture_not_array` | exit 2; `REFUSED: room.json furniture must be a list of objects` | Closed. |
| `identity_fallback_single_opening_no_id` | exit 0; `verdict CONTINUE score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=multiset_fallback/exact policy=strict` | Closed under strict. |
| `identity_fallback_a1_no_ids` | exit 0; `verdict CONTINUE score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=multiset_fallback/exact policy=strict`; `unverifiable_kinds=["window"]` | Closed. |
| `identity_fallback_multiple_ambiguous_kinds` | exit 0; `verdict CONTINUE score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=multiset_fallback/exact policy=strict`; `unverifiable_kinds=["door","window"]` | Closed. |
| `identity_malformed_negative_id` | exit 0; `verdict CONTINUE score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=multiset_fallback/exact policy=strict` | Closed under strict. |
| `identity_malformed_not_ap_form` | exit 0; `verdict CONTINUE score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=multiset_fallback/exact policy=strict` | Closed under strict. |
| `identity_mixed_some_ids_some_missing` | exit 0; `verdict CONTINUE score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=multiset_fallback/exact policy=strict` | Closed under strict. |
| `identity_mixed_unique_kinds_some_ids` | exit 0; `verdict CONTINUE score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=multiset_fallback/exact policy=strict` | Closed under strict. |
| `identity_duplicate_aperture_ids_refused` | exit 2; `REFUSED: duplicate aperture id ap0 — malformed render packet` | Closed. |
| `identity_out_of_range_id_claims_exact` | exit 0; `verdict CONTINUE score=0.4 opening_mismatches=1 extra_apertures=1 moved_objects=0 identity=exact/exact policy=strict` | No agreement. The "exact" label remains broad for gapped ids, but it does not agree. |
| `identity_non_contiguous_id_claims_exact` | exit 0; `verdict CONTINUE score=0.2 opening_mismatches=1 extra_apertures=1 moved_objects=0 identity=exact/exact policy=strict` | No agreement. |
| `identity_leading_zero_id` | exit 0; `verdict CONTINUE score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=multiset_fallback/exact policy=strict` | Closed. `ap00` no longer claims exact agreement. |
| `identity_nonstructural_gap_ap2_valid` | exit 0; `verdict BELOW_THRESHOLD score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=exact/exact policy=strict` | Expected valid platform gap: non-structural opening keeps source index. |
| `identity_spoofed_ids_to_match_swapped_order` | exit 0; `verdict BELOW_THRESHOLD score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=exact/exact policy=strict` | Not counted as a comparator break: exact mode is intentionally keyed by `ap<i>`, and this probe only reorders the array while preserving ids. |
| `R2_moved_object_same_id_moved_source_bbox` | exit 0; `verdict CONTINUE score=0.2 opening_mismatches=0 extra_apertures=0 moved_objects=1 identity=exact/exact policy=strict`; `moved=[{"bbox_render_source":[0.9,0.6,1.0,0.8],"bbox_target":[0.1,0.6,0.2,0.8],"object_id":"o1","offset_norm":0.8}]` | Headline round-2 finding is closed for valid target/render bboxes. |
| `manifest_iter_nan` | exit 2; `REFUSED: packet.json iter must be a finite integer` | Closed. |
| `manifest_produced_utc_null` | exit 2; `REFUSED: packet.json produced_utc must be a non-empty string (required by render-packet.schema.json)` | Closed. |
| `manifest_produced_utc_missing` | exit 2; same refusal as null | Closed. |
| `manifest_iter_string` | exit 2; `REFUSED: packet.json iter must be a finite integer` | Closed. |
| `manifest_run_id_numeric` | exit 2; `REFUSED: packet.json run_id must be a non-empty string` | Closed. |

## 3. Moved-Object Edge Cases

Executed:

```sh
cd /Users/tanishqsingh/Documents/GitHub/Image_Tagger_dk_latest && PYTHONPATH=. python3 /tmp/codex_v03_moved_edges.py
```

Breaking pattern: valid moved objects are now detected, but invalid or absent target-side `object_bbox` is treated as "no position claim" by `loop/run_loop_compare.py` lines 317-320. That lets strict mode reach `BELOW_THRESHOLD` with a render `_source_bbox` that is far away, non-proven, or wrong-keyed. This conflicts with the v0.3 strict-policy claim in `docs/PHOTO_VR_LOOP_DECOMPOSITION_2026-08-15.md` lines 142-148 and with the target object schema's string/id and four-number bbox requirements in `/Users/tanishqsingh/Documents/GitHub/New_VR_Platform/schemas/scene-semantic-graph.schema.json` lines 20-25 and 62-71.

Full evidence for four representative breaking cases:

```text
CASE: target_short_object_bbox_skips_position_and_agrees
TARGET: {"image_id":"edge-one-object","objects":[{"category":"chair","evidence":{},"id":"o1","object_bbox":[0.1,0.6,0.2]}],"openings":[]}
ROOM: {"apertures":[],"furniture":[{"_source_bbox":[0.9,0.6,1.0,0.8],"category":"chair","id":"o1"}],"schema_version":"0.3"}
EXIT: 0
STDOUT: verdict BELOW_THRESHOLD score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=exact/exact policy=strict sha256=e5c19c04b6d29d46446264fe3645063277cb4cbda67d68e4fa6edbf864296380 -> /tmp/codex_v03_runs/moved_edges/target_short_object_bbox_skips_position_and_agrees/verdict/verdict.json
VERDICT_FIELDS: {"identity":{"mode":"exact","objects_mode":"exact","position_unverified":[],"unverifiable_kinds":[]},"object_diff":{"extra_in_render":[],"matched":["chair"],"missing_in_render":[],"moved":[]},"verdict":"BELOW_THRESHOLD","score":0.0}

CASE: target_nan_object_bbox_skips_position_and_agrees
TARGET: {"image_id":"edge-one-object","objects":[{"category":"chair","evidence":{},"id":"o1","object_bbox":[NaN,0.6,0.2,0.8]}],"openings":[]}
ROOM: {"apertures":[],"furniture":[{"_source_bbox":[0.9,0.6,1.0,0.8],"category":"chair","id":"o1"}],"schema_version":"0.3"}
EXIT: 0
STDOUT: verdict BELOW_THRESHOLD score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=exact/exact policy=strict sha256=500090bfe6cc8f7388d262d13d27649227081f86951747cfd66b94cae1e9d9e1 -> /tmp/codex_v03_runs/moved_edges/target_nan_object_bbox_skips_position_and_agrees/verdict/verdict.json
VERDICT_FIELDS: identity.position_unverified=[]; object_diff.moved=[]; verdict="BELOW_THRESHOLD"; score=0.0

CASE: target_bbox_absent_render_echoes_bbox_agrees
TARGET: {"image_id":"edge-one-object","objects":[{"category":"chair","evidence":{},"id":"o1"}],"openings":[]}
ROOM: {"apertures":[],"furniture":[{"_source_bbox":[0.9,0.6,1.0,0.8],"category":"chair","id":"o1"}],"schema_version":"0.3"}
EXIT: 0
STDOUT: verdict BELOW_THRESHOLD score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=exact/exact policy=strict sha256=602cbd59ea10a0992012d843a473985899d8fec5b6b727be8b43e05f5b05994d -> /tmp/codex_v03_runs/moved_edges/target_bbox_absent_render_echoes_bbox_agrees/verdict/verdict.json
VERDICT_FIELDS: identity.position_unverified=[]; object_diff.moved=[]; verdict="BELOW_THRESHOLD"; score=0.0

CASE: target_wrong_key_bbox_xywh_render_echoes_bbox_agrees
TARGET: {"image_id":"edge-one-object","objects":[{"bbox_xywh":[0.1,0.6,0.2,0.8],"category":"chair","evidence":{},"id":"o1"}],"openings":[]}
ROOM: {"apertures":[],"furniture":[{"_source_bbox":[0.9,0.6,1.0,0.8],"category":"chair","id":"o1"}],"schema_version":"0.3"}
EXIT: 0
STDOUT: verdict BELOW_THRESHOLD score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=exact/exact policy=strict sha256=3502dc8d78217da7ab22f284d13e3c40b7867934982adccecf606fe62348bc4c -> /tmp/codex_v03_runs/moved_edges/target_wrong_key_bbox_xywh_render_echoes_bbox_agrees/verdict/verdict.json
VERDICT_FIELDS: identity.position_unverified=[]; object_diff.moved=[]; verdict="BELOW_THRESHOLD"; score=0.0
```

Every moved-object edge attack, with exact target/room input and observed output:

| Attack | Input | Observed output |
| --- | --- | --- |
| `control_matching_bbox_agrees` | target `{"image_id":"edge-one-object","objects":[{"category":"chair","evidence":{},"id":"o1","object_bbox":[0.1,0.6,0.2,0.8]}],"openings":[]}`; room `{"apertures":[],"furniture":[{"_source_bbox":[0.1,0.6,0.2,0.8],"category":"chair","id":"o1"}],"schema_version":"0.3"}` | `EXIT: 0; STDOUT: verdict BELOW_THRESHOLD score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=exact/exact policy=strict; verdict=BELOW_THRESHOLD; moved=[]` |
| `control_moved_bbox_detected` | target same valid bbox; room `_source_bbox:[0.9,0.6,1.0,0.8]` | `EXIT: 0; STDOUT: verdict CONTINUE score=0.2 opening_mismatches=0 extra_apertures=0 moved_objects=1 identity=exact/exact policy=strict; moved=[{"bbox_render_source":[0.9,0.6,1.0,0.8],"bbox_target":[0.1,0.6,0.2,0.8],"object_id":"o1","offset_norm":0.8}]` |
| `target_short_object_bbox_skips_position_and_agrees` | target `object_bbox:[0.1,0.6,0.2]`; room `_source_bbox:[0.9,0.6,1.0,0.8]` | `EXIT: 0; STDOUT: verdict BELOW_THRESHOLD score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=exact/exact policy=strict; position_unverified=[]; moved=[]` |
| `render_short_source_bbox_unverified` | target valid bbox; room `_source_bbox:[0.1,0.6,0.2]` | `EXIT: 0; STDOUT: verdict CONTINUE score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=exact/exact policy=strict; position_unverified=["o1"]; moved=[]` |
| `target_long_object_bbox_skips_position_and_agrees` | target `object_bbox:[0.1,0.6,0.2,0.8,0.9]`; room moved `_source_bbox:[0.9,0.6,1.0,0.8]` | `EXIT: 0; STDOUT: verdict BELOW_THRESHOLD score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=exact/exact policy=strict; position_unverified=[]; moved=[]` |
| `render_long_source_bbox_unverified` | target valid bbox; room `_source_bbox:[0.1,0.6,0.2,0.8,0.9]` | `EXIT: 0; STDOUT: verdict CONTINUE score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=exact/exact policy=strict; position_unverified=["o1"]` |
| `target_nan_object_bbox_skips_position_and_agrees` | target `object_bbox:[NaN,0.6,0.2,0.8]`; room moved `_source_bbox:[0.9,0.6,1.0,0.8]` | `EXIT: 0; STDOUT: verdict BELOW_THRESHOLD score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=exact/exact policy=strict; position_unverified=[]; moved=[]` |
| `render_nan_source_bbox_unverified` | target valid bbox; room `_source_bbox:[NaN,0.6,0.2,0.8]` | `EXIT: 0; STDOUT: verdict CONTINUE score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=exact/exact policy=strict; position_unverified=["o1"]` |
| `target_string_object_bbox_skips_position_and_agrees` | target `object_bbox:["bad",0.6,0.2,0.8]`; room moved `_source_bbox:[0.9,0.6,1.0,0.8]` | `EXIT: 0; STDOUT: verdict BELOW_THRESHOLD score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=exact/exact policy=strict; position_unverified=[]; moved=[]` |
| `render_string_source_bbox_unverified` | target valid bbox; room `_source_bbox:["bad",0.6,0.2,0.8]` | `EXIT: 0; STDOUT: verdict CONTINUE score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=exact/exact policy=strict; position_unverified=["o1"]` |
| `offset_exactly_epsilon_agrees` | target `object_bbox:[0.0,0.6,0.2,0.8]`; room `_source_bbox:[1e-06,0.6,0.2,0.8]` | `EXIT: 0; STDOUT: verdict BELOW_THRESHOLD score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=exact/exact policy=strict; moved=[]` |
| `offset_just_under_epsilon_agrees` | target `object_bbox:[0.0,0.6,0.2,0.8]`; room `_source_bbox:[9.99999e-07,0.6,0.2,0.8]` | `EXIT: 0; STDOUT: verdict BELOW_THRESHOLD score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=exact/exact policy=strict; moved=[]` |
| `offset_just_over_epsilon_detected` | target `object_bbox:[0.0,0.6,0.2,0.8]`; room `_source_bbox:[1.001e-06,0.6,0.2,0.8]` | `EXIT: 0; STDOUT: verdict CONTINUE score=0.2 opening_mismatches=0 extra_apertures=0 moved_objects=1 identity=exact/exact policy=strict; moved=[{"bbox_render_source":[1.001e-06,0.6,0.2,0.8],"bbox_target":[0.0,0.6,0.2,0.8],"object_id":"o1","offset_norm":1e-06}]` |
| `target_bbox_absent_render_echoes_bbox_agrees` | target object has no `object_bbox`; room moved `_source_bbox:[0.9,0.6,1.0,0.8]` | `EXIT: 0; STDOUT: verdict BELOW_THRESHOLD score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=exact/exact policy=strict; position_unverified=[]; moved=[]` |
| `target_wrong_key_bbox_xywh_render_echoes_bbox_agrees` | target object has wrong key `bbox_xywh:[0.1,0.6,0.2,0.8]`; room moved `_source_bbox:[0.9,0.6,1.0,0.8]` | `EXIT: 0; STDOUT: verdict BELOW_THRESHOLD score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=exact/exact policy=strict; position_unverified=[]; moved=[]` |
| `target_bbox_present_render_source_absent_unverified` | target valid bbox; room omits `_source_bbox` | `EXIT: 0; STDOUT: verdict CONTINUE score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=exact/exact policy=strict; position_unverified=["o1"]` |
| `duplicate_target_object_ids_fallback_blocks_agreement` | target ids `o1,o1`; room ids `o1,o2` | `EXIT: 0; STDOUT: verdict CONTINUE score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=exact/multiset_fallback policy=strict; position_unverified=["chair","desk"]` |
| `duplicate_render_object_ids_fallback_blocks_agreement` | target ids `o1,o2`; room ids `o1,o1` | `EXIT: 0; STDOUT: verdict CONTINUE score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=exact/multiset_fallback policy=strict; position_unverified=["chair","desk"]` |
| `target_id_missing_render_id_present_fallback_blocks` | target omits id; room id `o1` | `EXIT: 0; STDOUT: verdict CONTINUE score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=exact/multiset_fallback policy=strict; position_unverified=["chair"]` |
| `target_id_present_render_id_missing_fallback_blocks` | target id `o1`; room omits id | `EXIT: 0; STDOUT: verdict CONTINUE score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=exact/multiset_fallback policy=strict; position_unverified=["chair"]` |
| `cross_source_bbox_from_different_object_detected` | target `o1` bbox `[0.1,0.6,0.2,0.8]`, `o2` bbox `[0.6,0.6,0.8,0.8]`; render swaps `_source_bbox` values | `EXIT: 0; STDOUT: verdict CONTINUE score=0.2 opening_mismatches=0 extra_apertures=0 moved_objects=2 identity=exact/exact policy=strict; moved=[{"object_id":"o1","offset_norm":0.6},{"object_id":"o2","offset_norm":0.6}]` |

## 4. Strict-Policy Bypass Attempts

Executed:

```sh
cd /Users/tanishqsingh/Documents/GitHub/Image_Tagger_dk_latest && PYTHONPATH=. python3 /tmp/codex_v03_strict_vacuous.py
```

`_fully_verified()` only checks `identity.mode`, `objects_mode`, `unverifiable_kinds`, and `position_unverified` at `loop/run_loop_compare.py` lines 382-385. It trusts the upstream object comparer to mean those fields literally. The object comparer coerces ids and categories with `str(...)` at lines 293-310, so schema-invalid object IDs/categories can become exact matches and pass strict policy.

Breaking strict-policy attempts:

```text
CASE: strict_numeric_target_id_render_string_id_agrees
TARGET: {"image_id":"strict-numeric-object-id","objects":[{"category":"chair","evidence":{},"id":7,"object_bbox":[0.1,0.6,0.2,0.8]}],"openings":[]}
ROOM: {"apertures":[],"furniture":[{"_source_bbox":[0.1,0.6,0.2,0.8],"category":"chair","id":"7"}],"schema_version":"0.3"}
EXIT: 0
STDOUT: verdict BELOW_THRESHOLD score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=exact/exact policy=strict sha256=d1a320377078cb31037b7363e52037a77a252b817e82e6b3f49c2b43a0580d52 -> /tmp/codex_v03_runs/strict_vacuous/strict_numeric_target_id_render_string_id_agrees/verdict/verdict.json

CASE: strict_null_ids_on_both_sides_agree
TARGET: {"image_id":"strict-null-object-id","objects":[{"category":"chair","evidence":{},"id":null,"object_bbox":[0.1,0.6,0.2,0.8]}],"openings":[]}
ROOM: {"apertures":[],"furniture":[{"_source_bbox":[0.1,0.6,0.2,0.8],"category":"chair","id":null}],"schema_version":"0.3"}
EXIT: 0
STDOUT: verdict BELOW_THRESHOLD score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=exact/exact policy=strict sha256=348cbbdfcb9fef7a9ed6371e5812e444e6c22f3b6d2d004a863f432cd7d9236b -> /tmp/codex_v03_runs/strict_vacuous/strict_null_ids_on_both_sides_agree/verdict/verdict.json

CASE: strict_boolean_target_id_render_string_id_agrees
TARGET: {"image_id":"strict-bool-object-id","objects":[{"category":"chair","evidence":{},"id":true,"object_bbox":[0.1,0.6,0.2,0.8]}],"openings":[]}
ROOM: {"apertures":[],"furniture":[{"_source_bbox":[0.1,0.6,0.2,0.8],"category":"chair","id":"True"}],"schema_version":"0.3"}
EXIT: 0
STDOUT: verdict BELOW_THRESHOLD score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=exact/exact policy=strict sha256=d8d690bbf045af7edfab3235d6fa9bfa53008964f49153121b761f83f16fd1f7 -> /tmp/codex_v03_runs/strict_vacuous/strict_boolean_target_id_render_string_id_agrees/verdict/verdict.json

CASE: strict_numeric_category_coerced_agrees
TARGET: {"image_id":"strict-numeric-category","objects":[{"category":7,"evidence":{},"id":"o1","object_bbox":[0.1,0.6,0.2,0.8]}],"openings":[]}
ROOM: {"apertures":[],"furniture":[{"_source_bbox":[0.1,0.6,0.2,0.8],"category":"7","id":"o1"}],"schema_version":"0.3"}
EXIT: 0
STDOUT: verdict BELOW_THRESHOLD score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=exact/exact policy=strict sha256=c3eea49260d43db4372c20f327973ea680736005e0637494630bf9b4e0f7e4a2 -> /tmp/codex_v03_runs/strict_vacuous/strict_numeric_category_coerced_agrees/verdict/verdict.json
```

Strict attempts that did not bypass:

| Attack | Input | Observed output |
| --- | --- | --- |
| `strict_opening_idless_single_blocks` | target one west window; room same window without id | exit 0; `verdict CONTINUE score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=multiset_fallback/exact policy=strict` |
| `strict_opening_mixed_ids_unique_kinds_blocks` | target west window+north door; room window has `ap0`, door has no id | exit 0; `verdict CONTINUE score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=multiset_fallback/exact policy=strict` |
| `strict_object_idless_same_category_blocks` | target and room chair without ids | exit 0; `verdict CONTINUE score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=exact/multiset_fallback policy=strict`; `position_unverified=["chair"]` |
| `allow_unverified_opening_idless_single_agrees_control` | same as idless opening, with `--allow-unverified-agreement` | exit 0; `verdict BELOW_THRESHOLD score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=multiset_fallback/exact policy=allow_unverified` as explicitly allowed |

The bbox-based strict bypasses are also strict-policy bypasses:

| Attack | Input | Observed output |
| --- | --- | --- |
| `strict_target_bbox_absent_render_echoes_bbox_agrees` | target `{"id":"o1","category":"chair","evidence":{}}`; room same id/category with `_source_bbox:[0.9,0.6,1.0,0.8]` | exit 0; `verdict BELOW_THRESHOLD score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=exact/exact policy=strict`; `position_unverified=[]`; `moved=[]` |
| `strict_target_wrong_keyed_bbox_render_echoes_bbox_agrees` | target uses wrong object key `bbox_xywh:[0.1,0.6,0.2,0.8]`; room echoes moved `_source_bbox:[0.9,0.6,1.0,0.8]` | exit 0; `verdict BELOW_THRESHOLD score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=exact/exact policy=strict`; `position_unverified=[]`; `moved=[]` |

## 5. The Vacuous Case

The pure vacuous case is real: target with no objects and render with no furniture reaches `BELOW_THRESHOLD` when openings agree. That is not by itself a break if the target truly has no objects. The attack surface is that `load_target()` allows `objects` missing or `null` when `openings` exists (`loop/run_loop_compare.py` lines 186-192), while the frozen scene-semantic schema requires an `objects` array. Those malformed empty-object target variants also reach strict `BELOW_THRESHOLD`.

Executed vacuous cases from `/tmp/codex_v03_strict_vacuous.py`:

| Attack | Exact input | Observed output |
| --- | --- | --- |
| `vacuous_opening_no_objects_no_furniture_agrees` | target `{"image_id":"vacuous-empty-objects","objects":[],"openings":[{"bbox_xywh":[0.1,0.5,0.1,0.3],"kind":"window"}]}`; room `{"apertures":[{"id":"ap0","kind":"window","wall":"west"}],"furniture":[],"schema_version":"0.3"}` | exit 0; `verdict BELOW_THRESHOLD score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=exact/exact policy=strict` |
| `vacuous_opening_objects_missing_no_furniture_agrees` | target `{"image_id":"vacuous-objects-missing","openings":[{"bbox_xywh":[0.1,0.5,0.1,0.3],"kind":"window"}]}`; room same exact aperture, no furniture | exit 0; `verdict BELOW_THRESHOLD score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=exact/exact policy=strict` |
| `vacuous_opening_objects_null_no_furniture_agrees` | target `{"image_id":"vacuous-objects-null","objects":null,"openings":[{"bbox_xywh":[0.1,0.5,0.1,0.3],"kind":"window"}]}`; room same exact aperture, no furniture | exit 0; `verdict BELOW_THRESHOLD score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=exact/exact policy=strict` |
| `vacuous_target_has_object_render_has_none_continues` | target one chair object; room no furniture | exit 0; `verdict CONTINUE score=0.2`; `missing_in_render=["chair"]` |
| `vacuous_target_no_objects_render_has_furniture_continues` | target no objects; room one chair furniture | exit 0; `verdict CONTINUE score=0.2`; `extra_in_render=["chair"]`; `objects_mode=multiset_fallback` |
| `vacuous_target_two_objects_render_one_continues` | target chair+desk; room chair only | exit 0; `verdict CONTINUE score=0.1`; `missing_in_render=["desk"]` |
| `vacuous_target_one_object_render_two_continues` | target chair; room chair+desk | exit 0; `verdict CONTINUE score=0.1`; `extra_in_render=["desk"]` |
| `vacuous_no_openings_no_objects_refused` | target `{"image_id":"vacuous-empty-target","objects":[],"openings":[]}`; room empty | exit 2; `REFUSED: target scene has neither openings nor objects — nothing to compare` |

Conclusion: if the target truthfully contains `objects: []`, the vacuous agreement is a design choice. If the target object side is missing/null/emptied before compare, the comparator cannot recover that and will call the object side exact.

## 6. Determinism, Mirror Divergence, Test Overclaims

Executed:

```sh
cd /Users/tanishqsingh/Documents/GitHub/Image_Tagger_dk_latest && PYTHONPATH=. python3 /tmp/codex_v03_determinism_mirror.py
cd /Users/tanishqsingh/Documents/GitHub/Image_Tagger_dk_latest && PYTHONPATH=. python3 -m pytest loop/tests/test_run_loop_compare.py -v
```

Determinism result: two CLI runs on the same stress packet produced identical verdict bytes.

```text
EXIT_1: 0
STDOUT_1: verdict BELOW_THRESHOLD score=0.283333 opening_mismatches=1 extra_apertures=1 moved_objects=1 identity=exact/exact policy=strict sha256=8e76c65081462f365e6a4f3c0908f547e46f2ea38c47639900c8efe361a0cc44 -> /tmp/codex_v03_runs/determinism_mirror/determinism_two_cli_runs/verdict1/verdict.json
EXIT_2: 0
STDOUT_2: verdict BELOW_THRESHOLD score=0.283333 opening_mismatches=1 extra_apertures=1 moved_objects=1 identity=exact/exact policy=strict sha256=8e76c65081462f365e6a4f3c0908f547e46f2ea38c47639900c8efe361a0cc44 -> /tmp/codex_v03_runs/determinism_mirror/determinism_two_cli_runs/verdict2/verdict.json
VERDICT_SHA256_1: 8e76c65081462f365e6a4f3c0908f547e46f2ea38c47639900c8efe361a0cc44
VERDICT_SHA256_2: 8e76c65081462f365e6a4f3c0908f547e46f2ea38c47639900c8efe361a0cc44
BYTES_EQUAL: True
```

Mirror checks against the frozen platform behavior:

| Probe | Observed output |
| --- | --- |
| `mirror_zone_right_without_bbox` | exit 0; `verdict BELOW_THRESHOLD score=0.0`; no mismatch |
| `mirror_missing_bbox_no_zone` | exit 0; `verdict BELOW_THRESHOLD score=0.0`; no mismatch |
| `mirror_malformed_bbox_width_no_zone` | exit 0; `verdict BELOW_THRESHOLD score=0.0`; no mismatch |
| `mirror_out_of_range_center_refused` | exit 2; `REFUSED: opening 0 centre-x 1.5 out of [0,1] (platform bad_center)` |
| `mirror_nonstructural_kind_skipped` | exit 0; `verdict BELOW_THRESHOLD score=0.0`; target openings 0 |
| `mirror_nonstructural_gap_ap2_exact` | exit 0; `verdict BELOW_THRESHOLD score=0.0`; `ap2` gap accepted |
| `mirror_ap00_not_exact` | exit 0; `verdict CONTINUE score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=multiset_fallback/exact policy=strict` |

I found no remaining aperture wall-rule divergence from `_center_x()`, `_wall_for()`, non-structural opening skipping, bad-center refusal, source-index `ap<i>` gaps, or `ap00` spelling under the executed probes.

Remaining platform/schema divergence I did find: the target object schema requires object `id` and `category` to be non-empty strings and constrains `object_bbox` to four numeric values. The comparator does not enforce those target object field types, and the executed attacks above exploit that. The frozen platform `place_furniture.py` skips objects with absent/bad `object_bbox` at lines 98-101; the comparator instead can match such an object by id/category and report strict agreement.

Test execution:

```text
PYTHONPATH=. python3 loop/tests/test_run_loop_compare.py
-> exit 0, 22/22 passed

PYTHONPATH=. python3 -m pytest loop/tests/test_run_loop_compare.py -v
-> exit 1, /opt/homebrew/opt/python@3.13/bin/python3.13: No module named pytest
```

Test overclaims and gaps:

- `loop/tests/test_run_loop_compare.py` lines 3-5 say the negative controls encode the malformed-input fail-closed sweep. The current test covers a subset of the prior malformed cases and does not cover malformed target object IDs/categories or malformed target `object_bbox`.
- `test_good_render_agrees` uses target objects with no `object_bbox` and furniture with no `_source_bbox` at lines 36-47, then asserts strict `BELOW_THRESHOLD` at lines 112-122. That test normalizes the exact position gap that the new attacks exploit.
- `test_r2_position_claim_without_echo_blocks_agreement` covers only the direction "target has valid bbox, render omits `_source_bbox`" at lines 355-365. It does not cover the reverse direction "target bbox absent/wrong-keyed/malformed, render echoes one".
- `test_r2_moved_object_never_agrees` covers valid four-element bboxes only at lines 331-342. It does not exercise target-short, target-long, non-finite target, non-numeric target, or absent target bbox.
- `test_wall_rule_and_zone_fallback_match_platform` checks selected local examples at lines 201-215; it is useful but still not a direct execution of frozen `reconstruct.py`.

The claim "x_m/y_m consistency with `_source_bbox` is not verified" remains an explicit stated bound, not something I falsified.

## 7. What This Review Did NOT Cover

This review used synthetic fixtures only. I did not test a real photo, a real Tagger scene graph, a real render image, visual PNG-to-JSON consistency, HITL critique artifacts, end-to-end loop execution, `loop/orchestrate.py`, or `loop/tests/test_orchestrate.py`.

I did not perform exhaustive fuzzing or external JSON Schema validation. I did read the frozen platform source/schema context named in the prompt, but I did not execute the full New_VR_Platform pipeline.

I did not claim that epsilon-sized offsets are broken. The executed `1e-6` and `9.99999e-7` offsets agree because the comparator uses `off > _EPS`; the `1.001e-6` offset is detected. That boundary appears intentional.

## 8. Scratch Scripts Left On Disk

- `/tmp/codex_v03_common.py`
- `/tmp/codex_v03_regression.py`
- `/tmp/codex_v03_moved_edges.py`
- `/tmp/codex_v03_strict_vacuous.py`
- `/tmp/codex_v03_determinism_mirror.py`

Output logs and stable generated artifacts are also left on disk:

- `/tmp/codex_v03_regression.out`
- `/tmp/codex_v03_moved_edges.out`
- `/tmp/codex_v03_strict_vacuous.out`
- `/tmp/codex_v03_determinism_mirror.out`
- `/tmp/codex_v03_runs/`

## 9. Identity and Separation Level

I am Codex, GPT-5 lineage, acting as a different-lineage non-author reviewer of `render-verdict/v0.3`.
