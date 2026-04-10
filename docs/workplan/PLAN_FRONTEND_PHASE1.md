# FRONTEND PHASE 1

**Owner:** Engineer B. **Scope:** everything under `/frontend/` required for a credible v1 release against the current contract. **Out of scope:** backend changes, frontend sign-in UI, and optional annotation/polish work that does not block the final smoke flow.

Required v1 coordination note: `docs/workplan/COORDINATION.md` is part of the execution authority for this track. Coordination Tasks C-1, C-1.5, and C-2 are mandatory supporting tasks for the Phase 1 release and are not optional reference material.

## Phase 1 End State

Phase 1 is complete when:

- all four contracted journeys render from the shared API client
- explorer works anonymously against the contract
- workbench, monitor, and admin work against protected routes using a minimal demo-access mechanism backed by pre-issued JWTs
- the frontend handles loading, empty, error, and unauthorized states
- the UI is responsive and accessible at a baseline production level
- the app is deployed and can swap from mocks to the live backend in the joint smoke session

Phase 1 does **not** include:

- frontend sign-in or token-issuance UX
- advanced region-drawing tools
- extra polish work that does not change the contracted user journeys

## Task List

#### Task B-1: Mock API Client and Contract Fixtures
- **Goal:** Single API client used by all four apps, switchable between mock and live.
- **Files to create or modify:** `frontend/shared/src/api-client.js`, `frontend/shared/src/mocks/` (new, one file per endpoint group), `frontend/shared/src/types.ts` (new).
- **Implementation notes:** This task absorbs the deferred post-branch frontend bootstrap check. Use native `fetch` wrapped in typed functions: `explorer.search()`, `workbench.getNext()`, etc. When `import.meta.env.VITE_USE_MOCKS === "true"`, each function returns a Promise that resolves after a 150–400ms randomized delay with fixture data matching the contract. Keep the mock layer inside `frontend/shared/src/api-client.js` and `frontend/shared/src/mocks/`; do not introduce `msw` in Phase 1. Types are shared via TypeScript declaration files in `frontend/shared/src/types.ts`. Add one shared demo-access helper that reads role-scoped bearer tokens from Vite env vars for protected live routes: `VITE_DEMO_ADMIN_JWT`, `VITE_DEMO_TAGGER_JWT`, and `VITE_DEMO_SUPERVISOR_JWT`.
- **Acceptance criteria:** All four apps import from `frontend/shared` and render data without any backend running; flipping `VITE_USE_MOCKS=false` causes them to hit `VITE_API_BASE_URL` instead; the shared API client attaches the correct bearer token for admin, workbench, and monitor requests when the corresponding `VITE_DEMO_*_JWT` env var is present; `npm install && npm run dev` from `frontend/` boots the workspace locally after branching.
- **Depends on:** pre-sprint only.

#### Task B-2: Shared Design System and Layout Primitives
- **Goal:** Consistent visual language across all four apps: header, toasts, buttons, form inputs, loading skeletons, empty states, error banners, trust badges.
- **Files to create or modify:** `frontend/shared/src/components/{Button,Input,Select,Skeleton,EmptyState,ErrorBanner,TrustBadge,Modal,Pagination}.jsx`, `frontend/shared/src/theme.css`, `frontend/shared/preview.html`.
- **Implementation notes:** Build on the existing Tailwind config. `TrustBadge` takes an `evaluation_status` prop from the ML trust envelope and renders a clear pill state. Focus rings must be visible. All color pairs must meet WCAG AA contrast requirements.
- **Acceptance criteria:** `frontend/shared/preview.html` is the only component gallery for this task and renders every shared component in default, loading, error, and disabled states; with the frontend dev server running on `http://127.0.0.1:5173`, `npx @axe-core/cli http://127.0.0.1:5173/preview.html --exit` exits `0` and reports zero `critical` and zero `serious` violations.
- **Depends on:** B-1.

