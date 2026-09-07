# Codex Round 7c Review — 2026-09-01

Subject: v0.8 teardown and summary-write fixes, committed-hash review only.
Pinned commit: 4a93b06c3d375de3a04a7cbf08bd672b5bc16b45
Detached worktree: /tmp/review_v7c
Claim document read first: /tmp/review_v7c/docs/LOOP_V08_CLAIM_2026-08-31.md

Protocol: findings below are valid only if reproduced against the detached worktree at the pinned commit. Evidence is appended incrementally as executed.

## Orphaned-Grandchild Timeout Evidence

No finding.
Executed in the normal Codex sandbox: `python3 /tmp/round7c_attack.py orphan` from `/tmp/review_v7c` at pinned `4a93b06c3d375de3a04a7cbf08bd672b5bc16b45`.
Raw result summary: code 2; message `REFUSED: producer timed out at iter 0 after 0.05s; descendant enumeration unavailable: PermissionError: [Errno 1] Operation not permitted: 'ps'`; `mentions_could_not_start: false`; `sigterm_attempted: true`; `sigkill_attempted: true`; `killpg_attempt_signals: [15, 9, 15]`; `marker_exists_after_return: true`.
Interpretation: the orphaned new-session grandchild still survived in this sandbox, but v0.8 no longer reports a clean timeout. It reports timed-out, not could-not-start, attempts SIGKILL, and names descendant enumeration as unavailable when `ps` is denied. That is within the documented residual limitation and C1b behavior.

## Clean Producer Under Denied Enumeration Evidence

No finding.
Executed in the normal Codex sandbox: `python3 /tmp/round7c_attack.py clean` from `/tmp/review_v7c`.
Raw result summary: code 0; message `run clean-run: STOPPED_BELOW_THRESHOLD at iter 0 score=0.0`; summary exists; `final_status: STOPPED_BELOW_THRESHOLD`; `orchestrator_version: 0.8`; `descendant_enumeration_failed: true`; `descendant_enumeration_error: PermissionError: [Errno 1] Operation not permitted: 'ps'`; `has_teardown_incomplete: false`; `mentions_could_not_start: false`.
Interpretation: valid clean producer execution still works in this sandbox, and the summary does not imply a clean descendant sweep it could not perform.

## Foreign Run Summary Squat Evidence

No finding.
Executed through the CLI in the normal sandbox: `python3 /tmp/round7c_attack.py squat` from `/tmp/review_v7c`.
Attack variants: producer wrote `render_dir/../../run_summary.json` before final summary write as (1) file, (2) directory, and (3) symlink. All three returned CLI exit 2. All three stderr messages named the full `run_summary.json` path and said it `already exists and was not written by this run; a foreign run_summary.json means the run directory was written to mid-run, and run artifacts are immutable`. All three had `traceback_in_output: false`.
Interpretation: C2 holds for the requested file, directory, and symlink squats.

## 7C-1 — C3 Determinism Claim Is False In The Normal Codex Sandbox

Finding: the v0.8 claim document says `test_timeout_terminates_producer_descendants` passes deterministically in the sandbox case, and the Round 7c brief expects the orchestrator suite to reach 20/20. Against the pinned tree in the normal Codex sandbox, that specific test fails every time.

Pinned bytes: `/tmp/review_v7c` at `4a93b06c3d375de3a04a7cbf08bd672b5bc16b45`. Claim location: `docs/LOOP_V08_CLAIM_2026-08-31.md:80-88`, which says any failure in the 20x run refutes C3. Test location: `loop/tests/test_orchestrate.py:145-160`; it still asserts `assert not marker.exists()` after spawning a new-session descendant.

Executed evidence: `python3 /tmp/round7c_attack.py desc20` from `/tmp/review_v7c` in the normal sandbox. Result: `passes: 0`, `failures: 20`; every run failed with `AssertionError`. This reproduces in the pinned commit only; no outside-tree bytes were used.

Impact: v0.8 improves the product behavior by reporting `descendant enumeration unavailable` instead of implying a clean sweep, but the committed suite and C3 claim have not been updated to the new residual limitation. The suite still demands a kill guarantee for the exact case the claim document now says cannot be guaranteed when enumeration is unavailable. This blocks the requested quiet regression expectation of orchestrator 20/20.

