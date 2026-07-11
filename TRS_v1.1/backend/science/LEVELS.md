# Epistemic Levels for the CNfA Image Tagger

This document defines the inclusion conditions for each level in the science
pipeline.  Every computed attribute must belong to exactly one level.  The level
determines what provenance metadata is required and how the attribute may be
used in downstream analysis.

---

## L0 — Proximal Computational Features

### Inclusion Test

> Can a reader reproduce this number by reading the code and doing the math
> by hand on the pixel values?  If yes → L0.

### What Belongs Here

Any feature computed directly from pixel values using transparent, deterministic
algorithms.  No learned weights.  No neural networks.  No external API calls.

### Why It Matters

These are your **independent variables**.  They describe *what the stimulus IS*
in terms that map onto early visual processing.  When you find that
`fractal_D ∈ [1.3, 1.5]` predicts stress recovery, you've found a proximal
cause — something you can manipulate in a follow-up experiment.

### Provenance Requirements

- Algorithm name
- Parameter values
- Library version

### Examples

| ✅ Belongs in L0 | ❌ Does NOT belong in L0 |
|---|---|
| Fractal dimension (box-counting) | "This image feels complex" (VLM) |
| CIELAB L* mean | "The dominant color is warm beige" (VLM) |
| LGN contrast energy (Weibull fit) | Room type = kitchen (Places365 CNN) |
| GLCM homogeneity | "Prospect score" (trained regression) |
| Spatial frequency spectral slope | Material = wood (SigLIP2 classifier) |

### Adding New L0 Features

Use `frame.add_proximal(key, value, source="module.function")`.

The `source` string should be the fully-qualified function name so a reader
can find the computation.

---

## L1 — Derived Perceptual Features

### Inclusion Test

> Is this feature an explicit, documented formula over L0 features?
> Can you write it as `L1_feature = f(L0_a, L0_b, ...)` where `f` is a
> named function with a citation?  If yes → L1.

### What Belongs Here

Composite scores, indices, and ratios that combine L0 features according to a
theory or published formula.  The formula itself is the scientific claim —
changing it changes the theory.

### Why It Matters

These are your **theoretical constructs operationalized**.  "Complexity" is not
a pixel measurement — it's a composite of edge density, entropy, and spectral
slope weighted according to a theory of visual complexity.  Making the formula
explicit lets you TEST the theory by comparing its predictions to human ratings.

### Provenance Requirements

- Formula (as code or equation)
- Literature citation
- Version
- Which L0 features it uses

### Examples

| ✅ Belongs in L1 | ❌ Does NOT belong in L1 |
|---|---|
| Complexity = 0.4 × edge_density + 0.3 × entropy + 0.3 × spectral_slope | Edge density (this is L0 — not a composite) |
| Naturalness = f(green_fraction, sky_fraction, earth_fraction) | "How natural does this look?" (VLM) → that's L3 |
| Biophilia index = f(green%, fractal_D, water%) | Room type classification → that's L2 |

### Adding New L1 Features

Use `frame.add_derived(key, value, formula="...", source="module.function")`.

The `formula` string must be a human-readable description of how this value
was computed from L0 features.  This is your documentation AND your hypothesis.

---

## L2 — Structural Features

### Inclusion Test

> Does this feature require a trained neural network, BUT its output is a
> transparent, interpretable structure (mask, depth map, bounding box,
> class label)?  If yes → L2.

### What Belongs Here

Object detection, semantic segmentation, depth estimation, room classification,
material identification.  The model is a black box, but what it produces is a
**structural description** of the image — something you can visualize, verify,
and use as input to further computation.

### Why It Matters

These features mediate between pixels and meaning.  You need segmentation to
compute "wall fractal dimension" (which is L0 applied to an L2 mask).  You need
depth to compute prospect.  But the segmentation model itself is not your
research object — it's infrastructure.

### Provenance Requirements

- Model name and checkpoint hash
- Input resolution
- Class vocabulary
- Date of model download/update

### Examples

| ✅ Belongs in L2 | ❌ Does NOT belong in L2 |
|---|---|
| Semantic segmentation mask (wall/ceiling/floor) | "This room feels spacious" → L3 |
| Monocular depth map | Fractal dimension of the wall region → L0 (applied to L2 mask) |
| Room type = kitchen (Places365) | "The style is Scandinavian" → L3 |
| Material = wood (SigLIP2) | Naturalness composite → L1 |

### Adding New L2 Features

Use `frame.add_structural(key, value, model_version="...", source="module.function")`.

The `model_version` string must uniquely identify the model checkpoint so
results are reproducible.

---

## L3 — Semantic / Cognitive Features

### Inclusion Test

> Does this feature require a **judgment** about meaning, experience, or
> quality — whether from a human rater, a VLM, or a trained classifier
> predicting human ratings?  If yes → L3.

### ⚠️ CRITICAL: L3 Features Are Hypotheses

L3 features are the **dependent variables** in your research.  They are what
you are trying to EXPLAIN, not what you are using to explain.

**Never:**
- Use an L3 feature as a predictor of another L3 feature without explicit
  justification
- Treat a VLM's opinion as ground truth
- Report an L3 correlation as a causal finding

The entire point of the CNfA program is to explain L3 in terms of L0/L1.

### Provenance Requirements

- Source type: `human` or `vlm`
- If VLM: model name, model version, prompt text hash, prompt version
- If human: rater ID, date, inter-rater reliability
- Confidence score

### Examples

| ✅ Belongs in L3 | ❌ Does NOT belong in L3 |
|---|---|
| Kaplan mystery rating (VLM) | GLCM contrast → L0 |
| "This space affords conversation" (human or VLM) | Room type = kitchen → L2 |
| Style = Scandinavian (VLM) | Naturalness composite → L1 |
| Emotional valence = positive (human survey) | Depth map → L2 |

### Adding New L3 Features

Use `frame.add_hypothesis(key, value, source="gpt-4o", prompt_hash="...", model_name="...")`.

The default confidence is 0.5 (pessimistic).  VLM judgments should always start
with low confidence until validated against human ratings.

---

## L4 — Causal / Discovered Features

### Inclusion Test

> Is this a **discovered** statistical or causal relationship between L0/L1
> features and L3 outcomes, validated through proper methodology?  If yes → L4.

### What Belongs Here

Your research output.  Regression models, feature importance rankings,
mediation analyses, and experimentally validated causal paths.

### This Level Starts Empty

L4 is populated through research, not through the pipeline.  When you discover
that `fractal_D ∈ [1.3, 1.5]` predicts `restoration > 0.7`, you've created an
L4 finding.

### Provenance Requirements

- Dataset description
- Sample size
- Statistical method
- Cross-validation scheme
- Effect size and confidence interval
- Publication reference (if any)

### Adding L4 Findings

Add entries to `L4_causal/discovered_features.json` with the required
provenance metadata.  See the README in that directory.
