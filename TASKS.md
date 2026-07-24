# TASKS.md — Image_Tagger / CNfA sprint queue

*Last updated: 2026-07-19 late (Fable/Cowork). THE authoritative live queue (root-CLAUDE.md protocol).
Goal of record: **every attribute in the registry is a computational, effective procedure —
algorithmically correct, stats-audited (M1′), honestly tiered — and the results are viewable and
questionable.** Sprint docs give the how; this file tracks the what/when/who. Never delete
completed rows.*

> **📌 TANISHQ — NEW 2026-07-23:** assignable sprint cards are in `docs/TANISHQ_SPRINT_CARDS_2026-07-23.md`
> (includes the new **LEG-1 legibility-field** attribute). Pick a card, claim it in its row, ship it.
>
> **📌 NEW 2026-07-24 — environment IV forest landed (v0).** Three new tagger jobs feed it:
> **CC-5b** (MINC material segmentation), **ACO-1** (assembly-inference → acoustic pre-diagnosis),
> **LUM-1** (daylight-state + glare-from-luminance-map). See `Sprint ENV-PHYSICS` below. Spec:
> `Cognitive_and_Wellness_Code_Program/IV_FOREST_v0_2026-07-24.md` + `IV_FOREST_DECISIONS_LOG_2026-07-24.md`
> (decisions D8/D9/D10/D11).

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
| CC-5 | P1 | S4 detector wave: **model=SegFormer-B2 (pinned ONNX + version-hash, DEC-1 07-23)** → vegetation/window-view/blue-space/sociopetal ops; upgrades the partition's biophilic gate + adds segment-count clutter layer; art-CONTENT + text/signage VLM-tier gates ride the same decision. Neg-controls: green paint≠vegetation, indoor-plant≠window-view; M1′=segmentation_mask provenance. | FABLE/TANISHQ build | — (DEC-1 decided) |
| CC-5b | P1 | **Material segmentation (MINC-2500 taxonomy)** — per-pixel material class (wood/stone/tile/plaster/brick/concrete/glass/metal/textile/carpet/water/vegetation…), the image-computable feed for the materials branch (`L.MAT`) and the D9 assembly-inference layer. Emits `MAT.CLASS` map + M1′=`segmentation_mask` provenance; neg-controls: photo-of-wood≠wood-grain-wallpaper flagged low-confidence; wet-floor≠water. Rides the CC-5 SegFormer/DEC-1 decision (same model family, material head). | FABLE/TANISHQ build | — (DEC-1 model decided; needs material label set) |
| CC-6 | P2 | **Execute V6-proxy retirement (DEC-3 07-23: retire now, uncorrelated −0.117); keep V7 (0.717) parallel one more corpus cycle then re-decide.** | FABLE/TANISHQ | — (DEC-3 decided) |
| CC-7 | P2 | P3 finding to panel: reference-package collapse() lacks MATLAB ×4 upConv gain — which is "the" FC for us? | PANEL | — |
| CC-8 | P2 | Faithful V2 (Penacchio–Wilkins 2-D), `fft_2d` M1′ class. **FOV policy (DEC-2 07-23): declared-assumption tier, AMBER, disclose assumed FOV; hard-abstain only when FOV-sensitivity > threshold.** | FABLE | — (DEC-2 decided) |
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

## Sprint NEW-ATTR — legibility field (NEW, David 2026-07-23)

*Spec: `docs/JOB_LEGIBILITY_FIELD_WAYFINDING_2026-07-23.md`. Environment-side (IV) attribute + a
position-tagged spatial field: readability of wayfinding cues (signage / room numbers / arrows) as a
function of luminance contrast × adaptation luminance × visual angle vs the eye's contrast-sensitivity
limit (Adrian Visibility Level / Rea–Ouellette RVP / Barten CSF). Output: per-sign legibility distance +
a VL heat-map over viewer positions (isovist/gaze-gated) — "from where is sign X readable?", tagged to
3-D position. Reuses the isovist/spatial machinery; connects to the VIEW-3 wayfinding template.*

| ID | P | Task | Owner | Blocked by |
|----|---|------|-------|-----------|
| LEG-1 | P2 | Build **ATTR-LEG1 Legibility Field (VL)**. Tier-1 now: relative luminance + text/sign detect + Weber contrast + x-height(px) → qualitative VL heat-map, labelled uncalibrated. Tier-2: HDR-fisheye + Sekonic cross-cal → real cd/m² + legibility distances + Adrian age/glare/time terms. Tier-3: 3-D sign positions + isovist/gaze gating + oblique foreshortening + chromatic channel. Register ATTR-LEG1 in CNFA_ATTRIBUTE_INVENTORY (SPEC+PLAN) on pickup; validate `D_max` vs published legibility-index + one field measurement. | FABLE/CODEX build; DAVID decisions | reuses isovist/spatial (VIEW/geometry); Tier-2 needs HDR+Sekonic calibration |

