# Materials Encyclopedia — physical properties × human impact

**An evidence-graded reference mapping architectural materials to the physically-relevant properties they
carry and the known effects of those properties on human cognition, affect, and health/wellbeing.** Seed
started 2026-07-31 (cowork lane). Part of the CNfA / "reading space as place" program — this is the
*materials register* of a space.

## Why it exists
The literature is real but scattered across ≥6 fields that barely cite one another — room acoustics, wood
science, biophilic design, embodied cognition, materials-experience design research, autism/sensory
architecture, and building-science / indoor air quality. The partial precursors each miss most of it:
Terrapin's biophilic patterns touch materials but aren't a materials reference; Karana's *Materials
Experience* covers meanings but not cognition or health; engineering databases (Granta/CES) have the physical
properties but zero human impact; WELL has health features but isn't organized by material. **A consolidated,
evidence-graded materials→people reference does not exist.** This is that.

## The organizing principle — doubly indexed
Most effects do not belong to a *material*; they belong to a *physical property the material happens to have*
(acoustic absorption, surface reflectance/gloss, fractal dimension, thermal effusivity, VOC emission,
hardness/roughness). The same impact recurs across any material sharing the property. So the encyclopedia is
indexed two ways:
- **`entries/<material>.md`** — per material: its property profile + the impacts it inherits.
- **`MEDIATORS.md`** — per mediating property: the impact it drives, the mechanism, the evidence, the refs.
A material entry's claims *point to* the mediator that produces them, so "wood calms" resolves into "matte,
mid-fractal, warm-to-touch, sound-absorbing, low-VOC — and here is which of those does the calming." This
keeps it honest and makes it computable (see Program hooks).

## Impact dimensions covered
attention/focus · memory · speech intelligibility & communication · cognitive load / task performance ·
stress & autonomic restoration · affect / mood · preference / likeability · prosociality / aggression ·
neurodiverse sensory load · health.

## Evidence grading (David's bar — every claim carries one)
- **firm** — replicated, often physiological/controlled (e.g., acoustics→learning; IAQ→cognition).
- **framework** — a coherent, supported model but softer or largely correlational (e.g., biophilic
  restoration, materials-experience meanings).
- **contested** — plausible but with replication trouble or thin evidence (e.g., haptic priming of social
  judgment; wood→cognitive performance; material→aggression).
No design-blog assertion is laundered into a fact; if the source is weak, the grade says so.

## Program hooks
Materials are a readable property of a space, so this plugs into the same machinery as the clutter work: the
tagger reads material attributes from images, and a property-mediated encyclopedia lets a read material map to
*predicted human impacts* — feeding the wellbeing/affective channel and the space-use attributes. Materials
can become HITL-validated attributes (hypotheses, human review, per the species model) exactly like the
clutter species.

## Status & contribution
Seed: `MEDIATORS.md` + entries for wood, concrete, acoustic textile, glass. Lane: **cowork** authors;
**codex** commits via the `docs/` sweep (coordination protocol). Add materials as `entries/<name>.md` to the
same schema; extend `MEDIATORS.md` when a new mediating property appears.

## Entry schema (see any file in `entries/`)
1. Identity — class, typical architectural uses.
2. Physical property profile — values/qualities for each mediating property.
3. Impacts — table: dimension · direction · via which mediator · evidence grade · source.
4. Semantic / cultural meaning — what people read into it; cultural variation; beliefs about proper use.
5. Caveats / thin spots — where the evidence is weak or missing.
