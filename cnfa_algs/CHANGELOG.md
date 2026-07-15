# cnfa_algs CHANGELOG

All notable changes to the cognitive-code computation engine.

---

## v0.3 — 2026-07-15 (AG session)

### Added
- **`spatial_syntax.py`** — Full space-syntax simulation pipeline:
  BEV grid from depth+planes, Visibility Graph Analysis (Turner 2001),
  agent-based pedestrian simulation (Hillier 1996), three rendering
  styles (heatmap/dots/silhouettes, default heatmap). Produces three
  new attributes: `cnfa.social.predicted_occupancy`,
  `cnfa.social.movement_traces`, `cnfa.social.clustering_hotspots`.
  Confidence capped at 0.45 (single-image FOV limitation).
- **`vlm_activity_prompt.py: build_populated_prompt()`** — Second-pass
  VLM query for occupancy overlay evaluation.
- **`ARCHITECTURE.md`** — Module dependency graph, data flow diagrams,
  full inventory of 26 modules with purpose and key exports.
- **`JUSTIFICATION_TABLE.md`** — 20 new parameter entries for spatial
  syntax (BEV grid, VGA, agents, rendering, confidence).
- **`tests/test_spatial_syntax.py`** — 15 unit tests on synthetic grids.
- **`validation/ADVERSARIAL_REVIEW_SPATIAL_SYNTAX_2026-07-15.md`** —
  25-probe adversarial review by 4 simulated domain experts.
  Result: 15 pass, 8 fail, 2 conditional. Key findings: furniture
  blindness, 2-step ≠ real integration, flat-world assumption,
  no attractor model.

### Known issues (from adversarial review)
- Agents walk through furniture (no furniture segmentation layer)
- 2-step integration approximation loses global syntactic signal
- Monocular depth has no metric scale (grid_res units are arbitrary)
- No attractor model (configuration-only, ~30-50% of indoor variance)
- Confidence cap 0.45 may be generous for indoor-without-attractors

---

## v0.2 — 2026-07-14/15 (AG + Fable sessions)

### Added
- **`activity.py`** — 30-type activity taxonomy with attribute-based
  predictor, necessary conditions, and personality/time-of-day moderators.
- **`vlm_activity_prompt.py`** — Structured VLM prompt protocol for
  Gemini activity-likelihood rating + cross-validation framework.
- **`movement.py`** — Circulation scoring, wayfinding, decision-point
  analysis on PlanGrid.
- **`score_layout.py`** — Composite C1–C21 criteria scorer aggregating
  7 plan-space analysis modules.
- **`affordance.py`** — Prospect-refuge, territory, social distance
  scoring on PlanGrid.
- **`acoustics_plan.py`** — RT60 estimation, speech privacy zones.
- **`daylight_view.py`** — Daylight access, view quality scoring.
- **`thermal_plan.py`** — Thermal comfort zones, glazing effects.
- **`space_syntax.py`** — Axial-line integration on plan grids.
- **`wellbeing_plan.py`** — Biophilia, nature view, restoration potential.
- **`los.py`** — Supercover line-of-sight on plan grids (panel fix S1).
- **`validate_pipeline.py`** — Full pipeline smoke test.
- **`contracts.py`** — PlanGrid schema, C1–C21 criteria constants.
- **`JUSTIFICATION_TABLE.md`** — Initial table with ~40 parameter entries.
- **`validation/ADVERSARIAL_REVIEW_2026-07-14.md`** — 30-probe red-team
  of Tier-A attributes. Result: 20 pass, 9 fail, 0 crash.

### Fixed (from adversarial review v0.1)
- Key prefix: all attributes now use `cnfa.*` prefix
- Scalar range: fractal_dimension and prospect normalised to [0,1]
- Field shape: tile-grid fields upscaled to image dimensions
- NaN/Inf depth guards added
- 1×1 image guard (`MIN_DIM = 32`)
- k-means determinism (`cv2.KMEANS_PP_CENTERS`)

---

## v0.1 — 2026-07-13 (Fable session)

### Added
- **`core.py`** — `AttributeResult` schema, `heatmap_overlay`,
  `region_overlay`, `mask_overlay`, `gallery`, `save_results_json`.
- **`geometry.py`** — Vanishing point estimation, heuristic plane
  segmentation (k-means + spatial prior), `DepthProvider`
  (ONNX or geometric fallback).
- **`attributes.py`** — 14 Tier-A attributes: brightness_variance,
  edge_clarity, symmetry_horizontal, palette_entropy, processing_load,
  fractal_dimension_local, glare_risk, warmth_ratio,
  vertical_illuminance_proxy, enclosure_index, prospect,
  landmark_salience, acoustic_absorption_proxy, sociopetal_seating.
- **`plan.py`** — `infer_plan_from_image` (Tier B), `plan_from_floorplan_image`
  (Tier C), `isovist_fields` (openness, prospect, refuge, compactness).
- **`composition.py`** — `rule_of_thirds`, `visual_balance`.
- **`hedonics.py`** — Hedonic valence scoring.
- **`setting_classifier.py`** — Room-type classification.
- **`adapters/`** — External model wrappers for SegFormer, SpatialLM,
  Structured3D, pyroomacoustics.
- **`validation/`** — Credibility harness (L0–L3 probes, VLM judge).
- **`README.md`** — Package README with tier strategy and run instructions.
- **`CONTRACT.md`** — Pipeline schema, parallelism rules, delivery contract.

### Verified
- 16-image batch: corridor/office/glass-box clusters separate correctly.
- First credibility run (N=8): processing_load ρ=0.93, enclosure ρ=0.81.
