# Student Architectural Tag Sprint Contracts

Generated: 2026-07-07

Live repo surface: `/Users/davidusa/REPOS/Image_Tagger_dk_latest/Image_Tagger_3.4.74_vlm_lab_TL_runbook_full`

Companion backlog:

- `/Users/davidusa/REPOS/Image_Tagger_dk_latest/Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/docs/ARCHITECTURAL_TAG_OPERATIONAL_BACKLOG_2026-07-07.md`

## Purpose

These contracts turn the architectural tag backlog into verifiable student sprints. A sprint is complete only when its named files, tests, fixtures, and last-mile report pass. Plausible outputs are not enough.

## Global Contract

Every sprint must satisfy these rules.

| Rule | Requirement |
|---|---|
| Live root | Work only in `/Users/davidusa/REPOS/Image_Tagger_dk_latest/Image_Tagger_3.4.74_vlm_lab_TL_runbook_full`. Historical folders are reference-only unless named by the sprint. |
| Local evidence | Localizable tags must output bbox, mask, polygon, point, or explicit `whole_image`. |
| Global aggregate | Room/global tags must state denominator and aggregation rule. Example: `fenestration_ratio = accepted window/glass/opening area / visible boundary area`. |
| Provenance | Every output must include method, algorithm/version where relevant, confidence, and known failure modes. |
| Human validation | VLM or uncertain architectural-detail outputs are candidates until accepted by validator or human attestation. |
| Fixtures | Each sprint needs positive, negative, and ambiguous fixtures under `tests/fixtures/architectural_tags/`. |
| Visual inspection | Localized tags must be inspectable in an image viewer that overlays evidence regions on the source image. |
| Search inspection | Implemented tags must be searchable in a results gallery when they are ready for user-facing exploration. |
| Last mile | Each sprint writes an acceptance report under `reports/` with actual outputs, commands run, pass/fail results, and status `ACCEPTED`, `PARTIAL`, or `BLOCKED`. |

Minimum shared tests unless the sprint says otherwise:

```bash
pytest tests/test_feature_registry_coverage.py
pytest tests/test_science_pipeline_smoke.py
```

## Sprint S0: Student-Ready Repo Surface

| Field | Contract |
|---|---|
| Goal | Make the active repo and student path unambiguous. |
| Modify | `STUDENT_START_HERE.md`, `docs/STUDENT_ONBOARDING.md`, `README_v3.md` |
| Create | `reports/STUDENT_SPRINT_S0_REPO_SURFACE_ACCEPTANCE_2026-07-07.md` |
| Required work | Remove or qualify stale v3.3.7/v3.4.73 language; link the backlog and sprint contracts; state what folders are forbidden/historical. |
| Validation | `pytest tests/test_guardian.py`; `pytest tests/test_v3_api.py`; manual read-through confirms a student can identify active root, install route, test route, and first sprint. |
| Last mile | Report lists changed student-facing files, exact active root, commands run, and final status. |

## Sprint S1: Direct Image Statistics

| Field | Contract |
|---|---|
| Goal | Implement deterministic image statistics with no VLM calls. |
| Tags | `processing_load_proxy`, `brightness_variance`, `edge_clarity_mean`, `color_palette_entropy`, `symmetry_score_horizontal`, `fractal_dimension` |
| Modify | `backend/science/math/color.py`, `backend/science/math/complexity.py`, `backend/science/math/fluency.py`, `backend/science/math/fractals.py`, `backend/science/math/symmetry.py`, `backend/science/pipeline.py` |
| Optional create | `backend/science/math/architectural_primitives.py` |
| Tests | `tests/test_architectural_direct_stats.py` |
| Report | `reports/STUDENT_SPRINT_S1_DIRECT_STATS_ACCEPTANCE_2026-07-07.md` |
| Required work | Each tag returns finite numeric values; outputs are deterministic; debug artifacts are produced where practical. |
| Fixtures | flat image, high-edge image, high-color-variety image, symmetric image, asymmetric image, low/high brightness variance pair. |
| Validation | Values finite; expected monotonic direction on fixtures; deterministic across two runs; blank/invalid images fail safely. |
| Last mile | Report includes fixture, expected direction, observed value, pass/fail. |

## Sprint S2: Tag Evidence Envelope

