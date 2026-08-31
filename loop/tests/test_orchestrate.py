"""loop/tests/test_orchestrate.py — T1.3 orchestrator + HITL tests.

Stub producers (no cross-repo dependency), tmp_path, stdlib-runnable. The negative
control is T1.3's own: an unreachable threshold MUST end CAP_REACHED_FLAGGED at exactly
`cap` iterations with exit 3 — never accepted, never unbounded (infinite_or_silent_loop).
HITL rows must carry provenance (verdict_unprovenanced).

Run:  PYTHONPATH=. python3 -m pytest loop/tests/test_orchestrate.py -v
  or: PYTHONPATH=. python3 loop/tests/test_orchestrate.py
"""
from __future__ import annotations

import hashlib
import json
import signal
import sys
import time
from pathlib import Path

try:
    import pytest
except ImportError:
    pytest = None

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "loop"))

import orchestrate  # noqa: E402
import run_loop_compare as rlc  # noqa: E402

TARGET = {"image_id": "t13-fixture", "openings": [
    {"kind": "glazed_wall", "bbox_xywh": [0.86, 0.5, 0.26, 0.92]},
    {"kind": "door", "bbox_xywh": [0.50, 0.55, 0.06, 0.35]}]}

GOOD_ROOM = {"schema_version": "0.3",
             "apertures": [{"id": "ap0", "kind": "glazed_wall", "wall": "east"},
                           {"id": "ap1", "kind": "door", "wall": "north"}]}
BAD_ROOM = {"schema_version": "0.3",
            "apertures": [{"id": "ap0", "kind": "glazed_wall", "wall": "north"},
                          {"id": "ap1", "kind": "door", "wall": "north"}]}

STUB = '''#!/usr/bin/env python3
import hashlib, json, sys
from pathlib import Path
room = json.loads(Path({room_path!r}).read_text())
out = Path(sys.argv[sys.argv.index("--out-dir") + 1]); out.mkdir(parents=True, exist_ok=True)
run_id = sys.argv[sys.argv.index("--run-id") + 1]
it = int(sys.argv[sys.argv.index("--iter") + 1])
render = b"\\x89PNG-stub"; room_b = (json.dumps(room, sort_keys=True) + "\\n").encode()
cam_b = b'{{"fov_deg": 70}}'
(out / "render.png").write_bytes(render); (out / "room.json").write_bytes(room_b)
(out / "camera.json").write_bytes(cam_b)
sha = lambda b: hashlib.sha256(b).hexdigest()
(out / "packet.json").write_text(json.dumps({{
  "contract_version": "render-verdict/v0.7", "run_id": run_id, "iter": it,
  "target_image_id": "t13-fixture", "produced_utc": "2026-08-20T00:00:00+00:00",
  "sha256": {{"render_png": sha(render), "room_json": sha(room_b), "camera_json": sha(cam_b)}}}}))
print("stub packet", it)
'''


def make_stub(tmp: Path, room: dict, name: str) -> str:
    room_path = tmp / f"{name}_room.json"
    room_path.write_text(json.dumps(room), encoding="utf-8")
    stub = tmp / f"{name}_producer.py"
    stub.write_text(STUB.format(room_path=str(room_path)), encoding="utf-8")
    return (f"{sys.executable} {stub} --scene {{target}} --out-dir {{render_dir}} "
            f"--run-id {{run_id}} --iter {{iter}}")


def write_target(tmp: Path) -> Path:
    p = tmp / "target.json"
    p.write_text(json.dumps(TARGET), encoding="utf-8")
    return p


def test_good_producer_stops_below_threshold(tmp_path):
    code, msg = orchestrate.run_cycle(write_target(tmp_path), tmp_path / "run1",
                                      make_stub(tmp_path, GOOD_ROOM, "good"),
                                      cap=3, threshold=0.0)
    assert code == 0, msg
    s = json.loads((tmp_path / "run1" / "run_summary.json").read_text())
    assert s["final_status"] == "STOPPED_BELOW_THRESHOLD"
    assert len(s["iterations"]) == 1 and s["iterations"][0]["score"] == 0.0


