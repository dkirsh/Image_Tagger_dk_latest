# Architectural Tag Operational Backlog

Generated: 2026-07-07

Live repo surface: `/Users/davidusa/REPOS/Image_Tagger_dk_latest/Image_Tagger_3.4.74_vlm_lab_TL_runbook_full`

Sprint contracts:

- `/Users/davidusa/REPOS/Image_Tagger_dk_latest/Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/docs/STUDENT_ARCHITECTURAL_TAG_SPRINT_CONTRACTS_2026-07-07.md`

## Purpose

This document translates the architectural and common-language tag vocabulary into a student-readable operational backlog.

The important distinction is:

- **Local evidence**: where in the image the tag is visible, preferably as a bounding box, mask, polygon, or region reference.
- **Global room attribute**: an aggregate value for the whole image or room, such as total glass ratio, visible window area, mean enclosure, material naturalness ratio, or glare risk.

Most useful architectural tags need both. For example, `clerestory_presence` should point to the high window band, while `fenestration_ratio` should say how much of the visible boundary is window/glass/opening.

## Status Legend

| Status | Meaning |
|---|---|
| `live_core` | Already represented by current core tags or science outputs. May still need better evidence regions. |
| `live_partial` | Some related live tag, VLM prompt, ontology term, or pattern tag exists, but it is not a complete operational attribute. |
| `planned_computable` | Defined in the July 2026 planning docs and plausible to compute with ordinary CV, segmentation, depth, or rules. |
| `human_validated_first` | The machine may propose candidates, but human review should be required before accepting as fact. |
| `search_overlay` | Useful for search or teaching, but should map to lower-level attributes rather than become a primitive. |
| `composite_later` | A higher-level score derived from multiple lower-level measurements. |

## Operational Rule

Every operational tag should eventually define:

1. `tag_id`
2. `plain_language_meaning`
3. `localizable`: yes / no / partial
4. `evidence_region_type`: bbox / mask / polygon / point / whole_image
5. `global_aggregate`: none / ratio / count / ordinal / score / category
6. `measurement_method`
7. `confidence`
8. `known_failure_modes`
9. `human_attestation_status`

User-facing operational tags should also be visible in two interfaces:

- **Annotation viewer**: an image page where users can see local evidence regions overlaid on the source image and inspect tag meaning, value, confidence, method, and attestation status.
- **Smart search gallery**: a search page where users can query tags or ordinary-language aliases and see the full result set with match explanations, filters, pagination, and links back to the annotation viewer.

## Core Architectural Tags

