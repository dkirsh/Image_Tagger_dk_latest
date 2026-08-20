VERDICT: BROKEN

2. Subject and scope

Reviewed commit: `60d938df0007426e5a7f67a992041177e7dca429`.

Review subject was only `/tmp/review_v04/loop/` at the detached checkout. I did not read or test the live `~/Documents/GitHub/Image_Tagger_dk_latest` working tree. I read only the prompt-allowed frozen `New_VR_Platform` context files for mirror comparison, not as review subject. No lasting files were modified under `/tmp/review_v04`; generated Python cache was removed and `git status --short --branch` ended as `## HEAD (no branch)`.

Baseline command:

```text
cd /tmp/review_v04 && PYTHONPATH=. python3 loop/tests/test_run_loop_compare.py
```

Observed baseline output: `29/29 passed`. `pytest` itself was not installed (`No module named pytest`), so I used the test file's stdlib runner.

3. Round-3 regression results

All round-3 probes were rebuilt as `render-verdict/v0.4` packets by `/tmp/codex_v04_attacks.py`. Full JSONL rows, including exact target and room inputs plus observed outputs, are in `/tmp/codex_v04_attacks_output.jsonl`.

| Round-3 item | Exact attack input | Exact observed output | Result |
|---|---|---|---|
| R3-1 malformed or mis-keyed target bbox sweep | Target object `{"id":"o1","category":"chair","object_bbox":<value>}` with `<value>` = string `"0.1,0.6,0.1,0.2"`, short list `[0.10,0.60,0.10]`, long list `[0.10,0.60,0.10,0.20,0.30]`, non-numeric `[0.10,0.60,0.10,"x"]`, NaN, Infinity, bool `[0.10,0.60,0.10,true]`, mapping `{"x":0.10,"y":0.60}`; and mis-keyed object `bbox_xywh:[0.10,0.60,0.10,0.20]`. Room furniture was exact id/category with `_source_bbox:[0.10,0.60,0.10,0.20]`. | Every malformed/miskeyed row returned `code=0`, `verdict=CONTINUE`, `identity=exact/exact`, `position_unverified=["o1"]`, `score=0.0`. Genuinely absent bbox returned `code=0`, `verdict=BELOW_THRESHOLD`, `position_unverified=[]`. | Closed for the swept shapes, but reopened for present `object_bbox:null` in section 4. |
| R3-2 target identity refusal | Target object identities: `id:7`, `id:null`, `id:""`, `category:7`, `category:null`, `category:""`. | `id` cases returned `code=2`, `REFUSED: target object 0 id must be a non-empty string (scene schema)`. `category` cases returned `code=2`, `REFUSED: target object 0 category must be a non-empty string (scene schema)`. | Closed for target-side id/category. |
| R3-2 render furniture id degradation | Render furniture ids `7`, `null`, and `""` against string target ids. | All returned `code=0`, `verdict=CONTINUE`, `objects_mode=multiset_fallback`; non-empty category matches landed in `position_unverified=["chair"]` and strict mode did not reach `BELOW_THRESHOLD`. | Closed for render furniture id type. |

4. Attacks on R3-1 symmetry and absent-vs-malformed boundary

Finding V04-1: present `object_bbox:null` is treated as genuinely absent, so strict mode can falsely agree.

Exact attack input:

```json
{
  "target": {
    "image_id": "codex",
    "openings": [{"kind": "door", "bbox_xywh": [0.5, 0.55, 0.06, 0.35]}],
    "objects": [{"id": "o1", "category": "chair", "object_bbox": null, "evidence": {}}]
  },
  "room": {
    "schema_version": "0.3",
    "apertures": [{"id": "ap0", "kind": "door", "wall": "north"}],
    "furniture": [{"id": "o1", "category": "chair", "_source_bbox": [0.1, 0.6, 0.1, 0.2]}]
  },
  "threshold": 0.0,
  "allow_unverified": false
}
```

Exact observed output:

```text
name=r3_1_present_null_target_bbox_boundary
code=0
message=verdict BELOW_THRESHOLD score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=exact/exact policy=strict sha256=6ef8f84633d238ac0aff5da3bbba78ed31352a4a71b491ba5b11f93fb8dd0198 -> ...
observed.identity={"mode":"exact","objects_mode":"exact","position_unverified":[],"unverifiable_kinds":[]}
observed.object_diff={"matched":["chair"],"missing_in_render":[],"extra_in_render":[],"moved":[]}
observed.verdict=BELOW_THRESHOLD
```

This violates the v0.4 header claim that a target `object_bbox` that is present but malformed lands in `identity.position_unverified` and blocks strict agreement. The cause is `/tmp/review_v04/loop/run_loop_compare.py:352-354`: `tobj.get("object_bbox")` collapses a present JSON null to `None`, then the code treats `tb is None and "bbox_xywh" not in tobj` as genuinely absent without checking whether `"object_bbox"` is actually present.

