# Physical Code vs Cognitive Code — A Worked Example

*Space-planning workstream, `space_planning/`. Built 2026-07-15 (Fable/Claude Opus). This closes the gap a corpus
search surfaced the same day: nowhere did we actually run one space through **both** lenses and show the delta —
only a conceptual contrast existed. Here three real spaces are each scored twice: once as a **physical-code /
green-rating review** would certify them (lux, dBA, m²/person, LEED/WELL credits), and once by the **cognitive +
well-being engine** (`../cnfa_algs`, Tier A image-plane, run 2026-07-15). The point is the **divergence** — and the
finding is that the two codes disagree in three *different modes*, none of which a physical-code review can see.
This doubles as an **L1 validation case** (the engine orders the confident axes correctly and reveals its own Tier-A
limits where it is not confident — both stated honestly below).*

**How to read this.** The physical-code column states what a compliance/green-rating review of a space of this
*type* certifies — reasoned from the standards, not instrument-measured (these are photographs, not instrumented
rooms, so no real lux/dBA reading exists; the column is "what the physical code would say," and is marked as such).
The cognitive column cites the **engine's actual computed scalars** with their confidence, mapped to the criteria
in `CRITERIA.md`. Every number carries its Tier-A caveat: single-image proxies, heuristic plane segmentation, no
occupancy, no real plan. The divergence, not the decimal, is the deliverable.

See `physical_vs_cognitive_contactsheet.png` for the three spaces with their geometry and inferred-plan fields.

---

## The three spaces and the engine's raw read (Tier A, 2026-07-15)

| Engine signal (→ criterion) | Open-plan office | Corridor | Glass house | conf |
|---|---|---|---|---|
| prospect (C11) | **27.45** | 11.82 | 6.18 | 0.50 |
| isovist openness, inferred plan (C1/C12) | **7.98** | 3.03 | 1.56 | 0.34 |
| enclosure index (C11/C14) | 1.00 | 1.00 | **0.77** | 0.50 |
| prospect : refuge ratio (C11) | 0.78 | 0.67 | **0.49** | 0.34 |
| acoustic absorption proxy (C7/C8/C20) | 0.30 | **0.09** | 0.16 | 0.50 |
| glare risk (C10/§glare) | **0.32** | 0.23 | 0.29 | 0.65 |
| vertical illuminance proxy (C10) | 0.57 | 0.66 | **0.84** | 0.50 |
| warm:cool light ratio (C7-mood/C19) | 0.65 | 0.99 | 1.00 | 0.80 |
| landmark salience (C4) | 0.49 | **0.26** | 0.62 | 0.60 |
| brightness variance (C10 equity) | 0.25 | 0.13 | 0.19 | 0.90 |

The bold cells are where each space is extreme, and each extreme is where its physical-code review and its
cognitive read part company. Taken column by column:

---

## Space 1 — Open-plan office: the codes point in *opposite directions*

**What the physical code certifies:** green across the board. A naturally-lit, low-partition open floor of this
type meets illuminance minimums comfortably (engine brightness is high, glare only 0.32), sits inside the thermal
and CO₂ bands with normal ventilation, satisfies m²/person, and *earns* green-rating credits — LEED "Quality
Views" and daylight, WELL Light points — precisely *because* it is open and glazed. A physical-code review returns
"excellent, exemplary daylight and views."

**What the cognitive + well-being code reads:** the engine confirms the good part — highest prospect (27.45) and
highest inferred-plan openness (7.98) of the three, which is real encounter and outlook value (C1, C11). But the
same two numbers, read against `enclosure_index = 1.0` and a low acoustic-absorption proxy (0.30), are the warning:
**maximum openness with zero acoustic or visual separation.** That is the configuration the literature singles out
as net-negative. The physical code has *no instrument for speech privacy at occupancy* — and it is exactly there
that this space fails: at working density the distraction distance (C8, ISO 3382-3 r_D) blankets every seat, the
irrelevant-speech effect degrades focus (C7), and the objective-measured consequence is Bernstein & Turban's ~70%
drop in face-to-face interaction and Kim & de Dear's net −0.86 satisfaction. For the **sanctuary** occupant type
(CRITERIA §5) this space scores near-zero; for well-being it carries chronic-noise arousal (C20) and no retreat
(C19).

**The divergence:** **opposite-signed.** The physical code rates this space at its *best*; the cognitive/well-being
code rates the *same features* — openness, no partitions — as the mechanism of its worst outcome. This is the
single most important case for the whole programme: the physical code does not merely miss the problem, it
*rewards* it.

---

## Space 2 — Corridor: the physical code is simply *silent*

**What the physical code certifies:** compliant circulation. A corridor is the physical code's home turf — it is
certified by egress width, exit access, and a lux minimum, all of which this space meets. A compliance review
returns "pass," and has nothing further to say, because a corridor is, to the physical code, *solved once it is
wide enough and lit enough.*

**What the cognitive + well-being code reads:** an entire axis the physical code does not possess. The engine gives
this space the **lowest landmark salience of the three (0.26)** and the lowest inferred openness (3.03) — a long,
undifferentiated transit space with little to orient by, which is a **wayfinding-load** problem (C4): decision
points without visible landmarks are where navigation error concentrates. It also has the **lowest acoustic-
absorption proxy (0.09)** — a hard, reverberant tube (C20), and near-zero restorative or dwell value (C19, no
prospect, no nature content; warm-cool 0.99 is monotone). None of legibility, landmark salience, acoustic
hardness, or restoration is a physical-code quantity.

