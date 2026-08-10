# Vision Tagging of 2D Images and 3D Models: Current State

**Prepared:** 2026-07-29 (Pacific time)  
**Repository reviewed:** `/Users/davidusa/REPOS/Image_Tagger_dk_latest`  
**Purpose:** Give Image_Tagger and collaborating agents a precise account of what already exists, what has been tested, and what remains to make 2D and 3D tagging an integrated system.

## Short Answer

Yes. There is substantial working code for tagging ordinary 2D architectural images, including conventional computer vision, optional vision-language models, cognitively motivated CNFA attributes, plan-like inferences, evidence fields, and human validation.

There is also meaningful work toward 3D:

1. A strict GLB intake and validation core exists and passes its synthetic tests.
2. Structured3D annotations can be converted into the project's `PlanGrid` representation.
3. Parsers and adapters exist for depth, segmentation, wireframes, room layout, and SpatialLM output.
4. Once a `PlanGrid` exists, many spatial, visibility, movement, setting, and wayfinding metrics are already available.

However, there is not yet a complete path that reads an arbitrary architectural GLB, renders and normalizes it, derives a trustworthy `PlanGrid`, applies the taggers, and returns evidence-bound tags. The present 3D work is a strong foundation, not a finished 3D tagger.

## What Exists

| Capability | Current status | Evidence and qualification |
|---|---|---|
| Web application for 2D image upload and tagging | Operational | The React/FastAPI application stores images and runs the canonical science pipeline. |
| Canonical 2D science pipeline | Operational, with optional modules | Color, complexity, texture, fractals, symmetry, naturalness, fluency, biophilia, depth/spatial proxies, room detection, and basic materials are present. VLM, segmentation, and some advanced analyzers are optional or disabled by default. |
| CNFA research attribute engine | Operational but research-grade | Registry contains 68 predicates: 40 image attributes and 28 plan metrics. It emits value, confidence, method, evidence, tier, and abstention information. |
| Activity or use-support inference from images | Implemented, provisional | A 24-activity vocabulary and attribute/VLM methods exist. These infer likely support for activities; they do not observe actual behavior. |
| Image-to-depth and image-to-layout adapters | Partial | Several adapters and model assets exist, but availability and environment problems prevent a general end-to-end claim. |
| Structured3D annotation to `PlanGrid` | Working on a real fixture | One actual Structured3D scene was converted successfully. This begins with Structured3D geometry annotations, not with a photograph or GLB. |
| SpatialLM output to `PlanGrid` | Parser implemented | Weights and parser exist, but no confirmed end-to-end inference run was found. |
| Native GLB preflight | Implemented but uncommitted | Strict container, resource, extension, size, digest, scene-contract, and attestation checks pass 21 tests. It deliberately stops at `REVIEW_REQUIRED`. |
| Arbitrary 3D model to tags | Not yet implemented end to end | Rendering, semantic normalization, model-to-`PlanGrid`, multi-view aggregation, and evidence binding still need to be joined. |

## 1. Ordinary 2D Image Tagging

### Canonical web pipeline

The main application is:

`/Users/davidusa/REPOS/Image_Tagger_dk_latest/Image_Tagger_3.4.74_vlm_lab_TL_runbook_full`

Its central science files are:

- `backend/science/pipeline.py`
- `backend/services/science_runs.py`
- `backend/models/science_runs.py`

The pipeline includes analyzers for:

- color and palette properties;
- visual complexity and clutter;
- MPIB low-level features;
- GLCM texture;
- fractal measures;
- symmetry;
- naturalness, fluency, and biophilia proxies;
- depth and spatial proxies;
- room detection;
- heuristic material summaries;
- optional cognitive and semantic VLM analyses;
- optional OneFormer segmentation;
- optional Gemini, CLIP, and SigLIP material analysis;
- optional affordance inference.

The important qualification is that implementation and default production use are not the same. Segmentation, VLM analysis, and several advanced modules are opt-in. The affordance path has had a LightGBM compatibility problem. The default pipeline should therefore be described by what its current configuration actually runs, not by every analyzer present in the source tree.

### CNFA annotation socket

The cognitively motivated research engine is separate:

- `/Users/davidusa/REPOS/Image_Tagger_dk_latest/cnfa_algs/`
- `/Users/davidusa/REPOS/Image_Tagger_dk_latest/annotation_socket/`

The current registry contains:

- **68 total predicates**
- **40 image attributes**
- **28 plan metrics**
- **49 AMBER tier hints**
- **19 GREEN tier hints**

Representative image attributes include brightness variance, edge clarity, symmetry, palette entropy, visual processing load, clutter, fractal measures, glare, warm/cool balance, landmark salience, enclosure, prospect, acoustic-absorption proxies, light and shadow structure, sun patches, dark zones, texture, orderliness, verticality, ceiling and double-height cues, blind corners, barrier permeability, thresholds, feature congestion, and subband entropy.

