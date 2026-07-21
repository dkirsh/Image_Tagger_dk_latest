# CNfA FULL ATTRIBUTE TABLE — built + planned + newly harvested candidates
### Image_Tagger / CNfA · 2026-07-18 (Cowork) · FOR CODEX VERIFICATION

*Extends `CNFA_ATTRIBUTE_INVENTORY_2026-07-18.md`. Sections A–C (built operators, committee primitives,
panel compounds) are unchanged and live in that file. This file adds **Section D: a large harvested
candidate pool** drawn from the 424-construct canonical registry
(`TRS_v1.1/core/trs-core/v0.2.8/registry/cnfa_tag_registry_canonical_v0.2.8.yaml`), all marked
**NEEDS FINAL VERIFICATION** — i.e. collected as candidate viz operators but NOT yet feasibility-checked,
overlap-deduped, or spec'd. Codex's job (see `CODEX_DEEPEN_PLAN_AND_TESTPLAN_PROMPT_2026-07-18.md`) is to
verify each: is it image-computable, does a fraction already exist, what tier, and does it earn a build slot.*

**State vocabulary (unchanged) + one new state.** DONE+EXT / DONE+INT / SPEC+PLAN / NEEDS PLAN /
REJECTED as before, plus **NEEDS FINAL VERIFICATION** = harvested construct, not yet triaged into the
build plan. "existing fraction" = heuristic overlap with a built operator (verify, don't trust).

**Scope note (important).** Not everything in the canonical registry is a *viz* operator:
- `env.v1` (82) are the **physical code** (lux, CO₂, RT60, melanopic EDI) — instruments/specs, not image ops.
- `sound/smell/touch` (10) are **other sensors**, out of the image pipeline.
- `affect.*` / `cognitive.*` are **outcome targets** (what we validate against), not operators.
The genuinely image-computable candidate families are **env.v2a (74)** and **arch.pattern (20)**, enumerated
below; the rest are summarized with a verdict.

---

## SECTION D — HARVESTED CANDIDATE POOL (all NEEDS FINAL VERIFICATION)

### D-1. env.v2a — perceptual cues (74) — the prime image-computable candidates

| construct id | what it is | existing fraction | state |
|---|---|---|---|
| `v2a_001` | color palette hue saturation lightness harmony beyond cct | palette_entropy | NEEDS FINAL VERIFICATION |
| `v2a_002` | warm vs cool white appearance cct and perceived coziness act | warm/cool | NEEDS FINAL VERIFICATION |
| `v2a_003` | brightness level at eye vertical illuminance vs task plane | brightness_variance; brightness/glare | NEEDS FINAL VERIFICATION |
| `v2a_004` | brightness gradients and brightness contrast ratios | brightness_variance; brightness | NEEDS FINAL VERIFICATION |
| `v2a_005` | daylight presence sky view and view to outside content | C10; C9/C10 | NEEDS FINAL VERIFICATION |
| `v2a_006` | glare source count | glare_risk | NEEDS FINAL VERIFICATION |
| `v2a_007` | flicker temporal modulation risk cues led drivers | (new) | NEEDS FINAL VERIFICATION |
| `v2a_008` | color rendering saturation rendering | palette_entropy | NEEDS FINAL VERIFICATION |
| `v2a_009` | shadow softness hardness | (new light) | NEEDS FINAL VERIFICATION |
| `v2a_010` | lighting control cues dimmers blinds task lights | C17 | NEEDS FINAL VERIFICATION |
| `v2a_011` | evening like ambience cues vs daytime like ambience cues | (new) | NEEDS FINAL VERIFICATION |
| `v2a_012` | visual privacy via lighting backlit silhouettes vs evenly li | C7 | NEEDS FINAL VERIFICATION |
| `v2a_013` | high contrast spotlight social exposure cues | brightness | NEEDS FINAL VERIFICATION |
| `v2a_014` | presence of natural light patterns | C19/materials | NEEDS FINAL VERIFICATION |
| `v2a_015` | lighting temperature mismatch | (new) | NEEDS FINAL VERIFICATION |
| `v2a_067` | ceiling height and openness processing style | (needs height) | NEEDS FINAL VERIFICATION |
| `v2a_068` | room scale cues | (new) | NEEDS FINAL VERIFICATION |
| `v2a_069` | enclosure ratio wall to window balance | enclosure; prospect/daylight | NEEDS FINAL VERIFICATION |
| `v2a_070` | prospect refuge ability to see without being seen | prospect/C11; C11 | NEEDS FINAL VERIFICATION |
| `v2a_071` | exit visibility and path to exit complexity | V6/processing_load | NEEDS FINAL VERIFICATION |
| `v2a_072` | blind corners vs transparent partitions | (new) | NEEDS FINAL VERIFICATION |
| `v2a_073` | distance to others | (new) | NEEDS FINAL VERIFICATION |
| `v2a_074` | wayfinding legibility straight sightlines | C4; C3/C4 | NEEDS FINAL VERIFICATION |
| `v2a_075` | spatial complexity branching corridors vs simple loops | V6/processing_load | NEEDS FINAL VERIFICATION |
| `v2a_076` | perceived territoriality defined zones vs ambiguous shared s | C16 | NEEDS FINAL VERIFICATION |
| `v2a_077` | barrier permeability half walls vs full walls | (new) | NEEDS FINAL VERIFICATION |
| `v2a_078` | visual access to outdoors nature as escape affordance | (new) | NEEDS FINAL VERIFICATION |
| `v2a_079` | seating prospect facing entrance vs back to entrance | prospect/C11 | NEEDS FINAL VERIFICATION |
| `v2a_080` | verticality cues | (new) | NEEDS FINAL VERIFICATION |
| `v2a_081` | personal safety affordances lighting in corners | (new) | NEEDS FINAL VERIFICATION |
| `v2a_082` | curvature prevalence vs sharp angles | V1 contour | NEEDS FINAL VERIFICATION |
| `v2a_083` | symmetry and regularity | symmetry | NEEDS FINAL VERIFICATION |
| `v2a_084` | fractal self similar edge statistics | fractal_dimension/V9; edge_clarity/V13 | NEEDS FINAL VERIFICATION |
| `v2a_085` | clutter disorder object density occlusion surface coverage | V6/V7/processing_load; C12 | NEEDS FINAL VERIFICATION |
| `v2a_086` | cleanliness maintenance stains damage wear | (new) | NEEDS FINAL VERIFICATION |
| `v2a_087` | color diversity and saturation | palette_entropy | NEEDS FINAL VERIFICATION |
| `v2a_088` | texture density | C12; materials texture | NEEDS FINAL VERIFICATION |
| `v2a_089` | artwork density and semantic content | C12 | NEEDS FINAL VERIFICATION |
| `v2a_090` | naturalness of materials | materials cues; C19/materials | NEEDS FINAL VERIFICATION |
| `v2a_091` | visual complexity gradients | V6/processing_load | NEEDS FINAL VERIFICATION |
| `v2a_092` | signage density informational load | C12; (new) | NEEDS FINAL VERIFICATION |
| `v2a_093` | visual affordances for organization | (new) | NEEDS FINAL VERIFICATION |
| `v2a_094` | orderliness of lines alignment | (new) | NEEDS FINAL VERIFICATION |
| `v2a_095` | perceptual mystery cues | (new) | NEEDS FINAL VERIFICATION |
| `v2a_096` | visible vegetation quantity proximity and distribution | (new veg) | NEEDS FINAL VERIFICATION |
| `v2a_097` | window view content greenery sky water vs built up | prospect/daylight; C9/C10 | NEEDS FINAL VERIFICATION |
| `v2a_098` | natural materials wood stone | materials cues; material cov | NEEDS FINAL VERIFICATION |
| `v2a_099` | blue space | (new) | NEEDS FINAL VERIFICATION |
| `v2a_100` | prospect to distant views | prospect/C11; C9/C10 | NEEDS FINAL VERIFICATION |
| `v2a_101` | natural ventilation cues | C19/materials | NEEDS FINAL VERIFICATION |
| `v2a_102` | natural sound sources | C19/materials; C7/C20 | NEEDS FINAL VERIFICATION |
| `v2a_103` | daylight nature coupling | C10 | NEEDS FINAL VERIFICATION |
| `v2a_104` | seasonal cues | (new) | NEEDS FINAL VERIFICATION |
| `v2a_105` | animal presence cues | (new) | NEEDS FINAL VERIFICATION |
| `v2a_106` | sociopetal seating | (new) | NEEDS FINAL VERIFICATION |
| `v2a_107` | density crowding proxies chairs per area people present queu | C12 | NEEDS FINAL VERIFICATION |
| `v2a_108` | surveillance cues cameras exposed workstations panoramic vis | (new) | NEEDS FINAL VERIFICATION |
| `v2a_109` | privacy cues partitions doors curtains | C7 | NEEDS FINAL VERIFICATION |
| `v2a_110` | territoriality markers name plates | C16 | NEEDS FINAL VERIFICATION |
| `v2a_111` | norm cues formal vs informal | (new) | NEEDS FINAL VERIFICATION |
| `v2a_112` | shared resource competition cues | (new) | NEEDS FINAL VERIFICATION |
| `v2a_113` | social mixing affordances | (new) | NEEDS FINAL VERIFICATION |
| `v2a_114` | conflict overhearing risk cues | (new) | NEEDS FINAL VERIFICATION |
| `v2a_115` | waiting time cues | (new) | NEEDS FINAL VERIFICATION |
| `v2a_116` | user controls visible and accessible dimmers blinds thermost | C17 | NEEDS FINAL VERIFICATION |
| `v2a_117` | furniture adjustability movable chairs tables | (new) | NEEDS FINAL VERIFICATION |
| `v2a_118` | choice richness multiple zones | (new) | NEEDS FINAL VERIFICATION |
| `v2a_119` | personalization affordances pinboards | (new) | NEEDS FINAL VERIFICATION |
| `v2a_120` | policy cues restricting control | C17 | NEEDS FINAL VERIFICATION |
| `v2a_121` | control over privacy doors | C7; C17 | NEEDS FINAL VERIFICATION |
| `v2a_122` | control over sound headsets | C7/C20; C17 | NEEDS FINAL VERIFICATION |
| `v2a_123` | control over thermal fans | C17 | NEEDS FINAL VERIFICATION |
| `v2a_124` | control over lighting task lamps | C17 | NEEDS FINAL VERIFICATION |
| `v2a_125` | information control clear wayfinding reduces uncertainty | C4; C17 | NEEDS FINAL VERIFICATION |
### D-2. arch.pattern — architectural pattern detectors (20)

| construct id | what it is | existing fraction | state |
|---|---|---|---|
| `arch.pattern.axial_circulation_clear` | axial circulation clear | (new) | NEEDS FINAL VERIFICATION |
| `arch.pattern.bay_window` | bay window | prospect/daylight | NEEDS FINAL VERIFICATION |
| `arch.pattern.central_hearth` | central hearth | (new) | NEEDS FINAL VERIFICATION |
| `arch.pattern.circulation_maze_like` | circulation maze like | (new) | NEEDS FINAL VERIFICATION |
| `arch.pattern.colonnade` | colonnade | (new) | NEEDS FINAL VERIFICATION |
| `arch.pattern.corner_window` | corner window | prospect/daylight | NEEDS FINAL VERIFICATION |
| `arch.pattern.daylight_hard` | daylight hard | C10 | NEEDS FINAL VERIFICATION |
| `arch.pattern.daylight_soft` | daylight soft | C10 | NEEDS FINAL VERIFICATION |
| `arch.pattern.double_height_space` | double height space | (new) | NEEDS FINAL VERIFICATION |
| `arch.pattern.gallery_edge` | gallery edge | edge_clarity/V13 | NEEDS FINAL VERIFICATION |
| `arch.pattern.loft_mezzanine` | loft mezzanine | (new) | NEEDS FINAL VERIFICATION |
| `arch.pattern.long_view_corridor` | long view corridor | C9/C10 | NEEDS FINAL VERIFICATION |
| `arch.pattern.perimeter_seating` | perimeter seating | (new) | NEEDS FINAL VERIFICATION |
| `arch.pattern.prospect_strong` | prospect strong | prospect/C11 | NEEDS FINAL VERIFICATION |
| `arch.pattern.refuge_nook` | refuge nook | C11 | NEEDS FINAL VERIFICATION |
| `arch.pattern.refuge_strong` | refuge strong | C11 | NEEDS FINAL VERIFICATION |
| `arch.pattern.skylight_dominant` | skylight dominant | (new) | NEEDS FINAL VERIFICATION |
| `arch.pattern.staircase_sculptural` | staircase sculptural | (new) | NEEDS FINAL VERIFICATION |
| `arch.pattern.threshold_emphasized` | threshold emphasized | (new) | NEEDS FINAL VERIFICATION |
| `arch.pattern.window_seat_niche` | window seat niche | prospect/daylight | NEEDS FINAL VERIFICATION |
### D-3. Remaining canonical families — verdict summary (verify before enumerating)

| family | count | verdict |
|---|---|---|
| env.ae (binary AE tags) | 92 | CANDIDATE — high-level binary tags; mostly derivable by thresholding our continuous operators OR a VLM classifier. Verify overlap before building. |
| env.v1 (physical-code numeric) | 82 | PHYSICAL CODE — lux/CO2/RT60/melanopic etc. Needs instruments or declared spec inputs, NOT image viz operators. Out of the viz-operator scope. |
| env.v2a (perceptual cues) | 74 | verify |
| cnfa.* (engine) | 48 | MIXED — many already built (this is our own namespace); cross-ref the built list, the remainder are dynamic/depth/geometry candidates. |
| arch.pattern.* | 20 | verify |
| component.* (object detect) | 19 | CANDIDATE — object/material detection (brass fixture, coffered ceiling). Needs a detector (VLM/CNN); not classical CV. Tier caps AMBER. |
| misc semantic | 11 | MIXED — plant_count/biophilic ratio candidate; provenance/science.* are meta. |
| materials.* | 11 | MOSTLY BUILT/OVERLAP — material coverage/cues already in attributes.py; verify deltas only. |
| spatial.* | 11 | OVERLAP — central_openness/depth/isovist overlap C1/prospect/enclosure; verify deltas. |
| style.* | 11 | CANDIDATE — style classifiers (japandi, industrial...). VLM; descriptive, weak construct link. |
| cross-modal (sound/smell/touch) | 10 | OUT OF SCOPE for viz — different sensors (audio/chemo/haptic), not the image pipeline. |
| color.* | 7 | OVERLAP — lab/luminance/warmth overlap palette_entropy + warm/cool; verify deltas. |
| cognitive.* | 6 | OUTCOME TARGETS — coherence/legibility/mystery/restoration are L3 targets, not operators (some map to C3/C4). |
| affect.* | 5 | OUTCOME TARGETS — cozy/tranquil/scary are affect labels (targets), not operators. |
| isovist/affordance | 5 | OVERLAP — isovist area/compactness overlap C1 VGA/prospect; verify deltas. |
| texture.* | 4 | OVERLAP — micro/macro contrast overlap materials texture cues; verify deltas. |
| complexity.* | 3 | OVERLAP — edge/shannon/spatial entropy overlap V6/processing_load. |
| social.* | 3 | OVERLAP/NEEDS INPUT — occupancy/privacy/sociopetal overlap C7/C12/C23 (need seats). |
| meta/provenance | 2 | META — tag.evidence_pointer etc.; not attributes. |
---

## What "final verification" means for Section D (the Codex ask)
For each candidate: (1) is it **image-computable** with classical CV / geometry, or does it need a
pretrained model (→ AMBER) or a non-image sensor (→ out of scope)? (2) does a **fraction already exist**
in `cnfa_algs/` (dedupe — do not rebuild)? (3) what is its **honest tier**? (4) does it have a **real
construct→outcome link** in the literature or is it descriptive-only? (5) does it earn a **build slot**,
and in which wave? Output feeds the construction spec (`CNFA_CONSTRUCTION_SPEC_2026-07-18.md`).

*Counts: A–C carry 45 built + 56 committee + 48 compound (from the inventory file). Section D adds
74 env.v2a + 20 arch.pattern enumerated + ~330 more across summarized families — a large pool to triage.*
