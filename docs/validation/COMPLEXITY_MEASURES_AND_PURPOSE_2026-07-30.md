# What is complexity *for*? Measure divergence on SAVOIAS, and the case for operation-indexed complexity

### Companion analysis to the clutter review · 2026-07-30

*We downloaded the SAVOIAS crowdsourced visual-complexity dataset (1,420 images, 7 categories, per-image
human complexity ground truth from pairwise comparisons), computed eight of the measures different
research communities have used, and asked two questions: do the measures agree, and does any of them
recover human complexity? The answers — no, and only conditionally — motivate a claim we think is
correct and consequential: **complexity is not a property of an image; it is a proxy for the cost of a
particular operation, computed at a particular processing stage, and it must be indexed to both.** Figures
`fig1_rho_by_category.png`, `fig2_inter_measure.png`, `fig3_disagreement.png`.*

## 1. The measures do not measure the same thing

Eight measures, each the operationalization some literature settled on: **edge density** (Mack & Oliva;
search), **JPEG size** and **PNG size** (Donderi's compression account), **grayscale Shannon entropy**
(classic information), **subband entropy** and **contrast energy** (Rosenholtz feature-congestion family;
crowding/search), **quadtree leaf count** (structural/description-length; UX and design), and **colour
count** (variety). Computed on identical 256×256 inputs and correlated with one another (Spearman, pooled;
`fig2`), they span **ρ = 0.22 to 0.93**. Edge density and JPEG size are nearly redundant (0.93); colour
count is almost orthogonal to every entropy/texture measure (0.22–0.44); grayscale entropy sits apart from
the structural measures (0.36–0.49). "Visual complexity," operationalized eight reasonable ways, is at
least three or four weakly-related things, not one.

`fig3` makes the divergence concrete. A black-and-white **zebra in grass** sits at the 96th percentile of
edge density and the 89th of subband entropy — texture measures scream "complex" — yet at the 0th
percentile of colour, and humans rated it **16/100**, near the bottom. A **Suprematist composition** of a
few coloured bars is the mirror image: 96th percentile colour, 5th percentile edge/texture, human 43. Two
images, opposite verdicts depending on which measure you trust.

## 2. Which measure is "right" depends on the category — i.e., on the operation

The decisive result is `fig1`: the measure that best matches human complexity **flips across domains**.

| Category | Best measure | ρ | Worst measure ρ |
|---|---|---|---|
| Scenes | Colour count | 0.63 | 0.31 |
| Interior Design | **JPEG size** | 0.81 | 0.37 |
| Objects | Contrast energy | **0.43** | 0.19 |
| Art | Edge density | 0.59 | 0.44 |
| Suprematism | **Colour count** | 0.85 | 0.57 |
| Advertisement | JPEG size | 0.78 | 0.45 |
| Visualizations | JPEG size | 0.74 | 0.38 |

Compression (JPEG) tracks perceived complexity of *interiors, ads, and visualizations* — designed
artifacts whose complexity is largely how much non-redundant structure they pack. Colour count wins for
*Suprematism* — abstract art whose "complexity" viewers read off palette and element variety, not texture.
For *Objects*, **nothing works**: every measure tops out at ρ ≤ 0.43, because the perceived complexity of a
single object is about *what it is*, not its image statistics. There is no domain-general best measure.
"How complex is this image?" has no answer until you say *complex for what, and for whom*.

## 3. Why we want complexity: it is a proxy for an operation's cost

This dissolves the confusion. Each measure was not built to capture some Platonic complexity; each was
**engineered to predict a specific downstream operation**, and it succeeds exactly where that operation
governs the human judgment:

- **Edge density / subband entropy / contrast energy** were built to predict **visual-search difficulty
  and crowding** — how much the periphery's summary-statistic representation loses (Rosenholtz's texture
  account). They win where clutter *is* search cost (natural/textured scenes, art).
- **Compression size** (Donderi) is a proxy for **description length / transmission / discriminability** —
  it wins for designed artifacts whose value is information packed per unit area.
- **Quadtree / structural** measures proxy **encoding and layout cost** — the UX/design tradition
  (interface clutter).
- **Colour count / variety** proxies **feature heterogeneity** — it wins where judgment is dominated by
  palette (abstract art).
