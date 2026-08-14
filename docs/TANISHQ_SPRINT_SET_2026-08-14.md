# Tanishq — Sprint Set (shakedown · deploy plumbing)

*The hardware-and-deploy lane, written so the AI executing it needs nothing this document does not carry: absolute paths, exact instrument models and quantities, and an acceptance test for every task. It extends — it does not replace — the software sprints Tanishq already holds (`docs/TANISHQ_ONBOARDING_AND_SPRINTS_2026-07-21.md` Sprints A–G, and `docs/TANISHQ_SPRINT_CARDS_2026-07-23.md`). It adds only the two things those docs do not cover: a shakedown using already-available instruments, and the deployment/serving plumbing. **No procurement or buy-list is in scope for now — per David (2026-08-14), Tanishq's work uses his machine, the lab machine, and instruments already on hand; there is no buy-list task.***

- `STATE_AS_OF: 2026-08-14`
- `JUDGED_REVIEWED: 2026-08-14`
- `STALE_AFTER_DAYS: 30`
- **Lane (repo-level, disjoint):** Tanishq owns **`Image_Tagger_dk_latest`** and **`Post_Occupancy_Evals`** only. He does **not** commit into `Knowledge_Atlas` or `New_VR_Platform` (Stephan's), nor into any Article_Eater repo (codex holds it). Branches: `tanishq/<topic>`. Enforcement: the lane-guard pre-commit hook (`/Users/davidusa/REPOS/_control/hooks/lane_guard.py`, map `/Users/davidusa/REPOS/_control/lanes.json`) — declare once with `export FLEET_LANE=tanishq` or `echo tanishq > ~/.fleet_lane`. **[verified — `LANE_MAP_2026-08-14.md`]**

*Provenance convention: **[verified]** = read out of a repository or a source document this session; **[proposed]** = an intended artifact or path that does not yet exist; **[stated — DK]** = David Kirsh's recorded intent.*

---

> ## ⛔ SPRINT PRE-FLIGHT GATE (MANDATORY — Method-Enforcement Controller)
> **No task in this sprint starts until the Method-Enforcement Controller is installed and its self-tests
> pass on the machine and AI you are using.** Hard gate, not a recommendation. Install + verify per
> `/Users/davidusa/REPOS/_control/METHODOLOGY/METHOD_ENFORCEMENT_CONTROLLER_HANDOFF_2026-08-14.md` (§6 is
> your section). Acceptance: `dogged_stop_hook.py --selftest` and `headless_first_guard.py --selftest` both
> pass; a `Read` with a bare `limit` is blocked; a "TODO"-with-no-owner turn is blocked once. Record the
> pass in the sprint ledger before task 1.

---

## Sprint 0 — Install the controller (Task 0, the gate)

Nothing below begins until this passes. It comes first because Tanishq's work is fast and hardware-facing, and two of the guards are the ones that catch the failures that lane produces: the full-read guard (do not trust a partial sensor read or a truncated log as the whole reading) and the disclosure-not-remedy stop hook (a shakedown that "mostly works, TODO the rest" is not a finished shakedown). **[verified — handoff §6]**

**Task 0 — Install and verify the Method-Enforcement Controller.**
- **Repo / lane:** machine-level setup; no repo commit required.
- **Last-mile Success:** the hook block from the handoff is merged into `~/.claude/settings.json` (Option A if working in this checkout, Option B on Tanishq's own hardware with every absolute path re-pointed to where the hook files landed); the client has been restarted so the watcher activates the hooks; and the pass is recorded as the first line of the sprint ledger (`/Users/davidusa/REPOS/Image_Tagger_dk_latest/docs/TANISHQ_SPRINT_LEDGER_2026-08-14.md` **[proposed]**). **[verified — handoff §4]**
- **Validation:** `python3 /Users/davidusa/REPOS/_control/hooks/dogged_stop_hook.py --selftest` prints all-controls-pass; `python3 /Users/davidusa/REPOS/_control/hooks/headless_first_guard.py --selftest` prints all-controls-pass; a `Read` with a bare `limit` (no `offset`) is blocked; a turn that writes "TODO" with no owner is blocked once. On a foreign machine, also confirm `python3` and `bash` resolve.
- **Failure states:** `wired_but_not_activated` (settings merged but the client was not restarted, so no hook fires); `paths_point_at_daves_mac` (Option B copied without re-pointing the absolute paths, so the runner-queue paths do not exist — on a foreign machine, rely on Monitor as the durable channel, not the runner); `selftest_skipped` (installed but never self-tested — indistinguishable at runtime from not installed).
- **Checker ≠ author:** David, or whoever owns the machine handoff, confirms the two self-tests printed pass and observes one live block, against the actual `~/.claude/settings.json` — not against a claim that it was installed.
- **Depends-on:** nothing. This gates every task below.

---

## How every task below is shaped

Each carries: **Goal · Repo/lane · Last-mile Success** (the observable end-state and the exact artifact that turns the gear) · **Validation** (a check that passes only when the task is genuinely done) · **Failure states** (the ways it can look done without being done) · **Checker ≠ author** (a different person or AI lineage verifies, against the exact artifact) · **One-example-first** (the first item is done and verified before the rest are proposed) · **Depends-on**.

Two disciplines run through all of them, because they are the ones a software-oriented planner under-weights:

- **An instrument reading is a proxy until calibrated against a reference.** "Produces a number" is never acceptance; "reads within a stated tolerance of a known reference" is. **[verified — cowork prompt, Tanishq reminder 4]**
- **No procurement for now (David, 2026-08-14).** Tanishq's work uses already-available instruments — his machine, the lab machine, and borrowable campus gear. There is no buy-list. A task that would need an instrument not already on hand simply waits; it does not trigger a purchase. **[stated — DK 2026-08-14]**

---

## Sprint 1 — (removed: no procurement for now)

Per David (2026-08-14), a costed buy-list is **not** part of Tanishq's work at this stage. The lab is fine for a while on David's machine and the lab machine, using already-available instruments and borrowable campus gear. There is no purchasing task here. If dedicated procurement becomes necessary later, it returns as a David-owned decision, not a Tanishq sprint. The shakedown below therefore runs on whatever suitable instrument is already on hand; if none is, it waits rather than triggering a purchase. **[stated — DK 2026-08-14]**

---

## Sprint 2 — The debug-POE shakedown (one instrument, one space)

**Goal.** Before the full multi-space sweep, shake down **one** instrument in **one** space and prove it reads within tolerance of a known reference. This is an environmental shakedown with **no human subjects, so no IRB** — and it stays that way. It produces **receipts, not assurances**: what was measured, against what reference, in what calibration state, as evidence a checker who is not the author can re-verify. **[verified — cowork prompt reminders 2, 4, 5, 8; `FALL_HANDOFF_PACK` Tanishq]**

**Task 2.1 — Reuse the existing capture pipeline for environmental logger ingestion.**
- **Repo / lane:** `Image_Tagger_dk_latest` for the shakedown artifacts; the pipeline *pattern* is reused from `emotibit_polar_data_system` (do not commit into it — it is not in Tanishq's lane; copy or import the pattern into his lane). **[verified — `LANE_MAP`; cowork prompt reminder 6]**
- **Last-mile Success:** an ingestion path under `/Users/davidusa/REPOS/Image_Tagger_dk_latest/poe_shakedown/` **[proposed]** that ingests two co-located CO₂ logger files, schema-validates them, runs a **sync-QC** step reporting drift/overlap/jitter with a 0–100 confidence score and an R/Y/G band, and **refuses to emit metrics in strict mode when the two clocks cannot be trusted to align** — reusing the sync-QC + strict-gate + provenance design already built in `emotibit_polar_data_system` (`backend/`, `scripts/` sync-QC, and the Bland–Altman benchmark scaffold), rather than reinventing it. Sync-QC and provenance metadata are acceptance criteria, not extras. **[verified — `emotibit_polar_data_system/docs/PROJECT_GUIDE_FOR_HUMANS.md` §2–4]**
- **Validation:** on two co-located logs the pipeline emits a sync-QC report (drift, overlap, jitter, confidence, band) and, on a deliberately mis-clocked pair, the strict gate refuses to export — proving the gate is live, not decorative. A provenance record (instrument model, serial, firmware, calibration state, capture window) is attached to the output.
- **Failure states:** `reinvented_the_pipeline` (a fresh ad-hoc ingester instead of reusing the proven sync-QC/provenance machinery); `strict_gate_is_cosmetic` (a mis-clocked pair still exports); `provenance_missing` (numbers with no instrument/calibration metadata beside them); `passes_on_synthetic_only` (works on generated data but never run on a real logger file — the emotibit repo's own honest boundary is that its guarantees are scaffolds until run on real sessions).
- **Checker ≠ author:** David or Stephan re-runs the sync-QC computation from the raw logs and confirms the report and the strict-gate refusal reproduce.
- **One-example-first:** ingest and sync-QC **one** real pair of logs before wiring any batch or additional instruments.
- **Depends-on:** an already-available environmental logger (lab or borrowed — no procurement); the emotibit pipeline pattern (present on disk, git-tracked). **[verified — emotibit inventory 2026-08-14]**

**Task 2.2 — Calibrate the one instrument against a reference and produce the receipt.**
- **Repo / lane:** `Image_Tagger_dk_latest` (`poe_shakedown/`).
- **Last-mile Success:** a shakedown receipt at `/Users/davidusa/REPOS/Image_Tagger_dk_latest/poe_shakedown/RECEIPT_CO2_<space>_<date>.md` **[proposed]** recording: instrument (Aranet4, serial, firmware), the reference it was checked against (a borrowed reference-grade NDIR from EH&S, or a factory-fresh second unit plus a known outdoor ~420 ppm baseline and a CO₂-decay event), the co-located measurement window, the agreement statistics (bias and limits of agreement, Bland–Altman), and the pass/fail against a **stated tolerance** — the Aranet4 spec tolerance is ±(30 ppm + 3% of reading); the acceptance is "reads within that band of the reference across the measured range," not "produced a plausible curve." **Public-repo caution:** the receipt records environmental readings and instrument serials only — no participant data, and raw high-frequency logs are git-ignored (keep the summary + agreement stats in the repo).
- **Validation:** the receipt states a numeric tolerance and shows the measured agreement inside it (or, honestly, outside it → the instrument is flagged, not trusted); the raw log referenced by the receipt exists and the agreement statistic recomputes from it.
- **Failure states:** `number_not_calibration` (a reading reported as trustworthy with no reference comparison — the exact proxy-as-proof failure); `tolerance_unstated` (a "within tolerance" claim with no band written down); `reference_weaker_than_instrument` (checked against something no better than the instrument itself); `receipt_not_reproducible` (agreement stats that a checker cannot recompute from the referenced log).
- **Checker ≠ author:** David or Stephan recomputes the bias and limits of agreement from the referenced raw log and confirms the pass/fail verdict.
- **One-example-first:** this **is** the one example that gates the full sweep — one instrument, one space, one reference. The multi-instrument, multi-space sweep is proposed only after this receipt passes and is checked.
- **Depends-on:** Task 2.1; a borrowable reference-grade CO₂ instrument (borrow-first, EH&S).

---

## Sprint 3 — Deploy / pipeline plumbing (incl. the KA review-page handoff)

**Goal.** Stand up the deployment and data-serving plumbing the fall demo needs — and define the **cross-lane handoff** for serving the Knowledge-Atlas review webpage so the split does not strand the hosted adjudication surface. The division is fixed by the lane map: **Stephan owns the KA "Feature Review" page** (it is grafted into `Knowledge_Atlas`, which is his repo); **Tanishq owns the deploy/plumbing** — hosting it, serving it, and piping data to it — **without committing into `Knowledge_Atlas`.** **[verified — `LANE_MAP`; `FALL_HANDOFF_PACK` Tanishq + Stephan packets; cowork prompt reminder 7]**

**Task 3.1 — Define the serve contract (the interface that makes the split safe).**
- **Repo / lane:** `Image_Tagger_dk_latest` (Tanishq's deploy artifacts live in his lane, never in KA).
- **Last-mile Success:** a serve-contract document at `/Users/davidusa/REPOS/Image_Tagger_dk_latest/docs/KA_REVIEW_SERVE_CONTRACT_2026-08-14.md` **[proposed]** stating exactly what Stephan's lane hands off (a built, deployable bundle or a run command; the port it listens on; the environment variables it needs; the data mount it reads from — the `verification_packets.py` output plus the migration-024 annotations store) and what Tanishq's lane provides (the runtime host, reverse proxy, TLS, DNS, uptime, and the data-sync job that lands the packet files where the page reads them). The page is hosted, JWT-protected (URL + login, no local checkout). **[verified — `FALL_HANDOFF_PACK` Stephan packet, item C]**
- **Validation:** the contract names the artifact Stephan produces and the exact interface (port, env, data path) with no gap that requires Tanishq to edit KA source; a dry-run against a **sample** packet directory (not live data) serves the page and the page reads the sample. **Live data is blocked on codex's 1a pipeline handoff — do not wait on it to build against the sample.** **[verified — `FALL_HANDOFF_PACK`: "STARTABLE NOW against a sample, live data BLOCKED ON codex's 1a handoff"]**
- **Failure states:** `lane_crossed` (Tanishq edits files inside `Knowledge_Atlas` to make it deploy — the lane-guard should and will block the commit); `contract_implicit` (deployment that works only because the deployer happened to know an undocumented port/env, so the next person cannot reproduce it); `secret_in_public_repo` (a JWT signing key, credential, or token committed into the public Image_Tagger repo — GitHub push protection will reject it; design so it never arises, keep secrets in the runtime environment).
- **Checker ≠ author:** Stephan (owner of the KA page) confirms the serve contract matches what his lane actually produces; a second reader confirms no Image_Tagger commit touches KA source and no secret is committed.
- **One-example-first:** serve one sample packet end to end before wiring the live data-sync job.
- **Depends-on:** Stephan / the agent lane producing the built KA Feature-Review bundle (item C, spec `_control/METHODOLOGY/BUILD_SPEC_adjudication_console_2026-08-13.md`); codex's 1a pipeline handoff for **live** data only. **[verified — `FALL_HANDOFF_PACK`]**

**Task 3.2 — Stand up the deployment for the deployable tagger read (storyboard steps 2–3).**
- **Repo / lane:** `Image_Tagger_dk_latest`.
- **Last-mile Success:** a reproducible deployment (documented run command + environment) that serves the packaged tagger read of one real render into attribute fields, from `Image_Tagger_dk_latest`, hosted and reachable — the deploy/plumbing half of the fall demo. The *science* of the read (attributes, evidence binding, confidence rungs) is the software sprints' job (Sprints D/E/G and the agent-lane item B); this task is the serving of it. **[verified — `FALL_HANDOFF_PACK` agent-lane item B; SYSTEM_OVERVIEW §6]**
- **Validation:** a clean-environment run of the documented command brings the service up and returns the attribute fields for one known render; `node_modules`, venvs, caches, and any file >100 MB are git-ignored and absent from commits (public-repo constraint).
- **Failure states:** `works_on_my_machine` (comes up only in the author's environment, no documented reproducible run); `repo_bloated` (a venv, cache, or large binary committed — push protection / the 100 MB limit will reject it); `calibration_overclaimed` (serving a perceptual field as evidence when it is still uncalibrated — every reading must carry its maturity rung; an uncalibrated measure is exploratory, not evidence). **[verified — cowork prompt guardrails]**
- **Checker ≠ author:** a different AI lineage or David runs the documented command from a clean checkout and confirms the service comes up and returns the fields.
- **One-example-first:** one render, one deployment, verified, before any batch or multi-render serving.
- **Depends-on:** the packaged tagger read from the software/agent lane (item B); Sprint 0.

---

## Sequence & dependencies

The order is set by what gates what. With procurement out of scope for now, the near-term work is software-and-deploy plus a shakedown only if a suitable instrument is already on hand — none of which waits on a purchase.

1. **Sprint 0 (gate)** — now; blocks everything.
2. **Sprint 3.1 (serve contract + sample dry-run)** — startable now, independent of hardware and of live data (build against a sample; live data waits on codex 1a). The most useful thing Tanishq can do immediately, on existing machines.
3. **Sprint 2 (shakedown)** — runs whenever a suitable environmental logger is already available (lab or borrowed) plus a borrowable reference; one instrument, one space, one receipt, checked, before any full sweep. If no instrument is on hand, it waits — without triggering a purchase.
4. **Sprint 3.2 (deploy the tagger read)** — waits on the packaged tagger read from the software/agent lane (item B).

Cross-lane, in one line: **Stephan/agent lane hand off the KA page bundle and (later) codex hands off the live pipeline → Tanishq serves them.** The human-subjects lane (physiology, cognitive tasks on people, wearables, cortisol) needs IRB and stays **off Tanishq's critical path**. **[verified — kit protocol §2, §5]**

**The near-term work that proceeds now, on existing machines:** the deploy serve-contract (Sprint 3.1) and, if an instrument is already on hand, the one-instrument shakedown (Sprint 2). Neither waits on any purchase.

---

## Relationship to Tanishq's existing sprints (extend, don't duplicate)

This set adds the hardware/deploy lane. It does not restate the software sprints Tanishq already holds, which remain live and in his lane:
- `docs/TANISHQ_ONBOARDING_AND_SPRINTS_2026-07-21.md` — Sprint A (corpus image database), B (M1′ audit coverage), C (cross-environment determinism), D (Wave-3 detector deployment), E (corpus scoring pipeline), F (labelling console backend + deploy — **IRB before any real participant**), G (annotated-image search). **[verified]**
- `docs/TANISHQ_SPRINT_CARDS_2026-07-23.md` — the assignable tagger cards (LEG-1, CC-3/5/6/7/8/9, VIEW-4/5, DK-1-support). **[verified]**

Sprint 3.2 here is the *deployment* half of what Sprints D/E/G and agent-lane item B produce; Sprint 3.1 is the plumbing for Stephan's KA page. Where this set and the older docs both touch deployment, this set owns the hosting/serving contract and the older docs own the science of what is served.

---

## Provenance

The pre-flight gate, the acceptance self-tests, and the two guards that matter most for this lane are from `/Users/davidusa/REPOS/_control/METHODOLOGY/METHOD_ENFORCEMENT_CONTROLLER_HANDOFF_2026-08-14.md` (§6) and the cowork sprint-set builder prompt `/Users/davidusa/REPOS/_control/prompts/COWORK_SPRINT_SET_BUILDER_PROMPT.md` (Tanishq reminders 1–8, and the task-shape/guardrail requirements). The lane split and the lane-guard are from `/Users/davidusa/REPOS/_control/METHODOLOGY/LANE_MAP_2026-08-14.md`. The instrument list, models, indicative GBP prices, the environmental-vs-human-wear split, and the IRB line are from `/Users/davidusa/Documents/Zaha/_2026/POE_Pilot_Kit_Protocol_Instruments_IRB_ZHA_2026-07-21.html` §3–5 (a confidential-folder working document; only the procurement-guidance instrument list and IRB outline are used here — the ZHA commercials and first-meeting agenda are not reproduced). The pipeline-reuse target (sync QC, strict-sync gate, R/Y/G confidence, Bland–Altman scaffold, provenance) is from `/Users/davidusa/REPOS/emotibit_polar_data_system/docs/PROJECT_GUIDE_FOR_HUMANS.md`. The fall target, the per-person assignments, the KA Feature-Review handoff, and the ~£4–8k procurement gate are from `/Users/davidusa/REPOS/_control/METHODOLOGY/FALL_HANDOFF_PACK_2026-08-13.md`. The system frame, the fourth-code quantities (STI, m-EDI, real ventilation), and the maturity-rung / calibration-before-evidence discipline are from `/Users/davidusa/REPOS/SYSTEM_OVERVIEW.md` and `/Users/davidusa/REPOS/Post_Occupancy_Evals/docs/PROJECT_GUIDE_FOR_HUMANS.md`. Written under the science-communication norms in `/Users/davidusa/REPOS/atlas_shared/contracts/SCIENCE_COMMUNICATION_NORMS.md`. Items marked **[proposed]** are intended artifacts that do not yet exist; **[stated — DK]** is recorded intent; **[verified]** was read this session.