Render-side symmetry controls behaved correctly: `_source_bbox` short, long, non-numeric, NaN, and null all returned `CONTINUE` with `position_unverified=["o1"]` when the target bbox was valid. Matching position returned `BELOW_THRESHOLD`; moved position returned `CONTINUE` with `moved=[{"object_id":"o1","offset_norm":0.8,...}]`.

5. Attacks on R3-2 type strictness

Finding V04-2: render furniture `category` is still coerced with `str()`, producing strict false agreement.

Exact attack input:

```json
{
  "target": {
    "image_id": "codex",
    "openings": [{"kind": "door", "bbox_xywh": [0.5, 0.55, 0.06, 0.35]}],
    "objects": [{"id": "o1", "category": "7", "evidence": {}}]
  },
  "room": {
    "schema_version": "0.3",
    "apertures": [{"id": "ap0", "kind": "door", "wall": "north"}],
    "furniture": [{"id": "o1", "category": 7}]
  },
  "threshold": 0.0,
  "allow_unverified": false
}
```

Exact observed output:

```text
name=r3_2_render_category_number_coerces_false_agree
code=0
message=verdict BELOW_THRESHOLD score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=exact/exact policy=strict sha256=1ba2876e311497e54e91a2fa25927a60b89847e439c56b0c91a318ee9a038a6c -> ...
observed.identity={"mode":"exact","objects_mode":"exact","position_unverified":[],"unverifiable_kinds":[]}
observed.object_diff={"matched":["7"],"missing_in_render":[],"extra_in_render":[],"moved":[]}
observed.verdict=BELOW_THRESHOLD
```

The null variant also falsely agreed: target `category:"None"` with render `category:null` returned `BELOW_THRESHOLD`, `matched=["None"]`. The code path is `/tmp/review_v04/loop/run_loop_compare.py:342-343`, where both target and render categories are converted through `str()` before comparison; fallback category multisets also use `str()` at lines 372-373. This contradicts the v0.4 claim "No str() coercion anywhere in identity matching" for object category identity.

Finding V04-3: aperture id `"ap0\n"` is accepted as exact and can reach strict `BELOW_THRESHOLD`.

Exact attack input:

```json
{
  "target": {
    "image_id": "ap-ws",
    "openings": [{"kind": "door", "bbox_xywh": [0.5, 0.55, 0.06, 0.35]}]
  },
  "room": {
    "schema_version": "0.3",
    "apertures": [{"id": "ap0\n", "kind": "door", "wall": "north"}],
    "furniture": []
  },
  "threshold": 0.0,
  "allow_unverified": false
}
```

Exact observed output:

```text
name=r3_2_aperture_id_trailing_newline_false_exact
code=0
message=verdict BELOW_THRESHOLD score=0.0 opening_mismatches=0 extra_apertures=0 moved_objects=0 identity=exact/vacuous policy=strict sha256=678d9cf861caafc18a3f9da62453b917f4b711e83ac2a29ff245ee59b9ba0547 -> ...
observed.identity={"mode":"exact","objects_mode":"vacuous","position_unverified":[],"unverifiable_kinds":[]}
observed.verdict=BELOW_THRESHOLD
```

The control with `"ap0 "` returned `CONTINUE`, `mode=multiset_fallback`, so the failure is specifically Python regex end-anchor behavior: `_AP_ID = re.compile(r"^ap(0|[1-9][0-9]*)$")` at line 102 plus `_AP_ID.match(...)` at line 252 accepts a final newline before `$`. A non-platform aperture id is dressed as `exact`.

Target non-string ids/categories are refused as claimed. Render furniture ids that are non-string degrade as claimed. Object id whitespace/case/unicode normalization attacks did not falsely agree: `" o1 "`, `"O1"`, and composed/decomposed `e` forms returned `CONTINUE` with missing+extra object categories.

6. Attacks on `vacuous`

Vacuous is correctly reported, not dressed as exact, when an axis is absent on both sides:

| Case | Exact input | Observed output |
|---|---|---|
| Objects absent both sides | Target has one correct door and no `objects`; room has matching `ap0` door and `furniture:[]`. | `code=0`, `verdict=BELOW_THRESHOLD`, `identity=exact/vacuous`, `score=0.0`. |
| Openings absent both sides | Target has `objects:[{"id":"o1","category":"chair"}]` and no openings; room has no apertures and matching furniture. | `code=0`, `verdict=BELOW_THRESHOLD`, `identity=vacuous/exact`, `score=0.0`. |

