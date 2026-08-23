#!/usr/bin/env python3
"""orchestrate.py — T1.3: photo→VR production-loop cycle driver + HITL record.

Drives the loop: produce render packet → compare against target → stop on
BELOW_THRESHOLD or at the iteration cap (CAP_REACHED_FLAGGED — never a silent or
infinite loop), then records the human's accept/reject with provenance.

Lane: Image_Tagger_dk_latest (tanishq). The producer runs as an external COMMAND
(your production_loop/ code in New_VR_Platform, or any stub honouring the packet
contract) — no cross-repo imports; the loop crosses repos through render-verdict/v0.6.

METHOD BLOCK (Method Card v0.1)
- FREEZE: consumes render-verdict/v0.6 via loop/run_loop_compare.py (same commit);
  producer invoked by command template only.
- CLAIM: for one target scene and one producer, the orchestrator reaches a stop state in
  at most `cap` iterations, records every iteration's discrepancy, and a run that cannot
  reach the threshold ends CAP_REACHED_FLAGGED — visibly, with exit code 3.
- REFUTATION: any input on which the orchestrator loops past `cap`, exits 0 while
  flagged, or reports BELOW_THRESHOLD without a verdict file saying so.
- NEGATIVE CONTROL (tests): a producer that always emits a wrong-wall packet MUST end
  CAP_REACHED_FLAGGED at exactly `cap` iterations with exit 3 — never accepted, never
  unbounded.
- HITL: every accept/reject lands in an append-only hitl.jsonl with who / when_utc /
  run_id / iter / verdict / note / run_summary_sha256 (`verdict_unprovenanced` is the
  named failure this kills). The convergence score stays exploratory
  (`resemblance_used_as_evidence`): HITL acceptance is a HUMAN act, never automatic.
- Known bound: v0 has no automatic adjuster between iterations — each iteration re-runs
  the producer on the same target, so scores are typically flat until the producer
  consumes prior verdicts (open work, named in the run summary). Checker ≠ author:
  David or Stephan drives one accept and one reject (T1.3 acceptance).

CLI:
  python3 loop/orchestrate.py run --target scene.json --run-dir loop_runs/<run_id> \
      --producer-cmd "python3 .../emit_render_packet.py --scene {target} \
      --out-dir {render_dir} --run-id {run_id} --iter {iter}" \
      [--cap 3] [--threshold 0.05]
  python3 loop/orchestrate.py hitl --run-dir loop_runs/<run_id> --verdict accept|reject \
      --who <name> [--note "..."] [--when-utc <ISO>]
Exit codes: 0 stop-below-threshold; 3 cap-reached-flagged; 2 refused/producer failure.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_loop_compare as rlc  # noqa: E402  (same-lane sibling module)


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n"


def sha256_text(t: str) -> str:
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def run_cycle(target: Path, run_dir: Path, producer_cmd: str,
              cap: int, threshold: Optional[float]) -> Tuple[int, str]:
    if cap < 1:
        return 2, "REFUSED: cap must be >= 1 (a capless loop is the named failure)"
    if not target.exists():
        return 2, f"REFUSED: target {target} does not exist"
    run_dir.mkdir(parents=True, exist_ok=True)
    run_id = run_dir.name

    iterations = []
    final_status = "CAP_REACHED_FLAGGED"
    for k in range(cap):
        it_dir = run_dir / f"iter_{k}"
        render_dir, verdict_dir = it_dir / "render", it_dir / "verdict"
        cmd = producer_cmd.format(target=str(target), render_dir=str(render_dir),
                                  run_id=run_id, iter=k)
        proc = subprocess.run(shlex.split(cmd), capture_output=True, text=True)
        if proc.returncode != 0:
            return 2, (f"REFUSED: producer failed at iter {k} (exit {proc.returncode}): "
                       f"{(proc.stderr or proc.stdout).strip()[:400]}")
        code, msg = rlc.run(target, render_dir, verdict_dir, threshold)
        if code != 0:
            return 2, f"REFUSED: comparator at iter {k}: {msg}"
        v = json.loads((verdict_dir / "verdict.json").read_text(encoding="utf-8"))
        iterations.append({"iter": k, "score": v["discrepancy"]["score"],
                           "verdict": v["verdict"],
                           "identity_mode": v["identity"]["mode"],
                           "verdict_sha256": sha256_text(
                               canonical(v))})
        if v["verdict"] == "BELOW_THRESHOLD":
            final_status = "STOPPED_BELOW_THRESHOLD"
            break

    summary = {
        "run_id": run_id, "contract_version": rlc.CONTRACT_VERSION,
        "target": target.name, "cap": cap, "threshold": threshold,
        "iterations": iterations, "final_status": final_status,
        "adjuster": "none_v0 (producer does not yet consume prior verdicts — open work)",
        "note": "scores are exploratory_uncalibrated; acceptance is a human act (hitl)",
    }
    (run_dir / "run_summary.json").write_text(canonical(summary), encoding="utf-8")
    if final_status == "STOPPED_BELOW_THRESHOLD":
        return 0, (f"run {run_id}: STOPPED_BELOW_THRESHOLD at iter "
                   f"{iterations[-1]['iter']} score={iterations[-1]['score']}")
    return 3, (f"run {run_id}: CAP_REACHED_FLAGGED after {len(iterations)} iteration(s) "
               f"— threshold not reached; flagged for HITL, not silently accepted")


def record_hitl(run_dir: Path, verdict: str, who: str, note: str,
                when_utc: Optional[str]) -> Tuple[int, str]:
    summary_path = run_dir / "run_summary.json"
    if not summary_path.exists():
        return 2, "REFUSED: no run_summary.json — HITL records attach to a completed run"
    if verdict not in ("accept", "reject"):
        return 2, "REFUSED: verdict must be accept or reject"
    if not who.strip():
        return 2, "REFUSED: --who is required (verdict_unprovenanced is a named failure)"
    summary_text = summary_path.read_text(encoding="utf-8")
    summary = json.loads(summary_text)
    row = {
        "run_id": summary["run_id"],
        "iter": (summary["iterations"][-1]["iter"] if summary["iterations"] else None),
        "final_status": summary["final_status"],
        "verdict": verdict, "who": who.strip(), "note": note,
        "when_utc": when_utc or datetime.now(timezone.utc)
                                       .strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        "run_summary_sha256": sha256_text(summary_text),
    }
    with (run_dir / "hitl.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, sort_keys=True) + "\n")   # append-only, never rewritten
    return 0, f"hitl {verdict} by {row['who']} recorded for {row['run_id']}"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="photo->VR loop orchestrator (T1.3)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--target", required=True)
    r.add_argument("--run-dir", required=True)
    r.add_argument("--producer-cmd", required=True,
                   help="command template with {target} {render_dir} {run_id} {iter}")
    r.add_argument("--cap", type=int, default=3)
    r.add_argument("--threshold", type=float, default=None)
    h = sub.add_parser("hitl")
    h.add_argument("--run-dir", required=True)
    h.add_argument("--verdict", required=True)
    h.add_argument("--who", required=True)
    h.add_argument("--note", default="")
    h.add_argument("--when-utc", default=None)
    a = ap.parse_args(argv)
    if a.cmd == "run":
        code, msg = run_cycle(Path(a.target), Path(a.run_dir), a.producer_cmd,
                              a.cap, a.threshold)
    else:
        code, msg = record_hitl(Path(a.run_dir), a.verdict, a.who, a.note, a.when_utc)
    print(msg, file=sys.stderr if code == 2 else sys.stdout)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
