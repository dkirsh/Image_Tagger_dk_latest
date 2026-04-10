# DOCUMENT 1: SEAM ANALYSIS

**1. Are frontend and backend concerns physically mixed in the same files?**

No — not within individual files. The inventory shows clean file-level separation: Python modules live under `backend/` and React/Vite code lives under `frontend/apps/*`. There is no evidence of JSX imported into Python or of backend logic embedded in frontend components. However, *structural* mixing exists at the repository root: `backend/`, `frontend/`, `scripts/`, `tests/`, `docs/`, `deploy/`, `infra/`, `ai/`, `contracts/`, `governance/`, `archive/`, `scrapping/`, and twenty-odd changelog markdown files all sit at the top level of `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/`, alongside two sibling projects (`TRS_v1.1`, `biophilia-index-main`) that further dilute the boundary.

**2. Is there an identifiable folder boundary between frontend and backend?**

Yes, and it is cleaner than the top-level chaos suggests. `frontend/apps/{admin,explorer,monitor,workbench}` and `frontend/shared/` form a coherent monorepo, and `backend/{api,services,models,schemas,science,database}` is a textbook FastAPI layout. The boundary exists; it is simply buried under archival clutter (the `archive/` subtree contains ~60 historical snapshots from v3.2.x through v3.4.x) and under a single repository containing three independent projects.

**3. Riskiest structural dependency for parallel work**

The single most dangerous artifact is the repository root itself — specifically the coexistence of three projects (`Image_Tagger_3.4.74_vlm_lab_TL_runbook_full`, `TRS_v1.1`, `biophilia-index-main`) with overlapping ML concerns, combined with the massive `archive/` tree. Two engineers pulling from this root will hit merge conflicts on `.gitignore`, CI workflows, root-level READMEs, and — most importantly — will have no shared mental model of "where does new code go?" The second-riskiest item is `backend/science/pipeline.py`, which is the orchestration choke-point touched by both ML validation work (Track A) and any debug-view work that might bleed into Track B.

**4. Recommended scenario**

**Scenario C** — a one-day pre-sprint to establish boundaries and canonical docs only, with no feature work.

**5. Justification**

A full joint restructure (A) is unjustified because the internal structure of `backend/` and `frontend/` is already sound; the problem is scope, not architecture. A solo branch restructure (B) would block both engineers for a full day and create a single reviewer bottleneck. A one-day joint pre-sprint is sufficient because the required moves are boundary-establishing rather than feature-building: promote the active project to repo root, quarantine `archive/` and the sibling projects, commit the contract document, and clean up the canonical docs — after which the clean `backend/`/`frontend/` seam that already exists becomes usable for genuinely parallel work. Environment verification and secret migration are deferred into sprint tasks.

---

# COORDINATION MAP

This file is part of the authoritative v1 execution set, not optional background. Coordination Tasks C-1, C-1.5, and C-2 are mandatory supporting work for the Phase 1 release and must be treated as required inputs to the final smoke session alongside `docs/CONTRACT.md` and the track plan files.

| Sync Point | Track A Deliverable | Track B Dependency |
|---|---|---|
| Pre-sprint (day 0) | `/docs/CONTRACT.md` committed to `main` and phase plans committed | Frontend Phase 1 uses this as the source of truth for mocks and types. |
| Mid-sprint checkpoint | Phase 1 trust-envelope schema finalized in `backend/schemas/science.py` (Task A-7) with `features: Record<string, TrustEnvelope<number>>` and no separate feature-confidence map | Frontend Phase 1 `TrustBadge` rendering and explorer science rows use the exact `evaluation_status` enum values and trust-envelope shape. |
| End-of-sprint joint session | Backend platform verification is complete (Task A-12b) and the smoke runbook is finalized for the reduced Phase 1 scope, with deployment/auth/error handling and smoke-critical integration coverage complete | Frontend Phase 1 mock-to-live swap (Task B-9): explorer stays public; workbench, monitor, and admin swap from mocks to bearer-token auth, with monitor required to handle the contracted live response including `{ rows: [] }`. |

**Three sync points — inside the stated budget of four.** The contract and Phase 1 plan docs absorb what would otherwise have been a dozen coordination moments: endpoint shapes, error formats, protected-vs-public route behavior, pagination, trust-envelope shape, and the v1 end state are all resolved on day zero. Optional Phase 2 work is explicitly non-blocking; if the team later wants Prometheus `/metrics`, full Alembic replacement, seeded monitor IRR data, or backend deploy automation, that work starts only after the Phase 1 milestone is accepted.

**Branching strategy.** Both engineers branch from `main` immediately after the pre-sprint merge. Engineer A works on `track-a-backend-phase1` and Engineer B on `track-b-frontend-phase1`. Within each track, use short-lived feature branches (`track-a/auth-supabase`, `track-b/workbench-form`) that open PRs back into the track branch; Engineer A reviews Engineer B's PRs for contract conformance only (not CSS), and Engineer B reviews Engineer A's PRs for API-shape conformance only (not SQL). Merge order is: backend Phase 1 to `main`, frontend Phase 1 mock-to-live swap in the joint session, then frontend Phase 1 to `main`, then tag the v1 portfolio release. Optional Phase 2 branches, if taken, start only after the v1 tag or by explicit decision to continue after Phase 1 completion.