#### Task B-3: Explorer Journey (public browse + detail)
- **Goal:** Search, filter, paginate, and open image detail with science panel and trust badges.
- **Files to create or modify:** `frontend/apps/explorer/src/App.jsx`, `frontend/apps/explorer/src/SearchBar.jsx`, `frontend/apps/explorer/src/ImageGrid.jsx`, `frontend/apps/explorer/src/ImageDetailModal.jsx`.
- **Implementation notes:** URL-sync state via query params. Explorer calls are anonymous and use `GET /v1/explorer/search`. Detail modal shows Overview, Science Features, and Affordances using the trust-envelope shape from the contract. Science feature rows read their display value and `evaluation_status` directly from `science.features[feature_key]`; there is no separate feature-confidence lookup. Loading, empty, error, and success states must all be reachable from mocks.
- **Acceptance criteria:** With mocks enabled, Engineer B can toggle explicit mock behavior flags to produce loading, empty, error, and success states on the explorer route without changing component code; the explorer route issues anonymous requests with no `Authorization` header in browser devtools; opening a URL such as `/ ?q=window&page=2&room_type=living_room` and reloading preserves `q`, `page`, and `room_type` in the UI and in the URL.
- **Depends on:** B-2.

#### Task B-4: Workbench Journey (tagger HITL)
- **Goal:** Fetch next image, present the attribute form with client-side validation, submit, and advance.
- **Files to create or modify:** `frontend/apps/workbench/src/App.jsx`, `frontend/apps/workbench/src/AttributeForm.jsx`, `frontend/apps/workbench/src/KeyboardShortcuts.jsx`.
- **Implementation notes:** Keep Phase 1 focused on the core validation flow. `GET /v1/workbench/next` returns either one assigned image plus one assigned attribute or `{ empty: true }` when no work is currently available. When the response is `{ empty: true }`, the app must render a dedicated empty-queue state with clear copy such as “No items available to label right now,” suppress the attribute form entirely, and provide a visible retry action that re-requests `GET /v1/workbench/next` without a full page reload. When an assignment is present, the client must render the form from `assignment.value_type`, `allowed_values`, `min`, `max`, `step`, and `required`; do not hardcode attribute-specific UI rules in the client. Capture `duration_ms` from `performance.now()`. Use `zod` to validate the assigned value against the returned assignment metadata. Provide keyboard submission and next-item shortcuts for assignment states, but leave advanced region creation to Phase 2. In live mode, workbench uses the shared demo-access helper with `VITE_DEMO_TAGGER_JWT`; if that env var is absent, render a visible “demo access not configured” state instead of failing silently.
- **Acceptance criteria:** Tagging ten mock assignments with keyboard only completes without errors; enum, boolean, and numeric assignment mocks each render the correct form control from assignment metadata; a mock `GET /v1/workbench/next -> { empty: true }` response renders the dedicated empty-queue state, does not render the attribute form, and the retry action triggers another `getNext()` request without a full reload; submitting with a missing or out-of-range value shows inline validation and does not hit the network; with `VITE_USE_MOCKS=false` and `VITE_DEMO_TAGGER_JWT` set, one validation can be submitted successfully using the assigned `attribute_key` from `GET /v1/workbench/next`, and if the live backend returns `{ empty: true }` the app renders the same empty-queue state with no console errors; with `VITE_USE_MOCKS=false` and no tagger demo token configured, the app renders a visible demo-access configuration state.
- **Depends on:** B-2.

#### Task B-5: Monitor Journey (supervisor oversight)
- **Goal:** Velocity chart and inter-rater reliability table.
- **Files to create or modify:** `frontend/apps/monitor/src/App.jsx`, `frontend/apps/monitor/src/VelocityChart.jsx`, `frontend/apps/monitor/src/IRRTable.jsx`.
- **Implementation notes:** Use `recharts` for the velocity line chart. `GET /v1/monitor/irr` returns a list for the table, not a single-attribute detail object. IRR table columns: attribute, IRR, `n_pairs`, and `bin`. Empty state when the response is `{ rows: [] }`. Respect `403` for non-supervisor users and show a dedicated unauthorized screen. In live mode, monitor uses the shared demo-access helper with `VITE_DEMO_SUPERVISOR_JWT`; if that env var is absent, render a visible “demo access not configured” state.
- **Acceptance criteria:** With monitor mocks enabled, clicking each IRR table column header reorders the visible rows; hovering a velocity point shows a tooltip containing both `timestamp` and `count`; a supervisor-role mock user sees populated monitor data while a non-supervisor mock user sees the unauthorized state; a mock response of `{ rows: [] }` renders the contracted empty state with no console errors; with `VITE_USE_MOCKS=false` and no supervisor demo token configured, the app renders a visible demo-access configuration state.
- **Depends on:** B-2.

