# Image_Tagger / CNfA — Program State & Direction

*2026-08-01, cowork · **v1 — direction locked with David's 08-01 calls (§7).** A take-stock synthesis of where
we are and where we are going. It supersedes the
master-status chain (`MASTER_STATUS_ALL_PROJECTS_2026-07-14/15/20`) for the tagger workstream by folding in
the post-07-20 work those rollups predate — the POE pilot, the entrance/foyer demonstrator, the user-tailored
QA architecture, the activity/space-use and 3D threads, and this session's theory/knowledge layer. It absorbs
and replaces this morning's `STATUS_AND_SPRINT_PLAN_2026-08-01` (rev 1–2), which was written before the
post-07-20 evidence was in. Every state claim is graded and sourced; where something runs in parallel and is
not yet integrated, it says so.*

**Honesty tags used below:** `[OPERATIONAL]` runs and is used · `[PARALLEL]` built and working but not yet
integrated into the canonical path · `[FOUNDATIONAL]` theory/taxonomy in place, predicates not yet built ·
`[DESIGN]` specified on paper, not built · `[WIRED]` scoreable through the socket, not yet validated against
outcomes.

---

## 1. The vision (unchanged — everything serves it)
Move architecture evaluation from the **physical code** (lux, dBA, °C, CO₂, m²/person — certifies the
container) to a **cognitive code** ("can people think, find their way, concentrate, connect?") and a co-equal
**well-being code** ("does the space reduce stress and support health over the day?"). Both read the *same*
computed attribute engine. The destination (POE paper §6): turn each construct into a **design-time criterion**
checkable on a model on screen and back-propagated into parametric tools (Rhino/Grasshopper, Revit) — the Zaha
Hadid direction. The organizing lens is the **register model** (metric, morphological, luminous, tectonic,
perceptual, affective, affordance, configurational, semantic, evaluative, comparative); critique is a
cross-register act. Strategy: **engine-first**, climb primitives → perceptual/tectonic → cognitive constructs,
**validating at every rung** against a VLM and human judges. Current statement of vision:
`docs/VISION_AND_DIRECTION_2026-07-30.md` ("Reading Space as Cognitive Code").

## 2. Where we are — by layer
### 2.1 The CNFA engine + annotation socket — the biggest advance `[OPERATIONAL, but PARALLEL to the app]`
`cnfa_algs/` + `annotation_socket/` run **~68 predicates** (≈40 image attributes + 28 plan-derived metrics),
spanning primitive, perceptual/tectonic, and configurational registers, with C1–C24 built. Honest by
construction: the **M1′ audit spine** (method-replay; tampering/fabrication → RED; abstain-with-evidence),
**tiered GREEN/AMBER/RED** (most predicates honestly AMBER), **faithful feature computation** (Rosenholtz
FC/SE adjudicated to ~1e-7; 11-class complexity partition), and a clean **PlanGrid** seam to geometry.
Run evidence: 3–8 real interiors annotated end-to-end under the controller, a fabricated control rejected,
idempotent replay. **Key caveat:** the engine runs *parallel to* the production web pipeline — it is **not yet
the canonical science-run** inside the app; that integration (`backend/science/pipeline.py`) is named, open
work. Socket suite: 33 pass / 4 fail, the 4 a hard-coded Linux fixture path (not a logic defect).

### 2.2 The web application `[OPERATIONAL]`
The mature 2D product (`Image_Tagger_3.4.74_vlm_lab_TL_runbook_full`, React/FastAPI): ingests images, runs the
tagging pipeline, serves results. This is the working surface students and the pilot use.

### 2.3 The controller / socket trust layer `[OPERATIONAL; certification PENDING]`
The vision pipeline is a **conformant socket under the night-nurse CONTROLLER** (`_control/`): pull-driven,
content-addressed, independent mechanical gate (replay / evidence / anti-fabrication / abstention / coverage),
I7 "no-self-authorization" — a score exists only if mechanically derived with evidence. It shares **one UNKNOWN
sentinel / one overseer rule** with the AE extraction pipeline. Open: the socket sits **AMBER pending a ≠-mind
certification run**, and the checker is role-separated but not yet process-separated.