#### Coordination Task C-1: Deployed Smoke Test Runbook
- **Goal:** Create one shared smoke-test runbook before the B-9 mock-to-live session so deployment verification is copy-pasteable instead of improvised.
- **Files to create or modify:** `docs/SMOKE_TEST.md`.
- **Implementation notes:** Capture the exact deployed smoke sequence for the public explorer route plus the protected admin, workbench, and monitor flows. The runbook must include concrete commands for: `GET $RENDER_URL/health`; opening the deployed explorer UI; submitting one admin upload with a valid admin JWT; submitting one workbench validation with a valid tagger JWT; verifying the image detail appears in explorer with trust badges; and loading the monitor route with a valid supervisor JWT. The monitor step must verify the contracted live behavior for Phase 1, including correct handling of `{ rows: [] }`, and must not depend on ad hoc SQL or an uncommitted seed path. Use placeholder env vars for the deployed base URL and the JWTs.
- **Acceptance criteria:** `docs/SMOKE_TEST.md` is committed and contains at least six numbered steps with copy-pasteable commands or browser URLs, explicitly distinguishes live smoke actions from human-owned platform prerequisites, includes a monitor verification step that accepts either a populated `rows` array or `{ rows: [] }` without console errors, and ends with a final expected outcome that all four deployed journeys complete without console errors.

#### Coordination Task C-1.5: Platform Provisioning Checklist
- **Goal:** Separate human-owned platform setup from agent-executable repo changes so deployment status is verifiable instead of assumed.
- **Owner:** Engineer A for backend platforms, Engineer B for frontend platforms.
- **Files to create or modify:** `docs/SMOKE_TEST.md`.
- **Implementation notes:** Document the minimum live prerequisites for the final session: Render Web Service linked to GitHub, Render PostgreSQL provisioned, Vercel project linked to GitHub, required Render/Vercel env vars populated, Supabase Auth and Storage configured, and the three smoke-role JWT acquisition steps assigned to Engineer A. This checklist is human-owned and must not be phrased as if an agent could prove it from repo context alone.
- **Acceptance criteria:** `docs/SMOKE_TEST.md` contains a short prerequisites section that distinguishes human-owned platform state from repo-owned configuration and names the human owner for backend and frontend platform verification.

#### Coordination Task C-2: JWT Provisioning for Smoke Roles
- **Goal:** Ensure the final smoke session has valid short-lived JWTs for the three protected-role journeys without committing secrets to git.
- **Owner:** Engineer A.
- **Files to create or modify:** `docs/SMOKE_TEST.md`.
- **Implementation notes:** Engineer A creates three dedicated Supabase Auth test identities: one `admin`, one `tagger`, and one `supervisor`, with the required top-level `role` claim present in each JWT. The canonical method is: store each test account email/password in the team password manager, sign in to Supabase Auth shortly before the smoke session to obtain fresh access tokens, and export them locally as `SMOKE_ADMIN_JWT`, `SMOKE_TAGGER_JWT`, and `SMOKE_SUPERVISOR_JWT`. `docs/SMOKE_TEST.md` must reference only those env var names and must never contain raw JWTs, passwords, or refresh tokens. If tokens expire before the session ends, Engineer A re-authenticates and re-exports fresh values.
- **Acceptance criteria:** `docs/SMOKE_TEST.md` contains an ownership note naming Engineer A as the JWT provisioner, lists the three required env vars, and states that raw JWTs and passwords must not be committed, pasted into docs, or stored in the repo.

**The one joint Phase 1 task.** Task B-9 — mock-to-live swap with end-to-end smoke test — is performed by both engineers in one screen-sharing session lasting approximately one hour, using `docs/SMOKE_TEST.md` as the single acceptance runbook and inspectable artifact. That session starts only after both engineers have completed the human platform verification steps from Tasks A-12b and B-8b. For monitor, the Phase 1 acceptance bar is that the deployed route and UI handle the contracted response shape correctly, including the empty state. Phase 2 work does not create additional required sync points unless both engineers explicitly choose to take it on.

---

## References

Brown, L. D., Cai, T. T., & DasGupta, A. (2001). Interval estimation for a binomial proportion. *Statistical Science*, 16(2), 101–133. https://doi.org/10.1214/ss/1009213286

Fowler, M. (2018). *Refactoring: Improving the design of existing code* (2nd ed.). Addison-Wesley.

Landis, J. R., & Koch, G. G. (1977). The measurement of observer agreement for categorical data. *Biometrics*, 33(1), 159–174. https://doi.org/10.2307/2529310

Nygard, M. T. (2018). *Release it! Design and deploy production-ready software* (2nd ed.). Pragmatic Bookshelf.

Raschka, S. (2020). Model evaluation, model selection, and algorithm selection in machine learning. *arXiv Preprint*. https://doi.org/10.48550/arXiv.1811.12808

Richardson, C. (2018). *Microservices patterns: With examples in Java*. Manning.

Sculley, D., Holt, G., Golovin, D., Davydov, E., Phillips, T., Ebner, D., Chaudhary, V., Young, M., Crespo, J.-F., & Dennison, D. (2015). Hidden technical debt in machine learning systems. *Advances in Neural Information Processing Systems*, 28, 2503–2511. https://doi.org/10.5555/2969442.2969519

Sheng, V. S., Provost, F., & Ipeirotis, P. G. (2008). Get another label? Improving data quality and data mining using multiple, noisy labelers. In *Proceedings of the 14th ACM SIGKDD International Conference on Knowledge Discovery and Data Mining* (pp. 614–622). https://doi.org/10.1145/1401890.1401965

Web Content Accessibility Guidelines (WCAG) 2.1. (2018). W3C Recommendation. https://www.w3.org/TR/WCAG21/
