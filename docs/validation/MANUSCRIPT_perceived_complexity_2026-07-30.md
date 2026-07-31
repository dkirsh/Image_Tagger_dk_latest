# Complexity for Whom, and for What? Perceived Visual Complexity as an Operation-Indexed, Model-Relative, Time-Extended Construct

**Working manuscript · 2026-07-30**
*D. Kirsh and collaborators. Draft assembled from the theory + experiment programme; a consolidation of
the review, the SAVOIAS measure-divergence study, and the fluency-refund psychophysiology design. Section
numbering and float callouts are provisional; the reference list is completed at submission.*

---

## Abstract

Visual complexity — and its aversive cousin, clutter — is almost always operationalised as a single number
computed from an image, and used interchangeably to predict search cost, aesthetic preference, wayfinding
difficulty, and stress. We argue, and show, that this scalar habit is wrong in three linked ways.
**First**, complexity is *underdetermined without an operation*: across 1,420 images of the SAVOIAS dataset,
eight standard measures correlate with one another only weakly (Spearman ρ = 0.22–0.93) and, decisively,
the measure that best predicts human complexity **changes with the domain** — compression for interiors and
advertisements, colour variety for scenes and abstract art, and *no image measure at all* for isolated
objects. Each measure was engineered to predict a particular operation's cost, and it succeeds exactly where
that operation governs judgment. **Second**, complexity is *model-relative*: apparent disorder is
incompressibility with respect to the viewer's learned model, so expertise and activity change felt clutter
with no change to the image — a claim we ground in effective complexity, compression-progress accounts of
interest, and the projection of task structure onto space (the chef's mise en place). **Third**, complexity
is *time-extended*: perception proceeds from a fast, image-computable stage to a slow, model-based one, and
the affective consequence of disfluency depends on whether a gestalt is available to close. We derive a
sharp, testable prediction — that the stress evoked by a cluttered or disfluent image is **refunded at the
moment of perceptual closure** for gestalt-resolvable disorder but **endures** for disorder baked into
low-level image statistics — and we specify a time-resolved psychophysiology experiment (facial EMG, skin
conductance, pupillometry, recognition-locked) to test it. We describe the predicted results and their
consequences: complexity should be represented not as a scalar, nor even as a single vector, but as a
profile indexed by **(processing stage, operation, observer model)**, and an image-only measure is best
understood as a model of the enduring, low-level, well-being-relevant affective channel rather than as a
detector of complexity as such.

---

## 1. Introduction

Ask an interface designer, a cartographer, an advertiser, a hospital architect, and a vision scientist how
complex an image is and each will hand you a number, and each number will mean something different.
The designer's tracks findability; the advertiser's tracks whether the eye stops; the architect's tracks
whether a corridor calms or agitates; the scientist's tracks how long a target takes to find. That these
are *different* numbers is not usually treated as a problem, because "visual complexity" is spoken of as a
property an image *has* — more edges, more colours, more stuff — a quantity one could in principle read off
the pixels once and for all. This paper is an argument, with evidence, that there is no such quantity, and
that the search for it has obscured what complexity actually is.

The everyday cases break the scalar picture immediately. A lecture hall of a hundred identical seats is
visually busy yet orderly; three chairs left at angles are sparse yet disarrayed — quantity and disorder
come apart. A black-and-white photograph of a zebra in grass is, by any texture measure, near-maximally
complex, yet observers rate it *low* in complexity, because the moment they recognise "a zebra" the image
reorganises into one familiar thing. A Suprematist composition of a few coloured bars is texturally simple
yet reads as elaborate. And — the case that dissolves the scalar entirely — your own desk is not cluttered
*to you*, because you know the pile-spanning conventions and that a sheet's orientation in a stack carries
information; to a visitor the identical desk is surprising disarray. The felt complexity changed with no
pixel changing. Three of these cases appear together in **Figure 1**: a zebra whose texture is complex but whose meaning is instantly simple; a few chairs whose sparse arrangement nonetheless reads as disarray; and a Suprematist composition of a few elements that reads as elaborate.

From these cases we extract three claims, each of which the paper defends and, where possible, tests.

**(i) Complexity is operation-indexed.** The reason eight reasonable measures disagree is that each was built
to predict a *different downstream operation* — visual search, memory encoding, aesthetic preference,
navigation, transmission cost — and complexity is only ever wanted as a cheap proxy for one of these. A
number untethered from an operation is not a weak predictor of complexity; it is a predictor of nothing in
particular. We show this directly (§3): which measure best matches human complexity flips across image
domains, because the domain fixes which operation dominates the judgment.

**(ii) Complexity is model-relative.** The "order" that cancels complexity is compressibility, and
compressibility is only defined relative to a model or decoder. Formally this is the machine-relativity of
algorithmic complexity and the requirement, in effective complexity, that a model decide which structure
counts as regularity; cognitively it is expertise, which supplies stored chunks under which the novice's
noise becomes the expert's signal; and in the strongest form it is *activity*, because agents arrange the
world to support their doing and then read the arrangement through the task it was arranged for (§2.3, §5).

**(iii) Complexity is time-extended.** Perception is not a single read but a trajectory from a fast,
feed-forward, image-computable stage to a slow, model-based one, and complexity is computed — differently —
at both. The illusions isolate this: a hidden figure is maximally complex until recognition collapses it; an
ambiguous figure oscillates between models; an impossible figure looks simple until serial processing tries
and fails to build one consistent interpretation. "How complex is a contradiction?" has a precise answer —
low in description length, unbounded in the inference cost of closure — that only a time-extended account
can give (§2.4).

The three claims converge on a single reframing and a single experiment. The reframing: complexity is not a
scalar, nor even one vector of image features, but a **profile indexed by processing stage, operation, and
observer model**, with a fast affective channel and a slow interpretive channel that dissociate. The
experiment (§4) targets the affective channel's dynamics, because that is where the reframing makes its
riskiest, most useful prediction: that the stress of a disfluent scene is *transient* — refunded at
perceptual closure — when a gestalt is available, and *enduring* when the disorder is baked into low-level
statistics with no gestalt to close. Confirming this would establish the stage-and-operation view as a
measured fact, and would tell a computational programme exactly what an image-only complexity measure can
and cannot be for: not a detector of complexity, but a model of the enduring, low-level, stress-relevant
residual.

---

## 2. Background and theory

### 2.1 Three traditions, three partial measures

Work on visual complexity divides into three families that rarely cite one another, and each captures a
real part of the construct while mistaking it for the whole.

The **image-statistics** family, most fully developed by Rosenholtz and colleagues, operationalises clutter
as multiscale feature congestion — pooled local variability of colour, luminance, and orientation across a
pyramid — with subband entropy and edge density as relatives, and grounds them mechanistically in the
summary-statistic (texture) representation of peripheral vision. These measures are firm where they were
built to be firm: they predict visual-search difficulty and crowding. They are, by construction, blind to
the observer.

The **perceptual-dimensions** family asks people directly and lets the structure emerge. It repeatedly
recovers *more than one* dimension — quantity, variety, and organisation/symmetry among them — inherits
Berlyne's collative variables (in which complexity is one of several arousal-raising properties alongside
novelty, incongruity, and order), and finds consistently that subjective complexity diverges from any single
objective proxy. Recent computational work in this spirit decomposes perceived complexity into structure,
colour, and surprise — an explicit move to a component vector.