### 2.4 The well-being code `[WIRED; validation OWED]`
Runs over the same engine (operators tagged SHARED/WB). ~10 C-operators (C10/C16/C17/C18/C19/C21/C22/C23…) are
`+WIRED` through the socket's `input_values` channel and scored on a demo unit; C18 air is the strongest
money-backed lever (Fisk 2000). The masking diagnostic — a space that *reports* well while reverberation / low
melanopic dose / poor air still load physiology — is the validation path. Several operators remain SPEC+PLAN or
NEEDS PLAN (vegetation/material/water masks await the Wave-3 detector; melanopic-at-eye and the stress-
physiology hooks unbuilt).

### 2.5 The VIEW ladder `[VIEW-3 OPERATIONAL; study-contract DESIGN]`
VIEW-0..3 turn engine output into readable, layered views. **VIEW-3** (the question-driven composer) is **built
and passing** its acceptance test ("effects of street noise on the foyer"): question → classify → compose →
self-contained HTML, **advisory-only, ≠-mind-separated** (the LLM curates layers/prose, never computes/alters
scores; unverified numbers render `[redacted:unverified]`). The broader **user-tailored QA architecture** +
**Question-to-Test Contract** (turn a question into a doable study with a falsifier) is **specified 07-29, not
built** — its first branch is the 3D workbench.

### 2.6 Activity / space-use `[FOUNDATIONAL]`
A 24-activity vocabulary + attribute-profile matcher + a disciplined mining brief (activity episode → required
person-object-space relations → visually recoverable evidence → attribute → testable prediction), with **21
candidate relational attributes** and **8 first priorities**. Rules: don't infer behaviour from affordance;
declared inputs ≠ visible evidence; a proxy is never an outcome. Theory + taxonomy in place; predicates not yet
implemented.

### 2.7 The 3D thread — now anchored to ZHA models `[DESIGN → PRIORITIZED]`
Apply the same cognitive-code reading to 3D models. **Direction set 08-01 (David): we will get the 3D models
from ZHA**, which changes this from a research thread to a real intake requirement. Three things follow, and
they are the work:
1. **Plan extraction is easier than from 2D, not harder.** A 3D/BIM model gives the floor dimensions and the
   plan directly — no inferring `PlanGrid` from a photograph. This should *strengthen* every plan-derived
   metric (isovists, VGA, movement, seating, crowding, view-equity) because the geometry is exact.
2. **We must extract multiple occupant viewpoints ourselves.** The 3D model is not one image; we render views
   from occupant positions and eye-heights (entrance approach, seated, standing, along circulation) and run the
   perceptual/tectonic/affective reading *per viewpoint* — the space read as a set of lived perspectives, not a
   single frame.
3. **We must match materials to regions ourselves.** ZHA may hand us a materials *list*, but a list is not a
   map; we still have to bind each material name to the *locations/regions* where it occurs (surface/region →
   material-name assignment). That binding is the 3D-native feed into the materials branch (the encyclopedia +
   the material gate + CC-5b), replacing image-segmentation guesses with model-truth where the model provides
   it. We already hold Structured3D annotations as a stand-in until ZHA models arrive.

### 2.8 The correctness + supply-chain infrastructure `[INFRASTRUCTURE in place; calibration OWED]`
The **L6 correctness program** (panel reviews; M1′ expanded to 28-of-68 predicates; CC-1..CC-4 cycles) and the
**DK-1 corpus + labeling supply chain** (collectors, A/B collection, the Google-Drive offload path, the S3
labeling console, Tanishq onboarding) — the human-calibration layer the founding doc called a *need* now has
real infrastructure. What's owed: the PNG corpus export (DK-1) → the L6 replay → human/biosignal calibration.

