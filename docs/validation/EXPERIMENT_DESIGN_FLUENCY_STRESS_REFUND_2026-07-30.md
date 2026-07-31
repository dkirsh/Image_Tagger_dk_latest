# Does the "aha" refund the stress? A time-resolved test of transient vs enduring disfluency stress

### Experimental design / pre-registration draft · 2026-07-30

*Tests the trajectory the literature predicts but has not directly measured: that a disfluent/cluttered
image evokes an initial autonomic-affective stress response, and that stress is **refunded at the moment of
perceptual closure** for **gestalt-resolvable** disorder but **endures** for **statistically-baked-in**
disorder — with clutter-stress and complexity dissociating along the order axis. Equipment-tiered so it can
run as a class-scale behavioural study or a full psychophysiology study. Predicted-results panel:
`fig_predicted_trajectories.png`.*

## 1. Hypotheses (confirmatory)

- **H1 — Initial stress.** Disfluent/cluttered/complex stimuli raise negative affect and arousal vs
  fluent controls, within ~2 s of onset: ↑ corrugator EMG, ↑ skin-conductance (SCR), ↑ pupil, ↓ zygomaticus.
- **H2 — Dissociation (clutter ≠ richness).** At **matched low-level complexity** (edge density, subband
  entropy, spectral energy), **disordered/incoherent** stimuli evoke more stress than **ordered/coherent**
  ones. Stress tracks *disorder/disfluency*, not richness.
- **H3 — Refund at closure.** For **gestalt-resolvable** stimuli, at the recognition event fluency jumps and
  affect shifts positive (↓ corrugator, ↑ zygomaticus, SCR/pupil settle) with self-reported **relief/aha**.
  Transient stress.
- **H4 — Enduring for baked-in.** For **statistically-baked-in** disorder (no gestalt to close), no closure
  event occurs and stress **persists** across the trial. Enduring stress.
- **H5 — The crossover (primary test).** A **stimulus-class × time-window interaction**: resolvable and
  baked-in start equally aroused, then diverge after the closure latency (resolvable drops, baked-in stays
  high). This crossover is the confirmatory result.
- **H6 — Refund scales with aha (trial-level).** The magnitude of the corrugator drop at recognition
  correlates with self-reported aha/relief intensity.

## 2. Design

Within-subjects, repeated-measures, time-resolved. Stimulus **class** is the core factor; a matched
**order** contrast tests H2; a **within-image** manipulation gives the tightest refund test.

### 2.1 Stimulus conditions (matched on low-level statistics where noted)

1. **Fluent-simple** (control) — clear, ordered, low complexity. Baseline.
2. **Ordered-complex** — high complexity, high coherence (design-complex / well-organised rich scene).
3. **Disordered-complex / cluttered (resolvable)** — high complexity, low order, but a *recognisable* scene
   (a genuinely cluttered real room). *Matched to #2 on edge density + subband entropy* → the H2 contrast.
4. **Hidden-figure / Mooney (resolvable, sharp closure)** — two-tone/Mooney images that are noise-like until
   they snap. The cleanest datable closure.
5. **Statistically-baked-in (irresolvable)** — **phase-scrambled** versions of the scenes (identical
   amplitude spectrum, structure destroyed → not recognisable) and **1/f-departing** stimuli (dense
   gratings / mid-high-SF-boosted noise, the "uncomfortable images"). No gestalt to close.

Key matched pairs: **intact scene vs its phase-scramble** (same power spectrum; one resolves, one cannot)
and **ordered-complex vs cluttered** (matched complexity; differ in order). Stimulus selection and matching
use the SAVOIAS-style measure battery we already built — that battery is the stimulus-control instrument.

### 2.2 The within-image refund test (Mooney induced-recognition)

The tightest control holds the image constant and manipulates only whether closure is *available*: show a
degraded Mooney (disfluent); on cued trials, briefly present its grayscale solution (installs the percept);
then re-show the **identical** degraded image, which now resolves instantly (one-shot perceptual learning /
hysteresis). Compare the same image **pre-cue vs post-cue** — every low-level property identical, only
resolvability changed. Predicted: post-cue shows the corrugator drop + zygomaticus rise + SCR settle + aha
report that pre-cue does not. (Design lineage: Mooney recognition; camouflage "insight" paradigms.)

## 3. Procedure — trial structure (built for a within-trial arc)

```
fixation (jittered 1–2 s)
stimulus ON  ── viewed 10–12 s  (long, to capture: onset arousal 0–2 s → variable closure → post-closure settle)
   participant presses "I see it / it clicked" at the moment of recognition   ← timestamps the closure event
stimulus OFF
ratings: discomfort/stress (0–100), relief/pleasure "aha" (0–100), "what did you see?" (recognition check), confidence
ITI (jittered 2–4 s)
```

