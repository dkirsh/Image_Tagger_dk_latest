# Image_Tagger Brief: Mining Space-Use Repertoires for New Vision Attributes

**Audience:** Claude and other agents working on `Image_Tagger_dk_latest`  
**Date:** 2026-07-29  
**Timestamp convention:** Pacific Time, labeled PST or PDT as seasonally applicable  
**Source concept:** `SPACE_USE_REPERTOIRE_FOUNDATION_2026-07-29.md`

## Purpose

Use room activities and behavior settings to discover useful visual attributes without claiming that a photograph proves behavior, comfort, or psychological outcome.

The governing chain is:

> activity episode -> required person-object-space relations -> visually recoverable evidence -> image/3D attribute -> testable prediction

Do not jump directly from a room image to a statement such as "people collaborate here." The image may support a narrower statement such as "four seats have a shared sightline to one writable surface and permit face-to-face orientation." Collaboration remains a prediction requiring behavioral evidence.

## What to mine from the relevant literature

| Source family | What Image_Tagger can extract from it |
|---|---|
| Barker behavior settings | Recurrent behavior-milieu couplings; the room type alone is not the unit |
| Heft ecological psychology | Activities are nested in socially organized places; affordances depend on the actor and local norms |
| Ng behavioral mapping | Candidate ground truth: where episodes occur, their duration, sequence, social form, and conflicts |
| Smart-home activity recognition | Action vocabularies, object-use relations, event sequences, and co-occurring activities |
| Human-scene affordance prediction | Pose, reach, approach, sitting, standing, and contact feasibility |
| Activity-centric scene synthesis | Object arrangements required to support activities |
| Space-use ontologies | Explicit links among users, activities, spaces, equipment, and spatial requirements |
| Function-first scene generation | Functional briefs converted into spatial, ergonomic, activity, and environmental constraints |

## Required distinction

Every proposed attribute must be classified as one of:

1. **Visible primitive:** directly estimated from pixels, segmentation, depth, or geometry.
2. **Relational affordance proxy:** computed from several visible primitives relative to a specified activity and actor model.
3. **Declared-input measure:** requires a plan, dimensions, material specification, acoustic model, or operational information.
4. **Behavioral outcome:** requires observation or participant data and must not be presented as an image attribute.

Image_Tagger should return `UNKNOWN` or abstain when required evidence is absent. A semantic guess is not a substitute for a missing measurement.

## Existing attributes to reuse

Check current code and the generated computational-attribute table before adding anything. Important existing families include:

- brightness, luminance variation, glare risk, and light direction;
- edge clarity, symmetry, color entropy, processing-load and clutter proxies;
- enclosure, prospect, depth, visual integration, connectivity, and wayfinding load;
- landmark salience and signage-related plans;
- workstation density, crowding, path overlap, and collaborator proximity;
- sociopetal seating and social-connectedness inputs;
- speech privacy, distraction distance, and acoustic-absorption proxies;
- prospect-refuge, waiting-position, solitary-retreat, lingering, and focus-zone compounds;
- view equity, daylight proximity, local control, territory, and restoration/nature inputs.

Do not create a second scalar under a more attractive name when the intended evidence is already represented.

## High-value candidate attributes

These candidates emerge from common interior activity episodes and appear to add useful relations rather than duplicate broad affective labels. All remain candidates until deduplicated against the registry and validated.

