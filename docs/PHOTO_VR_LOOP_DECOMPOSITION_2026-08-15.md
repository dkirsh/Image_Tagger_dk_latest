# Photo→VR production loop — decomposition proposal (T1.1), v2

*STATUS: **DRAFT v2 — awaiting David's sign-off.** Nothing is enacted by this document.
v2 supersedes v1 after a non-author review (separation level: same-model-fresh-context —
the weakest rung; David remains the decider) found 8 defects in v1, worst being that v1
proposed a split OPPOSITE to one David already decided, without knowing it. All findings
are answered below; the v1→v2 change log is §7.*

*Author: Tanishq (drafted with Claude/Fable; adversarially reviewed by a second Claude
session against the live `_control` clone). Checker ≠ author: **David decides**; **Stephan
confirms** the VR-generation boundary.*

**Frozen subjects [verified]:** `New_VR_Platform` @ `vr-impl/perception-lane` `3fe1d505`;
`Image_Tagger_dk_latest` @ `cnfa-algs-2026-07-14` `084b3f3d`; `_control` @ main
(`lanes.json`, `METHODOLOGY/LANE_MAP_2026-08-14.md`, `METHODOLOGY/METHOD_CARD_v0.1`);
sprint set text as emailed 2026-08-14. `lane_guard.py` semantics verified by execution
(prefix matching at :93; unowned=allowed at :16; empty-commit-allow for dict specs at :117).

## 0 · The decision David actually needs to make

Two of David's own documents disagree about who owns the loop's VR generation:

- **LANE_MAP_2026-08-14.md §Decomposition ("decided 2026-08-14; revisable")** [verified]:
  **Tanishq** owns cycle orchestration + comparison + HITL (in `Image_Tagger_dk_latest`)
  **plus the loop's first-cut VR rendering** in `New_VR_Platform/production_loop/` — a
  path-lane carved to him and **already deployed in `lanes.json`**:
  `{"production_loop/": "tanishq", "*": "stephan"}`. Stated reason: "chosen so Tanishq's
  biggest task is not blocked on a parked track" (Stephan's VR science is parked).
- **TANISHQ_SPRINT_SET_2026-08-14.md §T1.1(b)** [stated — DK]: lanes assigned as "Tanishq:
  orchestration, scene-graph/wall-layout comparison, HITL; **Stephan: VR generation + the
  aligned render**."

These are opposite carves. This proposal recommends **Option 1 (the LANE_MAP carve, as
deployed)** and presents Option 2 as the explicit reversal it would be. David signs one.

## 1 · The loop, as components

| # | Component | What it does | Exists today? |
|---|-----------|--------------|---------------|
| C1 | Target intake | photo + its Tagger scene graph enter a run | partly [verified: scene-semantic-graph.schema.json requires kind, image_id, objects] |
| C2 | VR first cut | scene graph → shell + furniture | machinery exists: `reconstruct.py`, `place_furniture.py`, `photo_to_vr.py` [verified] |
| C3 | Aligned 2D render | render the room from a declared camera pose | partly: `render_semantic_room` / `render_geom.py` [verified]; alignment contract not yet explicit |
| C4 | Comparison | scene-graph diff + wall-layout diff, render vs target | new [proposed] |
| C5 | Cycle orchestration | C2→C3→C4 until threshold or cap; flag non-convergence | new [proposed] |
| C6 | HITL surface | provenanced accept / say-what's-wrong | partly: `photo_to_vr --review`, `critique.py` [verified]; loop wiring new |
| C7 | Run store | on-disk record per iteration (inputs, outputs, hashes) | new [proposed] |

## 2 · Option 1 (RECOMMENDED) — the LANE_MAP carve, already deployed

- **Tanishq:** C1, C4, C5, C6, C7 in `Image_Tagger_dk_latest/loop/` [proposed subtree,
  his whole-repo lane]; **and C2+C3 loop-specific code in
  `New_VR_Platform/production_loop/`** — the subtree `lanes.json` already carves to him.
  `production_loop/` **does not exist in the repo tree yet** [verified: absent at
  `3fe1d505`] — the carve precedes its contents; first commit creates it. Code there may
  *call* Stephan's `src/vr_condition_audit/` modules but never edits them.