Plan-related outputs include visual integration, connectivity, intelligibility, wayfinding load, setting fit, choice richness, spatial generosity, triangulation, and stranded amenity. Some are inferred from image evidence; others properly require declared inputs such as seating, glazing, acoustic data, facade data, or controls.

This engine has a stronger scientific output contract than a simple list of labels. It can return localized fields or regions, a scalar, confidence, method, evidence chain, tier, and an explicit abstention.

There is no evidence that the web application's canonical science pipeline currently imports and runs `cnfa_algs` or `annotation_socket`. They should therefore be treated as parallel systems until an integration path is implemented and tested.

### Fresh audit run

A fresh three-image socket run processed an office, a classroom corridor, and the Farnsworth House:

```text
queue: 3
worker processed: 3
checker: GREEN=0, AMBER=2, RED=1
```

The corridor produced 47 applicable predicates with 21 abstentions. The office produced 49 applicable predicates with 19 abstentions. Both were AMBER. The Farnsworth image was RED because two predicates remained `UNKNOWN` after anchor registration was judged unconfident. This was a fail-closed result, not an inability to read the image.

The seeded fabricated control was rejected and did not enter accepted output. A second identical run skipped all three inputs through content-addressed replay. Attempts by the worker to write checker-controlled acceptance fields were denied.

The annotation socket test suite currently reports **33 passed and 4 failed**. The four failures refer to a hard-coded absent Linux fixture path. This is a portability defect that should be repaired; it is not evidence that all algorithms pass.

## 2. Inferring Activities and Room Use from 2D Images

Relevant files are:

- `docs/ACTIVITY_PREDICTION_FRAMEWORK.md`
- `cnfa_algs/activity.py`
- `cnfa_algs/vlm_activity_prompt.py`

The implementation contains a 24-item activity vocabulary, including walking, wayfinding, waiting, focused work, contemplation, people-watching, private calls, eating, dyadic and group interaction, presentations, restorative pauses, play, and meditation.

Two approaches are present:

1. An attribute-profile matcher relates visual and spatial attributes to possible activity support.
2. A structured VLM prompt estimates activity likelihood and can be compared with the attribute-based prediction.

These should be named carefully. An image can support a claim such as "this setting affords waiting" or "focused work appears poorly supported." It cannot by itself establish that people actually wait there, how often they do so, or whether they perform well. Observed behavior requires occupancy evidence, video, traces, surveys, or a designed experiment.

The companion attribute-mining brief is:

`/Users/davidusa/REPOS/Image_Tagger_dk_latest/docs/IMAGE_TAGGER_SPACE_USE_ATTRIBUTE_MINING_BRIEF_2026-07-29.md`

It proposes additional relational attributes derived from the room-activity work.

## 3. Image-to-Geometry Work

The repository contains adapters or catalog entries for:

- Depth Anything V2;
- Depth Pro;
- Marigold;
- SegFormer plane segmentation;
- ESANet RGB-D segmentation;
- HAWP wireframes;
- uLayout room geometry;
- SpatialLM;
- Structured3D;
- saliency models.

Collected external assets occupy roughly 9.3 GB, with Structured3D archives occupying roughly 13 GB. Depth Anything V2, Mask2Former, SegFormer, GroundingDINO, OWLv2, CLIP, and SpatialLM assets are present.

The adapter smoke suite reports **11 passed, 0 failed**, but all optional model availability checks were false for Depth Pro, HAWP, uLayout, ESANet, Marigold, and TranSalNet. Those tests establish imports and controlled fallback behavior, not successful model inference.

Depth Anything V2 deserves a precise note:

- The full ONNX model is present.
- An ONNX Runtime session can load it and reports the input `pixel_values`.
- The normal system Python lacks `onnxruntime` and falls back to geometric depth.
- In the collection virtual environment, the adapter fails on dynamic ONNX dimensions because it tries to convert the string dimension `width` to an integer.
- A further OpenCV line-output shape incompatibility appeared in the vanishing-point fallback.

Thus the model asset is usable in principle, but the present adapter is not operational end to end. Its calibrated output is also described as "metric-ish"; it is not a substitute for measured metric geometry.

## 4. Geometry and Plan Analysis Already Available

The project's `PlanGrid` abstraction is important. Once reliable geometry and semantic anchors have been converted to this representation, the existing CNFA modules can calculate or estimate:

- visibility and isovist properties;
- space-syntax measures;
- connectivity and intelligibility;
- movement and route properties;
- line of sight;
- wayfinding and landmark relations;
- setting classification;
- seating, crowding, and social configuration;
- view and daylight proxies;
- some acoustic simulations or proxies.

A real Structured3D annotation was converted during this audit:

```text
shape: (260, 260)
cell_m: 0.0498440825
confidence: 0.98
FREE: 31407
UNKNOWN: 26230
OBSTACLE: 9963
```