| Field | Contract |
|---|---|
| Goal | Define the common record shape for local evidence and global aggregates. |
| Modify | `backend/science/core.py`, `backend/science/contracts.py`, `backend/models/attribute.py`, `contracts/attributes.yml` |
| Create | `contracts/architectural_tags.v1.json`, `tests/test_architectural_tag_contract.py`, `reports/STUDENT_SPRINT_S2_TAG_CONTRACT_ACCEPTANCE_2026-07-07.md` |
| Required work | Schema supports tag id, value, unit, scope, localizable flag, evidence regions, measurement method, algorithm/version, confidence, attestation, and failure modes. |
| Validation | Positive local/global examples pass; malformed records fail with exact reasons; bbox/mask/polygon shapes are validated. |
| Last mile | Report includes one accepted local example, one accepted global example, and one rejected malformed example. |

## Sprint S3: Materials And Surface Ratios

| Field | Contract |
|---|---|
| Goal | Convert material outputs into local masks/regions plus global ratios. |
| Tags | `materials-dominant-types`, `materials-naturalness-ratio`, `natural_material_ratio`, `material_diversity_index`, `surface-reflectance-sheen`, `glossy_surface`, `matte_surface`, `specular_reflectance` |
| Modify | `backend/science/vision/materials.py`, `backend/science/math/naturalness.py`, `backend/science/pipeline.py` |
| Tests | `tests/test_architectural_material_surface_ratios.py` |
| Report | `reports/STUDENT_SPRINT_S3_MATERIALS_ACCEPTANCE_2026-07-07.md` |
| Required work | Distinguish image-level guesses from region evidence; all ratios must declare denominator. Unknown material must not count as natural. |
| Fixtures | wood-heavy, glass-heavy, neutral/unknown, mixed-material. |
| Last mile | Report shows material class counts, area ratios, naturalness ratio, confidence, and caveats. |

## Sprint S4: Openings, Fenestration, And Boundary Permeability

| Field | Contract |
|---|---|
| Goal | Implement localized openings and global window/glass/opening ratios. |
| Tags | `boundary-opening-type`, `fenestration`, `fenestration-ratio`, `fenestration-pattern`, `clerestory_presence`, `skylight_presence`, `window_wall`, `curtain_wall`, `ribbon_window`, `aperture`, `doorway`, `archway`, `boundary-permeability`, `transparent_boundary`, `translucent_boundary`, `opaque_boundary`, `porosity` |
| Create | `backend/science/semantics/openings.py`, `backend/science/semantics/fenestration.py`, `tests/test_architectural_openings_fenestration.py`, `reports/STUDENT_SPRINT_S4_FENESTRATION_ACCEPTANCE_2026-07-07.md` |
| May modify | `backend/science/vision/segmentation.py`, `backend/science/semantics/ontology.py` |
| Required work | Candidate regions for openings; at least `fenestration_ratio`; false-positive guardrails for picture frames, mirrors, screens, light panels, and bright wall art. |
| Validation | Positive/negative/ambiguous fixtures; denominator explicit; uncertain `curtain_wall`, `ribbon_window`, and `fenestration-pattern` require human validation. |
| Last mile | Report includes at least 5 candidate regions with coordinates, numerator/denominator for ratio, false-positive outcomes, and pending-attestation list. |

## Sprint S5: Ceiling, Boundary Details, And Thresholds

| Field | Contract |
|---|---|
| Goal | Operationalize architect-specific details that students search for. |
| Tags | `ceiling-form`, `ceiling-form:vaulted`, `ceiling-form:domed`, `ceiling-form:coffered`, `ceiling-form:dropped`, `ceiling-form:exposed`, `ceiling_height_avg`, `threshold-type`, `threshold_emphasized`, `niche_presence`, `alcove_presence`, `window_seat_niche`, `soffit_presence`, `bulkhead_presence`, `cove_presence`, `cove_lighting_presence`, `wainscot_presence`, `dado_presence`, `plinth_presence`, `reveal_presence` |
| Create | `backend/science/semantics/ceiling_boundary.py`, `backend/science/semantics/thresholds.py`, `tests/test_architectural_ceiling_boundary_details.py`, `reports/STUDENT_SPRINT_S5_CEILING_BOUNDARY_ACCEPTANCE_2026-07-07.md` |
| May modify | `backend/science/semantics/arch_patterns_vlm.py`, `backend/science/spatial/depth.py` |
| Required work | Detail tags need region evidence or explicit whole-image scope. Human validation required for fine details until a reliable classifier exists. |
| Validation | Vaulted/coffered positives, flat-ceiling negative, ambiguous ornate ceiling, threshold positives/negatives. |
| Last mile | Report shows region evidence before/after, not just tag names. |

## Sprint S6: Spatial Layout, Affordance, And Social Visibility

