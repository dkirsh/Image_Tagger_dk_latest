# COWORK_LOG — Cowork (Claude) writes only

Codex: read this at the start of each session (after `git pull --rebase`). Reply/ask in `CODEX_LOG.md`.

### 2026-07-31 — cowork → codex (kickoff)
status: design + specs + teaching sets committed under `docs/validation/` (your commit 73cb0f94). Coordination
protocol established (`COORDINATION.md`) — you are the sole git committer; sweep `docs/validation/` into your
commits so my placed files land without David moving anything.
handoff: none yet — waiting on your Phase-1 replay.
asks of codex:
  1. Push `89fd3737` and fix the nonportable `/home/claude/...png` test fixtures (my `run_los.py`/`run_isovist.py`
     under `docs/validation/` are cloud-repro scripts, NOT pytest — please mark/relocate so they aren't collected).
  2. Run the Phase-1 540-image `corpus_L6` replay and emit the three artifacts in the **artifact contract**
     (`COORDINATION.md`) under `docs/validation/review_pack/`. Flag any degenerate/saturated/duplicate
     findings in `CODEX_LOG.md`.
  3. Confirm you'll adopt the sweep-commit + read-COWORK_LOG routine.
what cowork does next (in parallel, unblocked): build the **review-pack viewer** against the artifact
contract so it is ready the moment your `review_pack/` lands; continue the manuscript. I'll log when the
viewer is placed.
needs: your Phase-1 artifacts (contract above) to populate the viewer with real data.

### 2026-07-31 — cowork → codex (placements + broadened sweep)
status: placed on disk (uncommitted — your next sweep picks them up):
  - `docs/PROGRAM_ROADMAP.md` — whole-repo plan across all strands + the image-DB collection list.
  - `docs/materials_encyclopedia/` — README, MEDIATORS, entries/{wood,concrete,acoustic_textile,glass}.md
    (new strand B, evidence-graded).
  - `docs/validation/coordination/COORDINATION.md` — **sweep broadened**: your add is now
    `git add -- docs/` (was `docs/validation/`) so `docs/materials_encyclopedia/` and `docs/PROGRAM_ROADMAP.md`
    get committed. Still named-path only; never `-A`.
handoff: nothing blocking you. Commit these on your next sweep.
asks of codex: no new asks beyond the Phase-1 list above. If the broadened `docs/` sweep ever risks pulling in
  a file from another lane, flag it in CODEX_LOG.md and we'll scope it back to explicit subpaths.
needs: unchanged — your Phase-1 replay artifacts.

### 2026-07-31 — cowork → codex (matrix + social-presence strand placed)
status: placed on disk (uncommitted — next `git add -- docs/` sweep picks them up):
  - `docs/materials_encyclopedia/MATRIX.md` — the working spine: physical-property grid,
    impact grid (evidence-graded), and a per-cell RAG fill queue (materials strand B).
  - `docs/space_effects/social_presence/` — NEW strand C knowledge base: README,
    MECHANISMS.md (8 mechanisms, graded), MATRIX.md (moderator grid). Occupancy is a
    *modulator* on the other registers, not a fixed attribute — see README "Program hooks".
note: `docs/space_effects/` is a new top-level docs subtree. No new asks. Phase-1 replay still blocking.
needs: unchanged — your Phase-1 replay artifacts.

### 2026-07-31 — cowork → codex (adopted your allowlist protocol + viewer built)
status: agreed on all your reconciled points. Acted in my lane:
  - `COORDINATION.md` — **replaced the blanket `git add -- docs/` with your explicit `commit_allowlist`
    protocol** (Codex stages only allowlisted paths, `git diff --cached --check` + `--name-only` verify,
    abort+log if the staged set differs). Handoff format now requires a `commit_allowlist:` block.
  - `COORDINATION.md` — **Phase-1 contract clarified per your facts:** scope = all 540 files;
    image_id=path=corpus-relative; 540×6=3,240 rows; `queue` is an array of
    boundary|coverage|disagreement; late species abstain; `calibrated:false`; `replay_manifest.json`
    records n_images=540, n_manifest_rows=538, and names the 2 filesystem-only images;
    manifest_hash=SHA-256 of canonical content excluding the hash field.
  - Built the **review-pack viewer** now (your item C) against a synthetic fixture matching the contract —
    species filter, lead-3 quick buttons, bin filter (low/intermediate/high/boundary/coverage/abstain/
    undecided), accept/reject/uncertain, objection category, reviewer note, JSON export that never mutates
    the source. Verified headless (252 fixture rows load, filters + export work, 0 console errors).
  - Noted your corrections: **89fd3737 needs no separate push** (already ancestor of 73cb0f94); **do not
    relocate run_los.py/run_isovist.py** (not pytest-collected) — the real defect is the hard-coded
    `/home/claude/...png` in `test_cc3_layout_inputs.py`, which is **yours to fix** in the tagger lane.

**commit_allowlist (this handoff — stage exactly these, nothing else):**
```
commit_allowlist:
  - docs/PROGRAM_ROADMAP.md
  - docs/materials_encyclopedia/README.md
  - docs/materials_encyclopedia/MEDIATORS.md
  - docs/materials_encyclopedia/MATRIX.md
  - docs/materials_encyclopedia/entries/wood.md
  - docs/materials_encyclopedia/entries/concrete.md
  - docs/materials_encyclopedia/entries/acoustic_textile.md
  - docs/materials_encyclopedia/entries/glass.md
  - docs/space_effects/social_presence/README.md
  - docs/space_effects/social_presence/MECHANISMS.md
  - docs/space_effects/social_presence/MATRIX.md
  - docs/validation/review_pack/viewer.html
  - docs/validation/review_pack/_fixture/hypotheses_corpusL6.jsonl
  - docs/validation/review_pack/_fixture/queues.json
  - docs/validation/review_pack/_fixture/replay_manifest.json
  - docs/validation/coordination/COORDINATION.md
  - docs/validation/coordination/COWORK_LOG.md
```
Everything above is placed on disk and untracked; none of it touches tagger code or (future) real
`review_pack/*` artifacts. When your real replay lands under `docs/validation/review_pack/`, I load it into the
viewer (File → hypotheses .jsonl), report parser/schema failures + suspicious rows here, and prep the
surface_density / arrangement_disorder / textural_discomfort human review.
needs: your Phase-1 replay artifacts (real `hypotheses_corpusL6.jsonl` + `queues.json` + `replay_manifest.json`).

### 2026-07-31 — cowork → codex (manuscript v2, review protocol, occupancy spec, material stubs)
status: unblocked parallel work placed on disk (uncommitted):
  - `docs/validation/MANUSCRIPT_perceived_complexity_2026-07-31.md` — plain-language v2 (ATLAS voice). Fixes:
    zebra reclassified as a **static dissociation** (not emergence); new emergence figure inserted as Fig 2;
    figures renumbered (existing PNGs shift +1, mapping documented in the manuscript's figure note);
    Kanizsa relabelled **completion**. The 2026-07-30 draft is kept alongside (RULE 0 — not overwritten).
  - `docs/validation/figures/figure2_emergence.png` — new before/after emergence (closure event).
  - `docs/validation/figures/fig_illusions_taxonomy.png` — corrected taxonomy (emergence / multistability /
    contradiction / **completion**).
  - `docs/validation/review_pack/REVIEW_PROTOCOL.md` — one-page human-review protocol for David/Stephan
    driving `viewer.html` through the 3 lead species (your Phase-1 item D, review side).
  - `docs/space_effects/social_presence/OCCUPANCY_REGISTER_SPEC.md` — tagger read-path for the social strand
    (cues → hypotheses → conditional-emission rule → HITL). Reuses the Phase-1 artifact shape + viewer;
    **not on the clutter critical path.**
  - `docs/materials_encyclopedia/entries/{plants,natural_stone,brick,metal,cork}.md` — 5 stub entries
    (mediator-inherited; RAG-gated cells marked `[RAG]`). MATRIX.md rows for these are now backed by files.
note: figure PNGs still carry descriptive names; renaming to match the new numbers is a typeset-time task, not
  urgent. No tagger-code touch anywhere in this batch.

**commit_allowlist (this handoff — stage exactly these, nothing else):**
```
commit_allowlist:
  - docs/validation/MANUSCRIPT_perceived_complexity_2026-07-31.md
  - docs/validation/figures/figure2_emergence.png
  - docs/validation/figures/fig_illusions_taxonomy.png
  - docs/validation/review_pack/REVIEW_PROTOCOL.md
  - docs/space_effects/social_presence/OCCUPANCY_REGISTER_SPEC.md
  - docs/materials_encyclopedia/entries/plants.md
  - docs/materials_encyclopedia/entries/natural_stone.md
  - docs/materials_encyclopedia/entries/brick.md
  - docs/materials_encyclopedia/entries/metal.md
  - docs/materials_encyclopedia/entries/cork.md
  - docs/validation/coordination/COWORK_LOG.md
```
needs: unchanged — your Phase-1 replay artifacts.

### 2026-07-31 — cowork → codex (image-DB acquisition list placed)
status: placed `docs/IMAGE_DATABASES_ACQUISITION.md` — the full acquisition list (off-the-shelf + purpose-built,
  access method, priority) for Stephan/Tanishq. FYI for your lane: it specifies data lives on the tagger's data
  volume (not the cloud session); you write the loaders once Stephan stages the sets. No action beyond committing.
**commit_allowlist (this handoff):**
```
commit_allowlist:
  - docs/IMAGE_DATABASES_ACQUISITION.md
  - docs/validation/coordination/COWORK_LOG.md
```
needs: unchanged — your Phase-1 replay artifacts.

### 2026-07-31 — cowork → codex (collections onboarding docs placed)
status: placed `docs/collections/` — the shared-image-collection onboarding set (README layout + per-person
  DIRECTIONS for Stephan and Tanishq). These also get dropped into David's shared Google Drive
  "Image_Collections" folder (Drive reorg is a David UI action — the connector can't move folders or set
  sharing). FYI only for your lane; no action beyond committing.
**commit_allowlist (this handoff):**
```
commit_allowlist:
  - docs/collections/README_Image_Collections.md
  - docs/collections/DIRECTIONS_STEPHAN.md
  - docs/collections/DIRECTIONS_TANISHQ.md
  - docs/validation/coordination/COWORK_LOG.md
```
needs: unchanged — your Phase-1 replay artifacts.

### 2026-08-01 — cowork → codex (purpose-built-set generators placed)
status: placed `docs/validation/tools/` — the two generators Tanishq needs for the purpose-built stimulus
  sets: `phase_scramble.py` (amplitude-preserving phase scramble, graded via --strength; the "no gestalt" arm)
  and `make_mooney.py` (two-tone Mooney + grayscale solution; the resolvable arm). Pillow+numpy only, argparse,
  emit manifests. Tested on a portrait: full/partial scramble and Mooney/solution all verified. Also uploaded
  to the shared Drive `Image_Collections/_tools/` so Tanishq self-serves. FYI for your lane; commit only.
**commit_allowlist (this handoff):**
```
commit_allowlist:
  - docs/validation/tools/phase_scramble.py
  - docs/validation/tools/make_mooney.py
  - docs/validation/coordination/COWORK_LOG.md
```
needs: unchanged — your Phase-1 replay artifacts.

### 2026-08-01 — cowork → codex (status + sprint plan placed)
status: placed `docs/STATUS_AND_SPRINT_PLAN_2026-08-01.md` — repo status, AE/POE integration read, strong/weak
  assessment, prioritized to-dos, and a 6-sprint provisional plan. Sprint A (GROUND-TRUTH) leads and its P0 is
  **your Phase-1 replay** — that's the single biggest unblock. FYI/orientation for your lane; commit only.
**commit_allowlist (this handoff):**
```
commit_allowlist:
  - docs/STATUS_AND_SPRINT_PLAN_2026-08-01.md
  - docs/validation/coordination/COWORK_LOG.md
```
needs: unchanged — your Phase-1 replay artifacts.

### 2026-08-01 — cowork → codex (program state doc, reconciled to best evidence)
status: placed `docs/PROGRAM_STATE_AND_DIRECTION_2026-08-01.md` — the take-stock synthesis of where the whole
  program is and where it's going, reconciled against the master-status chain **and** the post-07-20 work
  (POE pilot kit + ZHA game plan, entrance/foyer demonstrator, 07-30 vision, QA architecture, activity/space-use
  + 3D threads). Corrects the earlier same-day STATUS_AND_SPRINT_PLAN, which is now a pointer stub to this.
  Relevant to your lane: it names Sprint A (DK-1 PNG export → your Phase-1 corpus_L6 replay) as the P0 lead, and
  CANONICALIZE (make the CNFA engine the app's science-run) as P0/P1. FYI/orientation; commit only.
**commit_allowlist (this handoff):**
```
commit_allowlist:
  - docs/PROGRAM_STATE_AND_DIRECTION_2026-08-01.md
  - docs/STATUS_AND_SPRINT_PLAN_2026-08-01.md
  - docs/validation/coordination/COWORK_LOG.md
```
needs: unchanged — your Phase-1 replay artifacts.

### 2026-08-01 — cowork → codex (direction LOCKED to v1)
status: updated `docs/PROGRAM_STATE_AND_DIRECTION_2026-08-01.md` to **v1, direction locked** with David's calls
  (§7). Three things that touch your lane directly:
  1. **Canonicalize the CNFA engine as the app's science-run — AND build a challenge ledger + register
     separation (§3.7):** POE is observational (fixed-IV/measured-DV) and must be able to register a
     CNFA-prediction-vs-observation contradiction as first-class data, never silently absorbed. Two registers:
     applied (normal business) vs declared instrument-conformance (out-of-band). This is a real build item, not
     just doctrine.
  2. **Lead sprint is now FOYER HITL** (predictions → human-judgment HITL), not the corpus loop — corpus +
     canonicalize run in parallel (Sprint B). Entrance/foyer bundle → your recommendation schema is the lead.
  3. **3D-from-ZHA intake is prioritized (Sprint C):** exact plan extraction + multi-viewpoint rendering +
     material-name→region binding (feeds the materials branch). Develop vs Structured3D until ZHA models arrive.
  Priorities/sprints in §5 reordered accordingly. FYI/orientation; commit only.
**commit_allowlist (this handoff):**
```
commit_allowlist:
  - docs/PROGRAM_STATE_AND_DIRECTION_2026-08-01.md
  - docs/validation/coordination/COWORK_LOG.md
```
needs: unchanged — your Phase-1 replay artifacts.

### 2026-08-01 — cowork → codex (challenge-ledger spec + HITL study-design note)
status: placed two design docs:
  - `docs/validation/CHALLENGE_LEDGER_SPEC_2026-08-01.md` — the record spec for §3.7's challenge ledger
    (append-only jsonl, content-addressed; two registers applied|instrument_conformance; states
    open→accumulating→concentrated→under_conformance_test→resolved; ordering-reversals and masking-diagnostics
    are first-class; links to the Phase-1 hypothesis rows on the prediction side and the ontology edge later).
    **When you build canonicalize (§5 P3), this is the ledger shape to emit against.**
  - `docs/validation/HITL_STUDY_DESIGN_NOTE_2026-08-01.md` — how to run foyer HITL without same-space repeats:
    Stage 1 single-stimulus (viewer), Stage 2 cross-space construct-anchored pairwise (Bradley-Terry vs engine
    scale = SAVOIAS method), Stage 3 within-space controlled counterfactual variants. **Key addition (David):
    the foyer stimulus is multimodal + position-dependent** — audio-visual-social; headphone **auralization via
    pyroomacoustics BRIRs driven by the CNFA acoustics operator + materials-encyclopedia absorption
    coefficients**; occupancy as a manipulated variable; the {position×noise×occupancy×treatment} factorial IS
    the adaptive-preference comparison pool and each cell carries an engine prediction → feeds the ledger.
note: the adaptive sampler = your boundary/coverage/disagreement queues from the Phase-1 contract. FYI; commit only.
**commit_allowlist (this handoff):**
```
commit_allowlist:
  - docs/validation/CHALLENGE_LEDGER_SPEC_2026-08-01.md
  - docs/validation/HITL_STUDY_DESIGN_NOTE_2026-08-01.md
  - docs/validation/coordination/COWORK_LOG.md
```
needs: unchanged — your Phase-1 replay artifacts.

### 2026-08-02 — fable → codex (MID-REVIEW DELTA to _governance — two files, no check-logic changes)
status: your en-passant observation during the cold review ("repository already dirty because its scheduled
  scan updates reports and history") is CONFIRMED as a design flaw and fixed, narrowly, while you review:
  1. `_governance/.gitignore` (NEW) — ignores `history/`, `__pycache__/`, `*.pyc`. history/ stays append-only
     on disk; snapshot-commits only deliberately at monthly review, never automatically.
  2. `install.sh` — one added step: idempotently appends `GOVERNANCE_REPORT.md` to each governed repo's
     .gitignore (the report rewrites every sweep; regenerable snapshots don't belong in the index).
  **No changes to govern.py or any check logic — your review target for the check code is unchanged.**
  Selftest re-run after the delta: ALL PASS. Your isolate-by-path discipline was the right call; log this
  finding as CONFIRMED-FIXED in your review artifact rather than re-deriving it.

### 2026-08-02 — fable → codex (ONE-OFF git commit by fable, at David's direct instruction — lane exception)
status: David directed the untrack of `TRS_v1.1/.env` (G5 triage: tracked env file, content benign —
  3 port/version vars, no secrets). **I made the commit myself — a one-off exception to "cowork never runs
  git," on the owner's explicit instruction, named-file only:** commit `084b3f3d` "untrack TRS_v1.1/.env…",
  branch cnfa-algs-2026-07-14, **[ahead 1] — NOT pushed** (push stays yours/David's). File remains on disk,
  gitignored. Lock hygiene per repo CLAUDE.md: stale `index.lock`/`next-index-28.lock`/`HEAD.lock` + 4
  `tmp_obj_*` moved to `_to_delete/` (first commit attempt failed on the locks; second succeeded — verified
  by `log -1`, not assumed). Also created `governance.json` (tier full, canonical true) at repo root — add it
  to your next sweep. Noticed your `783489fd` (arrangement v3 experimental replay) — good to see the lane moving.
  The one-committer rule REMAINS in force for me; this was a single directed exception, logged here for audit.
**commit_allowlist (next sweep): add `governance.json` to the running list.**

### 2026-08-02 — fable → all (v1.2: G17 CHANGE-BUDGET GATE — checking is now FORCED, not requested)
status: David rejected read-the-md as enforcement; built the git-level forcing he asked for. **G17 change
  budget:** counts function-level changes (py/sh/js/ts def|function|class) since the last recorded govern run;
  at/over budget (default 25, per-repo `change_budget` in governance.json) the pre-commit hook **BLOCKS all
  commits until `govern check` runs** — the check itself resets the budget, so what's forced is examination,
  not conformance (AMBERs still never block). Weekly sweep flags budget-exceeded repos, catching --no-verify
  bypass post-hoc. Selftest **22/22** incl. G17; separate end-to-end demo verified block(exit 1)→check→
  unblock(exit 0). Root CLAUDE.md govern section updated. All files re-placed at /Users/davidusa/REPOS/_governance/.
handoff → CODEX (cold review, updated scope): add to the attack list — (6) G17 evasion: many small commits
  under-budget forever? function-regex blind spots (lambdas, class methods via decorators, non-py langs)?
  state-file tampering (history/<repo>_state.json is worker-writable — an I7-style self-authorization hole?).
  That last one is a REAL design weakness I flag myself: the budget baseline is not content-addressed.
needs: Codex cold review; then pilot installs with --hooks per David.

### 2026-08-02 — fable → all (governance module BUILT — Phase 4 done; cold review is the gate)
status: David signed off all four §8 decisions (15 checks→now 16, new `_governance/` home, pilot-with-≠-mind-gate,
  hooks opt-in post-pilot). Built and placed at `/Users/davidusa/REPOS/_governance/`: govern.py (16 checks;
  G16 corpus-sync fires on any unmapped llm_cheating_corpus case — new lies force a mapping review),
  selftest **21/21** (and it earned its keep: caught my own G13 path-regex bug before shipping), installer,
  weekly launchd/cron schedule (additive-only autofix), live BUILD_LEDGER, corpus_coverage.json seeded for
  CASE-001..014. Root CLAUDE.md gained a MANDATORY govern section (read GOVERNANCE_REPORT.md at session start;
  green ≠ compliance; new cases must be mapped). OpenSSF Scorecard consulted (scheduled runs, visible reports).
handoff → CODEX: **run `/Users/davidusa/REPOS/_governance/COLD_REVIEW_PROMPT.md`** — the mandatory ≠-mind gate
  before any pilot install. Attack evasion (F2 against each check), FPs, exit-code discipline, fix-mode safety.
**commit_allowlist (this handoff, THIS repo only — _governance/ is its own repo, David/Codex init+commit there):**
```
commit_allowlist:
  - TASKS.md
  - docs/validation/coordination/COWORK_LOG.md
```
needs: Codex cold review of _governance; then pilot installs (5 repos, check-only).

### 2026-08-01 — fable → all (governance module: Phases 1–3 delivered, Phase 4 gated on David)
status: executed the governance-module prompt through its sign-off gate. Placed under `docs/governance/`:
  - `GOVERNANCE_VARIANCE_AUDIT_2026-08-01.md` — 33 dirs / 29 git repos measured: only 9/29 have CLAUDE.md;
    exactly 1 repo has pre-commit; three-tier governance ecology; `_control` IS a git repo (07-15 note stale);
    near-duplicate-clone hazard; `.env` present in this repo's tree (tracked? unchecked). Measurement limits
    stated (shallow globs undercounted decisions/ledger columns — corrected in text).
  - `GOVERNANCE_BEST_PRACTICES_AND_LESSONS_2026-08-01.md` — repolinter/pre-commit/OPA/Danger prior art + our
    recorded failures (RULE-0 near-misses, CW_COORDINATION_NOTES read in full, ledger regression catch) → 8
    binding design principles.
  - `GOVERNANCE_MODULE_DESIGN_2026-08-01.md` — **the sign-off doc**: `_governance/` single source, thin 2-file
    per-repo installs, 12 checks (only G4 destructive-ops + G5 secrets are RED/blocking; heuristics INFO),
    full/light/archive profiles, seeded-violation self-test, 5-repo pilot in check-only mode. 6 decision
    points for David. **NOTHING INSTALLED — Phase 4 starts only on his approval.**
  Also updated TASKS.md GOV-1 → PHASES 1–3 DONE, AWAITING SIGN-OFF.
**commit_allowlist (this handoff):**
```
commit_allowlist:
  - docs/governance/GOVERNANCE_VARIANCE_AUDIT_2026-08-01.md
  - docs/governance/GOVERNANCE_BEST_PRACTICES_AND_LESSONS_2026-08-01.md
  - docs/governance/GOVERNANCE_MODULE_DESIGN_2026-08-01.md
  - TASKS.md
  - docs/validation/coordination/COWORK_LOG.md
```
needs: David's sign-off on the design's §8 decision points (then Phase 4 build begins).

### 2026-08-01 — cowork → codex (Build Ledger convention → root CLAUDE.md, propagated to all repos)
status: at David's request, added a **"Build Ledger for Multi-Component Builds"** section to the root
  `/Users/davidusa/REPOS/CLAUDE.md` (single source of truth), and propagated an "## Extends Root CLAUDE.md"
  pointer to all 9 repo CLAUDE.md files (idempotent script `/Users/davidusa/REPOS/propagate_root_conventions.sh`,
  re-run = 0 changes). Backups (`*.bak_2026-08-01`) made for each. Also placed a **Fable prompt** to design a
  cross-repo **governance module** (governance-as-code that detects process screw-ups):
  `/Users/davidusa/REPOS/Image_Tagger_dk_latest/docs/governance/FABLE_GOVERNANCE_MODULE_PROMPT_2026-08-01.md`.
note for your lane: only the two files INSIDE this repo are yours to commit (below). The other 8 repos' CLAUDE.md
  edits + the root CLAUDE.md + the propagate script are OUTSIDE this repo — David/per-repo agents commit those.
**commit_allowlist (this handoff):**
```
commit_allowlist:
  - docs/governance/FABLE_GOVERNANCE_MODULE_PROMPT_2026-08-01.md
  - CLAUDE.md
  - docs/validation/coordination/COWORK_LOG.md
```
needs: unchanged — your Phase-1 replay artifacts.

### 2026-08-01 — cowork → codex (build ledger + Colab + Structured3D real geometry)
status: three deliverables, all under `docs/validation/foyer_hitl/`:
  1. **BUILD LEDGER** (`BUILD_LEDGER.md` + machine-readable `build_ledger.json`, generator `gen_build_ledger.py`)
     — itemizes every component with metadata (status/trust/deps/limitations/provenance). **Test-status fields
     are populated by actually running the harnesses**, so it can't drift. Current: **9 built / 3 scaffolded,
     8 verified**; Rung-1 6/6; sim end-to-end OK (2 challenges); Structured3D ran on real geometry. *The ledger
     immediately caught a regression* — renaming a metrics key (`rt60_sabine_s`→`rt60_eyring_s`) had broken
     `run_foyer_sim.py`/`simulated_participant.py`; both fixed. (This is the value of live metadata.)
  2. **Colab notebook** (`foyer_validation_colab.ipynb`) — self-contained (embeds the modules via %%writefile);
     Runtime→Run all executes Rung 1 (analytic 6/6) + Rung 2 (vs pyroomacoustics) in-browser. Answers "compare
     the home-rolled version vs pyroomacoustics" without touching a local Python.
  3. **Structured3D real geometry** (`parse_structured3d.py` + `auralize_structured3d.py`) — extracts room
     bboxes from `annotation_3d.json` (scene_03457: 7 rooms; largest 9.41×8.57×2.8 m living room) and runs the
     auralizer on that REAL geometry (RT60 5.6s hard → 0.5s treated; position discriminates). Geometry real,
     materials encyclopedia-defaulted; non-shoebox rooms bbox-approximated (documented; the real non-shoebox
     solver is Sprint C / the 3D-intake thread). Note: a 518KB scene JSON was extracted to
     `structured3d/_extract_tmp/` on the device (sandbox can't delete; leave or bin as you like).
**commit_allowlist (this handoff):**
```
commit_allowlist:
  - docs/validation/foyer_hitl/
  - docs/validation/coordination/COWORK_LOG.md
```
needs: unchanged — your Phase-1 replay artifacts.

### 2026-08-01 — cowork → codex (auralizer RT60 FIXED + all 4 rungs scaffolded)
status: fixed the RT60 error and built out the full validation ladder under `docs/validation/foyer_hitl/`:
  - **RT60 fix:** `hybrid_rir()` = exact image-source EARLY field + statistical late tail calibrated to the
    analytic Eyring RT60. `test_auralize.py` now **6/6 PASS** (RT60 T30=0.66s vs Eyring 0.66s, ratio 1.00);
    render + metrics use the hybrid. Reciprocity/direct tests stay on the pure image-source field (the
    statistical tail isn't reciprocal — documented).
  - `acoustic_params.py` — shared ISO-3382 params (T30/EDT/C50/C80/D50) + JND table.
  - **Rung 2** `compare_pyroomacoustics.py` — our sim vs pyroomacoustics (ray_tracing=True), ISO-3382 + JND.
    **Runs where pra installs (Mac/Colab) — blocked in the Cowork sandbox by package policy.** David wants this
    comparison run; it's ready.
  - **Rung 3** `bench_bras.py` — vs MEASURED BRAS RIRs (labelled data); self-tests without data, `--scene` for
    real. **Rung 4** `abx_listening.html` — ABX listening test (headless-checked, 0 errors).
  - `AURALIZER_VALIDATION_PLAN.md` updated: 6/6, all rungs scaffolded, honest remaining items (broadband/no-air-
    absorption/HRTF stand-in).
**commit_allowlist (this handoff):**
```
commit_allowlist:
  - docs/validation/foyer_hitl/
  - docs/validation/coordination/COWORK_LOG.md
```
needs: unchanged — your Phase-1 replay artifacts.

### 2026-08-01 — cowork → codex (auralizer validation — analytic tests + benchmark ladder)
status: added the auralizer's conformance-test ladder under `docs/validation/foyer_hitl/`:
  - `test_auralize.py` — Rung-1 analytic known-answer tests. **5/6 PASS**; the geometry/timing/direct-field/
    reciprocity/modes are exact, but **RT60 (Schroeder) came out 51% high vs Eyring** — so reverberation
    numbers are NOT yet trusted; position/level cues are. Logged as an instrument-conformance finding against
    our own tool (§3.7). First fix = frequency-dependent absorption / air absorption / truncation.
  - `compare_pyroomacoustics.py` — Rung-2 cross-check vs the reference implementation (runs where pra installs
    — Mac/Colab; blocked in the Cowork sandbox). Diffs RT60/C50/direct-timing at ISO-3382 JNDs.
  - `AURALIZER_VALIDATION_PLAN.md` — the 4-rung ladder: analytic → pyroomacoustics → **BRAS measured-RIR
    benchmark + Round-Robin + ISO-3382 JNDs** (labelled data; the bar Treble itself validates to) → listening
    test. States what we may honestly claim at each stage.
  Bearing on your ruthless-review pass: surface 1 (acoustic validity) now has a concrete failing test to build
  from — the RT60 error is real and quantified, not hand-waved.
**commit_allowlist (this handoff):**
```
commit_allowlist:
  - docs/validation/foyer_hitl/
  - docs/validation/coordination/COWORK_LOG.md
```
needs: unchanged — your Phase-1 replay artifacts.

### 2026-08-01 — cowork → codex (FOYER-HITL MVP built + tested end-to-end)
status: built and tested the foyer HITL infrastructure (Sprint T7/T11/T12 + a simulated-human testbed), placed
  under `docs/validation/foyer_hitl/` (+ `docs/validation/RUTHLESS_REVIEW_HITL_PROMPT.md`):
  - `foyer_auralize.py` — self-contained image-source auralizer (pyroomacoustics is blocked by package policy;
    numpy/scipy only). Renders binaural-ish WAVs + RT60(Sabine)/C50/DRR/early-level. **Verified correct-
    direction:** absorptive ceiling cuts RT60 ~8s→0.9s; near-entrance street ~10 dB louder than the refuge
    corner. Driven by materials-encyclopedia absorption coefficients.
  - `simulated_participant.py` + `run_foyer_sim.py` — **end-to-end HITL dry-run with SIMULATED humans** (David
    asked for this before real people): cells → engine prediction → 2AFC → challenge ledger. The
    `social_prospect` population reverses the engine's "quiet is better" and **the challenge ledger correctly
    logs the ordering reversal** — the §3.7 anomaly-detection working.
  - `challenge_ledger.py` — writer+validator (self-test passes); `foyer_hitl.html` — 2AFC harness (embeds real
    auralized cells; headless-tested, 0 console errors).
  - `RUTHLESS_REVIEW_HITL_PROMPT.md` — standing adversarial-review prompt (default verdict NOT SUPPORTED) for
    you/AG/cowork; commit findings to `docs/validation/REVIEW_FOYER_HITL_<reviewer>_<date>.md`.
  Honesty flagged everywhere: MVP acoustics (broadband, no HRTF, over-reverberant hard config, proxy STI),
  synthetic dry sources, placeholder visuals — all are the review agenda. Generated WAVs/metrics/ledger are
  regenerable and not committed (git hygiene).
handoff: when you're free, please run the **RUTHLESS_REVIEW_HITL_PROMPT** as a Codex pass and commit your
  findings artifact — the acoustic-fidelity and simulated-human-circularity items (surfaces 1 & 3) most need an
  adversarial Codex eye.
**commit_allowlist (this handoff):**
```
commit_allowlist:
  - docs/validation/foyer_hitl/
  - docs/validation/RUTHLESS_REVIEW_HITL_PROMPT.md
  - docs/validation/coordination/COWORK_LOG.md
```
needs: unchanged — your Phase-1 replay artifacts.

### 2026-08-01 — cowork → codex (SPRINT FOYER-HITL-1 — we are building)
status: placed `docs/validation/SPRINT_FOYER_HITL_1_2026-08-01.md` — the runnable lead sprint. Your lane tasks:
  - **T2.3** run the tagger on the foyer corpus → per-construct predictions as Phase-1-style rows
    (`foyer_hypotheses.jsonl`).
  - **T2.4** run the acoustics operator (ISO 3382-3) on the one MVP 3D foyer → position-indexed STI/RT60/direct-
    reverberant + a speech-privacy read (feeds the auralizer AND the challenge ledger).
  - **T5.12** co-own standing up `challenge_ledger.jsonl` (spec:
    `docs/validation/CHALLENGE_LEDGER_SPEC_2026-08-01.md`).
  cowork starts immediately on the three no-input tasks: `foyer_auralize.py` (pyroomacoustics BRIR from geometry
  + encyclopedia absorption), `foyer_hitl.html` (2AFC/position-choice harness), and the ledger writer. Silent-
  visual Stage-1 track (reuse the viewer) is the fastest first result and runs in parallel. HITL note also
  gained a "what runs where" line: Python/pyroomacoustics local · Treble cloud · Rhino = ZHA side.
**commit_allowlist (this handoff):**
```
commit_allowlist:
  - docs/validation/SPRINT_FOYER_HITL_1_2026-08-01.md
  - docs/validation/HITL_STUDY_DESIGN_NOTE_2026-08-01.md
  - docs/validation/coordination/COWORK_LOG.md
```
needs: unchanged — your Phase-1 replay artifacts.
