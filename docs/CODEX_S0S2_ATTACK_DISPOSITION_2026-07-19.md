# DISPOSITION of Codex's S0+S2 attack (CODEX_ATTACK_S0S2_VERDICT_2026-07-19)
### 2026-07-19 (Cowork/Fable). Verdict was CHANGES REQUIRED — all five priority fixes are now implemented and re-verified.

**Accepted in full.** Every finding was reproduced before fixing; every fix was re-verified by
executing Codex's own probe. The two HIGHs were both real socket-level gaps that the pure-core tests
could not see — exactly the layer the attack was asked to hit.

| Finding | Sev | Fix | Re-verified |
|---|---|---|---|
| **Street-noise UNKNOWN/RED with supplied inputs** | HIGH | The declared-input VALUE channel did not exist (tokens only — a gap the whole C5–C23 family shares; street-noise surfaced it first). `annotate_image` now takes `input_values`; a street-noise binding unpacks the `facade_spec` bundle (`facade_row`, `Rp` scalar-or-per-column, `alpha`), scores through `plan_ev`, and fails closed with `declared_input_value_missing:*` when a token arrives without its value. Records carry `input_values`; `verify._replay` threads them | with values → SCORED (0.0028, L_rev 27.96 on korridor plan), unit AMBER, zero street problems ✓; tokens-without-values → UNKNOWN naming the missing values ✓; Rp-length mismatch → informative UNKNOWN ✓ |
| **Honest no-signal images go RED** | HIGH | New ABSTAINED subtype `signal_absent` (derivation.abstain_signal): allowed ONLY for registry-flagged `MAY_LACK_SIGNAL` predicates (9 listed) AND only with the operator's own absence evidence (edge counts, std, saturation — all abstain paths now emit it); verifier demotes to AMBER instead of RED; unsanctioned or evidence-free signal-absent is still a problem | Codex's blank-wall probe: tier **AMBER** with 7 evidenced signal-absent abstentions, zero problems ✓ |
| **Missing M1′ demotes instead of failing** | MED | Legacy allowance REMOVED: the annotator emits m1p on every bound predicate and the MODEL_VERSION bump content-addresses all pre-M1′ records away, so a missing/failed block on a bound predicate is tampering or a broken worker → `M1_PRIME:<pid>:missing_stats`, RED | stripped-m1p record → **RED** ✓ |
| **Loader duplicated annotator↔M1′** | MED | `annotate_image` now calls `m1_prime.load_for_m1p()` — one definition, no drift surface | wiring tests + run_stage pass through the shared loader ✓ |
| **texture_density silently excludes periodic texture** | MED | Scoped honestly: registry note + intent now read "RESIDUAL micro-texture EXCLUDING structured/periodic pattern"; wallpaper/ribbing limitation named; a periodic-texture statistic is declared future work (not silently promised) | note visible in registry ✓ |
| **Adjacent-bimodal orderliness reads as two axes** | LOW | Emits `modes_adjacent` + `mode_bin_separation`; adjacent modes read as dominant-axis coverage | fixture unchanged, extras now disambiguate ✓ |
| **Colored-light shadow boundary accepted** | LOW | Named single-photo limit added to failure_modes (warm/cool illuminant change is not separable from material in one photo); accepted/rejected counts already exposed | declared ✓ |
| **A5: degenerate-regime inverted-U untested** | note | Too-quiet regime added to the street-noise self-test: best_huddle collapses to ~0 (no fake inverted-U) | PASS ✓ |

## Held surfaces (no action): A1 cross-image/forged-digest tamper caught incl. 0.05-entropy under
coarse palette rounding; A3 calibration honesty visible; A6 V7 delicensing sealed in HEAD+tree.

## Re-verification (sandbox, 2026-07-19)
All 6 test files PASS; wave1/street/wave2 self-tests PASS (street now includes the degenerate
regime); run_stage on 3 interiors → **AMBER=3 RED=0, 36/36 scored, negative control RED, idempotent**;
blank-wall unit AMBER; supplied-inputs street-noise unit AMBER with SCORED value.
MODEL_VERSION → `…+codexS0S2fix`.

## Still owed (unchanged by this pass)
Faithful V6/V7/V2 ([PORT] — reference toolbox); remaining M1′ classes (ssim_map, contour_stats,
penumbra_stats, texture_stats); Mac-side L5 replay; Drive corpus; S3 remainder (ceiling/blind-corner/
permeability); S4 model decision. Design note: the `input_values` channel now exists for ALL
declared-input predicates — wiring C5–C23 value bundles through it is a natural next step and should
get its own review.