**DAVID decisions for LEG-1:** (a) `VL_crit` for "readable" — bare threshold (~1) vs comfortable glance-while-walking (~7); (b) age/population term; (c) chromatic-contrast channel for colour-coded signage now or later; (d) commit HDR+Sekonic as the Tier-2 calibration path.

## Sprint ENV-PHYSICS — assembly & daylight inference (NEW, David 2026-07-24)

*The IV forest (`COGNITIVE_CODE_PROGRAM/IV_FOREST_v0_2026-07-24.md`) needs physics measures — acoustics,
daylight, glare — that CANNOT be read raw off a photo. Decision D9: an explicit, confidence-bearing,
client-overridable inference layer sits between image features and the physics measures. Decision D10:
every inferred value carries `value_confidence{provenance ∈ measured|modeled|assumed}`, kept distinct from
edge `credence`. Decision D11: client metadata (lat/long, timestamp, orientation, declared assemblies) +
intended-activity per zone condition the appropriateness verdict. These jobs build the tagger side of that.*

| ID | P | Task | Owner | Blocked by |
|----|---|------|-------|-----------|
| ACO-1 | P2 | **Assembly-inference → acoustic pre-diagnosis.** From `MAT.CLASS` map (CC-5b) + surface role (absorber/reflector/resonator/diffuser) + building type + region → **assembly posterior** → α(f) per surface + scattering s(f); combine with inferred room volume V + surface areas (geometry chain) → Sabine/Eyring **T30(f), C50, STI pre-estimate**, all tagged `source:inferred`, `value_confidence{provenance:modeled|assumed}`, **overridable** by client BIM/measured RT. Emit which targets the photo supplies (geometry, materials→α) vs which the client must (source/receiver layout, true RT). Neg-control: bare-prior assembly → `assumed`/low confidence, never GREEN. | FABLE/CODEX build; DAVID (assembly prior tables) | CC-5b (material map); geometry chain (volume/areas) |
| LUM-1 | P2 | **Daylight-state estimation + glare-from-luminance-map.** Tier-1: relative luminance map + glare *risk* flag (no metadata) labelled `provenance:assumed`. Tier-2: with client `CTX.META{lat/long, timestamp, orientation}` [+ multi-time image set] → **daylight-state posterior** (sun position, sky type, direct/diffuse split) → absolute-luminance / melanopic-context / **DGP** estimate, `provenance:modeled`. Tier-3: HDR-fisheye + Sekonic cross-cal → `measured` (shared calibration path with LEG-1 Tier-2). Activity-conditioned verdict (D11): DGP fine for circulation may fail for detailed-visual-work; undeclared activity → `undetermined`, route to VOI. | FABLE/CODEX build; DAVID (metadata schema sign-off) | LUM luminance ops; CTX.META schema; shares LEG-1 HDR calibration |

**DAVID decisions for ENV-PHYSICS:** (a) sign off the **client metadata schema** (`CTX.META` fields) and the **intended-activity vocabulary** (`CTX.ACTIVITY`); (b) supply / approve the **assembly prior tables** (material×role→α by building type/region) that INF.ASSEMBLY keys on, or authorize using a published handbook set (Cox & D'Antonio / ISO 11654 αw) as the v0 prior; (c) confirm HDR-fisheye + Sekonic as the shared Tier-2/3 calibration path for both LUM-1 and LEG-1.

## Decisions open (PANEL / DAVID)

| ID | Decision | Options |
|----|----------|---------|
| ~~DEC-1~~ **DECIDED 07-23** | Wave-3 segmentation model | **SegFormer-B2**, pinned ONNX + version-hash (David). Unblocks CC-5. |
| ~~DEC-2~~ **DECIDED 07-23** | Faithful-V2 FOV policy | **Declared-assumption tier, AMBER, assumed FOV disclosed in evidence; hard-abstain only when the metric's FOV-sensitivity exceeds a set threshold** (David). Unblocks CC-8. |
| ~~DEC-3~~ **DECIDED 07-23** | V6/V7 proxy retirement (see CC-6) | **Retire V6-proxy now** (uncorrelated −0.117); **keep V7** (0.717) one more corpus cycle, then decide (David). |

## DAVID-only

| ID | Task | Status |
|----|------|--------|
| DK-1 | Drive corpus export: **PNG**, ~120 interiors + 80 A/B pairs (Codex's category list) + nature-through-glass (DT-1) + wood/stone-material and bookshelf/ornament contrasts (new taxonomy classes) | **GO 07-23 (David): start the STARTER set NOW** — ~30 interiors + 15 A/B pairs + 5 each nature-glass/materials/collections, manifest.csv from day one, ALL PNG converted on Mac -> first L6 calibration pass -> grow to ~200 incl. ugly/ordinary rooms — gates all L6 |
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