#### Task B-6: Admin Journey (cockpit)
- **Goal:** Upload images, view budget, and toggle the kill-switch.
- **Files to create or modify:** `frontend/apps/admin/src/App.jsx`, `frontend/apps/admin/src/UploadPanel.jsx`, `frontend/apps/admin/src/BudgetPanel.jsx`, `frontend/apps/admin/src/KillSwitch.jsx`.
- **Implementation notes:** Upload uses drag-and-drop with client-side validation exactly matching the contract: accept only JPEG, PNG, and WebP; reject files larger than 10 MiB; reject batches larger than 200 files before any network call. The upload response is asynchronous and returns `job_id`, `items`, `image_ids`, and `status: "queued"`. Kill-switch is a confirmation-gated toggle because it disables paid models globally. Budget panel derives its progress bar and displayed values from the contracted `GET /v1/admin/budget` response fields `spent_usd`, `limit_usd`, and `remaining_usd`; do not introduce any separate frontend-only budget limit env var. In live mode, admin uses the shared demo-access helper with `VITE_DEMO_ADMIN_JWT`; if that env var is absent, render a visible “demo access not configured” state.
- **Acceptance criteria:** Attempting to upload 201 files, a file larger than 10 MiB, or a non-JPEG/PNG/WebP file shows an inline error before any network call; a successful mock upload returns `status: "queued"` and at least one `image_id`; mocked and live budget responses render correctly from returned `spent_usd`, `limit_usd`, and `remaining_usd` values without requiring any extra frontend-only budget env var; flipping the kill-switch requires explicit confirmation and rolls back on error; a non-admin mock user receives the unauthorized state; with `VITE_USE_MOCKS=false` and no admin demo token configured, the app renders a visible demo-access configuration state.
- **Depends on:** B-2.

#### Task B-7: Responsive Layout and Accessibility Audit
- **Goal:** All four apps usable on 360px mobile through 1920px desktop; WCAG AA baseline met.
- **Files to create or modify:** CSS and JSX across all four apps; `frontend/shared/src/hooks/useBreakpoint.js` (new); `frontend/tests/responsive.spec.ts` (new); `frontend/playwright.config.js` or `frontend/playwright.config.ts` (new or updated).
- **Implementation notes:** Verify against one concrete local topology: a single frontend preview server at `http://127.0.0.1:4173` serving `/`, `/workbench/`, `/monitor/`, and `/admin/`. Every image has alt text; every form input has an associated label; focus order is logical. If Playwright is not already configured under `frontend/`, add the minimum local config needed for `frontend/tests/responsive.spec.ts` to run against that preview server.
- **Acceptance criteria:** With `npm --prefix frontend run build` and `npm --prefix frontend run preview -- --host 127.0.0.1 --port 4173` running, `npx @axe-core/cli` passes with zero `critical` and zero `serious` violations on all four routes, and `npx playwright test frontend/tests/responsive.spec.ts` passes with a 360px viewport and no horizontal scrollbars on any primary screen.
- **Depends on:** B-3, B-4, B-5, B-6.

