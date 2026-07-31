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
**Explicit allowlist, not a blanket sweep.** (Revised 2026-07-31 after Codex found untracked docs a
blanket `docs/` sweep would wrongly capture.) A directory sweep is unsafe because the worktree can hold
untracked files not placed by cowork; Codex commits *only* the paths cowork names.
- **Codex is the sole git committer.** Per `COWORK_LOG.md` handoff it runs, for the paths in that handoff's
  `commit_allowlist` and no others:
  1. `git add --` <each allowlist entry>        — exact files/dirs only
  2. `git diff --cached --check`                — whitespace / conflict-marker guard
  3. `git diff --cached --name-only`            — confirm the staged set matches the allowlist; **abort and
     log in CODEX_LOG.md if it differs** (extra path staged, or an allowlisted path missing)
  4. `git commit && git push`
  Never `git add -A`; never `git add -- docs/`; never stage a path not on the allowlist; never touch another
  lane's code or the generated Phase-1 artifacts.
- **Cowork never runs git.** It places files via the desktop bridge and records each placement in
  `COWORK_LOG.md` with a `commit_allowlist:` block naming exactly the paths it placed.
- Net effect: Cowork produces + names the paths → Codex stages exactly those, verifies, commits/pushes →
  both read the repo. David moves nothing.

## Check-in cadence (removes the prompting too)
- **Codex:** at the start of each session, `git pull --rebase`, then read `COWORK_LOG.md` before working.
- **Cowork:** reads `CODEX_LOG.md` from the mounted repo when active. Optional full autonomy: a scheduled
  Cowork "coordination sync" task can poll `CODEX_LOG.md`, do the bounded next step, place results, and ping
  David **only** for a decision (see "Decisions reserved for humans"). Off by default; David enables it.

## Handoff entry format (in either LOG)
```
### YYYY-MM-DD HH:MM — <from> → <to or "all">
status | ask | handoff
artifacts: docs/<path>, ...
commit_allowlist:
  - docs/exact/path.md
  - docs/exact/dir/        # a dir entry means "everything cowork placed under here this handoff"
needs: <what you need from the other side, or "nothing">
```
Every cowork placement handoff MUST carry a `commit_allowlist`. No allowlist → Codex commits nothing from
that entry.

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
*Clarified 2026-07-31 with Codex against the real corpus.* Scope = **all 540 image files** in `corpus_L6`
(the filesystem, not the manifest). `manifest.csv` lists 538; the two filesystem-only images are named in
`replay_manifest.json` (see below), never silently dropped.

Codex emits, under `docs/validation/review_pack/`:
- `hypotheses_corpusL6.jsonl` — **540 images × 6 species = 3,240 rows**, one row per (image, species):
  `{ "image_id", "path", "species", "value", "presence": "present|absent|abstain", "uncertainty",
     "queue": [ ... ], "model_version", "calibrated": false }`
  - `image_id` **and** `path` are both the **corpus-relative path** (the unique ID).
  - `value` = provisional severity score (uncalibrated); `presence` ∈ `present|absent|abstain`; the **late
    species abstain** (they need the observer/HITL component, not image stats). `calibrated` is always `false`
    in Phase 1.
  - `queue` is an **array** holding zero or more of `"boundary"`, `"coverage"`, `"disagreement"` (empty `[]`
    if none). Not a scalar, not `null`.
- `queues.json` — the boundary / coverage / (empty) disagreement image lists.
- `replay_manifest.json` — `{ "corpus":"corpus_L6", "n_images": 540, "n_manifest_rows": 538,
     "filesystem_only": ["interiors/mit_indoor67_airport_inside_air_8eed507ec6_airport_inside.png",
     "interiors/mit_indoor67_children_room_pipp_d1f487ce65_children_room.png"], "species":[...],
     "generated_commit", "notes", "manifest_hash" }`.
  - `manifest_hash` = **SHA-256 of the canonical manifest content excluding the `manifest_hash` field itself.**
The Cowork review-pack viewer reads exactly these; a synthetic fixture matching this shape lives at
`docs/validation/review_pack/_fixture/` so the viewer is testable before the real replay lands. If Codex must
change the shape, note it in `CODEX_LOG.md` and Cowork updates this contract + the viewer.

## Decisions reserved for humans (ping David, don't guess)
Accept/reject of species/exemplars; redefining or dropping a species; target journal + experiment
feasibility; naming the `model_intake_core` committer; anything that changes scope or the science.
