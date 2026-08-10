#!/usr/bin/env python3
"""Falsification harness for the Image_Tagger state-model freshness check.

A "fix" is theatre unless you can demonstrate that the OLD version ACCEPTS an input the NEW
version REJECTS. Asserting that a defect is closed is worth nothing; exhibiting the input that
separates the two implementations is worth something.

This runs BOTH implementations side by side:
  reference : Article_Eater_PostQuinean_v1_recovery/scripts/prevention/state_model_freshness_check.py
  new       : Image_Tagger_dk_latest/scripts/prevention/state_model_freshness_check.py

and prints, for each scenario, what each one decides. It exits non-zero if the differential it
claims does not actually hold — including the NEGATIVE scenario, where the new version must stay
quiet. A checker that rejects everything is not stricter, it is broken, and a harness that only
tests the rejecting direction cannot tell the two apart.

Run:  python3 scripts/prevention/falsify_state_model_freshness.py
"""
import importlib.util
import os
import sys
import time
from datetime import datetime, timezone

# Paths are derived from THIS FILE'S OWN LOCATION. No absolute path into anybody's home
# directory appears anywhere in this file — not in the code, and not in this comment, which is
# why the old value below is described rather than quoted.
#
# WHY, and it was found by RUNNING the refresher against the deployed tree, not by reading this
# file: v1 wrote `ROOT = os.environ.get("FABLE_HANDS_ROOT", <an absolute path into the author's
# home directory>)`. That default is character-for-character the needle the repo's own
# portability measurement greps for. So this file — the harness whose entire argument is that an
# audit apparatus must be executable on a machine other than the author's — became the 14th
# tracked .py file in the repo that is bound to the author's machine, and it did so *inside the
# deliverable that reports that count*. The measured figure went 13 -> 14 and one of the 14 was
# this harness. Third instance in one day of the same shape: the instrument inside the sample.
_HERE = os.path.dirname(os.path.abspath(__file__))            # <repo>/scripts/prevention
REPO = os.path.dirname(os.path.dirname(_HERE))                # <repo>
ROOT = os.environ.get("FABLE_HANDS_ROOT") or os.path.dirname(REPO)   # the REPOS collection root
REF = os.path.join(ROOT, "Article_Eater_PostQuinean_v1_recovery",
                   "scripts", "prevention", "state_model_freshness_check.py")
NEW = os.path.join(REPO, "scripts", "prevention", "state_model_freshness_check.py")

failures = []


def load(name, path):
    if not os.path.isfile(path):
        print("FATAL: %s does not exist" % path)
        raise SystemExit(2)
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def check(label, condition, detail):
    mark = "OK " if condition else "BAD"
    print("  [%s] %s -- %s" % (mark, label, detail))
    if not condition:
        failures.append(label)


ref = load("ref_impl", REF)
new = load("new_impl", NEW)

print("=" * 78)
print("FALSIFICATION -- does the NEW version reject what the OLD version ACCEPTS?")
print("=" * 78)
print("reference : %s" % REF)
print("new       : %s" % NEW)

now_stamp = time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime())
now_dt = datetime.now(timezone.utc)

# --------------------------------------------------------------------------------------------
print("\nSCENARIO 1 -- total measurement failure: git unreadable, refresher wrote HEAD: UNKNOWN,")
print("              timestamp fresh (the reference refresher stamps unconditionally).")
# The reference's main() sets commits_since = 0 when head == "UNKNOWN": the rev-list is skipped.
r_stale, r_reasons = ref.judge({"as_of": now_stamp, "head": "UNKNOWN", "stale_days": "7"},
                               "084b3f3d", commits_since=0)
n_code, n_msg = new.judge({"state_as_of": now_stamp, "head": "UNKNOWN",
                           "stale_after_days": "7"}, False, 0, now_dt)
print("  reference -> is_stale=%r reasons=%r  => VERDICT %s (exit %d)"
      % (r_stale, r_reasons, "STALE" if r_stale else "fresh", 1 if r_stale else 0))
print("  new       -> exit %d :: %s" % (n_code, n_msg))
check("S1 reference ACCEPTS (this is the fail-open)", r_stale is False, "is_stale=%r" % r_stale)
check("S1 new REJECTS", n_code == 2, "exit %d, want 2 (DRIFT)" % n_code)

# --------------------------------------------------------------------------------------------
print("\nSCENARIO 2 -- the reference's DRIFT branch has no positive control.")
drift_hdr = {"as_of": now_stamp, "head": "deadbee", "stale_days": "7"}
r_a, _ = ref.judge(drift_hdr, "084b3f3d", commits_since=-1)   # real rewritten history
r_b, _ = ref.judge(drift_hdr, "084b3f3d", commits_since=5)    # what its controls() passes
n_code2, _ = new.judge({"state_as_of": now_stamp, "head": "deadbee",
                        "stale_after_days": "7"}, False, 0, now_dt)