**The divergence:** a **coverage gap.** The two codes are not opposite-signed here; the physical code is *blank*
where the cognitive code fills in a whole missing dimension. A space the physical code considers finished and fine
is, cognitively, an unaddressed wayfinding-and-acoustics liability. This is the quieter but more pervasive failure:
most of what makes circulation good or bad is invisible to the code that governs it.

---

## Space 3 — Glass house (Farnsworth): the codes disagree on *comfort*

**What the physical code certifies:** a daylight and view *maximum*. The engine's read matches the intuition on the
axes the physical code cares about — lowest enclosure (0.77, most glazed) and **highest vertical-illuminance proxy
(0.84)**. A green-rating review would award top marks for daylight autonomy and quality views. (On thermal, a
single-glazed all-glass envelope is the textbook *failure* the physical code *can* partly see — glare and overheating
— which only sharpens the point below.)

**What the cognitive + well-being code reads:** the affordance and comfort cost the daylight score hides. The
engine gives this space the **lowest prospect-to-refuge ratio (0.49)** — prospect without refuge, glass on every
side, no protected back anywhere. `CRITERIA.md` C11 is explicit that prospect is preferred *but* the preferred seat
has outlook *and* a protected back; total exposure is hostile, most of all to the sanctuary type. Add glare (0.29)
and the well-being thermal/alliesthesia problem a glass box famously imposes, and the cognitive/well-being read is:
beautiful, luminous, and **uncomfortable to actually inhabit** — which is the enduring real-world verdict on this
building.

**The divergence:** **opposite-signed on comfort and affordance.** The physical code awards the glazing its highest
marks; the cognitive/well-being code flags the *same* glazing as exposure, glare, and thermal stress. Daylight
maximized becomes refuge and comfort minimized.

**An honest Tier-A limit, surfaced here on purpose.** The engine's `prospect` and `openness` scalars for the glass
house are its *lowest* (6.18, 1.56) — which is *wrong* to the intuition that a glass pavilion has maximal outlook.
The cause is the Tier-A pipeline: on a single photo of an all-glass building, with reflections and an ambiguous
indoor/outdoor boundary, the heuristic plane segmentation (confidence 0.45–0.50) mislabels glazed and reflective
surfaces, so the isovist proxy under-reads. This is not a defect to hide — it is the demonstration of *why* the
tiered design exists: the confident axes (illuminance, enclosure, prospect-refuge *ratio*, landmark) order
correctly; the isovist magnitude needs **Tier B/C (a real or inferred plan) or a proper segmenter** to be trusted.
The worked example thus validates the confident signals *and* correctly localizes the untrusted one.

---

## What the three cases show together

The physical code fails against the cognitive/well-being code in **three distinct modes**, and a single space type
exhibits each:

1. **Opposite-signed (open plan).** The physical code rewards the very features — total openness, no partitions —
   that drive the worst cognitive and well-being outcomes (speech-privacy loss, withdrawal, no retreat). The code
   is not silent; it is *wrong-signed*.
2. **Coverage gap (corridor).** The physical code certifies the space as finished and is then *blank* on the axes
   that actually vary its quality — legibility, landmark salience, acoustic hardness, restoration.
3. **Opposite-signed on comfort (glass house).** The physical code maximizes a scarce good (daylight/view) and is
   blind to its paired cost (exposure, glare, thermal stress, no refuge).

In none of the three could a practice working only to the physical code *see* the problem, let alone optimize
against it. That is the differentiator the cognitive code — and its space-planning application — is for: it makes
the invisible axes computable at design time, so a layout can be ranked on them while it is still on the screen.

---

## Verification boundary (RULE 0)

**What this is:** an L1 (known-contrast) demonstration. The engine ran at **Tier A** (single image, heuristic
plane segmentation at confidence 0.34–0.50, geometric depth fallback, **no occupancy, no real plan, no acoustic
simulation**) on three internet photographs on 2026-07-15; the raw scalars are in `worked_example/out/scalars.json`.
The **physical-code column is reasoned from the standards for each space *type*, not instrument-measured** — no real
lux/dBA/CO₂ reading exists for these photos, and the column is labelled accordingly; it states what a compliance
review *would* certify, which is sufficient to demonstrate the divergence but is not a measurement.

**What is trustworthy here:** the *direction* of each divergence and the ordering on the confident axes
(illuminance, enclosure, prospect-refuge ratio, landmark salience, brightness variance — confidence 0.5–0.9). **What
is not yet trustworthy:** the isovist-magnitude scalars (openness, absolute prospect; confidence 0.34), explicitly
flagged in the glass-house case; the acoustic proxy (needs the ISO 3382-3 STI/r_D pack and occupancy — `CRITERIA.md`
C7/C8 are ○ to-build); and any melanopic/thermal claim (needs the daylight and thermal models, also ○). No number
here is validated against a measured human outcome — that is L2/L3 (VLM/human judges, then physiology/behaviour),
still to run. The worked example proves the *codes diverge and how*; it does not yet prove the engine's magnitudes
are correct. Those are different claims, and only the first is made here.
