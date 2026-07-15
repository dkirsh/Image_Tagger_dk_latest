# Image Tagger — Project Rules

## Scientific Justification Rule

Every operationalized attribute, visualization function, or computational
operator in this system must carry a scientific justification for every
non-trivial design decision.

### What counts as a design decision

- Threshold values (e.g., "warm hue < 30°")
- Formula choices (e.g., "complexity = 0.4×edge_density + 0.3×entropy + 0.3×spectral_slope")
- Normalization methods (e.g., "divide by theoretical max" vs "clamp to [0,1]")
- Distance bands (e.g., "social distance 0.45–3.7m")
- Model choices (e.g., "SegFormer-B5 over DeepLabV3")
- Window/kernel sizes (e.g., "31px Gaussian for local luminance")
- Confidence assignments (e.g., "0.6 for FFT saliency fallback")

### What the justification must include

1. **A citation** — author, year, and enough context to find it (DOI or title).
   If no published source exists, write: `"project convention, no published source"`.
2. **A rationale snippet** — 1–2 sentences explaining WHY this value, not just
   what it is. Quote the source if possible.
3. **Known limitations** — what the source's original context was (e.g., "Hall's
   proxemic distances were measured for standing North American adults, not
   seated postures in architecture").

### Where it goes

- In the code: the `method` string of `AttributeResult` must name the citation.
- In the docs: `cnfa_algs/JUSTIFICATION_TABLE.md` carries the full table mapping
  every parameter → citation → snippet → limitation.
- In the adversarial review: an attribute without a documented justification
  for its parameters is a contract violation.

### Why

This is a research system. Every computational parameter is an implicit
scientific claim. Implicit claims are unauditable, and unauditable claims
are indistinguishable from bugs.
