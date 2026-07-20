# 3-image stage smoke — skimage-present re-run (2026-07-20)

**Purpose**: close the DK-5/FC-1/FC-2 thread. Codex's TAX attack RED'd the faithful FC/SE because
scikit-image was missing on the Mac (compute_failed -> UNKNOWN -> RED, the correct fail-closed
behavior). This re-run confirms that WITH scikit-image present the RED verdicts clear.

**Where run (honest scope)**: the Cowork cloud sandbox, on the branch working tree at commit
`6d2d20a6` (the reconciled reliable-A batch), with scikit-image installed. The device VM that
bridges the Mac has neither scikit-image nor network, so the smoke cannot run there; the sandbox
runtime is equivalent to the Mac post-`pip install scikit-image` for the purpose of this thread
(same import resolves, same code path). Cross-environment EXACT digest replay (Mac vs sandbox,
L5) remains a separately-owed item and is NOT claimed here.

**Env**: python 3.11 · numpy 2.4.4 · opencv 4.13.0 · scipy 1.17.1 · scikit-image 0.26.0.
**Images**: 3 real interiors from `Example Images/` (originalfile...4785.jpg, UPCycle-Gensler-5,
Industrial-open-concept-office...).

## Result — RED verdicts cleared

(a) Every real unit: **tier=AMBER, scored=42/42 applicable, abstained=19, unknown=0,
    replayed=True, problems=[]**. The four clutter/fluency members that depend on the
    skimage-backed faithful stack — `grayscale_gabor_entropy_proxy`, `local_congestion_proxy`,
    `feature_congestion`, `subband_entropy` — all reach **AMBER, not RED**. No unit has any
    UNKNOWN/compute_failed predicate. This is the exact RED->cleared signal owed on the thread.

(b) score_layout **negative control**: seeded defaulted-C14 + constant-C8 record -> **RED,
    REJECTED**, absent from accepted/. The fabrication cannot recur structurally.

(c) **Idempotency**: second worker run does zero work (all 3 skipped by content address).
    Worker writes to control.jsonl and accepted/ DENIED (BoundaryError) — the [W:] boundary holds.

Units land AMBER (not GREEN) because they contain AMBER-tier predicates by rule (honest FC/SE
proxies + Tier-B inferred-plan geometry). AMBER awaits the not-equal-mind inference judge
(advisory); that is the designed state, not a defect.

## Disposition of the Codex TAX FC findings
- **FC-1 / FC-2** (faithful FC/SE compute_failed -> RED): **CLEARED** — root cause was missing
  scikit-image; with it present, both compute and land AMBER, unknown=0.
- The reconciled reliable-A batch (commit 6d2d20a6) additionally makes `symmetry_horizontal`
  independent of skimage (cv2 SSIM), so a future skimage regression cannot RED that predicate.

**Owed next** (unchanged): cross-env exact-replay (L5) once the PNG corpus (DK-1) lands; CC-4
wave-2 geometry; VIEW-3 composer.
