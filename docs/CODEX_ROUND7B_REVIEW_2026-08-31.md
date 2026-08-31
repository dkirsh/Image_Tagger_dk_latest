# Codex Round 7b Review — 2026-08-31

Subject: post-merge tree, committed-hash review only.
Pinned commit: 5fb46e39a25fa3d68b55d6578d2795f3e1d0e779
Detached worktree: /tmp/review_v7b

Protocol: findings below are valid only if reproduced against the detached worktree at the pinned commit. Evidence is appended incrementally as executed.

## Threshold Refusal Evidence

No finding.
Executed: `python3 /tmp/round7b_attack.py threshold` from `/tmp/review_v7b` at pinned `5fb46e39a25fa3d68b55d6578d2795f3e1d0e779`.
Results: comparator direct and CLI refused `1.0000001`, `NaN`, and `inf` with rc/code 2 and `REFUSED: threshold must be a finite number in [0,1]`. Direct comparator refused threshold as Python string `0.5` with code 2. Comparator CLI accepted literal `0.5` because argparse converts it to float.
Pre-ingestion check: comparator CLI with missing target/packet plus `--threshold NaN` returned rc 2 threshold refusal and created no output directory, proving threshold validation precedes input reads.
Orchestrator direct and CLI refused `1.0000001`, `NaN`, and `inf` before producer marker files were created. Direct orchestrator refused Python string `0.5` with code 2. CLI accepted `-0.0`/`0.5` as finite floats, then ran the producer path; `-0.0` stopped below threshold in the valid direct route.

## Run Directory Freshness Evidence

No finding.
Executed: `python3 /tmp/round7b_attack.py rundir` from `/tmp/review_v7b`.
Results: `existing_dir`, `existing_dir_trailing_slash`, `symlink_to_existing_dir`, `dangling_symlink`, and `existing_file` all returned code 2 with `REFUSED: run directory ... already exists; run artifacts are immutable and may not reuse stale packets`.
Freshness control: first run into `fresh_once` returned code 0 `STOPPED_BELOW_THRESHOLD`; a second run using the same directory returned code 2 already-exists refusal.
Race control: a patched `Path.mkdir` made the run directory appear exactly at the `run_dir.mkdir()` call; result was code 2 already-exists refusal and the producer marker stayed absent. This confirms the effective protection is the atomic create, not a stale pre-check.

## 7B-1 — Timeout Teardown Misses Orphaned New-Session Grandchildren

Finding: the orchestrator bounds the producer call and kills the producer process group plus descendants visible at timeout, but it does not reliably tear down a grandchild that enters a new session and whose intermediate parent exits before timeout. That process can continue after `run_cycle` has returned `REFUSED: producer timed out`.

Pinned bytes: `/tmp/review_v7b/loop/orchestrate.py` at `5fb46e39a25fa3d68b55d6578d2795f3e1d0e779`. Relevant code: `_run_producer` starts the producer with `start_new_session=True` at lines 112-116, snapshots descendants once at timeout at line 120, sends TERM/KILL to that fixed descendant set plus the root process group at lines 121-129, and never re-enumerates escaped/reparented descendants.

Executed evidence: `python3 /tmp/round7b_attack.py timeout` from `/tmp/review_v7b`. Invalid timeout controls held: timeout `0`, `-1`, `NaN`, and `inf` all returned code 2 `REFUSED: producer timeout must be a positive finite number` with producer markers absent. SIGTERM-resistant parent control held: `ignore_sigterm_parent` returned code 2 timeout and marker absent, showing SIGKILL cleanup handles the root process group. Attack case failed: `orphaned_grandchild_new_session` returned code 2 timeout but `marker_exists: true`; the orphaned grandchild wrote `orphan-grandchild-survived` after the orchestrator returned.

Impact: the timeout is bounded for the main producer, but the repair claim is too broad if it promises descendant-PID teardown for adversarial producers. A malicious or buggy producer can leave post-timeout side effects outside the run directory, including later filesystem writes, even though the orchestrator reports refusal.

