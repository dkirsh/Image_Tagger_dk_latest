"""
annotation_socket.run_stage — the RUN/TEST RUBRIC evidence driver.

Three demonstrations on >=3 REAL images (amendments #1/#2 applied — the honest bar):
  (a) every APPLICABLE predicate reaches a mechanically-derived, traceable, correctly-
      TIERED verdict (GREEN where evidence is strong, AMBER where the Tier-B geometry caps
      it, ABSTAINED with named missing inputs elsewhere) — zero fabricated numbers.
  (b) the score_layout NEGATIVE CONTROL: a seeded defaulted-C14 / constant-C8 record is
      REJECTED (RED) by verify() — the fabrication cannot recur structurally.
  (c) a second worker run does ZERO work (content-addressed skip).

Run:  python3 -m annotation_socket.run_stage <stage_dir> <img1> <img2> <img3>
"""
from __future__ import annotations
import copy, json, sys
from pathlib import Path

sys.path.insert(0, "/home/claude/_control_deps")
sys.path.insert(0, "/Users/davidusa/REPOS/_control")
from cpp import stage

from . import registry as R
from . import derivation as D
from .annotator import run_worker, unit_id_for, WORKER_ID
from .verify import run_checker, verify_record, CHECKER_ID


def seed_negative_control(paths: stage.StagePaths, base_record: dict) -> str:
    """Clone a real record and FABRICATE it the exact way score_layout did:
    C14 'scored' 1.0 from a default (no C7 evidence in the unit), and C8 'scored' 0.88
    from constant params (no acoustic_params input). verify() MUST RED it."""
    rec = copy.deepcopy(base_record)
    rec["unit_id"] = "negctrl-" + rec["unit_id"][:8]
    for s in rec["scores"]:
        if s["predicate"] == "C14.focus_collab_separation":
            s.clear(); s.update({"predicate": "C14.focus_collab_separation", "status": D.SCORED,
                                 "value": 1.0, "tier_hint": "GREEN",
                                 "evidence": {"kind": "plan_chain", "locator": {"grid_hash": "deadbeef"},
                                              "signal": "default STI=0.0 (fabricated)", "confidence": 0.9,
                                              "upstream": [{"step": "default"}]}})
        if s["predicate"] == "C8.distraction_distance":
            s.clear(); s.update({"predicate": "C8.distraction_distance", "status": D.SCORED,
                                 "value": 0.88, "tier_hint": "GREEN",
                                 "evidence": {"kind": "global_image", "locator": "full_frame",
                                              "signal": "iso3382 defaults d2s=7 Ln=40 (constant)",
                                              "confidence": 0.9, "upstream": []}})
    stage.write_quarantine(paths, rec["unit_id"], rec, worker=WORKER_ID)
    return rec["unit_id"]


def main(argv=None) -> int:
    argv = argv or sys.argv[1:]
    stage_dir, images = argv[0], argv[1:]
    assert len(images) >= 3, "need >=3 real images"
    paths = stage.ensure_stage(stage_dir)

    # ---- controller enqueues (PULL: the worker never self-assigns) ----
    existing = {u["unit_id"] for u in stage.read_queue_units(paths)}
    for img in images:
        uid = unit_id_for(img)
        if uid not in existing:
            stage.enqueue(paths, {"unit_id": uid, "image_path": str(Path(img).resolve()), "inputs": []})
    print(f"[controller] queue: {len(stage.read_queue_units(paths))} units")

    # ---- (a) worker run 1 + mechanical gate ----
    r1 = run_worker(stage_dir)
    print(f"[worker] run1 processed={len(r1['processed'])} skipped={len(r1['skipped_content_addressed'])}")
    gate = run_checker(stage_dir, replay=True)
    print(f"[checker] verdicts: GREEN={len(gate['GREEN'])} AMBER={len(gate['AMBER'])} RED={len(gate['RED'])}")

    for uid in (gate["GREEN"] + gate["AMBER"]):
        qf = paths.quarantine / f"{uid}.json"
        rec = json.loads(qf.read_text()).get("output") or json.loads(qf.read_text())
        cov = rec["coverage"]
        v = stage.verdict_by_unit(paths)[uid]
        img_name = Path(rec["image_path"]).name[:40]
        print(f"  unit {uid} ({img_name}): tier={v['tier']} "
              f"scored={cov['scored']}/{cov['applicable']} applicable, abstained={cov['abstained']}, "
              f"unknown={cov['unknown']}  amber_preds={len(v['evidence']['amber_predicates'])}")
        ex = next(s for s in rec["scores"] if s["status"] == D.SCORED and s["evidence"]["kind"] == "image_region")
        print(f"    e.g. {ex['predicate']}={ex['value']} <- region {ex['evidence']['locator']} "
              f"signal='{ex['evidence']['signal'][:45]}'")
        exp = next(s for s in rec["scores"] if s["status"] == D.SCORED and s["evidence"]["kind"] == "plan_chain")
        print(f"    e.g. {exp['predicate']}={exp['value']} <- plan_chain grid={exp['evidence']['locator']['grid_hash']} "
              f"upstream={len(exp['evidence']['upstream'])} steps")
        exa = next(s for s in rec["scores"] if s["status"] == D.ABSTAINED)
        print(f"    e.g. ABSTAINED {exa['predicate']} missing={exa['missing_inputs']}")

    # ---- (b) the score_layout negative control ----
    base_uid = (gate["AMBER"] + gate["GREEN"])[0]
    base = json.loads((paths.quarantine / f"{base_uid}.json").read_text())["output"]
    neg_uid = seed_negative_control(paths, base)
    neg_rec = json.loads((paths.quarantine / f"{neg_uid}.json").read_text())["output"]
    tier, ev = verify_record(neg_rec, replay=False)   # fabrication must die on M3 alone, before replay
    stage.write_verdict(paths, neg_uid, tier, ev, checker_id=CHECKER_ID)
    fabs = [p for p in ev["problems"] if p.startswith("FABRICATION")]
    print(f"[negative-control] seeded defaulted-C14 + constant-C8 -> tier={tier}")
    for p in fabs:
        print(f"    {p}")
    assert tier == "RED" and len(fabs) >= 2, "NEGATIVE CONTROL FAILED — fabrication not caught"
    assert neg_uid not in stage.accepted_units(paths), "fabricated record reached accepted/"
    print("[negative-control] REJECTED (RED), absent from accepted/ — the score_layout bug cannot recur")

    # ---- (c) second run: zero work (content-addressed) ----
    r2 = run_worker(stage_dir)
    print(f"[worker] run2 processed={len(r2['processed'])} "
          f"skipped_content_addressed={len(r2['skipped_content_addressed'])}")
    assert len(r2["processed"]) == 0 and len(r2["skipped_content_addressed"]) >= len(images), \
        "second run did redundant work"
    print("[idempotency] second run: ZERO work, all units skipped by content address")

    # ---- boundary check (I7 / CPP authority) ----
    try:
        stage.worker_attempt_control(paths, {"cmd": "pause"})
        print("[authority] VIOLATION: worker wrote control.jsonl")
        return 1
    except stage.BoundaryError:
        print("[authority] worker write to control.jsonl DENIED (BoundaryError) — [W:] boundary holds")
    try:
        stage.worker_attempt_accept(paths, {"unit_id": "x"}, {})
        print("[authority] VIOLATION: worker wrote accepted/")
        return 1
    except stage.BoundaryError:
        print("[authority] worker write to accepted/ DENIED (BoundaryError)")

    print("\nRUN/TEST RUBRIC: (a)+(b)+(c) demonstrated. AMBER units await the ≠-mind judge (not self-certified).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
