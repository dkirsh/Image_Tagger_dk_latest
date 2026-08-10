#!/usr/bin/env python3
"""Re-derive every VOLATILE figure in docs/REPO_STATE_MODEL_AND_PLAN.md BY EXECUTION,
then rewrite the generated-state header.

WHAT THIS DOES NOT DO, DELIBERATELY
-----------------------------------
It does not rewrite the prose of §5. It re-derives the figures, prints them next to what the
document currently says, and leaves reconciliation to a human or an agent. Auto-rewriting §5
would silently discard the interpretation attached to each number -- which failure is a missing
optional dependency and which is a contract violation -- and the interpretation is the part with
the value. The cost is that §5 can drift from this script's output. The mitigation is that this
script prints the drift loudly instead of papering over it.

WHAT IT REFUSES TO DO
---------------------
It refuses to stamp a fresh STATE_AS_OF that it did not earn.

  A timestamp that can be written whether or not the measurements succeeded is a PROXY for
  verification. Proxies get optimised for. If git is broken, if the registry will not import,
  if the tests cannot be collected -- and the script still writes a fresh-looking timestamp --
  then the freshness mechanism has become exactly the confident misinformation the state model
  exists to prevent, one layer down.

So: if fewer than QUORUM_MIN of the measurements return a value, this script writes
`STATE_AS_OF: FAILED-<utc>` and exits non-zero. A reader who sees FAILED knows the document is
unverified. A reader who sees a timestamp knows it was earned.

It also refuses to record `HEAD: UNKNOWN` as if it were a head. If git cannot be read, that is a
measurement failure and it counts against quorum.

Usage:
    python3 scripts/refresh_state_model.py [--check]

    --check   derive and report, but do not write. Exit 0 iff quorum met.
"""
from __future__ import annotations

import argparse
import importlib.util
import platform
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DOC = REPO / "docs" / "REPO_STATE_MODEL_AND_PLAN.md"

# How many of the measurements below must return a real value for a timestamp to be earned.
# Not 100%: an optional-dependency probe legitimately returns "absent". But a majority must
# have actually executed, or the run proves nothing.
QUORUM_MIN_FRACTION = 0.75

ABSENT = "ABSENT"
ERROR = "ERROR"

# Optional dependencies whose presence changes §5.3's test tallies. Named here so the header
# can bind the figures to the environment that produced them.
OPTIONAL_DEPS = ["numpy", "cv2", "PIL", "skimage", "scipy", "pytest"]


def sh(*args: str, cwd: Path | None = None, timeout: int = 120) -> str | None:
    """Run a command. Return stdout stripped, or None on ANY failure.

    None is the honest answer for 'the measurement did not happen'. It is counted against
    quorum. It is never rendered as a plausible-looking value.
    """
    try:
        r = subprocess.run(args, cwd=str(cwd or REPO), capture_output=True,
                           text=True, timeout=timeout)
    except Exception:
        return None
    if r.returncode != 0:
        return None
    return r.stdout.strip()


def git(*args: str) -> str | None:
    # --no-optional-locks is mandatory in this repo: plain `git status` leaves an index.lock
    # behind on the Cowork mount and blocks the native commits that follow. See CLAUDE.md.
    return sh("git", "--no-optional-locks", *args)


# ----------------------------------------------------------------------------- measurements
# Each measurement returns (label, command-as-shown-to-the-reader, value).
# `value` is ABSENT / ERROR when the measurement did not produce a fact. Those strings are
# deliberately un-number-like so nobody can mistake one for a figure.

def m_head():
    cmd = "git --no-optional-locks rev-parse HEAD"
    v = git("rev-parse", "HEAD")
    return ("HEAD", cmd, v or ERROR)


def m_branch():
    cmd = "git --no-optional-locks rev-parse --abbrev-ref HEAD"
    v = git("rev-parse", "--abbrev-ref", "HEAD")
    return ("branch", cmd, v or ERROR)


def m_head_date():
    cmd = "git --no-optional-locks log -1 --format=%ad --date=iso"
    v = git("log", "-1", "--format=%ad", "--date=iso")
    return ("HEAD date", cmd, v or ERROR)


def m_commits_total():
    cmd = "git --no-optional-locks rev-list --count HEAD"
    v = git("rev-list", "--count", "HEAD")
    return ("commits total", cmd, v or ERROR)


def m_commits_7d():
    cmd = "git --no-optional-locks rev-list --count --since='7 days ago' HEAD"
    v = git("rev-list", "--count", "--since=7 days ago", "HEAD")
    return ("commits last 7d", cmd, v or ERROR)


