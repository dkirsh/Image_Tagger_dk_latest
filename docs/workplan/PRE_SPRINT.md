# DOCUMENT 2: PRE_SPRINT.md

**Duration:** 1 full working day (target 6-8 hours), both engineers pairing for structural changes and then splitting for review/cleanup.

## Purpose

This pre-sprint is a setup phase, not a delivery phase. Its purpose is to establish an unambiguous repo boundary, commit the shared contract, and clean up the top-level docs so Track A and Track B can branch from a stable baseline.

## Explicit Non-Goals

- Do not perform per-laptop environment verification here.
- Do not migrate secrets or production credentials here.
- Do not debug runtime issues beyond import/path fixes required by the repo move.
- Do not start feature implementation for either track here.

## Target Folder Structure

```
/                              # repo root — was Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/
├── backend/                   # FastAPI application (Track A territory)
│   ├── api/                   # versioned routers (v1_*)
│   ├── services/              # business logic layer
│   ├── models/                # SQLAlchemy ORM models
│   ├── schemas/               # Pydantic request/response schemas
│   ├── science/               # ML pipeline (math, vision, semantics, spatial)
│   │   └── data/              # model weights and reference data (tracked)
│   ├── database/              # engine, session, migrations
│   ├── scripts/               # backend-local ops scripts
│   ├── tests/                 # backend unit + integration tests
│   └── main.py                # FastAPI entrypoint
├── frontend/                  # React monorepo (Track B territory)
│   ├── apps/
│   │   ├── explorer/          # public browse journey
│   │   ├── workbench/         # tagger journey (HITL)
│   │   ├── monitor/           # supervisor journey
│   │   └── admin/             # admin cockpit journey
│   ├── shared/                # shared components and API client
│   └── package.json           # npm workspace root
├── docs/                      # canonical documentation (both tracks read)
│   ├── CONTRACT.md            # shared API + schema contract (THIS pre-sprint)
│   ├── ML_EVALUATION.md       # to be written in Track A
│   ├── ARCHITECTURE.md        # promoted from README_v3.md
│   └── workplan/             # canonical execution plans (not archival)
│       ├── COORDINATION.md
│       ├── PRE_SPRINT.md
│       ├── PLAN_BACKEND_PHASE1.md
│       ├── PLAN_BACKEND_PHASE2.md
│       ├── PLAN_FRONTEND_PHASE1.md
│       └── PLAN_FRONTEND_PHASE2.md
├── deploy/                    # Dockerfiles, compose, nginx, host configs
├── .github/workflows/         # CI — one workflow per track plus integration
├── _archive/                  # EVERYTHING historical — root-level, git-tracked, frozen
│   ├── image_tagger_archive/  # old archive/ tree moved wholesale
│   ├── trs_v1_1/              # sibling project, out of scope
│   ├── biophilia_index/       # sibling project, out of scope
│   ├── changelogs/            # CHANGELOG_v3.4.*.md files
│   └── scrapping/             # exploratory scraping notebooks
├── .env.example               # all env vars documented, no values
├── .gitignore
└── README.md                  # short pointer to docs/ARCHITECTURE.md
```

`docs/workplan/` remains part of the canonical post-restructure layout and is not archival material.

## Shared Contract Reference

Use [CONTRACT.md](/Users/taggertsmith/Documents/GitHub/Image_Analyzer/image-tagger/docs/CONTRACT.md) as the only canonical source for:
- v1 endpoint shapes and example payloads
- auth rules and error-response structure
- shared TypeScript/Pydantic types
- ML trust-envelope fields
- workbench assignment metadata and pagination limits
- upload validation rules and post-upload processing semantics
- environment variable names

Do not duplicate or edit contract details in this file. If the contract changes, update `docs/CONTRACT.md` and treat this pre-sprint document as a consumer of that source of truth. This includes admin upload MIME rules, file-size and batch-size limits, and the asynchronous upload-to-explorer processing behavior used by the smoke runbook.

