# Deep processing, task-use, and the illusions: complexity as a *process profile*

### Companion note to the clutter review · 2026-07-30

*Answering three linked questions raised in discussion: what the "deep processing" concretely is, why anyone
needs a complexity measure and in what tasks (and whether it's been written about), and — the sharp
case — how complex a contradiction is. The through-line: perceived complexity is not a property of an
image but of the **operation that interprets it over time**. Optical illusions are the experiments that
prove this, because they hold the image fixed and vary only the processing.*

## 1. What the "deep processing" actually is

The shallow stage is feed-forward and fast (~100–150 ms): summary statistics — edge/spatial-frequency
energy, contrast, colour variety — the quantities all eight SAVOIAS measures approximate. The **deep
stage** is model-based scene interpretation, and concretely it is a sequence of operations:

1. **Segment & parse** — carve the field into objects, surfaces, and their relations (scene grammar:
   anchor vs local objects).
2. **Recognise & retrieve a schema** — match to stored object/scene models; this yields *gist* plus a set
   of expectations about what is where.
3. **Re-describe (compress)** — rewrite the scene as "known layout + residual." The **residual** — what the
   model does *not* explain — is what still feels complex.
4. **Predict & guide** — use the schema to predict locations (search guidance), afford actions, anticipate
   the next fixation.
5. **Evaluate closure** — check whether one globally-consistent model fits. If yes → coherence/legibility;
   if the fit is unstable or impossible → the phenomena in §3.

This is why the zebra collapses from 96th-percentile texture to human-rated 16: step 3 re-describes a
high-entropy image as "one zebra," and the residual is small. Your organised desk is the same move with a
private schema. Deep processing *is* the model-relative compression the review argues for — made into a
pipeline of operations, each of which has a cost.

## 2. Why anyone needs a complexity measure — concretely, and yes it's been written about

Nobody wants "complexity" as such; they want a cheap predictor of a specific operation's cost or outcome.
The literature is organised by which operation:

- **Advertising / attention.** Pieters, Wedel & Batra ([*The Stopping Power of Advertising*, J. Marketing
  2010](https://journals.sagepub.com/doi/10.1509/jmkg.74.5.048)) is the cleanest case and directly supports
  the "kind of complexity × task" thesis: they split **feature complexity** (visual busyness) from **design
  complexity** (structured, ordered elaboration) and show they have *opposite* effects — feature complexity
  hurts attention-to-brand and attitude, design complexity *helps* attention-to-ad and comprehension.
  Same scene, two complexities, two tasks, opposite signs. Use: media buyers and designers optimise ad
  layout against eye-fixations, recall, and attitude.
- **Web / UI first impressions & performance.** Tuch et al. ([*Visual complexity of websites: effects on
  experience, physiology, performance, and memory*,
  2009](https://www.sciencedirect.com/science/article/abs/pii/S107158190900055X)) and the first-impression
  work (complexity + prototypicality drive sub-second aesthetic judgments; [Google Research on visual
  complexity and prototypicality](https://research.google/pubs/the-role-of-visual-complexity-and-prototypicality-regarding-first-impression-of-websites-working-towards-understanding-aesthetic-judgments/))
  tie complexity to appeal, trust, findability, arousal, and memory. Use: predict conversion/appeal;
  optimise layout.
- **Data visualisation / maps.** Complexity predicts decision efficiency and error in reading tasks
  ([visual complexity × task difficulty in cluster-separation tasks,
  2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10604666/)). Use: legibility engineering (Tufte's
  data-ink is a complexity-minimisation rule).
- **Search / safety / HMI.** Clutter predicts visual-search time, target and hazard detection, and
  workload — the origin of Rosenholtz's clutter program (cluttered displays, roadside advertising, cockpit
  HMIs). Use: safety-critical display and signage design.
- **Environment / architecture (our program).** Complexity gated by **coherence** predicts preference,
  restoration/stress recovery, and wayfinding legibility (Kaplan; Berto's restorative environments; Stamps'
  meta-analysis). Use: design preferred, restorative, navigable space — the CNfA/ZHA use case itself.
- **Scene memory / gist.** Complexity predicts change-blindness, memory load, and gist-extraction speed.

The **mechanism** that makes a complexity measure predictive is written about too, and it names the deep
processing directly. **Processing fluency** (Reber, Winkielman & Schwarz) says the *ease* of the
interpretive operation is itself felt, and drives preference, confidence, and truth judgments — so a
complexity measure predicts an outcome exactly insofar as it predicts fluency of the relevant operation.
**Predictive-processing / prediction-error** accounts (perception as hypothesis testing, Gregory; Bayesian
brain) make this quantitative: the residual after the best model *is* prediction error, which is the cost
the system works to minimise. In both, "complexity" is not in the stimulus — it is the effort or error of
the operation the viewer is running.

## 3. The illusions: hold the image fixed, vary only the processing

Because these accounts locate complexity in the operation, the decisive evidence is stimuli where the image
is constant and only the processing changes. There are three families, and they are three *different*
complexities.

**Emergence (hidden figures).** Gregory's Dalmatian, the zebra: maximal low-level entropy that reorganises
into a simple percept the instant the model locks. Perceived complexity **drops discontinuously with
recognition** — the "aha." Formally: high description-length of the pixels, low description-length *given*
the object model. The complexity you feel is the *pre-recognition residual*, and it is transient.

**Multistability (ambiguous figures).** Rubin's vase/faces, the Necker cube, "My Wife and My
Mother-in-Law," duck/rabbit: few contours, low image complexity, yet the percept **oscillates** between
two-or-more equally good models, with characteristic dwell times and hysteresis
([bistable perception & its predictive-coding account](https://journals.plos.org/ploscompbiol/article?id=10.1371%2Fjournal.pcbi.1005536);
[Leopold & Logothetis, multistable phenomena](https://pmc.ncbi.nlm.nih.gov/articles/PMC7110285/)). Here the
complexity is **interpretive multiplicity** — the number and instability of viable models — and it is
measured in the *dynamics* (switch rate, dwell distribution), not in the image at all.

**Contradiction (impossible figures).** Escher's staircase, the Penrose triangle: clean line drawings, very
low edge density and description length — they look *un*complex — until **serial** processing tries to
integrate the locally-consistent parts into one globally-consistent 3-D model and cannot. Every local patch
compresses trivially; no global model closes.

## 4. How complex is a contradiction?

Answer: **minimal on image/description complexity, maximal on inference complexity** — and the two are
formally distinct quantities, which is the whole point.

The right formal handle is **Bennett's logical depth**: the *computation time* to generate an object from
its shortest description, as opposed to the length of that description (Kolmogorov complexity). A Penrose
triangle has a *short* description (three bars, three corners) — low Kolmogorov complexity — but the
process of building a consistent depth model runs, revisits, and **fails to halt on a stable
interpretation**: high logical depth, in the limit non-terminating. Effective complexity + logical depth
(Gell-Mann & Lloyd; [Ay, Müller & Szkoła](https://arxiv.org/abs/0810.5663)) is exactly the pairing that
separates "short to describe" from "expensive to unfold."

So a contradiction is the extremal demonstration of the thesis: it drives image-complexity to a floor and
interpretive/closure-complexity to a ceiling, at the same time, in the same picture. Its felt complexity is
**pure prediction error that never resolves** — the model keeps re-deriving and never reaches closure. In
predictive-processing terms, unresolvable free energy. In phenomenology, the specific *unsettledness* of an
impossible figure, which is different from the *busyness* of a cluttered kitchen and different again from
the *flicker* of an ambiguous figure. Three distinct feelings, three distinct complexities, one of which
(the contradiction) has essentially zero image-statistical footprint.

## 5. Synthesis: complexity is a profile over operations, not a scalar or even one vector

The illusions force the strong form of the review's claim. Perceived complexity decomposes not only by
*content* (surface density, arrangement, variety, incongruity) but by **processing operation and stage**:

| Facet | What it is | Isolated by | Measured in | Stage |
|---|---|---|---|---|
| Image/description | pixel-statistical busyness | ordinary scenes | edge/entropy/compression | early, feed-forward |
| Model residual | disorder left after recognition | zebra, Dalmatian | pre- vs post-recognition drop | late |
| Interpretive multiplicity | number/instability of viable models | Rubin, Necker | switch rate, dwell, hysteresis | late, dynamic |
| Closure / consistency | can one global model be built | Escher, Penrose | integration time, contradiction detection | late, serial |
| Inference cost (logical depth) | steps to a stable interpretation | all of the above | RT, "aha" latency, effort | late, serial |

An image-only measure — including our tagger — reaches only the first row. The rest are **behavioural**:
they are read off reaction time, recognition-driven drops, bistable switch dynamics, contradiction-detection
latency, and expert/novice differences. This is the operational meaning of "complexity must be tied to the
operations that use it": the facets *are* operations, and they are measured by running them.

## 6. Consequence for the program

Our vector should be labelled not just by content dimension but by **(stage, operation, measurement
channel)**: the early/image facets are validated against fast crowd judgments and the SAVOIAS-style
measures; the late/process facets require *behavioural* readouts (RT, switch rate, aha-latency,
contradiction detection) and cannot be validated against pixels. The image tagger is, precisely, a model
of row 1 — and its residual against human judgment is a *measurement* of rows 2–5, not error. A publishable
contribution is exactly this: **an operation-and-stage-indexed taxonomy of visual complexity, with the
optical illusions as the isolating experiments and logical depth as the formal account of contradiction.**

## 7. The deepest reason we care: activity projects structure onto the world

Everything to here still treats the observer as a *perceiver*. The final turn treats them as an **agent**.
Order and clutter matter because, in activity, people **arrange the world so its layout supports the doing**,
and then read that layout through the activity it was arranged for. Mise en place is the exact case: a chef
lays out ingredients and tools as a spatial encoding of the recipe's action sequence — the arrangement *is*
the plan, offloaded into space. It serves at once as **memory** (each position a reminder of a step),
**next-action cueing** (reach without deliberation), and **choice simplification** (the right thing where
the hand expects it). To a co-practitioner the station reads as ordered, even elegant; to a visitor, as
surprising disarray. The shelf did not change — the *activity the viewer projects onto it* did. Order here
is neither low image entropy nor mere recognition; it is the degree to which the layout **encodes and
supports the activity**, read by someone who holds the practice.

This is your own framework, and it is the theory of the whole review: the **intelligent use of space**
(Kirsh 1995) — arranging the environment to simplify perception, choice, and computation — and **epistemic
action** (Kirsh & Maglio 1994) — acting on the world to make one's own mental work cheaper. Goodwin's
**professional vision** (1994) is the perceptual complement: a profession's practices train its members to
*see* structure where outsiders see noise. Together: what counts as order vs clutter is a **relation
between a layout and an activity, mediated by whether the viewer holds the practice.** Clutter is residual
that does no activity-work *for this agent* — because it encodes nothing, or because the viewer lacks the
practice to parse it. This closes the loop to the program's founding claim: reading a space as a *place* is
reading building-in-relation-to-occupant-**activity**, and the SPACE_USE attributes are already
activity-relative legibility. The image-only tagger is the **practice-blind null model**; its residual
against a practitioner's judgment measures the projected, activity-relative structure. Study consequence:
frame the *same* stimuli under different activities ("as a chef about to cook service" vs "as a diner
glancing in") and across expertise, with the pre-registered prediction that order/clutter judgments
**reverse with the activity frame**.

## 8. But the early channel is not disposable: syntactic complexity produces stress that meaning does not refund

The activity story could over-rotate into "it's all late and relative." It is not, and your correction is
the needed counter-weight: there is a **fast, pre-semantic route** on which syntactic complexity drives
**discomfort, arousal, and stress directly**, and later semantic or activity ordering **does not fully
dissolve that charge**. You can recognise the scene, hold the practice, know where everything is — and still
feel the load.

The evidence is firm. **Visual discomfort** rises as an image departs from natural **1/f spatial-frequency
statistics** — excess mid-high-frequency energy (stripes, dense clutter) is aversive, physiologically
costly, even headache- or seizure-inducing, and this is a low-level, meaning-independent response
([O'Hare & Hibbard, *Visual discomfort and natural image statistics*](https://www.researchgate.net/publication/46280345_Visual_discomfort_and_natural_image_statistics);
[Wilkins, *A physiological basis for visual discomfort*](https://journals.sagepub.com/doi/full/10.1177/1477153515612526)).
Affect can **precede or bypass full cognition** (Zajonc, "preferences need no inferences"), and rapid
affective appraisal of environments is the core of Ulrich's psychoevolutionary account of stress and
restoration — the autonomic verdict lands before the scene is fully interpreted. Berlyne's collative
complexity was, from the start, a theory of **arousal**, not of cognition.

So the two stages are not merely sequential-and-superseding; they are **two channels with different outputs
and different persistence**: an early *affective* channel (comfort/stress, driven by image statistics, fast,
sticky) and a late *interpretive* channel (legibility/effort, driven by the model and the activity, slow,
revisable). Imposing semantic order operates on the second; it can make a scene *legible* without making it
*comfortable*. An expert reads a cluttered ER fluently yet still carries the autonomic load; your organised-
to-you desk may still stress a visitor even after you explain the system — and, tellingly, may still tax
*you* affectively even as it serves you cognitively.

This adds an **output-channel dimension** to the taxonomy, orthogonal to stage-and-content: any complexity
facet can be scored on *cognitive-effort* and on *affective-stress*, and the two dissociate. It sharpens the
measurement mandate: the affective channel must be read from **autonomic and discomfort measures** (skin
conductance, discomfort ratings, gaze avoidance), not inferred from the cognitive one — and a scene's
"clutter" is incompletely characterised until both are reported. For the program this is not a complication
but a second, independently useful target: image-statistic clutter, largely useless as a domain-general
*cognitive* predictor (§2), may be a rather *good* predictor of the **affective** channel — which is exactly
the channel that matters for stress, restoration, and the wellbeing side of the CNfA agenda.

## 9. The time course of fluency: transient vs enduring stress

Fluency is dynamic, and affect tracks its **change**, not its level. Perception unfolds coarse-to-fine, and
the gestalt is a discrete **closure event with a latency** — a perceptual-closure negativity plus
gamma-band binding (~230–300 ms for ordinary figures, longer or trigger-dependent for degraded ones;
[neuroelectromagnetic correlates of perceptual closure](https://www.jneurosci.org/content/30/24/8342)) —
which, once it fires, **locks with hysteresis** (the Dalmatian can't be un-seen). Because the affective
system hedonically marks fluency *gains* ([processing fluency & aesthetic pleasure](https://www.researchgate.net/publication/8144801_Processing_Fluency_and_Aesthetic_Pleasure_Is_Beauty_in_the_Perceiver's_Processing_Experience);
[Eureka-effect EEG dynamics](https://pmc.ncbi.nlm.nih.gov/articles/PMC10321100/)), the **trajectory**
governs the affect: pre-closure low fluency → effort/arousal (transient stress); at closure the fluency
jumps and the change is marked positively (relief, the pleasure of the "aha") → the stress is **refunded**.

So for **gestalt-resolvable** disorder (hidden figures, ambiguous-then-cued scenes) stress is transient —
this is the case where meaning *does* refund it. But where there is **no gestalt to close** — the
1/f-departing "uncomfortable" images, dense stripes/clutter that drive sustained cortical load —
recognition changes nothing and the stress **endures**. Transient-vs-enduring is therefore **diagnostic**:
it distinguishes surface disorder that organises from structural disorder baked into the image statistics,
and it reconciles the two claims of §8 — semantic order refunds the affective cost exactly when a gestalt is
available, and fails to when the cost is low-level and irresolvable. (Contradiction is the third branch: the
gestalt never closes, so the unsettledness persists but is curiosity more than autonomic load, and is
disengageable.)

**Measurement.** Track affect over time (corrugator/zygomaticus EMG, pupil, skin conductance) while
manipulating gestalt-availability — a Mooney/two-tone that resolves vs a statistically-matched scramble that
never does — with recognition latency marking the predicted refund. Prediction: a corrugator spike then
relief at the closure latency for the resolvable case; sustained corrugator and SCR for the irresolvable
one. **For the program:** the affective facet gains a *time parameter* (peak, refund?, time-to-refund), and
the **enduring affective residual** — the non-resolvable statistical discomfort — is plausibly the one place
the image-only tagger is a strong predictor, making it the natural clutter measure for the **wellbeing /
stress** side of CNfA even though it is a poor domain-general *cognitive* complexity measure.

## Key sources

- Pieters, Wedel & Batra (2010), *The Stopping Power of Advertising* — https://journals.sagepub.com/doi/10.1509/jmkg.74.5.048
- Tuch et al. (2009), *Visual complexity of websites…* — https://www.sciencedirect.com/science/article/abs/pii/S107158190900055X
- Visual complexity & first impressions (Reinecke line / Google Research) — https://research.google/pubs/the-role-of-visual-complexity-and-prototypicality-regarding-first-impression-of-websites-working-towards-understanding-aesthetic-judgments/
- Complexity × task difficulty, cluster-separation (2023) — https://pmc.ncbi.nlm.nih.gov/articles/PMC10604666/
- Bistable perception, predictive-coding account — https://journals.plos.org/ploscompbiol/article?id=10.1371%2Fjournal.pcbi.1005536
- Leopold & Logothetis, multistable phenomena — https://pmc.ncbi.nlm.nih.gov/articles/PMC7110285/
- Effective complexity & logical depth (Gell-Mann & Lloyd; Ay, Müller & Szkoła) — https://arxiv.org/abs/0810.5663
- Foundational (no single URL): Gregory, *perception as hypothesis*; Reber, Winkielman & Schwarz, *processing fluency and aesthetic pleasure*; Penrose & Penrose (1958), *impossible objects*; Bennett, *logical depth*.
