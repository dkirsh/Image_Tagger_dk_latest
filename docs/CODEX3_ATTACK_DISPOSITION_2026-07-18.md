# DISPOSITION of Codex's round-3 attack (FABLE_DISPOSITION_ATTACK_VERDICT)
### 2026-07-18 (Cowork). Response to `FABLE_DISPOSITION_ATTACK_VERDICT_RELIABLE_A_CODEX_2026-07-18.md`

**Accepted in full.** Codex confirmed F1, F2, F3, F6, F8 as fixed and F7 as materially hardened, and
found **two surviving overclaims + one boundary risk**. All three are now fixed and re-verified. The
headline catch — an AMBER proxy still *licensed* in a consumed hedonics path — is the most important
kind of finding, because it is a real downstream effect a label-level check misses.

| Issue (Codex) | Severity | Root cause | Fix | Re-verified |
|---|---|---|---|---|
| **V7 licensed in hedonics** | HIGH | The Mac `cnfa_algs/hedonics.py` had promoted `local_congestion_proxy` (V7) to the "DESIGNATED hedonic clutter signal, replaces legacy" — an AMBER, uncalibrated proxy emitting a *licensed* hedonic value, contradicting D2 | Removed V7 from `HEDONIC_SHAPE` entirely; it is now unregistered → `licensed=False`. Legacy `processing_load_proxy` stays as the ONLY licensed clutter→hedonic signal (per D2 compatibility), with a note that whether clutter belongs in hedonics is UNRESOLVED pending calibration | `hedonic_response('…local_congestion_proxy',0.4).licensed == False` ✓; legacy still licensed ✓ |
| **V9 stale GREEN docstring** | MED | `fractal_band.py` module docstring still read "GREEN, Tier A" / "ceiling GREEN" though `TIER_HINT` + registry are AMBER | Docstring now says AMBER with the F5/Codex caveat; "ceiling GREEN" → "ceiling AMBER". Only remaining "GREEN" token is the historical comment on the `TIER_HINT` fix line | grep: no GREEN claim left ✓ |
| **F7 boundary + thin audit evidence** | MED | `RIDGE_MIN_RELIQR=0.05` is a sharp cliff, and C01/C29 evidence exposed only distance/gate, not the raw ridge set/rank | (a) C01 evidence now carries `ridge_count`, `n_cells`, `ridge_frac`, `anchor_rank_pctl` for audit; (b) added `test_f7_ridge_boundary.py` locking the outlier + near-flat-vs-bimodal boundary so any threshold change is caught | new diagnostics present in real C01 record (`ridge_count=116/500`, `ridge_frac=0.232`, `anchor_rank_pctl=32.2`); boundary test PASSES ✓ |

## Notes
- **The V7 fix was on a file that had diverged from my sandbox.** The Mac `hedonics.py` (146 lines) was
  newer than my sandbox copy (138) — another edit had licensed V7. I staged the Mac version, fixed it
  there, and commit it back, so no other-terminal work is clobbered.
- **The exposed diagnostics are also honest self-criticism:** on a real image the percentile ridge is
  ~23% of cells (not the nominal 15%) because tied cells are included — now visible in every record, so
  an auditor can judge the ridge quality directly. I did NOT switch to a strict top-K ridge (Codex rated
  this acceptable-as-engineering and it risks new bugs); the transparency + boundary test address the ask.
- **F7 threshold cliff:** left at `RIDGE_MIN_RELIQR=0.05` (Codex: "may be acceptable as an engineering
  threshold") but now locked by `test_f7_ridge_boundary.py` so it is proven, not merely asserted.

## Re-verification (sandbox, 2026-07-18)
- Core suites PASS: C01, C29, V9, reliable-attrs, **+ new F7 boundary test**.
- `hedonic_response` for V7 → `licensed=False, shape=unregistered`; legacy still licensed.
- V9 docstring carries no GREEN claim.
- C01 record carries the four ridge-audit fields.
- Full gate on 3 interiors → AMBER=3 RED=0, negative control REJECTED, idempotent, boundaries DENIED.
- MODEL_VERSION → `…+codex2fix+codex3fix`.

## Still owed (unchanged)
Faithful V2/V6/V7 reimplementations; **M1′ sufficient-statistic replay** (Codex re-confirmed it is a
TODO, not done); Mac↔sandbox replay; Article_Eater grounding; labeled A-vs-B corpus. Whether clutter
belongs in the hedonics layer at all is now explicitly UNRESOLVED pending that calibration.

## Recommended next
One more short verify pass (same prompt) to confirm the hedonics delicensing + docstring + diagnostics
hold and nothing new broke. If clean, the batch is defensibly honest-AMBER and it is time to switch from
defense to construction: the faithful reimplementations + M1′.