def m_commits_14d():
    cmd = "git --no-optional-locks rev-list --count --since='14 days ago' HEAD"
    v = git("rev-list", "--count", "--since=14 days ago", "HEAD")
    return ("commits last 14d", cmd, v or ERROR)


def m_tracked():
    cmd = "git --no-optional-locks ls-files | wc -l"
    v = git("ls-files")
    return ("tracked files", cmd, str(len(v.splitlines())) if v is not None else ERROR)


def m_porcelain():
    cmd = "git --no-optional-locks status --porcelain | wc -l"
    v = git("status", "--porcelain")
    # NOTE: empty output is a VALID answer here (clean tree) and must not read as failure.
    return ("working-tree entries not clean", cmd,
            str(len([x for x in v.splitlines() if x.strip()])) if v is not None else ERROR)


def _load_registry():
    p = REPO / "annotation_socket" / "registry.py"
    if not p.exists():
        return None
    sys.path.insert(0, str(REPO))
    try:
        spec = importlib.util.spec_from_file_location("_reg_probe", p)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m
    except Exception:
        return None


_REG = None


def _reg():
    global _REG
    if _REG is None:
        _REG = _load_registry() or False
    return _REG or None


REG_CMD = ("PYTHONPATH=. python3 -c \"from annotation_socket.registry import PREDICATES, "
           "MODEL_VERSION; ...\"")


def m_model_version():
    r = _reg()
    return ("MODEL_VERSION", REG_CMD, getattr(r, "MODEL_VERSION", ERROR) if r else ERROR)


def m_predicates():
    r = _reg()
    if not r:
        return ("predicates registered", REG_CMD, ERROR)
    P = r.PREDICATES
    from collections import Counter
    kind = Counter(p["kind"] for p in P)
    tier = Counter(p["tier_hint"] for p in P)
    audit = Counter(p["audit_class"] for p in P)
    img_only = sum(1 for p in P if not p["requires"])
    plan_only = sum(1 for p in P if p["requires"] == frozenset({"plan"}))
    extra = sum(1 for p in P if p["requires"] and p["requires"] != frozenset({"plan"}))
    detail = (f"{len(P)} total | kind: " + ", ".join(f"{k}={v}" for k, v in sorted(kind.items()))
              + " | tier_hint: " + ", ".join(f"{k}={v}" for k, v in sorted(tier.items()))
              + " | audit_class: " + ", ".join(f"{k}={v}" for k, v in sorted(audit.items()))
              + f" | requires: image-only={img_only}, plan-only={plan_only}, extra-inputs={extra}")
    return ("predicate registry", REG_CMD, detail)


def m_greens():
    """Names, never a bare count. A count of GREEN predicates is not auditable; a list is."""
    r = _reg()
    if not r:
        return ("GREEN-ceiling predicates (names)", REG_CMD, ERROR)
    names = [p["id"] for p in r.PREDICATES if p["tier_hint"] == "GREEN"]
    return ("GREEN-ceiling predicates (names)", REG_CMD, f"{len(names)}: " + ", ".join(names))


TEST_CMD = ("for f in annotation_socket/tests/test_*.py; do PYTHONPATH=. python3 -c "
            "'<import module, call each test_* callable, tally>'; done")


