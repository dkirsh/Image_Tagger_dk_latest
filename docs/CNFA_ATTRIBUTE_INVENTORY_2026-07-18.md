# CNfA ATTRIBUTE INVENTORY — have + planned, with existing-fraction check
### Image_Tagger / CNfA · 2026-07-18 (Cowork)

*A complete inventory of the CNfA viz attributes we HAVE built and are PLANNING to make operational,
with — per David's request — a column checking whether the attribute (or a **fraction** of it) already
exists in the codebase, so nothing is rebuilt from scratch. Same state vocabulary as the well-being
appendix.*

**State key.** DONE+EXT = built + survived an external adversarial review (Fable panel and/or Codex
attack). DONE+INT = built + internally (unit/harness) tested, not yet externally attacked.
SPEC+PLAN = committee/panel-spec'd, skeptic-verified, in a build order, not yet built. NEEDS PLAN /
REJECTED as noted. "(AMBER)" = honest measurement ceiling; "(AMBER proxy)" = an honest proxy, not the
faithful published algorithm.

**How to read the "existing fraction" column.** It names existing operators a planned attribute would
REUSE or overlaps with — a heuristic reuse map, not an authoritative dedup. "(new — no existing
fraction)" means it needs building from primitives. The compound section always reuses existing base
measures by construction (that is what makes it a compound).

**Counts (2026-07-18).** 27 socket predicates BUILT + 18 plan/well-being operators registered (abstain
without inputs) = **45 operational operators**. Planned: **56 committee primitives** (6 already built)
+ **48 panel compounds** (2 already built). Demand-side catalog: the 424-construct canonical registry
(`TRS_v1.1/…/cnfa_tag_registry_canonical_v0.2.8.yaml`) — ~30 of the planned primitives fill a slot it
already lists.

---

## A. BUILT / OPERATIONAL  (in the annotation socket today; run on a real image)


### Base Tier-A image attrs (pre-existing)

| id | tier | state |
|---|---|---|
| `cnfa.light.brightness_variance` | GREEN | DONE+INT |
| `cnfa.fluency.edge_clarity_mean` | GREEN | DONE+INT |
| `cnfa.fluency.symmetry_score_horizontal` | GREEN | DONE+INT |
| `cnfa.fluency.color_palette_entropy` | GREEN | DONE+INT |
| `cnfa.fluency.processing_load_proxy` | GREEN | DONE+INT |
| `cnfa.fractal_dimension` | GREEN | DONE+INT |
| `glare-risk` | GREEN | DONE+INT |
| `cnfa.light.warm_vs_cool_ratio` | GREEN | DONE+INT |
| `cnfa.cognitive.landmark_salience` | GREEN | DONE+INT |
| `cnfa.spatial.enclosure_index` | AMBER | DONE+INT |
| `cnfa.spatial.prospect` | AMBER | DONE+INT |
| `acoustic_absorption_proxy` | AMBER | DONE+INT |
| `cnfa.light.vertical_illuminance_proxy` | AMBER | DONE+INT |

### Reliable-A sprint image attrs (this session)

| id | tier | state |
|---|---|---|
| `cnfa.fluency.spectral_slope_deviation` | AMBER | DONE+EXT (AMBER proxy) |
| `cnfa.fluency.edge_orientation_entropy` | AMBER | DONE+EXT (AMBER proxy) |
| `cnfa.geometry.contour_angularity` | AMBER | DONE+EXT (AMBER proxy) |
| `cnfa.fluency.grayscale_gabor_entropy_proxy` | AMBER | DONE+EXT (AMBER proxy) |
| `cnfa.fluency.local_congestion_proxy` | AMBER | DONE+EXT (AMBER proxy) |
| `cnfa.fluency.fractal_mid_d_band` | AMBER | DONE+EXT (AMBER proxy) |

### Plan metrics from inferred plan