This proves one real annotation-to-`PlanGrid` route. It does not prove photograph-to-plan inference or native model ingestion.

The SpatialLM adapter can parse model output describing walls, doors, windows, furniture, and seat orientation, then rasterize it to `PlanGrid`. SpatialLM weights are present, but the repository contains no confirmed real inference run from an architectural input through SpatialLM to accepted CNFA tags.

## 5. Native 3D Model Intake

The following currently appear as untracked files in the Image_Tagger repository:

- `model_intake_core/README.md`
- `model_intake_core/glb_preflight.py`
- `model_intake_core/scene_contract.py`
- `model_intake_core/digests.py`
- `model_intake_core/attestation.py`
- `model_intake_core/sprint_ledger.py`
- `tests/test_model_intake_core.py`

The 21 tests pass. They cover:

- GLB header, container, and chunk validation;
- embedded-resource and external-reference rules;
- required-extension checks;
- triangle limits;
- malformed and truncated inputs;
- canonical and package digests;
- normalized-scene semantic and referential checks;
- readiness attestation and role separation;
- sprint dependency and negative-evidence validation.

The assurance boundary is deliberately narrow. The component validates GLB structure and emits `REVIEW_REQUIRED`. It does not:

- render the model;
- replace the Khronos validator;
- infer architectural semantics;
- derive `PlanGrid`;
- calculate image or spatial tags;
- certify behavioral or cognitive claims.

No real `.glb`, `.gltf`, `.ifc`, `.obj`, `.fbx`, `.skp`, or `.rvt` fixture was found in the repository. The existing tests generate minimal GLB bytes. The model-intake specification sensibly proposes GLB as the first supported format, IFC next, and other formats later.

The larger working specifications presently live outside the Image_Tagger repository:

- `/Users/davidusa/Documents/New project/MODEL_INTAKE_WORKBENCH_SPEC_2026-07-29.md`
- `/Users/davidusa/Documents/New project/MODEL_INTAKE_SPRINT_SYSTEM_2026-07-29.md`

These should eventually be placed under an agreed, versioned documentation or contract location.

## 6. The Correct Combined Architecture

A reliable system should use both model-native evidence and rendered visual evidence:

```text
Native GLB
  -> structural preflight and official validation
  -> scale, axis, unit, material, and semantic review
  -> normalized scene package
       -> geometry/topology -> PlanGrid -> spatial and relational metrics
       -> canonical rendered views -> existing 2D taggers
       -> object/material metadata -> semantic tags
  -> cross-view and cross-substrate aggregation
  -> evidence-bound tag record with confidence, abstention, and provenance
```

This is preferable to reducing the 3D model to screenshots alone. Rendered views are valuable for visible appearance, but model geometry is the better source for topology, distances, connectivity, occlusion, route structure, and scale. Conversely, model geometry alone may omit the perceptual effects of lighting, material, texture, camera position, and view composition.

## 7. Recommended Next Work

1. **Review and commit the GLB intake core.** It is currently untracked and therefore not yet a stable repository capability.
2. **Obtain one real representative GLB from Tanishq or Stephan.** Run both the local preflight and the official Khronos validator; preserve the reports as fixtures.
3. **Implement normalized-scene-to-`PlanGrid`.** This is the central missing bridge between native 3D intake and the existing plan-analysis engine.
4. **Implement canonical multi-view rendering.** Define fixed camera selection, lighting profiles, image dimensions, and view provenance. Run the established 2D pipeline on every view.
5. **Aggregate tags conservatively.** Preserve per-view results; distinguish invariant model properties from view-dependent properties; abstain when views disagree without a principled aggregation rule.
6. **Repair Depth Anything V2 integration.** Handle dynamic ONNX input dimensions, package a reproducible runtime, and add a real inference test plus geometric sanity checks.
7. **Add real fixtures for Structured3D and SpatialLM.** Keep the verified Structured3D scene and add a real SpatialLM output or run. Test both positive and corrupted inputs.
8. **Integrate CNFA outputs into the canonical science-run contract.** At present, the research engine and web pipeline appear separate.
9. **Validate perceptual and activity tags against people.** Use human ratings, room-use observations, or experiments. Vision-derived affordances must not be presented as observed behavior.

## Bottom Line

The project already has a substantial 2D architectural vision system and a useful spatial-analysis engine. It also has the beginnings of a disciplined 3D intake path. The shortest route to a genuine 3D tagger is not to invent another classifier. It is to connect four existing pieces: validated GLB intake, normalized geometry, `PlanGrid` analysis, and canonical multi-view use of the 2D taggers.

Until that bridge is built and tested on real models, the accurate claim is:

> Image_Tagger can analyze 2D architectural images and supplied or inferred spatial representations; it is preparing, but does not yet provide, end-to-end native 3D model tagging.