#### Task B-8a: Frontend Deployment Repo Configuration
- **Goal:** Make the frontend deployable to Vercel from repo config alone.
- **Files to create or modify:** `frontend/vercel.json` (new), `.github/workflows/deploy_frontend.yml` (new), per-app `vite.config.js` build settings.
- **Implementation notes:** This is the agent-executable portion of deployment work. The intended topology is one Vercel project for the whole `frontend/` workspace, producing one build output that serves four route entrypoints at subpaths (`/`, `/workbench`, `/monitor`, `/admin`). Implement this with a single workspace build command and Vercel rewrites in `frontend/vercel.json`; do not create four independent Vercel projects. If Vite config needs changes, those changes must support one workspace build that emits the explorer, workbench, monitor, and admin entrypoints into the same deployable output tree. Keep environment-variable references limited to Vite-supported `VITE_*` names that are expected to be populated in Vercel. For protected live demos, the deploy must support `VITE_DEMO_ADMIN_JWT`, `VITE_DEMO_TAGGER_JWT`, and `VITE_DEMO_SUPERVISOR_JWT` so the three protected apps can be opened without a sign-in flow. Do not treat Vercel project creation, GitHub app installation, or dashboard secret entry as implied repo work.
- **Acceptance criteria:** `test -f frontend/vercel.json && test -f .github/workflows/deploy_frontend.yml` exits `0`; `rg -n '"/workbench"|"/monitor"|"/admin"' frontend/vercel.json` shows explicit subpath rewrites; `rg -n "paths:|frontend/" .github/workflows/deploy_frontend.yml` shows the frontend deploy or preview trigger is scoped to frontend-facing changes; from repo root, `npm --prefix frontend run build` exits `0`; `VITE_USE_MOCKS=true npm --prefix frontend run preview -- --host 127.0.0.1 --port 4173` serves `/`, `/workbench/`, `/monitor/`, and `/admin/` successfully for offline demo verification; a live-mode preview with the three `VITE_DEMO_*_JWT` env vars set reaches the protected routes without requiring a sign-in screen.
- **Depends on:** B-7.

#### Task B-8b: Frontend Platform Provisioning and Live Verification
- **Goal:** Verify the configured frontend deployment against actual Vercel and GitHub platform state.
- **Human-owned prerequisites:** A Vercel project exists and is linked to the repo; Vercel has the required `VITE_*` environment variables populated, including `VITE_DEMO_ADMIN_JWT`, `VITE_DEMO_TAGGER_JWT`, and `VITE_DEMO_SUPERVISOR_JWT`; GitHub-to-Vercel preview integration is enabled; the deployed backend URL from Task A-12b exists for live mode verification.
- **Files to create or modify:** none required beyond Task B-8a unless a repo-config correction is discovered during verification.
- **Implementation notes:** This is the human-verification portion of deployment work. Do not hand this task to an agent as if repo context alone could prove it complete. Use the repo configuration from Task B-8a plus the live Vercel project. If platform verification reveals a repo defect, fix it in a follow-up commit against the same task chain.
- **Acceptance criteria:** A human PR touching `frontend/` produces a Vercel preview URL visible in the PR checks; a human merge to `main` updates the production URL; with `VITE_USE_MOCKS=true` the deployed frontend renders the four routes without contacting the backend, and with `VITE_USE_MOCKS=false` it reaches the deployed backend URL from Task A-12b; the deployed `/workbench`, `/monitor`, and `/admin` routes are usable through the configured demo tokens without any sign-in UI.
- **Depends on:** B-8a.

#### Task B-9: Mock-to-Live Swap (FINAL TASK — joint with Engineer A)
- **Goal:** Replace mocks with the real backend and run the end-to-end smoke test.
- **Files to create or modify:** `frontend/shared/src/api-client.js`, `frontend/.env.production`, `README.md`.
- **Implementation notes:** Done in a joint session with Engineer A. Set `VITE_USE_MOCKS=false` and `VITE_API_BASE_URL` to the deployed backend URL. Explorer remains public; workbench, monitor, and admin use the configured demo-access tokens whose identity and role come from JWT claims. Use `docs/SMOKE_TEST.md` as the runbook.
- **Acceptance criteria:** Using the configured demo-access JWTs for protected routes, both engineers can verify on the deployed site that an authenticated admin uploads one valid image and receives `status: "queued"` plus a created `image_id`, that the image becomes reachable in Explorer within 5 seconds, that the smoke runbook can poll until `science.run_status` becomes `"completed"` within 60 seconds and then observe trust-wrapped science features and trust badges, and that an authenticated supervisor can load the monitor route and see either a populated IRR table or the contracted empty state from `{ rows: [] }`, all without console errors.
- **Depends on:** B-8b, A-12b.