| Name | Current Status | What Needs To Be Done To Make Operational | Meaning In Ordinary Language | Local Evidence | Global Room Attribute |
|---|---|---|---|---|---|
| `boundary-opening-type` | `planned_computable` | Add detector/segmenter for windows, doors, archways, skylights, clerestories, screens, and generic apertures; store subtype and confidence. | What kind of opening is present in a wall, ceiling, roof, or partition. | bbox or mask for each opening. | Counts by opening type; opening area ratio. |
| `fenestration` | `planned_computable` | Build rule layer from wall/facade plane, opening candidate, window/glass cue, daylight cue, and frame/mullion cue; require human validation for uncertain cases. | The pattern and amount of windows or window-like openings in the room or facade. | bbox/mask for each window or glazed opening. | `fenestration_ratio`: visible opening/window area divided by visible wall/facade/boundary area. |
| `fenestration-ratio` | `planned_computable` | Compute visible window/glass/opening area over visible boundary area after segmentation. | How much of the room boundary is window, glass, or opening. | Derived from all accepted fenestration regions. | Continuous ratio, ideally 0.0-1.0. |
| `fenestration-pattern` | `human_validated_first` | Group fenestration candidates and classify isolated, grid, ribbon, curtain wall, clerestory band, irregular. | The arrangement of windows: single, repeated, banded, gridded, etc. | grouped window regions. | Categorical whole-room/facade pattern. |
| `clerestory_presence` | `live_partial` | Use high-window rule: window/opening candidate near ceiling; add height-band and daylight evidence. | A high window band near the ceiling. | bbox/mask for high window. | Count and area ratio of clerestory openings. |
| `skylight_presence` | `planned_computable` | Detect opening/daylight source on ceiling or roof plane; distinguish from light panels. | A daylight opening overhead. | bbox/mask on ceiling/roof plane. | Skylight area ratio over ceiling/roof plane. |
| `toplighting` | `planned_computable` | Derive from skylight or roof-light evidence plus overhead daylight distribution. | Daylight entering from above. | skylight region plus luminance field. | Ordinal score for top-light contribution. |
| `window_wall` | `planned_computable` | Detect high transparent boundary ratio; separate curtain wall from ordinary large windows. | A wall that is mostly window or glass. | large contiguous glass/window mask. | Transparent-boundary ratio. |
| `curtain_wall` | `human_validated_first` | Detect large gridded or continuous glazed building skin; verify facade context. | A non-load-bearing glazed wall system, usually with a grid/frame. | facade/glass grid region. | Categorical fenestration pattern and glass ratio. |
| `ribbon_window` | `human_validated_first` | Detect horizontal band of windows across a wall/facade. | A long horizontal strip of windows. | grouped horizontal window band. | Ribbon-window presence and band length ratio. |
| `aperture` | `human_validated_first` | Add generic wall/roof opening predicate not necessarily glazed. | A hole or opening in a boundary. | bbox/mask for opening. | Opening count and opening area ratio. |
| `doorway` | `planned_computable` | Detect door-like opening or traversable threshold; store subtype. | A passage through a wall or partition. | bbox/mask for door/doorway. | Doorway count per visible boundary. |
| `archway` | `planned_computable` | Detect curved-top opening; classify as threshold/opening subtype. | A doorway or opening with an arched top. | bbox/mask plus curved contour. | Count; optional archway ratio. |
| `threshold-type` | `live_partial` | Combine doorway/archway/step/material-change/light-change evidence; preserve subtype. | The kind of transition between spaces. | region at boundary transition. | Count and dominant threshold type. |
| `threshold_emphasized` | `live_partial` | Existing pattern key exists; needs evidence regions and stricter rule. | An entrance or transition that is visually stressed or made important. | bbox/mask around threshold. | Ordinal emphasis score. |
| `niche_presence` | `planned_computable` | Detect recessed wall pockets; require human validation until segmentation is reliable. | A small recess in a wall. | bbox/mask for recess. | Count and total niche area. |
| `alcove_presence` | `planned_computable` | Detect larger occupiable recess; combine enclosure and scale. | A larger recess or pocket that a person could occupy. | bbox/mask/region. | Count; alcove area ratio. |
| `window_seat_niche` | `live_partial` | Existing pattern key exists; add detector for window plus seat plus recess/sill. | A sitting nook built into or beside a window. | region including window and seat/niche. | Count; presence flag. |
| `refuge_nook` | `live_partial` | Existing VLM pattern exists; ground in alcove/enclosure/seat evidence. | A protected small area for retreat. | region around nook. | Refuge-nook count and refuge score contribution. |
| `boundary-permeability` | `planned_computable` | Compute from openings, glass, screens, slats, transparency, and occlusion. | How visually open or closed a boundary is. | masks for openings/glass/screens. | Ordinal or continuous permeability score. |
| `transparent_boundary` | `planned_computable` | Detect glass/clear boundary and visible depth beyond it. | A boundary you can see through. | glass/transparent region mask. | Transparent area ratio. |
| `translucent_boundary` | `planned_computable` | Detect light-transmitting but view-obscuring material. | A boundary that lets light through but does not provide a clear view. | translucent region mask. | Translucent area ratio. |
| `opaque_boundary` | `planned_computable` | Segment solid wall/partition regions. | A solid boundary you cannot see through. | wall/partition masks. | Opaque boundary ratio. |
| `porosity` | `planned_computable` | Detect screens, perforations, slats, repeated openings; compute void/solid ratio. | How holey or porous a surface or boundary is. | screen/perforation region masks. | Void-to-solid ratio. |
| `reveal_presence` | `human_validated_first` | Detect shadow gap/recessed joint; likely needs human review. | A recessed edge or shadow gap around an opening, panel, or plane. | small bbox/line region. | Count; optional reveal density. |
| `soffit_presence` | `human_validated_first` | Detect underside of beam, stair, balcony, or lowered plane. | The visible underside of a projecting or lowered architectural element. | mask/region under projection. | Count; soffit area ratio. |
| `bulkhead_presence` | `human_validated_first` | Detect local lowered ceiling box or enclosed duct zone. | A boxed-down part of the ceiling. | bbox/mask on ceiling. | Bulkhead area ratio. |
| `cove_presence` | `human_validated_first` | Detect concave/recessed edge at ceiling/wall; often needs lighting cue. | A recessed curved or angled edge, often near a ceiling. | edge/region at ceiling-wall junction. | Count/presence. |
| `cove_lighting_presence` | `planned_computable` | Combine cove geometry with hidden indirect light/luminance gradient. | Indirect light hidden in a ceiling or wall recess. | cove plus light region. | Cove-lighting presence and luminance contribution. |
| `wainscot_presence` | `human_validated_first` | Detect lower wall cladding band; add wall-plane and horizontal-band rule. | A lower band of wall paneling or cladding. | horizontal lower-wall region. | Wall-area ratio covered by wainscot. |
| `dado_presence` | `human_validated_first` | Detect rail or band at mid/lower wall. | A horizontal wall band or rail. | line/band region. | Count/length ratio. |
| `plinth_presence` | `human_validated_first` | Detect base course, pedestal, or lower raised band. | A base element at the bottom of a wall, column, or object. | lower boundary region. | Plinth length/area ratio. |
| `ceiling-form` | `planned_computable` | Classify flat, vaulted, domed, coffered, dropped, exposed, mixed; use ceiling segmentation and VLM/human validation for hard cases. | The shape and construction type of the ceiling. | ceiling mask and salient ceiling regions. | Whole-room ceiling category. |
| `ceiling-form:vaulted` | `live_partial` | Existing component key and dataset examples exist; add region evidence and robust classifier. | A ceiling formed as an arch or vault. | ceiling mask/curved overhead region. | Presence; vaulted ceiling area ratio. |
| `ceiling-form:domed` | `planned_computable` | Add dome classifier; distinguish domes from vaults. | A rounded hemispherical or dome-like ceiling. | ceiling/dome region. | Presence; dome area ratio. |
| `ceiling-form:coffered` | `live_partial` | Existing component key exists; add repetition/recess detector. | A ceiling with repeated recessed panels. | ceiling panel grid/recess regions. | Coffered area ratio and panel count. |
| `ceiling-form:dropped` | `planned_computable` | Detect suspended lower ceiling planes or localized drops. | A lower suspended ceiling plane. | ceiling plane region. | Dropped-ceiling area ratio. |
| `ceiling-form:exposed` | `planned_computable` | Detect visible beams, services, ducts, pipes, or structure overhead. | A ceiling where structure/services are visible. | overhead structure regions. | Exposed-ceiling area ratio. |
| `ceiling_height_avg` | `live_partial` | Use depth/layout estimation; calibrate with visible scale cues where possible. | How high the ceiling appears. | whole image plus ceiling/wall geometry. | Numeric/ordinal height estimate. |
| `enclosure_index` | `live_partial` | Use wall/ceiling/floor masks and depth/isovist proxy; calibrate to human labels. | How enclosed or open the space feels physically. | boundary plane masks. | Whole-room enclosure score. |
| `spatial_compression` | `planned_computable` | Combine low ceiling, narrow width, high enclosure, and close depth. | A tight or compressed spatial feeling. | whole image plus constricted regions. | Whole-room compression score. |
| `plan_openness` | `live_partial` | Use enclosure, long sightlines, partition density, and depth. | Whether the layout feels open and continuous. | visible partition/boundary regions. | Whole-room openness score. |
| `open_plan` | `planned_computable` | Detect few partitions, long sightlines, shared zones. | A room or area with few dividing walls. | floor/partition regions. | Open-plan score/category. |
| `cellular_plan` | `planned_computable` | Detect many partitions, short sightlines, repeated doorways. | A layout divided into many rooms/cells. | partitions/doorways. | Cellular-plan score/category. |
| `enfilade` | `human_validated_first` | Detect aligned doorways/openings through multiple rooms; likely needs multiple views or strong perspective cues. | A sequence of rooms connected by aligned openings. | aligned openings. | Presence/sequence confidence. |
| `axis` | `planned_computable` | Detect strong symmetry/alignment/vanishing line/doorway sequence. | A dominant line of organization through the image. | line/region group. | Axiality score. |
| `rhythm_repetition` | `planned_computable` | Detect repeated windows, columns, beams, bays, lights, panels. | Repeated architectural elements forming a rhythm. | grouped repeated elements. | Repetition regularity score. |
| `pattern_rhythm_regularity` | `planned_computable` | Use repetition detector plus spacing regularity. | How regular the visible pattern rhythm is. | repeated element group. | Whole-image regularity score. |
| `contour-curvature-type` | `planned_computable` | Classify rectilinear, curvilinear, mixed, sharp-angular, biomorphic using edges/segmentation. | Whether forms are mostly straight, curved, angular, or organic. | contours/edge regions. | Whole-image curvature category and curved-edge ratio. |
| `curvilinear_contour` | `planned_computable` | Compute curved edge ratio; optionally localize curved walls/ceilings/furniture. | Visibly curved lines or surfaces. | curved contour regions. | Curved-edge ratio. |
| `sharp_angular_contour` | `planned_computable` | Compute acute angle density and sharp corner frequency. | Sharp, angular visual form. | edge/corner regions. | Angularity score. |
| `biomorphic_form` | `planned_computable` | Combine curvature, organic shapes, natural motifs; likely human validation for high-value cases. | Forms that resemble living/natural shapes. | region around biomorphic shape. | Biomorphic form score. |
| `flooring-system` | `planned_computable` | Segment floor, classify timber/plank/tile/paver/carpet/monolithic/raised/mixed. | The type of floor surface and construction. | floor mask plus material/joint regions. | Dominant flooring category and area ratios. |
| `flooring_system:timber` | `planned_computable` | Detect wood floor/planks/parquet on floor plane. | A wood floor. | floor-material mask. | Wood floor area ratio. |
| `flooring_system:terrazzo` | `human_validated_first` | Add material classifier for speckled polished composite. | A speckled stone/composite floor. | floor-material mask. | Terrazzo area ratio. |
| `flooring_system:stone_paver` | `human_validated_first` | Detect stone paving units and joints. | Stone paver or flagstone flooring. | floor-material/joint regions. | Stone paver area ratio. |
| `flooring_system:monolithic` | `planned_computable` | Detect continuous floor without visible joints. | One continuous floor surface. | floor mask. | Monolithic floor score. |
| `flooring_system:jointed` | `planned_computable` | Detect tile/plank/paver joints on floor. | A floor with visible joints or seams. | floor joint lines. | Joint density. |
| `materials-dominant-types` | `live_core` | Improve material localization and class confidence. | The main visible materials: wood, stone, glass, concrete, metal, fabric, etc. | masks by material class. | Area ratio by material. |
| `materials-naturalness-ratio` | `live_core` | Use material masks instead of broad image-level estimates; keep low-confidence when mask quality is poor. | How much visible material appears natural, such as wood, stone, plants, earth, or natural textiles. | material masks. | Natural material area ratio. |
| `natural_material_ratio` | `planned_computable` | Bridge from material classifier to CNFA attribute with provenance. | Share of the image/room made of natural-looking materials. | material masks. | Continuous ratio. |
| `material_diversity_index` | `planned_computable` | Compute entropy/count of material classes. | How many different materials appear and how balanced they are. | material masks. | Material entropy/diversity score. |
| `surface-reflectance-sheen` | `planned_computable` | Detect matte/satin/glossy/mirror-like from highlights and reflections. | How shiny or dull surfaces are. | surface highlight regions. | Dominant sheen category and glossy area ratio. |
| `glossy_surface` | `planned_computable` | Detect sharp highlights and reflections. | A shiny surface. | glossy surface masks/regions. | Glossy area ratio. |
| `matte_surface` | `planned_computable` | Detect diffuse low-highlight surfaces. | A dull/non-shiny surface. | matte surface regions. | Matte area ratio. |
| `specular_reflectance` | `planned_computable` | Detect mirror-like directional reflections; distinguish mirrors from windows. | Mirror-like reflection. | reflected/highlight regions. | Specular area ratio. |
| `material_patina` | `human_validated_first` | Propose from discoloration, wear, irregularity, corrosion; require review. | Aged, worn, weathered, or oxidized surface character. | material surface regions. | Patina presence/area ratio. |
| `lighting-function` | `planned_computable` | Classify ambient/task/accent/cove/decorative/daylight from fixtures and illumination patterns. | What the light is doing in the room. | fixture/light regions. | Dominant lighting function mix. |
| `ambient_lighting` | `planned_computable` | Use broad uniform light wash and fixture/context evidence. | General room lighting. | whole image and light regions. | Ambient-light score. |
| `task_lighting` | `planned_computable` | Detect localized work/reading light near desks/tables/seating. | Light aimed at a task area. | fixture and task-area region. | Count and presence score. |
| `accent_lighting` | `planned_computable` | Detect spotlight/wall-wash/focal illumination. | Light used to highlight an object or surface. | lit focal region. | Accent-light score. |
| `lighting-color-temperature` | `live_core` | Calibrate and separate surface color from illuminant where possible. | Whether light looks warm, neutral, or cool. | whole image or lit regions. | Whole-image CCT estimate/bin. |
| `warm_light` | `live_core` | Keep camera white-balance caveat; localize if possible. | Yellowish/warm illumination. | lit regions. | Warm-light ratio/score. |
| `cool_light` | `live_core` | Keep camera white-balance caveat; localize if possible. | Bluish/cool illumination. | lit regions. | Cool-light ratio/score. |
| `glare-risk` | `planned_computable` | Compute overexposure, high luminance contrast, window position, reflection intensity. | Whether the image suggests uncomfortable bright glare. | bright/glare regions. | Glare risk ordinal score. |
| `brightness_variance` | `planned_computable` | Compute spatial luminance variance after normalization. | How uneven brightness is across the room/image. | whole image or luminance map. | Numeric variance score. |
| `diffuse_vs_direct_ratio` | `planned_computable` | Estimate soft diffuse light versus hard direct light from shadow edges and luminance gradients. | Whether light is soft and spread out or hard/direct. | shadow/light regions. | Diffuse/direct ratio. |
| `vertical_illuminance_proxy` | `planned_computable` | Estimate brightness on vertical planes from wall masks. | How much light reaches vertical surfaces. | wall plane masks. | Mean vertical-plane luminance. |
| `visual_privacy` | `planned_computable` | Combine boundary opacity, screens, enclosure, exposure, and sightlines. | How visually private the space seems. | screens/boundaries/sightline regions. | Whole-room privacy score. |
| `prospect_to_refuge_ratio` | `planned_computable` | Combine view depth/openness with protected enclosure/refuge cues. | Balance between outlook and shelter. | view corridor plus refuge regions. | Whole-room ratio/score. |
| `prospect` | `live_core` | Improve depth/isovist proxy and evidence regions. | Ability to see outward or across distance. | view corridor/open field. | Prospect score. |
| `refuge` | `live_partial` | Ground in enclosure, alcove, nook, protected seating, and outward view. | A protected place from which one can observe. | refuge regions. | Refuge score. |
| `spatial-legibility` | `live_core` | Link to paths, landmarks, zones, axes; add evidence regions. | How easy the space is to understand or navigate. | paths/landmarks/axes. | Legibility score. |
| `landmark_salience` | `planned_computable` | Use saliency/object prominence plus wayfinding relevance. | How clearly a notable object/place anchors orientation. | landmark region. | Salience score. |
| `activity_zones_count` | `planned_computable` | Segment functional zones using objects, furniture, floor areas, and layout. | How many distinct activity areas are visible. | zone regions. | Count of zones. |
| `zoning_clarity` | `planned_computable` | Measure how distinct and readable activity zones are. | How clearly the space is divided into uses. | zone regions. | Zoning clarity score. |
| `sociopetal_seating` | `planned_computable` | Detect seats and face-to-face/group orientation. | Seating arranged to encourage social interaction. | seat/furniture group regions. | Sociopetal score/count. |
| `interactional_visibility` | `planned_computable` | Estimate whether occupants can see each other across activity areas. | Visual access among people or seating positions. | seating/sightline regions. | Interaction visibility score. |
| `clutter_density_count` | `planned_computable` | Count objects and normalize by visible floor/image area; later use room floor area. | How cluttered the space is by object count. | object boxes/masks. | Objects per floor area/image area. |
| `processing_load_proxy` | `planned_computable` | Compute JPEG bytes per pixel or richer compression/entropy measure. | A crude proxy for visual information load. | whole image. | Numeric score. |
| `symmetry_score_horizontal` | `planned_computable` | Compute similarity between image and horizontal mirror; local/global variants. | How symmetrical the image is left-to-right. | whole image; optional symmetric regions. | Symmetry score. |
| `edge_clarity_mean` | `planned_computable` | Compute edge sharpness/gradient clarity. | How crisp the visible edges are. | edge map. | Mean edge clarity. |
| `color_palette_entropy` | `planned_computable` | Cluster colors and calculate Shannon entropy of palette proportions. | How varied the color palette is. | whole image or regions. | Palette entropy score. |
| `fractal_dimension` | `planned_computable` | Use box-counting over edges/masks; standardize preprocessing. | Degree of self-similar visual complexity. | edge/texture masks. | Fractal dimension score. |
| `visual_entropy_spatial` | `planned_computable` | Compute entropy over object/region distribution. | How spatially distributed visual information is. | object/region map. | Spatial entropy score. |
| `figure_ground_clarity` | `planned_computable` | Use object/background contrast, segmentation confidence, and saliency. | How clearly objects or forms stand out from background. | salient objects/background masks. | Figure-ground score. |
| `hierarchy_depth` | `planned_computable` | Detect nested focal levels: dominant, secondary, tertiary elements. | How many levels of visual importance the composition has. | saliency/focal regions. | Hierarchy depth score. |
| `biophilic_design_score` | `composite_later` | Combine vegetation, daylight, natural material, water, biomorphic form, fractal texture. | Overall biophilic character. | component evidence regions. | Composite score with component breakdown. |
| `restorative-capacity` | `composite_later` | Derive from naturalness, vegetation, daylight, coherence, low glare, prospect/refuge, low clutter. | Whether the space has visual features associated with restoration. | supporting component regions. | Composite restorative score. |
| `intimacy_index` | `composite_later` | Combine scale, enclosure, warm light, alcove/refuge, soft/natural material, low glare. | Whether a space feels small, sheltered, and personally comfortable. | component regions. | Composite intimacy score. |
| `monumentality_index` | `composite_later` | Combine height, volume, axis, hierarchy, material mass, scale cues. | Whether a space feels grand or monumental. | component regions. | Composite monumentality score. |
| `serenity_index` | `composite_later` | Combine low clutter, diffuse light, naturalness, coherent pattern, low sharpness/glare. | Whether a space feels calm or serene. | component regions. | Composite serenity score. |
| `tension_index` | `composite_later` | Combine harsh light, sharp contours, high contrast, clutter, low refuge. | Whether a space feels visually tense. | component regions. | Composite tension score. |
| `acoustic-reverberation-proxy` | `planned_computable` | Estimate from volume, hard-surface ratio, soft-surface absorption, curtains/carpets/panels. | Whether the space is likely to sound echoey. | hard/soft surface regions. | Reverberation proxy score. |
| `acoustic_absorption_proxy` | `planned_computable` | Detect carpet, upholstery, curtains, acoustic panels, soft surfaces. | Whether the room likely absorbs sound. | soft/absorptive surface masks. | Absorptive area ratio. |
| `thermal_comfort_proxy` | `human_validated_first` | Use sun/shade, material, greenery, visible HVAC/fire/water; treat as weak proxy. | Visual cues that suggest thermal comfort or discomfort. | component evidence regions. | Weak ordinal proxy. |
| `olfactory_expectation_proxy` | `human_validated_first` | Use wood/plants/water/decay/industrial cues; never assert actual smell. | What the image visually suggests about smell. | component evidence regions. | Weak ordinal proxy. |

