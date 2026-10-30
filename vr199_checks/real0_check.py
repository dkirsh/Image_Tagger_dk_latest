#!/usr/bin/env python3
"""real0_check.py — the REAL-0 record checker, read-only.

Built from the REAL-0 brief as released at New_VR_Platform b381277 (students/task_briefs/REAL-0.md,
REAL-0_SETUP_PROMPT.md) and the Look notes panel's export in the BIM pair viewer at that revision.
It answers the mechanical half of the brief's ten success criteria for one student's record and
lists, as flags, what a person must decide. It never passes or fails a zero-pin seal: the brief's
criterion 1 allows "nothing noticed, with a reason in notes.md" while criteria 3, 4 and 6 presuppose
findings, so such a record is routed to David.

Two layers:
  * ``check(snapshot)`` is pure. A ``Snapshot`` holds the record folder's files at the handed-in
    commit, every committed version of look_findings.json in order, the task-state file and,
    optionally, the pull request's description. Tests build snapshots directly.
  * ``snapshot_from_git(repo, ref, base)`` reads those from a fetched ref with ``git show`` and
    ``git log`` only. ``main()`` is the command line.

Flag severities: ``block`` (the record is incomplete per the brief), ``judgment`` (a person decides;
the checker cannot), ``manual`` (evidence the checker could not read, e.g. a PR description it was
not given). ``Result.complete`` is True only when no ``block`` flag was raised and the seal is not
zero-pin.

Lane: Image_Tagger_dk_latest (tanishq). Never imports New_VR_Platform code.

Run:  python3 vr199_checks/real0_check.py --repo <New_VR_Platform clone> --ref <fetched ref>
      python3 vr199_checks/real0_check.py --repo <clone> --pr 41      # fetches pull/41/head first
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

TASK_ID = "REAL-0"
ROOM_ID = "gni_model18_office__ceiling_height"
REQUIRED_FILES = ("notes.md", "look_findings.json", "look_trial.json", "ranking.md")
RING = {"Diego": "Paco", "Paco": "Sami", "Sami": "Juan", "Juan": "Raven", "Raven": "Diego"}  # checker -> author
FIRST_RECORD_CHECKER = "Michael"          # D-088: Michael Bongiorno checks the first record handed in
ATTESTATION = ("I looked for myself, wrote every line in my own words, and before sealing pass 1 read "
               "neither the pass-2 prompts, nor the part of this brief below its stop line, nor another "
               "student's list.")
FINDING_ID = re.compile(r"t-[0-9a-f]{16}\.p[12]-\d{2}")
CLOCK = re.compile(r"\b(\d{1,2}):(\d{2})\b")
HEX = re.compile(r"\b[0-9a-f]{7,40}\b")
CRASH = re.compile(r"Traceback|TypeError|UnicodeDecodeError|crash|BLOCKED", re.I)
VAGUE = re.compile(r"^\W*(it\s+)?(looks?\s+)?(fake|weird|off|odd|wrong|bad|unreal|strange)\W*$", re.I)

BLOCK, JUDGMENT, MANUAL = "block", "judgment", "manual"


@dataclass
class Flag:
    code: str
    severity: str
    message: str


@dataclass
class Snapshot:
    """Everything the checker reads, already out of git."""
    login: str
    head: str
    files: dict[str, bytes]                                   # record-folder file name -> bytes, at head
    history: list[tuple[str, str, Any]] = field(default_factory=list)  # (sha, date, parsed look_findings or None)
    seal_commit_files: dict[str, list[str]] = field(default_factory=dict)  # sha -> paths that commit touched
    worklog: str | None = None                                # students/worklogs/<login>/REAL-0.md at head
    pr_body: str | None = None
    outside_paths: list[str] = field(default_factory=list)    # PR paths outside record folder + worklog


@dataclass
class Result:
    login: str
    head: str
    files_present: list[str]
    files_missing: list[str]
    files_unexpected: list[str]
    identity: dict[str, Any]
    seal: dict[str, Any]
    pictures: dict[str, Any]
    findings: dict[str, Any]
    ranking: dict[str, Any]
    notes: dict[str, Any]
    validators: dict[str, Any]
    checker: dict[str, Any]
    hours_lines: list[str]
    attestation: dict[str, Any]
    flags: list[Flag]
    complete: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# --------------------------------------------------------------------------- #
# parsers, each pure and tested on both layouts students actually used
# --------------------------------------------------------------------------- #
def parse_ranking(text: str) -> list[dict[str, Any]]:
    """Ranked entries in order of appearance, from any of the layouts seen in hand-ins:

      ``1. t-…p1-02`` then ``Fix: …`` on the next line          (PR #41)
      ``t-…p1-06 — <fix …>`` with no numbering                   (PR #42)
      ``1. `t-…p2-06` — what it is. Fix: …`` on one line          (staff pilot)
      ``1. Control of the character - make it …`` with no id      (PR #44)

    An entry starts at a numbered line or at a line holding a finding id; continuation lines join
    the entry before them. Each entry reports the ids it names and whether text beyond the id gives
    a fix (any words, or "I cannot say").
    """
    numbered = re.compile(r"\d+\s*[.)]")
    entries: list[list[str]] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        open_numbered_without_id = bool(entries) and bool(numbered.match(entries[-1][0])) \
            and not FINDING_ID.search(" ".join(entries[-1]))
        if numbered.match(line) or not entries:
            entries.append([line])
        elif FINDING_ID.search(line) and not open_numbered_without_id:
            entries.append([line])
        else:
            entries[-1].append(line)                           # "Fix: …" under its id, or a wrapped line
    out = []
    for parts in entries:
        body = " ".join(parts)
        ids = FINDING_ID.findall(body)
        if not ids and not numbered.match(body):
            continue                                           # a title or prose line, not a ranked entry
        rest = FINDING_ID.sub(" ", numbered.sub(" ", body, count=1))
        rest = re.sub(r"\bfix\s*:", " ", rest, flags=re.I)     # the label alone is not a fix sentence
        out.append({"text": body, "ids": ids, "has_fix": bool(re.search(r"[A-Za-z]{2,}", rest))})
    return out


def parse_notes(text: str) -> dict[str, Any]:
    """Start line, prior-exposure line 2, end line and the minutes between them (criterion 10)."""
    lines = text.splitlines()
    nonblank = [l for l in lines if l.strip()]
    i_start = next((i for i, l in enumerate(nonblank) if re.search(r"\bstart", l, re.I) and CLOCK.search(l)), None)
    i_end = next((i for i in range(len(nonblank) - 1, -1, -1)
                  if re.search(r"\bend\b", nonblank[i], re.I) and CLOCK.search(nonblank[i])), None)
    start = nonblank[i_start] if i_start is not None else None
    end = nonblank[i_end] if i_end is not None else None
    second = lines[1].strip() if len(lines) > 1 else ""
    if re.match(r"prior exposure\s*:", second, re.I):
        prior = "labelled"
    elif second.lower().strip(" .") == "none":
        prior = "bare_none"
    else:
        prior = "absent"
    minutes = None
    same_line = i_start is not None and i_start == i_end
    if start and end and not same_line and _date_part(start) == _date_part(end):
        a, b = CLOCK.findall(start)[0], CLOCK.findall(end)[-1]
        minutes = (int(b[0]) * 60 + int(b[1])) - (int(a[0]) * 60 + int(a[1]))
    return {"start_line": start, "end_line": end, "start_is_line_1": bool(lines) and lines[0] == start,
            "end_is_last_line": i_end is not None and i_end == len(nonblank) - 1, "same_line": same_line,
            "line_2": second, "prior_exposure": prior, "minutes": minutes}


def _date_part(line: str) -> str:
    """The date words of a start or end line ("Sat 24 Oct"), so lines on different days are not
    subtracted as if they were one day."""
    s = CLOCK.sub(" ", line.lower())
    s = re.sub(r"\b(start|end|time)\b", " ", s)
    return " ".join(re.sub(r"[^a-z0-9/]+", " ", s).split())


def _items(text: str) -> list[str]:
    """Split a task-state file into items: a list item or numbered item with its indented
    continuation lines, which may run across a blank line (Diego's step-2 paragraph does)."""
    items: list[list[str]] = []
    for raw in text.splitlines():
        if not raw.strip():
            continue
        marker = re.match(r"\s*([-*]|\d+\.)\s", raw)
        indented = raw[:1].isspace()
        if items and indented and not marker:
            items[-1].append(raw.strip())
        else:
            items.append([raw.strip()])
    return [" ".join(i) for i in items]


def parse_validators(worklog: str) -> dict[str, Any]:
    """The two validator results the hand-in records (criteria 2 and 8): pass, fail, crashed, absent."""
    out = {"history": "absent", "package": "absent", "history_text": None, "package_text": None}
    for item in _items(worklog):
        if "validate_look_findings" in item or re.search(r"history validator", item, re.I):
            kind = "history"
        elif "validate_package" in item or re.search(r"package validator", item, re.I):
            kind = "package"
        else:
            continue
        if kind == "history" and CRASH.search(item):
            status = "crashed"
        elif kind == "package" and re.search(r"PASS\s+\d+\s+FAIL 0", item):
            status = "pass"
        elif re.search(r"FAIL\s+0", item):
            status = "pass"
        elif re.search(r"FAIL\s+[1-9]", item):
            status = "fail"
        else:
            continue
        if out[kind] in ("absent", "pass") or status in ("crashed", "fail"):
            out[kind], out[kind + "_text"] = status, item[:240]
    return out


def parse_checker(worklog: str, login: str) -> dict[str, Any]:
    line = next((l.strip() for l in worklog.splitlines() if re.search(r"named checker", l, re.I)), None)
    named = None
    if line:
        named = re.sub(r"^[-*\s]*named checker\s*:\s*", "", line, flags=re.I).strip("` ")
    bad = bool(named) and bool(re.search(r"claude|gemini|codex|gpt|\bAI\b|" + re.escape(login), named, re.I))
    return {"line": line, "named": named, "student_or_ai": bad}


def parse_attestation(body: str | None, seal_sha: str | None) -> dict[str, Any]:
    """Criterion 7's fields in the PR description: the sentence, a name, a date, the seal's hash."""
    if body is None:
        return {"supplied": False}
    norm = " ".join(body.split())
    hashes = HEX.findall(body)
    return {"supplied": True,
            "sentence": " ".join(ATTESTATION.split()) in norm,
            "date": bool(re.search(r"\b20\d\d-\d\d-\d\d\b|\b\d{1,2} (Oct|Nov|October|November)\b", body)),
            "seal_hash": bool(seal_sha) and any(seal_sha.startswith(h) for h in hashes),
            "checker_names": [n for n in list(RING) + [FIRST_RECORD_CHECKER] if re.search(r"\b" + n + r"\b", body)],
            "real_designation": sorted({m for line in body.splitlines() if "REAL" in line
                                        for m in FINDING_ID.findall(line)})}


# --------------------------------------------------------------------------- #
# the check
# --------------------------------------------------------------------------- #
def check(s: Snapshot) -> Result:
    flags: list[Flag] = []

    def flag(code: str, severity: str, message: str) -> None:
        flags.append(Flag(code, severity, message))

    names = sorted(s.files)
    present = [f for f in REQUIRED_FILES if f in s.files]
    missing = [f for f in REQUIRED_FILES if f not in s.files]
    unexpected = [n for n in names if n not in REQUIRED_FILES and not re.fullmatch(r"look_.+\.jpg", n)]
    for f in missing:
        flag("missing_file", BLOCK, f"required file {f} is not in the record folder")
    for n in unexpected:
        flag("unexpected_file", JUDGMENT, f"file {n} is not one the brief asks for")
    for p in s.outside_paths:
        flag("outside_path", BLOCK, f"the pull request changes {p}, outside the record folder and task-state file")
    if s.worklog is None:
        flag("missing_worklog", BLOCK, f"no task-state file students/worklogs/{s.login}/REAL-0.md")

    doc = _json(s.files.get("look_findings.json"), "look_findings.json", flag)
    trial = _json(s.files.get("look_trial.json"), "look_trial.json", flag)
    findings = list((doc or {}).get("findings") or [])
    p1 = [f for f in findings if f.get("pass") == 1]
    p2 = [f for f in findings if f.get("pass") == 2]
    seal = (doc or {}).get("pass1_seal")

    # criterion 1: identity
    identity = {"student": (doc or {}).get("student"), "task_id": (doc or {}).get("task_id")}
    if doc is not None:
        if identity["student"] != s.login:
            flag("student_mismatch", BLOCK, f"student is {identity['student']!r}, folder login is {s.login!r}")
        if identity["task_id"] != TASK_ID:
            flag("task_id", BLOCK, f"task_id is {identity['task_id']!r}")
        if findings:
            wrong = [f.get("finding_id") for f in findings if f.get("room_id") != ROOM_ID]
            identity["room_ok"] = f"{len(findings) - len(wrong)}/{len(findings)}"
            if wrong:
                flag("room_id", BLOCK, f"findings not in {ROOM_ID}: {wrong}")
        else:
            trials = (trial or {}).get("trials") or {}
            cids = [t.get("contract_id") for t in (trials.values() if isinstance(trials, dict) else trials)
                    if isinstance(t, dict)]
            identity["room_ok"] = f"{cids.count(ROOM_ID)}/{len(cids)} trial contract_id"

    # criteria 1 and 2: the seal, its count, and its history
    sealed_ids = list((seal or {}).get("pass1_finding_ids") or [])
    seal_info: dict[str, Any] = {"present": seal is not None, "sealed_pins": len(sealed_ids),
                                 "nothing_noticed": (seal or {}).get("nothing_noticed"),
                                 "pass1": len(p1), "pass2": len(p2)}
    zero_pin = seal is not None and (seal.get("nothing_noticed") is True or not sealed_ids)
    if seal is None:
        flag("no_seal", BLOCK, "look_findings.json has no pass1_seal")
    elif zero_pin:
        flag("zero_pin_seal", JUDGMENT, "pass 1 sealed with no pins: criterion 1 allows it with a reason in "
             "notes.md, criteria 3, 4 and 6 presuppose findings; route to David, neither pass nor fail")
    elif len(sealed_ids) < 5:
        flag("few_sealed_pins", BLOCK, f"{len(sealed_ids)} sealed pass-1 pins; criterion 1 asks for at least five")
    mism = sorted(set(sealed_ids) ^ {f.get("finding_id") for f in p1})
    for m in mism:
        flag("seal_mismatch", BLOCK, f"pass-1 finding and seal disagree on {m}")
    seal_info.update(_history(s, flag))

    # pictures against pins (step 4; criterion 6 needs them)
    want = {(f.get("location") or {}).get("screenshot") or f"look_{f.get('finding_id')}.jpg" for f in findings}
    jpgs = {n for n in names if n.endswith(".jpg")}
    not_jpeg = sorted(j for j in jpgs if not s.files[j][:2] == b"\xff\xd8")
    pictures = {"pins_with_picture": f"{len(want & jpgs)}/{len(want)}",
                "pictures_with_pin": f"{len(jpgs & want)}/{len(jpgs)}", "not_jpeg": not_jpeg}
    for m in sorted(want - jpgs):
        flag("pin_without_picture", BLOCK, f"no picture {m}")
    for m in sorted(jpgs - want):
        flag("picture_without_pin", JUDGMENT, f"picture {m} matches no pin")
    for j in not_jpeg:
        flag("not_jpeg", BLOCK, f"{j} is not a JPEG")

    # criteria 3 and 4
    vague = [f.get("finding_id") for f in findings if VAGUE.match((f.get("verbatim") or "").strip())]
    real = [f.get("finding_id") for f in findings if (f.get("verbatim") or "").lstrip().startswith("REAL:")]
    finding_info = {"total": len(findings), "with_verbatim": sum(1 for f in findings if (f.get("verbatim") or "").strip()),
                    "vague_only": vague, "real": real}
    for v in vague:
        flag("vague_line", BLOCK, f"criterion 3: {v} is only a vague word")
    if findings and not real:
        flag("no_real_finding", JUDGMENT, "criterion 4: no finding begins REAL:; flag to David")

    # criterion 5
    ranking: dict[str, Any] = {"present": "ranking.md" in s.files}
    if ranking["present"]:
        entries = parse_ranking(s.files["ranking.md"].decode("utf-8", "replace"))
        ids_all = {f.get("finding_id") for f in findings}
        valid = [e for e in entries if e["ids"] and all(i in ids_all for i in e["ids"])]
        ranking.update({"entries": len(entries), "with_valid_id": f"{len(valid)}/{len(entries)}",
                        "with_fix": f"{sum(e['has_fix'] for e in entries)}/{len(entries)}",
                        "order": [e["ids"] for e in entries]})
        if len(entries) > 5:
            flag("ranking_too_long", BLOCK, f"ranking lists {len(entries)}; at most five")
        if len(entries) < min(len(findings), 5):
            flag("ranking_too_short", BLOCK, f"ranking lists {len(entries)}; the record has {len(findings)} findings")
        for e in entries:
            if not e["ids"]:
                flag("ranking_no_id", BLOCK, f"ranking entry names no finding_id: {e['text'][:80]}")
            elif not all(i in ids_all for i in e["ids"]):
                flag("ranking_unknown_id", BLOCK, f"ranking names an id not in look_findings.json: {e['ids']}")
            elif not e["has_fix"]:
                flag("ranking_no_fix", BLOCK, f"ranking entry {e['ids']} has no fix sentence or 'I cannot say'")

    # criterion 10
    notes: dict[str, Any] = {}
    if "notes.md" in s.files:
        notes = parse_notes(s.files["notes.md"].decode("utf-8", "replace"))
        if not notes["start_line"]:
            flag("no_start_line", BLOCK, "notes.md has no start line with a clock time")
        elif not notes["start_is_line_1"]:
            flag("start_not_line_1", JUDGMENT, "the start line is not the first line of notes.md")
        if not notes["end_line"]:
            flag("no_end_line", BLOCK, "notes.md has no end line with a clock time")
        if notes["same_line"]:
            flag("start_end_same_line", JUDGMENT, "start and end are on one line, not first and last lines")
        elif notes["end_line"] and not notes["end_is_last_line"]:
            flag("end_not_last_line", JUDGMENT, "the end line is not the last line of notes.md")
        if notes["prior_exposure"] == "bare_none":
            flag("prior_exposure_bare", JUDGMENT, f"line 2 reads {notes['line_2']!r}, without 'prior exposure:'")
        elif notes["prior_exposure"] == "absent":
            flag("prior_exposure_absent", BLOCK, "line 2 of notes.md is not a prior-exposure statement")
        if notes["minutes"] is not None and notes["minutes"] < 15:
            flag("short_look", BLOCK, f"the look lasted {notes['minutes']} minutes by notes.md")
        if notes["minutes"] is None and notes["start_line"] and notes["end_line"]:
            flag("minutes_not_computed", JUDGMENT, "start and end are on different dates or one line; "
                 "minutes not computed")

    # criteria 2, 8, 9 and the hours lines, from the task-state file
    validators = parse_validators(s.worklog or "")
    checker = parse_checker(s.worklog or "", s.login)
    hours = [l.strip() for l in (s.worklog or "").splitlines()
             if re.search(r"\b\d+\s*(min|mins|minutes|h|hr|hrs|hours)\b", l, re.I)]
    if s.worklog is not None:
        for kind, label in (("history", "validate_look_findings --history"), ("package", "validate_package")):
            st = validators[kind]
            if st == "crashed":
                flag(f"{kind}_crashed", BLOCK, f"{label} crashed (no FAIL 0 verdict): {validators[kind + '_text'][:120]}")
            elif st == "fail":
                flag(f"{kind}_fail", BLOCK, f"{label} recorded a failure")
            elif st == "absent":
                flag(f"{kind}_absent", BLOCK, f"no {label} result in the task-state file")
        if not checker["named"]:
            flag("no_checker", BLOCK, "the task-state file names no checker")
        elif checker["student_or_ai"]:
            flag("checker_is_student_or_ai", BLOCK, f"named checker {checker['named']!r} is the student or an AI")
        if not hours:
            flag("no_hours", JUDGMENT, "no minutes per stage in the task-state file (the brief's Hours line)")

    # criterion 7 (and the PR's checker line), only when the description was supplied
    seal_sha = seal_info.get("seal_commit")
    att = parse_attestation(s.pr_body, seal_sha)
    if not att["supplied"]:
        flag("pr_body_not_read", MANUAL, "PR description not supplied: criteria 7 and 9 and the pasted FAIL 0 lines")
    else:
        for key, msg in (("sentence", "the attestation sentence of criterion 7"),
                         ("date", "a date in the attestation"),
                         ("seal_hash", "the hash of the commit that holds the seal")):
            if not att[key]:
                flag(f"attestation_{key}", BLOCK, f"PR description lacks {msg}")
        if not att["checker_names"]:
            flag("pr_no_checker", BLOCK, "PR description names no checker from the ring")

    complete = not zero_pin and not any(f.severity == BLOCK for f in flags)
    return Result(s.login, s.head, present, missing, unexpected, identity, seal_info, pictures, finding_info,
                  ranking, notes, validators, checker, hours, att, flags, complete)


def _json(raw: bytes | None, name: str, flag) -> dict | None:
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except ValueError as exc:
        flag("bad_json", BLOCK, f"{name} does not parse: {exc}")
        return None


def _history(s: Snapshot, flag) -> dict[str, Any]:
    """Criterion 2 from git: the seal committed before any pass-2 finding, never changed after,
    and the sealed pass-1 findings never edited after it."""
    seal_at = first_p2 = None
    seal_val = p1_snap = None
    edits: list[str] = []
    for i, (sha, _date, d) in enumerate(s.history):
        if not isinstance(d, dict):
            flag("history_unparsed", BLOCK, f"look_findings.json at {sha[:8]} does not parse")
            continue
        fs = d.get("findings") or []
        sl = d.get("pass1_seal")
        snap = json.dumps(sorted([f for f in fs if f.get("pass") == 1], key=lambda f: str(f.get("finding_id"))),
                          sort_keys=True)
        if sl is not None and seal_at is None:
            seal_at, seal_val, p1_snap = i, json.dumps(sl, sort_keys=True), snap
        elif seal_at is not None and sl is None:
            flag("seal_removed", BLOCK, f"pass1_seal removed at {sha[:8]}")
        elif sl is not None and json.dumps(sl, sort_keys=True) != seal_val:
            flag("seal_changed", BLOCK, f"pass1_seal changed at {sha[:8]} after it was first committed")
        if seal_at is not None and i > seal_at and snap != p1_snap:
            edits.append(sha[:8])
        if first_p2 is None and any(f.get("pass") == 2 for f in fs):
            first_p2 = i
    out: dict[str, Any] = {"versions": len(s.history), "seal_commit": None, "first_pass2_commit": None,
                           "edits_after_seal": edits, "seal_before_pass2": None}
    if seal_at is None:
        if s.history:
            flag("seal_never_committed", BLOCK, "no committed version of look_findings.json carries a pass1_seal")
        return out
    out["seal_commit"] = s.history[seal_at][0]
    out["seal_commit_files"] = s.seal_commit_files.get(out["seal_commit"], [])
    if first_p2 is not None:
        out["first_pass2_commit"] = s.history[first_p2][0]
        out["seal_before_pass2"] = first_p2 > seal_at
        if first_p2 <= seal_at:
            flag("pass2_not_after_seal", BLOCK, f"a pass-2 finding was committed at {s.history[first_p2][0][:8]}, "
                 "not after the seal commit")
    for e in edits:
        flag("edited_after_seal", BLOCK, f"sealed pass-1 findings changed at {e}")
    return out


# --------------------------------------------------------------------------- #
# git adapter (read-only) and command line
# --------------------------------------------------------------------------- #
def _git(repo: Path, *args: str, ok_fail: bool = False) -> bytes | None:
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True)
    if r.returncode:
        if ok_fail:
            return None
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.decode('utf-8', 'replace').strip()}")
    return r.stdout


def snapshot_from_git(repo: Path, ref: str, base: str = "origin/main", pr_body: str | None = None) -> Snapshot:
    head = _git(repo, "rev-parse", ref).decode().strip()
    merge_base = _git(repo, "merge-base", head, base).decode().strip()
    paths = [p for p in _git(repo, "diff", "--name-only", merge_base, head).decode().splitlines() if p]
    folders = sorted({m.group(0) for p in paths for m in [re.match(r"students/looking_records/[^/]+/REAL-0/", p)] if m})
    if len(folders) != 1:
        raise RuntimeError(f"expected one REAL-0 record folder in {ref}, found {folders}")
    folder = folders[0]
    login = folder.split("/")[2]
    worklog_path = f"students/worklogs/{login}/REAL-0.md"
    tree = _git(repo, "ls-tree", "-r", "--name-only", head, folder).decode().splitlines()
    files = {p[len(folder):]: _git(repo, "show", f"{head}:{p}") for p in tree}
    log = _git(repo, "log", "--reverse", "--format=%H %ad", "--date=iso", f"{merge_base}..{head}", "--",
               folder + "look_findings.json").decode().splitlines()
    history, touched = [], {}
    for line in log:
        sha, date = line.split(" ", 1)
        raw = _git(repo, "show", f"{sha}:{folder}look_findings.json", ok_fail=True)
        try:
            parsed = json.loads(raw) if raw is not None else None
        except ValueError:
            parsed = None
        history.append((sha, date, parsed))
        touched[sha] = _git(repo, "show", "--format=", "--name-only", sha).decode().split()
    wl = _git(repo, "show", f"{head}:{worklog_path}", ok_fail=True)
    return Snapshot(login=login, head=head, files=files, history=history, seal_commit_files=touched,
                    worklog=wl.decode("utf-8", "replace") if wl is not None else None, pr_body=pr_body,
                    outside_paths=[p for p in paths if not p.startswith(folder) and p != worklog_path])


def render(r: Result) -> str:
    seal = r.seal
    lines = [
        f"REAL-0 record check   login {r.login}   head {r.head}",
        f"  required files present: {len(r.files_present)}/{len(REQUIRED_FILES)}"
        + (f"   missing {r.files_missing}" if r.files_missing else ""),
        f"  identity: student {r.identity.get('student')!r}, task_id {r.identity.get('task_id')!r}, "
        f"room {r.identity.get('room_ok')}",
        f"  seal: present {seal['present']}, sealed pass-1 pins {seal['sealed_pins']} (floor 5), "
        f"nothing_noticed {seal['nothing_noticed']}, findings pass1 {seal['pass1']} pass2 {seal['pass2']}",
        f"  seal history: {seal['versions']} committed versions; seal at {str(seal['seal_commit'])[:8]}; "
        f"first pass 2 at {str(seal['first_pass2_commit'])[:8]}; seal before pass 2: {seal['seal_before_pass2']}; "
        f"edits after seal: {len(seal['edits_after_seal'])}",
        f"  pictures: pins with picture {r.pictures['pins_with_picture']}, pictures with pin "
        f"{r.pictures['pictures_with_pin']}",
        f"  findings: {r.findings['total']}, REAL: {len(r.findings['real'])}/{r.findings['total']} "
        f"{r.findings['real']}, vague-only {len(r.findings['vague_only'])}/{r.findings['total']}",
        f"  ranking: entries {r.ranking.get('entries')}, with valid id {r.ranking.get('with_valid_id')}, "
        f"with fix {r.ranking.get('with_fix')}",
        f"  notes.md: start {r.notes.get('start_line')!r}; end {r.notes.get('end_line')!r}; "
        f"line 2 {r.notes.get('line_2')!r}; minutes {r.notes.get('minutes')}",
        f"  validators (task-state file): history {r.validators['history']}, package {r.validators['package']}",
        f"  checker named: {r.checker['named']!r}",
        f"  hours lines: {len(r.hours_lines)}",
        f"  attestation: {'not supplied' if not r.attestation['supplied'] else r.attestation}",
        f"FLAGS {len(r.flags)}  (block {sum(f.severity == BLOCK for f in r.flags)}, "
        f"judgment {sum(f.severity == JUDGMENT for f in r.flags)}, manual {sum(f.severity == MANUAL for f in r.flags)})",
    ]
    lines += [f"  - [{f.severity}] {f.code}: {f.message}" for f in r.flags]
    lines.append(f"COMPLETE PER THE BRIEF: {'yes' if r.complete else 'no'}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Read-only REAL-0 record checker.")
    ap.add_argument("--repo", required=True, type=Path, help="a New_VR_Platform clone")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--ref", help="a fetched ref or commit holding the record")
    g.add_argument("--pr", type=int, help="fetch pull/<N>/head into FETCH_HEAD first")
    ap.add_argument("--base", default="origin/main")
    ap.add_argument("--body", type=Path, help="the pull request's description, pasted into a file")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    ref = a.ref
    if a.pr is not None:
        _git(a.repo, "fetch", "-q", "origin", f"pull/{a.pr}/head")
        ref = "FETCH_HEAD"
    body = a.body.read_text(encoding="utf-8") if a.body else None
    result = check(snapshot_from_git(a.repo, ref, a.base, body))
    print(json.dumps(result.to_dict(), indent=2) if a.json else render(result))
    return 0 if result.complete else 1


if __name__ == "__main__":
    sys.exit(main())