- The Berlyne/Birkhoff aesthetic lineage tied complexity to **arousal and preference** (M = O/C); the
  Kaplan tradition tied it to **environmental preference and wayfinding** (complexity gated by coherence).

So the answer to "why do we want complexity?" is: **we never want complexity in the abstract — we want a
cheap predictor of some operation's cost**: time-to-find, load-to-encode, effort-to-navigate,
memory-to-store, or affect-to-feel. Untethered from an operation, the quantity is underdetermined, which
is precisely why eight defensible measures disagree and why the "best" one changes with the task the
category implies. A clutter number is only meaningful relative to the verb it is supposed to predict.

## 4. Complexity is computed at (at least) two stages — and the knowledge-relative one is late

Your further intuition — that "I know where everything is and why" is a *later* construct that arrives
after shallow visual processing — is, we think, exactly right, and the data show its fingerprint.

There is an **early, shallow complexity**: feed-forward, fast (~100–150 ms), image-computable summary
statistics — edge density, spatial-frequency/subband energy, contrast, colour variety. This is what
peripheral vision and gist deliver; it is observer-general and is what all eight measures approximate. And
there is a **late, knowledge-relative order**: it requires object recognition, scene-schema retrieval, and
application of stored structure (scene grammar; expert chunks), so it is slower and model-based. The zebra
is the proof: the early measures fire at the 90th-plus percentile on its texture, but by the time
recognition resolves "a zebra in grass," the *perceived* complexity has collapsed to 16 — the late stage
has re-described a high-entropy image as one familiar thing. The **Objects category's ceiling** (no measure
> 0.43) is the same effect at scale: object complexity lives at the recognition stage, above where image
statistics can reach. Your desk is the everyday version — the late stage supplies a model M under which the
"mess" is compressible, and only *you* hold M.

The consequence is structural, not merely a caveat. Complexity is not one signal available at one moment;
it is **at least two quantities, computed at different stages, feeding different operations**:

- *early / shallow / observer-general* → drives peripheral search cost, crowding, gist, first-glance
  affect;
- *late / knowledge-relative / observer-specific* → drives interpreted disorder, wayfinding-once-familiar,
  expert legibility, "I know where everything is."

A single scalar collapses these, which is why it is unstable across tasks and viewers. The right object is
**complexity indexed to (processing stage, operation, observer-model)** — which is exactly the vector the
review proposes, now with a temporal/functional reading of its axes: the D1/D3 (surface density, variety)
components are early and image-recoverable; D2 (arrangement order) is intermediate; and D4/D5 (semantic
incongruity, legibility-to-observer) are late and largely *not* image-recoverable, which is why the
tagger–human residual on them is a measurement of the late stage, not error.

## 5. What this means for the program

Three concrete consequences. **(a) Stop reporting a clutter scalar.** Report the vector, and label each
component with the operation it predicts and the stage it lives at. **(b) Validate against operations, not
against "complexity."** The ledger's target for an early component should be search/crowding behaviour or
the crowd's fast judgment; for a late component it should be recognition-dependent tasks and expert
ratings — and the image-only tagger is explicitly a model of the *early* stage, whose residual estimates
the late contribution. **(c) The SAVOIAS result is a reusable instrument**: the eight-measure battery and
the per-category ρ profile are a template for asking, of any new predicate, *which operation and which
stage it is actually tracking* before we trust it.

## Method note

SAVOIAS: Saraee, Jalal & Betke, *SAVOIAS: A Diverse, Multi-Category Visual Complexity Dataset*
(github.com/esaraee/Savoias-Dataset); per-image ground truth = crowdsourced pairwise-comparison global
ranking (0–100). Measures computed on 256×256 RGB (compression measures at fixed size/quality); Spearman ρ
throughout; N = 1,420 across 7 categories. Full per-image table: `savoias_measures.csv`. Reproduce with
`measures.py` + `figs.py`.

*Reads as a results section for the review's §2–§4 and a standalone short paper ("Complexity for what? An
operation-indexed account, with evidence that no image measure is domain-general"). Next: add a
recognition-time / expert-vs-novice manipulation to pin the early-vs-late split empirically.*
