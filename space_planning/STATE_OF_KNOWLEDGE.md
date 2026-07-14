# Office Space Planning — State of Knowledge

*Space-planning workstream, `space_planning/`. Compiled 2026-07-14 (Fable/Claude Opus, from five parallel literature searches). This is the knowledge foundation §3.6 of the Reading Space direction document calls for — the reading that must precede any optimizer. Its job is to say what actually matters in laying out a floor plate, how strong the evidence is, and which findings can be **computed on a plan**. It becomes the basis for `CRITERIA.md` (the scoring rubric) and `BASELINE_REQUIREMENTS.md` (the physical-code floor). Framed against the cognitive code: the physical code sets the admissible; these findings rank within it.*

**How to read the evidence tags.** **STRONG** = well-replicated, safe to build on. **CONTESTED** = real but with debated effect size or boundary conditions. **PROMISING** = plausible, thinly evidenced; use as a candidate, validate before trusting. Every principle carries one, and a verification boundary is stated at the end — several famous numbers are flagged because their own authors warn against over-reading them.

**The one-sentence summary.** Configuration reliably predicts *where people move and co-locate*; it only weakly predicts *whether they interact*, and barely predicts *whether they collaborate* — so a layout scorer should be confident about movement, co-presence, sightlines, daylight, and acoustics, and explicitly humble (probabilistic, organizationally caveated) about interaction and collaboration.

---

## 1. Principles

Grouped by domain. Each: a one-line statement, the mechanism, key citation(s), and an evidence tag.

### A. Configuration, movement, and encounter (space syntax)

**A1. Natural movement — configuration generates movement.** The spatial integration of a space within the whole layout is the primary generator of pedestrian movement; attractors (cafés, printers) amplify but do not cause the base pattern. *Hillier et al. 1993.* **STRONG** (as a law); **CONTESTED** (exact magnitude, which is context-dependent).

**A2. Two metric families for two behaviours.** In the largest workplace dataset (41 offices, 159 floors; Sailer/Koutsolampros), *local* visibility/isovist metrics — connectivity, through-vision, isovist area, visual mean depth — predict **movement** (visual mean depth alone R²≈0.28 per floor; near-monotonic when binned), while *global* **visual integration** and visual entropy predict **co-presence/encounter**. They are empirically distinct jobs. *Koutsolampros & Sailer 2019; Turner et al. 2001.* **STRONG.**

**A3. Movement is confidently predictable; interaction is not.** Configuration predicts where people are, but realized interaction varies by site and is mediated by organizational and cultural factors; the spatial→interaction link is weak (R²≈0.10 per floor). *Rashid, Kampschroer, Wineman & Zimring 2006; Sailer & McCulloh 2012.* **STRONG** (that the link is weak/mediated).

**A4. Intelligibility = learnability of the plan.** The correlation (R²) between a local measure (connectivity) and global integration across all spaces indexes how well what you see locally predicts the whole — high R² = legible, navigable; low R² = disorienting (worked example: Rotterdam whole-city R²=0.14 vs centre 0.44). *Hillier & Hanson 1984.* **STRONG** as a metric; **PROMISING** as a validated predictor of real wayfinding error indoors.

**A5. Functional (path) proximity beats Euclidean distance for collaboration.** Shared daily paths — the overlap of the routes two people walk to common destinations — predict scientific collaboration; +100 ft of path overlap → +15–29% collaboration, while straight-line distance loses significance once path overlap is controlled. *Kabo et al. 2014/2015; Wineman et al. 2014.* **STRONG** (quantified, controlled).

### B. Proximity and communication

**B1. The Allen curve — communication decays steeply with distance.** Probability of regular communication falls off exponentially, to a near-floor by ~25–50 m; and distance depresses **all** media, not just face-to-face (seeing someone in person predicts also phoning/emailing them). *Allen 1977; Allen & Henn 2007.* **STRONG** (classic); the exact decay function is dated to 1970s labs and its persistence in the hybrid era is **CONTESTED**.

