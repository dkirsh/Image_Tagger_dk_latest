# Social-presence matrix — the moderator grid

*How the presence of others moves each impact, and what flips the sign. The columns are
the **moderators** (the things that decide which way presence cuts); the cells give the
direction under that condition and the evidence grade. This is the grid the tagger's
occupancy register conditions on. Last updated 2026-07-31 by cowork. Lives at
`docs/space_effects/social_presence/MATRIX.md`.*

Legend: **↑/↓** raises/lowers · **~** neutral/mixed · grades **[F]** firm · **[K]**
framework · **[C]** contested. Mechanism numbers (§1–§8) index `MECHANISMS.md`.

---

## Matrix 1 — Impact × who the others are × task/condition
The single most useful cut. "Presence of others" is read through two questions:
**what's the task?** and **who are they?**

| impact | simple/known task | complex/novel task | others = strangers/crowd | others = trusted/supportive | via |
|---|---|---|---|---|---|
| task performance | **↑ [F]** | **↓ [F]** | ↓ if evaluative/dense [F] | ~/↑ (reduced anxiety) [K] | §1, §6 |
| stress / autonomic | ↑ arousal (mild) [F] | ↑ arousal [F] | **↑↑ crowding stress [F]** | **↓↓ buffered [F]** | §2, §3 |
| attention / self-reg | ↑ focus (drive) [K] | ↓ (distraction/monitoring) [K] | ↓ (overload) [K] | ~ [K] | §1, §2 |
| affect / mood | ~ | ~ | ↓ (crowded, cold) [K] | **↑ [F]** | §3, §7 |
| communication / speech | — | — | **↓ competing talkers [F]** | ~ | §2 (+ materials §1) |
| prosociality vs aggression | ~ | ~ | **↓ helping / ↑ withdrawal [F]**; ↑ aggression if chronic+no control [C] | ↑ prosocial [K] | §2, §7 |
| privacy / control | ~ | ~ | ↓ (intrusion) [K] | ~ (if chosen) [K] | §4, §5 |
| neurodiverse load | ↑ | ↑ | **↑↑ [K]** | ~/↓ if trusted [K] | §8 |

Reading it: the two firm, opposite-sign anchors are **crowding stress** (strangers +
density + low control → ↑↑ stress) and **social buffering** (trusted others → ↓↓ stress).
Between them, **task complexity** flips performance (help on easy, hurt on hard). Nearly
every "does a crowd help or hurt?" question resolves by locating the case on these axes.

## Matrix 2 — Occupancy level × what changes (holding the space fixed)
Same room, three occupancy states — the conditioning the tagger emits.

| occupancy state | dominant mechanism | net effect (typical) | biggest caveat |
|---|---|---|---|
| **empty** | none (baseline) | space's physical registers act at baseline | isolation can itself stress (§5 mismatch) |
| **low / working density** | §1 mild facilitation, §6 if observed | ~ / mild ↑ arousal; often optimal for routine work | depends on evaluation & relationship |
| **crowded (strangers, low control)** | §2 crowding, §4 proximity | **↑↑ stress, ↓ complex performance, ↓ helping** | control/predictability can rescue it |
| **full but supportive (event, chosen)** | §3 buffering, §7 positive contagion | ↑ mood, ↓ stress despite density | flips negative if control/choice is removed |

The lesson for the tagger: **density alone doesn't set the sign — control, relationship,
and choice do.** So the occupancy register must carry more than a headcount; it needs
(where readable) density-relative-to-area, personal-distance violations, and any cue to
whether presence is chosen/supportive vs imposed.

---

## RAG fill queue — thin cells, query ready
Ordered by value; run when connectors are on, then grade + cite.

1. **Density → aggression/withdrawal, field evidence (pin the [C]).** Scite:
   *"residential/institutional crowding and aggression — replications and null results."*
   Separate acute lab from chronic field; likely stays [C] for aggression, [F] for
   withdrawal.
2. **Social buffering × social anxiety (the reversal).** Elicit report: *"When does the
   presence of others fail to buffer or amplify stress? Role of social anxiety and
   relationship quality."* Sharpens §3's moderator.
3. **Open-plan office: co-worker presence & overheard speech → performance/stress [F→quantify].**
   Consensus: *"open-plan office occupancy and irrelevant speech effects on cognitive
   performance and stress."* Bridges to materials §1 (acoustics).
4. **Classroom/learning density → attention & achievement.** PubMed/Elicit: *"class size
   and physical density effects on attention and learning outcomes."*
5. **Proxemics distances by culture (firm-up §4 specifics).** Elicit: *"cross-cultural
   personal-space preferences — measured interpersonal distances."*
6. **Neurodiverse social load vs sensory load (which dominates).** Scite: *"autistic
   adults built environment — social presence vs sensory environment as stressor."*
   Feeds §8 and the materials §8 cross-ref.
7. **Emotional/behavioural contagion at scale (ceiling on §7).** Scite: *"deindividuation
   and crowd behaviour — contemporary evidence."* Keep large-crowd claims [C].

New mechanisms get added to `MECHANISMS.md` first, then referenced here. The tagger's
occupancy-register spec (cues → hypotheses → HITL) is a `docs/validation/` artifact and
points back at this base for the impact model.