def test_unreachable_threshold_caps_and_flags(tmp_path):
    """T1.3's negative control: never silent, never infinite, never accepted."""
    code, msg = orchestrate.run_cycle(write_target(tmp_path), tmp_path / "run2",
                                      make_stub(tmp_path, BAD_ROOM, "bad"),
                                      cap=3, threshold=0.0)
    assert code == 3, msg
    s = json.loads((tmp_path / "run2" / "run_summary.json").read_text())
    assert s["final_status"] == "CAP_REACHED_FLAGGED"
    assert len(s["iterations"]) == 3                      # exactly cap, not unbounded
    assert all(i["verdict"] == "CONTINUE" for i in s["iterations"])
    assert "FLAGGED" in msg and "not silently accepted" in msg


def test_zero_cap_refused(tmp_path):
    code, msg = orchestrate.run_cycle(write_target(tmp_path), tmp_path / "run0",
                                      "echo {target}", cap=0, threshold=None)
    assert code == 2 and "cap" in msg


def test_bad_threshold_refused_before_producer_runs(tmp_path):
    marker = tmp_path / "producer-ran"
    code, msg = orchestrate.run_cycle(
        write_target(tmp_path), tmp_path / "bad-threshold",
        f"touch {marker}", cap=1, threshold=float("inf"))
    assert code == 2 and "threshold" in msg
    assert not marker.exists()


def test_existing_run_directory_refused_to_prevent_stale_packet_reuse(tmp_path):
    run_dir = tmp_path / "existing"
    run_dir.mkdir()
    (run_dir / "stale.txt").write_text("old", encoding="utf-8")
    code, msg = orchestrate.run_cycle(
        write_target(tmp_path), run_dir, make_stub(tmp_path, GOOD_ROOM, "stale"),
        cap=1, threshold=0.0)
    assert code == 2 and "already exists" in msg and "stale" in msg


def test_run_summary_binds_target_and_producer(tmp_path):
    target = write_target(tmp_path)
    command = make_stub(tmp_path, GOOD_ROOM, "bound")
    run_dir = tmp_path / "bound-run"
    code, msg = orchestrate.run_cycle(target, run_dir, command, cap=1, threshold=0.0)
    assert code == 0, msg
    summary = json.loads((run_dir / "run_summary.json").read_text())
    assert summary["target_sha256"] == hashlib.sha256(target.read_bytes()).hexdigest()
    assert summary["producer_cmd_sha256"] == hashlib.sha256(command.encode()).hexdigest()


def test_producer_timeout_is_bounded(tmp_path):
    sleeper = tmp_path / "sleep.py"
    sleeper.write_text("import time; time.sleep(5)", encoding="utf-8")
    code, msg = orchestrate.run_cycle(
        write_target(tmp_path), tmp_path / "timeout-run", f"{sys.executable} {sleeper}",
        cap=1, threshold=0.0, producer_timeout_seconds=0.01)
    assert code == 2 and "timed out" in msg


def test_timeout_terminates_producer_descendants(tmp_path):
    marker = tmp_path / "descendant-survived"
    sleeper = tmp_path / "spawn.py"
    sleeper.write_text(
        "import subprocess,sys,time\n"
        "subprocess.Popen([sys.executable,'-c',"
        "\"import sys,time; time.sleep(.2); open(sys.argv[1],'w').write('bad')\","
        "sys.argv[1]], start_new_session=True)\n"
        "time.sleep(5)\n", encoding="utf-8")
    code, msg = orchestrate.run_cycle(
        write_target(tmp_path), tmp_path / "descendant-run",
        f"{sys.executable} {sleeper} {marker}", cap=1, threshold=0.0,
        producer_timeout_seconds=0.05)
    time.sleep(0.3)
    assert code == 2 and "timed out" in msg
    assert not marker.exists()


def test_producer_cannot_mutate_target_snapshot(tmp_path):
    mutator = tmp_path / "mutate.py"
    mutator.write_text(
        "import pathlib,sys,time\n"
        "pathlib.Path(sys.argv[1]).write_text('{}')\n", encoding="utf-8")
    code, msg = orchestrate.run_cycle(
        write_target(tmp_path), tmp_path / "mutation-run",
        f"{sys.executable} {mutator} {{target}}", cap=1, threshold=0.0)
    assert code == 2 and "mutated target snapshot" in msg
    assert not (tmp_path / "mutation-run" / "run_summary.json").exists()


