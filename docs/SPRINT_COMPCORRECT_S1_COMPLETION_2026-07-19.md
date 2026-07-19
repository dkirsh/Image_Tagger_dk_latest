# Sprint COMP-CORRECT — S1 Completion Report
**Date**: 2026-07-19 · **Stage**: S1 faithful V6/V7 ([PORT]) · **Status**: COMPLETE (AMBER pending corpus L6 only)

## Summary
The faithful Feature Congestion (V7) and Subband Entropy (V6) operators are registered and running
(42/42 socket predicates). The algorithm is the UNMODIFIED vendored Rosenholtz reference
(`visual_clutter` 1.0.7, MIT) on our pyramid shim, adjudicated against REAL pyrtools across two
Codex passes: after the sqrt(2) binomial fix (P2) and the log_rad bookkeeping fix (S1B — scale
progression lives solely in the Xrcos shift), **every subband coefficient std matches real
pyrtools to ~1e-7** and the full harness PASSES within 2%. Near-blank input ABSTAINS (SE/FC of a
featureless field is the entropy of numerical noise — platform-dependent, construct-meaningless).

## The Q3 divergence measurement (proxies vs faithful, 9 interiors, Spearman rank)
| pair | rank corr | verdict |
|---|---|---|
| V6: grayscale_gabor_entropy_proxy vs faithful SE | **-0.117** | the proxy was measuring something else ENTIRELY — any past inference from it as "subband entropy" is void |
| V7: local_congestion_proxy vs faithful FC | 0.717 | directionally useful, materially imperfect |

Both proxies stay registered (parallel run) but the V6 proxy's registry note should now say
UNCORRELATED-WITH-CONSTRUCT; retirement decision at the next panel.

## Files
`cnfa_algs/faithful_clutter.py` (+near-blank guards, ADJUDICATED status), `cnfa_algs/_pyrtools_min.py`
(P2 + P4a-c + S1B fixes), `cnfa_algs/_vendor/visual_clutter/` (unmodified reference),
`scripts/reference_clutter_compare.py` (+blank noise-dominated rule), registry/annotator (+2
predicates, MODEL_VERSION +faithfulV6V7). Adjudication chain: `docs/CODEX_S1_ADJUDICATION_2026-07-19.md`,
`docs/CODEX_S1B_NOTE_2026-07-19.md`, `docs/SUBBAND_DUMP_MAC_2026-07-19.json`,
`docs/CLUTTER_REFERENCE_{MAC,SANDBOX_v6}_2026-07-19.json`.

## Open on this thread
Corpus L6 (construct validation on interiors; DT-1 stands: vegetation reads as clutter — the
complexity_partition operator is the response); P3 finding (package-vs-MATLAB 4x collapse gain)
for panel; V6-proxy retirement decision; M1' audit classes for the two faithful operators.