## Viewer And Search Requirements

The tag system must not stop at backend extraction. The student implementation must include a practical way to inspect and use tags.

| Interface | Required Behavior | Why It Matters |
|---|---|---|
| Annotation viewer | Show the image with togglable bbox/mask/polygon overlays; display tag id, ordinary-language meaning, value, confidence, method, and attestation status. | Localized tags are not trustworthy unless a reviewer can see the evidence. |
| Smart search gallery | Search by tag id and human alias; filter by confidence/status/global thresholds; show paginated result cards; explain why each image matched. | Users need to find images by architectural qualities once image databases arrive. |
| Result detail link | Every search result opens the annotation viewer for that image. | Search and evidence inspection must be connected. |
| Candidate handling | Candidate/VLM/human-pending tags must be visually distinguished from accepted tags. | Prevents plausible but unvalidated tags from looking final. |
| Large-corpus readiness | Pagination, loading states, empty states, and deterministic ordering. | The system must be ready for incoming image databases, not only tiny demos. |

## First Student Implementation Slice

The first student-ready sprint should choose a small slice that is testable without expensive VLM calls:

| Sprint Tag | Why First | Minimum Acceptance |
|---|---|---|
| `processing_load_proxy` | Pure image statistic. | Returns numeric value; tested on small/large/simple/complex images. |
| `brightness_variance` | Pure luminance statistic. | Returns numeric value and heatmap/debug artifact. |
| `edge_clarity_mean` | Existing edge/debug infrastructure. | Returns edge map and mean clarity. |
| `color_palette_entropy` | Straightforward color clustering. | Returns palette bins and entropy. |
| `symmetry_score_horizontal` | Deterministic and interpretable. | Returns score plus mirror-difference diagnostic. |
| `fractal_dimension` | Already planned and close to MPIB feature set. | Returns standardized box-counting estimate. |
| `clutter_density_count` | Useful but needs object boxes; allow image-area fallback. | Returns object count and normalized density with method caveat. |
| `natural_material_ratio` | High research value; initially low confidence if material masks are weak. | Returns material classes, masks if available, area ratio, confidence. |

## Second Student Implementation Slice

After the direct statistics work, move to localized architectural predicates:

| Sprint Tag | Dependency |
|---|---|
| `boundary-opening-type` | window/door/opening detector. |
| `fenestration-ratio` | boundary plane masks plus window/glass/opening masks. |
| `clerestory_presence` | fenestration candidates plus vertical position. |
| `skylight_presence` | ceiling/roof plane plus daylight opening. |
| `ceiling-form` | ceiling segmentation plus classifier. |
| `threshold-type` | doorway/opening plus floor/material/light transition cues. |
| `niche_presence` / `alcove_presence` | wall geometry and depth/recess evidence. |
| `boundary-permeability` | opening/glass/screen/slat masks. |

## Notes For Students

- A tag is not operational merely because a VLM can name it.
- A localized tag should show the evidence region.
- A global attribute should state the aggregation method.
- If a detector is uncertain, the correct output is `candidate_pending_human_validation`, not a confident architectural fact.
- Composite scores must keep their source components inspectable.
