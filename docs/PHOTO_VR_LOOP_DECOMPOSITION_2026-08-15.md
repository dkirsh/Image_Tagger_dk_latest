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
  sign-off). **Version:** `render-verdict/v0.1`, carried in every artifact.
- **Breaking change protocol:** version bump + a ledger/status-board announcement BEFORE
  any producer or consumer changes — announce-and-reconcile, never a silent push.

**Render packet — producer writes `iter_<k>/render/`:**
- `render.png` (RGB, target's aspect); `room.json` (validates against
  `room.v0_3.schema.json` [verified]); `camera.json`
  `{position_m, look_at_m, fov_deg, image_wh}`;
- `packet.json` `{contract_version: "render-verdict/v0.1", run_id, iter, target_image_id,
  produced_utc, sha256: {render_png, room_json, camera_json}}`

**Verdict — comparator writes `iter_<k>/verdict/`, canonical JSON, byte-identical re-runs:**
- `verdict.json` `{contract_version: "render-verdict/v0.1",
  built_against: "<producer contract_version echoed>",  ← the dependency check: the
  comparator REFUSES (fail-closed) a packet whose contract_version it was not built
  against, rather than guessing;
  run_id, iter, target_image_id, input_sha256: {…},
  wall_layout_diff: {target_walls, render_walls, opening_mismatches:
    [{opening_id, expected_wall, rendered_wall}]},
  object_diff: {matched, missing_in_render, extra_in_render,
    moved: [{object_id, bbox_target, bbox_render, offset_px}]},
  discrepancy: {score, components, calibration: "exploratory_uncalibrated"},  ← never
    treated as truth (`resemblance_used_as_evidence` refusal),
  verdict: "CONTINUE" | "BELOW_THRESHOLD" | "CAP_REACHED_FLAGGED"}`
- Loop end: `hitl.json` per `reconstruction-critique.schema.json` [verified] +
  `{who, when_utc, run_id, iter}`.

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
