# TASKS.md — Image_Tagger / CNfA sprint queue

*Last updated: 2026-07-19 late (Fable/Cowork). THE authoritative live queue (root-CLAUDE.md protocol).
Goal of record: **every attribute in the registry is a computational, effective procedure —
algorithmically correct, stats-audited (M1′), honestly tiered — and the results are viewable and
questionable.** Sprint docs give the how; this file tracks the what/when/who. Never delete
completed rows.*

## Queue discipline
Priority = P0 (unblocks other work) > P1 (sprint-critical) > P2 (valuable) > P3 (later).
Owner = FABLE (this session class) / CODEX (dropped prompt, artifact contract applies) /
DAVID (only-human-can) / PANEL (decision). Every CODEX row names its committed artifact path.

## Sprint COMP-CORRECT — remaining (algorithms; docs/SPRINT_COMPCORRECT_ALGORITHMS_2026-07-19.md)

| ID | P | Task | Owner | Blocked by |
|----|---|------|-------|-----------|
| CC-1 | P0 | External ATTACK pass on the un-attacked batch: clutter_stack + complexity_partition (11-class taxonomy) + faithful FC/SE + wave2_geometry — the cadence rule says attack before building on top | CODEX (prompt to write; artifact `docs/CODEX_ATTACK_TAX_VERDICT_<date>.md`) | — |
| CC-3 | P1 | C5–C23 declared-input VALUE bundles through the `input_values` channel (street-noise opened it); full-socket fixtures per predicate | FABLE | — |
| ~~CC-4~~ **DONE 07-20** | P1 | S3 remainder W2.2-W2.5/W2.8 built + W2.1/W2.6 registered — all AMBER, abstain-with-evidence; registry 68 preds; smoke GREEN=0/AMBER=3/RED=0 | FABLE | commit 90bd03e9 · docs/CC4_WAVE2_GEOMETRY_2026-07-20.md |
| CC-5 | P1 | S4 detector wave: pinned segmentation model → vegetation/window-view/blue-space/sociopetal ops; upgrades the partition's biophilic gate + adds segment-count clutter layer; art-CONTENT + text/signage VLM-tier gates ride the same decision | FABLE build; PANEL/DAVID model choice (Q1) | DEC-1 |
| CC-6 | P2 | V6-proxy retirement decision (Spearman −0.117 vs faithful — measured 2026-07-19); V7 proxy (0.717) keep-parallel question | PANEL | corpus helps but not required |
| CC-7 | P2 | P3 finding to panel: reference-package collapse() lacks MATLAB ×4 upConv gain — which is "the" FC for us? | PANEL | — |
| CC-8 | P2 | Faithful V2 (Penacchio–Wilkins 2-D) with FOV gate; `fft_2d` M1′ class | FABLE | DEC-2 |
| CC-9 | P2 | Geometry-chain robustness: jittered-input stability test (L5 found 13% cell_m amplification); scale anchors (W2.7) once detector lands | FABLE | CC-5 for anchors |
| CC-10 | P3 | Hedonic licensing of partition zone tags; clutter-layer weight fitting; Wave-1 constant refits; GREEN promotions | FABLE+PANEL | CORPUS |

## Sprint VIEW — the annotation viewer (NEW, David 2026-07-19)

