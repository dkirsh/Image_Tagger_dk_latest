VERDICT: BROKEN

Reviewed commit: `cc21164d588107cfe967d35f388413bf07ed779b`.

Scope confirmation: subject inspection and all comparator executions were from `/tmp/review_v05`, limited to `/tmp/review_v05/loop/` for the Image_Tagger subject. I did not read or test the live `~/Documents/GitHub/Image_Tagger_dk_latest` tree. I read only the permitted New_VR_Platform context files named in the prompt, and did not treat them as authoritative.

Worktree hygiene: `git status --short` was empty before and after. I did not modify anything under `/tmp/review_v05`.

Commands run from the worktree included:

```sh
cd /tmp/review_v05 && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 loop/tests/test_run_loop_compare.py
cd /tmp/review_v05 && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 /tmp/codex_v05_round4_regressions.py
cd /tmp/review_v05 && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 /tmp/codex_v05_marker_attacks.py
cd /tmp/review_v05 && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 /tmp/codex_v05_null_edges.py
cd /tmp/review_v05 && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 /tmp/codex_v05_misc_attacks.py
```

The in-scope stdlib test runner passed `35/35`. `pytest` was not installed, so I used the test file's own fallback runner. The attack harness recorded 74 JSONL observations under `/tmp/codex_v05_runs/*/results.jsonl`.

## Round-4 Regression Results

All four round-4 findings were re-run as v0.5 packets and are closed against the original failure mode.

| Finding | Exact attack input mutation | Observed output | Result |
|---|---|---|---|
| V04-1 | `target.objects[0].object_bbox = null`; render has matching `id/category` and `_source_bbox` | code `0`; `verdict CONTINUE score=0.0`; `identity.position_unverified=["o1"]`; strict did not agree | CLOSED |
| V04-2 | render furniture `category` values `7`, `null`, `true`, `[1]`, `{"x":1}`, `1.5` against target string categories | each code `0`; `matched=[]`; `missing_in_render` has the target string; `extra_in_render` has `<unreadable-category:TYPE>`; `verdict CONTINUE score=0.4` | CLOSED for generated non-string category false-match |
| V04-2 openings | render aperture `kind=7` or `wall=true` with exact `ap0` id | code `0`; one opening mismatch; rendered display `<non-string:int>` or `<non-string:bool>`; `verdict CONTINUE` | CLOSED for no `str()` compare on kind/wall |
| V04-3 | aperture ids `"ap0\n"`, `"ap0\t"`, `"ap0 "` | each code `0`; `identity.mode="multiset_fallback"`; score `0.0`; strict `verdict CONTINUE`, not exact | CLOSED |
| V04-4 | packet manifest `iter=-1` | code `2`; `REFUSED: packet.json iter must be >= 0 ...` | CLOSED |

Full records: `/tmp/codex_v05_runs/round4_regressions/results.jsonl`.

## Marker-Mechanism Attacks

Generated markers from non-string render categories did not enter `matched`. For every generated type I could produce (`int`, `NoneType`, `bool`, `list`, `dict`, `float`), I used target category equal to the literal marker string and render category equal to the non-string value. Example exact input:

```json
target.objects[0].category = "<unreadable-category:int>"
room.furniture[0].category = 7
```

Observed: code `0`, `verdict CONTINUE score=0.4`, `matched=[]`, `missing_in_render=["<unreadable-category:int>"]`, `extra_in_render=["<unreadable-category:int>"]`. The same shape held for all generated marker types in exact and fallback object modes. This closes the specific v0.5 claim that a generated marker from a non-string render category cannot false-match the target marker string.

Fresh marker finding M1: marker-shaped literal strings are not reserved. Exact input:

