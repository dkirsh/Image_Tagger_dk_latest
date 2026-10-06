# Signage Annotation Contract

Date: 2026-07-21  
Purpose: Define how signage examples should be collected, annotated, and validated for Image Tagger.

## Why signage matters

Signage is not only a visual object. It is a navigation and social coordination device. A useful signage pipeline should detect signs, classify what kind of sign they are, estimate where they are placed, determine whether they are visible from relevant observer points, and decide whether they help navigation or social interaction.

## Minimum annotation fields

Each sign instance should have:

- image_id
- building_type
- sign_id
- sign_category
- sign_type
- text_visible
- text_transcription
- icon_present
- arrow_present
- placement_type
- mounting_surface
- bbox_xyxy
- readable_from_image
- estimated_viewing_distance_class
- navigation_role
- interaction_role
- decision_point_relevance
- occlusion_level
- confidence
- notes

## Building type vocabulary

Allowed building types:

- hospital
- office
- university
- airport
- train_station
- mall
- museum
- hotel
- library
- parking_garage
- other

## Sign category vocabulary

Allowed sign categories:

- directional
- identification
- safety
- regulatory
- amenity
- directory
- digital
- temporary
- interpretive
- commercial
- decorative
- unknown

## Placement vocabulary

Allowed placement types:

- overhead_hanging
- wall_mounted
- door_mounted
- glass_mounted
- freestanding
- floor_decal
- desk_mounted
- digital_panel
- ceiling_mounted
- unknown

## Navigation role vocabulary

Allowed navigation roles:

- route_choice
- destination_confirmation
- global_orientation
- emergency_routing
- access_control
- amenity_location
- schedule_coordination
- interpretation_only
- decorative_only
- unknown

## Social interaction role vocabulary

Allowed interaction roles:

- reduces_help_seeking
- supports_service_interaction
- supports_meeting_coordination
- controls_access
- supports_queueing
- supports_emergency_movement
- supports_learning
- supports_commercial_browsing
- no_social_role
- unknown

## Evidence contract

Every detected sign must include either:

- a bounding box
- a polygon
- a mask
- or an explicit reason why localization is missing

For the first prototype, bounding boxes are enough.

## Validation rules

A signage result should be considered valid only if:

1. The sign region is localized.
2. The sign category is assigned.
3. The placement type is assigned.
4. The navigation role is assigned.
5. The confidence value is finite and in the range 0 to 1.
6. If text is transcribed, the OCR confidence must be stored.
7. If the sign is treated as navigation relevant, decision point relevance must not be unknown.

## Hard cases

The validation set must include:

- small distant signs
- oblique signs
- partially occluded signs
- decorative text that is not navigational signage
- brand signs that do not help navigation
- signs visible but unreadable
- signs readable but not useful for route choice
- digital displays
- room scheduling tablets
- exit signs
- hospital department signs
- office room numbers

## First prototype rule

The first prototype should not try to solve all signage. It should detect and classify only:

- exit signs
- toilet signs
- room numbers
- meeting room displays
- directional arrows
- directories

Everything else can be recorded as unknown or other.
