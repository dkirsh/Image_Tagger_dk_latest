# CRITERIA.md — Scoring Rubric for Floor-Plate Layouts

*Space-planning workstream, `space_planning/`. Drafted 2026-07-15 (Fable/Claude Opus); revised same day to
ground it in the keystone paper, Kirsh, *From Physical Code to Cognitive Code* (working paper, 9 July 2026;
`../../../Post_Occupancy_Evals/POE_Cognitive_Code_v1_2026-07-09.md`). This turns the C1–C18 rubric in
`STATE_OF_KNOWLEDGE.md` §2 into a **scorer specification**: for a candidate layout on a fixed shell, the
measurable criteria, their directions and thresholds, the exact quantity a program computes, which piece of the
`cnfa_algs` engine computes it (or must be built to), the evidence tag, and the form of the output. It is the
cognitive code — and, from this revision on, the **well-being** strand within it — rendered for the floor plate.
It sits above `BASELINE_REQUIREMENTS.md` (the physical-code floor): baseline requirements decide what is
**admissible**; the criteria here **rank within** the admissible. Nothing scored here is trusted as fact until it
clears the validation gate in §6.*

**The three transformations this rubric must honour (keystone paper §3).** The physical code measures the
*aggregate*, the *report*, and the *snapshot*; the cognitive code measures the **signal** (melanopic not lux; STI
not dBA), the **generator** (physiology/behaviour, not the satisfaction Likert), and the **trajectory and fit**
(dose across the day, per-task-per-type, not one number for "the building"). Every criterion below is written to
compute a signal, to be validated against a generator (§6), and to be reported as a trajectory/fit rather than a
snapshot (§5). Where a criterion still leans on an aggregate or a snapshot, that is a known weakness, flagged.

---

## 0. Two objectives, one rubric