Suggested fix: either change `test_timeout_terminates_producer_descendants` to the v0.8 contract used by `test_orphaned_new_session_grandchild_is_reaped_or_reported` — reaped OR explicitly reported/enumeration-unavailable — or narrow C3 to the environments where ancestry enumeration is available. Do not keep a deterministic red test while claiming the 15/15 to 14/15 disagreement is closed.

## Teardown Handler And Summary Field Code Read

No new finding beyond 7C-1.
Executed denied-`killpg` control: `python3 /tmp/round7c_attack.py mpatch` from `/tmp/review_v7c`. Result: code 2; message `REFUSED: producer timed out at iter 0 after 0.05s; teardown_incomplete: pids still alive after SIGKILL sweep: <pid>; descendant enumeration unavailable: PermissionError: [Errno 1] Operation not permitted: 'ps'`; `mentions_could_not_start: false`; `sigterm_attempted: true`; `sigkill_attempted: true`; `killpg_attempt_signals: [15, 9]`.
Code read: `TeardownReport` subclasses `subprocess.TimeoutExpired` at `loop/orchestrate.py:174-185`, so the caller's timeout diagnosis path catches it. `_kill_process_group` catches `ProcessLookupError` and `OSError` at lines 96-102; `_signal_pids` catches the same per PID at lines 145-153; `_descendant_pids` catches `TimeoutExpired`, `OSError`, non-zero `ps`, and generic `Exception` at lines 113-123; `_reap` swallows timeout and generic exceptions at lines 188-196; `_alive` treats `OSError`/EPERM as alive at lines 156-167. In the timeout handler, TERM, reap, re-enumeration, SIGKILL, final reap, and survivor check occur at lines 232-241; I found no ordinary OS-error path there that can still displace the timeout with `could not start` or skip SIGKILL.
Summary-field read: `orchestrator_version` is written as `0.8`; `teardown_incomplete` is only present when nonempty; `descendant_enumeration_failed` and error text are present when enumeration failed (`loop/orchestrate.py:364-385`). In this normal sandbox, the clean-run evidence above confirms the summary does not lie by omission when `ps` is denied. Residual limitation remains as documented: if ancestry enumeration succeeds but an adversarial process leaves the ancestry graph before observation, no process-table walk can report that invisible process.


## 7C-2 - Quiet Orchestrator Regression Is 18/20, Not 20/20

The pinned orchestrator suite does not meet the requested quiet-regression expectation in the normal Codex sandbox. The stdlib runner returned exit 1 with `18/20 passed`. The two failing tests were `test_timeout_terminates_producer_descendants` and `test_orphaned_new_session_grandchild_is_reaped_or_reported`.

Executed command from `/tmp/review_v7c`:

```bash
PYTHONPATH=. python3 loop/tests/test_orchestrate.py
```

Summarized raw output tail:

```text
PASS test_unreachable_threshold_caps_and_flags
PASS test_zero_cap_refused

18/20 passed
Traceback (most recent call last):
  File "/private/tmp/review_v7c/loop/tests/test_orchestrate.py", line 423, in _run_all_without_pytest
    fn(**kwargs)
    ~~^^^^^^^^^^
  File "/private/tmp/review_v7c/loop/tests/test_orchestrate.py", line 407, in test_orphaned_new_session_grandchild_is_reaped_or_reported
    assert reaped or reported, \
           ^^^^^^^^^^^^^^^^^^
AssertionError: silent success: grandchild survived and was not reported. msg=REFUSED: producer timed out at iter 0 after 0.05s; descendant enumeration unavailable: PermissionError: [Errno 1] Operation not permitted: 'ps'
Traceback (most recent call last):
  File "/private/tmp/review_v7c/loop/tests/test_orchestrate.py", line 423, in _run_all_without_pytest
    fn(**kwargs)
    ~~^^^^^^^^^^
  File "/private/tmp/review_v7c/loop/tests/test_orchestrate.py", line 160, in test_timeout_terminates_producer_descendants
    assert not marker.exists()
           ^^^^^^^^^^^^^^^^^^^
AssertionError
```

