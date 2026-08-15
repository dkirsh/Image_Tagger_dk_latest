# Tanishq — Sprint Set (photo→VR production loop · POE shakedown · deploy plumbing)

*The engine-and-deploy lane, written so the AI executing it needs nothing this document does not carry: absolute paths, exact acceptance tests, and named failure states. His **biggest task** is the photo→VR production loop (Sprint 1, pending David's directory decomposition); his **secondary** work is the debug-POE shakedown and the deploy/serving plumbing. It extends — it does not replace — the software sprints Tanishq already holds (`docs/TANISHQ_ONBOARDING_AND_SPRINTS_2026-07-21.md` Sprints A–G; `docs/TANISHQ_SPRINT_CARDS_2026-07-23.md`). **No procurement / buy-list is in scope (David, 2026-08-14).***

- `STATE_AS_OF: 2026-08-15` (refreshed to current scope) · `STALE_AFTER: 30 commits / scope edits`
- **Lane:** Tanishq owns **`Image_Tagger_dk_latest`** and **`Post_Occupancy_Evals`** (plus, for the loop, shared subtrees governed by **path-level lanes**). He does **not** commit into `Knowledge_Atlas` or (except through an agreed path-level split) `New_VR_Platform` — Stephan's — nor any Article_Eater repo (Codex's). Branch prefix `tanishq/<topic>`. [verified — `LANE_MAP_2026-08-14.md`; `lanes.json`]
- *Provenance: **[verified]** read this session · **[proposed]** intended artifact not yet built · **[stated — DK]** David's recorded intent · **[BLOCKED — DK decision]** waits on a David decision named in the build prompt §9.*

---

> **PRIORITIES (David, 2026-08-14): (1) BIGGEST — the photo→VR production loop** (Sprint 1: image → VR first cut → aligned render → Image_Tagger scene-graph/wall-layout comparison → cycle → HITL). **(2) Secondary** — the debug-POE shakedown (Sprint 2; existing instruments, no buy-list) and the deploy/serve plumbing (Sprint 3). **Lane:** Tanishq owns `Image_Tagger_dk_latest` + `Post_Occupancy_Evals` + the `production_loop/` subtree of `New_VR_Platform` (path-lane); decomposition + render↔verdict interface in `_control/METHODOLOGY/LANE_MAP_2026-08-14.md`.

## Sprint 0 — Q0 pre-flight (nothing below starts until all three tasks pass)

> ## ⛔ SPRINT PRE-FLIGHT GATE (MANDATORY — Method-Enforcement Controller)
> **No task in this sprint starts until the Method-Enforcement Controller is installed and its self-tests
> pass on the machine and AI you are using.** Hard gate, not a recommendation. Install + verify per
> `/Users/davidusa/REPOS/_control/METHODOLOGY/METHOD_ENFORCEMENT_CONTROLLER_HANDOFF_2026-08-14.md` (§6 is
> your section). Acceptance: `dogged_stop_hook.py --selftest` and `headless_first_guard.py --selftest` both
> pass; a `Read` with a bare `limit` is blocked; a "TODO"-with-no-owner turn is blocked once. Record the
> pass in the sprint ledger before task 1.

### Task 0 — Install and verify the Method-Enforcement Controller
- **Repo/lane:** machine-level setup; no repo commit required.
- **Last-mile Success:** the hook block (handoff §6/§4) is merged into `~/.claude/settings.json`; the client is restarted so the watcher activates; the pass is the first row of the sprint ledger. On Tanishq's own hardware, re-point every absolute path and rely on Monitor as the durable channel.
- **Validation:** `python3 /Users/davidusa/REPOS/_control/hooks/dogged_stop_hook.py --selftest` and `.../headless_first_guard.py --selftest` both print all-controls-pass; a bare-`limit` `Read` is blocked; an ownerless-"TODO" turn is blocked once.
- **Failure states:** `wired_but_not_activated` (client not restarted); `paths_point_at_daves_mac` (Option B copied without re-pointing); `selftest_skipped`.
- **Checker ≠ author:** David (or the machine-handoff owner) confirms both self-tests and one live block against the actual `~/.claude/settings.json`.
- **One-example-first / Depends-on:** this is the gate; nothing precedes it.