def test_failing_producer_refused_with_iter_named(tmp_path):
    bad = tmp_path / "boom.py"
    bad.write_text("import sys; sys.exit(7)", encoding="utf-8")
    code, msg = orchestrate.run_cycle(
        write_target(tmp_path), tmp_path / "run3",
        f"{sys.executable} {bad} --out-dir {{render_dir}} --run-id {{run_id}} --iter {{iter}}",
        cap=2, threshold=None)
    assert code == 2 and "iter 0" in msg and "exit 7" in msg


def test_hitl_accept_and_reject_recorded_with_provenance(tmp_path):
    t = write_target(tmp_path)
    orchestrate.run_cycle(t, tmp_path / "run4", make_stub(tmp_path, GOOD_ROOM, "g2"),
                          cap=1, threshold=0.0)
    code, _ = orchestrate.record_hitl(tmp_path / "run4", "accept", "tanishq",
                                      "looks right", "2026-08-20T12:00:00+00:00")
    assert code == 0
    code, _ = orchestrate.record_hitl(tmp_path / "run4", "reject", "david",
                                      "glazing wrong wall", "2026-08-20T12:05:00+00:00")
    assert code == 0
    rows = [json.loads(l) for l in
            (tmp_path / "run4" / "hitl.jsonl").read_text().splitlines()]
    assert [r["verdict"] for r in rows] == ["accept", "reject"]     # append-only, both kept
    summary_text = (tmp_path / "run4" / "run_summary.json").read_text()
    for r in rows:
        assert r["who"] and r["when_utc"] and r["run_id"] == "run4"
        assert r["run_summary_sha256"] == hashlib.sha256(
            summary_text.encode()).hexdigest()                      # bound to the exact run


def test_hitl_without_who_or_run_refused(tmp_path):
    code, msg = orchestrate.record_hitl(tmp_path / "nope", "accept", "x", "", None)
    assert code == 2 and "run_summary" in msg
    t = write_target(tmp_path)
    orchestrate.run_cycle(t, tmp_path / "run5", make_stub(tmp_path, GOOD_ROOM, "g3"),
                          cap=1, threshold=0.0)
    code, msg = orchestrate.record_hitl(tmp_path / "run5", "accept", "   ", "", None)
    assert code == 2 and "who" in msg
    code, msg = orchestrate.record_hitl(tmp_path / "run5", "maybe", "tanishq", "", None)
    assert code == 2 and "accept or reject" in msg


def test_hitl_refuses_forged_summary_and_bad_timestamp(tmp_path):
    forged = tmp_path / "forged"
    forged.mkdir()
    (forged / "run_summary.json").write_text(json.dumps({
        "run_id": "forged", "iterations": [],
        "final_status": "STOPPED_BELOW_THRESHOLD",
    }), encoding="utf-8")
    code, msg = orchestrate.record_hitl(forged, "accept", "attacker", "", None)
    assert code == 2 and "invalid completed run evidence" in msg

    run_dir = tmp_path / "valid-run"
    orchestrate.run_cycle(write_target(tmp_path), run_dir,
                          make_stub(tmp_path, GOOD_ROOM, "timestamp"), 1, 0.0)
    code, msg = orchestrate.record_hitl(run_dir, "accept", "reviewer", "", "not-a-time")
    assert code == 2 and "timestamp" in msg


def test_hitl_hash_chain_detects_prior_row_tampering(tmp_path):
    run_dir = tmp_path / "ledger-run"
    orchestrate.run_cycle(write_target(tmp_path), run_dir,
                          make_stub(tmp_path, GOOD_ROOM, "ledger"), 1, 0.0)
    assert orchestrate.record_hitl(run_dir, "accept", "one", "", None)[0] == 0
    ledger = run_dir / "hitl.jsonl"
    row = json.loads(ledger.read_text(encoding="utf-8"))
    row["who"] = "tampered"
    ledger.write_text(json.dumps(row, sort_keys=True) + "\n", encoding="utf-8")
    code, msg = orchestrate.record_hitl(run_dir, "reject", "two", "", None)
    assert code == 2 and "broken HITL hash chain" in msg