| id | tier | state |
|---|---|---|
| `C1.visual_integration` | AMBER | DONE+EXT (Fable panel) |
| `C2.connectivity` | AMBER | DONE+EXT (Fable panel) |
| `C3.intelligibility` | AMBER | DONE+EXT (Fable panel) |
| `C4.wayfinding_load` | AMBER | DONE+EXT (Fable panel) |
| `C13.setting_fit` | AMBER | DONE+EXT (Fable panel) |
| `C24.spatial_generosity` | AMBER | DONE+EXT (Fable panel) |

### Compound social predicates (this session)

| id | tier | state |
|---|---|---|
| `C01.triangulation_ignition` | AMBER | DONE+EXT (AMBER) |
| `C29.stranded_amenity_index` | AMBER | DONE+EXT (AMBER) |

### Plan / well-being operators (registered; ABSTAIN without their spec input)

| criterion | operator | needs input | state |
|---|---|---|---|
| C5 | collaborator_proximity | seats,collab | DONE+EXT (Fable panel); needs input |
| C6 | path_overlap | seats,dest | DONE+EXT (Fable panel); needs input |
| C7 | speech_privacy | collab,focus | DONE+EXT (Fable panel); needs input |
| C8 | distraction_distance | acoustic params | DONE+EXT (Fable panel); needs input |
| C9 | view_equity | seats,glazing | DONE+EXT (Fable panel); needs input |
| C10 | daylight_proximity | seats,glazing | DONE+EXT (Fable panel); needs input |
| C11 | prospect_refuge | seats | DONE+EXT (Fable panel); needs input |
| C12 | crowding_risk | seats | DONE+EXT (Fable panel); needs input |
| C14 | focus_collab_separation | collab,focus | DONE+EXT (Fable panel); needs input |
| C15 | active_design | seats,amenities | DONE+EXT (Fable panel); needs input |
| C16 | territory | territory spec | DONE+EXT (Fable panel); needs input |
| C17 | local_control | control zones | DONE+EXT (Fable panel); needs input |
| C18 | air_quality | air spec | DONE+EXT (Fable panel); needs input |
| C19 | restoration_nature | seats,nature cells | DONE+EXT (Fable panel); needs input |
| C20 | chronic_soundscape | collab sources | DONE+EXT (Fable panel); needs input |
| C21 | thermal | seats,glazing | DONE+EXT (Fable panel); needs input |
| C22 | circadian_contrast | seats,glazing | DONE+EXT (Fable panel); needs input |
| C23 | social_connectedness | seats,commons | DONE+EXT (Fable panel); needs input |
---

## B. PLANNED PRIMITIVES  (committee 2026-07-15; not yet built unless noted)

