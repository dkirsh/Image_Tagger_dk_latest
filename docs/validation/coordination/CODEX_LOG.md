# CODEX_LOG — Codex writes only

Cowork reads this when active. Append entries newest-last using the handoff format in `COORDINATION.md`.
Use this file to: report status, hand off artifacts (by path), ask questions, and propose changes to
`COORDINATION.md` (Cowork will apply them).

<!-- Codex: first entry goes below -->

### 2026-07-31 11:05 PDT — codex → all
status: Phase 1 corpus replay STARTED; current branch is synchronized with origin and commit `89fd3737`
is already remote as an ancestor of `73cb0f94`.
ask: propose replacing blanket `git add -- docs/` with exact paths declared in each COWORK_LOG handoff;
the present worktree contains untracked docs without recorded provenance.
handoff: pending. Replay scope is all 540 image files under `corpus_L6`; `manifest.csv` has 538 rows, so
the two filesystem-only images will be included and named in the replay manifest. Corpus-relative paths
will be the unique image IDs, preserving all 540 items even if content duplicates exist.
artifacts: pending under `docs/validation/review_pack/`
needs: nothing; cowork can build the contract-fixture viewer in parallel.

### 2026-07-31 11:26 PDT — codex → cowork
status: Phase 1 corpus replay DONE on all 540 filesystem images; exact viewer contract verified. The
portable fixture repair is also DONE and the final complete annotation suite is green: 53 passed in 120.96s.
handoff: 3,240 flattened image/species rows, 216 boundary selections, 105 coverage selections, and an
empty disagreement queue (no human rows yet). Producer commit is
`11539c57883b543867f38424ec35034053dc6b05`; model is `complexity-species-proxy-v2`.
artifacts:
  - `docs/validation/review_pack/hypotheses_corpusL6.jsonl`
    sha256 `84afa42f7f6d3dc267d511de1c19cf4ad29a6f099df2b077939200e01b46f469`
  - `docs/validation/review_pack/queues.json`
    sha256 `a0c798fd8ffc219ee150d8d2b5874a9ba334e40633b652a7b67dd53f2e23fda9`
  - `docs/validation/review_pack/replay_manifest.json`
    file sha256 `c15fc0d5e98a7e752acb21b2fa9e58545c7ff91009d8f0fb77c6bdc9340e3375`;
    canonical manifest hash `23a5839e6d786185d2ee6fb0d286df1359a20ce74854f1b31a4b8e444ed9b413`
findings:
  - First full replay caught a real defect: `textural_discomfort` was 1.0 for 540/540 because an already
    normalized spectral fraction was divided by 0.20. Fixed, negatively tested, and model bumped to v2.
    Corrected range is 0.315106–0.588158 with 458 unique values at 6dp.
  - `surface_density` is well spread (0.078641–1.0; 249 absent / 291 present).
  - Continuous `arrangement_disorder` and `variety` values vary, but provisional presence is highly
    imbalanced: 534/540 and 531/540 present respectively. Treat presence as a hypothesis needing human
    calibration, not as a label.
  - 78 duplicate-content groups: 77 are source-image ↔ generated A-base reuse; one is pair-only and is
    flagged for review. No deletion or corpus mutation was performed.
  - `manifest.csv` lists 538; both filesystem-only images are included and named in the manifest.
  - `semantic_incongruity` and `concealed_order` abstain for all 540 as required.
needs: load the real artifacts into `viewer.html`; report schema/parser failures and suspicious examples in
`COWORK_LOG.md`, then prepare David/Stephan's lead-three review.

### 2026-07-31 12:17 PDT — codex → cowork
status: Improved `arrangement_disorder` prototype and adversarial replay DONE, but remains AMBER. The
canonical v2 review pack was deliberately preserved; v3 lives under an experimental subdirectory.
handoff: v3 replaces coarse PNG compressibility with repeated-large-region placement regularity and keeps
the old value only as a legacy diagnostic. It abstains on texture-dominated images and fewer than four
repeated regions. Fail-first controls now pass; the teaching schematic orders low 0.001304 < intermediate
0.243817 < high 0.351673, while intentional clusters score 0.226538. Full annotation suite: 55 passed.
The 540-image replay is deterministic (3/3 files byte-identical): 328 measured, 139 insufficient-region
abstentions, 73 texture abstentions; flattened result 128 absent / 200 present / 212 abstain, versus v2's
6 absent / 534 present. Do not treat this improvement as validation.
findings: visual and invariance attacks reject promotion. A regimented conference room scores 0.829909
because perspective corrupts apparent spacing/orientation. Across 82 geometry-preserving A/B photometric
pairs, absolute score difference is mean 0.0542, p95 0.2221, max 0.4581, with 6 evidence-status flips.
The audit pins a next gate: semantic furniture instances + perspective normalization; no pair status flips,
p95 <= 0.10, max <= 0.20; then matched-photo David/Stephan review.
artifacts:
  - `docs/validation/review_pack/experimental_arrangement_v3/ARRANGEMENT_DISORDER_V3_AUDIT.md`
  - `docs/validation/review_pack/experimental_arrangement_v3/hypotheses_corpusL6.jsonl`
    sha256 `4e0bcb03647e243c03148df20c302b859002ef5ac55bbb8e880460618e759881`
  - `docs/validation/review_pack/experimental_arrangement_v3/queues.json`
    sha256 `af486ed9ffc0a61561fc3550e5ad21c610cdac62eb17eb42b64460ad4de2a4db`
  - `docs/validation/review_pack/experimental_arrangement_v3/replay_manifest.json`
    file sha256 `f35250fc449e71c8051dfd420d990753cec036405508b5e4743b781ebedf470d`
needs: cowork should keep the viewer on canonical v2 unless explicitly adding an `experimental_v3` mode;
please preserve the AMBER warning and surface the perspective/photometric objections if that mode is added.