**B2. Communication is intensely local; the floor is a hard barrier.** 52% of conversations occur within the same corridor, 87% within the same floor; 83% of collaborations were between same-floor colleagues though those were only 26% of possible pairs; spontaneous talk is even more proximity-bound (91% same-floor) than scheduled. *Kraut, Fish, Root & Chalfonte; Kraut & Cummings 2002.* **STRONG.**

**B3. Functional distance predicts ties.** Whose paths cross — set by doors, stairs, mailboxes, orientation — predicts friendship/tie formation better than metric distance; units off the shared path had less than half the within-group friendships. *Festinger, Schachter & Back 1950.* **STRONG** (mechanism; specific percentages are canonical but flagged unverified-at-source).

### C. Open plan, enclosure, and activity-based working

**C1. Removing walls REDUCES face-to-face interaction.** Objective before/after badge measurement across two Fortune-500 HQs: open-plan conversion cut face-to-face interaction ~70% and raised electronic communication (IM +67%/+75%). Loss of privacy drives withdrawal to digital channels. *Bernstein & Turban 2018.* **STRONG** (rare objective measurement; two firms, quasi-experimental). **This reverses the central justification for open plan.**

**C2. The privacy–communication trade-off is net-negative in open plan.** Across 42,764 respondents / 303 buildings, the interaction benefit of open plan (+0.21 satisfaction) was outweighed by noise (−0.41), sound privacy (−0.20), and visual privacy (−0.46) penalties — net −0.86; enclosed private offices ranked highest on overall satisfaction. *Kim & de Dear 2013.* **STRONG.**

**C3. Intelligible speech, not loudness, corrupts focus.** The irrelevant-speech effect degrades serial recall/working memory in proportion to speech *intelligibility*; people do not fully habituate. *Banbury & Berry 1998; Hongisto 2005.* **STRONG.**

**C4. Open-plan carries health/absence signals.** Short-spell sick leave is elevated in open-plan vs cellular offices (odds ratios ~1.2–1.9, worse for women). *Bodin Danielsson et al. 2014.* **PROMISING/CONTESTED** (observational; job-type self-selection confounds).

**C5. Activity-based working helps satisfaction, not focus or team cohesion.** ABW zoning raised workspace satisfaction (d≈0.84), commensality, and movement, but produced a small productivity decline (d≈−0.28) and reduced own-team cohesion; outcomes depend heavily on whether focus zones are actually protected. *Engelen et al. 2018; Bäcklander & Richter 2022.* **CONTESTED/PROMISING.**

**C6. "Collision"/serendipity design backfires without motivation.** Proximity raises encounter *probability*, but forced co-location without task interdependence or incentive produces active avoidance, not innovation; only individuals already disposed to collaborate formed new ties. *Irving, Ayoko & Ashkanasy 2020.* **CONTESTED** for the pro-collision belief; the avoidance finding is **PROMISING** (rich single case).

### D. Acoustics as a planning constraint

**D1. Performance loss is a sigmoid in speech intelligibility.** Decrease in performance rises steeply across STI≈0.25–0.70 and plateaus at a maximum of ~7% for STI≳0.70; the disruptor is intelligibility, so masking (raising the noise floor to lower STI) works where quieting does not. *Hongisto 2005.* **STRONG** (shape); **CONTESTED** (exact 7% magnitude, task/age dependent).

**D2. ISO 3382-3 gives codified open-plan targets.** Distraction distance r_D (where STI<0.50) ≤ 5 m is good / >10 m poor; spatial decay of speech D2,S ≥ 7 dB good; A-weighted speech level at 4 m ≤ 48 dB good; privacy distance where STI<0.20. *ISO 3382-3:2012/2022.* **STRONG** (standard). r_D is a **contour on the plan** — the single most planning-friendly acoustic number.

**D3. Zone by acoustic district.** A collaboration zone is a speech source with its own r_D contour; that contour must not intrude on a focus-zone seat. Quiet districts target STI<0.50 (→0.20 for confidentiality); masking pulls the contour inward without moving walls. *ISO 3382-3; Hongisto 2005.* **STRONG** (principle); **CONTESTED** (optimal thresholds).

### E. Daylight, view, and biophilia as distributable resources

