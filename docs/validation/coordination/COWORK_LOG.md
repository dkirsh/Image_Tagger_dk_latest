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
note: `docs/space_effects/` is a new top-level docs subtree; the broadened `git add -- docs/`
  sweep already covers it. No new asks. Phase-1 replay still the blocking handoff.
needs: unchanged — your Phase-1 replay artifacts.