| Candidate attribute | Activity question | Recoverable evidence | Substrate | Main limit |
|---|---|---|---|---|
| `shared_focal_surface_access` | Can a group jointly see and use a display, board, drawing, or artifact? | Focal-surface detection, seat positions, facing, occlusion, viewing angles | Image+depth or 3D | Seeing a surface does not prove joint attention |
| `co_viewing_configuration_capacity` | Can two or more people inspect the same document or screen side-by-side? | Seat/work-surface geometry, adjacent approach zones, shared sight cone | Image+depth/3D | Requires reliable scale and object relations |
| `document_transfer_reachability` | Can people pass or jointly annotate physical material without standing or obstructing others? | Inter-seat distance, surface continuity, reach envelopes, route overlap | 3D preferred | Actor dimensions must be declared |
| `presentation_sightline_equity` | Do audience positions have comparably unobstructed views of the presenter or display? | Seat detection, focal target, occlusion, angular deviation, distance | 3D preferred | Image viewpoint may conceal occlusions |
| `arrival_orientation_support` | On entering, can a newcomer identify reception, destination, sign, or principal route? | Entry hypothesis, target salience, preview depth, decision-point options | Image sequence/3D | A single interior image may not include the entrance |
| `waiting_route_conflict` | Can a person wait without blocking arrival, circulation, or service? | Waiting supports, protected standing zones, path overlap, doorway clearance | Image+depth/3D | Actual traffic volume is not visible |
| `queue_capacity_without_crossflow` | Is there plausible queuing space separated from normal cross-traffic? | Counter/gate detection, free-space geometry, linear capacity, crossing paths | 3D preferred | Demand and service rate require operational data |
| `focus_seat_interruption_exposure` | Is focused work placed beside approach paths or spontaneous-contact zones? | Seat/desk positions, visibility from path, distance to route and shared resources | Image+depth/3D | Interruption frequency is behavioral |
| `interaction_choice_diversity` | Does the setting offer configurations for solitary, dyadic, small-group, and larger-group occupation? | Seating clusters, capacities, orientation, separation, enclosure | Image+depth/3D | Availability does not prove use or permission |
| `activity_conflict_colocation` | Are visibly incompatible activity supports placed in the same exposure zone? | Focus desks, social seating, circulation, displays, service points, partitioning | Image+depth/3D | Acoustic and organizational conflict often need extra inputs |
| `informal_perch_availability` | Are there short-duration leaning, ledge-sitting, or pause supports near activity without blocking paths? | Ledges, rails, seat-height surfaces, edge depth, adjacent clearance | Image+depth | Current seat proxy is too crude; object validation required |
| `protected_edge_occupation` | Can a person occupy an edge while retaining prospect and avoiding through movement? | Back/side protection, prospect, route distance, seat or standing zone | Image+depth/3D | Social acceptability is context-dependent |
| `conversation_cluster_clearance` | Can a small standing or seated group form without entering the main circulation path? | Free-space pockets, likely group diameter, route overlap, barriers | 3D preferred | Actual group size distribution is external |
| `reconfiguration_readiness` | Can furniture be rearranged for another activity? | Movable/fixed furniture classification, free storage, clearance, cable constraints | Image+depth/3D | Weight, locking, and policy may be invisible |
| `alternative_posture_support` | Does the room visibly support sitting, standing, leaning, and movement while performing the activity? | Furniture types, work heights, clear floor, reach relations | Image+depth | Ergonomic suitability requires scale and actor model |
| `mobility_approach_clearance` | Can a mobility-device user approach, turn, and use the relevant object or service point? | Free-space segmentation, turning envelope, approach direction, obstruction | Calibrated 3D | Never claim accessibility from an unscaled photograph |
| `shared_resource_approach_conflict` | Does access to printer, storage, food, or controls cut through occupied work zones? | Resource detection, approach envelope, route and seat overlap | Image+depth/3D | Resource-use frequency is external |
| `storage_retrieval_legibility` | Are stored materials visible, differentiated, reachable, and approachable? | Storage/object detection, labeling/OCR, height, obstruction, approach zone | Image+depth/3D | Contents and permissions may be unknown |
| `caregiver_supervision_coverage` | Can a caregiver oversee relevant activity zones while attending to another task? | Sightlines between caregiver station and child/patient zones, occlusion | 3D preferred | Supervision quality is not reducible to visibility |
| `service_occupant_coexistence` | Can cleaning, delivery, replenishment, or maintenance occur without occupying the principal user route? | Service/storage points, route alternatives, door widths, staging space | Plan/3D | Timing and operations are declared inputs |
| `hybrid_meeting_capture_geometry` | Are participants, display, camera, and light arranged for remote participation? | Camera/display detection, participant facing, backlight, field of view | Image+depth/3D | Audio quality and system operation are not visible |
| `privacy_gradient_visibility` | Does visual exposure change gradually between public, shared, and private zones? | Partition permeability, doors, depth, sightlines, workstation exposure | 3D preferred | Social privacy also requires norms and acoustics |

