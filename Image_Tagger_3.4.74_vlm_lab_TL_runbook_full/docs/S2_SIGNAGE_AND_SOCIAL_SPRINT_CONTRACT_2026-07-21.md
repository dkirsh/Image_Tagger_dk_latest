# S2 Sprint Contract: Signage and Social Interaction Foundations

Date: 2026-07-21  
Status: Proposed  
Owner: Tanishq

## Goal

Build the foundation for operationalizing signage, navigation, and social interaction attributes in Image Tagger.

This sprint does not try to solve all signage detection. It creates the taxonomy, annotation contract, validation set plan, and first low risk prototype targets.

## Why this sprint

Professor Kirsh identified signage, isovists, social interaction, and acoustic inference as high value directions. These should not be implemented as loose tags. They need contracts and validation first.

## Deliverables

### Deliverable 1: Signage taxonomy

File:
datasets/signage_seed/signage_taxonomy_seed_2026-07-21.csv

Required content:
- building type
- sign category
- sign type
- examples
- typical placement
- navigation role
- social interaction role
- priority
- notes

Acceptance:
- includes hospitals and offices
- includes at least 25 signage rows
- includes exit signs, toilets, room numbers, meeting room displays, directories, and hospital department signs

### Deliverable 2: Signage annotation contract

File:
docs/SIGNAGE_ANNOTATION_CONTRACT_2026-07-21.md

Acceptance:
- defines required annotation fields
- defines sign category vocabulary
- defines placement vocabulary
- defines navigation role vocabulary
- defines social interaction role vocabulary
- defines hard cases
- defines first prototype scope

### Deliverable 3: Social interaction taxonomy

File:
docs/SOCIAL_INTERACTION_ATTRIBUTE_TAXONOMY_2026-07-21.md

Acceptance:
- defines at least 10 interaction classes
- maps each interaction class to environmental attributes
- separates observed, computed, inferred, VLM judged, and composite attributes

### Deliverable 4: Open source method shortlist

File:
reports/OPEN_SOURCE_VISUAL_PROCESSING_SURVEY_DRAFT_2026-07-21.md

Acceptance:
- includes OCR and scene text detection options
- includes indoor navigation references
- includes isovist and visibility graph options
- includes material to acoustic inference direction
- includes recommendation for first prototype

### Deliverable 5: First prototype scope

The first implementation prototype should focus only on:

- exit signs
- toilet signs
- room numbers
- meeting room displays
- directional arrows
- directories

## Proposed architecture

### Stage 1: Candidate detection

Use one or more methods:
- OCR text detector
- object detector for sign like regions
- VLM candidate review for low confidence cases

Output:
- sign candidate bounding boxes
- crop path
- detection confidence

### Stage 2: Text and icon parsing

Use:
- OCR for text
- icon classifier or VLM for signs with icons
- arrow detector for directional signs

Output:
- text transcription
- OCR confidence
- icon class
- arrow direction if present

### Stage 3: Sign function classification

Classify signs into:
- directional
- identification
- safety
- regulatory
- amenity
- directory
- digital
- temporary
- decorative
- unknown

### Stage 4: Placement and visibility

Estimate:
- placement type
- image location
- approximate height class
- occlusion level
- readability class
- decision point relevance

### Stage 5: Navigation value

Compute:
- sign_navigation_value
- sign_visibility_from_path
- decision_point_support
- wayfinding_legibility_support

## Validation

### Unit validation

- all confidence values finite
- all bounding boxes inside image
- all sign categories from allowed vocabulary
- all placement labels from allowed vocabulary
- unknown allowed only when confidence is low

### Dataset validation

- hospital examples
- office examples
- positive sign examples
- negative decorative text examples
- small distant signs
- partially occluded signs
- signs visible but unreadable

### Review validation

A human should review at least 30 examples and label:

- accepted
- questionable
- rejected

## Known risks

- decorative text mistaken for signage
- brand signs mistaken for navigation
- small signs missed by OCR
- oblique signs unreadable
- digital displays blurred
- signs visible in image but not actually visible from human path
- image plane visibility confused with real 3D visibility

## Success condition

This sprint is accepted when the repo contains:
- a signage taxonomy seed file
- a signage annotation contract
- a social interaction taxonomy
- an open source method survey
- a narrow first prototype plan with validation rules
