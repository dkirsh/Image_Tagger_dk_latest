# Sweep inventory: New_VR_Platform and Image_Tagger on Tanishq's Mac, 2026-10-04

*Recorded 2026-10-04, updated 2026-10-05 for New_VR_Platform PRs #17 and #18 and Image_Tagger PR #1, by a Claude Code session working for Tanishq Rathore, executing
Priority 2 of David Kirsh's 1 October priorities note ("record first, then push").
This file was written before anything was committed or pushed. The only state changes
made before it were `git fetch` in each clone and a fast-forward of New_VR_Platform's
local `main` ref from `3fe1d50` to `991e2f1` (no checkout, no working-tree change).
Nothing was deleted, reset, rebased or force-pushed.*

## Where the clones are

A search of the home directory found three Git clones of the two repositories and no
worktrees or stashes:

| Clone | Remote | Checked-out branch |
|---|---|---|
| `/Users/tanishqsingh/Documents/GitHub/New_VR_Platform` | `github.com/dkirsh/New_VR_Platform` | `tanishq/production-loop` |
| `/Users/tanishqsingh/Documents/GitHub/Image_Tagger_dk_latest` | `github.com/dkirsh/Image_Tagger_dk_latest` | `tanishq/loop-comparator` |
| `/Users/tanishqsingh/Documents/GitHub/Image_Tagger_dk_latest/Image_Tagger_dk_latest_prof_latest` | same Image_Tagger remote, nested inside the clone above | `main` |

`git worktree list` shows only the main worktree in each, and `git stash list` is
empty in all three. There is no clone of Article_Finder on this machine; the nearest
thing is `Article_Eater`, a different repository, which this sweep did not touch.

## Every branch, and whether it is pushed

Push state was checked against the remote itself (`git ls-remote`), because the
Image_Tagger clone's fetch refspec tracks only `main` and would otherwise make
pushed branches look unpushed.

| Repo | Branch | Local tip | On remote? | What remains incomplete |
|---|---|---|---|---|
| New_VR_Platform | `tanishq/production-loop` | `d22f455` | yes, identical | Holds the only copy of the real producer (`production_loop/emit_render_packet.py`, commit `fb3a873`); it has not been ported to `main`, which is S15. |
| New_VR_Platform | `main` | `991e2f1` | yes, identical (after fast-forward) | Not our work. |
| Image_Tagger | `tanishq/loop-comparator` | `89cc5150` | yes, identical | Fully merged into `origin/main`; `loop/RUN_INSTRUCTIONS.md` there still drives the stale producer branch, which is E-RUN-1's open revision. |
| Image_Tagger | `tanishq/loop-decomposition` | `ad6c8037` | yes, identical | Fully merged into `origin/main`; nothing outstanding. |
| Image_Tagger | `tanishq-s1-direct-stats-local` | `3ecbc399` | yes, identical | One commit not on `main` ("Add S1 direct stats validation checkpoint", 2026-07-21); this is the July COMP-CORRECT S1, not VR seed S1, and whether it should merge is unrecorded. |
| Image_Tagger | `tanishq-sprint-a-corpus-db-v2` | `1d3d4373` | yes, identical | Fully merged into `origin/main`. |
| Image_Tagger | `tanishq-sprint-a-corpus-db` | `b7bbf8b4` | no branch of that name | Points at an old `main` commit already in `origin/main`; it carries no unique work. |
| Image_Tagger | `main` (local) | `b7bbf8b4` | behind `origin/main` (`3a2d9b72`) | Not our work. |
| Image_Tagger nested clone | `main` | `7597047a` | the commit is on the remote, in `origin/main`'s history; remote `main` is now `3a2d9b72` | A clone of 2026-07-11 `main`, not ignored by the outer repository; it holds the nine uncommitted files listed below. |

## Uncommitted work in the working trees

| Repo | `git status --short` | What it is |
|---|---|---|
| New_VR_Platform | `?? reference/` | `reference/books/MANIFEST.md` only; no PDFs are present. Under `lanes.json` the path belongs to Stephan's lane, and the manifest goes to David by email rather than as a commit. |
| Image_Tagger | `git status` did not finish in 30 minutes (the iCloud-backed scan stall). A metadata-only substitute found no file modified since the index was written on 2026-09-09 16:12, the moment of the last commit (`89cc5150`), apart from the nested clone, which shows up untracked. | Clean, apart from the nested clone directory. |
| Image_Tagger nested clone | nine untracked files under `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/`, all dated 2026-07-21: `datasets/signage_seed/signage_taxonomy_seed_2026-07-21.csv`; `docs/SIGNAGE_ANNOTATION_CONTRACT_…`, `docs/S2_SIGNAGE_AND_SOCIAL_SPRINT_CONTRACT_…`, `docs/SOCIAL_INTERACTION_ATTRIBUTE_TAXONOMY_…` (`.md`); `scripts/validate_signage_taxonomy_seed.py`; `reports/OPEN_SOURCE_VISUAL_PROCESSING_SURVEY_DRAFT_…md`, `reports/SIGNAGE_TAXONOMY_SEED_VALIDATION_…txt`, `reports/PROFESSOR_LATEST_ACTIVE_CONCEPT_SEARCH_…txt`, `reports/PROFESSOR_REVISION_DEEP_REVIEW_DRAFT_…md`. None appears anywhere in Image_Tagger's history. | Tanishq's July signage and social-interaction sprint drafts (the contract says "Owner: Tanishq", status Proposed; the review is "in progress"). This is partial work. A secret-pattern scan of all nine files found nothing, and on 2026-10-05, with Tanishq's approval, they were committed unchanged as `9bdbca61` on the new branch `tanishq/signage-social-wip-2026-07-21` (parent `7597047a`, the commit they were written against) and pushed; the commit message labels them PARTIAL. The working-tree files were left in place. |

