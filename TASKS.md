# TASKS.md — Image_Tagger / CNfA sprint queue

*Last updated: 2026-07-19 (Fable/Cowork). THE authoritative live queue (root-CLAUDE.md protocol).
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
| CC-2 | P1 | M1′ audit classes still owed: ssim_map, contour_stats, penumbra_stats, texture_stats + classes for faithful FC (`feature_congestion` layer means) and SE (subband entropy vector) and complexity_partition (zone table digest) | FABLE | — |
| CC-3 | P1 | C5–C23 declared-input VALUE bundles through the `input_values` channel (street-noise opened it); full-socket fixtures per predicate | FABLE | — |
| CC-4 | P1 | S3 remainder: W2.2 ceiling_openness_relative, W2.3 double-height flag, W2.4 blind_corner_index, W2.5 barrier_permeability, W2.8 thresholds; register W2.1 verticality + W2.6 choice_richness with the batch | FABLE | CC-1 (attack first) |
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
| VIEW-0 | P1 | Field-sidecar persistence: worker writes each operator's field + zone table to `fields/<unit_id>.npz` (+PNG renders), content-addressed; viewer consumes ONLY records+sidecars (never recomputes) | FABLE | — |
| VIEW-1 | P1 | Layered static viewer: self-contained HTML per unit (canvas overlays, the 8 layer groups above, toggles+opacity+legend, zone tooltips with class/D/hypothesis). Acceptance: open one HTML file, understand a room's annotation without any docs | FABLE | VIEW-0 |
| VIEW-2 | P1 | Function inspector: per-predicate page — value, field, evidence bbox, ALL declared params/constants (from extras), method string, failure modes, M1′ digest + tier; deep-linkable from any layer. Parameterized ops (street-noise Leq/R′) show their declared inputs; interactive re-run is a later server-mode task (VIEW-5) | FABLE | VIEW-1 |
| VIEW-3 | P1 | Question-driven composer: question → (LLM, registry-aware) → display-composition JSON {layers, focus bboxes, narrative-with-anchors} → rendered view. Acceptance test IS David's example: "effects of street noise on the foyer" → explanatory answer + SPL/huddle layers + how-to-read guidance pointing at specific zones. Template library for the common question classes (noise, clutter-where, biophilia, wayfinding, privacy) | FABLE (+VLM) | VIEW-1; street-noise needs input_values (CC-3) for live units |
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
| DK-1 | Drive corpus export: **PNG**, ~120 interiors + 80 A/B pairs (Codex's category list) + nature-through-glass (DT-1) + wood/stone-material and bookshelf/ornament contrasts (new taxonomy classes) | OPEN — gates all L6 |
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