*Design intent (decided): layers divide by REGISTER, mirroring the code's own structure — (1) base
image; (2) SEMANTIC ZONES (the 11-class partition overlay — the "rename regions by their
semantics" layer); (3) LIGHT fields (brightness/gradient/glare/dark-zones/pools/sun-patches);
(4) FLUENCY-CLUTTER fields (FC map, clutter-stack layers, texture, orderliness); (5) SPACE-GEOMETRY
(inferred plan, VGA integration, prospect/enclosure, C01 ridge+anchors); (6) ACOUSTICS
(street-noise SPL + huddle + STI fields, plan-projected); (7) EVIDENCE (per-predicate bbox + value
chips); (8) AUDIT (tier, M1′ digest status — the honesty layer). Question-driven entry composes
layer sets + narrative; the LLM is ADVISORY-ONLY (composes displays and explanations, never alters
scores — same separation as the ≠-mind judge).*

| ID | P | Task | Owner | Blocked by |
|----|---|------|-------|-----------|
| ~~VIEW-3~~ **DONE 07-20** | P1 | Question-driven composer: question → (LLM, registry-aware) → display-composition JSON {layers, focus bboxes, narrative-with-anchors} → rendered view. Acceptance test IS David's example: "effects of street noise on the foyer" → explanatory answer + SPL/huddle layers + how-to-read guidance pointing at specific zones. Template library for the common question classes (noise, clutter-where, biophilia, wayfinding, privacy) | FABLE (+VLM) | VIEW-1; street-noise needs input_values (CC-3) for live units |
| VIEW-4 | P2 | A-vs-B compare view (two units side-by-side, synchronized layers) — also the corpus-labeling tool | FABLE | VIEW-1 |
| VIEW-5 | P3 | Server mode: parameter sliders with live recompute; batch browsing | FABLE | VIEW-2 |

## Decisions open (PANEL / DAVID)

| ID | Decision | Options |
|----|----------|---------|
| DEC-1 | Wave-3 segmentation model | SegFormer-B0 (light) vs B2 (better masks); pinned ONNX either way |
| DEC-2 | Faithful-V2 FOV policy | hard-abstain without EXIF vs declared-assumption tier |
| DEC-3 | V6/V7 proxy retirement (see CC-6) | retire V6-proxy now (uncorrelated) vs keep one corpus cycle |

## DAVID-only

| ID | Task | Status |
|----|------|--------|
| DK-1 | Drive corpus export: **PNG**, ~120 interiors + 80 A/B pairs (Codex's category list) + nature-through-glass (DT-1) + wood/stone-material and bookshelf/ornament contrasts (new taxonomy classes) | OPEN — STAGED plan AGREED 2026-07-20: starter set FIRST (~30 interiors + 15 A/B pairs + 5 each nature-glass/materials/collections, manifest.csv from day one, ALL PNG converted on Mac) -> first L6 calibration pass -> grow to ~200 incl. ugly/ordinary rooms  — gates all L6 |
| DK-2 | Drop CC-1 attack prompt into Codex when written | waiting on prompt |
| DK-3 | Master-doc well-being entry revision (docs/MASTERDOC_WELLBEING_REVISION_TODO_2026-07-18.md) | OPEN |
| DK-4 | Periodic `git push` (several local commits accumulate between pushes) | recurring |

## Completed (this sprint cycle — full history in the sprint/completion docs)

| Task | Completed | Outcome |
|------|-----------|---------|
| S0 M1′ core+wiring (8 audit classes incl. geometry chain) | 07-19 | tamper→RED proven; strict gate |
| S2 Wave-1 (9 ops) + street-noise operator | 07-19 | registered; Codex attack survived, all findings fixed |
| Clutter stack C-CLUT-2a/b/c (proto-objects/MSG/MUC) | 07-19 | registered; no combined scalar by design |
| S1 faithful FC/SE ([PORT], adjudicated vs real pyrtools ~1e-7) | 07-19 | registered; V6-proxy shown UNCORRELATED (−0.117) |
| Complexity partition + 11-class Kellert/Terrapin taxonomy | 07-19 | registered; DT-1 resolved (Farnsworth 0.711 vs office 0.258 biophilic) |
| L5 cross-env (decode finding, tolerances, geometry amplification) | 07-19 | closed with findings; corpus must be PNG |
| Codex cycles: S0S2 attack+fixes, S1 adjudication, S1B subband dump | 07-19 | all dispositioned; artifact contract in repo CLAUDE.md |
| VIEW-0 field sidecars (fields_sink; npz+manifest v2 w/ meta; deterministic) | 07-19 | commit 7346ded7, 88e55989 |
| VIEW-1 layered viewer (8 register groups, zone tooltips, 4.8 MB) | 07-19 | commits a3995318, 229640f0; example in viz/examples/ |
| VIEW-2 function inspector (61 predicate pages, all constants surfaced) | 07-19 | commit 88e55989 |
| CC-2 owed M1' classes (7 bindings; 15 predicates now emit M1') | 07-19 | commit d5fe276b; MODEL_VERSION +cc2m1p |
| Reliable-A reconciliation: honest keys (V2/V6/V7 renamed), F1/F7/F8 fixes, cv2 SSIM, full-BFS Turner integration | 07-20 | commit 6d2d20a6; HEAD was inconsistent (committed registry used new keys, impl returned old) — now aligned; all per-file tests + spatial_syntax self-test PASS |
| (a) skimage-present 3-image stage smoke | 07-20 | 3 units AMBER, 42/42 scored, unknown=0, replayed, problems=[]; FC/SE (gabor/congestion/feature_congestion/subband) RED->cleared; neg-control RED; idempotent; docs/SMOKE_SKIMAGE_RERUN_2026-07-20.md |
| CC-4 wave-2 geometry (W2.2-W2.5,W2.8 built; W2.1/W2.6 registered) | 07-20 | commit 90bd03e9; all AMBER, abstain-with-evidence; 68 preds; module+socket tests + 68-pred smoke (AMBER x3, unknown=0, neg-control RED) |
| VIEW-3 question-driven composer (advisory-only, score-separated) | 07-20 | commit 743d0d6a; acceptance 'street noise on foyer' PASS; rogue-LLM number redacted; noise/clutter/biophilia/wayfinding/privacy templates; docs/VIEW3_QUESTION_COMPOSER_2026-07-20.md |
