# Open tasks — complexity/clutter program

**Durable backlog · last updated 2026-07-31 (post-Codex status).** `[ ]` open · `[~]` in progress · `[x]`
done · `[⏰]` scheduled. Lanes: **cowork** (Claude) · **codex** (tagger code, one committer) · **ccode**
(experiment-platform) · **david**. Cross-lane work = findings, not edits.

## P0 — repo stabilization (Codex flagged; do first)
- [ ] Commit the untracked `docs/validation/` files (specs, HITL design, teaching sets, backlog, figures) — the immediate repo risk. `commit_docs_validation.sh` provided (named path, rebase-first, docs only — never touches `cnfa_algs/`). **cowork script → david/codex runs**
- [ ] Fix the nonportable test fixtures (tests depending on `/home/claude/...png`). Mine (`run_los.py`, `run_isovist.py`) are cloud-repro scripts, not pytest — mark/relocate so they aren't collected; any real test fixtures are **codex**'s. **cowork+codex**
- [x] Destale this backlog to the 2026-07-31 state. **cowork**

## Tagger measurement (codex — largely DONE)
- [x] Six-species model + naming/polarity settled (`arrangement_disorder`, higher = more disordered). **codex+cowork**
- [x] Per-species hypotheses + 3 selection queues implemented — local commit `89fd3737`; 10 focused + 43 portable tests pass. **codex**
- [x] `surface_density`/`arrangement_disorder`/`variety`/`textural_discomfort` emit **uncalibrated** hypotheses (honest AMBER); `semantic_incongruity`/`concealed_order` abstain. **codex**
- [ ] Push `89fd3737` + integrate into the **canonical science run** as a versioned artifact (not premature DB columns); retrieval + negative-control tests; keep standalone handoff. **codex**
- [ ] Full **540-image `corpus_L6` replay** → hypothesis/boundary/coverage artifacts; inspect for saturation, degenerate measures, duplicates, pathological rankings. **codex**
- [ ] Deliver the **platform seam** to ccode: sample handoff + schema fixture + manifest hash + projection into HITL `identify.tagger_hypothesis`. **codex → ccode**
- [ ] Prototype improved **`arrangement_disorder`** (segment large elements → placement regularity, separate from texture; AMBER until checked vs the teaching schematic). **codex** (cowork has the reference construct)
- [ ] Disagreement queue — needs real human responses (blocked on the study). **codex(ready)/cowork(study)**

## HITL / study (cowork) — sequenced AFTER the review pack validates the species
- [ ] **Review-pack viewer** — an accept/reject interface over Codex's corpus artifacts (low/int/high/uncertain for `surface_density`, `arrangement_disorder`, `textural_discomfort`) for David + Stephan. First exercise of the objection loop. **cowork**
- [ ] Build the species-gated instrument (teach → discriminate → identify → within-species degree → cross-species probes); consume real tagger hypotheses via the platform seam. **cowork → ccode findings**
- [~] Teaching sets drafted (`teaching_sets/`): 3 species real graded exemplars; `arrangement_disorder` rebuilt as top-down schematic; 2 late species pending. **cowork**
- [ ] Curate matched-scene real anchors + build the two late-species sets (`semantic_incongruity` composites, `concealed_order` framing pairs) with Stephan. **cowork+david**

## Manuscript (parallel track — kept open)
- [~] `MANUSCRIPT_perceived_complexity_2026-07-30.md` drafted. **cowork**
- [ ] Zebra wording (static dissociation, not emergence); emergence Mooney before/after figure; Kanizsa→"completion" relabel. **cowork**
- [ ] Plain-language revision to the ATLAS norms (`atlas_shared`); final figure numbering; reference list + typeset PDF/docx. **cowork**
- [ ] David: read draft; pick venue; decide experiment equipment/feasibility. **david**

## Validation harness
- [⏰] Isovist supercover-LOS fix — scheduled `trig_01HPaybGWhbgM414SgVKDnEL`, ~2026-07-31 09:00 PT → will deliver a patch to review. **cowork(scheduled)**

## Housekeeping (david)
- [ ] Run `publish_tagger_main.sh` (commit 3 named docs + fast-forward `main`). **david**
- [ ] Run `rollout_governance.sh`. **david**
- [ ] Name a committer for `model_intake_core`. **david**

## Coordination (with Codex)
- [x] Lanes locked; naming/polarity resolved; tagger hypotheses + queues implemented. Codex's earlier three questions are effectively answered: hypotheses/queues **live in the tagger** (89fd3737); the platform seam (#5 above) is the hand-off format; tagger one-committer = codex. **cowork+codex**
- [ ] Add a one-page README indexing `docs/validation/`. **cowork**

*This file is the source of truth; the in-app task widget is transient.*
