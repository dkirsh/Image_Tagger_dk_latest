# Professor Revision Deep Review Draft

Date: 2026-07-21  
Repo reviewed: https://github.com/dkirsh/Image_Tagger_dk_latest  
Active app root: Image_Tagger_3.4.74_vlm_lab_TL_runbook_full  
Status: Draft review in progress

## Purpose

Professor Kirsh asked for a deep review of the latest pushed Image Tagger revision. The review should identify what is good, what is bad, what is questionable, and where there are opportunities to push forward.

Special focus areas:
- low-level visual functions
- local-region visual attributes
- topographic exposure maps
- isovists
- space syntax and sightlines
- navigation inference
- material and spatial cues for acoustic inference
- social interaction attributes
- signage and wayfinding

## Initial repo status

The latest repo was cloned directly from:

https://github.com/dkirsh/Image_Tagger_dk_latest

The previous local S1 checkpoint was preserved separately on branch:

tanishq-s1-direct-stats-local

## Early findings from file inventory

The latest active app root contains relevant science modules for:

- low-level math analyzers
- materials
- social context
- affordance prediction
- depth
- isovist analysis
- semantic VLM tags
- canonical feature registry
- science tag maps
- student sprint contracts
- visual attribute inventory

Relevant active files to inspect:
- backend/science/spatial/isovist.py
- backend/science/spatial/isovist_25d.py
- backend/science/spatial/depth.py
- backend/science/context/social.py
- backend/science/context/affordance.py
- backend/science/vision/materials.py
- backend/science/features_canonical.jsonl
- contracts/attributes.yml
- docs/STUDENT_ARCHITECTURAL_TAG_SPRINT_CONTRACTS_2026-07-07.md
- docs/ARCHITECTURAL_TAG_OPERATIONAL_BACKLOG_2026-07-07.md
- reports/IMAGE_TAGGER_VISUAL_ATTRIBUTE_INVENTORY_2026-07-07.md

## What looks good so far

### 1. The project has moved beyond whole-image tagging

The current direction appears to support a richer model of image understanding than simple image-level labels. The important move is toward localized attributes, spatial exposure, and interpreted spatial relationships.

This is good because many architectural and social attributes are not just properties of the entire image. They depend on where a person is standing, what they can see, what surfaces are near them, what paths are available, and what signs or landmarks are visible from decision points.

### 2. Isovists are a strong conceptual bridge

Isovists give a way to move from image tags toward spatial claims. They can support questions like:

- what can be seen from a point
- where visual exposure is high
- where refuge or privacy might be stronger
- where signage is visible before a decision point
- how sightlines support navigation
- how social visibility changes across a room

This is much stronger than simply saying a room is open or closed.

### 3. The materials to acoustics idea is valuable

Using visible spatial and material properties to derive acoustic properties is high value. For example:

- glass, tile, stone, concrete, and metal suggest more reflection
- carpet, curtains, upholstered seating, acoustic panels, and bookshelves suggest more absorption
- room volume and surface hardness affect speech privacy
- openings and partitions affect where speech carries

This could support social interaction tags like overhearing risk, conversational privacy, and speech intelligibility zones.

### 4. Signage is a high-value subproject

Signage is important because navigation is not only geometry. People navigate using signs, arrows, labels, maps, room numbers, exits, color coding, and landmarks.

A sign should not only be detected. It should be evaluated by placement and visibility:

- is it visible from a path
- is it visible before a decision point
- is it occluded
- is it high enough
- is it readable at the likely viewing distance
- does it reduce ambiguity
- is it related to movement or safety

## What is questionable or needs validation

### 1. 2D image evidence versus actual spatial geometry

A single photo can suggest space, but it does not fully define geometry. Any isovist or visibility inference from a single image must say whether it is using:

- actual plan geometry
- depth-estimated geometry
- segmentation-derived proxy geometry
- image-plane proxy only

This distinction matters because spatial claims can easily become overconfident.

### 2. Acoustic inference from visual evidence needs careful confidence handling

Acoustics inferred from materials are useful, but they are indirect. The system should separate:

- visible material evidence
- inferred absorption or reflection
- inferred speech intelligibility
- inferred privacy or overhearing risk

Each layer should reduce confidence unless supported by stronger evidence.

### 3. Social interaction attributes need a taxonomy first

Before creating social tags, we should classify the interaction types. Otherwise the attributes will become too vague.