def test_summary_deterministic_across_reruns(tmp_path):
    t = write_target(tmp_path)
    cmd = make_stub(tmp_path, GOOD_ROOM, "g4")
    # same run_id in two parents: byte-identical summaries prove determinism
    orchestrate.run_cycle(t, tmp_path / "a" / "runX", cmd, cap=2, threshold=0.0)
    orchestrate.run_cycle(t, tmp_path / "b" / "runX", cmd, cap=2, threshold=0.0)
    ba = (tmp_path / "a" / "runX" / "run_summary.json").read_bytes()
    bb = (tmp_path / "b" / "runX" / "run_summary.json").read_bytes()
    assert ba == bb


# ------------------------------------------------------------------ stdlib runner

# --- v0.8 regression tests (claims C1, C2, C3: docs/LOOP_V08_CLAIM_2026-08-31.md) ---

def test_timeout_reports_timed_out_even_when_killpg_is_denied(tmp_path):
    """C1: an EPERM from killpg must not displace the diagnosis or abort the sweep.

    Records every killpg attempt while denying all of them, which is what a sandbox that
    refuses to signal a new-session process looks like from inside the orchestrator.
    """
    import os as _os
    attempts = []
    original_killpg = _os.killpg

    def denying_killpg(pgid, sig):
        attempts.append(sig)
        raise PermissionError(1, "Operation not permitted")

    _os.killpg = denying_killpg
    try:
        sleeper = tmp_path / "sleep.py"
        sleeper.write_text("import time\ntime.sleep(5)\n", encoding="utf-8")
        code, msg = orchestrate.run_cycle(
            write_target(tmp_path), tmp_path / "eperm-run",
            f"{sys.executable} {sleeper}", cap=1, threshold=0.0,
            producer_timeout_seconds=0.05)
    finally:
        _os.killpg = original_killpg
    assert code == 2, msg
    assert "timed out" in msg, f"diagnosis was displaced: {msg}"
    assert "could not start" not in msg, f"timeout misreported as a start failure: {msg}"
    # Every killpg raised, yet the escalation continued to the final SIGKILL.
    assert signal.SIGTERM in attempts, f"SIGTERM stage skipped; attempts={attempts}"
    assert signal.SIGKILL in attempts, \
        f"final SIGKILL sweep did not run after EPERM; attempts={attempts}"


def test_mid_run_foreign_summary_refuses_with_exit_2(tmp_path):
    """C2: a run_summary.json appearing mid-run refuses cleanly, never tracebacks."""
    # A working stub, plus one extra line that squats the summary path the orchestrator
    # is about to write. Built by prepending to the real STUB so it stays a valid producer.
    room_path = tmp_path / "squat_room.json"
    room_path.write_text(json.dumps(GOOD_ROOM), encoding="utf-8")
    body = STUB.format(room_path=str(room_path))
    squat_line = ("\nimport pathlib as _pl\n"
                  "_out = _pl.Path(sys.argv[sys.argv.index('--out-dir') + 1])\n"
                  "(_out.parent.parent / 'run_summary.json').write_text('{\"squatted\": true}')\n")
    squatter = tmp_path / "squat_producer.py"
    squatter.write_text(body + squat_line, encoding="utf-8")
    cmd = (f"{sys.executable} {squatter} --scene {{target}} --out-dir {{render_dir}} "
           f"--run-id {{run_id}} --iter {{iter}}")
    code, msg = orchestrate.run_cycle(write_target(tmp_path), tmp_path / "squat-run",
                                      cmd, cap=1, threshold=0.0)
    assert code == 2, f"expected refusal exit 2, got {code}: {msg}"
    assert "run_summary.json" in msg, msg
    assert "Traceback" not in msg
    assert "already exists and was not written by this run" in msg, msg


def _deny_ps(store):
    """Deny executing `ps` only, as Codex's sandbox does, leaving every other
    subprocess.run untouched. Appends a restore callable to `store`."""
    import subprocess as _sp
    original = _sp.run

    def denying(args, *a, **k):
        if args and args[0] == "ps":
            raise PermissionError(1, "Operation not permitted", "ps")
        return original(args, *a, **k)

    _sp.run = denying
    store.append(lambda: setattr(_sp, "run", original))


