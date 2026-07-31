# Methods — Measures

*Drop-in section for the theory + experiment paper. Two families: **stimulus measures** that characterise
and match the images, and **response measures** that index the fluency trajectory and its affective
consequences. The guiding principle is that the fast affective channels are acquired continuously and
reduced twice — locked to stimulus onset (the initial response) and locked to the participant's recognition
response (the closure event) — because closure latency varies from trial to trial and onset-locking alone
would smear the very transition the study is about. Citations are author–year; the reference list is
completed in the manuscript.*

## 2.3 Measures

### 2.3.1 Stimulus complexity measures (characterisation and matching)

Every image is described by a battery of eight computational complexity measures, each drawn from a
distinct research tradition and each computed on a common, size-normalised input (256 × 256 px; compression
measures at fixed dimensions and quality) so that values are comparable across images. The battery serves
two purposes: it quantifies the divergence among operationalisations reported in Study 1, and it is the
instrument used to **equate the ordered-complex and cluttered conditions on low-level complexity** so that
any difference between them is attributable to organisation rather than to richness.

The measures fall into four construct groups. **Texture/feature-density** measures — *edge density* (the
proportion of Canny-detected edge pixels), *contrast energy* (mean local luminance standard deviation pooled
across three spatial scales), and *subband entropy* (summed entropy of the detail coefficients of a
three-level image pyramid) — index the local, multiscale feature congestion that the summary-statistic
account of peripheral vision ties to visual-search and crowding cost (Rosenholtz et al., 2007).
**Compression** measures — *JPEG size* (lossy, fixed quality) and *PNG size* (lossless) — index
description length and redundancy, the information-theoretic construal of complexity (Donderi, 2006).
**Intensity information** — grayscale *Shannon entropy* of the luminance histogram — indexes first-order
tonal variety. **Structure** — *quadtree leaf count*, the number of homogeneous blocks required to encode
the image under a variance threshold — indexes layout/encoding cost in the design tradition. **Chromatic
variety** — *colour count*, the number of distinct quantised colours — indexes palette heterogeneity. For
condition matching we equate the ordered-complex and cluttered sets on edge density and subband entropy
(the texture-density group), which carry the bulk of "how much is going on," and we verify that the
conditions differ on independent coherence/order indices rather than on these low-level measures.

### 2.3.2 Facial electromyography (primary affective channel)

Facial EMG provides a continuous, covert index of affective valence with sub-second temporal resolution,
and is the study's primary dependent measure. Activity over **corrugator supercilii** (the "frown" muscle)
increases with negative affect and processing difficulty, and **decreases** when a stimulus becomes fluent;
activity over **zygomaticus major** (the "smile" muscle) increases with positive affect. The two therefore
give a bidirectional read on the predicted arc — corrugator for the initial stress and its refund,
zygomaticus for the positive shift at closure (Cacioppo, Petty, Losch & Kim, 1986; Winkielman & Cacioppo,
2001). Signals are recorded with miniature Ag/AgCl electrodes at the standard sites (Fridlund & Cacioppo,
1986), sampled at ≥ 1000 Hz, band-pass filtered (≈ 20–400 Hz) with a mains notch, rectified and integrated
(root-mean-square in short bins, ≈ 20–50 ms), corrected to a pre-stimulus fixation baseline, and
standardised (z) within participant and muscle to remove placement and individual gain differences. Trials
with blink or movement artefact in the analysis window are rejected. Corrugator is analysed in an **early
window** (0–2 s post-onset; H1/H2) and a **peri-recognition window** (−0.5 to +3 s around the recognition
press; H3–H5).

### 2.3.3 Electrodermal activity (autonomic arousal)