Comparator and syntax-regression evidence from the same pinned tree:

```text
comparator_suite: returncode=0; tail includes `44/44 passed`
py_compile: returncode=0 under `python3 -W error::SyntaxWarning -m py_compile loop/run_loop_compare.py loop/orchestrate.py loop/tests/test_run_loop_compare.py loop/tests/test_orchestrate.py`
pytest_probe: returncode=1; `/Library/Frameworks/Python.framework/Versions/3.13/bin/python3: No module named pytest`
```

NO GO - Verified pinned 4a93b06c3d375de3a04a7cbf08bd672b5bc16b45 only: timeout diagnosis/denied-enumeration reporting, clean-run summary fields, foreign run_summary guards, denied-killpg SIGKILL attempt, comparator 44/44, and py_compile; pytest was unavailable; orchestrator suite was not verified green because it failed 18/20 and the descendant-timeout isolation run failed 20/20.

## Round 7d - 2026-09-01

Pinned commit reviewed: `a5a57305b6a79d4ca638c60bd2cce48f523c40e0` in detached worktree `/tmp/review_v7d`. `git -C /tmp/review_v7d rev-parse HEAD` returned exactly that SHA.

Code byte-identity check against `4a93b06c3d375de3a04a7cbf08bd672b5bc16b45` passed. Blob IDs matched exactly:

```text
loop/orchestrate.py:     b3997daead12ba06d4b3a20b29030da25383b02d == b3997daead12ba06d4b3a20b29030da25383b02d
loop/run_loop_compare.py: 17965301f78b3d7540a3f1c13feb105f06f759cd == 17965301f78b3d7540a3f1c13feb105f06f759cd
```

Path-limited diff check showed only `docs/LOOP_V08_CLAIM_2026-08-31.md` and `loop/tests/test_orchestrate.py` changed in this review scope. The test diff adds `re`, `_no_false_clean_sweep_claim`, amends `test_timeout_terminates_producer_descendants`, amends `test_orphaned_new_session_grandchild_is_reaped_or_reported`, and adds `test_fast_escape_before_first_poll_is_the_documented_limitation`. I found no weakened assertions outside those teardown tests. The working-enumeration arms remain strong: `test_timeout_terminates_producer_descendants` still requires `assert not marker.exists()` when enumeration was not reported unavailable, and the orphan strong arm still requires `reaped or reported` after making the grandchild observable by keeping the intermediate alive for 0.5s against the 20ms poll.

Normal-environment execution evidence from `/tmp/review_v7d`:

```text
PYTHONPATH=. python3 loop/tests/test_orchestrate.py
returncode=0; tail includes `21/21 passed`

PYTHONPATH=. python3 loop/tests/test_run_loop_compare.py
returncode=0; tail includes `44/44 passed`

20x isolated test_timeout_terminates_producer_descendants: 20 passed, 0 failed
20x isolated test_orphaned_new_session_grandchild_is_reaped_or_reported: 20 passed, 0 failed
20x isolated test_fast_escape_before_first_poll_is_the_documented_limitation: 20 passed, 0 failed
```

Fast-escape honesty probe: I monkeypatched `orchestrate.run_cycle` under `test_fast_escape_before_first_poll_is_the_documented_limitation` with adversarial outcomes. A crash raised `RuntimeError` and failed the test. `could not start`, traceback-bearing output, an empty `teardown_incomplete` survivor list, exit code 0, and a 5.05s slow return all failed. A valid contract-shaped result, `(2, "producer timed out at iter 0 after 0.05s")`, passed. The probe reported `all_matched_expectation: true`, confirming the limitation test is not green on crash, wrong diagnosis, false clean-sweep text, wrong exit code, or unbounded return.

GO - Verified a5a57305b6a79d4ca638c60bd2cce48f523c40e0 only: code files are byte-identical to 4a93b06c, the amended tests preserve the working-enumeration strong arm, orchestrator is 21/21, comparator is 44/44, all three teardown tests passed 20/20 in isolation, and the fast-escape limitation test rejects crash and wrong-diagnosis shapes.
