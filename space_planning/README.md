# space_planning/

*Created 2026-07-14. The knowledge-first workstream for §3.6 of the Reading Space direction document
(`/Users/davidusa/REPOS/Image_Tagger_dk_latest/docs/VISION_AND_DIRECTION_2026-07-14.md`). This project is
deliberately **reading before code**: we cannot compute a good floor-plate layout until we know what the
literature says makes one good, and by which criteria one layout beats another — framed against the new
POE / cognitive-code way of deciding what matters, not the old physical-code checklist.*

## The question this folder answers
Given a fixed shell, how should desks, offices, meeting rooms, and shared spaces be laid out across a large
floor plate so as to produce measurably better cognitive and wellbeing outcomes than convention and taste —
and how do we judge one layout better than another? This is the cognitive-code paper's named killer
application and the strongest commercial case for the Zaha direction.

## What must be produced here, in order
1. **STATE_OF_KNOWLEDGE.md** — a literature synthesis: what is actually known about good space planning,
   organized as *principles* (things that reliably matter) each tagged by evidence strength (strong /
   contested / promising), with citations. Candidate bodies to cover:
   - Space syntax & workplace behaviour (UCL lineage): integration/movement, co-presence, encounter,
     visibility-graph metrics that predict workplace interaction (Hillier; Koutsolampros & Sailer).
   - Proximity & communication: the Allen curve; Kraut on distance and collaboration; functional distance
     (Festinger) — who ends up talking to whom as a function of layout.
   - Activity-based working & neighbourhood planning: zoning for focus vs collaboration; the "types" a floor
     must serve (maps onto the Q-sort occupant types in the cognitive-code paper).
   - Daylight & view allocation as a scarce resource distributed across seats (sDA/view equity).
   - Acoustic zoning: keeping speech-intelligibility below the focus threshold in quiet districts while
     collaboration districts run hot (ISO 3382-3 / the essay's Part VI).
   - Crowding-under-control, territory, prospect-refuge at the *preferred* seat (cognitive-code dimension 6).
   - Wayfinding/circulation legibility of the plan (cognitive-code dimension 5).
2. **CRITERIA.md** — the synthesis turned into a *scoring rubric*: for a candidate layout, the measurable
   criteria (per-seat prospect-refuge, daylight/view equity, speech-privacy in quiet zones, proximity of
   collaborators, circulation legibility, crowding-under-control), their directions, thresholds, and
   trade-offs, each tagged by evidence strength. This is the cognitive code rendered for the floor plate.
3. **BASELINE_REQUIREMENTS.md** — the physical-code / basic requirements that still bind (egress, code
   widths, area ratios, accessibility) — the floor beneath the cognitive-code optimisation, kept explicit so
   we never optimise a layout that fails basic code.
4. *(Later, code)* an optimiser that searches layouts against CRITERIA.md with occupant *types* as the demand
   profile, reusing the M3 plan-field machinery in `../cnfa_algs/plan.py` (isovist/space-syntax fields) and
   the acoustic/daylight simulators in `../cnfa_algs/adapters/`.

## Framing discipline (non-negotiable)
- **Cognitive code, not physical code, decides what is *good*.** Physical code sets the floor of the
  admissible; the cognitive-code criteria rank within it. Keep the two explicitly separate (CRITERIA vs
  BASELINE_REQUIREMENTS).
- **Every principle and criterion carries its evidence tag** (strong / contested / promising-import), carried
  through to any future optimiser output, exactly as in the cognitive-code paper §4.
- **Validation is required before any criterion is trusted as fact.** A layout that scores better must be
  shown to produce better outcomes — routing through the experiment platform and, eventually, real
  post-occupancy data.

## Status
EMPTY — awaiting the literature pass. The right first action (Fable/Claude, a deep-research effort) is to
produce STATE_OF_KNOWLEDGE.md. Nothing here is code yet, by design.