Skin conductance indexes sympathetic arousal and, unlike EMG, carries no valence sign — it registers the
*intensity* of the response and so distinguishes an aroused-but-refunded trajectory from a sustained one.
Electrodes are placed on the distal phalanges of the non-dominant hand; the signal is sampled (≈ 250–1000
Hz), low-pass filtered, and decomposed into a slowly varying **tonic** level and discrete **phasic**
responses using a standard continuous-decomposition method (e.g., Ledalab/cvxEDA; Benedek & Kaernbach,
2010). Event-related SCR amplitude is scored in a 1–4 s window locked both to onset and to recognition; the
persistence of tonic elevation across the trial is the electrodermal expression of "enduring" stress
(Boucsein, 2012).

### 2.3.4 Pupillometry (effort/arousal)

Pupil diameter provides a second, continuous arousal/effort index sensitive to the locus-coeruleus–
noradrenaline system and to cognitive effort (Beatty, 1982; Mathôt, 2018): dilation is expected during
effortful search and a characteristic change is expected at closure. Because the pupil is dominated by the
light reflex, **mean luminance is equated across conditions**, blinks are interpolated, and diameter is
baseline-corrected to the pre-stimulus interval; the analysis emphasises the **recognition-locked change**
rather than absolute diameter, and luminance is reported per condition so any residual confound is visible.

### 2.3.5 Behavioural indices (the closure clock and its validation)

Two behavioural measures anchor the design. **Recognition latency** — the time from stimulus onset to the
participant's "I see it / it clicked" key-press — operationalises the closure event and provides the
event marker to which the physiological channels are re-locked; it is the study's central timing variable.
**Recognition accuracy** — a post-trial identification or forced-choice verification against foils —
confirms that a press reflects genuine perceptual closure rather than a guess or a response to task demand;
trials with an incorrect identification are treated as non-closure. Unsolvable catch stimuli, on which no
veridical closure is possible, provide a within-design baseline for spurious presses.

### 2.3.6 Self-report (the conscious outcome)

After each trial, participants provide continuous 0–100 ratings of **peak discomfort/stress**, **relief /
"aha" intensity**, and **confidence**, and (for valence/arousal) a Self-Assessment Manikin rating (Bradley
& Lang, 1994). These index the consciously accessible affective outcome and are entered into trial-level
models against the physiology: H6 predicts that the magnitude of the corrugator drop at recognition scales
with reported relief/aha, linking the covert and overt refunds.

### 2.3.7 Electroencephalography (optional; neural closure markers)

In the psychophysiology-plus tier, EEG provides the neural signature of gestalt closure: the perceptual
**closure negativity** (≈ 230–300 ms) and induced **gamma-band** power increase at the moment of
organisation (perceptual-closure ERP/MEG work). Data are recorded from a standard montage, epoched to both
onset and recognition, and used to time the closure event independently of the motor press, guarding
against the press's motor artefact contaminating the peri-recognition analyses.

### 2.3.8 Derived indices (operationalising the theoretical constructs)

The hypotheses are tested on four derived quantities computed from the channels above, each a direct
operationalisation of a construct in the theory. **Initial stress** = mean corrugator (and phasic SCR) in
the 0–2 s onset window. **Refund magnitude** = corrugator peak minus corrugator at the post-recognition
asymptote (with the parallel zygomaticus rise). **Enduring index** = mean corrugator/tonic SCL in the late
window (last 2–3 s) relative to baseline, indexing stress that closure did not remove. **Stress
area-under-the-curve (AUC)** = integrated corrugator across the whole trial, used for the cue-timing
dosage analysis (earlier closure predicts smaller AUC). The confirmatory **crossover** (H5) is the
stimulus-class × window interaction on corrugator and SCR; the tightest refund test contrasts the
within-image Mooney conditions (pre-cue vs post-cue) on all channels. Finally, to close the loop to the
computational programme, the stimulus complexity battery (2.3.1) is regressed onto the **enduring index**
and, separately, onto the **refund magnitude**: the prediction is that image-computable complexity tracks
the enduring, non-resolvable component but not the refundable one — i.e., an image-only measure is a model
of the sustained affective residual, not of the resolvable transient.