```json
target = {
  "image_id": "codex-v05",
  "openings": [{"kind": "door", "bbox_xywh": [0.5, 0.55, 0.06, 0.35]}],
  "objects": [{"id": "o1", "category": "<unreadable-category:int>", "evidence": {}}]
}
room = {
  "schema_version": "0.3",
  "apertures": [{"id": "ap0", "kind": "door", "wall": "north"}],
  "furniture": [{"id": "o1", "category": "<unreadable-category:int>"}]
}
```

Observed: code `0`; `verdict BELOW_THRESHOLD score=0.0`; `identity=exact/exact`; `object_diff.matched=["<unreadable-category:int>"]`. The same happened for nested marker text (`"<<unreadable-category:int>>"`), repeated marker text (`"<unreadable-category:int><unreadable-category:int>"`), and the render `element` fallback path when `category` was missing and `element` was the marker-shaped string.

This is not the same as a generated non-string marker entering the render category multiset. It is still a marker-mechanism break if the marker namespace is meant to be display-only/reserved, because an input can put marker-shaped text into `matched` and change the verdict to strict `BELOW_THRESHOLD`.

Other marker probes:

| Case | Observed |
|---|---|
| target marker string, render non-string category, exact id | `matched=[]`, `missing=marker`, `extra=generated marker`, `CONTINUE` |
| target marker string, render non-string category, missing/null id fallback | `matched=[]`, `missing=marker`, `extra=generated marker`, `CONTINUE` |
| target normal `"chair"`, render string `"<unreadable-category:int>"` | `missing=["chair"]`, `extra=["<unreadable-category:int>"]`, `CONTINUE` |
| literal marker string on both sides, fallback object mode | `matched=["<unreadable-category:int>"]`, `position_unverified=["<unreadable-category:int>"]`, score `0.0`, strict `CONTINUE` |
| present `category:null` plus `element:"<unreadable-category:int>"` | null wins; `extra=["<unreadable-category:NoneType>"]`, `missing=["<unreadable-category:int>"]`, `CONTINUE` |

Full records: `/tmp/codex_v05_runs/marker_attacks/results.jsonl`.

## `_disp` / Display-Value Leak Trace

Trace in `loop/run_loop_compare.py`:

| Lines | Use |
|---|---|
| 277-280 | `_disp` returns raw non-empty strings or `<non-string:TYPE>` display text |
| 326, 328 | exact opening mismatch display fields |
| 329-330 | exact-mode extra aperture display strings |
| 340-341 | fallback opening `have` multiset keys and values are built with `_disp` |
| 348 | fallback membership test `if w in avail` consults values created by `_disp` |
| 353 | fallback mismatch picks `sorted(avail)[0]`, also `_disp` output |
| 358 | fallback extra aperture strings are sorted from `_disp`-derived keys/values |

Attack `opening_disp_fallback_nonstring_kind_and_wall` exact input:

```json
target.openings = [{"kind": "door", "bbox_xywh": [0.5, 0.55, 0.06, 0.35]}]
room.apertures = [{"id": null, "kind": 7, "wall": true}]
```

Observed: code `0`; `identity.mode="multiset_fallback"`; `wall_layout_diff.extra_render_apertures=["<non-string:int>-><non-string:bool>"]`; `opening_mismatches=[{"expected_wall":"north","rendered_wall":"MISSING",...}]`; `score=0.4`; `verdict CONTINUE`.

I did not find a strict false agreement through `_disp`: generated `<non-string:TYPE>` values cannot equal a structural target kind or `wall_for()` wall. But the helper/docstring claim "display-only" / "never used for matching" is false as written: display values reach a multiset, a membership test, a sort key, and the extra-aperture score path in fallback mode.

## Null-Policy Edge Attacks

Container null policy held for the four named containers:

| Container | Empty | Missing | Null |
|---|---|---|---|
| target `openings` | accepted as `identity.mode="vacuous"` when objects exist | accepted as `vacuous` | refused exit `2` |
| target `objects` | accepted as `identity.objects_mode="vacuous"` when openings exist | accepted as `vacuous` | refused exit `2` |
| room `apertures` | accepted as `vacuous` when target has no openings | accepted as `vacuous` | refused exit `2` |
| room `furniture` | accepted as `vacuous` when target has no objects | accepted as `vacuous` | refused exit `2` |