**E1. Nature-content views aid recovery and cognition.** A nature view vs a blank wall shortened hospital stays (7.96 vs 8.70 days) and reduced analgesia (Ulrich); daylight+view improved working memory and inhibition and cut eyestrain in offices (Jamrozik); and view content matters more than raw daylux for cognition (Heschong/LBL: best view +10–16% acuity/memory, daylight-alone ~0.4%). *Ulrich 1984; Jamrozik et al. 2019; Heschong/LBL.* **STRONG** (view content drives it) / **CONTESTED** (office effect sizes; small N).

**E2. View and perimeter daylight are scarce, spatially-fixed resources to allocate equitably.** Perimeter seats capture them; core seats do not; left to seniority they become a status good rather than an allocated health resource. LEED codifies the equity target: ≥75% of occupied area with a line of sight to qualifying glazing (VLT>40%, within 3× head-height). *LEED v4.1 EQc8; WELL v2.* **STRONG** (codified framing).

**E3. Daytime circadian (melanopic) light is daylight's best-evidenced benefit.** Expert consensus: ≥250 melanopic-EDI lux at the eye (vertical, ~1.2 m) during the day; the metric is inherently per-desk and time-varying, and perimeter daylight is the distributed resource that lets core desks fall short. *Brown et al. 2022; CIE S 026.* **STRONG.**

**E4. Biophilic design is a useful vocabulary, not a source of hard thresholds.** The "14 Patterns" bundle real mechanisms, but office-specific evidence for many individual patterns is thin; the strong components reduce to view content (E1), circadian light (E3), and prospect/refuge (F1). *Browning et al. 2014.* **PROMISING** — do not claim broad "biophilia" productivity ROI.

### F. Environmental psychology of the workstation

**F1. Prospect is strongly preferred; refuge is weak indoors.** People prefer seats with open outlook; the meta-analysis supports prospect in 53% of tests but refuge in only 22% (41% neutral, 41% contrary), and interiors often prefer open rooms to enclosed ones. The preferred seat = outlook in front + protected back, with prospect carrying most of the effect. *Dosen & Ostwald 2016; Appleton 1975.* **STRONG** (prospect) / **CONTESTED** (refuge, weak indoors).

**F2. Crowding ≠ density; control moderates.** Stress arises from density *appraised as* crowding and from loss of control over social contact, not from density per se; layouts that let occupants regulate contact blunt the effect at constant density. *Stokols 1972/1976; Evans.* **STRONG.**

**F3. Territory/personalization supports identity and belonging.** Assigned, markable space is a channel for self-categorization; hot-desking imposes identity threat and workers improvise ownership (same desk daily). Dissatisfaction tracks lost belonging/control, not decoration. *Elsbach 2003; Brunia & Hartjes-Gosselink 2009.* **PROMISING/CONTESTED** (largely qualitative).

**F4. Active-design layouts induce incidental movement.** Prominent, visible stairs near entrances (ahead of elevators) plus point-of-decision prompts reliably raise stair use; amenities sited to require short walks raise daily movement. *NYC Active Design Guidelines.* **STRONG** (stair prominence) / **PROMISING** (whole-layout walkability → wellbeing).

**F5. Plan legibility predicts ease of circulation.** Wayfinding success rises with visual access, architectural differentiation, signage, and simpler floor-plan configuration; navigation load concentrates at decision points, and visible landmarks/goals at junctions reduce error. *Weisman 1981; Passini & Arthur.* **STRONG.**

### G. Heterogeneity, fit, and what actually predicts outcomes

**G1. Occupants are heterogeneous; one plan cannot fit all.** Activity complexity ranges widely (≈23% of workers ≤5 important activities, ≈17% with 16+), and distinct segments — focus/anchor, hub/connector, mobile/nomad — have conflicting spatial needs; a uniform open plan optimizes for none. *Leesman; office-worker segmentation studies.* **PROMISING** (large but proprietary/self-report).

**G2. Fit is task-conditional, not an absolute property of a building.** Vischer's model nests physical, functional (task-support), and psychological comfort; workspace stress is the energy diverted from the task to cope. A space excellent for one task/person can be hostile for another — so the evaluator should emit a per-task-per-type fit matrix, never a single "good building" scalar. *Vischer 2005/2007.* **STRONG** (framework).

