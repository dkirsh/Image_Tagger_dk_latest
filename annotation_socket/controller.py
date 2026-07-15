"""
annotation_socket.controller — a REAL controller loop driving THIS vision pipeline.

The point (David, 2026-07-15): integrate Cowork's already-built vision pipeline with a
controller DESIGNED to control it, end-to-end, to learn the requirements on each side.
Unlike run_stage.py (a linear demo driver), this is the CONTROLLER ROLE as a loop:
  schedule(enqueue) -> observe(events) -> drive worker -> gate(checker) ->
  route: GREEN->accept_output / AMBER->escalate-to-≠-mind / RED->digest -> resume -> audit.

★ INTEGRATION FINDING (confirmed by reading, 2026-07-15): the CPP ABI does NOT pin the
unit-identity field. Cowork's worker reads unit["unit_id"] (annotator.py:176) and hand-rolls
its pull loop because stage.claim_next reads unit["id"] (stage.py:311); stage.accept_output /
unit_by_id also read unit["id"]. So NO single key satisfies both sides. This controller
therefore enqueues DUAL-KEYED units {"id": uid, "unit_id": uid} as a TEMPORARY BRIDGE so the
integration runs today. The permanent fix is CPP-1g: pin ONE canonical identity key in the ABI
+ a conformance check that round-trips a real pipeline's unit through claim_next->accept_output.
When that lands, delete the dual-key bridge and enqueue {"id": uid} only.

UNRUN (this session's Bash is down). Run:
  python3 -m annotation_socket.controller <stage_dir> <img1> <img2> <img3>
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, "/Users/davidusa/REPOS/_control")
from cpp import stage

from .annotator import run_worker, unit_id_for
from .verify import run_checker, CHECKER_ID  # the pipeline's worker + checker, unchanged

CONTROLLER_ID = "anno-controller"


def enqueue_images(paths: stage.StagePaths, images: list[str]) -> int:
    existing = {u.get("id") or u.get("unit_id") for u in stage.read_queue_units(paths)}
    n = 0
    for img in images:
        uid = unit_id_for(img)
        if uid in existing:
            continue
        # DUAL-KEY BRIDGE (see module header): worker reads unit_id, library helpers read id.
        stage.enqueue(paths, {"id": uid, "unit_id": uid,
                              "image_path": str(Path(img).resolve()), "inputs": []},
                      controller_id=CONTROLLER_ID)
        n += 1
    return n


def observe(paths: stage.StagePaths) -> dict:
    """Coverage + liveness from events.jsonl ALONE (no screen-scraping) — the controller's eyes."""
    counts = stage.event_counts(paths)
    return {"started": counts.get("started", 0), "done": counts.get("done", 0),
            "failed": counts.get("failed", 0), "terminal_units": len(stage.terminal_event_units(paths))}


def control_loop(stage_dir: str, images: list[str]) -> int:
    paths = stage.ensure_stage(stage_dir)

    # 1. SCHEDULE
    enq = enqueue_images(paths, images)
    print(f"[controller] scheduled: enqueued={enq} queue={len(stage.read_queue_units(paths))}")

    # 2. DRIVE WORKER (pull-side runs; controller does not annotate)
    w1 = run_worker(stage_dir)
    print(f"[controller] worker run1: processed={len(w1['processed'])} skipped={len(w1['skipped_content_addressed'])}")

    # 3. OBSERVE
    obs = observe(paths)
    print(f"[controller] observe: started={obs['started']} done={obs['done']} "
          f"failed={obs['failed']} terminal_units={obs['terminal_units']}")

    # 4. GATE (the ≠-mind mechanical checker writes verdicts)
    gate = run_checker(stage_dir, replay=True)
    print(f"[controller] gate: GREEN={len(gate['GREEN'])} AMBER={len(gate['AMBER'])} RED={len(gate['RED'])}")

    # 5. ROUTE by tier — the actual control decision, per the CPP trust split
    accepted, escalated, red = 0, 0, 0
    for uid in gate["GREEN"]:
        unit = stage.unit_by_id(paths, uid)                # reads unit["id"] -> needs the bridge
        rec = stage.read_quarantine(paths, uid)            # CPP-1e envelope unwrap
        stage.accept_output(paths, unit, {"output": rec}, controller_id=CONTROLLER_ID)  # <-- the latent-break site
        accepted += 1
    for uid in gate["AMBER"]:
        stage.digest_line(paths, "AMBER", "await ≠-mind inference judge", unit_id=uid)  # escalate, not auto-accept
        escalated += 1
    for uid in gate["RED"]:
        stage.digest_line(paths, "RED", "gate rejected — quarantined, human review", unit_id=uid)
        red += 1
    print(f"[controller] routed: accepted_GREEN={accepted} escalated_AMBER={escalated} digest_RED={red}")

    # 6. RESUME (crash-safety): a second drive must do ZERO redundant work (content-addressed)
    w2 = run_worker(stage_dir)
    zero = len(w2["processed"]) == 0
    print(f"[controller] resume: run2 processed={len(w2['processed'])} "
          f"skipped={len(w2['skipped_content_addressed'])} zero_redundant={zero}")

    # 7. AUDIT trail exists (controller-written, append-only)
    print(f"[controller] audit rows={len(stage.read_audit(paths))} digest rows={len(stage.read_digest(paths))}")

    ok = (obs["done"] == enq or enq == 0) and zero
    print("INTEGRATION: controller drove the vision pipeline end-to-end"
          + (" — OK" if ok else " — CHECK OUTPUT"))
    print("NOTE: accepted_GREEN>0 exercises accept_output — the dual-key bridge is what keeps it from KeyError; "
          "pin the ABI (CPP-1g) to remove the bridge.")
    return 0 if ok else 1


def main(argv=None) -> int:
    argv = argv or sys.argv[1:]
    if len(argv) < 2:
        print("usage: python3 -m annotation_socket.controller <stage_dir> <img1> <img2> ...")
        return 2
    return control_loop(argv[0], argv[1:])


if __name__ == "__main__":
    sys.exit(main())
