# Source-Blind Ruthless Review - 2026-08-24

## Freeze and method

- Subject: `main` at `1b1453bef8a38dc5a2597e45b834ece0137272d4`.
- Reviewer: a fresh headless Codex `gpt-5.6-terra` session, isolated with
  `--ignore-user-config --ephemeral`; no connectors, web, or Scite were available.
- Prior review reports, sync reports, commit messages, and conclusions were excluded until
  the independent report was complete.
- The reviewer read implementation before tests and created all hostile fixtures under
  `/tmp`. It was forbidden to edit the repository; the post-run worktree was clean.
- Scope: comparator, orchestrator/HITL, corpus database, and corpus scoring/resume.

The adversarial prompt required executable reproductions for every defect; findings without
a reproduction were to be labelled residual risks rather than defects. It expressly attacked
false agreement, identity confusion, non-finite JSON/numbers, special files, TOCTOU, stale or
concurrent runs, mutable evidence, timeout descendants, forged HITL, duplicate database rows,
partial resume, and the distinction between engineering correctness and scientific calibration.

## Independent result

The baseline focused suite passed `76/76`, and both schemas parsed. Seven hostile probes then
reproduced seven defects:

1. **P0:** a producer could mutate the target between the orchestrator's provenance hash and
   comparison, yielding an accepted run bound to the old hash.
2. **P1:** an arbitrary JSON object named `run_summary.json` could receive a HITL acceptance.
3. **P1:** producer timeout killed the direct process but left descendants alive.
4. **P1:** scoring resume treated one row for an image as proof that every attribute was complete.
5. **P1:** the corpus database admitted infinity and silently selected the last duplicate
   `(filename, attr_id)` row.
6. **P2:** direct comparator use overwrote an existing verdict artifact.
7. **P2:** a FIFO packet member blocked the comparator indefinitely.

The independent verdict was NO-GO for all five lanes. The scientific-calibration NO-GO was not
an engineering defect: the code honestly labels discrepancy values `exploratory_uncalibrated`,
and no empirical study yet establishes a scientifically defensible acceptance threshold.

## General repairs

- Comparator inputs now use descriptor-based, nonblocking, no-symlink regular-file reads.
  Output directories and `verdict.json` are create-once and cannot be overwritten.
- The orchestrator captures target bytes once, writes an exclusive snapshot, gives the producer
  that snapshot, compares the captured bytes, and refuses snapshot mutation. It also binds packet
  `run_id`, iteration, and target identity to the run.
- Producers run in a new process group. Timeout terminates the group, escalates to `SIGKILL`, and
  successful producers have residual children terminated as well.
- HITL now accepts only canonical summaries whose target snapshot and every canonical verdict
  revalidate against recorded hashes and run identities. UTC timestamps require offsets. Ledger
  rows are serialized under a file lock and form a predecessor-hash chain.
- Scoring writes a per-image completion seal: row count plus SHA-256 of the complete attribute-ID
  set. Resume skips only a self-consistent sealed image; partial and legacy rows are rescored and
  replaced atomically.
- Corpus loading rejects malformed or non-finite numeric fields and duplicate score identities;
  it no longer uses last-row-wins replacement.

These are contract-level repairs. None is conditional on a named PDF, image, or test fixture.

## Post-repair evidence

- Focused repair tests: `85/85` passed.
- Active top-level and loop suites: `100/100` passed.
- Python compilation with `SyntaxWarning` promoted to an error: passed.
- `git diff --check`: passed.
- Exact hostile probes after repair:
  - target mutation: refused, no summary emitted;
  - timeout descendant: refused, marker process did not survive;
  - comparator overwrite: second call refused, original bytes unchanged;
  - forged HITL: refused, no ledger created;
  - partial resume: image rescored, both attributes present;
  - non-finite/duplicate database input: rejected with `ValueError`;
  - FIFO member: immediate regular-file refusal.

A naive repository-wide `pytest` is not presently a meaningful gate. It enters historical
archives containing duplicate test-module names, an unconfigured nested backend, and a model
script whose checkpoint is absent; collection stopped with 34 errors before executing tests.
This is a repository-layout/test-entry-point engineering defect, not a failure of the active
100-test suite, and should be corrected by a canonical test manifest plus archive exclusion.

## Remaining boundaries

The local HITL hash chain is tamper-evident only while its latest hash is anchored externally; it
is not a cryptographic identity signature. A producer that deliberately creates a detached process
session can escape ordinary process-group containment. Most importantly, no unit test establishes
scientific calibration. Promotion beyond synthetic engineering readiness still requires frozen
real-image cases, source-blind human decisions, predeclared error metrics, and held-out validation.