**G3. Focus and collaboration have opposite environmental requirements.** Quiet/enclosed/low-interruption vs proximate/visible/interruptible pull in opposite directions; the same open floor serves one and defeats the other — the core reason uniform open plan and poorly-zoned ABW underperform. *Engelen et al. 2022; Bäcklander & Richter 2022.* **STRONG** (direction).

**G4. Acoustics/speech-privacy and thermal are the top empirical dissatisfiers.** Across ~600 buildings / 20 years, the largest dissatisfaction sources are sound/speech privacy (~54%), temperature (~39%), and noise (~34%); acoustic quality has the largest negative impact on self-reported productivity; overall building satisfaction tracks personal-workspace satisfaction. *Graham, Parkinson & Schiavon 2021 (CBE).* **STRONG** — weight these first.

**G5. Personal control helps, but conditionally.** Control widens comfort tolerance and (per Leaman & Bordass) is a "killer variable," but the effect is self-reported and ordinal, and later field work shows control only counts when it targets the binding local stressor — in dense open plan that is usually noise/privacy, not the thermostat. *Leaman & Bordass 1999/2016; Veitch/Newsham COPE 2007–08.* **CONTESTED** (control-as-king) / **STRONG** (the conditionality qualifier).

**G6. IEQ health/cognition economics are real but widely over-quoted.** The famous figures — Fisk's $20–50B/yr national gains, Allen's +101% cognition on "Green+" days — are respectively an explicitly uncertain scoping estimate and an n=24 single-day chamber result with artificially set CO₂; the real-building follow-up found ~26%. Treat ventilation/CO₂/low-VOC as scored specs with ranges, not headline returns. *Fisk 2000; Allen et al. 2016.* **CONTESTED/inflated.**

---

## 2. Criteria — how to judge one layout better than another

A candidate scoring rubric a system can compute over a floor plan. Direction of preference, rough thresholds where the literature gives them, the metric, and the tier of confidence. These become `CRITERIA.md`.

| # | Criterion | Direction / threshold | Computable metric | Evidence |
|---|---|---|---|---|
| C1 | **Encounter potential** | higher in commons, structured | Mean/distribution of **VGA global visual integration**; site social magnets at integration peaks | STRONG |
| C2 | **Movement/footfall surface** | route to high-value collisions | **Visual mean depth, connectivity, through-vision** per cell → footfall map | STRONG |
| C3 | **Plan intelligibility (legibility)** | higher is better | **R² of connectivity vs global integration** across cells (single scalar) | STRONG metric |
| C4 | **Wayfinding load** | fewer decision points; goals visible | Decision-point count on primary routes; % junctions with visible landmark/goal; route directness | STRONG |
| C5 | **Collaborator proximity** | must-collaborate pairs same-floor, ≤ ~30–50 m | % collaborator pairs same floor & corridor; median pairwise walking distance; # cross-floor splits (heavily penalized) | STRONG |
| C6 | **Path-overlap / collision potential** | higher among interdependent teams | Shared route length between desk pairs to common destinations | STRONG |
| C7 | **Speech-privacy in focus zones** | STI ≤ 0.50 (→0.20 confidential) | Per-seat STI; **no collaboration r_D contour crosses a focus seat** | STRONG |
| C8 | **Distraction distance (open plan)** | r_D ≤ 5 m; D2,S ≥ 7 dB; L_p,A,S,4m ≤ 48 dB | ISO 3382-3 metrics on the plan | STRONG |
| C9 | **View equity** | ≥ 75% of seats with qualifying nature-content view | % seats with line of sight to glazing (VLT>40%, within 3× head-height); view-content class | STRONG (codified) |
| C10 | **Circadian light equity** | % desks ≥ 250 melanopic-EDI for ≥ X daytime hrs | Per-desk melanopic-EDI across the day; distance-to-window | STRONG |
| C11 | **Prospect–refuge seat quality** | prospect-led; back-to-wall bonus | % seats with large forward isovist/window view AND protected back within ~1.5 m (weight prospect > refuge) | STRONG (prospect) |
| C12 | **Perceived-crowding risk** | lower | local density × visible co-workers in isovist ÷ retreat-spaces per N occupants | STRONG |
| C13 | **Setting variety / segment fit** | min-fit across occupant types, not average | # distinct setting types; enclosed:open ratio vs task mix; coverage of high-complexity tail | PROMISING |
| C14 | **Focus:collaboration separation** | minimum quiet-setting ratio; zones not co-scored | conflict penalty where a zone scores high on both demands; enclosed focus seats per M open seats | STRONG (direction) |
| C15 | **Active-design movement** | stairs prominent; amenities a short walk | stair within entrance isovist & nearer than elevator; mean seat-to-amenity distance (non-minimized) | STRONG (stairs) |
| C16 | **Territory provision** | as task/culture require | % assigned vs hot-desk; desk-sharing ratio; % seats with personalization surface; home-base per team | PROMISING |
| C17 | **Functioning local control** | credit only vs the binding stressor | operable controls that target the dominant local stressor (acoustic/visual privacy weighted highest in dense zones) | CONTESTED→conditional |
| C18 | **Air-quality spec** | CO₂ well under ~800–1000 ppm; adequate outdoor air; low-VOC | predicted CO₂ at design occupancy; L/s/person; material VOC class (as a *range*, not a cognition promise) | CONTESTED |

