# HITL Study Design — how to run it without multiple copies of the same space

*2026-08-01, cowork. Answers David's question: adaptive-preference HITL wants *comparisons*, but we may not
have multiple examples of the same entrance/foyer. Lives at
`docs/validation/HITL_STUDY_DESIGN_NOTE_2026-08-01.md`. Pairs with `CHALLENGE_LEDGER_SPEC` (a HITL result that
contradicts a prediction is a challenge record) and the entrance/foyer demonstrator (§3.5 of the direction doc).*

## The real problem (why this isn't trivial)
Adaptive-preference methods learn a preference/scale efficiently by choosing informative **pairwise
comparisons**. Two things bite at the start:
1. We likely have **many different** foyers but few or no repeats of the **same** foyer, so there's no
   within-space pair to hand the method.
2. Even if we grab arbitrary cross-space pairs, an uncontrolled "which foyer do you prefer?" confounds a dozen
   factors at once — you learn *that* people prefer foyer X, not *why*, so the preference data **cannot
   adjudicate any specific engine prediction.**

**So the governing principle is not "get pairs" — it is "get pairs that isolate the construct the engine
predicts, holding other factors fixed."** That is the facet-isolation logic (from the clutter work) applied to
foyers. Once you accept that, the "same-foyer" requirement dissolves: you don't need repeats of nature, you
**construct** the comparison set.

## Three ways to get comparison structure — staged by what we can do now
### Stage 1 — Single-stimulus prediction validation (NO pairs; do this first)
Not all HITL needs comparison. For each foyer in a corpus, the engine emits a per-construct prediction
("low arrival-orientation support"; "high glare risk"); a human judges **agree / disagree / can't-tell** (the
review-pack viewer already does exactly this) or gives an absolute rating (VAS). *Tests:* does the engine's
read of THIS foyer match human perception? *Needs:* only a foyer corpus. *Feeds the ledger:* a disagreement is
a `kind:"level"` challenge. This is the fastest first HITL and it unblocks the demonstrator immediately.

### Stage 2 — Cross-space, construct-anchored pairwise (many different foyers)
Use the many *different* foyers, but **anchor every comparison to one named construct**: "which of these two
entrances better supports *finding reception*?" / "…feels more *welcoming on arrival*?". Collect 2AFC
judgments, fit a **Bradley-Terry / Thurstonian scale**, and compare the human scale to the engine's predicted
scale on that construct (Spearman/Kendall). *This is exactly the SAVOIAS method* (pairwise → global ranking) —
so we already know it works and how to analyze it. *Tests:* does the engine's *ordering* on a construct match
the human ordering across real spaces? *Feeds the ledger:* a rank reversal is a `kind:"ordering"` challenge.

### Stage 3 — Within-space controlled counterfactual variants (the sharpest test)
Take **one** foyer and generate variants that differ on **one predicted factor** — material swapped, lighting
changed, clutter added/removed, a partition moved, occupancy varied — everything else held. Now you have
within-space pairs that isolate the construct, which is what adaptive preference actually wants. *Tests:* when
the engine predicts variant A > variant B on comfort/legibility, do humans agree? *This is the cleanest
challenge generator* because the only thing that changed is the thing the engine predicted on. *Needs:* a
variant generator (below).

## Where the variants come from (so Stage 3 is cheap)
- **From a 3D model (best — and this is why the ZHA 3D intake matters for HITL):** re-render the same foyer with
  one factor changed. One geometry, N controlled variants, photoreal, exact. The 3D intake path (§2.7) is
  therefore also the HITL stimulus factory.
- **From 2D now (before ZHA models):** the generators already built — `phase_scramble.py` and `make_mooney.py`
  for the perceptual/complexity arm — plus edit-based variants (relight, declutter, material-swap via
  inpainting) for the foyer constructs. Cruder than 3D re-renders but enough to start Stage 3 on key factors.
- **Design-alternative framing:** the QA "Question-to-Test Contract" (07-29) already models "the changeable
  design alternatives" — a variant set *is* that contract instantiated.

## The stimulus is multimodal and position-dependent (David, 08-01) — the harder half
A silent flat image cannot elicit the judgments the foyer constructs are *about*. "Where would you stand?" is
not a visual choice — by our own theory it depends on **street noise, room acoustics, speech intelligibility,
being overheard, and where other people are**. So the stimulus has to render **audio + visual + social state as
a function of position**, and the participant's response is read against that joint field. This is not a
complication bolted onto the comparison design — it *is* the comparison design: the manipulated "ingredients"
are exactly the factors the engine predicts on.

**The manipulated ingredients (each is an engine input and an engine prediction):**
- **Acoustic field** — street-noise level (we already simulate street noise), reverberation from the space's
  geometry+materials, the direct/reverberant balance and STI at the listener position, plus specific sources: a
  reception/queue babble, and a *target talker* for the "would this be overheard?" judgment.
- **Social field** — the location, number, and grouping of other people (empty / a queue at reception / a
  cluster by the door / dispersed). Occupancy is a **manipulated variable here**, not just a reading — this is
  the social-presence strand entering as stimulus.