## Root Collision Resolution

When promoting `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/` to repo root, use the table below as the canonical collision policy. Do not resolve these paths ad hoc during the move.

| Path | Decision | Canonical rule | Verification |
|---|---|---|---|
| `docs/` | merge, then verify with command X | Keep the current outer `docs/` tree as the canonical execution-doc location. Do not overwrite `docs/CONTRACT.md`, `docs/ENGINEERING_BRIEF.md`, `docs/SMOKE_TEST.md`, or anything under `docs/workplan/` with the inner project copy. Preserve the inner project's historical docs under `_archive/image_tagger_archive/docs/` when the old project tree is moved, and only mine `README_v3.md` for `docs/ARCHITECTURE.md` as already specified below. | `test -f docs/CONTRACT.md && test -f docs/ENGINEERING_BRIEF.md && test -f docs/SMOKE_TEST.md && test -f docs/workplan/PRE_SPRINT.md && test -d _archive/image_tagger_archive/docs` |
| `.github/` | keep inner copy | There is no competing outer `.github/` tree. Promote the active project's `.github/` directory to repo root as the canonical CI/workflow location. | `test -d .github/workflows && test -f .github/workflows/ci.yml` |
| `README*` | keep inner copy | There is no competing outer `README*` at repo root. Promote the active project's root readme material to repo root, then rewrite repo-root `README.md` in Phase 2 of this pre-sprint as the short canonical pointer doc. `README_v3.md` remains source material for `docs/ARCHITECTURE.md`, not the final canonical root README. | `find . -maxdepth 1 \\( -name 'README*' -o -name 'README.md' \\) | sort` |
| `.gitignore` | keep outer copy | Keep the current outer `.gitignore` as canonical because it already reflects the outer repo boundary and ignores agent-generated files at the actual repository root. If inner-project ignore rules are needed, merge them deliberately in a follow-up diff rather than replacing the outer file during the move. | `test -f .gitignore && rg -n '^\\.DS_Store$|^\\.claude/$' .gitignore` |
| `.DS_Store` | merge, then verify with command X | Treat both outer and inner `.DS_Store` files as disposable generated junk. Do not promote either one into the canonical root tree. Delete them during the move. | `find . -name '.DS_Store'` returns no matches |
| `.pytest_cache/` | merge, then verify with command X | Treat both cache directories as disposable generated artifacts. Do not promote either one into the canonical root tree. Delete them during the move and let tooling recreate them locally if needed. | `find . -name '.pytest_cache' -type d` returns no matches |

## Pre-Sprint Sequence

### Phase 1: Boundary Establishment (paired, Engineer A driving)

- [ ] Create `_archive/` at repo root and move the entire `archive/`, `scrapping/`, root-level `CHANGELOG_v3.4.*.md` files, `deconcat_v3_3.py`, and the two sibling projects (`TRS_v1.1`, `biophilia-index-main`) into it. **Done when:** from repo root, `find . -maxdepth 1 \( -name 'archive' -o -name 'scrapping' -o -name 'TRS_v1.1' -o -name 'biophilia-index-main' -o -name 'CHANGELOG_v3.4.*.md' -o -name 'deconcat_v3_3.py' \)` returns no top-level matches outside `_archive/`, and `find _archive -maxdepth 2 \( -name 'archive' -o -name 'scrapping' -o -name 'TRS_v1.1' -o -name 'biophilia-index-main' \)` shows the moved material.
- [ ] Promote the active project up one level: move contents of `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/` to repo root, resolving collisions exactly as specified in the `Root Collision Resolution` table above rather than by judgment call during the move. **Done when:** from repo root, `test -f backend/main.py && test -f frontend/package.json && test -d deploy && test -d .github/workflows` exits `0`, `test -f docs/CONTRACT.md && test -f docs/workplan/PRE_SPRINT.md` exits `0`, and `find . -maxdepth 1 -name 'Image_Tagger_3.4.74_vlm_lab_TL_runbook_full'` returns no directory containing active source files.
- [ ] Update `backend/main.py`, any `sys.path` hacks, and `pyproject.toml`/`requirements-install.txt` references that assumed the old nested root. **Done when:** from repo root, `python -c "import backend.main"` exits `0`, and `rg -n "Image_Tagger_3.4.74_vlm_lab_TL_runbook_full|sys\\.path" backend/ pyproject.toml requirements-install.txt` returns only intentional remaining references documented in the PR notes or no matches.