def m_socket_tests():
    """Run the socket tests the way this repo runs them: per file, without pytest.

    pytest is not guaranteed present (it is absent in the Cowork sandbox), and CLAUDE.md
    prescribes per-file runs. Files that cannot even be imported are reported as UNCOLLECTABLE
    rather than being silently dropped from the denominator -- dropping them would inflate the
    pass rate, which is the exact arithmetic this repo exists to refuse.
    """
    tdir = REPO / "annotation_socket" / "tests"
    if not tdir.is_dir():
        return ("socket tests", TEST_CMD, ABSENT)
    files = sorted(tdir.glob("test_*.py"))
    if not files:
        return ("socket tests", TEST_CMD, ABSENT)
    # The runner lives in a temp dir OUTSIDE the repo, and puts the repo on sys.path itself
    # (argv[2]) rather than relying on being co-located with it.
    #
    # WHY, and it was found by running this, not by reading it: the first version wrote
    # `.refresh_test_runner.py` into the repo root and unlinked it in a `finally`. On the Cowork
    # mount `unlink` is denied (see CLAUDE.md), the except swallowed the error, and the file was
    # still sitting untracked in `git status` afterwards. A measurement instrument that leaves
    # debris in the thing it measures is not read-only, however loudly its docstring says so.
    runner = r'''
import importlib.util, sys
sys.path.insert(0, sys.argv[2])
spec = importlib.util.spec_from_file_location("t", sys.argv[1])
m = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(m)
except BaseException as e:
    print("UNCOLLECTABLE|%s: %s" % (type(e).__name__, str(e).splitlines()[0][:100])); raise SystemExit(0)
fns = [n for n in dir(m) if n.startswith("test_") and callable(getattr(m, n))]
p = f = 0; fails = []
for n in fns:
    try:
        getattr(m, n)(); p += 1
    except BaseException as e:
        f += 1; fails.append("%s (%s)" % (n, type(e).__name__))
print("RAN|%d|%d|%d|%s" % (p, f, len(fns), "; ".join(fails)))
'''
    with tempfile.TemporaryDirectory(prefix="refresh_state_model_") as td:
        rp = Path(td) / "runner.py"
        rp.write_text(runner)
        collected = uncollectable = passed = failed = 0
        detail = []
        for f in files:
            out = sh(sys.executable, str(rp), str(f), str(REPO), timeout=180)
            if out is None:
                uncollectable += 1
                detail.append(f"{f.name}: RUNNER-ERROR")
                continue
            line = [x for x in out.splitlines() if x.startswith(("RAN|", "UNCOLLECTABLE|"))]
            if not line:
                uncollectable += 1
                detail.append(f"{f.name}: NO-VERDICT")
                continue
            line = line[-1]
            if line.startswith("UNCOLLECTABLE|"):
                uncollectable += 1
                detail.append(f"{f.name}: UNCOLLECTABLE {line.split('|', 1)[1]}")
            else:
                _, p_, f_, t_, fl = line.split("|", 4)
                passed += int(p_); failed += int(f_); collected += int(t_)
                if int(f_):
                    detail.append(f"{f.name}: {p_} pass / {f_} FAIL -> {fl}")
        summary = (f"{len(files)} files | {len(files) - uncollectable} collected, "
                   f"{uncollectable} UNCOLLECTABLE | {collected} tests collected, "
                   f"{passed} pass, {failed} fail")
        if detail:
            summary += "\n        " + "\n        ".join(detail)
        return ("socket tests", TEST_CMD, summary)


# The needle is assembled at runtime and NEVER appears as a literal in this file.
#
# WHY, and this too was found by running it: the first version spelled the path literally in
# both the grep and the command-as-shown, so this file matched its own search and the count
# came back 14 instead of 13. The instrument was inside the sample. Whenever a measurement can
# see itself, the number it reports is about the measurement, not about the repo.
NEEDLE = "/Users/" + "davidusa"


def m_hardcoded_paths():
    cmd = (r'''grep -rln "''' + NEEDLE + r'''" --include=*.py . '''
           r"""| grep -v _to_delete | grep -v '\.venv' | wc -l""")
    out = sh("bash", "-lc",
             r"""cd "$(printf %s '""" + str(REPO) + r"""')" && grep -rln '""" + NEEDLE + r"""' """
             r"""--include=*.py . 2>/dev/null | grep -v _to_delete | grep -v '\.venv' || true""")
    label = "tracked .py hard-coding " + NEEDLE
    if out is None:
        return (label, cmd, ERROR)
    names = [x.strip() for x in out.splitlines() if x.strip()]
    return (label, cmd, f"{len(names)}: " + ", ".join(sorted(n.lstrip('./') for n in names)))


MEASUREMENTS = [
    m_head, m_branch, m_head_date, m_commits_total, m_commits_7d, m_commits_14d,
    m_tracked, m_porcelain, m_model_version, m_predicates, m_greens,
    m_socket_tests, m_hardcoded_paths,
]


def env_string() -> str:
    parts = [f"python{platform.python_version()}", platform.system().lower()]
    dep = []
    for mod in OPTIONAL_DEPS:
        try:
            __import__(mod)
            dep.append(f"{mod}=yes")
        except Exception:
            dep.append(f"{mod}=NO")
    return " ".join(parts) + " · " + " ".join(dep)


# ----------------------------------------------------------------------------- header write

HEADER_KEYS = ["STATE_AS_OF", "HEAD", "STALE_AFTER_DAYS", "VERIFIED_BY",
               "MEASURED_ON", "MEASUREMENT_QUORUM"]