Nulled render axes did not erase target-side claims: `furniture:null` against a target object returned `CONTINUE` with `missing_in_render=["chair"]`; `apertures:null` against a target opening returned `CONTINUE` with a `MISSING` opening mismatch.

Observed vacuous boundary risk: target `objects:null` with empty render furniture returned `BELOW_THRESHOLD`, `identity=exact/vacuous`. If a present JSON null is considered malformed rather than absent, this is a false-vacuous path. I am not using it as primary breakage because the prompt explicitly notes a schema-vs-fixture conflict and the comparator currently allows absent object axes. It should be decided explicitly.

Non-structural target opening `{"kind":"artwork"}` with empty render apertures returned `identity=vacuous/vacuous`, `BELOW_THRESHOLD`; this matches the frozen platform rule that non-structural openings are skipped.

7. Fresh findings, determinism, RFC 8259, mirror divergence, test overclaims

Fresh strict false agreements found:

| ID | Summary | Strict result |
|---|---|---|
| V04-1 | Target object `object_bbox:null` present but treated absent. | `BELOW_THRESHOLD`, `position_unverified=[]`. |
| V04-2 | Render category `7` matched target category `"7"` through `str()`. | `BELOW_THRESHOLD`, `objects_mode=exact`. |
| V04-3 | Aperture id `"ap0\n"` matched platform id `ap0` due regex `$`/`match`. | `BELOW_THRESHOLD`, `mode=exact`. |

Determinism/RFC 8259 command:

```text
cd /tmp/review_v04 && PYTHONPATH=. python3 /tmp/codex_v04_verdict_audit.py > /tmp/codex_v04_verdict_audit_output.jsonl
jq -e . /tmp/codex_v04_verdict_audit_work/v1/verdict.json
```

Observed: two identical runs produced byte-identical verdicts with `sha256=c3eb414b6f613db37ef1b4a519c351ae7dc8fdca62d75b317f151bfc1bb0b4e1`; strict Python JSON parse succeeded; recursive non-finite scan was true; canonical round-trip was identical; `jq` returned `jq_ok`. No RFC 8259-invalid verdict artifact was found in these attacks. `jsonschema` was not installed, so schema validation by that library was not executed.

Schema/comparator divergence: `loop/schemas/render-packet.schema.json:21-23` says `iter` has `"minimum": 0`, but `load_packet()` accepts `iter:-1`. Exact observed audit row: `packet_manifest_iter=-1`, `code=0`, `verdict=BELOW_THRESHOLD`, output verdict `iter=-1`. This is not a render false-agreement by itself, but it is a schema-invalid packet being accepted.

Mirror context: the frozen platform context still matched the wall rule and `ap<i>` source-index id rule I checked (`reconstruct.py:64-73`, `127-149`). Furniture context showed `_source_bbox` copied from `object_bbox` at `place_furniture.py:119`. I did not find a wall-rule divergence in the subject. I did note the platform context line `place_furniture.py:116` still string-coerces furniture ids, while v0.4's comparator contract is now type-strict on identity; because target non-string ids are refused before a match, I did not count this as a separate false agreement.

Test overclaims/gaps: the stdlib runner reported 29 tests, not 24. The R3 malformed target bbox test covers string, short, non-numeric, NaN, bool, and mapping, but misses present `object_bbox:null` and long-list in the committed test body. The R3-2 tests cover target id/category type and render id type, but do not cover render category type coercion or aperture trailing-newline ids.

8. What this review did NOT cover

This was synthetic-only. I did not run a real-photo render loop, did not inspect or test `orchestrate.py` or `tests/test_orchestrate.py`, did not execute the live Image_Tagger working tree, did not run the full New_VR_Platform producer, and did not calibrate the exploratory discrepancy score. I did not fuzz exhaustively; the attack set was 42 comparator cases plus the baseline tests and the deterministic/RFC audit. `jsonschema` was unavailable in this environment, so schema validation was limited to reading the schema text and executing comparator behavior.

9. Scratch scripts and evidence left on disk

Scratch scripts:

```text
/tmp/codex_v04_attacks.py
/tmp/codex_v04_verdict_audit.py
```

Evidence outputs:

```text
/tmp/codex_v04_attacks_output.jsonl
/tmp/codex_v04_verdict_audit_output.jsonl
/tmp/codex_v04_verdict_audit_work/v1/verdict.json
/tmp/codex_v04_verdict_audit_work/v2/verdict.json
/tmp/codex_v04_verdict_audit_work/negative_iter_verdict/verdict.json
/tmp/codex_v04_jq_verdict_parse.txt
```

10. Identity and separation level

Reviewer identity: Codex, OpenAI GPT-5 coding agent.

Separation level: adversarial non-author review. I did not author the comparator changes, did not commit, and did not modify the review subject. The report was written directly to `/tmp/codex_v04_report.md` for the author side to move and commit.
