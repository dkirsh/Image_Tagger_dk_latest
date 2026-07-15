# SOCKET_CONFORMANCE — the vision-annotation pipeline as a night-nurse socket

**Repo root (verified exists): `/Users/davidusa/REPOS/Image_Tagger_dk_latest`**
*Pipeline: `annotation_socket/` (this package), predicates from `cnfa_algs/`. Shared libraries ADOPTED, not
reimplemented: `cpp.stage` (Codex CPP-1, `/Users/davidusa/REPOS/_control/cpp/stage.py`, landed 2026-07-15 and
imported directly) and the I7 sentinel from `/Users/davidusa/REPOS/_control/supervisor/trusted_derivation.py`.
Built 2026-07-15 (Fable/Cowork) per the annotation-socket prompt, with two DAVID-APPROVED amendments:
(#1) tri-state SCORED/ABSTAINED/UNKNOWN with coverage over the APPLICABLE set — verify() audits every
abstention so a failure cannot be laundered as one; (#2) the evidence bar is "every applicable predicate
correctly TIERED and traceable, zero fabricated values," not "all predicates GREEN" — GREEN is an outcome of
evidence, not a target. Amendment (#3): evidence is a derivation CHAIN (image→geometry→plan→value) for plan
metrics, a pixel region for image attributes.*

---

## 1. The 8 socket properties → the exact implementation

| # | Property | Implementation (file:line, verified this session) |
|---|---|---|
| 1 | **UNITIZED** | unit = one image; sub-unit = one (image, predicate) pair. `annotator.annotate_image` (annotator.py:51) emits one record per unit containing one entry per registry predicate — 37 sub-units/unit, each SCORED/ABSTAINED/UNKNOWN, never a monolith. Contract = `registry.PREDICATES` (registry.py:44–98: requires/audit_class/tier_hint declared as data); success-conditions = verify M1–M5. |
| 2 | **PULL-DRIVEN** | `annotator.run_worker` (annotator.py:167) claims from the controller-written `queue.jsonl` via `cpp.stage.claim` — `O_CREAT\|O_EXCL` atomic (stage.py:176–180). The worker never enqueues; enqueue is controller-role only (run_stage.py:62 `stage.enqueue`). |
| 3 | **OBSERVABLE** | `stage.emit_event` started/heartbeat/done/failed with coverage counts (annotator.py:184–197); liveness/coverage computable from `events.jsonl` alone — no screen-scraping. |
| 4 | **PROVENANCE-CARRYING** | every SCORED value ships evidence: image attrs → `image_region` bbox of the field's hottest tile + producing signal + confidence (annotator.py:38–48, 96–101); plan metrics → `plan_chain` {grid_hash, free_cells} + the 4-step upstream geometry chain (vp → segment_planes → depth → plan; annotator.py:76–84, 103–105). Constructor-enforced: `derivation.scored` (derivation.py:70) REFUSES to build a value without valid evidence — it returns UNKNOWN instead. **This is the score_layout fix made structural.** |
| 5 | **GATED FAIL-CLOSED** | output lands in `quarantine/` (annotator.py:191); nothing reaches `accepted/` except through `verify.run_checker` (verify.py:126) — mechanical-primary M1 replay / M2 evidence / M3 dependency-fabrication / M4 abstention-audit / M5 coverage (verify.py:54–116). Any UNKNOWN, fabrication, invalid region, replay mismatch, or applicable-coverage gap ⇒ RED. The ≠-mind inference judge is ADVISORY on AMBER (SPEC-2). |
| 6 | **CHECKER≠AUTHOR BY TOPOLOGY** | producer=`cnfa-annotator` writes only events/claims/quarantine; checker=`verify-mechanical` writes verdicts; only the controller role writes `accepted/` — enforced by `stage.assert_can_write` (stage.py:141), raising `BoundaryError` (demonstrated, §3). Verify's core is author-neutral: M1 REPLAYS the value from image bytes (verify.py:46–51) — it checks the world, not the author's assertions — and its tests CAN fail (the negative control fails it by construction). |
| 7 | **CONTENT-ADDRESSED** | `unit_id = sha256(image_bytes + MODEL_VERSION)[:16]` (annotator.py:31); accepted outputs hash-named by `stage.accept_output` (stage.py:260); re-run skips verdicted/accepted units BEFORE claiming (annotator.py:172–181) — zero redundant work, demonstrated §3(c). |
| 8 | **TIERED-ESCALATING** | GREEN/AMBER/RED conditions are DATA: per-predicate `tier_hint` evidence ceilings in the registry (a Tier-B-geometry predicate can never self-claim GREEN — registry.py:56–76) + the verdict rules in verify.py:24–28,103–118. RED ⇒ stays quarantined ⇒ digest; AMBER ⇒ awaits ≠-mind; GREEN ⇒ accepted. |

**The trust chokepoint (I7 for predicates).** `derivation.py` is the single constructor for every believed
number: `scored()` (evidence-mandatory, finite-value-mandatory) / `abstain()` (names the exact missing
inputs) / `unknown()` (fail-closed). It imports the sentinel from the extraction controller's
`trusted_derivation.py`, so both controllers speak one trust vocabulary: **a value only exists if
mechanically derived; a defaulted/constant/absent score is UNKNOWN → RED, never a "believed" number.**

## 2. The 6 CPP conformance checks

The shared harness (`/Users/davidusa/REPOS/_control/cpp/conformance.py`) was run in this sandbox against the
adopted `cpp.stage` library: **6/6 PASS + negative gate PASS** (schedule+claim incl. forced-race no-double-claim;
observe; gate incl. seeded-BAD→RED and coverage<100%⇒batch-RED; liveness≠progress→`SPEND_DEAD_SUSPECTED`;
kill-mid-run resume with zero redundant work; authority-I7). This pipeline uses that same library for every
artifact, and re-demonstrates on its own stage: **schedule+claim** (3 units enqueued controller-role, claimed
O_EXCL), **observe** (started/heartbeat/done per unit in `events.jsonl`), **gate** (negative control RED, never
accepted), **resume** (run-2 zero work), **authority** (worker `control.jsonl`/`accepted/` writes DENIED) — §3.
*Liveness≠progress lives in the supervisor/controller loop (progress = `accepted/` growth), i.e. above this
worker, per the CPP trust split; the harness run covers it.*

## 3. RUN/TEST RUBRIC evidence (real run, 2026-07-15, sandbox)

CMD: `python3 -m annotation_socket.run_stage /tmp/anno-stage <3 real images from "Example Images/">`
```
[controller] queue: 3 units
[worker] run1 processed=3 skipped=0
[checker] verdicts: GREEN=0 AMBER=3 RED=0
  unit 1d4efdd9a0c1cab5 (korridor.jpg): tier=AMBER scored=19/19 applicable, abstained=18, unknown=0  amber_preds=10
    e.g. cnfa.light.brightness_variance=0.1277 <- region [640, 26, 643, 29] signal='local luminance SD, 31px window (M1)'
    e.g. C1.visual_integration=0.998 <- plan_chain grid=4286c8fd36888fbe upstream=4 steps
    e.g. ABSTAINED C5.collaborator_proximity missing=['collab_pairs', 'seats']
  unit af72d327025ce732 (Industrial-open-concept-office-project-b): tier=AMBER scored=19/19 applicable, abstained=18, unknown=0
  unit eb2682bc4c9a3703 (Ludwig_Mies_van_der_Rohe__Farnsworth_Hou): tier=AMBER scored=19/19 applicable, abstained=18, unknown=0
[negative-control] seeded defaulted-C14 + constant-C8 -> tier=RED
    FABRICATION:C8.distraction_distance scored but requires ['acoustic_params'] absent from unit
    FABRICATION:C14.focus_collab_separation scored but requires ['collab_sources', 'focus_seats'] absent from unit
[negative-control] REJECTED (RED), absent from accepted/ — the score_layout bug cannot recur
[worker] run2 processed=0 skipped_content_addressed=3
[idempotency] second run: ZERO work, all units skipped by content address
[authority] worker write to control.jsonl DENIED (BoundaryError) — [W:] boundary holds
[authority] worker write to accepted/ DENIED (BoundaryError)
```
**(a)** 19/19 applicable predicates scored on each image, every score traceable (pixel bbox or 4-step plan
chain with grid hash); 18 ABSTAINED with named missing inputs; 0 UNKNOWN; 0 fabricated. Units are honestly
**AMBER**, not GREEN — 10 predicates ride the heuristic Tier-B geometry whose registry ceiling is AMBER, so
they await the ≠-mind judge (amendment #2: all-GREEN would have required mislabeling exactly what the CNfA
panel flagged). The M1 replay pass (deterministic since the S2 seed fix) is what earned the SCORED statuses.
**(b)** the score_layout regression, seeded exactly (defaulted C14=1.0, constant C8=0.88 with high self-claimed
confidence): caught by M3 DEPENDENCY **alone, before replay even runs** — self-reported confidence never
authorizes (I7). RED, quarantined, absent from `accepted/`.
**(c)** second run: zero work; all 3 units skipped by content address before claiming.

## 4. checker≠author — the boundary stated (RULE 0)

**I built both the annotator and verify(); this document is builder-run evidence, NOT certification.** What is
author-neutral by construction: M1 replay re-derives values from image bytes (a fabricated value cannot match)
and the [W:] boundary is enforced by the shared `cpp.stage` library I did not write. What still requires a
≠-mind: (1) run this harness end-to-end (`python3 -m annotation_socket.run_stage <stage> <imgs>`) and the CPP
conformance harness against this stage; (2) the AMBER inference judgments ("does the score follow from the
region?") — a VLM/AG pass, per the L2 validation protocol, never me; (3) adversarial attack on verify() itself
(can a fabricated record be crafted that survives M1–M5? — e.g. a value computed from the image by a DIFFERENT
procedure than claimed would survive replay-by-recompute only if it exactly matches the pinned pipeline, which
is the point, but the ≠-mind should try). **Verified by me:** every CMD/OUT above ran in this sandbox as shown;
determinism of replay (S2 seeding) verified across 4 runs earlier this session. **Not verified:** behaviour on
the Mac's Python/OpenCV versions (pixel-exact replay across environments may need per-environment baselines);
the ≠-mind runs; multi-worker claim races on this stage (covered generically by the CPP harness, not
re-forced here). Never "should work": everything claimed above was executed.