Possible interaction classes:
- private one-to-one conversation
- small group meeting
- collaborative work
- public presentation
- waiting or queuing
- casual encounter
- service interaction
- confidential conversation
- navigational help seeking
- passive co-presence
- crowd movement
- emergency movement

Each class needs different spatial, acoustic, visibility, and signage evidence.

### 4. Local-region attributes need evidence contracts

For every local-region output, the system should say:

- region type
- coordinates
- scale
- denominator
- aggregation rule
- confidence
- failure mode
- whether it is observed or inferred

Without this, local maps may be visually impressive but hard to validate.

## Opportunity: signage and isovists

Signage can become a serious project because it combines four layers:

### Layer 1: Sign detection

Detect sign-like regions:
- wall signs
- overhead signs
- door signs
- room numbers
- exit signs
- restroom signs
- directories
- elevator signs
- scheduling tablets
- warning signs
- temporary signs

### Layer 2: Sign reading or classification

Classify sign function:
- destination
- identification
- direction
- safety
- warning
- rule or policy
- room booking
- accessibility
- emergency
- brand or logo
- decorative text

### Layer 3: Placement and visibility

Use geometry, depth, and isovist-style logic:
- sign visibility from observer points
- visibility along circulation paths
- visibility before decision points
- line-of-sight obstruction
- viewing distance
- angular size
- height and position
- contrast with background

### Layer 4: Navigation value

Estimate whether the sign helps navigation:
- does it appear near a decision point
- does it clarify route choice
- does it identify a destination
- does it help emergency movement
- does it reduce wayfinding ambiguity

## Building-type signage taxonomy

### Hospitals

Common signs:
- emergency
- triage
- registration
- pharmacy
- radiology
- surgery
- ward names
- room numbers
- elevator signs
- exit signs
- toilets
- restricted access
- color-coded zones
- department directories
- patient waiting areas

Hospital-specific issues:
- high stress
- dense signage
- similar corridors
- safety-critical wayfinding
- multilingual signs
- accessibility requirements

### Offices

Common signs:
- reception
- meeting room names
- room numbers
- toilet signs
- exit signs
- department labels
- scheduling displays
- elevator signs
- stair signs
- fire evacuation maps
- restricted access signs
- desk or name plates
- temporary event signs

Office-specific issues:
- room scheduling panels are signs and interaction interfaces
- branding signs may not help navigation
- meeting room signs often matter for social coordination

### Universities

Common signs:
- room numbers
- lecture halls
- department offices
- laboratories
- exits
- toilets
- floor directories
- event posters
- accessibility routes
- building maps

### Airports and stations

Common signs:
- gates
- exits
- baggage
- security
- restrooms
- platforms
- transfers
- ticketing
- emergency exits
- direction arrows

## Proposed next sprint

### S2: Evidence envelope and local-region contract

Goal:
Before implementing more tags, define a strict evidence contract for whole-image, region-level, and map-level outputs.

Required output fields:
- tag_id
- value
- confidence
- evidence_type
- evidence_region
- coordinate_system
- method
- version
- denominator
- aggregation_rule
- observed_or_inferred
- known_failure_modes
- validation_status

Acceptance tests:
- every output has required fields
- local outputs have valid coordinates
- map outputs declare resolution and coordinate system
- inferred outputs have lower-confidence rules
- unknown or invalid evidence fails safely

### S3: Signage discovery prototype

Goal:
Build a first signage dataset and sign taxonomy before model implementation.

Deliverables:
- 50 to 100 example images across hospitals, offices, universities, airports, malls, and museums
- sign placement taxonomy
- sign function taxonomy
- sample annotation schema
- candidate algorithms for sign detection and OCR
- isovist-based visibility ranking proposal

## Open-source search targets

Need review robust algorithms for:
- OCR and scene text detection
- sign detection
- visual saliency
- isovist and visibility graph analysis
- indoor navigation datasets
- material segmentation
- room layout estimation
- depth estimation
- acoustic inference from visual surfaces

## Questions for Professor Kirsh

1. Should signage become its own sprint now, or should it wait until after the evidence envelope contract?
2. Should we treat isovist outputs as geometry-backed only, or allow image-plane proxy isovists with lower confidence?
3. For acoustic inference, should the first goal be speech privacy, speech intelligibility, or general acoustic comfort?
4. Should the first real-image validation set focus on offices and hospitals only, since those are the clearest signage cases?