- **Position** — the listener/viewer's standing point, because all of the above change with where you are.

**How the audio is made (the headphones part).** Auralize per position: build a **binaural room impulse
response (BRIR)** from the space geometry + per-surface absorption using the image-source method
(`pyroomacoustics` does this offline now), convolve the dry sources (street noise, babble, target talker) with
it, and deliver over headphones. Crucially the BRIR is driven by **the CNFA acoustic model itself** (the
`acoustics_plan` operator, ISO 3382-3) and by **material absorption coefficients from the materials
encyclopedia** (acoustic absorption §1 is its firmest mediator) — so the simulation and the engine share one
model, and the human judgment tests whether the engine's acoustic/privacy/proxemic prediction matches felt
experience. A near-term MVP needs no game engine: **discrete stations, pre-rendered binaural audio + rendered
views, 2AFC or position-choice.** Interactive "move and hear it change" is a later Unity+Steam-Audio / web
Resonance-Audio build — and the **ZHA VR material** (the set I asked Tanishq about) may be the immersive visual
substrate for it.

**The responses this unlocks:** a preferred-standing-position **heatmap**; "where would you hold a private
word?" (speech-privacy); willingness-to-linger per position; and 2AFC **between audio-visual-social cells**
(this is the adaptive-preference pool — see below).

**Why this *solves* the comparison problem rather than worsening it.** The cells of the factorial
{position × noise × occupancy × acoustic treatment} over ONE foyer are exactly the within-space controlled
variants of Stage 3 — one factor changed, everything else held, each rendered in all modalities. So the
multimodal stimulus and the comparison set are the same object, and each cell carries the engine's prediction,
so every human reversal is a challenge-ledger record.

**What runs where (no local CAD needed).** Our side is Python + cloud: the **tagger/CNFA engine and the
`pyroomacoustics` auralizer are pure Python** (run in our pipeline / any Mac, no GUI); **Treble** (if we ever
buy realism) is **cloud/browser**; **Rhino/Grasshopper (+ Pachyderm)** is the **ZHA-side** parametric surface
and the back-propagation target, *not* something to install on a MacBook to run this work.

**Honest caveats.** Headphone auralization on a flat screen ≠ being there (no own-voice, limited immersion); a
VR headset + spatial audio narrows the gap. And the auralization is itself an instrument — whether our BRIR
matches a *measured* room is its own declared instrument-conformance question (recursion, but on the books).
The fully real version is the in-situ POE pilot; the sim tests *predictions* against judgment, which is the
right job for it.

**Per-construct staging correction:** Stage 1 (silent single-stimulus) validates the *visual* constructs
(glare, clutter, visual openness). The **acoustic / proxemic / speech-privacy constructs require the
multimodal sim from the start** — they cannot be done silently. So staging is per-construct, not strictly
sequential.

## The adaptive layer (once a pool exists)
Adaptive preference selects the next most informative comparison. Its pool is whichever of the three stages is
running, and its selection rule is the **boundary / coverage / disagreement queues** already in the Phase-1
artifact contract — so the active-corpus selection we specced *is* the adaptive sampler. Priority goes to pairs
near the engine's decision boundary and to items where model and humans (or two humans) disagree.

## Staging recommendation
1. **Now:** Stage 1 on a foyer corpus (single-stimulus, via the viewer) — unblocks the demonstrator, needs no
   pairs, needs no 3D.
2. **Next:** Stage 2 construct-anchored pairwise over the same corpus (Bradley-Terry vs engine scale).
3. **When variants exist (2D generators, then ZHA 3D):** Stage 3 controlled counterfactuals — the definitive
   test and the primary challenge-ledger feed.
Every stage's disagreements/reversals write to the challenge ledger, so HITL and the epistemics of §3.7 are the
same pipeline seen from two ends.

## Open items for David
- **Do we have a foyer/entrance corpus yet?** SUN397 / Places365 have `lobby`, `entrance_hall`,
  `reception` categories — a Stage-1/2 corpus is buildable from the datasets on the acquisition list. I can
  inventory what entrance/foyer images we already hold on request.
- **Which constructs anchor the foyer study first?** Candidates from the space-use priorities:
  arrival-orientation support, wayfinding-to-reception, welcomingness/affect-on-arrival, waiting/route conflict.
- **How many variants per factor** for Stage 3, and which factors first (materials + lighting are the cheapest
  from a 3D model and map straight onto the materials branch).
- **Auralization toolchain:** start with an offline `pyroomacoustics` BRIR MVP (discrete stations, pre-rendered
  binaural + views, 2AFC), or invest earlier in an interactive VR+spatial-audio build? The **ZHA VR material**
  (pending Tanishq's answer) may decide this.
- **Dry audio assets** to record/source: street noise, reception/queue babble, and a scripted **target talker**
  for the overheard-speech judgment; plus headphone hardware + a level-calibration step.
- **Which foyer constructs go multimodal-first** (speech privacy, where-to-stand, arrival comfort under
  noise) vs silent-visual-first (glare, clutter, openness).