The **structural-semantic** family locates complexity in the parse. Scene-grammar research distinguishes
large, positionally predictive **anchor objects** from small, surface-populating **local objects**, and
separates syntactic violations (wrong position) from semantic ones (wrong identity). This is the level at
which the two everyday clutters — a disarrayed furniture layout versus a junk-covered surface — are finally
distinguishable: the first is anchor-level syntactic disorder, the second is high local-object density. They
feel incommensurable because they are different constructs at different levels of a hierarchy.

Running beneath all three, the environmental-aesthetics tradition has always paired complexity with its
antidote — coherence — scoring a scene on complexity *and* legibility, so that complexity without coherence
is aversive and complexity with coherence is engaging. Order, in this tradition, is not the absence of
complexity but a separate axis that can cancel its cost.

### 2.2 Order is compressibility, and compressibility is model-relative

The tempting formalisation of "regimented versus random" is information-theoretic: order is compressibility;
a regular arrangement has a short description, a random one does not, even at equal element count. This is
correct as far as it goes, and it is exactly where the observer re-enters. Algorithmic (Kolmogorov)
complexity is defined only relative to a description language or universal machine, and the quantity relevant
to a viewer is the *conditional* complexity — the cost of describing the scene *given the model the viewer
already holds*. A scene that looks maximally disarrayed has low conditional complexity for the observer whose
model explains it.