### 2.9 This session's additions — the theory/knowledge/validation layer
Not a separate project; these feed specific operators above. The **perceived-complexity manuscript** (theory
under the clutter/partition/FC work); the **materials encyclopedia** (feeds V12 natural-material, the material
gate, CC-5b); the **social-presence/occupancy base** (feeds C23 connectedness, C16 territory, C12 density); the
**review-pack viewer + human-review protocol + HITL/occupancy specs**; the **image-DB acquisition plan +
`Image_Collections` + phase-scramble/Mooney generators**.

## 3. Integration — the corrected, evidence-based picture
### 3.1 POE — the tagger is the design-time arm of a concrete, staffed pilot
This is the correction that matters. Post-07-20 we specified a **unified Cognitive + Wellness + Physiology POE
pilot** (`docs/POE_HomePilot_and_ZHA_GamePlan_shareable_2026-07-21.md`,
`docs/POE_Pilot_Kit_Protocol_Instruments_IRB_ZHA_2026-07-21.md`): a **two-phase design** (classical POE Phase 0,
then the same 4–6 campus spaces redone with the unified code, Phase 1), a full **instrument kit** (STIPA/RT60,
spectral m-EDI/DGP/flicker, MRT/thermal, CO₂/VOC/PM₂.₅, HRV/EDA + salivary cortisol, PVT/n-back/Stroop, ESM,
PRS/valence-arousal, the 2AFC labeling console), a **one-page IRB outline**, and a **ZHA first-meeting agenda**.
It runs as **two clean tracks**: the **academic track** (David's lab — pilot, instruments, human subjects,
publications) *validates and de-risks*; the **collaboration track** (ZHA) puts the validated method on real
projects. Crucially, **Phase 1 calibrates the tagger's design-time proxies against measured post-occupancy
outcomes** — *that calibration is the construct-validation path and the proof of the "code" claim.* It is
**staffed**: Stephan (acoustic, light, thermal, physiology/IRB, cognition, affect), Tanishq (air, dosimetry,
glare capture, cognitive-battery build, behaviour/ESM). **Status: fully specified, not yet run.** *(Note: the
dataset/collection roles I set up for Stephan and Tanishq this session are one slice of these larger pilot
roles.)*

### 3.2 The Knowledge Atlas (AE) — the literature-grounding layer, conceptually central
The unified method is explicitly *grounded in the research literature (the Knowledge Atlas)* for evidence and
*read off renders by the Image Tagger* for design time — "the same construct measurable at design time and
post-occupancy, which is the whole point of a code." **This session's encyclopedias (materials, social
presence) are exactly Knowledge-Atlas content.** So the conceptual integration is central. **What's missing is
the mechanical pipe:** the tagger does not yet auto-query ATLAS for its citations, and the encyclopedias are
ATLAS-shaped but not in ATLAS.

### 3.3 The night-nurse controller (AE governance) — wired at the trust layer, insulated operationally
As §2.3: the tagger and AE extraction are both sockets under one controller sharing the CPP, I7, and one trust
vocabulary — **mechanically integrated for governance**, **operationally insulated** (separate stage dirs; the
tagger doesn't need AE's extraction healthy). This is why we can proceed through the AE-pipeline repair.

### 3.4 The experiment platform (physiology) — the pilot's Phase-1 layer; designed + staffed, not run
The physiology/biosignal validation I earlier called "the big unbuilt gap" is precisely the **POE pilot's
Phase-1 physiology layer** (HRV/EDA/cortisol + the cognitive battery, under IRB, Stephan/Tanishq). So it is
designed, staffed, and IRB-scoped — what's owed is *running* it, plus the L6 corpus that ties the design-time
proxies to the measured outcomes.