Physiology is analysed **twice-locked**: to **stimulus onset** (initial stress) and, crucially, to the
**recognition button-press** (peri-closure), because closure latency varies trial to trial and must not be
smeared by onset-locking alone. Catch trials with **no solution** (unsolvable foils) guard against a demand
to "press aha."

## 4. Measures

- **Facial EMG — primary valence channel.** Corrugator supercilii (negative affect/effort) and zygomaticus
  major (positive affect) — the Winkielman-Cacioppo markers. Corrugator time-course is the headline DV.
- **Skin conductance (SCR).** Tonic arousal + phasic responses locked to onset and to recognition.
- **Pupillometry.** Effort/arousal; expect dilation during search, change at closure. *Confound:* pupil is
  light-driven — equate mean luminance across conditions and rely on the response-locked change.
- **Behaviour.** Recognition latency (button), recognition accuracy (what was seen).
- **Self-report.** Peak discomfort, relief/aha intensity, confidence; end-of-block preference.
- **Optional EEG (Tier 3).** Perceptual-closure negativity (~230–300 ms) + gamma at closure — the neural
  refund marker; and the Eureka-effect signature.

## 5. Analysis plan

- **H5 crossover (confirmatory):** stimulus-class (resolvable vs baked-in) × window (early 0–2 s vs late
  post-recognition) mixed-effects model on corrugator and SCR; predicted interaction = both high early,
  resolvable drops late, baked-in sustained. Pre-registered as the decisive test.
- **Within-image refund:** pre-cue vs post-cue (same image) on corrugator/zygomaticus/SCR + relief rating.
- **H2 dissociation:** ordered-complex vs cluttered, matched on the image battery → cluttered evokes more
  corrugator/SCR despite matched complexity (stress ⟂ richness).
- **H6:** trial-level correlation of corrugator-drop-at-recognition with aha rating (mixed model, random
  slopes by participant/stimulus).
- **Program link:** test whether the SAVOIAS-style **image measures predict the *enduring* (baked-in)
  affective component but not the *refundable* component** — i.e., the image-only tagger is a model of the
  sustained, wellbeing-relevant stress channel. This is the result that feeds the tagger's ledger.

Mixed-effects throughout (crossed random effects for participants and stimuli), pre-registered; multiverse
for EMG preprocessing choices.

## 6. Participants, power, stimuli

- **N ≈ 48** within-subjects for the psychophysiology (facial-EMG within-subject effects are ~medium;
  finalise by simulation on the crossover interaction). Class-scale behavioural pilot (Tier 1) can run
  N ≈ 30 on ratings + recognition RT alone.
- **Trials:** 5 conditions × ~24 = ~120, blocked with breaks; counterbalanced; luminance/contrast/size
  equated; ordered-vs-disordered matched via the measure battery.
- **Stimulus sources:** our `corpus_L6` + SAVOIAS (range and matching), Mooney two-tones generated from
  grayscale scenes, phase-scrambled controls (computed to preserve the amplitude spectrum), and
  1/f-departing gratings/filtered noise generated to spec.

## 7. Confounds & controls

Pupil light confound (equate luminance; response-lock). Motor artifact of the recognition press on EMG/SCR
(quiet/foot response; model the press; separate motor baseline). Demand for "aha" (unsolvable catch trials;
score genuine recognition accuracy, not just the press). Habituation/order (counterbalance, jittered ITI,
blocks). Mooney-difficulty individual differences (titrate difficulty; covariate). Blink/movement EMG
artifacts (standard filtering + rejection).

## 8. Secondary manipulations (bridges to the other threads)

- **Activity/expertise frame** (mise-en-place thread): frame identical cluttered scenes under a task ("you
  are the chef about to cook service") vs neutral; predict the frame supplies order and *reduces* the stress
  response for those holding the practice — the enactive prediction, testable here.
- **Cue-timing:** vary *when* the Mooney solution is given (early vs late); predict earlier refund lowers
  total stress (area-under-the-corrugator-curve) — dosage evidence that closure, not time, does the work.

## 9. Phased plan

1. **Tier 1 — behavioural (class-scale).** Ratings + recognition RT only, no physiology; establishes the
   discomfort→relief pattern and the dissociation. Cheap, fast, de-risks stimuli.
2. **Tier 2 — EMG + SCR + pupil.** The full within-trial arc and the crossover (H5) + refund (H3).
3. **Tier 3 — + EEG.** Adds the neural closure/refund marker.

## 10. Why it matters (payoff)

Confirms the transient-vs-enduring distinction as a **measured physiological fact**, establishes that
clutter-stress dissociates from complexity along the order axis, and — for the program — shows the
image-only clutter measure is a valid predictor of the **enduring, wellbeing-relevant affective residual**
(not of cognitive complexity). That result is what licenses using the tagger's clutter score for the
stress/restoration side of CNfA, and it is a clean, novel contribution: nobody has tracked the full
disfluency → closure → relief arc physiologically for scenes.