| id | attribute | reg | existing fraction to reuse | state |
|---|---|---|---|---|
| V1 | `contour_angularity_index` | SHARED | V1 contour; edge_clarity/V13 | **DONE+EXT (AMBER, built)** |
| V2 | `spectral_discomfort_deviation` | WB | V2 spectral_slope; V2 | **DONE+EXT (AMBER, built)** |
| V3 | `visible_vegetation_fraction` | WB | (none — new); C9/C10/prospect | SPEC+PLAN |
| V4 | `mystery_occlusivity` | SHARED | C19 restoration; (none — new); (none — new isovist) | SPEC+PLAN (needs input) |
| V5 | `window_view_layer_content` | SHARED | brightness_variance/glare; prospect/daylight; C9/C10/prospect | SPEC+PLAN |
| V6 | `subband_entropy_clutter` | SHARED | processing_load/V6/V7; V6; palette_entropy/V6 | **DONE+EXT (AMBER, built)** |
| V7 | `feature_congestion_clutter` | COG | processing_load/V6/V7; V6/V7 clutter; V7 | **DONE+EXT (AMBER, built)** |
| V8 | `spectral_naturalness` | WB | V2 spectral_slope; V2/V8; V13 orient_entropy | SPEC+PLAN (AMBER) |
| V9 | `fractal_mid_d_band_score` | SHARED | fractal_dimension/V9 | **DONE+EXT (AMBER, built)** |
| V10 | `landmark_differentiation` | COG | landmark_salience | SPEC+PLAN |
| V11 | `route_angular_continuity` | COG | V1 contour; C6 path_overlap; C4 wayfinding | SPEC+PLAN (AMBER) |
| V12 | `natural_material_fraction` | WB | materials cues (attributes); material coverage | SPEC+PLAN (AMBER) |
| V13 | `edge_orientation_entropy` | SHARED | V13 orient_entropy; edge_clarity/V13; palette_entropy/V6 | **DONE+EXT (AMBER, built)** |
| V14 | `luminance_histogram_shape` | WB | brightness_variance/glare; C9/C10/prospect | SPEC+PLAN (AMBER) |
| V15 | `spatial_contrast_composition` | COG | brightness_variance/glare; C10 daylight | SPEC+PLAN (AMBER) |
| V16 | `sun_patch_geometry` | SHARED | brightness_variance/glare | SPEC+PLAN (AMBER) |
| V17 | `popout_margin` | COG | (new — no existing fraction) | SPEC+PLAN |
| V18 | `vantage_prospect_refuge_balance` | WB | prospect + C11; C11 prospect-refuge; C1 VGA/prospect | SPEC+PLAN (needs input) |
| V19 | `boundary_permeability_split` | SHARED | C9/C10/prospect; enclosure_index; C1 VGA/prospect | SPEC+PLAN (AMBER) |
| V20 | `decision_point_preview_depth` | COG | V13 orient_entropy; C9/C10/prospect; depth (geometry) | SPEC+PLAN (AMBER) |
| V21 | `ceiling_height_percept` | SHARED | V1 contour; (none — needs height) | SPEC+PLAN (AMBER) |
| V22 | `light_directionality_modelling` | SHARED | brightness_variance/glare | SPEC+PLAN (AMBER) |
| V23 | `wall_luminance_dominance` | SHARED | brightness_variance/glare | SPEC+PLAN (AMBER) |
| V24 | `visible_window_wall_ratio` | WB | prospect/daylight | SPEC+PLAN (AMBER) |
| V25 | `threshold_doorway_density` | COG | (new — no existing fraction) | SPEC+PLAN (AMBER) |
| V26 | `choice_point_option_differentiation` | COG | V13 orient_entropy | SPEC+PLAN (AMBER) |
| V27 | `signage_salience` | COG | landmark_salience; C4 wayfinding | SPEC+PLAN (AMBER) |
| V28 | `eye_level_information_richness` | SHARED | (new — no existing fraction) | SPEC+PLAN (AMBER) |
| V29 | `edge_following_affordance` | SHARED | edge_clarity/V13 | SPEC+PLAN (AMBER) |
| V30 | `scaling_coherence_octaves` | COG | (new — no existing fraction) | SPEC+PLAN |
| V31 | `curved_sightline_promise` | SHARED | V1 contour; C9/C10/prospect; C6 path_overlap | SPEC+PLAN (AMBER) |
| V32 | `scene_coherence_grouping` | SHARED | (new — no existing fraction) | SPEC+PLAN (AMBER) |
| V33 | `isovist_jaggedness` | COG | C1 VGA/prospect; C17 local_control | SPEC+PLAN (AMBER) |
| V34 | `maintenance_dilapidation_index` | WB | (none — needs height) | REJECTED |
| V35 | `visible_workstation_density` | SHARED | C18 | SPEC+PLAN (AMBER) |
| V36 | `peripheral_crowding_load` | COG | C19 restoration; C9/C10/prospect; C12 crowding | SPEC+PLAN (AMBER) |
| V37 | `isovist_radial_asymmetry` | SHARED | symmetry; C1 VGA/prospect | SPEC+PLAN (AMBER) |
| V38 | `isovist_drift` | COG | C1 VGA/prospect | SPEC+PLAN (needs input) |
| V39 | `blank_frontage_run_length` | SHARED | edge_clarity/V13 | SPEC+PLAN (AMBER) |
| V40 | `vista_termination_salience` | COG | landmark_salience; C6 path_overlap; depth (geometry) | SPEC+PLAN (AMBER) |
| V41 | `view_depth_layering` | WB | C9/C10/prospect; depth (geometry) | SPEC+PLAN (AMBER) |
| V42 | `egress_aperture_salience` | SHARED | landmark_salience; C4/legibility | REJECTED |
| V43 | `material_perceived_warmth` | WB | materials cues (attributes); warm/cool ratio; palette_entropy | SPEC+PLAN (AMBER) |
| V44 | `spectral_expansion` | COG | V2 spectral_slope; V13 orient_entropy | SPEC+PLAN (AMBER) |
| V45 | `proto_object_set_size` | COG | processing_load/V6/V7 | SPEC+PLAN (AMBER) |
| V46 | `nested_symmetry_index` | COG | symmetry | SPEC+PLAN (AMBER) |
| V47 | `phog_self_similarity` | COG | V13 orient_entropy | SPEC+PLAN (AMBER) |
| V48 | `hominess_composite` | WB | materials cues (attributes) | REJECTED |
| V49 | `desk_personalization_index` | SHARED | depth (geometry); C16 territory | SPEC+PLAN (AMBER) |
| V50 | `spectral_openness` | SHARED | V2 spectral_slope; prospect/daylight | SPEC+PLAN (AMBER) |
| V51 | `spectral_mean_depth` | SHARED | V2 spectral_slope; C19 restoration; depth (geometry) | SPEC+PLAN (AMBER) |
| V52 | `size_hierarchy_exponent` | COG | (new — no existing fraction) | REJECTED |
| V53 | `water_feature_presence` | WB | V7 | SPEC+PLAN (needs input) |
| V54 | `facade_pareidolia_salience` | COG | landmark_salience | REJECTED |
| V55 | `floor_guidance_continuity` | COG | edge_clarity/V13; C6 path_overlap | SPEC+PLAN (AMBER) |
| V56 | `patina_wear_index` | WB | C19/materials | REJECTED |