## First implementation priorities

Prioritize attributes that are useful across several room types and have observable negative controls:

1. `shared_focal_surface_access`
2. `arrival_orientation_support`
3. `waiting_route_conflict`
4. `focus_seat_interruption_exposure`
5. `interaction_choice_diversity`
6. `presentation_sightline_equity`
7. `conversation_cluster_clearance`
8. `mobility_approach_clearance`

These should begin as region-level relational measures, not whole-image psychological scores.

## Context envelope required for every relational attribute

```text
room_type_hypotheses[]
activity_episode
actor_profile_or_range
image_or_model_viewpoint
scale_confidence
required_object_detections[]
required_region_pairs[]
geometry_source
visibility_or_occlusion_method
score
confidence
abstention_reason
known_failure_modes[]
```

The same image may support different scores for different episodes. A layout suitable for a presentation may be poor for private consultation. Preserve the episode parameter rather than collapsing all functionality into one value.

## Mining workflow for Claude

1. Select one room type and 10-20 activity episodes from its Space-Use Repertoire.
2. Decompose each episode into people, actions, objects, spatial relations, transitions, and conflicts.
3. Mark each requirement as pixel-visible, geometry-recoverable, plan/spec-required, operational, or behavioral.
4. Search the generated attribute table and registry for existing primitives and compounds.
5. Keep only genuinely new primitive or relational evidence.
6. State the narrowest honest attribute name.
7. Define applicability, required inputs, scale, confidence, abstention, and failure modes before implementation.
8. Create synthetic positive, synthetic negative, and ambiguity/abstention fixtures.
9. Test on real rooms across at least two architectural typologies.
10. Corroborate the proxy against human-coded behavioral maps or controlled judgments before linking it to an outcome.

## Scientific and engineering rules

- Do not infer observed behavior from designed affordance.
- Do not infer social permission from physical possibility.
- Do not infer acoustics, temperature, air quality, occupancy demand, or time from a still image.
- Do not use a room classifier as proof that a particular activity occurs.
- Do not bury actor assumptions; reach, view, and clearance are relative to bodies.
- Do not hide uncertainty in a compound score.
- Preserve primitive measurements so later studies can test alternate compounds.
- A VLM may nominate objects and relations, but deterministic geometry or reviewed labels should verify them where feasible.
- Every construct link remains a hypothesis until validated against an appropriate corpus or experiment.

## Suggested pilot

Use three spaces with dissimilar activity ecologies:

- entrance or foyer;
- open office or design studio;
- classroom or seminar room.

For each space, annotate focal surfaces, seating, paths, thresholds, entries, waiting zones, shared resources, partitions, controls, and service points. Then score the eight priority relational attributes. Compare the outputs with human-coded activity maps and expert judgments. This gives Image_Tagger a direct route from visual evidence to design-relevant, falsifiable claims.

## Key references

- Barker, R. G. (1968). *Ecological Psychology*.
- Heft, H. (2018). "Places: Widening the Scope of an Ecological Approach to Perception-Action." https://doi.org/10.1080/10407413.2018.1410045
- Ng, C. (2015). "Behavioral Mapping and Tracking." https://doi.org/10.1002/9781119162124.ch3
- Chen et al. (2013). "A knowledge-based framework for automated space-use analysis." https://doi.org/10.1016/j.autcon.2012.08.002
- Chen (2019). "Ontology-Based Representations of User Activity and Flexible Space Information." https://doi.org/10.1155/2019/3690419
- Fisher et al. (2015). "Activity-centric Scene Synthesis for Functional 3D Scene Modeling." https://graphics.stanford.edu/projects/actsynth/
- Li et al. (2019). "Putting Humans in a Scene." https://openaccess.thecvf.com/content_CVPR_2019/html/Li_Putting_Humans_in_a_Scene_Learning_Affordance_in_3D_Indoor_CVPR_2019_paper.html
- Wang et al. (2026). "Function2Scene." https://arxiv.org/abs/2605.30819

