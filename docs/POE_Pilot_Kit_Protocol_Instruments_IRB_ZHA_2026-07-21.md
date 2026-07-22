# POE Pilot Kit — protocol, instruments, IRB & ZHA agenda

Everything to run the unified Cognitive + Wellness + Physiology POE pilot on campus, and to open the ZHA conversation

Working document · 21 July 2026 · companion to the Home Pilot & ZHA Game Plan
**Scope.**This expands the game plan into the actionable pieces you asked for: a detailed pilot **protocol + measurement schedule**(§1–2), the full **sensor/instrument list**(§3–4), a one-page **IRB outline**(§5), and a first-meeting **ZHA agenda + talking points**(§6). §7 connects it to the Qualcomm healthcare proposal, which shares the same evidence base and sensor stack. Indicative kit costs are procurement guidance, not commercials.
## 1. Pilot protocol — the two-phase design

**Design.**The same 4–6 campus spaces are measured twice — first as a **classical POE**(Phase 0), then with the **unified code**(Phase 1) — so the contrast is the argument. Within-space, within-time-window where possible, so the two methods see the same conditions. Add repeated visits at 2–3 times of day (morning / midday / late afternoon) because light, CO₂, acoustics, and alertness all swing across the day — a single snapshot is exactly what standard POE gets wrong.

### Per-space run sheet

- **Fixed environmental sweep**(both phases): walk the space on a grid; log the environmental instruments at each station (see §3); photograph each station for the Image Tagger; note occupancy + activities.
- **Occupant measures**(Phase 1, consented): a short survey; the cognitive micro-battery in situ; wearables (HRV/EDA) on a volunteer subset for a seated 20–30 min window; salivary cortisol before/after on a smaller subset; an ESM week for regular occupants.
- **Design-time read**: run the Image Tagger on the station photos / any available render, so the design-time proxies can be calibrated against the measured outcomes (the point of a "code").

## 2. Measurement schedule

| Block                    | Phase 0 — classical                  | Phase 1 — unified                                                                                                     | Who                           |
|--------------------------|--------------------------------------|-----------------------------------------------------------------------------------------------------------------------|-------------------------------|
| **Acoustic**| dBA spot-check                       | LAeq + STI/STIPA + RT60 at ≥3 positions; note talker distance                                                         | Stephan                       |
| **Light**| desk lux; "window? y/n"              | m-EDI + CCT + lux at eye; DGP (HDR fisheye); flicker %/Hz; view-content score; wearable dosimeter (subset, multi-day) | Stephan / Tanishq             |
| **Thermal**| air temp; PMV band                   | MRT (globe) + air/RH loggers + air velocity; adaptive-controls audit; skin-temp gradient (subset)                     | Stephan                       |
| **Air**| CO₂ spot                             | CO₂-decay air-change + continuous CO₂/VOC/PM₂.₅ logging; material off-gassing walk-through; (optional) TD-GC-MS assay | Tanishq                       |
| **Space / cognition**| wayfinding Likert; "supports focus?" | prospect/refuge map; timed destination-finding + sketch-map (naïve visitors); Image Tagger fields                     | Stephan + David               |
| **Physiology**| comfort/stress Likert                | HRV + EDA (seated window); salivary cortisol pre/post (subset)                                                        | Stephan (IRB)                 |
| **Cognition (task)**| self-reported productivity           | PVT + n-back + Stroop micro-battery in situ                                                                           | Tanishq builds / Stephan runs |
| **Behaviour**| —                                    | occupancy/seat-choice logging; ESM week; stair-vs-lift counts                                                         | Tanishq                       |
| **Affect / restoration**| satisfaction Likert                  | PRS + Russell valence/arousal; 2AFC image comparisons (labeling console)                                              | Stephan                       |

Cadence: Wk 2–4 Phase 0 (fast, ~1 visit/space); Wk 4–8 Phase 1 (the instrument-heavy phase, 2–3 visits/space + the ESM week); Wk 8–10 analysis + the before/after case study.

## 3. Sensor & instrument list (the kit)

Grouped by domain. "Type/model" gives a representative instrument (choose exact models with Tanishq); own = buy into the kit, borrow = campus facilities/other labs likely have it. Costs are indicative GBP for procurement planning.