### Task 0.1 — Declare the lane and install the lane-guard
- **Last-mile Success:** `echo tanishq > ~/.fleet_lane`; the pre-commit lane-guard is installed on `Image_Tagger_dk_latest` and `Post_Occupancy_Evals`, refusing a commit into a repo (or, once path-level lanes exist, a subtree) his lane does not own.
- **Validation:** `python3 /Users/davidusa/REPOS/_control/hooks/lane_guard.py --selftest` prints all-controls-pass; after declaring, a trial commit in his repos is accepted and a trial commit into a Stephan-owned repo is refused. [install via `_control/hooks/install_lane_guard.sh`]
- **Failure states:** `lane_undeclared`; `declared_wrong_lane` (deliberate, recorded, not accidental).
- **Checker ≠ author:** David confirms the self-test and one refused cross-lane commit.
- **One-example-first:** install on `Image_Tagger_dk_latest` first, confirm accept/refuse, then `Post_Occupancy_Evals`.

### Task 0.2 — Load the Kirsh Method and hold the problem-solving heuristics
- **Last-mile Success:** Tanishq's AI has read `METHOD_CARD_v0.1_2026-08-13.md` and can restate the moves that shape every task: **Think → Plan → Test → Replan → Implement**; **prove-the-negative**; **checker ≠ author**; **adversarial testing**; **FSM contracts + a control plane**; **provenance / DB meta-awareness**.
- **Validation:** a ledger row confirming the restatement, and that Sprint-1 planning carries a claim + refutation + a negative control before any build. (Checklist is the fallback; the gate is that the tasks are visibly shaped by the moves.)
- **Failure states:** `card_unread`; `ritual_restatement`.
- **Checker ≠ author:** David confirms the restatement and that the first real task carries a claim+refutation+negative-control.
- **One-example-first:** demonstrate the moves on the first Sprint-1 task.

*Record all three Q0 passes as START rows in `_control/SHARED_SPRINT_AND_ARTIFACT_LEDGER.md` before Task 1.*

---

## Sprint 1 — BIGGEST: the photo→VR production loop  **[BLOCKED — DK decision: directory decomposition]**

