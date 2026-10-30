"""vr199_checks/tests/test_real0_check.py — the REAL-0 record checker.

Every fixture is constructed here; no student's record is copied. The layouts, though, are the
ones hand-ins actually used: a ranking with the id on a numbered line and "Fix:" on the next
(PR #41's layout), an unnumbered "id — <fix>" ranking (PR #42's), a numbered ranking that names no
id (PR #44's), a task-state file whose history validator crashed on Windows (PR #42's), start and
end on one line of notes.md (PR #44's), and a zero-pin seal (the staff pilot's).

Run:  python3 -m pytest vr199_checks/tests/test_real0_check.py -v
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from vr199_checks import real0_check as rc  # noqa: E402

LOGIN = "student-x"
TRIAL = "t-0123456789abcdef"
JPEG = b"\xff\xd8\xff\xe0fixture"


def fid(p: int, n: int) -> str:
    return f"{TRIAL}.p{p}-{n:02d}"


def finding(p: int, n: int, verbatim: str) -> dict:
    return {"finding_id": fid(p, n), "task_id": "REAL-0", "student": LOGIN, "room_id": rc.ROOM_ID,
            "pass": p, "verbatim": verbatim, "location": {"screenshot": f"look_{fid(p, n)}.jpg"}}


def doc(findings: list[dict], sealed: list[str] | None, nothing: bool = False) -> dict:
    d = {"schema_version": "look-finding/v1", "record_id": "rec-1", "task_id": "REAL-0", "student": LOGIN,
         "viewer_commit": "abc1234", "findings": findings}
    if sealed is not None:
        d["pass1_seal"] = {"sealed_at": "2026-10-24T01:00:00Z", "nothing_noticed": nothing,
                           "pass1_finding_ids": sealed}
    return d


P1 = [finding(1, i, f"the skirting board on the east wall stops {i} cm short of the door frame")
      for i in range(1, 6)]
P1[0]["verbatim"] = "REAL: the wood grain on the desk top runs the right way and varies along it"
P2 = [finding(2, 6, "lighting: the shadow under the sofa is missing, so it seems to float")]
SEALED = [f["finding_id"] for f in P1]

RANKING_41 = "REAL-0 Ranking\n" + "".join(
    f"{i}. {fid(1, i)}\nFix: make the board meet the frame on wall {i}.\n\n" for i in range(1, 6))
RANKING_42 = "".join(f"{fid(1, i)} — <add a shadow pass for object {i}.>\n\n" for i in range(1, 6))
RANKING_PILOT = "# REAL-0 ranking\n\nMost damaging first; each is named by its `finding_id`.\n\n" + "".join(
    f"{i}. `{fid(1, i)}` — a gap at the frame. Fix: close it.\n" for i in range(1, 6))
RANKING_NO_IDS = "".join(f"{i}. Texture {i} - use higher resolution maps on the walls\n" for i in range(1, 6))

NOTES = "Sat 24 Oct, 16:19, start\nprior exposure: none\n\npass 1 thoughts\n\nSat 24 Oct, 17:05, end\n"

WORKLOG = """# Task state: REAL-0

- Student: `student-x`
- Named checker: `Juan`

## Implementation and verification

- `python3 students/validate_look_findings.py students/looking_records/student-x/REAL-0/look_findings.json --history`: final line `FAIL 0`.
- `cd students && python3 validate_package.py && cd ..`: final line `PASS 1985  FAIL 0`.
- Setup 20 min; looking 40 min; ranking 10 min; hand-in 15 min.
"""

WORKLOG_WINDOWS_CRASH = """# Task state: REAL-0

- Named checker: `yuz292`

## Implementation and verification
1. Package validator — PASS.
   `cd students && PYTHONUTF8=1 <python> validate_package.py && cd ..`
   Last line: `PASS 1985  FAIL 0`, exit 0.
   without PYTHONUTF8 the same command reports a false `FAIL 1` on a catalogue file.

2. Look-findings validator with `--history` — BLOCKED, validator crash.
   `PYTHONUTF8=1 <python> students/validate_look_findings.py students/looking_records/x/REAL-0/look_findings.json --history`
   Last line: `TypeError: the JSON object must be str, bytes or bytearray, not NoneType`

   The record itself validates without `--history`:
   `PASS look_findings.json: 7 findings` / `FAIL 0`, exit 0. Only the ancestry walk crashes.
