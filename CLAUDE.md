# CLAUDE.md — Image_Tagger_dk_latest (repo-level)

*Created 2026-07-19. Extends the root-level `/Users/davidusa/REPOS/CLAUDE.md` (all its rules apply).*

## Cross-AI Artifact Contract (MANDATORY — David, 2026-07-19)

**Every prompt written for another AI worker (Codex, AG, Gemini, Fable-panel) MUST specify the exact
absolute repo path where the worker commits its answer artifact** (e.g.
`/Users/davidusa/REPOS/Image_Tagger_dk_latest/docs/CODEX_<TASK>_<DATE>.md`), and MUST instruct the
worker to COMMIT that file. Rationale: Claude/Fable reads the repo directly through the device
bridge, so a committed artifact at a declared path closes the loop without David copy-pasting
outputs between windows. A prompt without a declared output path is incomplete. When assigning,
also record the expected path in the conversation so the assigning session can poll for it.

## Active sprint context (2026-07-19)

- Sprint: **COMP-CORRECT** (`docs/SPRINT_COMPCORRECT_ALGORITHMS_2026-07-19.md`); validation ladder in
  `docs/CNFA_VALIDATION_METHODOLOGY_2026-07-19.md`. S0 (M1′, 8 audit classes) + S2 (9 Wave-1 ops +
  street-noise) built, attacked by Codex, all findings fixed (`docs/CODEX_S0S2_ATTACK_DISPOSITION_2026-07-19.md`).
- L5 cross-environment findings (`docs/L5_CROSS_ENV_FINDINGS_2026-07-19.md`): JPEG decode is
  platform-dependent → **calibration corpus must be PNG**; cross-machine comparison uses declared
  tolerances (`scripts/m1p_cross_env_replay.py --compare-tol`); the Tier-B geometry chain amplifies
  pixel noise (13% cell_m shift) — robustness work item.
- S1 (faithful V6/V7) is [PORT]-gated: constants must come from the Rosenholtz reference, never from
  memory. Acquired so far (2026-07-19, from the Piranhas MATLAB mirror): FC combination weights
  **color/0.2088 + contrast/0.0660 + orientation/0.0269, Minkowski p=1**; computeClutter defaults
  (numlevels=3, contrast_filt_sigma=1, contrast_pool_sigma=3, color_pool_sigma=3,
  orient_pool_sigma=3.5); collapse kernel [0.05 0.25 0.4 0.25 0.05] with element-wise max across
  scales; SE chroma weight wght_chrom=0.0625, wlevels=3 (kargaranamir/visual-clutter API). Still
  needed VERBATIM: computeColorClutter / contrastClutter / orientationClutter internals + SE
  band-entropy code — the `visual-clutter` PyPI sdist in `reference/` (David downloads) or further
  verbatim fetches.

## Standing repo rules

- Never `git add -A`; add only named files. `.gitignore` blocks `*prompt*.md` (use `git add -f` for
  prompt docs that must be committed).
- The Cowork sandbox cannot delete git lock files — if a commit fails on a stale `.git/*.lock`
  with no live git process, move it aside (`mv` to `_to_delete/`) or delete from a Mac terminal.
- Tests are run per-file (`PYTHONPATH=. python3 annotation_socket/tests/test_*.py`); pytest may be absent.

## Sandbox git commits WORK (discovered 2026-07-19)
The Cowork sandbox mount blocks `unlink` but permits `rename`. Therefore git commits FROM THE
SANDBOX SUCCEED: (1) `mv` any stale `.git/*.lock` into `_to_delete/` first; (2) run git with
`--no-optional-locks`; (3) after the commit, `mv` the leftover `HEAD.lock` / `objects/*/tmp_obj_*`
into `_to_delete/` so the next operation isn't blocked. `git status` itself leaves an index.lock
behind — always use `git --no-optional-locks status`. Never force-delete locks without checking
they are zero-byte and no live git process holds them.