**The loop.** A user picks an image → VR takes a first cut (an editable room) → renders an aligned 2D view of that 3D space → Image_Tagger compares the render's scene graph + wall-layout inference against the target image → the difference drives another cycle → a HITL step lets the user accept or say what is wrong. It spans `New_VR_Platform` (VR generation, Stephan's) and `Image_Tagger_dk_latest` (scene-graph/wall-layout comparison, Tanishq's), meeting at a **render↔verdict interface**. [scope — build prompt; `LANE_MAP` path-level-lanes section]

**Why it is BLOCKED, and what is STARTABLE anyway.** The build cannot begin until David decomposes the loop into directories and assigns them (open decision §9): under the LANE_MAP's proposal, Tanishq owns cycle orchestration + the scene-graph/wall-layout comparison + the HITL surface; Stephan owns VR generation (photo→editable room + the aligned render); path-level lanes in `lanes.json` then keep them from colliding in a shared repo. Until those directories exist and are assigned, no cross-repo loop code may be committed (the lane-guard is repo-level today). **Do not guess the decomposition — flag it and do the design that makes the decision cheap.**

### T1.1 — STARTABLE now: decompose the loop and propose the directory split + interface  **(design; unblocks the rest)**
- **Repo/lane:** `Image_Tagger_dk_latest/docs/` (a proposal doc in Tanishq's lane; it does not commit code into either shared subtree).
- **Last-mile Success:** a proposal at `Image_Tagger_dk_latest/docs/PHOTO_VR_LOOP_DECOMPOSITION_2026-08-15.md` **[proposed]** that (a) lists the loop's components as concrete modules/directories, (b) assigns each to a lane (Tanishq: orchestration, scene-graph/wall-layout comparison, HITL; Stephan: VR generation + aligned render), (c) specifies the **render↔verdict interface** (what a render hands the comparator; what a verdict hands back — fields, formats, file paths), and (d) proposes the exact `lanes.json` path-level entries to enact it.
- **Validation (exits 0 iff done):** the proposal names every component with an owning lane and no unowned gap in the loop; the render↔verdict interface is specified concretely enough that a checker could stub both sides; the proposed `lanes.json` diff passes `lane_guard.py --selftest` when applied to a scratch copy (path-level mode).
- **Failure states:** `decomposition_guessed_as_decided` (proposal committed to `lanes.json` before David approves — the guard/ownership changed without the decision); `interface_underspecified` (a render↔verdict contract too vague to stub); `unowned_seam` (a loop step assigned to no lane).
- **Checker ≠ author:** **David decides** the decomposition and ownership; Stephan confirms the VR-generation boundary matches his lane. Cowork/Codex does not enact `lanes.json` until David signs.
- **One-example-first:** specify the single render↔verdict hop first and get David's read before decomposing the whole cycle.

### T1.2 — BLOCKED (needs T1.1 approved): scene-graph / wall-layout comparison on ONE image
- **Repo/lane:** `Image_Tagger_dk_latest` (Tanishq's comparison subtree, per the approved split).
- **Last-mile Success:** for one target image and one VR first-cut render, a deterministic comparison emits a structured discrepancy report (scene-graph diff + wall-layout inference diff) at a declared path, re-runnable to byte-identical canonical JSON.
- **Validation (exits 0 iff done):** a `run_loop_compare.py` **[proposed]** exits 0 only when the report exists, validates against its schema, and a second run reproduces the hash; a deliberately mismatched render (wrong wall count) makes the report show the discrepancy — it must **not** report agreement on a bad render (the negative control).
- **Failure states:** `passes_on_synthetic_only` (compared against a self-render, never a real target); `false_agreement` (a wrong render reported as matching); `nondeterministic_run`.
- **Checker ≠ author:** a different lineage (or Stephan, owning the render side) re-runs the comparison and confirms the discrepancy on the mismatched render.
- **One-example-first:** one target/render pair, one room type, before any batch.

### T1.3 — BLOCKED (needs T1.1 + T1.2): cycle orchestration + user HITL accept/reject
- **Repo/lane:** `Image_Tagger_dk_latest` (orchestration + HITL subtree).
- **Last-mile Success:** the loop cycles — render → compare → adjust → re-render — until the discrepancy falls below a stated threshold or a cap, then presents the user a HITL step to accept or mark what is wrong; the user's verdict is recorded with provenance.
- **Validation (exits 0 iff done):** the orchestrator runs the cycle to its stop condition on one image and records each iteration's discrepancy; the HITL verdict lands in an audited store; a run with an unreachable threshold stops at the cap and is **flagged**, not looped forever or falsely accepted.
- **Failure states:** `infinite_or_silent_loop` (no cap / no flag on non-convergence); `verdict_unprovenanced` (accept/reject stored without who/when/what-image); `resemblance_used_as_evidence` (a convergence score treated as calibrated truth — it is exploratory until calibrated).
- **Checker ≠ author:** David or Stephan drives one accept and one reject and confirms both are recorded correctly.
- **One-example-first:** one full accept-path and one full reject-path on a single image before generalizing.

---

## Sprint 2 — SECONDARY: the debug-POE shakedown (one instrument, one space, no procurement)

**Goal.** Shake down **one** already-available instrument in **one** space and prove it reads within tolerance of a known reference — **receipts, not assurances**; **no human subjects → no IRB**; **no buy-list** (uses on-hand/borrowable gear). [scope; `FALL_HANDOFF_PACK` Tanishq]

### T2.1 — Reuse the proven capture pipeline for logger ingestion
- **Repo/lane:** `Image_Tagger_dk_latest/poe_shakedown/` **[proposed]** (reuse the *pattern* from `emotibit_polar_data_system` — import/copy, do not commit into it).
- **Last-mile Success:** an ingestion path that ingests two co-located logger files, schema-validates, runs sync-QC (drift/overlap/jitter → 0–100 confidence + R/Y/G band), and **refuses to emit metrics in strict mode when the clocks cannot be trusted to align** — reusing the sync-QC/strict-gate/provenance design already built, not reinventing it.
- **Validation (exits 0 iff done):** on two co-located logs it emits a sync-QC report; on a deliberately mis-clocked pair the strict gate refuses to export (gate is live, not cosmetic); a provenance record (model, serial, firmware, calibration state, window) is attached.
- **Failure states:** `reinvented_the_pipeline`; `strict_gate_is_cosmetic`; `provenance_missing`; `passes_on_synthetic_only`.
- **Checker ≠ author:** David or Stephan re-runs sync-QC from the raw logs and confirms the report and the strict-gate refusal.
- **One-example-first / Depends-on:** one real pair of logs first; an already-available logger + the emotibit pattern (on disk).

### T2.2 — Calibrate the one instrument against a reference; produce the receipt
- **Repo/lane:** `Image_Tagger_dk_latest/poe_shakedown/`.
- **Last-mile Success:** a receipt `RECEIPT_<instr>_<space>_<date>.md` **[proposed]** recording instrument (model/serial/firmware), the reference checked against, the co-located window, the agreement stats (bias + limits of agreement, Bland–Altman), and pass/fail against a **stated tolerance** (e.g. Aranet4 ±(30 ppm + 3% of reading)). Raw high-frequency logs gitignored; summary + stats in-repo; no participant data.
- **Validation (exits 0 iff done):** the receipt states a numeric tolerance and shows measured agreement inside it (or honestly outside → flagged, not trusted); the referenced raw log exists and the agreement statistic recomputes from it.
- **Failure states:** `number_not_calibration` (reading trusted with no reference); `tolerance_unstated`; `reference_weaker_than_instrument`; `receipt_not_reproducible`.
- **Checker ≠ author:** David or Stephan recomputes bias + limits of agreement from the referenced log and confirms the verdict.
- **One-example-first:** this IS the one example gating any multi-instrument/space sweep.

---

## Sprint 3 — SECONDARY: deploy / serving plumbing (incl. the KA review-page handoff)

**Goal.** Stand up the deploy/data-serving plumbing the fall demo needs, and define the **cross-lane serve contract** so the split does not strand the hosted KA adjudication surface: **Stephan owns the KA "Feature Review" page** (in `Knowledge_Atlas`); **Tanishq owns hosting/serving/piping data to it — without committing into `Knowledge_Atlas`.** [scope; `LANE_MAP`; `FALL_HANDOFF_PACK`]

### T3.1 — Define the serve contract (the interface that makes the split safe)
- **Repo/lane:** `Image_Tagger_dk_latest/docs/KA_REVIEW_SERVE_CONTRACT_2026-08-14.md` **[proposed]** (Tanishq's deploy artifacts stay in his lane).
- **Last-mile Success:** a contract stating exactly what Stephan's lane hands off (deployable bundle or run command; port; env vars; data mount — `verification_packets.py` output + the migration-024 annotations store) and what Tanishq provides (host, reverse proxy, TLS, DNS, uptime, the data-sync job). Hosted, JWT-protected.
- **Validation (exits 0 iff done):** the contract names the artifact + exact interface (port/env/data path) with no gap requiring Tanishq to edit KA source; a dry-run against a **sample** packet directory serves the page and it reads the sample. (Live data BLOCKED on Codex 1a — build against the sample, don't wait.)
- **Failure states:** `lane_crossed` (Tanishq edits `Knowledge_Atlas` to deploy — the guard blocks it); `contract_implicit` (works only via an undocumented port/env); `secret_in_public_repo`.
- **Checker ≠ author:** Stephan confirms the contract matches what his lane produces; a second reader confirms no Image_Tagger commit touches KA source and no secret is committed.
- **One-example-first:** serve one sample packet end-to-end before wiring the live data-sync.

### T3.2 — Stand up the deployment for the deployable tagger read
- **Repo/lane:** `Image_Tagger_dk_latest`.
- **Last-mile Success:** a reproducible deployment (documented run command + env) that serves the packaged tagger read of one real render into attribute fields, hosted and reachable — the serving half of the fall demo. (The *science* of the read is the software/agent lane's job; this task serves it.)
- **Validation (exits 0 iff done):** a clean-environment run of the documented command brings the service up and returns the fields for one known render; `node_modules`/venvs/caches/>100 MB are gitignored and absent from commits.
- **Failure states:** `works_on_my_machine`; `repo_bloated`; `calibration_overclaimed` (serving an uncalibrated perceptual field as evidence — every reading carries its maturity rung).
- **Checker ≠ author:** a different lineage or David runs the documented command from a clean checkout and confirms the service + fields.
- **One-example-first / Depends-on:** one render, verified, before batch; the packaged tagger read from the software/agent lane (item B).

---

## Sequence, guardrails, provenance

**Sequence.** Sprint 0 (0 → 0.1 → 0.2) gates everything. **Sprint 1 (biggest) is BLOCKED on David's directory decomposition** — but **T1.1 (the decomposition proposal) is STARTABLE now** and is the thing that unblocks it; T1.2/T1.3 wait on David's sign-off. In parallel, **Sprint 3.1 (serve contract + sample dry-run) is STARTABLE now** on existing machines and is the most useful immediate non-blocked work; **Sprint 2 (shakedown)** runs whenever a suitable instrument is on hand; **Sprint 3.2** waits on the packaged tagger read. The human-subjects lane (wearables, cortisol) needs IRB and stays off this critical path.

**Guardrails.** Lane: every task names its repo; the loop's shared subtrees are governed by path-level lanes **only after David approves T1.1** — until then no cross-repo loop commit. Public-repo cautions (`Image_Tagger_dk_latest`, `Post_Occupancy_Evals` public): no secrets, no participant data, nothing >100 MB. Calibration-before-evidence: an instrument reading or a perceptual/convergence score is exploratory until calibrated against a reference. Cross-visibility: log START/DONE and shared artifacts to `_control/SHARED_SPRINT_AND_ARTIFACT_LEDGER.md`.

**Provenance.** Scope from `COWORK_BUILD_SPRINTS_STEPHAN_TANISHQ_2026-08-14.md`; task-shape/gate from `COWORK_SPRINT_SET_BUILDER_PROMPT.md`; lanes from `LANE_MAP_2026-08-14.md` + `lanes.json` + `lane_guard.py`; controller from `METHOD_ENFORCEMENT_CONTROLLER_HANDOFF_2026-08-14.md` §6; shakedown pipeline pattern from `emotibit_polar_data_system/docs/PROJECT_GUIDE_FOR_HUMANS.md`; deploy/KA-handoff from `FALL_HANDOFF_PACK_2026-08-13.md`. Extends `TANISHQ_ONBOARDING_AND_SPRINTS_2026-07-21.md` + `TANISHQ_SPRINT_CARDS_2026-07-23.md`. No task depends on a David-only, non-git file. Refreshed 2026-08-15 by cowork (Claude/Opus) to the current scope; a draft for a different-lineage certifier (Codex) or David to sign. Written under `atlas_shared/contracts/SCIENCE_COMMUNICATION_NORMS.md`.