## Appendix B2, item by item

Each item was searched for in four places: New_VR_Platform `origin/main` and every
remote branch; Image_Tagger `origin/main` and every local branch; the full history of
both repositories, including files later deleted (`git log --all --diff-filter=A`); and
the working trees of both clones and `_control` on disk. "Nothing exists" below means
all four searches came back empty, and it is stated separately for each item.

| Item | Pushed hash, or the statement that nothing exists | Where it lives |
|---|---|---|
| S4 window knowledge card | **Nothing exists.** No card file has ever been committed in either repository or found on disk. | — |
| S4 generator | **Nothing exists.** No generator code has ever been committed or found on disk. | — |
| S5 ingest normalizer | **The normalizer itself was not found.** The only S5-related artifact is the normalized exemplar asset, committed by the Fable lane as SEED-5 (`3778e06`), not by us. | `New_VR_Platform/students/viewer/assets_seed/Sofa_01/` on `main` |
| S7 embedding-index seed | **Nothing found.** The queue calls it "seeded, ~500 images" and S11 records CLIP encoding verified on this Mac on 2026-09-09, but no index, embedding file, or indexing script exists in either repository's history or on disk. | not located; the queue's PARTIAL status is unsupported by any file found here |
| S8 ticket-flow skeleton | **Nothing found.** The queue says "exercised once"; no ticket-flow code or run record exists in either repository's history or on disk. | not located |
| S14 source-test gate | **Nothing of ours exists, and none is now needed for the gate.** Another lane restored the gate on 2026-09-30 in PR #3 (`71c8863`, merged as `f2a320a`), removing three unused imports of never-written constructors and skipping the one test of the other three. PR #17 (`claude/s14-record-2026-10-04`, tip `8ea89af`, 2026-10-04, open) records it as Done. The six tree constructors remain owed to Tanishq and Stephan as non-blocking work. An unrelated branch, `codex/s14-hitl` (`f34c06e`), adds an S14 forced-choice HITL contract. | PR #17 on New_VR_Platform |
| S15 / E-PROD-1 producer port | **Nothing of ours beyond the stale branch; a port drafted for Tanishq exists.** The producer exists at `fb3a873` on `origin/tanishq/production-loop` (tip `d22f455`). PR #18 (`claude/s15-producer-2026-10-04`, tip `cf6c134`, 2026-10-04, draft) brings the file to `main` byte-identical (blob `6d80119d`), with five contract tests and a contract document. It awaits Tanishq's ratification; it is not merged. | PR #18 on New_VR_Platform |
| E-RUN-1 revision | **Nothing of ours since `89cc5150`; a revision drafted by another lane exists.** Image_Tagger PR #1 (`claude/run-instructions-main-producer-2026-10-04`, tip `9a906a3c`, 2026-10-04, draft) points the runbook at the producer on New_VR_Platform `main` and documents exit 3 and the refused-run directory rule. It awaits S15. | PR #1 on Image_Tagger_dk_latest |
| Clean-clone execution logs, hashes, timings, reproduction notes | **Nothing exists.** No run record, timing log, or reproduction note was found in either repository's history or on disk. | — |

## Files to send David by email (not to commit)

- **Books manifest.** `/Users/tanishqsingh/Documents/GitHub/New_VR_Platform/reference/books/MANIFEST.md`
  (untracked). A byte-identical copy is at `/Users/tanishqsingh/Downloads/MANIFEST.md`
  (4,096 bytes, dated 6 September).
- **`tanishq_sprint_claims_2026-09-07.patch`: missing.** The 7 September session wrote
  it to that session's temporary scratchpad,
  `/private/tmp/claude-501/-Users-tanishqsingh-Documents-GitHub-Image-Tagger-dk-latest/8cd631b1-39a2-4cdc-b835-3142e078b9af/scratchpad/`.
  That directory no longer exists, and searches of the home directory, `/private/tmp`, `/private/var/folders`
  and both repositories' full histories find no copy. The 7 September transcript says
  the patch was 81 lines and held edits to `students/SPRINTS.md` and
  `students/TASK_QUEUE.md`, refused by the lane guard. It would have to be
  reconstructed from that transcript, and the reconstruction would need checking
  against today's queue, which has changed since then.
