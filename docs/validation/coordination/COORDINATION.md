# Coordination — Codex ⇄ Cowork (Claude)

**The shared git repo is the channel. No human shuttles content.** Both agents read and write files under
`docs/validation/coordination/`; the artifacts they hand off live elsewhere in `docs/validation/` and are
referenced by path, never pasted. Last updated 2026-07-31 by cowork.

## Files in this folder
- `COORDINATION.md` — this file: the plan, lanes, sequence, and the artifact contracts. **Cowork maintains
  it; Codex proposes changes via `CODEX_LOG.md`** (so there is only ever one writer per file → no merge
  conflicts).
- `CODEX_LOG.md` — **Codex writes only.** Status, completed items, questions, handoffs.
- `COWORK_LOG.md` — **Cowork writes only.** Same.

## Commit mechanics (this is what removes the human)
- **Codex is the sole git committer for the repo.** As part of its routine it runs
  `git add -- docs/ && git commit && git push` — this sweeps in the files Cowork *placed* (via
  the desktop bridge) but cannot commit itself (the Cowork VM can't finalise git objects). Named path only;
  never `git add -A`; never touches another lane's code.
- **Cowork never runs git.** It places files into the working tree and records the handoff in
  `COWORK_LOG.md`. Codex's next sweep commits them.
- Net effect: Cowork produces → Codex commits/pushes → both read the repo. David does not move content.

## Check-in cadence (removes the prompting too)
- **Codex:** at the start of each session, `git pull --rebase`, then read `COWORK_LOG.md` before working.
- **Cowork:** reads `CODEX_LOG.md` from the mounted repo when active. Optional full autonomy: a scheduled
  Cowork "coordination sync" task can poll `CODEX_LOG.md`, do the bounded next step, place results, and ping
  David **only** for a decision (see "Decisions reserved for humans"). Off by default; David enables it.

## Handoff entry format (in either LOG)
```
### YYYY-MM-DD HH:MM — <from> → <to or "all">
status | ask | handoff
artifacts: docs/validation/<path>, ...
needs: <what you need from the other side, or "nothing">
```

## Lanes (ownership)
- **codex** — tagger code: measures, per-species hypotheses, selection queues, corpus replay, canonical
  science-run integration, platform seam. Sole git committer.
- **cowork** — study design, review-pack viewer, HITL instrument, teaching sets, analysis, manuscript,
  reference measure algorithms.
- **ccode** — experiment-platform / adaptive_preference; receives the platform seam as findings.
- **david / stephan** — accept/reject reviews, science + scope decisions.

## Sequence
- **Phase 0 — stabilise (DONE/near).** Cowork docs committed (73cb0f94). Codex: push 89fd3737; fix the
  nonportable `/home/claude/...png` test fixtures.
- **Phase 1 — corpus replay (codex).** Full 540-image `corpus_L6` → per-image per-species hypotheses +
  boundary/coverage queues; inspect distributions (saturation, degenerate measures, duplicates, pathological
  rankings). Emit per the **artifact contract** below.
- **Phase 2 — review-pack viewer (cowork).** An accept/reject UI over Phase-1 artifacts for the three lead
  species (`surface_density`, `arrangement_disorder`, `textural_discomfort`).
- **Phase 3 — human review (david/stephan).** Accept / reject / uncertain per example → objections.
- **Phase 4 — science-run integration + platform seam (codex).** Species vector as a versioned science
  artifact (not premature DB columns) + retrieval/negative-control tests; deliver the seam to ccode.
- **Phase 5 — HITL instrument (cowork).** Species-gated study consuming real tagger hypotheses.
- **Phase 6 — run study (stephan + RA).**
- **Parallel:** codex prototypes the improved `arrangement_disorder` (segment large elements → placement
  regularity, AMBER until checked vs the teaching schematic); cowork finishes the manuscript.

## Artifact contract — Phase 1 replay output (so nothing is re-negotiated)
Codex emits, under `docs/validation/review_pack/`:
- `hypotheses_corpusL6.jsonl` — one row per (image, species):
  `{ "image_id", "path", "species", "value", "presence": "present|absent|abstain", "uncertainty",
     "queue": ["boundary"|"coverage"|null], "model_version", "calibrated": false }`
- `queues.json` — the boundary / coverage / (empty) disagreement image lists.
- `replay_manifest.json` — `{ "corpus":"corpus_L6", "n_images", "species":[...], "generated_commit",
     "notes" }` + a manifest hash.
The Cowork review-pack viewer reads exactly these. If Codex must change the shape, note it in `CODEX_LOG.md`
and Cowork updates this contract + the viewer.

## Decisions reserved for humans (ping David, don't guess)
Accept/reject of species/exemplars; redefining or dropping a species; target journal + experiment
feasibility; naming the `model_intake_core` committer; anything that changes scope or the science.
