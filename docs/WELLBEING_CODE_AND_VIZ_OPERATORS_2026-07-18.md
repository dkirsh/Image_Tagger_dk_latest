# THE WELL-BEING CODE AND ITS VIZ OPERATORS
### Image_Tagger / CNfA · 2026-07-18 (Cowork)

*A short, standalone explainer of the well-being code: what it is, how it relates to the physical
and cognitive codes, each computable viz operator with its scientific justification and location,
and how much each matters for diagnosing whether a space is cognitively/affectively effective or
needs design improvement. The dated Appendix gives every operator's development state.*

---

## 1. What the well-being code is

The **well-being code** is a normative specification of a building written in the **health and
affect constructs** the research literature shows actually change how people *feel and fare* —
stress physiology, restoration of depleted attention, circadian regulation, air-borne cognitive
load, thermal pleasure, and social connectedness — rather than in the physical units of the
container. Where the cognitive code asks "can people think, find their way, concentrate, connect?",
the well-being code asks "does the space **reduce stress and support health over the day**, or
quietly erode them?" It reads every environmental measure as a **cost** (glare, noise, heat, poor
air) or a **resource** (daylight, greenery, refuge, real control); well-being accrues when resources
outweigh costs over time. It is, by construction, longitudinal (a trajectory across the day/week)
and conditional (a fit between building, occupant, and task).

## 2. How it relates to the physical code and the cognitive code

We have all three defined:

- **Physical code** (what design/POE use today): the container in physical units against fixed,
  occupant-independent thresholds — lux, dBA, °C, m²/person, air changes/hour. Necessary; prevents
  gross failure; says nothing about the human outcome.
- **Cognitive code**: the building–occupant *relation* in human-relevant cognitive constructs —
  speech **intelligibility** not level, **melanopic** light not lux, perceived crowding *under
  control* not density, prospect-refuge at the *preferred* position, wayfinding, fluency.
- **Well-being code**: the **same measures, read for health and affect** — the parallel register.

The crucial architectural point: **the well-being code is not a separate computation.** It runs over
the *same* CNfA attribute engine as the cognitive code; most operators are tagged `SHARED` (they feed
both registers) or `WB` (well-being-dominant). A glazed façade is one geometry that the cognitive
code reads for daylight/view access and the well-being code reads for circadian dose *and* glare/heat
cost. The two codes are two *interpretations* of one set of computed attributes — which is why the
"compound attribute" work (synergy / antagonism / masking) matters equally to both.

## 3. The well-being viz operators (what, why, where, how important)

"Importance" = how strongly the operator discriminates a space that is **cognitively/affectively
effective** from one that **needs design improvement**. HIGH = a bad value is a strong, well-evidenced
signal to redesign; MED = a real but weaker or contested signal.

**C19 — restoration / nature contact** *(WB)*. Per-seat line-of-sight to greenery / a nature-facing
window. *Why:* Ulrich's Stress Recovery Theory (Ulrich 1984; Ulrich et al. 1991) — unthreatening
nature drives parasympathetic recovery within minutes (EDA↓, BP↓, HRV↑); Kaplan's Attention
Restoration Theory (Kaplan & Kaplan 1989; Kaplan 1995) — soft fascination replenishes directed
attention. *Where:* `cnfa_algs/wellbeing_plan.py` (`restoration_nature`). *Importance:* **HIGH** — a
desk with zero restorative access in a high-demand zone is a defensible redesign flag. *(Needs a
nature-cell map; abstains on image-only.)*

**C18 — air quality** *(WB)*. Steady-state CO₂ at design occupancy + outdoor-air L/s/person + VOC
class. *Why:* ventilation and VOC load move cognition and symptoms (Allen et al. 2016; Wargocki et
al. 2000) with a real health-and-productivity economics (Fisk 2000). *Where:* `wellbeing_plan.py`
(`air_quality`). *Importance:* **HIGH** — the strongest money-backed lever; a failing value is a
direct, cheap-to-fix design defect. *(Spec input: air spec.)*

**C22 — circadian contrast** *(WB)*. Daytime melanopic-light contrast proxy at the eye across the
plan. *Why:* ipRGC→SCN signalling; high melanopic dose by day / low by evening stabilises circadian
phase, alertness, and sleep (Lucas et al. 2014; CIE S 026:2018; Brown et al. 2022). *Where:*
`cnfa_algs/daylight_view.py`. *Importance:* **HIGH (mechanism) / MED (thresholds)** — seats that
never reach a daytime circadian target are a real flag; exact dose thresholds are expert-consensus,
not RCT.