Two literatures make this rigorous. **Effective complexity** separates a description into its regularities
and its incidental randomness and explicitly requires a judgment — a model — of which features count as
regularity; there is no model-free fact about how much of a desk is signal. And **compression-progress**
accounts make subjective interest and beauty relative to the observer's current compressor: what is
interesting is what the present model is in the act of learning to compress. Perceived order simply *is*
compression by this observer's model, and the cognitive name for the model is expertise: since Chase and
Simon we have known that domain experts encode scenes into chunks that novices lack and therefore see
structure where novices see noise.

### 2.3 The deepest relativity: activity projects structure

Expertise as *recognition* is not yet the strongest form of the claim. The strongest form treats the viewer
as an **agent**. People arrange the world so its layout supports the doing, and then read the layout through
the activity it was arranged for. A chef's mise en place is a spatial encoding of the recipe's action
sequence: the arrangement *is* the plan, offloaded into space, serving at once as memory, as next-action
cue, and as choice simplification. To a co-practitioner it is ordered and legible; to a visitor it is
surprising disarray. This is the intelligent use of space — arranging the environment to simplify
perception, choice, and computation — and its perceptual complement is professional vision, in which a
practice trains its members to see structure and relevance where outsiders cannot. What counts as order
versus clutter is therefore a **relation between a layout and an activity, mediated by whether the viewer
holds the practice**. Clutter, in this deepest sense, is residual that does no activity-work for *this*
agent — either because it encodes nothing, or because the viewer lacks the practice that would parse it.

### 2.4 Complexity is computed at two stages; the illusions isolate them

The observer- and activity-relativity of complexity are not static caveats; they arrive at a particular
*time*. Perception runs from a fast, feed-forward stage (~100–150 ms) that delivers summary statistics —
edge and spatial-frequency energy, contrast, colour variety, the quantities the image measures approximate —
to a slower, model-based stage that segments, recognises, retrieves a schema, and re-describes the scene as
"known structure plus residual." The optical illusions are the experiments that hold the image fixed and
vary only this processing, and they reveal not one hidden complexity but three.

**Emergence.** A hidden figure — Gregory's Dalmatian, a Mooney face, the zebra — is high in low-level entropy
and low in complexity *given* the object model, and the felt complexity is the transient, pre-recognition
residual that collapses discontinuously at recognition. **Multistability.** An ambiguous figure — Rubin's
vase, the Necker cube — is low in image complexity yet oscillates between equally good models with
characteristic dwell times and hysteresis; here the complexity is interpretive multiplicity, measured in the
*dynamics* of switching, not in the image. **Contradiction.** An impossible figure — an Escher staircase,
the Penrose triangle — is a clean line drawing of very low description length that *looks* simple until
serial processing tries to integrate its locally consistent parts into one globally consistent model and
cannot.

The contradiction case answers a question the scalar view cannot even pose. How complex is a contradiction?
Minimal in description length, maximal in inference cost. The right formal handle is **logical depth** — the
computation time to generate an object from its shortest description, as distinct from the length of that
description. A Penrose triangle is short to describe and unbounded to unfold; its felt complexity is
prediction error that never resolves. Description-length complexity and inference complexity, ordinarily
correlated, are here driven to opposite extremes in the same picture — the clearest possible demonstration
that complexity is a property of the operation, not of the image.

### 2.5 Two channels: cognitive effort and affective stress, on different clocks