- **Stephan:** everything else in `New_VR_Platform` (`"*": "stephan"`) — his parked VR
  science, untouched.
- **lanes.json change required: NONE.** This split is enforced TODAY — proven live by the
  Q0 probes (root-file commit as tanishq REFUSED exit=1; `production_loop/` file commit
  ACCEPTED exit=0; ledger row sprint0.1, 2026-08-19).
- Known limitation carried from Q0 Finding 1: in path-level repos an **empty** commit is
  accepted regardless of lane (`lane_guard.py:117`).
- Why recommended: it is the split David already chose, for a reason that still holds
  (Stephan's track is parked), and it is the only option with zero enactment risk.

## 3 · Option 2 — the sprint-set carve (an explicit reversal of LANE_MAP)

Stephan owns VR generation + aligned render (un-parking his track); Tanishq owns only
C1/C4/C5/C6/C7 in his own repo; no Tanishq path in `New_VR_Platform`. Enactment would
require editing `lanes.json` to remove `production_loop/` or reassign it to stephan —
exactly **one** changed entry, written as a **plain prefix string with no globs**
(the guard does prefix matching, not glob matching: a `**` key matches nothing real and,
with no `*` default, silently makes the whole repo unowned-and-allowed — defect found and
killed in v1 review, finding 3). Cost: Tanishq's biggest task becomes blocked on Stephan
un-parking — the dependency LANE_MAP §Decomposition says it was designed to avoid.
Proposed only if David wants Stephan running VR generation this fall.

## 4 · The exchange root (shared data, no shared code)

`loop_runs/<run_id>/iter_<k>/` holds render packets and verdicts. The guard **has no
shared-lane concept** — a `"shared-data"` pseudo-lane blocks BOTH lanes (verified by
executing `decide()`; v1 finding 4). Therefore the exchange root lives **outside every
lane-managed repo** (proposed: a Drive-synced `Image_Collections/loop_runs/` or a lab-
machine path David names) — deliberately unmanaged, recorded HERE as a decision rather
than left as an implicit absence. If David wants shared paths *declarable* inside managed
repos, that is a `lane_guard.py` feature request for the guard's owner, out of this doc's
scope. `run_id = <image_id>_<YYYYMMDD>_<seq>`.

## 5 · The render↔verdict interface — a versioned contract (LANE_MAP seam rules)

Per LANE_MAP §"Path isolation is not interface safety", every seam needs an owner, a
versioned contract, a dependency check, and breaking-change notification. All four:

- **Contract owner:** Tanishq (under Option 1 both sides are his lane; under Option 2 the
  contract stays Tanishq-owned, Stephan implements the producer side — David confirms at
  sign-off). **Version:** `render-verdict/v0.5`, carried in every artifact.
- **Breaking change protocol:** version bump + a ledger/status-board announcement BEFORE
  any producer or consumer changes — announce-and-reconcile, never a silent push.

**Render packet — producer writes `iter_<k>/render/`:**
- `render.png` (RGB, target's aspect); `room.json` (validates against
  `room.v0_3.schema.json` [verified]); `camera.json`
  `{position_m, look_at_m, fov_deg, image_wh}`;
- `packet.json` `{contract_version: "render-verdict/v0.5", run_id, iter, target_image_id,
  produced_utc, sha256: {render_png, room_json, camera_json}}` — `run_id` and
  `target_image_id` must be non-empty strings, `produced_utc` a non-empty string, and `iter`
  an integer `>= 0`. These are type-checked, not merely required; a malformed manifest is
  refused with exit 2 rather than carried into the verdict.
- **Producer requirements, all needed for a verdict that can reach agreement:**
  1. `room.json` apertures carry the platform's `ap<i>` ids (`reconstruct.py:148`), spelled
     exactly as the platform writes them — matched against `^ap(0|[1-9][0-9]*)\Z`, so
     `ap00`, `ap0 `, and `ap0\n` are all rejected as not-the-platform-spelling and drop the
     packet to `multiset_fallback`. Gaps in the sequence are legitimate: non-structural
     kinds keep their source indices.
  2. Each furniture entry carries the source object `id` and `_source_bbox`
     (`place_furniture.py:115-120`), the latter being the target object's `object_bbox`
     echoed back. Without them a moved object cannot be detected.
  3. **Furniture `id` and `category` must be STRINGS.** Identity matching performs no type
     coercion at all, so a numeric or null id no longer quietly matches its string spelling;
     it degrades to `multiset_fallback`. An unreadable category becomes a display-only
     marker that can never enter the match set, even if a target category happens to equal
     the marker text.
  4. Absent any of these, the comparator degrades rather than guesses: openings fall to
     `multiset_fallback` and no kind with two or more target openings can be reported as
     agreeing; objects fall to category multisets and every matched category is recorded in
     `identity.position_unverified`.
- **The null policy, decided once and applying everywhere (v0.5).** A present JSON `null` is
  never treated as absent. On a leaf claim such as `object_bbox` it is an *unreadable claim*,
  so the object lands in `position_unverified` and strict agreement is blocked. On a
  container — target `openings`/`objects`, room `apertures`/`furniture` — it is a *malformed
  document* and the whole packet is refused with exit 2. Only a genuinely missing key counts
  as absent, and only an absent key owes nothing. This is a decision rather than a discovery,
  and David may override it; it interacts with the schema-versus-fixture question below.

**Verdict — comparator writes `iter_<k>/verdict/`, canonical JSON, byte-identical re-runs:**
- `verdict.json` `{contract_version: "render-verdict/v0.5",
  built_against: "<producer contract_version echoed>",  ← the dependency check: the
  comparator REFUSES (fail-closed) a packet whose contract_version it was not built
  against, rather than guessing;
  run_id, iter, target_image_id, input_sha256: {…},
  agreement_policy: "strict" | "allow_unverified",  ← strict is the default; see below,
  wall_layout_diff: {target_openings, render_apertures, opening_mismatches:
    [{opening_id, expected_wall, rendered_wall}], extra_render_apertures},
  object_diff: {matched, missing_in_render, extra_in_render,
    moved: [{object_id, bbox_target, bbox_render_source, offset_norm}]},
  identity: {mode: "exact" | "multiset_fallback" | "vacuous", unverifiable_kinds: [...],
    objects_mode: "exact" | "multiset_fallback" | "vacuous", position_unverified: [...]},
    ← vacuous means nothing was claimed on that axis by either side: allowed to agree,
      never dressed up as "exact",
  discrepancy: {score, components: {opening_wall_mismatch_frac, extra_aperture_frac,
    object_missing_frac, object_extra_frac, object_moved_frac},
    calibration: "exploratory_uncalibrated"},  ← never
    treated as truth (`resemblance_used_as_evidence` refusal),
  verdict: "CONTINUE" | "BELOW_THRESHOLD" | "CAP_REACHED_FLAGGED"}`
- The verdict is canonical JSON under RFC 8259 strictly: a non-finite number anywhere in it
  is a refusal, never a `NaN` token written into the artifact.
- **`agreement_policy`, and the one decision it hands David.** Under `strict`, the default,
  `BELOW_THRESHOLD` requires that identity was actually established on both sides — exact
  aperture ids with no `unverifiable_kinds`, exact object ids, and an empty
  `position_unverified`. A packet that simply omits ids can therefore never be reported as
  agreeing, even when nothing in it visibly disagrees, because the comparator was never in a
  position to tell. `allow_unverified` relaxes that for stub or foreign producers.
  Strict is recommended, since the real producer always emits ids and `_source_bbox`. David
  confirms or overrides.
- Loop end: `hitl.json` per `reconstruction-critique.schema.json` [verified] +
  `{who, when_utc, run_id, iter}`.

**v0.1 → v0.5 (2026-08-21), announced per this section's own breaking-change protocol**
(`_control` ledger, superseding each earlier announcement in turn). Any producer still on
v0.1 migrates straight to v0.5: v0.2 was announced but never landed in a commit, and v0.3 and
v0.4 were each superseded within a day, so no producer ever had a packet to build against
until now. The comparator refuses every earlier version rather than comparing across them.

Four rounds of different-lineage non-author review by Codex drove this, and each round found
what the previous fix had not thought of.

Round 1 (`…ATTACK_2026-08-20.md` @ `ae160481`) broke v0.1: a same-kind wall permutation and an
invented aperture both reported agreement. Round 2 (`…V02…` @ `d50d9fb1`) broke v0.2: a chair
moved clear across the room still scored 0.0, because `object_diff.moved` had been specified
here since v0.1 and emitted as `[]` throughout — a field promised in the contract and never
populated fails more quietly than one that is wrong, not less badly. Round 3 (`…V03…` @
`ad6c8037`) broke v0.3: a target `object_bbox` that was present but malformed, or mis-keyed as
`bbox_xywh`, was silently skipped as "no position claim", and `str()` coercion let `7` match
`"7"`. Round 4 (`…V04…` @ `95c071af`) broke v0.4 on three more: a present `object_bbox: null`
read as absent, render-side category coercion that had survived the round-3 sweep, and an
aperture id `"ap0\n"` accepted as exact because Python's `$` matches before a trailing
newline.

The pattern across rounds is worth naming, because it shaped v0.5. Each fix enumerated the bad
shapes someone had thought of, and the next round arrived with the shape nobody had. So v0.5
stops enumerating: the bbox test asks whether the *key is present*, not whether the value is
one of a list of known-bad things, and the null policy above settles a whole class of
questions in one decision rather than case by case.

This section changed too, not only the code. Earlier revisions named
`target_walls` / `render_walls` where the schema and implementation used
`target_openings` / `render_apertures` — where prose and schema disagree, the schema wins. And
`moved` entries carry `bbox_render_source` and `offset_norm` rather than the `bbox_render` and
`offset_px` once specified here, because what the producer can honestly echo is the source
bbox it placed from, not a rendered-pixel measurement nobody computes.

**Review protocol, adopted after a failure of ours (v0.4).** During round 3 the working tree
was edited underneath the review, so the report described a file that no longer existed by the
time it landed. The review subject is now a **committed hash**, checked out detached, and the
author stays hands-off until the artifact lands. A finding that reproduces only outside the
hash is a protocol violation rather than a finding.

Stub-level test: either side can be faked with hand-written files; T1.2's negative
control (wrong-wall render → non-empty `opening_mismatches`, never "agreement") runs
against a stub packet before any producer code exists.

## 6 · Method block

- **Claim:** §1's seven components cover the loop with no unowned seam under either
  option, and §5 is concrete enough that a checker could stub both sides today.
- **Refutation:** name a loop step belonging to no component, or a field a stub would
  need that §5 omits. Either kills the proposal as written.
- **Negative control:** hand §5 and a deliberately wrong-wall stub packet to someone with
  no other context; if they cannot produce the expected non-empty `opening_mismatches`
  without asking questions, the interface is underspecified → revise.
- **One-example-first [stated — DK]:** the single render↔verdict hop goes to David before
  the whole cycle is built.
- **Threshold ownership:** David sets the discrepancy threshold after seeing baseline
  numbers (a threshold chosen by the comparator's author would self-certify).

## 7 · v1 → v2 change log (answers to the non-author review, findings 1–8)

1. v1's "Variant A" unknowingly reversed LANE_MAP's decided carve → restructured as
   Option 1 (decided carve, recommended) vs Option 2 (explicit reversal); the sprint-set ↔
   LANE_MAP contradiction is now §0, the first thing David sees.
2. False claim "repo-level lanes already enforce it" deleted; `lanes.json` is path-level
   for New_VR_Platform and already enforces the decided carve.
3. All `**` glob entries deleted (guard is prefix-match; `**` + no `*` default would have
   silently unmanaged the repo). Option 2's single entry is a plain prefix string.
4. `"shared-data"` pseudo-lane deleted (blocks both lanes, verified by execution);
   exchange root moved outside managed repos and recorded as a decision.
5. "Four entries…exactly as listed" (which listed six) deleted; Option 1 needs zero
   entries, Option 2 exactly one.
6. Seam upgraded to the LANE_MAP's four requirements: named owner, `contract_version`,
   `built_against` dependency check (fail-closed), breaking-change protocol.
7. `production_loop/` absence from the tree now stated in §2, not left as inference.
8. Path-level empty-commit acceptance noted as a known limitation in §2.

*RECORD step: this file must be committed (branch `tanishq/loop-decomposition`) before it
is cited anywhere as an artifact — "if it isn't recorded, it didn't happen."*