**C10 — daylight proximity** *(SHARED)*. Geometric daylight access per seat. *Why:* daylight access
predicts sleep and mood (Boubekri et al. 2014). *Where:* `daylight_view.py`. *Importance:* **MED–HIGH**
— strong direction; a windowless deep-plan seat is a legitimate flag. *(Certified melanopic-at-eye
needs a spectral input — see Needs Plan.)*

**C21 — thermal comfort (adaptive + alliesthesia)** *(WB)*. Adaptive-opportunity + radiant + thermal-
pleasure proxy, not a single setpoint. *Why:* adaptive comfort predicts satisfaction in free-running
buildings (de Dear & Brager 1998); thermal *change* can be pleasurable (Cabanac 1971 alliesthesia).
*Where:* `cnfa_algs/thermal_plan.py`. *Importance:* **MED** — real, but the operator is a proxy until
radiant/adaptive inputs are supplied.

**C17 — functioning local control** *(WB)*. Credits control **only where it targets the zone's
binding stressor** (a dimmer where glare binds, not a generic "has controls" bonus). *Why:* perceived
control is a top "killer variable" for satisfaction (Leaman & Bordass 1999), qualified by whether the
control actually works (Newsham et al. 2012). *Where:* `wellbeing_plan.py` (`local_control`).
*Importance:* **MED–HIGH** — a zone whose binding stressor has no matching control is a clear flag.

**C16 — territory / personalization** *(WB)*. Assigned-seat ratio + team-anchor provision. *Why:*
territoriality and personalization support belonging and well-being (Altman; Wells 2000). *Where:*
`wellbeing_plan.py` (`territory_provision`). *Importance:* **MED** — belonging is real but the signal
is weaker and policy-dependent.

**C23 — social connectedness** *(SHARED)*. Commons provision per N + isolated-seat detection. *Why:*
social connection is a health variable (the W-F literature); co-presence + commons predict informal
support. *Where:* `wellbeing_plan.py` (`social_connectedness`). *Importance:* **MED–HIGH** — an
isolated seat set far from any commons is a defensible flag.

**V2 — spectral slope deviation (visual-discomfort proxy)** *(WB, image operator)*. Radial 1/f power-
slope + mid-band residual. *Why:* deviation from natural 1/f image statistics predicts visual
discomfort/stress (Field 1987; Fernandez & Wilkins 2008; Penacchio & Wilkins 2015). *Where:*
`cnfa_algs/reliable_attrs.py` (`spectral_slope_deviation`). *Importance:* **MED** — a genuinely
discomforting striped/gridded surface is a real flag, **but this is an honest PROXY (not the 2-D
Penacchio–Wilkins metric) and now carries an AMBER ceiling** after external review.

**Shared fluency operators that also serve well-being.** The perceptual-fluency → affect layer
(`cnfa_algs/hedonics.py`) and the fractal mid-D band (`fractal_band.py`, V9) bear on well-being via
fractal-fluency stress reduction (Taylor; Spehar); tagged `SHARED`, AMBER.

## 4. How the well-being code is used in diagnosis

A region is read twice off one annotation: the **cognitive** readout (can you think/navigate/connect
here?) and the **well-being** readout (does it recover you or load you?). The diagnostic value is
strongest where the two **diverge** — e.g., a beautiful daylit atrium seat (cognitive: fine) that is
also a glare + thermal cost with no control (well-being: redesign). The masking-diagnostic compounds
exist precisely to catch a space that *reports* well (warm materials, greenery) while a hidden cost
(reverberation, low melanopic dose, poor air) still loads physiology — the subjective→biosignal→
physical triplet is how that is validated. HIGH-importance WB operators (C18 air, C19 restoration,
C22 circadian) are the ones whose failing value most reliably means "this space needs design work,"
not just "this space scored lower."

---

## Appendix — WELL-BEING VIZ OPERATOR STATE (as of 2026-07-18)

State key: **DONE+EXT** = built, tested, and survived an external adversarial review (Fable panel
and/or Codex attack). **DONE+INT** = built + internally (unit/harness) tested, not yet external.
**SPEC+PLAN** = committee-spec'd, skeptic-verified, in a build order, not yet built. **NEEDS PLAN** =
construct named, no operator and no build plan yet.

