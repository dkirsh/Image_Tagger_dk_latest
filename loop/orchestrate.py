#!/usr/bin/env python3
"""orchestrate.py — T1.3: photo→VR production-loop cycle driver + HITL record.

Drives the loop: produce render packet → compare against target → stop on
BELOW_THRESHOLD or at the iteration cap (CAP_REACHED_FLAGGED — never a silent or
infinite loop), then records the human's accept/reject with provenance.

Lane: Image_Tagger_dk_latest (tanishq). The producer runs as an external COMMAND
(your production_loop/ code in New_VR_Platform, or any stub honouring the packet
contract) — no cross-repo imports; the loop crosses repos through render-verdict/v0.7.

METHOD BLOCK (Method Card v0.1)
- FREEZE: consumes render-verdict/v0.7 via loop/run_loop_compare.py (same commit);
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
- TEARDOWN (orchestrator v0.8; the wire contract stays render-verdict/v0.7 because nothing
  a producer emits or consumes changed). On timeout the orchestrator returns within a
  bounded time and reports completely. Descendants are enumerated by polling DURING the
  run, so an intermediate that exits and orphans its children is still seen. A target that
  cannot be signalled — PermissionError/EPERM, which a sandbox may raise for a new-session
  process — is recorded, never raised: it neither aborts the sweep nor displaces the
  TimeoutExpired, so a producer that timed out is always reported as having timed out, and
  the final SIGKILL sweep always runs. Anything still alive afterwards is named in the
  refusal message and, when a summary is written, in a `teardown_incomplete` field.
  What this does NOT promise: a kill guarantee against an adversarial producer. One that
  double-forks into a new session before the first poll leaves the ancestry graph and
  cannot be found by walking it afterwards. The guarantee is bounded return plus complete
  reporting — `teardown_incomplete` means "these pids were alive when we gave up".

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
import fcntl
import hashlib
import json
import os
import shlex
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_loop_compare as rlc  # noqa: E402  (same-lane sibling module)


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False) + "\n"


def sha256_text(t: str) -> str:
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def finite_number(value) -> bool:
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and value == value and value not in (float("inf"), float("-inf")))


def _kill_process_group(proc: subprocess.Popen, sig: int) -> set:
    """Signal the producer's process group. Returns pids that could NOT be signalled.

    ProcessLookupError means the target is already gone, which is success. Any other OSError
    — PermissionError (EPERM) above all, which a sandbox can raise for a new-session target —
    means we could not signal it. Neither is allowed to propagate: a failure to signal one
    target must not abort the sweep, and must never displace the TimeoutExpired being handled.
    """
    try:
        os.killpg(proc.pid, sig)
    except ProcessLookupError:
        pass
    except OSError:
        return {proc.pid}
    return set()


def _descendant_pids(root_pid: int) -> Tuple[set, Optional[str]]:
    """Descendants of root_pid, plus why enumeration failed if it did. NEVER raises.

    Returns (pids_found_so_far, error_text_or_None). The error half matters: a sandbox can
    deny executing `ps` outright, and an empty set then means "we could not look", not
    "there is nothing there". Reporting `teardown_incomplete: []` on the strength of a
    failed enumeration would be a false statement, so callers carry the error and say so.
    """
    try:
        result = subprocess.run(
            ["ps", "-axo", "pid=,ppid="], capture_output=True, text=True, timeout=1.0)
    except subprocess.TimeoutExpired:
        return set(), "ps timed out after 1.0s"
    except OSError as exc:
        return set(), f"{type(exc).__name__}: {exc}"
    except Exception as exc:  # noqa: BLE001 — enumeration must never abort a teardown
        return set(), f"{type(exc).__name__}: {exc}"
    if result.returncode != 0:
        return set(), f"ps exited {result.returncode}: {(result.stderr or '').strip()[:120]}"
    children = {}
    for line in result.stdout.splitlines():
        try:
            pid, ppid = (int(part) for part in line.split())
        except (TypeError, ValueError):
            continue
        children.setdefault(ppid, set()).add(pid)
    found, frontier = set(), [root_pid]
    while frontier:
        for pid in children.get(frontier.pop(), ()):
            if pid not in found:
                found.add(pid)
                frontier.append(pid)
    return found, None


def _signal_pids(pids: set, sig: int) -> set:
    """Signal every pid. Returns the subset that could NOT be signalled.

    One unsignallable pid must not stop the others being tried, so nothing raises here.
    """
    unsignalled = set()
    for pid in sorted(pids, reverse=True):
        try:
            os.kill(pid, sig)
        except ProcessLookupError:
            pass
        except OSError:
            unsignalled.add(pid)
    return unsignalled


def _alive(pid: int) -> bool:
    """True if the pid still exists. Signal 0 checks existence without delivering anything.

    EPERM means it exists but is not ours to signal, which still counts as alive.
    """
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except OSError:
        return True
    return True


_POLL_INTERVAL_S = 0.02
ORCHESTRATOR_VERSION = "0.8"


class TeardownReport(subprocess.TimeoutExpired):
    """A TimeoutExpired that also carries which pids the sweep could not confirm dead.

    Subclassing keeps every existing `except subprocess.TimeoutExpired` correct — the
    diagnosis stays "timed out" — while giving callers the survivors to report.
    """

    def __init__(self, expired: subprocess.TimeoutExpired, survivors: set,
                 enumeration_error: Optional[str] = None):
        super().__init__(expired.cmd, expired.timeout, expired.output, expired.stderr)
        self.survivors = set(survivors)
        self.enumeration_error = enumeration_error


def _reap(proc: subprocess.Popen, seconds: float) -> None:
    """Wait briefly for the producer, swallowing everything. Used only inside teardown,
    where a second failure must not displace the diagnosis already being reported."""
    try:
        proc.communicate(timeout=seconds)
    except subprocess.TimeoutExpired:
        pass
    except Exception:  # noqa: BLE001 — teardown must not raise, whatever goes wrong here
        pass


def _run_producer(args, timeout_seconds: float) -> subprocess.CompletedProcess:
    proc = subprocess.Popen(
        args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        start_new_session=True,
    )
    # Accumulate descendants WHILE the producer runs. A single snapshot taken after the
    # deadline cannot see an intermediate that already exited and orphaned its children.
    seen: set = set()
    enum_error: Optional[str] = None

    def enumerate_into_seen() -> None:
        nonlocal enum_error
        pids, err = _descendant_pids(proc.pid)
        seen.update(pids)
        if err and enum_error is None:
            enum_error = err

    deadline = time.monotonic() + float(timeout_seconds)
    try:
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                enumerate_into_seen()
                raise subprocess.TimeoutExpired(args, float(timeout_seconds))
            try:
                stdout, stderr = proc.communicate(timeout=min(_POLL_INTERVAL_S, remaining))
                break
            except subprocess.TimeoutExpired:
                enumerate_into_seen()
    except subprocess.TimeoutExpired as expired:
        # Escalate. NOTHING below may raise: a second failure here — an unsignallable pid,
        # a denied `ps`, a broken pipe — must not displace the timeout diagnosis or skip
        # the SIGKILL stage. Every call is either total or wrapped.
        unsignalled = _signal_pids(seen, signal.SIGTERM)
        unsignalled |= _kill_process_group(proc, signal.SIGTERM)
        _reap(proc, 0.5)
        enumerate_into_seen()
        # The final SIGKILL sweep ALWAYS runs, whatever happened above.
        unsignalled |= _signal_pids(seen, signal.SIGKILL)
        unsignalled |= _kill_process_group(proc, signal.SIGKILL)
        _reap(proc, 0.5)
        survivors = {pid for pid in (seen | unsignalled) if _alive(pid)}
        raise TeardownReport(expired, survivors, enum_error) from None
    finally:
        if proc.poll() is not None:
            # A successful producer may still have left children in its process group.
            _kill_process_group(proc, signal.SIGTERM)
    done = subprocess.CompletedProcess(args, proc.returncode, stdout, stderr)
    # A producer can exit 0 and still leave descendants behind; report them rather than
    # letting a clean exit code imply a clean process table. If enumeration failed we say
    # so, because an empty list would claim we looked.
    enumerate_into_seen()
    done.teardown_incomplete = sorted(  # type: ignore[attr-defined]
        pid for pid in seen if _alive(pid))
    done.enumeration_error = enum_error  # type: ignore[attr-defined]
    return done


def _parse_aware_utc(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("timestamp must be a non-empty ISO-8601 string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"timestamp is not valid ISO-8601: {value!r}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timestamp must include a UTC offset")
    return parsed.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def run_cycle(target: Path, run_dir: Path, producer_cmd: str,
              cap: int, threshold: Optional[float],
              producer_timeout_seconds: float = 300.0) -> Tuple[int, str]:
    if isinstance(cap, bool) or not isinstance(cap, int) or cap < 1:
        return 2, "REFUSED: cap must be >= 1 (a capless loop is the named failure)"
    if threshold is not None and (
            not finite_number(threshold) or not 0.0 <= float(threshold) <= 1.0):
        return 2, "REFUSED: threshold must be a finite number in [0,1]"
    if not finite_number(producer_timeout_seconds) or producer_timeout_seconds <= 0:
        return 2, "REFUSED: producer timeout must be a positive finite number"
    try:
        target_bytes = rlc.read_regular_bytes(target, "target scene")
        target_scene = rlc.load_target_bytes(target_bytes)
    except rlc.Refused as exc:
        return 2, f"REFUSED: {exc}"
    target_sha256 = hashlib.sha256(target_bytes).hexdigest()
    try:
        run_dir.parent.mkdir(parents=True, exist_ok=True)
        run_dir.mkdir()
    except FileExistsError:
        return 2, (f"REFUSED: run directory {run_dir} already exists; "
                   "run artifacts are immutable and may not reuse stale packets")
    except OSError as exc:
        return 2, f"REFUSED: cannot create run directory {run_dir}: {exc}"
    run_id = run_dir.name
    target_snapshot = run_dir / "target.snapshot.json"
    try:
        with target_snapshot.open("xb") as fh:
            fh.write(target_bytes)
            fh.flush()
            os.fsync(fh.fileno())
    except OSError as exc:
        return 2, f"REFUSED: cannot create target snapshot: {exc}"

    iterations = []
    teardown_incomplete: set = set()
    enumeration_error: Optional[str] = None
    final_status = "CAP_REACHED_FLAGGED"
    for k in range(cap):
        it_dir = run_dir / f"iter_{k}"
        render_dir, verdict_dir = it_dir / "render", it_dir / "verdict"
        try:
            cmd = producer_cmd.format(target=str(target_snapshot), render_dir=str(render_dir),
                                      run_id=run_id, iter=k)
            proc = _run_producer(shlex.split(cmd), float(producer_timeout_seconds))
        except (KeyError, ValueError) as exc:
            return 2, f"REFUSED: malformed producer command template: {exc}"
        except subprocess.TimeoutExpired as expired:
            # A producer that timed out is ALWAYS reported as timed out. Anything the sweep
            # could not confirm dead is named here rather than passed over in silence.
            survivors = sorted(getattr(expired, "survivors", ()) or ())
            enum_err = getattr(expired, "enumeration_error", None)
            detail = ("" if not survivors else
                      f"; teardown_incomplete: pids still alive after SIGKILL sweep: "
                      f"{', '.join(str(p) for p in survivors)}")
            # An empty survivor list is only meaningful if we were able to look.
            if enum_err:
                detail += f"; descendant enumeration unavailable: {enum_err}"
            return 2, (f"REFUSED: producer timed out at iter {k} after "
                       f"{producer_timeout_seconds:g}s{detail}")
        except OSError as exc:
            return 2, f"REFUSED: producer could not start at iter {k}: {exc}"
        teardown_incomplete |= set(getattr(proc, "teardown_incomplete", ()) or ())
        if enumeration_error is None:
            enumeration_error = getattr(proc, "enumeration_error", None)
        if proc.returncode != 0:
            return 2, (f"REFUSED: producer failed at iter {k} (exit {proc.returncode}): "
                       f"{(proc.stderr or proc.stdout).strip()[:400]}")
        try:
            if rlc.read_regular_bytes(target_snapshot, "target snapshot") != target_bytes:
                return 2, f"REFUSED: producer mutated target snapshot at iter {k}"
        except rlc.Refused as exc:
            return 2, f"REFUSED: target snapshot integrity failed at iter {k}: {exc}"
        code, msg = rlc.run(target_snapshot, render_dir, verdict_dir, threshold,
                            target_bytes=target_bytes)
        if code != 0:
            return 2, f"REFUSED: comparator at iter {k}: {msg}"
        v = json.loads((verdict_dir / "verdict.json").read_text(encoding="utf-8"))
        expected_target_id = target_scene.get("image_id")
        if v.get("run_id") != run_id or v.get("iter") != k:
            return 2, (f"REFUSED: packet identity mismatch at iter {k}: "
                       f"run_id={v.get('run_id')!r}, iter={v.get('iter')!r}")
        if isinstance(expected_target_id, str) and expected_target_id and \
                v.get("target_image_id") != expected_target_id:
            return 2, (f"REFUSED: packet target_image_id {v.get('target_image_id')!r} "
                       f"does not match target image_id {expected_target_id!r}")
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
        # The wire contract stays v0.7; this names the orchestrator that drove the run,
        # so a summary can be read against the teardown semantics that produced it.
        "orchestrator_version": ORCHESTRATOR_VERSION,
        "target": target.name, "target_snapshot": target_snapshot.name,
        "target_sha256": target_sha256,
        "producer_cmd_sha256": sha256_text(producer_cmd),
        "producer_timeout_seconds": float(producer_timeout_seconds),
        "cap": cap, "threshold": threshold,
        "iterations": iterations, "final_status": final_status,
        "adjuster": "none_v0 (producer does not yet consume prior verdicts — open work)",
        "note": "scores are exploratory_uncalibrated; acceptance is a human act (hitl)",
    }
    if teardown_incomplete:
        # Only present when something outlived the sweep, so its absence is not a claim.
        summary["teardown_incomplete"] = sorted(teardown_incomplete)
    if enumeration_error is not None:
        # Without this, an absent teardown_incomplete would imply we looked and found
        # nothing. We could not look, and the summary has to say so.
        summary["descendant_enumeration_failed"] = True
        summary["descendant_enumeration_error"] = enumeration_error
    summary_path = run_dir / "run_summary.json"
    try:
        with summary_path.open("x", encoding="utf-8") as fh:
            fh.write(canonical(summary))
            fh.flush()
            os.fsync(fh.fileno())
    except FileExistsError:
        return 2, (f"REFUSED: {summary_path} already exists and was not written by this run; "
                   "a foreign run_summary.json means the run directory was written to "
                   "mid-run, and run artifacts are immutable")
    except OSError as exc:
        return 2, f"REFUSED: cannot write run summary {summary_path}: {exc}"
    if final_status == "STOPPED_BELOW_THRESHOLD":
        return 0, (f"run {run_id}: STOPPED_BELOW_THRESHOLD at iter "
                   f"{iterations[-1]['iter']} score={iterations[-1]['score']}")
    return 3, (f"run {run_id}: CAP_REACHED_FLAGGED after {len(iterations)} iteration(s) "
               f"— threshold not reached; flagged for HITL, not silently accepted")


def record_hitl(run_dir: Path, verdict: str, who: str, note: str,
                when_utc: Optional[str]) -> Tuple[int, str]:
    summary_path = run_dir / "run_summary.json"
    if verdict not in ("accept", "reject"):
        return 2, "REFUSED: verdict must be accept or reject"
    if not isinstance(who, str) or not who.strip():
        return 2, "REFUSED: --who is required (verdict_unprovenanced is a named failure)"
    try:
        summary_text = rlc.read_regular_bytes(summary_path, "run_summary.json").decode("utf-8")
        summary = rlc._strict_loads(summary_text, "run_summary.json")
        if not isinstance(summary, dict) or canonical(summary) != summary_text:
            raise ValueError("run_summary.json is not canonical")
        iterations = summary.get("iterations")
        cap = summary.get("cap")
        final_status = summary.get("final_status")
        if summary.get("run_id") != run_dir.name or \
                summary.get("contract_version") != rlc.CONTRACT_VERSION:
            raise ValueError("run identity or contract version mismatch")
        if isinstance(cap, bool) or not isinstance(cap, int) or cap < 1:
            raise ValueError("invalid cap")
        if not isinstance(iterations, list) or not iterations or len(iterations) > cap:
            raise ValueError("completed run must contain 1..cap iterations")
        if [item.get("iter") for item in iterations if isinstance(item, dict)] != \
                list(range(len(iterations))):
            raise ValueError("iterations are malformed or non-contiguous")
        if final_status not in ("STOPPED_BELOW_THRESHOLD", "CAP_REACHED_FLAGGED"):
            raise ValueError("invalid final_status")
        if final_status == "STOPPED_BELOW_THRESHOLD" and \
                iterations[-1].get("verdict") != "BELOW_THRESHOLD":
            raise ValueError("stop status disagrees with final verdict")
        if final_status == "CAP_REACHED_FLAGGED" and (len(iterations) != cap or any(
                item.get("verdict") != "CONTINUE" for item in iterations)):
            raise ValueError("cap status disagrees with iteration evidence")
        snapshot_name = summary.get("target_snapshot")
        if not isinstance(snapshot_name, str) or Path(snapshot_name).name != snapshot_name:
            raise ValueError("invalid target_snapshot")
        snapshot = rlc.read_regular_bytes(run_dir / snapshot_name, "target snapshot")
        if hashlib.sha256(snapshot).hexdigest() != summary.get("target_sha256"):
            raise ValueError("target snapshot hash mismatch")
        for item in iterations:
            vpath = run_dir / f"iter_{item['iter']}" / "verdict" / "verdict.json"
            vtext = rlc.read_regular_bytes(vpath, f"iteration {item['iter']} verdict").decode("utf-8")
            vobj = rlc._strict_loads(vtext, "verdict.json")
            if canonical(vobj) != vtext or rlc.validate_verdict(vobj):
                raise ValueError(f"iteration {item['iter']} verdict is invalid")
            if sha256_text(vtext) != item.get("verdict_sha256") or \
                    vobj.get("run_id") != summary["run_id"] or \
                    vobj.get("iter") != item["iter"] or \
                    vobj.get("verdict") != item.get("verdict"):
                raise ValueError(f"iteration {item['iter']} provenance mismatch")
        when = _parse_aware_utc(
            when_utc or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00"))
    except (OSError, UnicodeDecodeError, ValueError, TypeError, KeyError,
            json.JSONDecodeError, rlc.Refused) as exc:
        return 2, f"REFUSED: invalid completed run evidence: {exc}"

    hitl_path = run_dir / "hitl.jsonl"
    flags = os.O_RDWR | os.O_CREAT | os.O_APPEND | getattr(os, "O_CLOEXEC", 0)
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(hitl_path, flags, 0o600)
        with os.fdopen(fd, "r+", encoding="utf-8") as fh:
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
            fh.seek(0)
            previous = "0" * 64
            for line_no, line in enumerate(fh, 1):
                old = rlc._strict_loads(line, f"hitl.jsonl line {line_no}")
                claimed = old.pop("row_sha256", None)
                if old.get("previous_hitl_sha256") != previous or \
                        claimed != sha256_text(canonical(old)):
                    raise ValueError(f"broken HITL hash chain at line {line_no}")
                previous = claimed
            row = {
                "run_id": summary["run_id"], "iter": iterations[-1]["iter"],
                "final_status": final_status, "verdict": verdict,
                "who": who.strip(), "note": str(note), "when_utc": when,
                "run_summary_sha256": sha256_text(summary_text),
                "previous_hitl_sha256": previous,
            }
            row["row_sha256"] = sha256_text(canonical(row))
            fh.seek(0, os.SEEK_END)
            fh.write(canonical(row))
            fh.flush()
            os.fsync(fh.fileno())
    except (OSError, ValueError, TypeError, json.JSONDecodeError, rlc.Refused) as exc:
        return 2, f"REFUSED: cannot append HITL ledger: {exc}"
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
    r.add_argument("--producer-timeout-seconds", type=float, default=300.0)
    h = sub.add_parser("hitl")
    h.add_argument("--run-dir", required=True)
    h.add_argument("--verdict", required=True)
    h.add_argument("--who", required=True)
    h.add_argument("--note", default="")
    h.add_argument("--when-utc", default=None)
    a = ap.parse_args(argv)
    if a.cmd == "run":
        code, msg = run_cycle(Path(a.target), Path(a.run_dir), a.producer_cmd,
                              a.cap, a.threshold, a.producer_timeout_seconds)
    else:
        code, msg = record_hitl(Path(a.run_dir), a.verdict, a.who, a.note, a.when_utc)
    print(msg, file=sys.stderr if code == 2 else sys.stdout)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