**Weighting guidance from the evidence.** The strongest single empirical predictors of occupant outcomes are **acoustic/speech privacy and thermal zoning** (G4), so C7/C8 and thermal should dominate the objective; **movement/encounter and legibility** (C1–C4) are the most confidently computable; **view/daylight equity** (C9–C10) are codified and equitable-by-design; **collaboration criteria** (C5–C6) are real but should be reported as *opportunity* estimates, organizationally caveated; and **setting-variety/segment fit** (C13) should be scored as *minimum fit across occupant types*, explicitly penalizing monoculture plans.

---

## 3. Tensions and contingencies

The criteria conflict, and the conflicts are the substance of the problem — an optimizer that ignores them will produce a plan that is good on average and hostile to everyone in particular.

**Openness vs enclosure (the master tension).** Encounter, movement, integration, and collaboration (C1–C6) pull toward openness and proximity; speech privacy, focus, crowding-control, and refuge (C7, C11, C12, C14) pull toward enclosure and separation. The evidence does not favour one pole — it favours *zoning*: distinct districts each optimized for one mode, with acoustic buffers (r_D contours) keeping them apart, rather than a uniform compromise that satisfies neither (C1 reverses under C7 when a collaboration contour reaches a focus seat). This is why the single most robust finding — open-plan cut face-to-face interaction ~70% (C1/C1-reverse) — is best read not as "enclosure is better" but as "unzoned uniformity is worse than either pole."

**Collision vs avoidance.** Proximity raises encounter probability (B1, A5), but forced proximity without task interdependence produces avoidance, not serendipity (C6). Contingency: co-locate only pairs/teams with a shared deliverable; the metric must gate collision potential by interdependence, or it optimizes for the wrong thing.

**The window as status vs health resource.** View/daylight (C9–C10) are scarce and spatially fixed; maximizing quality for a favoured few (seniority at the perimeter) conflicts with the equity target of a floor for *all* seats. The evidence and the codes both favour distribution — maximize the fraction of seats meeting a floor, not the peak.

**Control is conditional (C17).** A flat "personal control" bonus is not supported; control only helps where it addresses the binding local stressor. In dense open plan that is acoustics/privacy, not temperature — so the same control feature is worth different amounts in different zones.

**Task-type and individual differences (the deepest contingency).** Every criterion's weight depends on the occupant's task and type (G1–G3): deep-focus and collaborative work have opposite requirements, and worker segments (sanctuary/hub/nomad) conflict. The correct objective is therefore not a single ideal but a *fit matrix* — per-task, per-type — with the layout required to clear a minimum for each segment rather than maximize the average. A plan that is excellent on average can fail the focus-dependent quartile entirely.

**Movement is a benefit and a cost.** Active design deliberately *lengthens* some paths to induce walking (C15), while collaboration criteria *shorten* paths to induce encounter (C5–C6); these are reconciled by direction — short paths among interdependent collaborators, longer/more-visible paths to shared amenities and stairs for everyone.

---

## 4. Open questions / what is not settled

