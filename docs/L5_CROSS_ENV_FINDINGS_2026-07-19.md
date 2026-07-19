# L5 CROSS-ENVIRONMENT FINDINGS — Mac (arm64) vs sandbox (x86), M1′ digests
### 2026-07-19 (Cowork/Fable) · data: `M1P_DIGESTS_MAC_v2` vs `M1P_DIGESTS_SANDBOX_v2` (7 smoke images × 8 audit classes)

## Verdict
Strict digest equality FAILS cross-machine (expected); the tolerant comparison (measured, declared
per-stat tolerances) leaves **2 genuine sensitivities, both on the decode-differing image** — and both
are operator-robustness findings, not measurement noise.

## Finding 1 — JPEG decode is platform-dependent (CONFIRMED by fingerprint)
`korridor.jpg` decodes to DIFFERENT PIXELS on the two machines (decoded-sha256 mismatch; file bytes
identical). Legal under the JPEG spec (libjpeg version/SIMD differences). 6 of 7 images decode
identically; korridor's encoding (likely progressive) hits the divergent path.
**Consequence (methodology rule):** the calibration corpus MUST be PNG (decoder-exact). JPEG smoke
images remain fine for same-machine testing.

## Finding 2 — cv2 SIMD float deltas are tiny and now bounded
On byte-identical decodes, only the two Sobel/Canny-dependent classes differ: entropy_norm ≤ 4e-4,
D ≤ 4e-4, R2 ≤ 3e-5, edge counts ≤ 0.15% relative. All were measured and encoded as
`CROSS_ENV_TOL` in `scripts/m1p_cross_env_replay.py` (`--compare-tol`). Policy: **same-machine
verify.py stays strict-digest; cross-machine L5 uses the declared tolerances.** All 12 such
mismatches are within tolerance.

## Finding 3 — the Tier-B geometry chain AMPLIFIES pixel noise (the important one)
On korridor's sub-1% pixel perturbation, the inferred plan changed materially: `cell_m` 0.0956 vs
0.0847 (**13%**), free_cells 6496 vs 6610 (1.75%). The vanishing-point→planes→depth→plan chain has a
branch-point sensitivity — small input shifts cross a threshold and re-scale the whole plan. This is
an independently-measured confirmation of WHY the chain is capped AMBER, and it puts a number on it.
**Action items:** (a) any operator consuming `cell_m` inherits this instability (C01/C29 gate
distances are in metres!); (b) a robustness test (jittered-input stability of the chain) belongs in
the S3 gate; (c) plan-scale estimation should be a calibration target once scale anchors (W2.7) exist.

## Finding 4 — seeded k-means is stable in value but not in path
Palette entropy moved 0.9047→0.9272 (0.0225) across the decode difference — k-means switched basins
on perturbed input despite the fixed seed. Within-machine it is exactly reproducible; the M1 scalar
tolerance (0.02) is just barely exceeded here, so on decode-differing images the palette operator is
the first to disagree. Same corpus-must-be-PNG consequence; also argues for canonicalizing palette
comparison at coarser granularity cross-machine (already done: centers 1dp).

## State
- Mac digests v2: committed `90e450fa` (David). Sandbox v2 + upgraded harness: committed `6109902e`.
- Tolerant compare (`--compare-tol`) added and run: **2 EXCEEDS, both decode-driven** (C1 geometry,
  palette entropy on korridor), 12 within-tol, everything else digest-identical.
- L5 rung status per methodology: **conditionally PASSED for identical-decode inputs with declared
  tolerances; decode-normalization (PNG corpus) required before any GREEN claim.**
