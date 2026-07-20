# Codex TAX Attack — Disposition (2026-07-20)

**Verdict attacked**: `docs/CODEX_ATTACK_TAX_VERDICT_2026-07-19.md` (Codex attacked HEAD 88e55989). `GATE: FAIL (TAX-0, FC-1, FC-2, CP-1, CP-2, W2-1)`. Every finding engaged; nothing skimmed.

| ID | Codex severity | Disposition |
|----|---------------|-------------|
| TAX-0 | BROKEN | **FIXED**: PEP 366 package bootstrap in all 4 modules; `python3 cnfa_algs/<file>.py` now runs identically to `-m` form. Locked by test_codex_tax_fixes. |
| FC-1/FC-2 | BROKEN | **ENV + DECLARED**: root cause is missing scikit-image on the Mac (sandbox has it — why my runs passed and Codex's didn't). David asked to `pip3 install scikit-image --break-system-packages` (DK-5). compute_failed→UNKNOWN→RED is the CORRECT fail-closed behavior; not softened. |
| FC-3 | DISHONEST | **FIXED**: registry notes for FC/SE now declare the scikit-image runtime dependency explicitly. |
| FC-6 | FRAGILE | **FIXED**: `std_threshold_dn: 2.0` surfaced in abstain extras (both ops). |
| CP-1 | DISHONEST | **FIXED**: all 30 gate constants now in `extras["constants"]` (materials, water, fire, sky, periodicity, coherence, art frame, merge connectivity). Locked by test. |
| CP-2 | BROKEN | **FIXED**: water gate now requires lower-frame position + specular-glint band, with smoothness judged on median-filtered luminance (glints must not fail the gate they license). Codex's blue wall: water 0.73→0.0; a glinted lower-frame pool still reads water 0.43. Locked by test. |
| CP-3 | FRAGILE | **DECLARED**: mirror/art confusion added to failure_modes; real fix is Wave-3 detector + VLM art-content gate (CC-5). |
| CP-4 | FRAGILE | **DECLARED**: bright textured ceiling → junk noted as corpus-refit target in failure_modes. |
| CP-8 | FRAGILE | **FIXED**: `merge_connectivity: 4` declared in extras. |
| CS-3 | FRAGILE | **FIXED**: alpha policy declared and normalized — RGBA input drops alpha at entry in clutter_stack (3 ops) + complexity_partition; RGBA==BGR locked by test. |
| W2-1 | BROKEN | **ACKNOWLEDGED**: the 5 missing wave-2 ops are CC-4 (queued, was attack-gated, now unblocked). Codex correctly flags DO-NOT-REGISTER-YET; they are unregistered. |
| CS-1/2/4/5, CP-5/6/7, FC-4/5/7, W2-2/3, X-1..4 | CLEAN | Recorded. Vendor bytes match wheel; M1′ strict gate holds; boundary/idempotency held under real stage smoke. |
| X-4 / W2-4 | FRAGILE | Standing: full-stage determinism proof and W2.1 coverage wait on the skimage install + corpus. |

**Files changed**: cnfa_algs/{complexity_partition,clutter_stack,faithful_clutter,wave2_geometry}.py, annotation_socket/registry.py (+taxfix), annotation_socket/tests/test_codex_tax_fixes.py (new). All self-tests + new locks PASS in sandbox.

**Still owed on this thread**: DK-5 skimage install, then a Mac re-run of the 3-image stage smoke (expect RED→GREEN/AMBER); CC-4 builds W2.2–W2.5, W2.8.