### Phase 2: Canonical Docs (paired, Engineer B driving)

- [ ] Write and commit `/docs/CONTRACT.md` as the canonical source of truth for API shapes, upload policy, and post-upload processing behavior. **Done when:** file is committed on `main`.
- [ ] Create `docs/ARCHITECTURE.md` using `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/README_v3.md` as the primary source file to mine before the move, plus the target folder structure in this document as the canonical post-restructure layout. The file must contain exactly these headings in order: `# Architecture`, `## Purpose`, `## Repo Boundary`, `## Backend`, `## Frontend`, `## Shared Contracts`, `## Deployment Surface`, `## Out-of-Scope Archived Material`. Keep it to 120 lines or fewer and do not restate endpoint-level contract details already owned by `docs/CONTRACT.md`. **Done when:** `test -f docs/ARCHITECTURE.md && wc -l docs/ARCHITECTURE.md` reports at most `120`, and `rg -n "^# Architecture$|^## Purpose$|^## Repo Boundary$|^## Backend$|^## Frontend$|^## Shared Contracts$|^## Deployment Surface$|^## Out-of-Scope Archived Material$" docs/ARCHITECTURE.md` returns all eight required headings.
- [ ] Rewrite repo-root `README.md` as a short pointer (≤ 20 lines) to `docs/ARCHITECTURE.md`, `docs/CONTRACT.md`, and the four phase plan docs under `docs/workplan/`. **Done when:** `test -f README.md && wc -l README.md` reports at most `20`, and `rg -n "docs/ARCHITECTURE\\.md|docs/CONTRACT\\.md|docs/workplan/" README.md` returns matches for all three references.

### Phase 3: Branch Readiness (paired review, both engineers)

- [ ] Review the target folder structure, contract, and branching model together and resolve any path-level ambiguity before branching. **Done when:** the pairing session adds a short checklist to the merge PR description or commit message naming the canonical paths for `backend/`, `frontend/`, `docs/`, `deploy/`, and `_archive/`, and both engineers confirm those exact paths before creating branches.
- [ ] Create the two Phase 1 track branches from post-pre-sprint `main`: `track-a-backend-phase1` and `track-b-frontend-phase1`. **Done when:** `git branch --list 'track-a-backend-phase1' 'track-b-frontend-phase1'` shows both local branches and `git ls-remote --heads origin track-a-backend-phase1 track-b-frontend-phase1` shows both remote heads.

## Deferred To Sprint Tasks

- Secret externalization and `.env.example` creation move to Track A Task A-1. Use the environment variable list already committed in `/docs/CONTRACT.md` as the baseline source of names.
- Docker credential cleanup moves to Track A Task A-1.
- Per-laptop clone/bootstrap verification moves to the first execution steps of Track A and Track B after branching.

## Exit Criteria

1. `git log --oneline -1` on `main` shows the pre-sprint merge commit and both engineers have pulled it.
2. `/docs/CONTRACT.md` exists on `main` and both engineers have read it end to end.
3. `docs/ARCHITECTURE.md` exists on `main`, and repo-root `README.md` points to it and the contract.
4. `ls` at repo root shows no stray changelogs, no sibling projects, and no `archive/` outside `_archive/`.
5. Two feature branches exist: `track-a-backend-phase1` and `track-b-frontend-phase1`, both branched from the post-pre-sprint `main`.

---
