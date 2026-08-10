# AG Assignment — Operationalize Defined-but-Unbuilt Image-Tagger Attributes

*An assignable work packet for AG (and other agents), **owned by a student/PI**. Implements Workstream O
of `New_VR_Platform/docs/TARGET_IMAGE_TO_EDITABLE_VR_SPRINT_PLAN.md`. Scope: the ~119 candidates marked
NEEDS FINAL VERIFICATION plus the broader image-computable pool (`env.v2a` 74 + `arch.pattern` 20),
measured against the ~45 already operational. Author: Claude (COWORK) — draft for PI/Codex certification.*

## The one-line
**Reuse before you build.** AG's first job is to find where each attribute is *already* implemented in
open source; only what has no reusable implementation gets built from primitives — and everything, reused
or built, passes the same adversarial gate before it counts.

## Phase 1 — REUSE SEARCH (AG's strongest task; do this first)
For each attribute on the build list, AG web-searches for an existing, maintained open-source
implementation (model, package, or repo) and produces one **triage row**:

| attribute id | what it measures (by function) | existing implementation + link | licence | maturity | verdict |
|---|---|---|---|---|---|
| e.g. `v2a_067` ceiling height / openness | monocular height / scale cue | Depth-Anything-V2 (repo) | Apache-2.0 | active | ADAPT |

Verdicts: **REUSE** (drop-in), **ADAPT** (wrap / fine-tune / threshold), **BUILD** (no reusable impl).
Search by the attribute's *function*, not our name for it. Known reuse landscape to check first, by family:

- **Depth / layout / geometry:** MiDaS, Depth-Anything(-V2), Metric3D; room layout via HorizonNet /
  LGT-Net / LSUN-Room-Layout.
- **Segmentation (surfaces, objects, openings/windows/doors):** SegFormer, Mask2Former, SAM / SAM2, on the
  ADE20K label space.
- **Materials (per-surface):** OpenSurfaces / MINC models, Dense Material Segmentation (DMS).
- **Illumination / lighting:** single-image illumination & exposure estimation; daylight / glare cues.
- **Objects / clutter / occupancy:** YOLO / DETR / Detectron2 detectors → object-count, occupied-floor,
  and clutter proxies.
- **Low-level (usually cheap to BUILD):** colorfulness (Hasler–Süsstrunk), warmth (CCT proxy), fractal
  dimension (box-counting), edge / contour density, symmetry (existing symmetry-detection libs), curvature.

*Phase-1 deliverable:* a triage table covering the whole list, with the REUSE / ADAPT / BUILD split, links,
and licences. This alone answers "what can we reuse vs. must we build" — and it is squarely what AG is good
at (broad, fast web/repo scanning + structured triage).

## Phase 2 — BUILD (only for BUILD / ADAPT verdicts)
Implement each to the tagger's contract [verified · `Image_Tagger_dk_latest/cnfa_algs/CONTRACT.md`]:
`AttributeResult` = **scalar** (∈[0,1] or value) + **confidence** (>0) + optional **`field`** (H×W heatmap)
+ **`regions`** (`kind`, `coords`, `label`, `value`). Each operator ships with a **JUSTIFICATION_TABLE**
entry (param → citation → rationale → limitation) and **known-good / known-bad** fixtures. ADAPT = wrap the
reused model behind the same contract; BUILD = from `cnfa_algs` primitives. Record each operator's licence
(attribution / redistribution) — a reused model's licence rides with it.

## Phase 3 — CERTIFY (never self-certified)
A **different model lineage** adversarially attacks each operator (the repo's DONE+EXT convention) and
labels it **GREEN** (faithful) or **AMBER** (honest proxy / measurement ceiling). Only GREEN, or AMBER with
a stated ceiling, enters the operational set.

## What AG can do reliably — and what it cannot
- **Reliable for AG:** Phase-1 reuse search + triage; drafting Phase-2 operators, tests, and justifications.
- **Not AG's call:** the Phase-3 certification verdict, licence acceptance, and whether an AMBER ceiling is
  acceptable — these are human/PI + different-lineage decisions. **Affective / holistic attributes**
  (soothing, prospect-feel) are **out of scope**: they remain human-study measures, not image operators.

## Acceptance (per attribute)
Triage row complete → (if BUILD/ADAPT) contract-conforming operator + JUSTIFICATION + passing fixtures →
different-lineage certification → GREEN/AMBER recorded in the attribute inventory
(`Image_Tagger_dk_latest/docs/CNFA_ATTRIBUTE_INVENTORY_2026-07-18.md`). Work in **family batches**; report
the reuse/build split and the running GREEN count after each batch.

## How to hand this to AG
Give AG this file plus: `cnfa_algs/CONTRACT.md`, `cnfa_algs/JUSTIFICATION_TABLE.md`, the attribute
inventory + full table, and the canonical registry
(`TRS_v1.1/core/trs-core/v0.2.8/registry/cnfa_tag_registry_canonical_v0.2.8.yaml`). Start AG on **Phase 1
only** and review the triage table before authorizing any Phase-2 build — the triage is where most of the
leverage (and the reuse savings) lives.