Leaf and nested null observations:

| Case | Observed |
|---|---|
| `sha256.room_json = null` | refused exit `2` as sha mismatch |
| whole `sha256 = null` | refused exit `2`, `sha256 must be an object` |
| extra `sha256.extra_json = null` | accepted and echoed into `input_sha256`; strict `BELOW_THRESHOLD` |
| `camera.json` document is `null` | accepted; strict `BELOW_THRESHOLD` |
| `room.schema_version = null` | accepted; strict `BELOW_THRESHOLD` |
| aperture `kind:null` or `wall:null` | exact-mode mismatch; strict `CONTINUE` |
| aperture `id:null` | fallback identity; score `0.0`; strict `CONTINUE` |
| furniture `category:null` | unreadable category marker in `extra_in_render`; strict `CONTINUE` |
| furniture `id:null` | object fallback; `position_unverified=["chair"]`; strict `CONTINUE` |
| furniture `_source_bbox:null` with target bbox claim | `position_unverified=["o1"]`; strict `CONTINUE` |
| target `object_bbox:null` | `position_unverified=["o1"]`; strict `CONTINUE` |
| target `object_bbox` array containing `null` | `position_unverified=["o1"]`; strict `CONTINUE` |
| render `_source_bbox` array containing `null` | `position_unverified=["o1"]`; strict `CONTINUE` |
| target object with only mis-keyed `bbox_xywh:null` | `position_unverified=["o1"]`; strict `CONTINUE` |
| target object with valid `object_bbox` plus extra `bbox_xywh:null` | accepted; strict `BELOW_THRESHOLD` |
| target opening `bbox_xywh:null` | falls through platform-style center fallback to north; strict `BELOW_THRESHOLD` |
| target opening `bbox_xywh` array containing `null` | same fallback to north; strict `BELOW_THRESHOLD` |

Boundary assessment: the null policy is enforced for the four named containers and for object position claims. It is not enforced for `camera.json`, `room.schema_version`, extra sha entries, or opening `bbox_xywh`. The opening behavior mirrors the frozen platform `_center_x` fallback for malformed/missing bboxes, so I do not call it a mirror divergence; it is still a policy boundary worth stating explicitly because a present null is treated like no usable opening bbox.

Full records: `/tmp/codex_v05_runs/null_edges/results.jsonl`.

## Fresh Findings, Determinism, RFC 8259, Mirror Divergence, Test Overclaims

Fresh finding F1: marker-shaped literal categories can enter `matched` and produce strict `BELOW_THRESHOLD`. See M1 above. This is the main marker-mechanism break: generated markers did not match, but marker syntax is not reserved or escaped.

Fresh finding F2: `_disp` values are not display-only in opening fallback mode. They feed the fallback `have` multiset, membership test, sort, and extra scoring path. I found no false agreement from this, but it contradicts the helper contract and the requested display-leak criterion.

Fresh finding F3: input parsing is not RFC 8259-strict. Python `json.loads` accepts `NaN`, and the comparator can still return strict `BELOW_THRESHOLD` when the non-finite token is in ignored/unconsumed fields. Exact observed cases:

| Invalid input | Observed |
|---|---|
| `room.json` has `"schema_version": NaN` | code `0`; strict `BELOW_THRESHOLD`; output verdict strict-parseable |
| `packet.json` has extra `"unused_nan": NaN` | code `0`; strict `BELOW_THRESHOLD`; output verdict strict-parseable |
| `camera.json` is raw `NaN\n` | code `0`; strict `BELOW_THRESHOLD`; output verdict strict-parseable |
| target scene has extra `"unused_nan": NaN` | code `0`; strict `BELOW_THRESHOLD`; output verdict strict-parseable |