| Domain / construct                       | Instrument — type & representative model                                                                                                 | ~£           | Src         | Operator / note                                              |
|------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------|--------------|-------------|--------------------------------------------------------------|
| **Acoustic**— LAeq, STI, RT60           | Class-1/2 SLM + STIPA analyser (NTi **XL2**+ M2230 mic; or Brüel&Kjær 2255). Impulse-response for RT60.                                 | 1,500–2,500  | own/borrow  | Stephan — calibrate with an acoustic calibrator each session |
| Acoustic — continuous dB                 | Logging SLM or 2–3 calibrated noise loggers (e.g. Svantek/Convergence); phone SLM app for screening only                                 | 0–600        | borrow      | Tanishq — time-sync to the survey                            |
| **Light**— m-EDI, CCT, lux, spectrum    | Spectral light meter / spectroradiometer (**Sekonic C-800**or UPRtek MK350S), measured vertically at eye                                | 1,200–1,800  | own         | Stephan — the melanopic (circadian) instrument               |
| Light — circadian dose (multi-day)       | Wearable light dosimeter (LYS button / ActLumus / Daysimeter) logging m-EDI at the eye                                                   | 150–900 ea   | own/borrow  | subset of occupants for a few days                           |
| Light — glare (DGP)                      | DSLR/mirrorless + fisheye → HDR → evalglare; or a luminance camera (Technoteam LMK) if borrowable                                        | 0–500\*      | borrow      | Tanishq — \*if no camera on hand                             |
| Light — flicker (TLM)                    | Flicker meter, modulation% + frequency (Viso Light Spion / UPRtek)                                                                       | 300–1,200    | own/borrow  | at each luminaire type                                       |
| **Thermal**— MRT, air, RH, velocity     | Globe thermometer + air/RH loggers (**HOBO MX1101/MX1104**) + hot-wire anemometer; or an integrated comfort meter (Testo 400 / B&K 1213) | 400–1,500    | own/borrow  | Stephan — multi-height for radiant asymmetry                 |
| Thermal — skin gradient                  | Skin-temp loggers (Maxim **iButton DS1922L**) at hand (distal) + clavicle (proximal); or a thermal wearable                              | 200–500      | own/lab     | subset; distal-proximal gradient                             |
| **Air**— CO₂ (air-change)               | NDIR CO₂ monitors ×2–3 (**Aranet4**), logging, for the CO₂-decay tracer method                                                           | 180–250 ea   | own         | Tanishq — also the ventilation-vs-cognition pairing          |
| Air — VOC / PM₂.₅ / HCHO                 | Continuous IAQ monitors (Awair Element / Airthings / AtmoTube Pro); a PID for TVOC (Ion Science Tiger); formaldehyde meter               | 200–900      | own         | Tanishq — low-cost for trend + PID for magnitude             |
| Air — speciation (optional)              | Passive VOC samplers → **TD-GC-MS**lab assay (per-sample cost)                                                                          | assay        | lab/service | only where the material-emissions story needs it             |
| **Physiology**— HRV                     | ECG chest strap (**Polar H10**) or ECG patch (Movesense/Bittium)                                                                         | 80–300 ea    | own/lab     | Stephan (IRB) — seated 20–30 min window                      |
| Physiology — EDA + skin temp + PPG       | Research wearable (**Empatica EmbracePlus**or **Shimmer3 GSR+**)                                                                        | 500–1,500 ea | lab         | Stephan — palmar/wrist EDA                                   |
| Physiology — cortisol                    | Salivettes + ELISA/LC-MS assay (pre/post exposure)                                                                                       | kit + assay  | lab/service | small subset; timing-controlled                              |
| Physiology — neuro (optional, later)     | Mobile EEG (frontal-alpha asymmetry) / fNIRS for neuroaesthetic response                                                                 | lab          | lab         | advanced; only if a lab rig is free                          |
| **Behaviour**— occupancy / seat choice  | BLE/UWB beacons or PIR occupancy loggers; door/stair counters; wrist actigraphy (ActiGraph/Axivity)                                      | 0–500        | lab         | Tanishq — anonymised counts                                  |
| **Software**— perceptual + tasks + code | Image Tagger; 2AFC labeling console; PsychoPy battery (PVT/n-back/Stroop/SART); ESM prompt app; Knowledge Atlas grounding                | 0 (ours)     | ours        | David / Tanishq                                              |

**Core purchasable kit**lands roughly £4–6k before assays and the physiology wearables (many of which the lab likely already has). Borrow-first from campus EH&S / facilities / other labs wherever possible — SLMs, comfort meters, luminance cameras, and actigraphs are common shared instruments.

## 4. Non-hardware instruments (scales, tasks, protocols)

- **Cognitive tasks**(PsychoPy, already in Experiment_Maker): Psychomotor Vigilance Task (PVT), n-back (working memory), Stroop (interference), SART (sustained attention). Brief in-situ versions (~2–5 min each).
- **Perceived Restorativeness Scale (PRS)**— 3–4 items (being-away, fascination, coherence, compatibility).
- **Affect**— Russell valence/arousal (circumplex) short form.
- **View Content Rating**— nature/built/sky classification of any window view.
- **Prospect–refuge mapping**— visible-floor + view-distance (prospect) and back/side enclosure (refuge) per seat.
- **Wayfinding**— timed destination-finding + sketch-map/pointing accuracy with naïve visitors.
- **ESM**— smartphone prompts (mood/location/activity/conditions) across a week.
- **2AFC image comparisons**— the labeling console, for the perceptual-attribute validation.