There is a temptation, having gone this far, to conclude that complexity is *entirely* late and relative —
that once the model closes, the cost is gone. This over-rotates. A second, fast route runs in parallel, and
it is affective rather than interpretive. Images that depart from natural 1/f spatial-frequency statistics —
dense gratings, over-detailed clutter — are physiologically costly and aversive independent of meaning;
affect can precede or bypass full cognition; and rapid affective appraisal of environments is the core of
psychoevolutionary accounts of stress and restoration. So a scene can be fully understood — recognised,
even navigated by an expert — and still be *stressful*. Complexity therefore has at least two outputs on two
clocks: a **cognitive-effort** channel (legibility, search cost, driven by the model and the activity, slow
and revisable) and an **affective-stress** channel (comfort, arousal, driven partly by image statistics,
fast and sticky). Imposing semantic or activity order operates on the first; it can make a scene legible
without making it comfortable.

Whether the affective cost is refunded, however, has a time course, and this is the paper's central
empirical claim. Processing fluency is dynamic, and affect tracks its *change*, not its level: a gain in
fluency is hedonically marked, which is why the "aha" of perceptual closure is not merely relief but
pleasure. Closure is a datable event, with an electrophysiological signature ~230–300 ms after the
organising input. Putting the fast affective route together with the dynamics of fluency yields a precise,
branching prediction. When a gestalt is **available** to close — a hidden figure, an ambiguous-then-cued
scene, a cluttered but recognisable room — an initial disfluency-driven stress response is **refunded** at
closure, sometimes overshooting into the pleasure of the aesthetic aha; the stress is transient. When there
is **no gestalt to close** — disorder baked into low-level statistics, with no organising model available —
recognition changes nothing and the stress **endures**. Transient versus enduring stress is thus
*diagnostic* of the kind of complexity, and it reconciles the two halves of §2.5: semantic order refunds the
affective cost exactly when a gestalt is available, and fails to when the cost is low-level and irresolvable.

This is the hinge from theory to experiment. The prediction is riskier and more useful than the qualitative
observation that clutter is unpleasant, and — as we show next after establishing that the measures diverge —
it has not been directly tested.

---

## 3. Study 1 — The measures diverge, and their validity is operation-dependent

### 3.1 Rationale

If complexity were a single image property, the many measures that estimate it should agree with one
another and, jointly, with human judgment. Study 1 tests this on a large, human-rated benchmark, and asks a
sharper question than "do the measures predict human ratings" — namely, *does the best-predicting measure
depend on the domain*, as the operation-indexed view requires.

### 3.2 Method

**Dataset.** We used SAVOIAS, a crowdsourced visual-complexity dataset of 1,420 images across seven
categories (Scenes, Interior Design, Objects, Art, Suprematism, Advertisement, Visualizations), each carrying
a per-image complexity score derived from human pairwise comparisons (global ranking, 0–100).

**Measures.** On every image, size-normalised to 256 × 256 px, we computed eight measures spanning the
research traditions of §2.1: edge density; JPEG size (lossy compression, fixed quality) and PNG size
(lossless); grayscale Shannon entropy; subband entropy (summed detail-coefficient entropy of a three-level
pyramid); quadtree leaf count (homogeneous blocks under a variance threshold); distinct-colour count; and
contrast energy (mean local luminance standard deviation pooled over three scales). Full definitions are in
the Measures section (Methods 2.3.1). We computed Spearman correlations of each measure with the human score,
per category and pooled, and the inter-measure correlation matrix.

### 3.3 Results

The eight measures were far from redundant: pooled inter-measure correlations ranged from ρ = 0.22 (colour
count vs subband entropy) to 0.93 (edge density vs JPEG size), with colour count nearly orthogonal to the
entropy/texture family and grayscale entropy only weakly tied to the structural measures (Figure 3). "Visual
complexity," operationalised eight defensible ways, is three or four weakly related things.

The decisive result concerns validity against human judgment (Figure 2). No measure was best everywhere, and
the best measure *changed with the domain*: JPEG compression best matched human complexity for Interior
Design (ρ = 0.81), Advertisement (0.78), and Visualizations (0.74) — designed artifacts whose complexity is
non-redundant structure per unit area; colour count won for Suprematism (0.85) and Scenes (0.63) — where
judgment rides on palette and element variety; edge density won for Art (0.59); and for **Objects no measure
exceeded ρ = 0.43**, because the perceived complexity of a single object is semantic, not image-statistical.
The concrete face of this divergence (Figure 4): a black-and-white zebra sits at the 96th percentile of edge
density and 89th of subband entropy yet was rated 16/100 by humans, while a few-element Suprematist
composition sits at the 96th percentile of colour and the 5th of edge density and was rated 43/100 — two
images, opposite verdicts depending on which measure one trusts.