"""


def files_for(d: dict, ranking: str = RANKING_41, notes: str = NOTES, pictures: bool = True) -> dict[str, bytes]:
    f = {"notes.md": notes.encode(), "look_findings.json": json.dumps(d).encode(),
         "look_trial.json": json.dumps({"trials": {TRIAL: {"contract_id": rc.ROOM_ID}}}).encode(),
         "ranking.md": ranking.encode()}
    if pictures:
        for x in d["findings"]:
            f[x["location"]["screenshot"]] = JPEG
    return f


def history_ok(final: dict) -> list:
    sealed_only = doc(P1, SEALED)
    return [("a" * 40, "2026-10-24 18:00", sealed_only), ("b" * 40, "2026-10-24 18:30", final)]


def snap(**kw) -> rc.Snapshot:
    final = doc(P1 + P2, SEALED)
    base = dict(login=LOGIN, head="c" * 40, files=files_for(final), history=history_ok(final), worklog=WORKLOG)
    base.update(kw)
    return rc.Snapshot(**base)


def codes(r: rc.Result) -> set[str]:
    return {f.code for f in r.flags}


# --------------------------------------------------------------------------- #
# a complete record
# --------------------------------------------------------------------------- #
def test_complete_record_has_no_block_flags_and_reports_counts() -> None:
    r = rc.check(snap())
    assert [f for f in r.flags if f.severity == rc.BLOCK] == []
    assert codes(r) == {"pr_body_not_read"}                    # manual only: no description supplied
    assert r.complete is True
    assert r.seal["sealed_pins"] == 5 and r.seal["seal_before_pass2"] is True
    assert r.seal["seal_commit"] == "a" * 40 and r.seal["edits_after_seal"] == []
    assert r.pictures["pins_with_picture"] == "6/6"
    assert r.findings["real"] == [fid(1, 1)]
    assert r.ranking["with_valid_id"] == "5/5" and r.ranking["with_fix"] == "5/5"
    assert r.notes["minutes"] == 46 and r.notes["prior_exposure"] == "labelled"
    assert r.validators["history"] == "pass" and r.validators["package"] == "pass"
    assert r.checker["named"] == "Juan" and len(r.hours_lines) == 1


# --------------------------------------------------------------------------- #
# the two ranking layouts misread by the first shell checker, and the pilot's
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("text", [RANKING_41, RANKING_42, RANKING_PILOT], ids=["fix-next-line", "unnumbered", "pilot"])
def test_ranking_layouts_all_parse_to_five_entries_with_ids_and_fixes(text: str) -> None:
    entries = rc.parse_ranking(text)
    assert [e["ids"] for e in entries] == [[fid(1, i)] for i in range(1, 6)]
    assert all(e["has_fix"] for e in entries)


def test_ranking_id_without_fix_sentence_is_caught() -> None:
    entries = rc.parse_ranking(f"1. {fid(1, 1)}\nFix:\n2. {fid(1, 2)}\nI cannot say\n")
    assert [e["has_fix"] for e in entries] == [False, True]


def test_ranking_with_no_ids_blocks_on_every_entry() -> None:
    final = doc(P1 + P2, SEALED)
    r = rc.check(snap(files=files_for(final, ranking=RANKING_NO_IDS)))
    no_id = [f for f in r.flags if f.code == "ranking_no_id"]
    assert len(no_id) == 5 and all(f.severity == rc.BLOCK for f in no_id)
    assert r.ranking["with_valid_id"] == "0/5" and r.complete is False


def test_ranking_naming_an_unknown_id_blocks() -> None:
    final = doc(P1 + P2, SEALED)
    bad = RANKING_41.replace(fid(1, 5), f"{TRIAL}.p1-99")
    assert "ranking_unknown_id" in codes(rc.check(snap(files=files_for(final, ranking=bad))))


# --------------------------------------------------------------------------- #
# seal: zero pins, too few, history order, edits after the seal
# --------------------------------------------------------------------------- #
def test_zero_pin_seal_is_routed_to_david_never_passed() -> None:
    sealed0 = doc([], [], nothing=True)
    final = doc(P2, [], nothing=True)
    s = snap(files=files_for(final), history=[("a" * 40, "d1", sealed0), ("b" * 40, "d2", final)])
    r = rc.check(s)
    z = [f for f in r.flags if f.code == "zero_pin_seal"]
    assert len(z) == 1 and z[0].severity == rc.JUDGMENT and "David" in z[0].message
    assert "few_sealed_pins" not in codes(r)                   # not failed on count either
    assert r.complete is False                                 # and not passed
    assert r.seal["sealed_pins"] == 0 and r.seal["seal_before_pass2"] is True


def test_fewer_than_five_sealed_pins_blocks() -> None:
    final = doc(P1[:3] + P2, SEALED[:3])
    s = snap(files=files_for(final, ranking=RANKING_41.split("4.")[0]),
             history=[("a" * 40, "d1", doc(P1[:3], SEALED[:3])), ("b" * 40, "d2", final)])
    assert "few_sealed_pins" in codes(rc.check(s))


def test_pass2_in_the_seal_commit_blocks() -> None:
    final = doc(P1 + P2, SEALED)
    r = rc.check(snap(history=[("a" * 40, "d1", final)]))
    assert "pass2_not_after_seal" in codes(r) and r.seal["seal_before_pass2"] is False


def test_sealed_pass1_finding_edited_after_the_seal_blocks() -> None:
    edited = json.loads(json.dumps(P1))
    edited[2]["verbatim"] = "changed after the seal"
    final = doc(edited + P2, SEALED)
    r = rc.check(snap(files=files_for(final), history=[("a" * 40, "d1", doc(P1, SEALED)), ("b" * 40, "d2", final)]))
    assert "edited_after_seal" in codes(r) and r.seal["edits_after_seal"] == ["b" * 8]


def test_seal_changed_after_commit_blocks() -> None:
    final = doc(P1 + P2, SEALED)
    final["pass1_seal"]["sealed_at"] = "2026-10-25T00:00:00Z"
    r = rc.check(snap(files=files_for(final), history=[("a" * 40, "d1", doc(P1, SEALED)), ("b" * 40, "d2", final)]))
    assert "seal_changed" in codes(r)


# --------------------------------------------------------------------------- #
# pictures, REAL finding, vague lines
# --------------------------------------------------------------------------- #
def test_missing_picture_and_non_jpeg_block() -> None:
    final = doc(P1 + P2, SEALED)
    f = files_for(final)
    del f[f"look_{fid(2, 6)}.jpg"]
    f[f"look_{fid(1, 1)}.jpg"] = b"PNG"
    r = rc.check(snap(files=f))
    assert {"pin_without_picture", "not_jpeg"} <= codes(r)


def test_no_real_finding_is_a_judgment_for_david_and_a_designation_is_read_from_the_pr() -> None:
    plain = json.loads(json.dumps(P1))
    plain[0]["verbatim"] = "the wood grain on the desk top runs the right way"
    final = doc(plain + P2, SEALED)
    body = f"Checker: Diego\nREAL finding designated: {fid(1, 1)}\n"
    r = rc.check(snap(files=files_for(final), pr_body=body,
                      history=[("a" * 40, "d1", doc(plain, SEALED)), ("b" * 40, "d2", final)]))
    f = [x for x in r.flags if x.code == "no_real_finding"]
    assert len(f) == 1 and f[0].severity == rc.JUDGMENT
    assert r.attestation["real_designation"] == [fid(1, 1)]


def test_vague_only_line_blocks() -> None:
    vague = json.loads(json.dumps(P1))
    vague[3]["verbatim"] = "looks fake"
    final = doc(vague + P2, SEALED)
    r = rc.check(snap(files=files_for(final), history=[("a" * 40, "d1", doc(vague, SEALED)), ("b" * 40, "d2", final)]))
    assert "vague_line" in codes(r)


# --------------------------------------------------------------------------- #
# notes.md
# --------------------------------------------------------------------------- #
def test_notes_start_and_end_on_one_line_with_bare_none() -> None:
    n = rc.parse_notes("October 25, 2026 6:25 start time End time: 10/26 7:22\nNone")
    assert n["same_line"] is True and n["minutes"] is None and n["prior_exposure"] == "bare_none"
    final = doc(P1 + P2, SEALED)
    r = rc.check(snap(files=files_for(final, notes="October 25, 2026 6:25 start time End time: 10/26 7:22\nNone")))
    assert {"start_end_same_line", "prior_exposure_bare", "minutes_not_computed"} <= codes(r)
    assert all(f.severity == rc.JUDGMENT for f in r.flags
               if f.code in {"start_end_same_line", "prior_exposure_bare", "minutes_not_computed"})


def test_notes_short_look_blocks_and_label_first_layout_parses() -> None:
    n = rc.parse_notes("Start: Sat 24 Oct, 16:19\nPrior exposure: none\nEnd: Sat 24 Oct, 16:25")
    assert n["minutes"] == 6 and n["prior_exposure"] == "labelled"
    final = doc(P1 + P2, SEALED)
    assert "short_look" in codes(rc.check(snap(files=files_for(final, notes="Start: Sat 24 Oct, 16:19\n"
                                                                    "Prior exposure: none\nEnd: Sat 24 Oct, 16:25"))))


def test_notes_on_different_days_are_not_subtracted() -> None:
    n = rc.parse_notes("Fri 23 Oct, 23:50, start\nprior exposure: none\nSat 24 Oct, 00:20, end")
    assert n["minutes"] is None


# --------------------------------------------------------------------------- #
# validators, checker, hours, attestation
# --------------------------------------------------------------------------- #
def test_windows_crashed_history_line_is_crashed_not_fail0() -> None:
    v = rc.parse_validators(WORKLOG_WINDOWS_CRASH)
    assert v["history"] == "crashed"
    assert v["package"] == "pass"                              # the "false FAIL 1" aside does not count
    r = rc.check(snap(worklog=WORKLOG_WINDOWS_CRASH))
    assert "history_crashed" in codes(r) and r.complete is False


def test_both_validator_lines_on_one_paragraph_still_split() -> None:
    v = rc.parse_validators(WORKLOG)
    assert v == {"history": "pass", "package": "pass", "history_text": v["history_text"],
                 "package_text": v["package_text"]}


def test_missing_worklog_and_ai_checker_block() -> None:
    assert "missing_worklog" in codes(rc.check(snap(worklog=None)))
    ai = WORKLOG.replace("`Juan`", "Claude")
    assert "checker_is_student_or_ai" in codes(rc.check(snap(worklog=ai)))


def test_attestation_fields_read_from_the_description() -> None:
    body = (f"Checker: Juan\n\"{rc.ATTESTATION}\" Student X, 2026-10-24, seal {'a' * 7}\n"
            "history: FAIL 0 at abcdef1\npackage: PASS 1985  FAIL 0 at abcdef1\n")
    r = rc.check(snap(pr_body=body))
    assert r.attestation["sentence"] and r.attestation["date"] and r.attestation["seal_hash"]
    assert r.complete is True and codes(r) == set()
    partial = rc.check(snap(pr_body="Checker: Juan\nI did it myself.\n"))
    assert {"attestation_sentence", "attestation_date", "attestation_seal_hash"} <= codes(partial)


def test_outside_path_blocks() -> None:
    assert "outside_path" in codes(rc.check(snap(outside_paths=["students/TASK_QUEUE.md"])))


# --------------------------------------------------------------------------- #
# the git adapter, on a real throwaway repository
# --------------------------------------------------------------------------- #
def _git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True).stdout


def test_snapshot_from_git_reads_record_history_and_worklog(tmp_path: Path) -> None:
    repo = tmp_path / "nvp"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "t@example.org")
    _git(repo, "config", "user.name", "t")
    (repo / "README.md").write_text("x\n")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-q", "-m", "base")
    _git(repo, "branch", "base")
    folder = repo / "students" / "looking_records" / LOGIN / "REAL-0"
    folder.mkdir(parents=True)
    wl = repo / "students" / "worklogs" / LOGIN
    wl.mkdir(parents=True)
    final = doc(P1 + P2, SEALED)
    (folder / "look_findings.json").write_text(json.dumps(doc(P1, SEALED)))
    (folder / "look_trial.json").write_text(json.dumps({"trials": {}}))
    (folder / "notes.md").write_text(NOTES)
    _git(repo, "add", "students")
    _git(repo, "commit", "-q", "-m", "REAL-0: pass 1 sealed")
    for name, data in files_for(final).items():
        (folder / name).write_bytes(data)
    (wl / "REAL-0.md").write_text(WORKLOG)
    _git(repo, "add", "students")
    _git(repo, "commit", "-q", "-m", "REAL-0: export")
    s = rc.snapshot_from_git(repo, "main", base="base")
    assert s.login == LOGIN and len(s.history) == 2 and s.outside_paths == []
    assert sorted(s.files) == sorted(files_for(final))
    r = rc.check(s)
    assert r.seal["seal_before_pass2"] is True and r.complete is True
    assert sorted(r.seal["seal_commit_files"]) == sorted(
        f"students/looking_records/{LOGIN}/REAL-0/{n}" for n in ("look_findings.json", "look_trial.json", "notes.md"))
    assert rc.main(["--repo", str(repo), "--ref", "main", "--base", "base"]) == 0
