"""
annotation_socket.controller_drive — the CONTROLLER IN CHARGE (the CPP operational loop).

This inverts authority relative to run_stage.py (a demo driver): here the CONTROLLER is the
system in charge, implementing the CPP spec's one-tick loop
(`CONTROLLER_PIPELINE_PROTOCOL_2026-07-15.md`) over the shared cpp.stage verbs, and the
annotator runs as a SUPERVISED SUBPROCESS whose stdout+exit the controller owns and
classifies with the supervisor's primitives (classify_result / ProgressWatchdog).

The tick (verbatim from the CPP spec, no pipeline-specific fields):
  reclaim stale claims                      # crash recovery
  ingest events -> liveness + coverage      # OBSERVE
  gate quarantined-unverdicted units        # GATE (≠-mind checker, mechanical-primary)
    GREEN -> accepted/ ; AMBER -> adjudicate(digest) ; RED -> escalate(digest)
  liveness check: heartbeats fresh but accepted/ flat -> SPEND_DEAD_SUSPECTED
  coverage < 100% at batch end -> RED digest (never silently "done")
  audit log-BEFORE-enact on every decision  # I4

The controller keeps NO in-memory authoritative state: everything is reconstructed from
the stage artifacts each tick (CPP hard-part 4 — stateless-recoverable).

Run:  CONTROL_ROOT=... python3 -m annotation_socket.controller_drive <stage_dir> <image>...
"""
from __future__ import annotations
import json, os, subprocess, sys, time
from pathlib import Path

os.environ.setdefault("CONTROL_ROOT", "/home/claude/_control_deps"
                      if Path("/home/claude/_control_deps").exists()
                      else "/Users/davidusa/REPOS/_control")
sys.path.insert(0, os.environ["CONTROL_ROOT"])
from cpp import stage
sys.path.insert(0, str(Path(os.environ["CONTROL_ROOT"]) / "supervisor"))
import supervisor as sup

from .annotator import unit_id_for
from .verify import run_checker

CONTROLLER_ID = "nn-controller"
CLAIM_STALE_S = 3600


# ------------------------------------------------------------------ supervised worker spawn
def spawn_worker(stage_dir: str) -> tuple[str, str]:
    """Spawn the annotator as a headless subprocess; OWN stdout+stderr+exit; classify with
    the supervisor's classifier (output-grep dominates exit code)."""
    code = ("import sys, json; sys.path.insert(0, '/home/claude'); "
            "from annotation_socket.annotator import run_worker; "
            f"print(json.dumps(run_worker({stage_dir!r})))")
    proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                          timeout=1800, env={**os.environ})
    death = sup.classify_result(proc.returncode, proc.stdout, proc.stderr)
    return death.value, proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else ""


