# Open Source Visual Processing Survey Draft

Date: 2026-07-21  
Purpose: Identify robust open source methods for signage, visibility, spatial interpretation, materials, acoustics, and social interaction attributes.

## Executive summary

The strongest immediate direction is not to build a custom signage model from scratch. The first prototype should combine existing OCR and text detection tools with a narrow signage taxonomy and an evidence contract.

Recommended first prototype stack:

1. PaddleOCR or MMOCR for scene text detection and OCR.
2. A simple sign candidate filter based on text region size, position, contrast, and sign vocabulary.
3. Optional VLM review only for ambiguous sign function classification.
4. A visibility and placement layer that estimates whether the sign is useful for navigation.
5. Human review on a small curated hospital and office validation set.

## Problem decomposition

Signage for navigation should be treated as five linked problems:

1. Detect sign-like regions.
2. Read text or detect icon and arrow information.
3. Classify the sign function.
4. Estimate placement and visibility.
5. Estimate navigation value or social interaction value.

## OCR and scene text options

### PaddleOCR

Why it matters:
PaddleOCR is a strong first baseline for OCR and scene text because it is actively maintained, supports many languages, and includes practical deployment paths.

Potential use:
- detect text regions in architectural interiors
- OCR room numbers, exits, toilets, department labels, and directories
- produce text boxes and confidence values
- feed sign candidates into a higher-level sign classifier

Strength:
- practical and actively maintained
- multilingual support
- scene text support
- deployable locally

Risk:
- OCR alone does not know whether text is signage
- small or oblique signs may fail
- decorative text may become false positive signage

### DB and DB plus plus text detection

Why it matters:
DB style text detection is useful for detecting irregular scene text regions. It is a candidate for sign region detection before OCR.

Potential use:
- detect candidate text regions
- crop sign-like areas
- pass cropped regions to OCR and sign classifier

Risk:
- detects all text, not only signs
- may miss icons with no text
- may detect posters or decorative words that are not wayfinding signs

### MMOCR

Why it matters:
MMOCR is a PyTorch and OpenMMLab based OCR toolkit supporting detection, recognition, key information extraction, and evaluation tools.

Potential use:
- compare against PaddleOCR
- use modular text detectors and recognizers
- build evaluation scripts for sign OCR accuracy

Risk:
- heavier setup
- may be more complex than needed for first prototype

## Navigation and signage references

### SignNav

Why it matters:
SignNav directly frames signs as semantic navigation hints in large scale indoor environments like hospitals and airport terminals. This is very close to Professor Kirsh's signage direction.

Potential use:
- conceptual framing for sign assisted navigation
- sign to action reasoning
- navigation value score
- hospital and airport examples

Core insight for Image Tagger:
A sign is not just an object. It changes what action a person can infer from a viewpoint.

### NaVIP

Why it matters:
NaVIP is useful because it is image-centric indoor navigation. It has phone camera images, pose labels, indoor points of interest, captions, and public code.

Potential use:
- inspiration for collecting interior image validation data
- point of interest based navigation framing
- image plus pose plus caption structure
- accessibility focused evaluation

Core insight for Image Tagger:
Even without a building map, images can support navigation and exploration if linked to points of interest and local cues.

## Isovists and visibility

Potential methods:
- point isovist
- path isovist
- region isovist
- visibility graph analysis
- directed visibility
- co-visibility
- integration
- choice
- depth to location

Use in signage:
- estimate which signs are visible from a path
- estimate whether a sign is visible before a decision point
- rank signs by visibility value
- identify blind spots where wayfinding support is weak

Important distinction:
If the system has true floor plan or 3D geometry, isovist claims can be stronger. If the system only has a single image and a depth map, claims should be marked as image plane or 2.5D proxy.

## Materials to acoustics

Potential material categories:
- glass
- stone
- tile
- concrete
- metal
- wood
- carpet
- fabric
- curtains
- acoustic panels
- upholstered furniture
- bookshelves
- plants

Possible acoustic derived attributes:
- acoustic_absorption_proxy
- acoustic_reflection_proxy
- speech_privacy_proxy
- overhearing_risk
- speech_intelligibility_zone
- reverberation_risk

Validation issue:
Acoustic outputs are inferred from visual evidence. They should not be labeled as directly measured acoustics unless actual acoustic data is available.

## Social interaction attributes

Potential social outputs:
- private_conversation_support
- small_group_meeting_support
- queueing_support
- service_interaction_support
- navigational_help_seeking_likelihood
- passive_copresence_support
- emergency_movement_support
- conversational_privacy
- overhearing_risk
- social_exposure_from_point

Evidence sources:
- room function
- seating layout
- material softness
- enclosure
- isovist exposure
- sign visibility
- circulation path clarity
- object density
- lighting
- acoustic proxies

## Recommendation

Next prototype should not start by training a model. It should start by building a narrow, inspectable pipeline:

1. collect 50 to 100 real interior examples
2. annotate sign bounding boxes and function
3. run PaddleOCR or MMOCR
4. classify signs using a small controlled taxonomy
5. assign placement and navigation role
6. calculate simple visibility and image position proxies
7. produce a report card per image

First target building types:
- hospitals
- offices

First sign types:
- exit
- toilet
- room number
- meeting room display
- directional arrow
- directory