### 3.4 Interpretation

Each measure succeeds exactly where the operation it was built to predict governs the human judgment, and
fails where a different operation dominates. Compression tracks perceived complexity of designed artifacts
because their value *is* packed non-redundant structure; colour variety tracks it for abstract art because
there is little else to go on; nothing tracks it for objects because that judgment waits on recognition,
above where image statistics reach. "How complex is this image" has no domain-general answer; the domain
fixes the operation, and the operation fixes the measure. This is the empirical form of claim (i), and it
motivates treating an image-only measure not as *the* complexity of a scene but as a model of one operation's
cost — which sets up the question of *which* operation an image measure is actually good for, answered for
the affective operation in Study 2.

---

## 4. Study 2 — Does perceptual closure refund the stress? (design and predictions)

Study 1 shows an image measure is not a domain-general complexity detector. Study 2 asks what one *is* good
for by testing the theory's riskiest claim: that the affective cost of a disfluent scene is refunded at
perceptual closure when a gestalt is available and endures when it is not, and that an image measure predicts
the enduring component specifically. Because no dataset can settle a within-trial affective *trajectory*, this
is a time-resolved psychophysiology experiment. We present it as a pre-registered design with explicit
predictions; results are described in §5 as the outcome we expect and are prepared to be wrong about.

### 4.1 Design overview

Within-subjects, repeated-measures, with continuous psychophysiology reduced twice — locked to stimulus
onset and to the participant's recognition response — because closure latency varies trial to trial and
onset-locking alone would smear the transition of interest.

**Stimulus classes.** (1) *Fluent-simple* control: clear, ordered, low complexity. (2) *Ordered-complex*:
high complexity, high coherence. (3) *Cluttered-resolvable*: high complexity, low order, but a recognisable
scene. (4) *Hidden-figure/Mooney*: two-tone images that are noise-like until they snap — the cleanest datable
closure. (5) *Statistically-baked-in*: phase-scrambled scenes (identical amplitude spectrum, structure
destroyed) and 1/f-departing gratings/filtered noise — no gestalt to close. Two matched comparisons carry the
key contrasts: intact scene versus its phase-scramble (same power spectrum; one resolves, one cannot), and
ordered-complex versus cluttered equated on the low-level image battery of Study 1 (matched complexity;
differ only in order).

**Within-image refund test.** The tightest control holds the image constant and manipulates only whether
closure is *available*: a degraded Mooney is shown (disfluent); on cued trials its grayscale solution is
briefly presented, installing the percept; the identical degraded image is then re-shown and now resolves
instantly (one-shot perceptual learning). The same image, pre-cue versus post-cue, isolates the refund with
every low-level property held constant.

### 4.2 Procedure

Each trial: jittered fixation (1–2 s); stimulus for 10–12 s, during which the participant presses a key at
the instant of recognition ("it clicked"), timestamping closure; stimulus offset; continuous ratings of
peak discomfort, relief/aha intensity, confidence, and a recognition check; jittered inter-trial interval.
Unsolvable catch stimuli, on which no veridical closure is possible, provide a baseline for spurious presses
and guard against a demand to "press aha." Approximately 120 trials (five classes × ~24), blocked with
breaks, counterbalanced, with luminance, contrast, and size equated.

### 4.3 Measures

The dependent measures are specified in full in the Methods (2.3). In brief: **facial EMG** over corrugator
supercilii (negative affect/effort; the primary DV) and zygomaticus major (positive affect); **skin
conductance**, decomposed into tonic level and phasic responses, as a valence-free arousal index that
separates aroused-but-refunded from sustained trajectories; **pupillometry** as a second arousal/effort index
(with luminance equated to control the light reflex, and the recognition-locked change emphasised);
**recognition latency and accuracy**, the closure clock and its validation; and continuous **self-report** of
discomfort, relief, and confidence. In the extended tier, **EEG** provides the perceptual-closure negativity
and induced gamma as neural closure markers, timing the event independently of the motor press. Four derived
indices operationalise the constructs: *initial stress* (corrugator/phasic SCR, 0–2 s post-onset), *refund
magnitude* (corrugator peak minus post-recognition asymptote, with the parallel zygomaticus rise), *enduring
index* (corrugator/tonic SCL in the final 2–3 s relative to baseline), and *stress AUC* (integrated
corrugator across the trial).