---

## C. PLANNED COMPOUNDS  (panel 2026-07-15; not yet built unless noted)

| id | compound | reg | reuses existing base measures | state |
|---|---|---|---|---|
| C01 | `triangulation_ignition_field` | None | reuses: landmark salience, C1 visual integration (VGA), C6 path overlap | **DONE+EXT (AMBER, built)** |
| C02 | `triangulated_conversation_permission` | None | reuses: landmark salience, C1 visual integration (VGA), acoustic absorption proxy | SPEC+PLAN (AMBER) |
| C03 | `conversation_initiation_propensity` | None | reuses: social.sociopetal, mean/variance depth (Hall band), enclosure index (barrier) | SPEC+PLAN (needs input) |
| C04 | `huddle_shelter_viability` | None | reuses: C7 speech privacy (STI to others), C11 prospect-refuge / enclosure, C1 visual integration | SPEC+PLAN (needs input) |
| C05 | `reverberant_affect_masking_flag` | None | reuses: warm/cool ratio, material coverage (wood), acoustic absorption proxy | SPEC+PLAN |
| C06 | `transit_vs_dwell_classifier` | None | reuses: C1 visual integration, C2 connectivity, C6 path overlap | SPEC+PLAN (AMBER) |
| C07 | `focus_zone_viability` | None | reuses: C7 speech privacy (STI), C8 distraction distance, C11 prospect-refuge | SPEC+PLAN (AMBER) |
| C08 | `approach_propensity_field` | None | reuses: curvature/rectilinearity index, enclosure index, processing-load/clutter (Rosenholtz) | SPEC+PLAN (AMBER) |
| C09 | `window_prospect_glare_antagonism` | None | reuses: prospect (view depth), vertical illuminance / daylight proxy, glare risk | SPEC+PLAN (AMBER) |
| C10 | `organized_complexity_dwell` | None | reuses: fractal dimension (global+local), colour palette entropy, processing-load/clutter (Rosenholtz) | SPEC+PLAN (AMBER) |
| C11 | `sittable_prospect_ledge` | None | reuses: prospect (view depth), enclosure index, acoustic absorption proxy | SPEC+PLAN (needs input) |
| C12 | `sun_seat_amenity_colocation` | None | reuses: sun-patch geometry, landmark salience, C21 thermal comfort proxy | SPEC+PLAN (needs input) |
| C13 | `self_congestion_conversation_pinch` | None | reuses: C6 path overlap, threshold density, C12 crowding risk | SPEC+PLAN (AMBER) |
| C14 | `triangulation_vs_decoration_ratio` | None | reuses: landmark salience, C1 visual integration, C24 spatial generosity/awe | SPEC+PLAN (AMBER) |
| C15 | `solitary_retreat_affordance` | None | reuses: social.sociopetal (inverted), C11 prospect-refuge, C6 path overlap | SPEC+PLAN (AMBER) |
| C16 | `proxemic_intrusion_stress` | None | reuses: mean/variance depth (Hall intimate band), social.sociopetal, enclosure index (barrier) | SPEC+PLAN (needs input) |
| C17 | `co_awareness_integration` | None | reuses: C1 visual integration, prospect (view depth) | SPEC+PLAN (AMBER) |
| C18 | `waiting_position_desirability` | None | reuses: prospect (view depth), C11 prospect-refuge, C1 visual integration | SPEC+PLAN (AMBER) |
| C19 | `collaboration_bump_field` | None | reuses: C6 path overlap, C5 collaborator proximity, C23 social connectedness (commons gravity) | SPEC+PLAN (AMBER) |
| C20 | `group_audibility_reserve` | None | reuses: acoustic absorption proxy, material coverage (hard surfaces), enclosure index | SPEC+PLAN (AMBER) |
| C21 | `speech_privacy_gradient` | None | reuses: acoustic absorption proxy, enclosure index, C8 distraction distance | SPEC+PLAN (needs input) |
| C22 | `cocktail_party_suppression` | None | reuses: C12 crowding risk, acoustic absorption proxy, enclosure index | SPEC+PLAN (AMBER) |
| C23 | `felt_safety_field` | None | reuses: prospect (view depth), enclosure index, brightness variance | SPEC+PLAN (AMBER) |
| C24 | `lingering_affordance` | None | reuses: felt_safety_field, C11 prospect-refuge, C12 crowding risk | SPEC+PLAN (AMBER) |
| C25 | `prospect_refuge_polarity` | None | reuses: prospect (view depth), enclosure index, C1 visual integration | SPEC+PLAN (AMBER) |
| C26 | `safety_perception_masking_gap` | None | reuses: vertical illuminance proxy, prospect (view depth), processing-load/clutter proxy | REJECTED |
| C27 | `restorative_refuge_window` | None | reuses: prospect (view depth), enclosure index, mystery occlusivity | SPEC+PLAN (AMBER) |
| C28 | `natural_surveillance_reassurance` | None | reuses: C1 visual integration, C11 prospect-refuge, landmark salience | SPEC+PLAN (needs input) |
| C29 | `stranded_amenity_index` | None | reuses: landmark salience, perceptual-fluency affect, C1 visual integration | **DONE+EXT (AMBER, built)** |
| C30 | `restorative_social_nook_score` | None | reuses: visible vegetation fraction, soft-material composite (specularity inverse, texture homogeneity, wood/upholstery coverage), acoustic absorption proxy | SPEC+PLAN (AMBER) |
| C31 | `recovery_seat_index` | None | reuses: prospect (view depth), visible vegetation fraction (distal-view region only), C11 prospect-refuge / enclosure (protected back) | SPEC+PLAN (AMBER) |
| C32 | `soft_fascination_field` | None | reuses: visible vegetation fraction, fractal dimension (global+local), processing-load/clutter proxy | SPEC+PLAN (AMBER) |
| C33 | `green_commons_gravity` | None | reuses: visible vegetation fraction, C1 visual integration / C23 commons gravity, seating presence | SPEC+PLAN (AMBER) |
| C34 | `daylit_talk_pocket` | None | reuses: vertical illuminance / daylight proxy, acoustic absorption proxy, glare risk | SPEC+PLAN (AMBER) |
| C35 | `hominess_nook_index` | None | reuses: material coverage (wood), warm/cool ratio, enclosure index | SPEC+PLAN (AMBER) |
| C36 | `angular_specular_avoidance` | None | reuses: contour angularity, specularity proxy, edge clarity | SPEC+PLAN (AMBER) |
| C37 | `threshold_invitation_gradient` | None | reuses: approach_propensity_field, mystery occlusivity, decision-point preview | SPEC+PLAN (AMBER) |
| C38 | `fluency_discomfort_mask` | None | reuses: perceptual-fluency proxy (symmetry + edge clarity + fractal-fit), spectral discomfort deviation | SPEC+PLAN (AMBER) |
| C39 | `cozy_dim_circadian_deficit` | None | reuses: warm/cool ratio, vertical illuminance proxy, brightness variance | SPEC+PLAN (needs input) |
| C40 | `biophilic_air_quality_halo` | None | reuses: C19 restoration/nature contact, visible vegetation fraction, enclosure index | SPEC+PLAN (needs input) |
| C41 | `visual_refuge_acoustic_leak_false_shelter` | None | reuses: enclosure index, C11 prospect-refuge, acoustic absorption proxy | SPEC+PLAN (AMBER) |
| C42 | `hue_heat_thermal_comfort_illusion` | None | reuses: warm/cool ratio, material coverage (glass), colour palette entropy | REJECTED |
| C43 | `total_environmental_load_superadditive` | None | reuses: glare risk, acoustic absorption proxy, warm/cool ratio | SPEC+PLAN (AMBER) |
| C44 | `agency_buffered_load` | None | reuses: glare risk, acoustic absorption proxy, C17 local control | SPEC+PLAN (needs input) |
| C45 | `thermal_acoustic_misattribution_index` | None | reuses: warm/cool ratio, material coverage (wood/stone), acoustic absorption proxy | SPEC+PLAN (needs input) |
| C46 | `load_gated_conversation_suppression` | None | reuses: landmark salience, C1 visual integration, glare risk | SPEC+PLAN (AMBER) |
| C47 | `designed_in_conflict_flag` | None | reuses: enclosure index, acoustic absorption proxy, C7 speech privacy (STI) | SPEC+PLAN (AMBER) |
| C48 | `belonging_anchorage` | None | reuses: C16 territoriality, enclosure index, warm/cool ratio | SPEC+PLAN (needs input) |
---

