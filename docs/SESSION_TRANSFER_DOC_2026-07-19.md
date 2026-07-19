# SESSION TRANSFER DOC — 2026-07-19 (overnight, Fable/Cowork)
### For David's morning + any AI worker. Repo: /Users/davidusa/REPOS/Image_Tagger_dk_latest, branch cnfa-algs-2026-07-14.

## Where the sprint stands (COMP-CORRECT)
S0 (M1′, 8 audit classes incl. geometry chain) ✅ · S2 (9 Wave-1 ops + street-noise) ✅ · Codex
attack survived, all findings fixed ✅ · S3 slice 1 (verticality + choice-richness) ✅ built,
unregistered · Clutter stack C-CLUT-2a/b/c (proto-object count / MSG / MUC) ✅ built + registered
(39/39 scoring) · **S1 faithful V6/V7: EXECUTED overnight — see below** · L5 cross-env: closed with
findings (decode-dependence; tolerances set; geometry chain amplifies pixel noise 13%).

## What happened overnight (all run + verified in sandbox)
1. **The Rosenholtz reference is in and running.** The `visual_clutter` 1.0.7 wheel David downloaded
   is vendored UNMODIFIED at `cnfa_algs/_vendor/visual_clutter/` (MIT, attributed). Every constant
   is now the reference's own — nothing invented.
2. **`cnfa_algs/_pyrtools_min.py`** — pyrtools-compatible shim (corrDn/upConv reflect1, binom5
   Gaussian pyramid, frequency-domain steerable pyramid). Internal invariants PASS: radial mask
   complementarity |hi0|²+|lo0|²=1 (dev 9.4e-6, interpolation-limited like pyrtools itself) and the
   angular steering identity Σ_b mask² = 1 (dev 4.2e-6). Four PORT-CHECK notes (P1–P4) mark every
   convention the Mac must adjudicate.
3. **`cnfa_algs/faithful_clutter.py`** — `feature_congestion_faithful` + `subband_entropy_faithful`:
   the vendored reference on the shim, full extras (raw values, per-layer means, all params).
   Fixtures PASS (clutter>texture>blank on FC; determinism ×2; real-interior smoke run). NOT yet
   registered — the [PORT] gate requires the Mac adjudication first; proxies stay running (Q3).
4. **FINDING DT-1 (important):** the REFERENCE measure ranks minimal-but-foliage-framed Farnsworth
   (FC 4.98 / SE 3.54) ABOVE the cluttered industrial office (4.62 / 3.38) — vegetation's
   contrast/orientation/color variance reads as clutter. Our proto_object_count gets the intuitive
   ordering (269 vs 143 objects). This empirically demonstrates the 2007 maps/UI→interiors transfer
   problem with the authors' own algorithm, and strengthens the three-layer clutter-stack verdict.
   Corpus (L6) adjudicates; Farnsworth-type images (nature through glass) are now priority corpus items.
5. **FINDING P3 (logged, pending adjudication):** the Python reference package's `collapse()` calls
   upConv with a unity-sum kernel (no ×4 gain), so upper pyramid levels are attenuated ~4×/level
   relative to the 2007 MATLAB (`RRoverlapconvexpand` doubled the kernel per axis). The package is
   our declared reference, but the package-vs-MATLAB divergence question goes to Codex/panel.
6. **`scripts/reference_clutter_compare.py`** — the adjudication harness; sandbox side RUN
   (8 entries → `docs/CLUTTER_REFERENCE_SANDBOX_2026-07-19.json`).

## Files and Artifacts (this session, committed unless noted)
| File | Type | Change |
|---|---|---|
| `cnfa_algs/_pyrtools_min.py` | Code | NEW pyramid shim, invariant-tested |
| `cnfa_algs/_vendor/visual_clutter/*` + `_vendor/__init__.py` | Vendored | reference impl, unmodified |
| `cnfa_algs/faithful_clutter.py` | Code | NEW faithful FC/SE operators (unregistered) |
| `scripts/reference_clutter_compare.py` | Code | NEW adjudication harness |
| `docs/CLUTTER_REFERENCE_SANDBOX_2026-07-19.json` | Data | sandbox-side reference values |
| `docs/CODEX_S1_REFERENCE_ADJUDICATION_PROMPT_2026-07-19.md` | Prompt | Mac-run task (artifact paths declared) |
| `cnfa_algs/clutter_stack.py` + registry/annotator | Code | C-CLUT-2a/b/c (was staged pre-sleep; committed with this batch) |
| `docs/CNFA_COMPUTATIONAL_ATTRIBUTES_TABLE_2026-07-19.md` | Doc | 58-predicate registry-generated table |
| `docs/SESSION_TRANSFER_DOC_2026-07-19.md` | Transfer | this doc |

## David's morning checklist (order matters)
1. Drop `docs/CODEX_S1_REFERENCE_ADJUDICATION_PROMPT_2026-07-19.md` into any Codex window — it
   commits its own artifacts; no copy-paste back needed (per the CLAUDE.md artifact contract).
2. `git push origin cnfa-algs-2026-07-14` when convenient (several local commits).
3. Still open from before: the VERIFY2 Codex pass (optional, prompt unchanged); the Drive corpus
   export (now: PNG format, and include Farnsworth-type nature-through-glass interiors for DT-1).

## Next build steps (any worker)
Adjudication PASS → register faithful FC/SE (AMBER), add `steerable_pyramid`/`feature_congestion`
M1′ classes, run proxies in parallel per Q3, measure proxy-vs-faithful divergence on the smoke set.
Adjudication FAIL → fix the named P1–P4 item, re-run, THEN register. Then: S3 remainder, penumbra/
texture/ssim M1′ classes, C5–C23 value-bundle wiring, S4 model decision.