A late-breaking design decision (2026-07-15, at David's prompt) shapes this document: there is not one objective
but **two**, and every criterion is tagged by which it serves.

- **COG — the cognitive code.** Does the space let the occupant *think, perceive, find their way, focus, and
  collaborate*? The mind-as-information-processor. Outcomes: task performance, attention, memory, wayfinding
  success, realized collaboration.
- **WB — the well-being code.** Does the space let the occupant *stay calm, healthy, rested, moving, connected,
  and in good spirits*? The person-as-organism. Outcomes: stress physiology, sleep/circadian health, physical
  activity, affect/mood, social connectedness, comfort. (Scoped in `WELLBEING_STATE_OF_KNOWLEDGE.md` — see §7.)
- **SHARED** — many computed inputs feed both objectives with **different** outcome constructs. Daylight feeds
  cognitive alertness *and* circadian health *and* mood; acoustics feed concentration *and* chronic-stress
  arousal; wayfinding legibility feeds task efficiency *and* the anxiety of getting lost. These are tagged
  SHARED and **scored once but read twice** — the same physical quantity, mapped to two different outcomes with
  two different weights. The discipline (§4) is to never silently double-count a SHARED input as if it were two
  independent wins.

The objective tag is not cosmetic: it sets which weighting profile a criterion enters (§4) and which validation
target it is checked against (§6). A layout is scored against *both* objectives and can be strong on one and weak
on the other — that divergence is a finding, not an error.

**How this squares with the keystone paper.** Kirsh uses "cognitive code" as the *umbrella* term for a
specification written in human-relevant constructs spanning "cognition, affect, physiology, and behaviour" — so
well-being is not outside his cognitive code, it is a strand already inside it (dimensions 3, 6, 7, 8 and the
physiological methods layer). Our COG/WB split is therefore a **refinement, not a rival taxonomy**: we lift the
affective/physiological/health strand out as its own *scored objective* with its own outcome constructs (stress,
sleep, mood, connectedness, movement) and its own validation targets, while keeping it inside the one cognitive-
code framework. WB is a lens on the same computed signals, not a second code. `WELLBEING_STATE_OF_KNOWLEDGE.md`
will make that strand's evidence base explicit; nothing here contradicts the paper's eight dimensions.

### 0.1 Grounding in the eight canonical dimensions

The keystone paper collapses the 38-item POE inventory into **eight substantive dimensions + a methods layer + two
cross-cutting principles**. Every criterion here operationalizes one of those dimensions on the plan; the map keeps
the rubric answerable to the theory rather than to an ad-hoc grouping:

| Paper dimension | Criteria that compute it |
|---|---|
| **1. Acoustic cognition** (STI, irrelevant-speech, privacy) | C7, C8, C20 |
| **2. Light as biological/cognitive signal** (melanopic, CCT, glare, timing) | C9 (view/glazing), C10, C22; glare via `attributes.glare_risk` |
| **3. Thermal experience** (adaptive opportunity, MRT, alliesthesia) | C21 |
| **4. Air** (perceived air quality, VOC/PM + cognition) | C18 |
| **5. Spatial cognition & wayfinding** (cognitive-map accuracy, legibility cues) | C3, C4 |
| **6. Spatial affordance** (prospect–refuge, crowding-under-control, territory) | C11, C12, C16 |
| **7. Restoration, affect, aesthetics** (view content, neuroaesthetics, biophilia) | C9 (content), C19, C23, C24 |
| **8. Agency & the active body** (control efficacy, movement/metabolic) | C15, C17 |

**One structural note the paper implies.** The eight dimensions are *individual-experiential* — they score what a
seat does to the person in it. The **configurational/social layer** (encounter, movement, collaboration:
**C1, C2, C5, C6**) is not one of the eight; it is the space-syntax substrate the paper invokes specifically in §6
(space planning) as *the layer the floor-plate optimizer runs on* — it sets *where people are and whose paths
cross*, which then modulates the eight experiential dimensions. So the rubric has two strata: a configurational
substrate (C1–C6) and the eight experiential dimensions layered on it. Keeping them distinct matters because the
substrate predicts opportunity (movement, co-presence) confidently but interaction weakly (§1.3), whereas the
experiential dimensions predict individual outcomes more directly.

---

## 1. Scoring philosophy (non-negotiable)

1. **Gate, then rank.** `BASELINE_REQUIREMENTS.md` is a hard filter: a layout that fails egress, accessible
   routes, or code widths is inadmissible and is never scored. The criteria here only ever compare admissible
   layouts. The physical code sets the floor; the cognitive and well-being codes rank above it.

2. **Minimum-fit across occupant types, not the average.** Per `STATE_OF_KNOWLEDGE.md` G1–G3, occupants are
   heterogeneous and focus vs collaboration have opposite requirements. The objective is **not** a single "good
   building" scalar. The primary output is a **fit matrix** (occupant type × setting), and a layout's headline
   score is bounded by its *worst-served* segment, not lifted by its best. A plan that is excellent on average
   and hostile to the focus-dependent quartile scores as hostile-to-a-quartile, explicitly.

3. **Opportunity, not outcome, for the social criteria.** Configuration predicts where people move and co-locate
   (STRONG); it only weakly predicts whether they *interact* and barely predicts whether they *collaborate*
   (STATE_OF_KNOWLEDGE A3). So encounter/collaboration criteria (C1, C5, C6) are reported as **opportunity
   estimates with organizational caveats**, never as predicted collaboration counts. The language in any output
   must preserve this: "raises encounter probability," not "will collaborate."

4. **Every criterion carries its evidence tag** (STRONG / CONTESTED / PROMISING), inherited from the synthesis
   and carried through to any optimizer output — exactly as in the cognitive-code paper §4. A criterion's tag
   caps how hard the optimizer is allowed to push on it.

5. **Direction is safer than magnitude.** Where the literature gives a codified threshold (ISO 3382-3 r_D ≤ 5 m,
   LEED 75%-of-seats view, ≥250 melanopic-EDI) the scorer uses it. Where it gives only a direction (more prospect
   is better; shorter collaborator paths are better) the scorer ranks on the gradient and does **not** invent a
   cutoff. Fabricated precision is a validation failure.

6. **Score the plan you can compute, flag the plan you cannot.** Each criterion names its fidelity tier
   (image-only A / inferred-plan B / true-plan-or-BIM C, per the engine's existing tiers). A criterion that needs
   Tier C is reported as *unavailable* at Tier A rather than guessed.

---

## 2. Output forms

A criterion resolves to one of five machine-renderable forms; the table in §3 names each:

- **scalar** — one number for the whole floor (e.g., plan intelligibility R²).
- **per-seat** — a value at every workstation → a seat table and a choropleth over the plan.
- **field/heatmap** — a value at every free cell → a continuous surface (e.g., footfall, integration, melanopic
  light).
- **contour** — a boundary on the plan (e.g., the r_D distraction-distance ring around a collaboration zone; the
  isovist boundary of a seat).
- **matrix** — the fit matrix (occupant type × setting type), the top-level deliverable.

Every criterion also emits its **evidence tag** and **fidelity tier** as provenance, so a downstream report can
render "computed at Tier B, PROMISING evidence" beside any number.

---

## 3. The criteria

Direction/threshold, the computed quantity, the `cnfa_algs` source (✓ = implemented today; ◐ = partial/heuristic
present; ○ = specified here, to build), evidence tag, and output form. IDs C1–C18 preserve the synthesis; C19–C24
are the well-being additions flagged by David's 2026-07-15 note and detailed in `WELLBEING_STATE_OF_KNOWLEDGE.md`.

### Configuration, movement, encounter

| # | Criterion | Obj | Direction / threshold | Computed quantity | Engine source | Evid | Output |
|---|---|---|---|---|---|---|---|
| C1 | Encounter potential | COG | higher in commons; magnets at peaks | VGA **global visual integration**; check social magnets sit at integration maxima | `plan.isovist_fields` ◐ (integration field), magnet-overlay ○ | STRONG | field + scalar |
| C2 | Movement / footfall surface | COG | route past high-value collisions | **visual mean depth, connectivity, through-vision** per cell → footfall proxy | `plan.isovist_fields` ◐ | STRONG | field |
| C3 | Plan intelligibility | SHARED | higher (COG: efficiency; WB: less lost-anxiety) | **R² of connectivity vs global integration** across cells | `plan.isovist_fields` + regression ○ | STRONG (metric) | scalar |
| C4 | Wayfinding load | SHARED | fewer decision points; goals visible | decision-point count on primary routes; % junctions with a visible landmark/goal; route directness | `plan.isovist_fields` + `attributes.landmark_salience` ◐; route graph ○ | STRONG | per-route + scalar |

### Proximity and collaboration (opportunity estimates — see §1.3)

| # | Criterion | Obj | Direction / threshold | Computed quantity | Engine source | Evid | Output |
|---|---|---|---|---|---|---|---|
| C5 | Collaborator proximity | COG | must-collaborate pairs same-floor, ≤ ~30–50 m | % collaborator pairs same floor & corridor; median pairwise walking distance; # cross-floor splits (heavily penalized) | walking-distance graph on `PlanGrid` ○; needs team adjacency demand | STRONG | pair table + scalar |
| C6 | Path-overlap / collision potential | COG | higher **only among interdependent teams** | shared route length between desk pairs to common destinations, gated by interdependence | route-overlap on `PlanGrid` ○ | STRONG | pair field |

### Acoustics (the strongest empirical dissatisfier — weight first)

| # | Criterion | Obj | Direction / threshold | Computed quantity | Engine source | Evid | Output |
|---|---|---|---|---|---|---|---|
| C7 | Speech privacy in focus zones | SHARED | STI ≤ 0.50 (→0.20 confidential) | per-seat STI; **no collaboration r_D contour crosses a focus seat** | `adapters.acoustics_sim` (RT60) ◐ → STI/r_D model ○ | STRONG | per-seat + contour |
| C8 | Distraction distance (open plan) | SHARED | r_D ≤ 5 m good / >10 m poor; D2,S ≥ 7 dB; L_p,A,S,4m ≤ 48 dB | ISO 3382-3 metrics on the plan | `adapters.acoustics_sim` ◐ → ISO 3382-3 pack ○ | STRONG | contour + scalar |

### Daylight, view, circadian (scarce, spatially-fixed resources — distribute, don't peak)

| # | Criterion | Obj | Direction / threshold | Computed quantity | Engine source | Evid | Output |
|---|---|---|---|---|---|---|---|
| C9 | View equity | SHARED | ≥ 75% of seats with a qualifying nature-content view | % seats with line of sight to glazing (VLT>40%, within 3× head-height); view-content class | seat→window isovist on `PlanGrid` ○; content class from `attributes` ◐ | STRONG (codified) | per-seat + scalar |
| C10 | Circadian light equity | SHARED (WB-led) | % desks ≥ 250 melanopic-EDI for ≥ X daytime hrs | per-desk melanopic-EDI across the day; distance-to-window | daylight model ○; `attributes.vertical_illuminance` ◐ as proxy | STRONG | per-seat + field |
| C11 | Prospect–refuge seat quality | SHARED | prospect-led; back-to-wall bonus (weight prospect > refuge) | % seats with large forward isovist / window AND protected back within ~1.5 m | `attributes.prospect` ◐ + `attributes.enclosure_index` ◐ | STRONG (prospect) | per-seat |

### Crowding, focus/collaboration separation, activity, territory, control, air

| # | Criterion | Obj | Direction / threshold | Computed quantity | Engine source | Evid | Output |
|---|---|---|---|---|---|---|---|
| C12 | Perceived-crowding risk | SHARED | lower | local density × visible co-workers in isovist ÷ retreat spaces per N occupants | `plan.isovist_fields` + occupancy ○ | STRONG | field |
| C13 | Setting variety / segment fit | COG | **minimum** fit across occupant types, not average | # distinct setting types; enclosed:open ratio vs task mix; coverage of the high-complexity tail | setting classifier ○ + demand profile | PROMISING | matrix |
| C14 | Focus:collaboration separation | COG | minimum quiet-setting ratio; zones not co-scored | conflict penalty where one zone scores high on *both* demands; enclosed focus seats per M open seats | derived from C1/C7 co-map ○ | STRONG (direction) | penalty field |
| C15 | Active-design movement | SHARED (WB-led) | stairs prominent; amenities a short (not minimized) walk | stair inside entrance isovist & nearer than elevator; mean seat-to-amenity distance | `plan.isovist_fields` + amenity graph ○ | STRONG (stairs) | scalar + field |
| C16 | Territory provision | WB | as task/culture require | % assigned vs hot-desk; desk-sharing ratio; % seats with a personalization surface; home-base per team | plan tags + policy input ○ | PROMISING | scalar |
| C17 | Functioning local control | SHARED | credit **only** vs the binding local stressor | operable controls that target the dominant local stressor (acoustic/visual privacy weighted highest in dense zones) | zone stressor map (from C8/C12) + control inventory ○ | CONTESTED→conditional | per-zone |
| C18 | Air-quality spec | WB | CO₂ well under ~800–1000 ppm; adequate outdoor air; low-VOC | predicted CO₂ at design occupancy; L/s/person; material VOC class — as a **range**, not a cognition promise | ventilation/occupancy model ○ | CONTESTED | per-zone |

### Well-being additions (C19–C24) — new dimensions David flagged, detailed in the well-being synthesis

| # | Criterion | Obj | Direction / threshold | Computed quantity | Engine source | Evid | Output |
|---|---|---|---|---|---|---|---|
| C19 | Restoration / nature contact | WB | more restorative content & retreat within short reach | % seats with nature view (C9-linked) or greenery in isovist; # micro-restorative retreats per N occupants; distance-to-nearest retreat | seat isovist + greenery detector ○; `attributes` palette/greenery ◐ | CONTESTED (ART/SRT real; office effect sizes soft) | per-seat + field |
| C20 | Chronic-stress soundscape | WB | lower sustained arousal; positive soundscape where present | area-weighted sustained sound level (distinct from C7 *intelligibility*); presence of positive soundscape zones | `adapters.acoustics_sim` level model ○ | PROMISING | field |
| C21 | Thermal comfort & zoning | WB | within adaptive-comfort band; per-zone control | predicted PMV/PPD band by zone (façade orientation, glazing load); # thermal zones with control | thermal/solar-gain model ○ | STRONG (top dissatisfier) | per-zone |
| C22 | Sleep/circadian day–night contrast | WB | high daytime melanopic + low evening | C10 daytime score paired with evening-light restraint | daylight model ○ (shares C10) | STRONG | per-seat |
| C23 | Social connectedness / belonging | WB | commensality + belonging, distinct from task collaboration | shared-eating/lounge provision per N; % with a stable home-base/team anchor; loneliness-risk seats (isolated, low co-presence) | commons inventory + co-presence from C1 ○ | PROMISING | scalar + per-seat |
| C24 | Awe / spatial generosity | WB | selective volume where it aids affect (not everywhere) | ceiling-height / volume variation; presence of a generous "release" space against compressed circulation | height field from Tier-C model ○ | PROMISING | field |

**Legend.** Obj: COG cognitive / WB well-being / SHARED both. Engine source: ✓ implemented, ◐ partial or
heuristic present, ○ to build. Evid: STRONG / CONTESTED / PROMISING from `STATE_OF_KNOWLEDGE.md`.

---

## 4. Weighting, aggregation, and the double-counting discipline

**Two weight profiles, one computation.** The engine computes each criterion once, then aggregates twice — once
under a COG profile, once under a WB profile — using the objective tags in §3. A SHARED criterion enters both
sums but with **different weights and different outcome mappings**: C10 daylight is a modest alertness term in the
COG profile and a heavy circadian-health term in the WB profile. The reports are separate; a combined score, if
ever emitted, must show the two components, never a blended scalar that hides which objective is failing.

**Evidence-anchored base weights** (from `STATE_OF_KNOWLEDGE.md` G4 and the weighting note in §2 there):

- **Dominant (weight highest):** acoustic/speech privacy (C7, C8, C20) and thermal (C21) — the largest empirical
  dissatisfiers across ~600 buildings/20 years (CBE). These lead both profiles.
- **Most confidently computable (high weight, high trust):** movement/encounter/legibility (C1–C4) and
  view/circadian equity (C9, C10, C22). Codified or STRONG and directly computable from geometry.
- **Real but caveated (moderate weight, opportunity language):** collaboration proximity/overlap (C5, C6),
  restoration and social connectedness (C19, C23).
- **Conditional / ranged (low weight, tagged):** local control (C17), air quality (C18), awe (C24), territory
  (C16) — scored, surfaced, but never allowed to dominate; their CONTESTED/PROMISING tags cap their pull.

**The double-counting rule.** Because SHARED inputs recur, the aggregator maintains a provenance ledger: each
*physical quantity* (a daylight field, an acoustic field, an isovist) is computed once and referenced by every
criterion that reads it. Two criteria reading the same field are allowed to both score — they map it to different
outcomes — but a report must be able to show that, e.g., "daylight" is behind C9, C10, C19, and C22, so a reader
never mistakes four criteria for four independent pieces of evidence. This is the RULE-0 discipline applied to
scoring: containment of what a number actually rests on, stated explicitly.

**Conflict penalties (the tensions made computable).** From `STATE_OF_KNOWLEDGE.md` §3, the criteria fight, and
the fights are scored as penalties, not averaged away:

- **Openness × enclosure (C1 vs C7/C11/C14).** Where a collaboration zone's r_D contour (C8) reaches a focus
  seat, C1's encounter credit is *reversed* into a C14 penalty at that seat. Zoning is rewarded; uniform
  compromise is penalized.
- **Collision × avoidance (C6).** Path-overlap credit is gated by team interdependence; proximity between
  non-interdependent groups earns nothing (and may earn a crowding penalty via C12).
- **Window as status × health (C9/C10 vs equity).** The scorer rewards the *fraction of seats* meeting the floor,
  not the peak value at the best seat — maximizing perimeter quality for a few is penalized against distribution.
- **Movement benefit × cost (C15 vs C5).** Short paths among interdependent collaborators are rewarded; longer,
  more-visible paths to shared amenities/stairs are also rewarded — the two are reconciled by *whose* path and
  *to what*, not by a single distance term.

**Non-additivity (keystone paper, cross-cutting principle 27).** The dimensions **interact non-additively** — a
thermally neutral room is judged too warm when it is also acoustically stressful (Schweiker et al. 2020). So the
weighted sums above are a *first-order* aggregation, explicitly acknowledged as incomplete: the scorer must carry
known interaction terms rather than pretend the criteria are independent. The seed interactions to model (each to
be fit at L3, not hand-set): acoustic stress **amplifies** thermal and crowding discomfort (C7/C20 × C21/C12);
glare **negates** daylight benefit (glare_risk × C10); and a criterion that is individually acceptable can tip a
seat into failure only in combination. Until these are fit against data, the aggregate score is reported with an
"interactions un-modelled" caveat, and the per-criterion maps — which do not hide behind a sum — are the primary
evidence. A single blended scalar that conceals an interaction is exactly the false precision the paper warns
against.

---

## 5. The top-level deliverable: a fit matrix, not a grade

The scorer's headline output is a **matrix of occupant type × setting type**, each cell a fit score with its
evidence tag and fidelity tier, plus the per-seat and field maps that back it.

**The demand profile is the Q-sort occupant types (keystone paper §5).** The rows of the matrix are not invented;
they are the shared viewpoints a Q-sort/20-sort surfaces among the actual occupants, which the paper reduces to a
canonical three whose needs *conflict by construction*: the **sanctuary** type (wants enclosure, low speech
intelligibility, refuge at the back wall — weights C7/C11/C14 heavily), the **hub** type (wants visibility, buzz,
prospect over the floor — weights C1/C11-prospect/C23), and the **nomad** (indifferent to territory, optimizes
for the nearest free surface — weights C13-variety/C15, discounts C16). A uniform open plan satisfies none; the
whole point of the matrix is that a layout must clear a *minimum* for each type, which is what forces zoning. For
a real project the three are re-derived from that site's Q-sort; absent one, these three are the default demand
profile. A layout is summarized by:

1. its **worst-served segment** under each objective (the binding constraint — §1.2),
2. the **per-objective profile** (COG vector, WB vector) so a space strong for focus-workers' cognition but poor
   for everyone's well-being is visible as exactly that,
3. the **maps** (footfall, integration, r_D contours, daylight/melanopic, crowding) as the evidence a human
   designer reads, and
4. a **provenance panel**: which physical quantities were computed at which fidelity tier, and which criteria are
   PROMISING/CONTESTED and therefore not yet trustworthy.

No single letter grade. The comparison between two layouts is a comparison of matrices and maps, with the weakest
segment and the least-trusted criteria surfaced first.

---

## 6. Validation gate — nothing here is fact until it clears it

Every criterion is a **hypothesis about human outcomes** until validated on the CNfA credibility ladder:

- **L0 analytic** — the metric returns the right value on a synthetic plan with known ground truth (e.g., r_D on
  a shoebox; integration on a canonical space-syntax test case).
- **L1 known-contrast** — the metric orders obvious cases correctly (corridor vs office vs glass box; hard vs
  soft room), the discipline already run on the 16 repo example images.
- **L2 VLM/human judges** — ordinary-language descriptions of the criterion, judged by a checker ≠ author (AG /
  Gemini), Spearman ρ against the metric, pre-registered bands (ρ≥0.6 CONVERGING / 0.3–0.6 WEAK / <0.3 FAILING).
- **L3 behavior/physiology** — the criterion predicts measured outcomes via the experiment platform and,
  eventually, real post-occupancy data, using the paper's methods layer with the **right instrument per
  dimension**: immediate **serial recall** for the acoustic criteria (the task most sensitive to the irrelevant-
  speech effect), **PVT / n-back / Stroop** for attention and working memory, **salivary cortisol, HRV, and EDA**
  (EDA spikes within a second of a glare or noise event the slower measures average away) plus **skin-temperature
  gradient** for the thermal/stress WB criteria, **pointing-error / sketch-map** tasks for wayfinding (C3/C4),
  **Experience Sampling** for the trajectory, and **movement traces / badge co-presence** for the configurational
  substrate (C1–C6).

**A tag the paper insists on: "promising-import."** Some measures (the IAT, adaptive-preference/counterfactual
elicitation, Q-sort) are bedrock in their home disciplines but **scarcely tested in a built-environment setting** —
so a criterion validated *only* by such a measure carries a distinct `promising-import` marker: its POE payoff is a
hypothesis we are helping to establish, not a settled result. This sits beside the STRONG/CONTESTED/PROMISING
evidence tag and further caps how hard the optimizer may push.

A criterion may inform a *ranking* at L1, but it is not trusted as *fact* — and its threshold is not treated as
real — until L2 converges and L3 is at least designed. The WB criteria (C19–C24) especially must reach L3 against
physiological/affective outcomes before any well-being claim is published, because their literature is thinner
(§7) and the temptation to over-claim health ROI is exactly what the synthesis flags (G6).

---

## 7. Boundaries — what this file does not cover

- **The physical-code floor** is in `BASELINE_REQUIREMENTS.md`. It is a gate, not a score; if a layout fails it,
  nothing here applies.
- **The well-being code's evidence base** (the literature behind C19–C24 and the WB re-reading of the SHARED
  criteria) belongs in a parallel synthesis, `WELLBEING_STATE_OF_KNOWLEDGE.md`, the natural companion to
  `STATE_OF_KNOWLEDGE.md`. This file wires the well-being criteria into the scorer; that file will justify them.
- **Engine build-out.** The ○/◐ marks in §3 are the honest state: isovist/space-syntax fields and the acoustic
  RT60 simulation exist in `../cnfa_algs/`; the daylight/melanopic model, the ISO 3382-3 STI/r_D pack, the
  walking-distance and route-overlap graphs, the setting classifier, and the thermal/solar model are specified
  here and not yet built. CRITERIA.md is the contract those builds satisfy.

---

## 8. Verification boundary (RULE 0)

This rubric is derived entirely from `STATE_OF_KNOWLEDGE.md` (whose own verification boundary applies) plus one
design decision taken this session (the COG/WB objective split, at David's prompt). No criterion has yet been run
end-to-end on a real plan through the full scorer; the ✓/◐/○ marks state exactly what is implemented versus
specified. Thresholds quoted (r_D ≤ 5 m, 75% view, 250 melanopic-EDI, STI ≤ 0.50) are the codified/standard
values carried from the synthesis, not re-derived here. The weighting in §4 is *evidence-anchored but not
empirically fitted* — the relative weights are a defensible starting prior from the dissatisfier literature (G4),
to be tuned only against measured outcomes at L3, never hand-set to produce a desired ranking.
