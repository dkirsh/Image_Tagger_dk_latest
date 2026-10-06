# Social Interaction Attribute Taxonomy

Date: 2026-07-21  
Purpose: Define social interaction types before deriving architectural attributes.

## Why this matters

Social interaction attributes should not be added as vague labels. Different social interactions need different spatial, visual, acoustic, material, and signage evidence. The first step is to classify the interaction types, then define what environmental attributes matter for each type.

## Interaction classes

### 1. Private one to one conversation

Examples:
- confidential discussion
- counseling
- private office talk
- doctor patient conversation

Relevant attributes:
- acoustic privacy
- visual privacy
- enclosure
- distance from circulation path
- soft material ratio
- speech intelligibility inside zone
- overhearing risk outside zone
- refuge quality

### 2. Small group meeting

Examples:
- team meeting
- design review
- seminar discussion
- meeting room collaboration

Relevant attributes:
- sociopetal seating
- speech intelligibility among participants
- meeting room legibility
- display visibility
- room scheduling signage
- acoustic absorption
- glare on screens
- table orientation
- enclosure without isolation

### 3. Public presentation

Examples:
- lecture
- conference talk
- lobby presentation
- town hall

Relevant attributes:
- speaker visibility
- audience sightlines
- acoustic projection
- screen visibility
- seating orientation
- crowd capacity
- entry and exit clarity
- signage to room

### 4. Service interaction

Examples:
- reception desk
- hospital registration
- retail checkout
- information desk

Relevant attributes:
- desk visibility
- queue affordance
- signage clarity
- approachability
- access control
- privacy at counter
- staff visibility
- waiting area proximity

### 5. Waiting and queuing

Examples:
- hospital waiting
- airport line
- office reception waiting
- cafeteria queue

Relevant attributes:
- queue path clarity
- seating availability
- crowding risk
- signage visibility
- prospect to service point
- acoustic comfort
- social exposure
- movement conflict

### 6. Casual encounter

Examples:
- hallway chat
- lounge encounter
- coffee area conversation
- lobby interaction

Relevant attributes:
- path intersection
- pause affordance
- standing zones
- visibility to others
- acoustic masking
- seating nearby
- social exposure
- interruption likelihood

### 7. Collaborative work

Examples:
- open office collaboration
- studio work
- lab teamwork
- group project work

Relevant attributes:
- shared surface availability
- display visibility
- seating flexibility
- acoustic separation from quiet zones
- writable surfaces
- material durability
- task lighting
- proximity to tools

### 8. Navigational help seeking

Examples:
- asking for directions
- finding a room
- locating restroom
- finding exit

Relevant attributes:
- signage visibility
- landmark salience
- route legibility
- decision point ambiguity
- staff desk visibility
- directory availability
- room number clarity
- isovist exposure to signs

### 9. Passive co presence

Examples:
- people sharing a lobby
- people reading in a library
- people waiting silently
- open office co presence

Relevant attributes:
- social density
- visual exposure
- acoustic masking
- seating separation
- refuge pockets
- movement paths
- lighting comfort
- privacy gradient

### 10. Emergency movement

Examples:
- evacuation
- emergency department routing
- fire exit movement
- crowd redirection

Relevant attributes:
- exit sign visibility
- path clarity
- bottleneck risk
- emergency lighting
- stair visibility
- corridor width proxy
- decision point signs
- crowd flow risk

## Derived attribute candidates

The following attributes should be considered for operationalization:

- conversational_privacy
- overhearing_risk
- speech_intelligibility_zone
- social_visibility
- social_exposure_from_point
- gathering_affordance
- queueing_affordance
- approachability
- interruption_likelihood
- route_legibility
- sign_visibility_from_path
- decision_point_support
- refuge_for_private_interaction
- prospect_for_public_interaction

## Evidence sources

Potential evidence sources:

- isovist area
- visibility graph measures
- path exposure maps
- material classification
- soft surface ratio
- room function
- seating layout
- object detection
- signage detection
- OCR
- depth map
- segmentation
- VLM candidate judgment

## Contract rule

Each social attribute must declare whether it is:

- directly observed
- computed from visible geometry
- inferred from material or spatial evidence
- VLM judged
- composite

Inferred social attributes should not be given high confidence unless they have multiple supporting evidence sources.