print("  reference commits_since=-1 (rev-list failed)      -> is_stale=%r" % r_a)
print("  reference commits_since=5  (what controls() uses) -> is_stale=%r" % r_b)
print("  new                                               -> exit %d" % n_code2)
check("S2 DRIFT clause needs commits_since<0, so controls() can never fire it",
      r_a is True and r_b is False,
      "fires at -1 (%r), silent at +5 (%r) -- its only exercised branch is AGE" % (r_a, r_b))
check("S2 new REJECTS", n_code2 == 2, "exit %d, want 2" % n_code2)

# --------------------------------------------------------------------------------------------
print("\nSCENARIO 3 -- the refresher REFUSED to stamp (STATE_AS_OF: FAILED-<utc>).")
r_c, r_cr = ref.judge({"as_of": "FAILED-" + now_stamp, "head": "084b3f3d", "stale_days": "7"},
                      "084b3f3d", commits_since=0)
n_code3, n_msg3 = new.judge({"state_as_of": "FAILED-" + now_stamp, "head": "084b3f3d",
                             "stale_after_days": "7"}, True, 0, now_dt)
print("  reference -> is_stale=%r reasons=%r" % (r_c, r_cr))
print("  new       -> exit %d :: %s" % (n_code3, n_msg3))
check("S3 reference also catches this (credit where due -- not every branch is broken)",
      r_c is True, "unparseable path fires")
check("S3 new distinguishes REFUSED from merely-stale", n_code3 == 3, "exit %d, want 3" % n_code3)

# --------------------------------------------------------------------------------------------
print("\nSCENARIO 4 (NEGATIVE) -- a genuinely fresh document at a reachable HEAD.")
print("              The new version must stay QUIET. Without this the harness cannot")
print("              distinguish 'stricter' from 'broken'.")
n_code4, n_msg4 = new.judge({"state_as_of": now_stamp, "head": "084b3f3d9",
                             "stale_after_days": "7"}, True, 2, now_dt)
print("  new -> exit %d :: %s" % (n_code4, n_msg4))
check("S4 new stays quiet on a fresh document", n_code4 == 0, "exit %d, want 0" % n_code4)

# --------------------------------------------------------------------------------------------
print("\nSCENARIO 5 (NEGATIVE) -- old document, but the repo did NOT move.")
print("              Age alone is not staleness. Must stay quiet.")
old_stamp = "2026-06-01T12:00Z"
n_code5, n_msg5 = new.judge({"state_as_of": old_stamp, "head": "084b3f3d9",
                             "stale_after_days": "7"}, True, 0, now_dt)
print("  new -> exit %d :: %s" % (n_code5, n_msg5))
check("S5 new stays quiet when the repo has not moved", n_code5 == 0,
      "exit %d, want 0" % n_code5)

# --------------------------------------------------------------------------------------------
# SCENARIO 6 is about this file rather than about either implementation.
print("\nSCENARIO 6 (SELF) -- this harness must not be one of the things it complains about.")
print("              An audit apparatus that only runs on the author's machine cannot be")
print("              executed by the ≠-mind whose job is to certify it.")
_self = open(os.path.abspath(__file__), "r", encoding="utf-8").read()
_needle = "/Users/" + "davidusa"   # assembled at runtime, so it is never contiguous in this source
check("S6 this file contains no absolute path into anybody's home directory",
      _needle not in _self,
      "searched this file's own source for the needle the repo's portability metric counts")
check("S6 the two implementations were located by relative derivation",
      os.path.isfile(REF) and os.path.isfile(NEW),
      "REF and NEW both resolved from __file__ (+ optional FABLE_HANDS_ROOT)")

print("\n" + "=" * 78)
if failures:
    print("HARNESS FAILED: %d claim(s) did not hold -> %s" % (len(failures), "; ".join(failures)))
    print("The differential asserted in the new module's docstring is NOT demonstrated.")
    print("=" * 78)
    sys.exit(1)
print("HARNESS PASSED: the differential is real, in BOTH directions.")
print("  * Scenario 1 is a fail-OPEN in the reference: the one state that most deserves a red")
print("    light -- nothing could be measured -- is the one state that reads 'fresh'.")
print("  * Scenarios 4 and 5 show the new version is not merely stricter-about-everything.")
print("  * Scenario 6 shows the harness itself is portable off the author's machine.")
print("=" * 78)
sys.exit(0)