| Field | Contract |
|---|---|
| Goal | Implement room-level spatial and affordance tags for search and later interpretation. |
| Tags | `enclosure_index`, `spatial_compression`, `plan_openness`, `open_plan`, `cellular_plan`, `axis`, `rhythm_repetition`, `pattern_rhythm_regularity`, `visual_privacy`, `prospect_to_refuge_ratio`, `prospect`, `refuge`, `spatial-legibility`, `landmark_salience`, `activity_zones_count`, `zoning_clarity`, `sociopetal_seating`, `interactional_visibility` |
| Create | `backend/science/spatial/architectural_layout.py`, `backend/science/context/social_visibility.py`, `tests/test_architectural_layout_affordance.py`, `reports/STUDENT_SPRINT_S6_LAYOUT_AFFORDANCE_ACCEPTANCE_2026-07-07.md` |
| May modify | `backend/science/spatial/depth.py`, `backend/science/spatial/isovist.py`, `backend/science/context/social.py`, `backend/science/context/affordance.py` |
| Required work | Separate geometric estimates from psychological interpretations; expose source components for prospect/refuge/privacy/social tags. |
| Validation | Open room, enclosed room, cluttered room, seating group, corridor/axis fixtures. |
| Last mile | Report shows component values for every composite, with actual numbers. |

## Sprint S7: Composite Search Scores And UI Readiness

| Field | Contract |
|---|---|
| Goal | Expose safe composite search terms without pretending they are direct facts. |
| Tags | `biophilic_design_score`, `restorative-capacity`, `intimacy_index`, `monumentality_index`, `serenity_index`, `tension_index`, `acoustic-reverberation-proxy`, `acoustic_absorption_proxy`, `thermal_comfort_proxy`, `olfactory_expectation_proxy` |
| Create | `backend/science/composites/architectural_search_scores.py`, `tests/test_architectural_composite_scores.py`, `reports/STUDENT_SPRINT_S7_COMPOSITES_ACCEPTANCE_2026-07-07.md` |
| May modify | `backend/science/summary.py`, `backend/science/index_catalog.py`, `docs/SCIENCE_TAG_MAP.md` |
| Required work | Composite scores list component inputs; missing components lower confidence or produce `insufficient_evidence`; nonvisual outputs are labelled as proxies. |
| Validation | Missing components do not produce confident outputs; component changes move scores in expected directions; output includes explanations. |
| Last mile | Report includes decomposed example search outputs. |

## Sprint S8: Annotation Viewer And Smart Search Gallery

| Field | Contract |
|---|---|
| Goal | Give users and reviewers a visual way to inspect localized annotations and search all tagged images. |
| User-facing features | Image viewer with annotation overlays; tag search page; smart results gallery; result cards that explain why an image matched. |
| Modify | `frontend/` app files for Research Explorer or a new architectural tag view; relevant API routers under `backend/api/` if needed; docs that point students/users to the page. |
| Likely create | `tests/test_architectural_annotation_viewer_smoke.py`, `tests/test_architectural_search_gallery_smoke.py`, `reports/STUDENT_SPRINT_S8_VIEWER_SEARCH_ACCEPTANCE_2026-07-07.md` |
| Required viewer behavior | Show image; toggle tags on/off; draw bbox/mask/polygon overlays; display tag id, ordinary-language meaning, value, confidence, method, and human-attestation status; distinguish candidates from accepted tags. |
| Required search behavior | Search by tag id and human vocabulary alias; filter by status/confidence; show all matching images in a gallery; each card shows matched tags, global values, and a link/open action for the annotation viewer. |
| Database readiness | Design for incoming image databases: pagination, empty states, loading states, no assumption that the corpus is small. |
| Validation | Smoke tests prove the viewer loads an image with at least one overlay and the search gallery returns deterministic fixture results for at least three query types: exact tag id, alias/common term, and global aggregate threshold. |
| Last mile | Report includes screenshots or saved render artifacts for the viewer and gallery; includes the exact test queries and result counts. |

## Final Release Gate

The tag expansion is student-ready only when:

- all completed sprint reports exist;
- sprint-specific tests pass;
- `pytest tests/test_feature_registry_coverage.py` passes;
- `pytest tests/test_science_pipeline_smoke.py` passes;
- each implemented tag is updated in `ARCHITECTURAL_TAG_OPERATIONAL_BACKLOG_2026-07-07.md`;
- each localizable tag has evidence-region support or an explicit whole-image exception;
- each global tag states its denominator or aggregation rule;
- every VLM-dependent tag is marked as candidate, human-validated, or validator-accepted.
- localized annotations are inspectable in an image viewer.
- searchable tags appear in a smart results gallery with match explanations.

Recommended final report:

- `/Users/davidusa/REPOS/Image_Tagger_dk_latest/Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/reports/STUDENT_ARCHITECTURAL_TAG_RELEASE_GATE_2026-07-07.md`