### 3.5 The entrance/foyer demonstrator — predictions first, then HITL `[ACTIVE — the #1 near-term focus]`
`docs/CLAUDE_ENTRANCE_FOYER_TAGGER_ASSIGNMENT_2026-07-30.md`: a small, trustworthy, exportable Image_Tagger
attribute bundle; Codex builds the recommendation schema/adapter. **Direction set 08-01 (David): the foyer is
NOT empirical at first — it is a set of engine *predictions* about how the entrance/foyer will read and behave.
The biggest near-term focus is running those predictions past *human judgments in a HITL manner* (do people
agree with the engine's read of this foyer?), which comes before any instrumented measurement. Some simple
local measures may come alongside, but they are secondary.** So the demonstrator's first proof is
prediction → HITL-on-human-judgment, not physiology. This is the near-term ZHA-facing showcase and leads the
plan.

### 3.6 The construct-ontology mapping — the formal POE link, currently gated
The formal predicate → construct mapping is onto the multi-level typed graph in `_control/status/`
(is-a / is-realized-by / causes / measured-by), with a hard rule: a CNfA predicate is **is-realized-by** its
computation or contributes a **causes** edge, **never** a flat is-a. **Gated:** the node taxonomy is not
stabilized (~1-in-5 constructs don't cleanly place; 0.1833 forced-placement), `measured-by` untested, verdict
not version-controlled, fleet on HOLD pending David's scaffold sign-off (TX-3).

### 3.7 The epistemics of validation — why POE can still challenge the engine (David, 08-01)
*(BN / EN are David's constructs — the belief network and the entrenched network the engine is the source of;
kept verbatim, not redefined here.)*

**The circularity, stated plainly.** The CNFA engine's measures are *theory-laden*: an STI reading "means"
degraded comprehension only because we accept the speech-intelligibility science and have entrenched it in the
EN. We then use that measure in an applied way to make space-planning recommendations. But **our POE tests are
themselves based on the engine.** So a POE cannot be a clean test of the science it presupposes — that would be
circular. Testing whether the STI *instrument itself* conforms to a human sample is a distinct act that must be
**declared explicitly and run outside the normal course of business**, precisely because you cannot presuppose
a measure's meaning and test it in the same breath.

**The resolution (Quinean, and it is a design requirement, not just a caveat).** No measurement is
theory-neutral; you never test "the science" from nowhere. But the web of belief still faces experience *as a
whole*, and POE observations are that tribunal for our applied web. We therefore build in three things:

1. **Two explicitly separated registers.** (a) *Applied / normal-business*: engine measures presupposed, used
   to generate predictions and recommendations. (b) *Instrument-conformance* (declared, out-of-band): we
   deliberately test one named instrument against a human sample. The engine must know which register it is in
   and never silently blur them.
2. **POE as observational data — fixed-IV, measured-DV.** We do not manipulate to isolate causes; we **fix the
   environmental configuration (the IV, as read/held by the engine) and measure the human response (the DV)**.
   This is observational, not experimental — and still informative: it (i) confirms or disconfirms the engine's
   *directional* predictions in the wild, (ii) surfaces context/interaction effects the science's
   ceteris-paribus claims omit, and (iii) yields real-world effect sizes that **calibrate** the design-time
   proxies (the tagger-proxy → measured-outcome curve). POE thus accumulates its **own** claims — observational,
   not experimental — that stand alongside the entrenched science.
3. **The challenge ledger (the key new artifact to build).** Every POE run emits observations. Where an
   observation diverges from the engine's entrenched prediction beyond a stated tolerance, log a first-class
   **CHALLENGE record**: `{prediction, observation, magnitude, space/context, provenance, entrenchment-of-the-
   challenged-belief}`. A challenge is **not** an experimental refutation and does not auto-revise the engine;
   it is an accumulating observational claim. The failure mode this exists to prevent is the entrenched engine
   *explaining away its own anomalies*. **Entrenchment-aware routing:** each engine belief carries its
   entrenchment (how load-bearing, how much converging science — the same firm/framework/contested grading).
   Revise at the periphery first; but when challenges *concentrate* on a node — especially a strongly-entrenched
   one — that concentration is the trigger to spend the expensive, out-of-band **instrument-conformance test**
   (register (a) → register (b)). The ledger is what routes scarce controlled-testing effort to where the web is
   under the most observational strain.

**So:** canonicalize the engine (it is the entrenched source of the BN/EN and of our recommendations) — *and*
build the challenge ledger + register separation, so a contradiction between a CNFA prediction and a POE
observation is *registered as data*, never absorbed. The existing **masking diagnostic** (a space that reports
well while physiology still loads) is one instance of exactly this mechanism; the ledger generalizes it.

## 4. What is strong, what is less strong
**Strong.** (1) The validation rigour — M1′ method-replay, "provenance or the score does not exist" (I7), an
independent gate that makes fabricated scores structurally impossible, faithful reference ports to ~1e-7, and
survival of multiple adversarial attack cycles plus a 9-reviewer ruthless panel. (2) The dual cognitive/well-
being read over one engine. (3) A **concrete, instrument-backed, IRB-bound, two-track POE pilot with a ZHA
path** — the validation *and* commercialization route is planned and staffed, not vapor. (4) VIEW-3 shipped
with a disciplined ≠-mind separation that runs system-wide. (5) The space-planning killer-app corpus is
complete and runnable through the socket. (6) One honesty vocabulary across the whole system.

**Less strong / the real gaps, in rough order.** (1) **The engine runs parallel to the production app** — not
yet the canonical science-run; this is the first integration to close. (2) **No construct validation against
human/biosignal data yet** — owed; it requires the PNG corpus (DK-1) → L6 replay → the POE pilot actually
running. (3) **The socket is not ≠-mind-certified** (AMBER; checker not process-separated). (4) **Open panel
items** cap trust in the geometry chain (Tier-B glass-house inversion; C11/C13 construct validity; the
C10/C22 provenance ledger). (5) **The construct taxonomy is unstable**, blocking the formal POE/ontology
mapping. (6) **Activity/space-use, the 3D thread, and the Q&A→study contract are foundational/design, not
built.** (7) **The ATLAS mechanical pipe is absent**, and the knowledge encyclopedias are seeds
(RAG-gated). (8) **Data isn't in** (priority datasets unacquired). (9) **The challenge ledger + register separation (§3.7)
are not yet built** — today a POE observation that contradicts a CNFA prediction has nowhere first-class to
land, which is the exact risk the ledger removes.

## 5. Where we are going — priorities and a sprint set
### 5.1 Priorities (reordered per David's 08-01 direction · P0 unblocks · P1 sprint-critical · P2 valuable)
1. **(P0 — the #1 near-term focus) Entrance/foyer: predictions → HITL on human judgments.** Produce the
   engine's predictions for an entrance/foyer, export the trustworthy attribute bundle to Codex's
   recommendation schema, and **run those predictions past human judges (HITL)** — do people agree with the
   engine's read? Simple local measures may ride along but are secondary. *Why:* David's chosen lead ZHA proof,
   and it is achievable now without instruments. **cowork/Claude + Codex + David (HITL).**
2. **(P0) DK-1 PNG corpus export → Codex Phase-1 `corpus_L6` replay.** The named validation gate (FC/SE + the
   partition are AMBER "pending L6"; all construct validation is owed against it). **David → Codex.**
3. **(P0/P1) Canonicalize the CNFA engine as the app's science-run — AND build the challenge ledger + register
   separation (§3.7).** Make the engine the canonical `backend/science/pipeline.py` path (retire the parallel
   one) *and* add the §3.7 machinery so a CNFA-prediction-vs-POE-observation contradiction is registered as
   data, never absorbed, with the applied vs instrument-conformance registers kept distinct. *Why:* the engine
   is the entrenched source of the BN/EN and our recommendations, so it must be canonical — but canonicalizing
   an entrenched view without a way to record its anomalies is the trap §3.7 removes. **Codex/Fable.**
4. **(P1) 3D-from-ZHA intake path.** Build the model-intake: exact plan extraction (easier than 2D),
   multi-occupant-viewpoint rendering, and material-name→region binding (the 3D-native feed to the materials
   branch). Develop against Structured3D now; wire to ZHA models when they arrive. **Fable/Codex + cowork
   (materials).**
5. **(P1) Human review of the lead constructs** via the viewer (surface_density / arrangement_disorder /
   textural_discomfort + the WB gates). First real ground truth; also seeds the challenge ledger. **David +
   Stephan.**
6. **(P1) ≠-mind certification run of the socket.** The credibility unlock. **Codex/AG + David.**
7. **(P1) Acquire priority datasets** (ADE20K, SUN Attributes, MINC-2500, OpenSurfaces) + **build the
   purpose-built sets** (facet-isolation, Mooney, occupancy series). **Stephan + Tanishq (scripts ready).**
8. **(P1) Wave-3 detector wiring** (CC-5 SegFormer / CC-5b MINC material head) — AMBER veg/material/water gates
   → real masks; feeds the materials branch. **Codex/Fable (needs #7's MINC).**
9. **(P1/P2) Stand up the POE pilot — the observational engine.** IRB, instruments, Phase 0 (classical) → Phase
   1 (unified) on 4–6 campus spaces. This is the **fixed-IV / measured-DV** data engine (§3.7): it feeds the
   challenge ledger and the proxy→outcome calibration curves. Follows the foyer-HITL work, not before it.
   **David + Stephan + Tanishq.**
10. **(P2) Clear the open panel items** (Tier-B geometry, C11/C13, provenance ledger). **Codex/Fable + PANEL.**
11. **(P2) Enable RAG connectors + elaborate the encyclopedias** (PubMed/Scite/Elicit). **David enables; cowork.**
12. **(P2, gated) Predicate → construct-ontology mapping** via is-realized-by/causes — **only after TX-3.**
    **cowork + David.**
13. **(P2/P3) Finish the manuscript**; build out the activity/space-use predicates as their own track. **cowork
    / Fable.**

### 5.2 Provisional sprints (parallelized; entrance/foyer HITL leads)
1. **Sprint A — FOYER HITL (lead).** Engine predictions for an entrance/foyer → export the attribute bundle to
   Codex's recommendation schema → **HITL study of the predictions against human judgment**. *Exit:* a
   ZHA-facing foyer demo whose predictions have been human-checked; the first HITL agreement/disagreement data.
2. **Sprint B — CORPUS, CANONICALIZE & CHALLENGE-LEDGER (parallel).** DK-1 PNG export → Phase-1 replay → make
   the CNFA engine the app's science-run + **build the challenge ledger + register separation (§3.7)** + fix the
   4 fixture failures → ≠-mind certification. *Exit:* one canonical pipeline that can register challenges; L6
   replayed; socket off AMBER.
3. **Sprint C — 3D INTAKE (parallel, ZHA-facing).** Build the ZHA-model intake — plan extraction,
   multi-viewpoint rendering, material-region binding — against Structured3D now, ZHA models when they land.
   *Exit:* the cognitive-code reading runs on a 3D model with per-viewpoint outputs + material regions.
4. **Sprint D — DATA & MASKS.** Datasets + purpose-built sets (Stephan/Tanishq) → CC-5/CC-5b detector masks;
   calibrate the material gate. *Exit:* real masks with M1′ provenance.
5. **Sprint E — POE PILOT (David-led, the observational engine).** IRB; kit locked (borrow-first); Phase 0 →
   Phase 1; feed the challenge ledger + the proxy→outcome calibration. *Exit:* fixed-IV/measured-DV observations
   accumulating; first calibration curves.
6. **Sprint F — CLEAR-PANEL + KNOWLEDGE (parallel).** Tier-B geometry + C11/C13 + provenance ledger; enable
   connectors + elaborate the encyclopedias. *Exit:* geometry trustworthy; thin cells cited.
7. **Sprint G — VALIDATE & PUBLISH (the payoff).** Analyze the pilot before/after case study (proxies calibrated
   against measured outcomes; challenges catalogued); finish the manuscript. *Exit:* the "code" evidenced on
   real spaces, with its anomalies honestly on the books.

## 6. Governing-doc index (the map)
- Vision: `docs/VISION_AND_DIRECTION_2026-07-30.md` (current) ← `…2026-07-14.md` (founding register model).
- Keystone: `…/Post_Occupancy_Evals/POE_Cognitive_Code_v1_2026-07-09.md`.
- POE pilot: `docs/POE_HomePilot_and_ZHA_GamePlan_shareable_2026-07-21.md`,
  `docs/POE_Pilot_Kit_Protocol_Instruments_IRB_ZHA_2026-07-21.md`.
- Demonstrator: `docs/CLAUDE_ENTRANCE_FOYER_TAGGER_ASSIGNMENT_2026-07-30.md`.
- Engine: `cnfa_algs/ARCHITECTURE.md` · `CONTRACT.md` · `JUSTIFICATION_TABLE.md`; `annotation_socket/SOCKET_CONFORMANCE.md`.
- Controller: `…/REPOS/_control/status/` (07-15 master §2 is canonical for the architecture).
- Well-being: `docs/WELLBEING_CODE_AND_VIZ_OPERATORS_2026-07-18.md`.
- Space planning: `space_planning/` (CRITERIA / BASELINE / worked_example).
- QA architecture: `docs/USER_TAILORED_QA_SYSTEM_ARCHITECTURE_2026-07-29.md`; `viz/question_composer.py`.
- Activity/space-use: `docs/IMAGE_TAGGER_SPACE_USE_ATTRIBUTE_MINING_BRIEF_2026-07-29.md`.
- Current state (2D/3D): `docs/VISION_TAGGING_2D_3D_CURRENT_STATE_2026-07-29.md`.
- This session's strand roadmap + acquisition: `docs/PROGRAM_ROADMAP.md`, `docs/IMAGE_DATABASES_ACQUISITION.md`.
- Live queue: `TASKS.md`. Cross-project history: `…/REPOS/MASTER_STATUS_ALL_PROJECTS_2026-07-20.md` (+ 07-15 §2).

---

### 7. Direction locked — David's 08-01 calls (folded into §3.5, §2.7, §3.7, §5)
1. **Canonicalize — with an epistemic guard.** The CNFA engine is the entrenched source of the BN/EN and of our
   recommendations, so yes, make it canonical. **But** because our POE tests are themselves based on the engine,
   we cannot let it silently absorb its own anomalies: we build the **challenge ledger + the two registers**
   (applied vs declared instrument-conformance) and treat POE as **observational, fixed-IV/measured-DV** data
   that accrues its own claims and can flag contradictions with CNFA predictions (§3.7).
2. **Entrance/foyer leads, as predictions → HITL.** The foyer is a set of engine *predictions* first, not an
   empirical study; the biggest near-term focus is **HITL on those predictions against human judgment**, with
   simple local measures secondary (§3.5). The instrumented campus pilot follows.
3. **3D from ZHA is prioritized, not held.** We will receive ZHA 3D models; the work is exact plan extraction
   (easier than 2D), **extracting multiple occupant viewpoints ourselves**, and **binding material names to the
   regions where they occur** (feeding the materials branch) (§2.7).

*This is v1. It stays a living doc — as the foyer HITL, the corpus replay, and the ZHA models land, the state
tags and the challenge ledger update against them.*