| Operator | Code | What it does | Why it matters for CNfA | Location | Dev state |
|---|---|---|---|---|---|
| C19 restoration_nature | WB | per-seat LOS to greenery/nature window | Ulrich SRT + Kaplan ART; HIGH redesign signal | `cnfa_algs/wellbeing_plan.py` | DONE+EXT (Fable C1–C24 panel); needs nature-cell input |
| C18 air_quality | WB | CO₂ + L/s/person + VOC class | Allen 2016/Fisk 2000; HIGH, money-backed | `cnfa_algs/wellbeing_plan.py` | DONE+EXT (panel); needs air spec |
| C22 circadian_contrast | WB | daytime melanopic contrast proxy | Lucas 2014/CIE S026/Brown 2022; HIGH mechanism | `cnfa_algs/daylight_view.py` | DONE+EXT (panel) |
| C10 daylight_proximity | SHARED | geometric daylight access per seat | Boubekri 2014; MED–HIGH | `cnfa_algs/daylight_view.py` | DONE+EXT (panel) |
| C21 thermal (adaptive+alliesthesia) | WB | adaptive/radiant/pleasure proxy | de Dear&Brager; Cabanac; MED | `cnfa_algs/thermal_plan.py` | DONE+EXT (panel); needs radiant input |
| C17 local_control | WB | control credited only vs binding stressor | Leaman&Bordass killer variable; MED–HIGH | `cnfa_algs/wellbeing_plan.py` | DONE+EXT (panel); needs control-zone input |
| C16 territory_provision | WB | assigned-seat ratio + team anchor | Altman/Wells belonging; MED | `cnfa_algs/wellbeing_plan.py` | DONE+EXT (panel); needs territory spec |
| C23 social_connectedness | SHARED | commons/N + isolated-seat detection | social connection as health var; MED–HIGH | `cnfa_algs/wellbeing_plan.py` | DONE+EXT (panel); needs seats/commons input |
| V2 spectral_slope_deviation | WB | radial 1/f slope + mid-band residual (discomfort proxy) | Wilkins visual discomfort; MED | `cnfa_algs/reliable_attrs.py` | DONE+EXT (Fable+Codex×2) → AMBER honest proxy |
| V9 fractal_mid_d_band | SHARED | mid-D fractal-fluency band score | Taylor/Spehar fractal fluency; MED | `annotation_socket/predicates/fractal_band.py` | DONE+EXT (Codex) → AMBER |
| hedonics fluency→affect layer | SHARED | perceptual-fluency inverted-U affect | Reber/Winkielman; MED | `cnfa_algs/hedonics.py` | DONE+INT (L0-tested) |
| V3 visible_vegetation_fraction | WB | pixel fraction of live greenery in view | Ulrich 1984; catches desk-facing-blank-wall | committee report `docs/COMMITTEE_NEW_VISUAL_ATTRIBUTES_2026-07-15.*` | SPEC+PLAN (VIABLE, AMBER) |
| V8 spectral_naturalness | WB | orientation-isotropy naturalness | Oliva&Torralba; upstream of restoration | committee report | SPEC+PLAN (AMBER) |
| V12 natural_material_fraction | WB | visible wood/stone fraction (dose–response) | Tsunetsugu 2007 wood & relaxation | committee report | SPEC+PLAN (AMBER) |
| V14 luminance_histogram_shape | WB | luminance distribution statistics | Van Den Wymelenberg&Inanici 2014 | committee report | SPEC+PLAN (AMBER) |
| V24 visible_window_wall_ratio | WB | aperture fraction on wall planes | Keep 1980 delirium/recovery w/ windows | committee report | SPEC+PLAN (AMBER) |
| V41 view_depth_layering | WB | number of visible view layers/depth | Ulrich 1983 depth preference | committee report | SPEC+PLAN (AMBER) |
| V43 material_perceived_warmth | WB | perceived material warmth | Wastiels 2012 material experience | committee report | SPEC+PLAN (AMBER) |
| V18 vantage_prospect_refuge_balance | WB | seat-level prospect×refuge balance | Appleton 1975 | committee report | SPEC+PLAN — NEEDS extra input (seat map) |
| V53 water_feature_presence | WB | visible blue-space | White et al. 2010 blue space | committee report | SPEC+PLAN — NEEDS extra input |
| Certified melanopic-at-eye | WB | true melanopic EDI at the eye | CIE S026 — beyond geometric proxy | (construct only) | NEEDS PLAN (spectral input / Tier-C) |
| Stress-physiology hooks | WB | subjective→biosignal→physical triplet wiring | the masking-detection validation path | (construct only) | NEEDS PLAN |
| V34 maintenance_dilapidation / V48 hominess / V56 patina | WB | (proposed) upkeep / hominess / patina | — | committee report | REJECTED by skeptic (not planned) |

*Boundary (RULE 0): "DONE+EXT (panel)" for the C-series plan operators means they were built,
harness-tested, and reviewed in the 2026-07-15 Fable C1–C24 panel; construct-validation against
labeled human/biosignal data and the Mac↔sandbox replay check remain OWED for the whole set. The
plan operators require declared spec inputs (seats, air/thermal/control specs, nature cells) and
ABSTAIN honestly on an image-only unit. V2/V9 are DONE+EXT but AMBER honest proxies after the
Fable+Codex attacks — see `docs/CODEX2_ATTACK_DISPOSITION_2026-07-18.md`.*