Suggested fix: track child creation with a stronger containment boundary than a one-time PPID snapshot, for example launch the producer in a disposable process sandbox/job object equivalent, or repeatedly enumerate descendants during TERM/KILL and treat any child that called `setsid`/reparented before timeout as out of contract unless OS-level containment can kill it. If the intended guarantee is only best-effort cleanup of visible descendants, downgrade the claim and test name accordingly.

## Run Summary Binding Evidence

No finding.
Executed: `python3 /tmp/round7b_attack.py summary` from `/tmp/review_v7b`.
Target-swap attack: producer rewrote the original `target.json` after the orchestrator had read and snapshotted it. The run still returned code 0, and `run_summary.json` recorded `target_sha256` `a93f6c575263d21ad1ceda442cfb209bc49bb597a32a581edce0dfd5ee97d389`, matching both the pre-swap bytes and `target.snapshot.json`, while differing from the swapped original hash `1efcf455e8fd0ce5d927d4fb3c99d4e1f322dc248e37debf03b8b8439928786e`. This verifies binding to bytes, not just `target.json` by name.
Naive-command-collision attack: two producer templates whose argv tokens collide under `"".join(shlex.split(cmd))` were run under the same basename `same-run`. They both produced summaries, and the summaries carried distinct exact-string command hashes: `284e7a732a01cd20002c4c8e734d2f3410529a794030590a2024ce06e4a30632` vs `2c9977ce4c01f9e32c13c403513dea348bb1d7b6dc0150e49a863df519722eab`.
Code basis: `/tmp/review_v7b/loop/orchestrate.py` hashes the read target bytes at line 165, writes an immutable snapshot at lines 175-180, gives the snapshot path to the producer at lines 190-192, writes `target_sha256` and `producer_cmd_sha256` into the summary at lines 230-235, and HITL re-verifies the snapshot hash at lines 286-291.

### 7B-1 Addendum — CLI Timeout Controls

Additional executed evidence: CLI route `python3 /tmp/review_v7b/loop/orchestrate.py run ... --producer-timeout-seconds 0` and `--producer-timeout-seconds -1` both returned rc 2 `REFUSED: producer timeout must be a positive finite number`, with marker files absent. The CLI flag in the pinned code is `--producer-timeout-seconds` (`loop/orchestrate.py` line 353), not the prompt shorthand `--producer-timeout`. Search also found `docs/CODEX_SOURCE_BLIND_RUTHLESS_REVIEW_2026-08-24.md` claiming timeout cleanup covers a new-session descendant; 7B-1 is therefore a live claim-vs-behavior defect for the post-merge tree.

## Regression Pass Evidence

Comparator suite: `PYTHONPATH=. python3 loop/tests/test_run_loop_compare.py` from `/tmp/review_v7b` passed `44/44`.
Orchestrator suite: `PYTHONPATH=. python3 loop/tests/test_orchestrate.py` from `/tmp/review_v7b` failed `14/15`. The failing test was `test_timeout_terminates_producer_descendants`, assertion `assert not marker.exists()` at `loop/tests/test_orchestrate.py:159`. This is the same failure class as 7B-1.
Stability check: reran `test_timeout_terminates_producer_descendants` alone five times from the pinned tree; it failed 5/5 with the same marker-exists assertion.
Syntax pass: `PYTHONPATH=. python3 -W error::SyntaxWarning -m py_compile loop/run_loop_compare.py loop/orchestrate.py loop/tests/test_run_loop_compare.py loop/tests/test_orchestrate.py` passed rc 0.
Pytest note: `python3 -m pytest --version` returned `No module named pytest`, so the regression counts above come from the test files built-in stdlib runners, not pytest.

NO GO — verified against pinned commit 5fb46e39a25fa3d68b55d6578d2795f3e1d0e779 that threshold refusal, run-directory freshness, target hash binding, command hash binding, comparator 44/44, and py_compile hold; not verified as releasable because producer timeout descendant teardown fails for orphaned new-session grandchildren and the orchestrator regression suite is 14/15, not expected 15/15.
Record: pytest was unavailable in the Codex environment, so the stdlib runners were the executed harness; comparator was 44/44, orchestrator was 14/15, and the descendant-timeout failure was stable across 5 isolated reruns.