Several things the optimizer will need are genuinely unresolved, and should be carried as explicit uncertainty, not papered over.

The **magnitude** of configuration→movement effects is context-dependent (office single-metric R²≈0.28 per floor, near-1.0 only when binned), and urban normalization formulas underperform on floor plates — so movement predictions are directional, not precise. Whether the **Allen decay** still holds in hybrid/remote-saturated work is actively debated; the ~50 m figure may be softening. The **causal** step from co-presence to interaction to collaboration is weak and organizationally mediated — spatial variables set opportunity, not outcome, and no model reliably predicts realized collaboration from geometry alone. **ABW and open-plan** outcomes hinge on implementation fidelity (whether focus zones are actually protected) more than on the concept, which the geometry cannot fully capture. The **office effect sizes** for daylight/view cognition rest on small-N studies; the robust claim is directional (view content > daylux) not quantitative. **Refuge indoors** is weakly and inconsistently supported, so its weight is uncertain. And the **IEQ economics** (Fisk, Allen) are order-of-magnitude scoping estimates whose achievable fraction is the real unknown — usable as sensitivity envelopes, not point returns. Finally, almost the entire literature is **cross-sectional and self-report**; the field lacks the longitudinal, behaviorally-and-physiologically-measured validation that the cognitive-code programme (and the experiment platform) is positioned to supply — which is precisely why validation must gate any criterion before it is trusted as fact.

---

## 5. References (deduplicated)

