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
import sys
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
  "contract_version": "render-verdict/v0.6", "run_id": run_id, "iter": it,
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