## Notes on overlap / "fractions already exist"

The most important reuse findings from the check:

- **Clutter family already overlaps.** V6/V7 (built) + the legacy `processing_load_proxy` all measure
  clutter — Decision D2 says pick ONE for hedonics; do NOT build a fourth clutter primitive.
- **Fractal family.** V9 (built) reuses `fractal_dimension` (built) — no recompute. Any further fractal
  primitive (lacunarity, 1/f spectral slope) partially overlaps `fractal_dimension` + V2 spectral slope.
- **Vegetation/nature.** V3 visible_vegetation is genuinely NEW as an image operator, but the *construct*
  overlaps C19 restoration_nature (plan operator, needs a nature-cell map) — V3 is the image-only sibling.
- **Isovist/prospect family.** Several planned isovist primitives (occlusivity, jaggedness, radial
  asymmetry) reuse the C1 VGA + prospect geometry already built — fractional overlap, not new geometry.
- **Every compound reuses built base measures** (that is the definition) — the compound work is wiring,
  not new primitives, EXCEPT where a base measure it needs is itself only SPEC+PLAN.

## Owed before any planned row is trusted
Same as the reviews: faithful reimplementation where a built row is an AMBER proxy; Mac↔sandbox replay;
Article_Eater grounding of anchors; labeled corpus for calibration. See
`docs/CODEX2_ATTACK_DISPOSITION_2026-07-18.md` and `docs/COMPOUND_IMPLEMENTATION_PLAN_2026-07-15.md`.
