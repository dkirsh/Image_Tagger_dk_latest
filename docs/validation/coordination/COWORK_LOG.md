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