## 5. IRB — one-page submission outline
Human-subjects measurement (cortisol, HRV/EDA, cognitive tasks, surveys, ESM, occupancy sensing) requires IRB approval and informed consent **before any data collection**. UCSD Health / the Qualcomm proposal note existing IRB relationships — check whether an umbrella or expedited pathway applies. This outline is a drafting aid, not the submission.
- **Title / PI:**"Environmental correlates of cognition, comfort, and physiological state in campus interiors" — PI David Kirsh; co-I Stephan.
- **Design & population:**observational + within-participant; adult volunteers (staff/students) who consent; naïve visitors for wayfinding. Target N per venue small (e.g. 8–20 for wearables; more for surveys/ESM).
- **Procedures:**non-invasive environmental sensing of the space; consented occupant measures — surveys, brief cognitive tasks, wearable HRV/EDA for a seated window, salivary cortisol (pre/post) on a subset, ESM prompts, anonymised occupancy counts.
- **Risks:**minimal — no intervention; benign interiors; wearables non-invasive; task fatigue mild. Privacy is the main risk → mitigations below.
- **Privacy / data:**no images/audio/video of identifiable people leave the room (edge-only where sensing people — mirrors the Qualcomm HIPAA-by-architecture stance); occupancy is anonymous counts; wearable/cortisol data coded, stored on approved systems; consent covers reuse; retention + destruction stated.
- **Consent:**written informed consent; voluntary; withdraw any time; separate consent for saliva collection.
- **Benefit / compensation:**minimal incentive for time; scientific benefit; no clinical claims.

## 6. ZHA — first-meeting agenda & talking points

### Agenda (45–60 min)

- **1 · The gap (5m):**physical code vs the cognitive+wellness code — what standard POE misses.
- **2 · The machine (10m):**live Image-Tagger read of a foyer — the spatialised fields — plus the Atlas grounding.
- **3 · The proof plan (10m):**we're validating on our own campus first — classical POE vs the unified code on the same spaces — and will bring a before/after case study. De-risked, evidenced.
- **4 · What a ZHA engagement looks like (10m):**one POE on one existing ZHA building → design-time checks in your tools → the signature entrance. Two clean tracks (our academic pilot; the commercial collaboration).
- **5 · What we'd need from you (10m):**a champion, one existing building, one live project, a couple of designers + IT.
- **6 · Next steps (5m):**confirm the target building + champion; settle the collaboration terms separately.

### Talking points

- "We turn *make it feel spectacular and welcoming* into a checkable brief — while it's still on screen."
- "The arrival sequence is where ZHA is known; it's the cleanest place to show a space can be spectacular *and* measurably good to think, breathe, and settle in."
- "Every reading traces to a vetted source and states how firm the science is — defensible to a sceptical engineer."
- "You own what we build together in architecture; we keep and keep growing the engine — which is what keeps it improving for you."
- "We're not pitching a report that sits on a shelf; we're building the check into how the studio designs."

## 7. Connection to the Qualcomm proposal (found 2026-05-27)

**\`Kirsh_Design_Lab_Qualcomm_2026-05-27.pptx\`**("UCSD Design Lab × Qualcomm — Continuous environmental monitoring for hospital outcomes") is the **same methodology in a different sector**: the "38 things" evidence base and POE, applied to healthcare with Qualcomm's edge-AI stack (QRB5165 / Hexagon / Aware) for on-device, privacy-preserving monitoring of light, sound, air, motion, presence. Its three projects — Smart ICU Room, Aging-in-Place, and **POE-as-a-Service**— and its "every sensor choice has a citation behind it" framing are the healthcare twin of the ZHA architecture track. Why it matters here:

- **Shared sensor stack + evidence base**— the domains in §3 (acoustic, light, air, motion/presence, physiology) are exactly what the Qualcomm deck monitors; the campus pilot doubles as a proving ground for both.
- **IRB & clinical infrastructure**— the deck cites existing UCSD Health IRB approvals + outcomes-data feeds; that pathway may accelerate §5.
- **Two markets, one IP**— architecture (ZHA) and healthcare (Qualcomm) are the "same system licensed into different fields" that the term sheet reserves; the pilot evidence supports both conversations.
- **The \`Post_Occupancy_Evals/\` folder**holds the full POE lineage (the "38 things" review + sci-writer pass, the pitch decks, the v1 Zaha dossier, the Cognitive Code v1, the corpus growth plan) — worth mining as we finalise the pilot.

Working document, 21 July 2026. Companion to `POE_HomePilot_and_ZHA_GamePlan`. Instrument models are representative, not endorsements; confirm exact models + current campus availability with Tanishq. Human-subjects work requires IRB approval and consent. Not legal, financial, or medical advice.