This does not produce an invalid `verdict.json`; the output canonicalization still refuses non-finite values that reach the verdict. The break is that invalid JSON inputs can be accepted and agree.

Fresh finding F4 / policy gap: `camera.json:null`, `room.schema_version:null`, and extra null sha entries can be accepted with strict `BELOW_THRESHOLD`. If the null policy was intended to cover only compared containers and object position leaves, this is just a stated boundary. If it was intended literally as "a present JSON null is never absent" across packet documents/leaves, these are misses.

Determinism: normal rerun hashes matched byte-for-byte:

```text
d6953db408f9be3c173c3a55a169cb4807c8d464e5cb9bc9644f838e8bb6fabb
d6953db408f9be3c173c3a55a169cb4807c8d464e5cb9bc9644f838e8bb6fabb
```

Wrong-render controls under strict threshold `0.0`:

| Wrong render | Observed |
|---|---|
| wrong wall `north` expected, render `east` | code `0`; one opening mismatch; score `0.2`; `CONTINUE` |
| moved object `_source_bbox` offset `0.8` | code `0`; one moved object; score `0.2`; `CONTINUE` |

RFC 8259 output validity: all produced verdicts that existed were accepted by a strict `json.loads(..., parse_constant=reject)` check in the misc harness. The RFC issue is accepted invalid input, not emitted invalid output.

Mirror divergence: for the named frozen platform context, I saw no new divergence in `_center_x`, `_wall_for`, structural-kind filtering, aperture `ap<i>` indexing, furniture id, or `_source_bbox` comparison. The target opening `bbox_xywh:null` fallback to north is consistent with the frozen `_center_x` malformed-bbox fallback. I did not treat the platform schema-versus-fixture conflict as authoritative.

Test overclaims:

- `test_v04_2_marker_string_cannot_false_match` checks a generated int marker against a target marker string, but not literal marker-shaped render strings, nested/repeated marker text, `element` fallback, or fallback object multiset marker-shaped strings.
- `_disp`'s docstring says "Never used for matching"; the code uses `_disp` in fallback opening matching structures.
- Existing null tests cover the four named containers and `object_bbox:null`, but not `camera.json:null`, `room.schema_version:null`, extra sha nulls, opening `bbox_xywh:null`, or invalid RFC 8259 input accepted by Python's default JSON parser.
- Running the stdlib test file emitted a `SyntaxWarning` for `\Z` in a docstring (`invalid escape sequence '\Z'`). It did not affect test results, but it is a small test hygiene issue.

## What This Review Did NOT Cover

This was synthetic-only. I did not run a real photo/platform end-to-end render. I did not review or test `loop/orchestrate.py` or `loop/tests/test_orchestrate.py`. I did not inspect the live Image_Tagger working tree. I did not perform exhaustive fuzzing, performance testing, or complete JSON Schema validation of every packet/room/camera field. I tested strict agreement primarily at threshold `0.0`; high thresholds can intentionally accept nonzero discrepancy scores by design and were not treated as refutations.

## Scratch Scripts Left On Disk

- `/tmp/codex_v05_attack_lib.py`
- `/tmp/codex_v05_round4_regressions.py`
- `/tmp/codex_v05_marker_attacks.py`
- `/tmp/codex_v05_null_edges.py`
- `/tmp/codex_v05_misc_attacks.py`

Full exact run records and generated verdict files:

- `/tmp/codex_v05_runs/round4_regressions/results.jsonl`
- `/tmp/codex_v05_runs/marker_attacks/results.jsonl`
- `/tmp/codex_v05_runs/null_edges/results.jsonl`
- `/tmp/codex_v05_runs/misc_attacks/results.jsonl`

## Identity And Separation Level

Reviewer identity: Codex, GPT-5 coding agent, acting as non-author adversarial reviewer.

Separation level: independent checker for this round. I did not author v0.5, did not commit, did not modify `/tmp/review_v05`, and did not coordinate with the author side during the review.