Allen, T. J. (1977). *Managing the Flow of Technology.* MIT Press. — and Allen, T. J., & Henn, G. (2007). *The Organization and Architecture of Innovation.* Elsevier.
Appleton, J. (1975). *The Experience of Landscape.* Wiley.
Bäcklander, G., & Richter, A. (2022). Task–environment fit in activity-based working. *Environment and Behavior.*
Banbury, S., & Berry, D. C. (1998). Disruption of office-related tasks by speech and office noise. *British Journal of Psychology, 89*(3).
Bernstein, E. S., & Turban, S. (2018). The impact of the "open" workspace on human collaboration. *Philosophical Transactions of the Royal Society B, 373,* 20170239.
Bodin Danielsson, C., et al. (2014). Office design's association with sick leave. *Ergonomics.*
Brown, T. M., et al. (2022). Recommendations for daytime, evening, and nighttime indoor light exposure. *PLOS Biology, 20*(3), e3001571. (with CIE S 026:2018.)
Browning, W., Ryan, C., & Clancy, J. (2014). *14 Patterns of Biophilic Design.* Terrapin Bright Green.
Brunia, S., & Hartjes-Gosselink, A. (2009). Personalization in non-territorial offices. *Journal of Corporate Real Estate, 11*(3).
Dosen, A. S., & Ostwald, M. J. (2016). Evidence for prospect-refuge theory: a meta-analysis. *City, Territory and Architecture, 3,* 4.
Elsbach, K. D. (2003). Relating physical environment to self-categorizations. *Administrative Science Quarterly, 48*(4).
Engelen, L., et al. (2018/2022). Activity-based working: health, behaviour, and the "productivity tax." *Building & Environment / Management Review Quarterly.*
Evans, G. W. (and Lepore). Residential density, control, and social withdrawal.
Festinger, L., Schachter, S., & Back, K. (1950). *Social Pressures in Informal Groups.* Harper.
Fisk, W. J. (2000). Health and productivity gains from better indoor environments. *Annual Review of Energy and the Environment, 25.*
Graham, L. T., Parkinson, T., & Schiavon, S. (2021). Lessons learned from 20 years of CBE occupant surveys. *Buildings & Cities.*
Hartig, T., Mitchell, R., de Vries, S., & Frumkin, H. (2014). Nature and health. *Annual Review of Public Health, 35.*
Hillier, B., & Hanson, J. (1984). *The Social Logic of Space.* Cambridge Univ. Press. — and Hillier, B., Penn, A., Hanson, J., Grajewski, T., & Xu, J. (1993). Natural movement. *Environment and Planning B, 20*(1).
Hongisto, V. (2005). A model predicting the effect of speech of varying intelligibility on work performance. *International Journal of Industrial Ergonomics* / *Indoor Air.*
ISO 3382-3:2012/2022. Acoustics — room acoustic parameters — Part 3: Open-plan offices.
Irving, G. L., Ayoko, O. B., & Ashkanasy, N. M. (2020). Collaboration, physical proximity and serendipitous encounters. *Organization Studies.*
Jamrozik, A., et al. (2019). Access to daylight and view improves cognition and reduces eyestrain. *Building and Environment, 165,* 106379.
Kabo, F., et al. (2014/2015). Shared paths to the lab. *Environment and Behavior, 47*(1). — with Wineman, J., et al. (2014). Spatial layout, social structure, and innovation. *Environment and Planning B, 41*(6).
Kim, J., & de Dear, R. (2013). Workspace satisfaction: the privacy–communication trade-off in open-plan offices. *Journal of Environmental Psychology, 36.*
Kraut, R. E., Fish, R. S., Root, R. W., & Chalfonte, B. L. (1990). Informal communication in organizations. — and Kraut, R. E., & Cummings, J. (2002). Proximity and distance in work groups. In *Distributed Work.*
Leaman, A., & Bordass, B. (1999). Productivity in buildings: the "killer" variables. *Building Research & Information, 27*(1); "Twenty Years On" (2016).
Leesman (2017–2019). The complexity equation; workplace alignment. (Industry data.)
LEED v4.1 EQ credit "Quality Views"; WELL v2 (Light/Mind).
Allen, J. G., MacNaughton, P., Satish, U., et al. (2016). Cognitive function scores, CO₂, ventilation, VOCs (COGfx). *Environmental Health Perspectives, 124*(6).
Rashid, M., Kampschroer, K., Wineman, J., & Zimring, C. (2006). Spatial layout and face-to-face interaction in offices. *Environment and Planning B, 33*(6).
Sailer, K., & McCulloh, I. (2012). Social networks and spatial configuration. *Social Networks, 34*(1). — and Koutsolampros, P., Sailer, K., et al. (2019). Dissecting Visibility Graph Analysis. *SSS12.*
Stokols, D. (1972). On the distinction between density and crowding. *Psychological Review;* (1976) *Environment and Behavior, 8.*
Turner, A., Doxa, M., O'Sullivan, D., & Penn, A. (2001). From isovists to visibility graphs. *Environment and Planning B, 28*(1).
Ulrich, R. S. (1984). View through a window may influence recovery from surgery. *Science, 224.*
Veitch, J. A., Charles, K. E., Farley, K. M. J., & Newsham, G. R. (2007). A model of satisfaction with open-plan office conditions (COPE). *Journal of Environmental Psychology.*
Vischer, J. C. (2005/2007). Environmental psychology of workspace; workspace stress. *Stress and Health, 23*(3).
Weisman, J. (1981). Evaluating architectural legibility: way-finding. *Environment and Behavior, 13*(2). — with Passini, R., & Arthur, P. (wayfinding as spatial problem-solving).

---

## 6. Verification boundary (RULE 0)

This synthesis is drawn from five parallel literature searches on 2026-07-14. Full text was obtained for: the Dissecting-VGA dataset R² values, Kabo path-overlap effect sizes, Kraut locality percentages, Kim & de Dear satisfaction figures, Dosen & Ostwald prospect/refuge percentages, ISO 3382-3 targets, LEED EQc8 thresholds, Brown et al. melanopic numbers, Ulrich statistics, Jamrozik results, Engelen ABW effect sizes, Vischer's model, the CBE 20-year synthesis, and the Leaman & Bordass 2016 update. Reported at abstract/secondary level (verify against primary before publication): Bernstein & Turban exact IM figures, Banbury & Berry decrement magnitude, Festinger's exact percentages, the space-syntax movement meta-analysis pooled coefficient, Hillier 1993 and Turner 2001 originals, Elsbach 2003, and the Allen/Fisk/Allen-COGfx figures (the last flagged as inflated by their own authors). The **direction** of every principle above is well supported; several **magnitudes** are context-dependent and tagged accordingly. No criterion here should be trusted as fact in the optimizer until the cognitive-code validation programme confirms it against measured human outcomes.