def rewrite_header(text: str, values: dict) -> tuple[str, list[str]]:
    """Rewrite EVERY generated header line, not just some of them.

    The reference implementation this is modelled on declares four generated lines and
    machine-writes two. A line that claims to be generated but is hand-maintained is a small,
    permanent lie in the most-read part of the document. Every key in HEADER_KEYS that appears
    in `values` is written here, and any that is not found in the document is reported.
    """
    missing = []
    for k in HEADER_KEYS:
        if k not in values:
            continue
        pat = re.compile(r"^- `" + k + r": [^`]*`", re.M)
        if not pat.search(text):
            missing.append(k)
            continue
        text = pat.sub("- `" + k + ": " + values[k].replace("\\", "\\\\") + "`", text, count=1)
    return text, missing


def read_header(text: str) -> dict:
    out = {}
    for k in HEADER_KEYS:
        m = re.search(r"^- `" + k + r": ([^`]*)`", text, re.M)
        if m:
            out[k] = m.group(1).strip()
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="derive and report; do not write the document")
    args = ap.parse_args()

    if not DOC.exists():
        print(f"FATAL: {DOC} does not exist. Nothing to refresh.", file=sys.stderr)
        return 3

    results = []
    for fn in MEASUREMENTS:
        try:
            results.append(fn())
        except Exception as e:  # a measurement must never take the refresher down
            results.append((fn.__name__, "(raised)", f"{ERROR}: {type(e).__name__}: {e}"))

    print("=" * 78)
    print("RE-DERIVED BY EXECUTION  —  §5 of docs/REPO_STATE_MODEL_AND_PLAN.md")
    print("=" * 78)
    for label, cmd, val in results:
        print(f"\n{label}")
        print(f"    $ {cmd}")
        print(f"    = {val}")

    good = [r for r in results if not str(r[2]).startswith((ABSENT, ERROR))]
    quorum = len(good) / len(results)
    quorum_str = (f"{len(good)}/{len(results)} measurements returned a value "
                  f"({len(results) - len(good)} ABSENT or ERROR)")

    print("\n" + "=" * 78)
    print(f"QUORUM: {quorum_str}  ->  {quorum:.0%} (need {QUORUM_MIN_FRACTION:.0%})")
    print("=" * 78)

    text = DOC.read_text()
    before = read_header(text)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")

    head_val = dict((r[0], r[2]) for r in results).get("HEAD", ERROR)
    earned = quorum >= QUORUM_MIN_FRACTION and not str(head_val).startswith(ERROR)

    if earned:
        values = {
            "STATE_AS_OF": now,
            "HEAD": head_val[:9],
            "MEASURED_ON": env_string(),
            "MEASUREMENT_QUORUM": quorum_str,
        }
        verdict = "EARNED"
    else:
        # The refusal. This is the whole point of the script.
        values = {
            "STATE_AS_OF": f"FAILED-{now}",
            "MEASURED_ON": env_string(),
            "MEASUREMENT_QUORUM": quorum_str + "  <- BELOW QUORUM, figures NOT verified",
        }
        if not str(head_val).startswith(ERROR):
            values["HEAD"] = head_val[:9]
        verdict = "REFUSED"

    print(f"\nSTAMP: {verdict}")
    if verdict == "REFUSED":
        print("  Too few measurements executed for a fresh timestamp to mean anything.")
        print("  Writing STATE_AS_OF: FAILED-<utc> so a reader cannot mistake this for a")
        print("  verified state. Fix the measurements, then re-run.")

    if args.check:
        print("\n--check: document NOT written.")
        return 0 if earned else 1

    new_text, missing = rewrite_header(text, values)
    if missing:
        print(f"\nWARNING: header keys declared generated but not found in the document: "
              f"{', '.join(missing)}")
    DOC.write_text(new_text)

    after = read_header(new_text)
    print("\nHEADER REWRITTEN:")
    for k in HEADER_KEYS:
        if before.get(k) != after.get(k):
            print(f"  {k}:\n      was: {before.get(k)}\n      now: {after.get(k)}")

    print("\nREMINDER: §5 PROSE WAS NOT REWRITTEN — deliberately (see §10.6).")
    print("Compare the figures printed above against what §5 says, and reconcile by hand.")
    print("The numbers are mechanical; the interpretation beside them is not, and")
    print("auto-rewriting would destroy the interpretation to save the numbers.")

    return 0 if earned else 1


if __name__ == "__main__":
    raise SystemExit(main())
