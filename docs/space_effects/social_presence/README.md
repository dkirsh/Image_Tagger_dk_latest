# Social Presence & Occupancy — how *other people* modulate a space's effects

**An evidence-graded reference on how the presence, number, density, relationship, and
behaviour of other people change what a space does to a person.** A space is not a
fixed stimulus; the same room acts differently empty, at working density, and crowded,
and differently again depending on *who* those others are. Seed started 2026-07-31
(cowork lane). Part of the CNfA / "reading space as place" program — this is the
**social-presence register** of a space, and it *conditions every other register.*

## Why it exists, and why it's separate from materials
Materials, clutter, and geometry are properties *of the space*. Social presence is
not — it is a property of the *occupation* of the space, and it acts as a **modulator**
on all the others. A "cluttered" open-plan office is more stressful full of strangers
than empty; a reverberant hall matters more when people are talking in it. So this
can't be a column in the materials matrix; it's a separate knowledge base whose output
is a *conditioning variable*. Treating occupancy as just another fixed attribute is the
central mistake this base exists to prevent.

## The organizing principle — one variable, two signs
"Other people" is not one thing. The literature splits it cleanly into two opposite-sign
bundles, and almost every apparent contradiction dissolves once you separate them:

- **Load / threat side (costs):** mere presence raises arousal and self-monitoring;
  density without control becomes crowding stress; strangers and evaluators add
  evaluative pressure. Hurts complex/novel tasks, raises stress, drives withdrawal.
- **Support / affiliation side (benefits):** the *supportive* presence of trusted others
  buffers the stress response (lower cortisol/cardiovascular reactivity) and improves
  mood and resilience. Opposite sign to crowding.

Which side dominates is set by **moderators**: task complexity, relationship to the
others (stranger/competitor vs friend/supporter), density relative to area, perceived
**control** and predictability, personal-distance and culture, and whether one is
observed/evaluated. `MECHANISMS.md` is the index of these; `MATRIX.md` is the grid.

## Impact dimensions covered
task performance (by complexity) · attention & self-regulation · stress & autonomic
reactivity · affect / mood · communication & speech (competing talkers) · prosociality
vs aggression/withdrawal · sense of privacy & control · neurodiverse load.

## Evidence grading (same bar as the materials encyclopedia)
- **firm** — replicated, often meta-analytic or physiological (social facilitation
  meta-analysis; crowding→physiological stress; social buffering of cortisol).
- **framework** — coherent supported model, softer/correlational (proxemics,
  territoriality, privacy-regulation).
- **contested** — plausible but thin or replication-troubled (mere-presence *mechanism*
  debates; some density→aggression field claims).

## Program hooks — what the tagger does with this
The tagger already reads a space; here it reads **occupancy cues** from the image as a
register: headcount, density relative to floor area, personal-distance violations,
gathering/queue structure, and (harder) relationship/behaviour signals. Its outputs are
hypotheses, HITL-validated like the clutter species. The key architectural move: every
*other* register's predicted impact is emitted **conditional on** the occupancy read —
e.g. "predicted stress from reverberation × (occupancy: crowded, strangers) → upgraded."
Empty-room predictions and occupied-room predictions are different outputs, not one.

## Status & contribution
Seed: `MECHANISMS.md` (mechanism index) + `MATRIX.md` (moderator grid). Lane: **cowork**
authors; **codex** commits via the `docs/` sweep. Extend `MECHANISMS.md` when a new
mechanism appears; RAG-fill the thin cells per the queue in `MATRIX.md`.