### 4.4 Predictions

- **P1 (initial stress).** Classes 3–5 raise corrugator, SCR, and pupil within ~2 s of onset relative to the
  fluent control; classes are indistinguishable in this early window.
- **P2 (dissociation).** At matched low-level complexity, cluttered (disordered) evokes greater initial and
  sustained corrugator/SCR than ordered-complex — stress tracks disorder, not richness.
- **P3 (refund).** For gestalt-resolvable classes (3, 4), corrugator falls sharply at the recognition event,
  often undershooting baseline, with a concurrent zygomaticus rise and self-reported relief/aha.
- **P4 (endurance).** For statistically-baked-in stimuli (5), no closure occurs and corrugator/tonic SCL
  remain elevated across the trial.
- **P5 (the crossover; confirmatory).** A stimulus-class × time-window interaction: resolvable and baked-in
  start equally aroused and diverge after the closure latency (Figure 5). This is the decisive test.
- **P6 (refund scales with aha).** Trial-level, the corrugator drop at recognition correlates with reported
  relief/aha intensity.
- **P7 (image measure predicts endurance, not refund).** The Study-1 image battery regressed onto the derived
  indices predicts the *enduring index* but not the *refund magnitude* — an image-only measure models the
  sustained affective residual, not the resolvable transient.