# ------------------------------------------------------------------ the controller tick
def tick(stage_dir: str) -> dict:
    paths = stage.ensure_stage(stage_dir)
    report = {}

    # 1. reclaim stale claims (crash recovery)
    now = stage.now_ms()
    reclaimed = []
    terminal = stage.terminal_event_units(paths)
    for uid, c in stage.read_claims(paths).items():
        if uid not in terminal and now - c.get("ts", now) > CLAIM_STALE_S * 1000:
            stage.audit(paths, "reclaim_stale_claim", uid, {"age_ms": now - c.get("ts", now)})
            stage.reset_claim(paths, uid)
            reclaimed.append(uid)
    report["reclaimed"] = reclaimed

    # 2. OBSERVE: coverage purely from artifacts (stateless reconstruction)
    queue = stage.read_queue_units(paths)
    accepted_before = stage.accepted_units(paths)
    verdicts = stage.verdict_by_unit(paths)
    report["observe"] = {"queued": len(queue), "events": stage.event_counts(paths),
                         "verdicted": len(verdicts), "accepted": len(accepted_before)}

    # 3. GATE: verdict every quarantined-unverdicted unit (≠-mind mechanical checker)
    stage.audit(paths, "gate_begin", None, {"pending": len(stage.quarantine_unit_ids(paths)) - len(verdicts)})
    gate = run_checker(stage_dir, replay=True)          # checker role; GREEN auto-accepts
    for uid in gate["AMBER"]:
        stage.audit(paths, "adjudicate_needed", uid, {"tier": "AMBER"})   # log BEFORE enact
        stage.digest_line(paths, "AMBER", f"unit {uid} awaits ≠-mind inference judge")
    for uid in gate["RED"]:
        stage.audit(paths, "escalate", uid, {"tier": "RED"})
        stage.digest_line(paths, "RED", f"unit {uid} REJECTED by mechanical gate — quarantined")
    report["gate"] = {k: len(v) for k, v in gate.items()}

    # 4. liveness != progress (accepted/ growth is the only progress oracle)
    accepted_after = stage.accepted_units(paths)
    hb = stage.event_counts(paths).get("heartbeat", 0)
    if hb > 0 and len(accepted_after) == len(accepted_before) and not gate["AMBER"] and not gate["GREEN"] and not gate["RED"]:
        stage.digest_line(paths, "RED", "heartbeats present but no gate progress: SPEND_DEAD_SUSPECTED")
        report["liveness"] = "SPEND_DEAD_SUSPECTED"
    else:
        report["liveness"] = "progressing"

    # 5. coverage at batch end: every queued unit must reach a verdict — else RED
    verdicts = stage.verdict_by_unit(paths)
    unresolved = [u["unit_id"] for u in queue if u["unit_id"] not in verdicts
                  and u["unit_id"] not in stage.accepted_units(paths)]
    if unresolved:
        stage.digest_line(paths, "RED", f"coverage<100%: {len(unresolved)} unit(s) unresolved: {unresolved[:3]}")
        report["batch"] = f"RED coverage<100% ({len(unresolved)} unresolved)"
    else:
        counts = {}
        for uid, v in verdicts.items():
            counts[v["tier"]] = counts.get(v["tier"], 0) + 1
        report["batch"] = f"complete: {counts}"
    stage.audit(paths, "tick_end", None, report["gate"])
    return report


# ------------------------------------------------------------------ controller main
def main(argv=None) -> int:
    argv = argv or sys.argv[1:]
    stage_dir, images = argv[0], argv[1:]
    paths = stage.ensure_stage(stage_dir)

    # SCHEDULE: the controller enqueues (log-before-enact)
    existing = {u["unit_id"] for u in stage.read_queue_units(paths)}
    for img in images:
        uid = unit_id_for(img)
        if uid in existing:
            print(f"[{CONTROLLER_ID}] unit {uid} already queued (content-addressed) — not re-enqueued")
            continue
        stage.audit(paths, "enqueue", uid, {"image": Path(img).name})
        stage.enqueue(paths, {"unit_id": uid, "image_path": str(Path(img).resolve()), "inputs": []},
                      controller_id=CONTROLLER_ID)
        print(f"[{CONTROLLER_ID}] ENQUEUE {uid} <- {Path(img).name}")

    # SUPERVISED WORKER: spawn, own streams, classify
    death, tail = spawn_worker(stage_dir)
    stage.audit(paths, "worker_run", None, {"classification": death})
    print(f"[{CONTROLLER_ID}] worker subprocess -> classified '{death}'; result={tail[:100]}")
    if death == "spend_dead":
        stage.digest_line(paths, "RED", "worker spend_dead — escalate to David, no respawn")
        print(f"[{CONTROLLER_ID}] RED: spend_dead — stopping (I5: only David resets credit)")
        return 1

    # THE TICK
    report = tick(stage_dir)
    print(f"[{CONTROLLER_ID}] tick: observe={report['observe']}")
    print(f"[{CONTROLLER_ID}] tick: gate={report['gate']} liveness={report['liveness']}")
    print(f"[{CONTROLLER_ID}] tick: batch={report['batch']}")

    # the controller's outward face: the digest + the audit trail
    print(f"\n[{CONTROLLER_ID}] DIGEST (what David sees):")
    for row in stage.read_digest(paths)[-6:]:
        print(f"    {row.get('severity','?'):5s} {row.get('message','')}")
    print(f"[{CONTROLLER_ID}] AUDIT (last 8 decisions, logged before enactment):")
    for row in stage.read_audit(paths)[-8:]:
        print(f"    {row.get('action','?'):22s} unit={str(row.get('unit_id'))[:16]:16s} {json.dumps(row.get('detail',{}))[:60]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