def test_timeout_under_denied_ps_still_reports_timed_out_and_says_it_could_not_look(tmp_path):
    """C1b(a): a denied `ps` must not displace the diagnosis or skip the SIGKILL stage,
    and the refusal must admit that enumeration was unavailable."""
    import os as _os
    restores = []
    attempts = []
    original_killpg = _os.killpg

    def recording_killpg(pgid, sig):
        attempts.append(sig)
        return original_killpg(pgid, sig)

    _deny_ps(restores)
    _os.killpg = recording_killpg
    restores.append(lambda: setattr(_os, "killpg", original_killpg))
    try:
        sleeper = tmp_path / "sleep.py"
        sleeper.write_text("import time\ntime.sleep(5)\n", encoding="utf-8")
        code, msg = orchestrate.run_cycle(
            write_target(tmp_path), tmp_path / "nops-run",
            f"{sys.executable} {sleeper}", cap=1, threshold=0.0,
            producer_timeout_seconds=0.05)
    finally:
        for undo in reversed(restores):
            undo()
    assert code == 2, msg
    assert "timed out" in msg, f"diagnosis displaced by the ps failure: {msg}"
    assert "could not start" not in msg, msg
    assert signal.SIGKILL in attempts, f"SIGKILL stage skipped; attempts={attempts}"
    assert "descendant enumeration unavailable" in msg, \
        f"silent about being unable to look: {msg}"


def test_clean_run_under_denied_ps_succeeds_and_records_enumeration_failure(tmp_path):
    """C1b(b): a clean run under a denied `ps` still exits 0 — never 'could not start' —
    and the summary records that enumeration failed rather than implying an empty sweep."""
    restores = []
    _deny_ps(restores)
    try:
        code, msg = orchestrate.run_cycle(
            write_target(tmp_path), tmp_path / "nops-clean",
            make_stub(tmp_path, GOOD_ROOM, "nops"), cap=3, threshold=0.0)
    finally:
        for undo in reversed(restores):
            undo()
    assert code == 0, f"clean run misreported under denied ps: {msg}"
    assert "could not start" not in msg, msg
    s = json.loads((tmp_path / "nops-clean" / "run_summary.json").read_text())
    assert s["final_status"] == "STOPPED_BELOW_THRESHOLD"
    assert s.get("descendant_enumeration_failed") is True, \
        f"summary implies a clean sweep it could not perform: {sorted(s)}"
    assert "Operation not permitted" in s.get("descendant_enumeration_error", "")
    assert "teardown_incomplete" not in s, \
        "must not claim an empty survivor list when enumeration failed"


def test_orphaned_new_session_grandchild_is_reaped_or_reported(tmp_path):
    """C1: never a silent success — either the grandchild dies or it is reported."""
    marker = tmp_path / "orphan-survived"
    spawner = tmp_path / "orphan.py"
    spawner.write_text(
        "import subprocess, sys, time\n"
        "subprocess.Popen([sys.executable, '-c',\n"
        "  \"import sys,time; time.sleep(.4); open(sys.argv[1],'w').write('bad')\",\n"
        "  sys.argv[1]], start_new_session=True)\n"
        "time.sleep(0.01)\n",            # parent exits at once, orphaning the grandchild
        encoding="utf-8")
    code, msg = orchestrate.run_cycle(
        write_target(tmp_path), tmp_path / "orphan-run",
        f"{sys.executable} {spawner} {marker}", cap=1, threshold=0.0,
        producer_timeout_seconds=0.05)
    time.sleep(0.6)
    assert code == 2, msg
    reaped = not marker.exists()
    reported = "teardown_incomplete" in msg
    assert reaped or reported, \
        f"silent success: grandchild survived and was not reported. msg={msg}"


def _run_all_without_pytest() -> int:
    import inspect
    import tempfile
    import traceback
    tests = [(n, f) for n, f in sorted(globals().items())
             if n.startswith("test_") and callable(f)]
    failed = 0
    for name, fn in tests:
        with tempfile.TemporaryDirectory() as td:
            kwargs = {"tmp_path": Path(td)} if \
                "tmp_path" in inspect.signature(fn).parameters else {}
            try:
                fn(**kwargs)
                print(f"PASS {name}")
            except Exception:
                failed += 1
                print(f"FAIL {name}")
                traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    if pytest is not None:
        raise SystemExit(pytest.main([__file__, "-v"]))
    raise SystemExit(_run_all_without_pytest())