Two bolt-on manipulations extend the design without changing its logic: an *activity/expertise frame*
(identical cluttered scenes framed as a practitioner's task versus neutral), predicted to supply order and
lower the stress response for those holding the practice; and *cue-timing* (early versus late installation of
the Mooney solution), predicted to reduce stress AUC when closure comes earlier — dosage evidence that
closure, not elapsed time, does the refunding.

---

## 5. Anticipated results and discussion (assuming the predictions obtain)

We write this section in the conditional it deserves: it describes the pattern the theory predicts and the
conclusions we would be licensed to draw *if* it is observed, and it names in advance what would falsify the
account.

### 5.1 The expected pattern

If P1–P7 hold, the headline is a single figure (Figure 5): two disfluent trajectories that rise together to a
common peak of corrugator activity and sympathetic arousal, then part company at the moment of recognition —
the resolvable trace dropping steeply, undershooting into a brief negative-going relief consistent with the
aesthetic aha, and settling near or below baseline; the baked-in trace holding its elevation to the end of
the trial. The fluent control stays flat and low throughout. The within-image Mooney contrast shows the same
refund with the image held physically constant: the identical degraded picture that stressed the observer
before the solution was installed no longer does so after, the difference carried by the corrugator drop and
the relief report. And the dissociation contrast shows cluttered and ordered-complex scenes, matched on the
image battery, separating on stress — disorder, not richness, doing the work.

### 5.2 What it would establish

**That the transient/enduring distinction is a measured fact, not a metaphor.** The same subjective word,
"stressful," would be shown to name two physiologically distinct trajectories distinguished by a single
property — whether a gestalt is available to close — with the affective system marking the *change* in
fluency at the closure event. This makes concrete the claim that complexity is time-extended and that the
affective channel runs on its own clock: understanding refunds the cost exactly when there is a model to
close, and not otherwise.

**That clutter-stress and complexity are dissociable along the order axis.** P2 would show that the aversive
component of a complex scene is its disorder, not its quantity — reconciling the inverted-U of preference
(rich, ordered complexity is engaging) with the monotonic aversiveness of clutter (rich, disordered
complexity is not), and giving the environmental-psychology pairing of complexity with coherence a
mechanistic, within-trial grounding.

**That an image-only complexity measure has a precise and limited job.** P7 is the result that speaks to the
computational programme. An image measure, shown in Study 1 to be a poor domain-general predictor of
*cognitive* complexity, would here be shown to be a *good* predictor of the enduring affective residual — the
low-level, statistically baked-in discomfort that no recognition removes. That is exactly the channel that
matters for stress, restoration, and well-being in built environments. The measure is therefore not a clutter
detector; it is a model of the sustained affective cost, and it should be used, and validated, as such — its
residual against a viewer's judgment being not error but a *measurement* of the resolvable, model-relative
component it cannot see.

### 5.3 Consequences for how complexity should be represented

Together the two studies argue that complexity should be represented as a **profile indexed by processing
stage, operation, and observer model**, not as a scalar and not as a single feature vector. The early,
image-computable facets (surface density, variety, spectral departure) are one column, validated against fast
crowd judgment and against the affective-stress channel; the late, model-relative facets (semantic
incongruity, legibility-to-observer, activity-relative order) are another, validated behaviourally — by
recognition-driven drops, bistable switch dynamics, contradiction-detection latency, and expert–novice and
activity-frame differences — and *not* against pixels. An image model such as a vision tagger occupies the
first column only, and its honest role is to report the enduring affective residual and to expose the
late-column residual as a measurement rather than absorb it as noise. The optical illusions, on this view,
are not curiosities at the edge of the topic but the isolating experiments at its centre, because each holds
the image fixed and varies exactly one operation.

### 5.4 What would falsify the account

The account is refutable. If the resolvable and baked-in trajectories do *not* diverge at closure — if
recognition fails to reduce corrugator/arousal for resolvable stimuli, or reduces it equally for baked-in
ones — the transient/enduring distinction collapses. If cluttered and ordered-complex scenes matched on the
image battery evoke equal stress, the dissociation claim fails and disorder is not doing independent work. If
the image battery predicts the refund magnitude as well as, or better than, the enduring index, then an
image measure is *not* specifically a model of the sustained channel and P7's programmatic conclusion does
not follow. And if the within-image Mooney refund does not appear — if installing the solution leaves the
affective response unchanged — then closure is not the operative variable and some confound of time or
exposure is. We regard these as live possibilities and have powered and pre-registered the design to detect
their absence.

### 5.5 Limitations and scope

The design tests scenes and canonical hidden/impossible figures; generalisation to dynamic and embodied
settings — where a space is legible partly because one *acts* in it — is future work, as is the full
individual- and culture-level variation in the model M that sets what resolves. The activity-frame
manipulation is a first probe of the enactive claim, not a full test of it. And the affective channel we
isolate is one of several downstream operations complexity feeds; search, memory, and preference each deserve
the same time-resolved, operation-indexed treatment. The contribution here is to have shown, in one case,
that treating complexity as operation-indexed, model-relative, and time-extended is not a philosophical
gloss but a source of concrete, falsifiable predictions — and to have supplied the measures, the divergence
evidence, and the experiment that turn the reframing into a research programme.

---

## Figures

**Figure 1. Three everyday cases that break the single-number view of complexity.**
(A) A monochrome zebra in grass — high edge/texture energy, yet rated low in complexity once recognised as one
familiar thing. (B) A few chairs at odd angles with one overturned — sparse and low-density, yet disordered
arrangement reads as clutter. (C) A Suprematist composition — little texture but high colour/variety, reading
as elaborate. Panels A and C are SAVOIAS images (Objects #50; Suprematism #84); panel B is an original
schematic.

**Figure 2. The best-matching measure flips by domain.** Spearman ρ between each of eight image measures and
SAVOIAS human complexity ratings, by category (red box = best measure per category). No measure is best
everywhere; Objects has no image measure above ρ = 0.43.

**Figure 3. The measures are not one thing.** Pooled inter-measure Spearman correlations (0.22–0.93); colour
count is nearly orthogonal to the entropy/texture family.

**Figure 4. Same image, opposite verdicts.** Two SAVOIAS images where the measures rank complexity oppositely
(percentile ranks shown): a texture-maxed zebra rated low by humans, and a colour-rich but texture-poor
composition.

**Figure 5. Predicted stress trajectories (Study 2).** Corrugator EMG / arousal across a trial for
gestalt-resolvable disorder, statistically-baked-in disorder, and a fluent control. Both disfluent classes
peak together; at the recognition event the resolvable trace is refunded (undershooting into relief) while
the baked-in trace endures. The class × time-window crossover is the confirmatory prediction (P5).

---

## References (to be completed at submission)

Beatty, J. (1982). Task-evoked pupillary responses, processing load, and the structure of processing
resources. *Psychological Bulletin.*
Bennett, C. H. (1988). Logical depth and physical complexity. *The Universal Turing Machine.*
Berlyne, D. E. (1971). *Aesthetics and Psychobiology.*
Boucsein, W. (2012). *Electrodermal Activity* (2nd ed.).
Cacioppo, J. T., Petty, R. E., Losch, M. E., & Kim, H. S. (1986). Electromyographic activity over facial
muscle regions can differentiate the valence and intensity of affective reactions. *JPSP.*
Chase, W. G., & Simon, H. A. (1973). Perception in chess. *Cognitive Psychology.*
Donderi, D. C. (2006). An information theory analysis of visual complexity and dissimilarity. *Perception.*
Fridlund, A. J., & Cacioppo, J. T. (1986). Guidelines for human electromyographic research. *Psychophysiology.*
Gell-Mann, M., & Lloyd, S. (1996/2004). Effective complexity. (See Ay, Müller & Szkoła, 2010.)
Goodwin, C. (1994). Professional vision. *American Anthropologist.*
Graf, L. K. M., & Landwehr, J. R. (2015). A dual-process perspective on fluency-based aesthetics. *PSPR.*
Graf, L. K. M., & Landwehr, J. R. (2017). Aesthetic pleasure versus aesthetic interest. *Frontiers in Psychology.*
Gregory, R. L. (1970). *The Intelligent Eye.*
Kaplan, S. (1987). Aesthetics, affect, and cognition: Environmental preference from an evolutionary
perspective. *Environment and Behavior.*
Kirsh, D. (1995). The intelligent use of space. *Artificial Intelligence.*
Kirsh, D., & Maglio, P. (1994). On distinguishing epistemic from pragmatic action. *Cognitive Science.*
Leopold, D. A., & Logothetis, N. K. (1999). Multistable phenomena. *Trends in Cognitive Sciences.*
Mathôt, S. (2018). Pupillometry: Psychology, physiology, and function. *Journal of Cognition.*
Muth, C., & Carbon, C.-C. (2013). The aesthetic aha: On the pleasure of having insights into Gestalt.
*Acta Psychologica.*
Oliva, A., Mack, M. L., Shrestha, M., & Peeper, A. (2004). Identifying the perceptual dimensions of visual
complexity of scenes. *Proceedings of the Cognitive Science Society.*
Pieters, R., Wedel, M., & Batra, R. (2010). The stopping power of advertising: Measures and effects of
visual complexity. *Journal of Marketing.*
Reber, R., Schwarz, N., & Winkielman, P. (2004). Processing fluency and aesthetic pleasure. *PSPR.*
Rosenholtz, R., Li, Y., & Nakano, L. (2007). Measuring visual clutter. *Journal of Vision.*
Saraee, E., Jalal, M., & Betke, M. (2020). SAVOIAS: A diverse, multi-category visual complexity dataset.
Saxbe, D. E., & Repetti, R. (2010). No place like home: Home tours correlate with daily patterns of mood
and cortisol. *Personality and Social Psychology Bulletin.*
Schmidhuber, J. (2009). Driven by compression progress. *Anticipatory Behavior in Adaptive Learning Systems.*
Stamps, A. E. (2004). Mystery, complexity, legibility and coherence: A meta-analysis. *Journal of
Environmental Psychology.*
Võ, M. L.-H., Boettcher, S. E. P., & Draschkow, D. (2019). Reading scenes: How scene grammar guides
attention and aids perception. *Current Opinion in Psychology.*
Wilkins, A. J. (2016). A physiological basis for visual discomfort: Application in lighting design.
*Lighting Research & Technology.* (See also O'Hare & Hibbard, 2011, Visual discomfort and natural image
statistics.)
Winkielman, P., & Cacioppo, J. T. (2001). Mind at ease puts a smile on the face. *JPSP.*
Zajonc, R. B. (1980). Feeling and thinking: Preferences need no inferences. *American Psychologist.*
