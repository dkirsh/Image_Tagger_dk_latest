# The Dimensionality of Perceived Clutter: From Image Statistics to Model-Relative Disorder

### A working review and a research program · draft, 2026-07-30

*Prepared for the CNfA / image-tagger program (D. Kirsh). A "quick but thorough" synthesis intended to be
kept, sharpened, and grown into a publishable review + empirical contribution. It argues that perceived
clutter is neither one-dimensional nor observer-independent, codifies a candidate **clutter vector**, and
proposes a crowdsourcing study that estimates how many dimensions people actually use and how much of
"disorder" is model-relative. Citations are to primary sources; claims are flagged **firm / framework /
open** where the evidence is uneven.*

---

## 1. The problem, and why the scalar habit is wrong

In practice "clutter" and "visual complexity" are treated as a single number — one slider in a UX audit,
one term in an architectural rating, one scalar in a saliency/search model. Everyday phenomenology resists
this immediately. A room can be *busy but regimented* (a lecture hall of identical seats) or *sparse but
haphazard* (three chairs thrown at angles); a surgical tray and a junk drawer may carry the same object
count yet sit at opposite ends of "cluttered." And — the case that breaks the scalar outright — a scene
that looks like disarray to one viewer is orderly to another who holds the key: your own desk is not
cluttered *to you*, because you know the pile-spanning conventions and that a sheet's orientation in a
stack carries information. The felt clutter changed with no pixel changing.

Two claims follow, and this review defends both. First, perceived clutter is **multidimensional**: at
least *scale* (coarse arrangement vs fine surface accumulation) and *kind/order* (how, and by what, the
busyness is produced) are separable. Second, one of those dimensions is **observer-relative**: apparent
disorder is incompressibility *relative to the viewer's learned model of what such scenes usually are*,
so there is no assumption-free "true clutter" of a knowledge-structured scene. The constructive payoff is
a **vector** representation and a study design that estimates its effective dimensionality across levels
of expertise.

## 2. Three traditions, three partial answers

**2.1 Image statistics (bottom-up, computable).** The dominant operational measures come from Rosenholtz
and colleagues: **Feature Congestion**, a multiscale measure pooling local variability of color,
luminance, and orientation over a Gaussian pyramid; **Subband Entropy**, a coding-cost measure; and the
simpler **edge density** ([Rosenholtz, Li & Nakano 2007](https://pubmed.ncbi.nlm.nih.gov/18217832/)).
Their mechanistic backing is the account of peripheral vision as **summary-statistic (texture) pooling** —
the Texture Tiling Model / "mongrels" and the pooling account of crowding ([Rosenholtz et al., crowding
via feature pooling](https://pmc.ncbi.nlm.nih.gov/articles/PMC4790193/)): clutter is, mechanistically, the
loss of information when the periphery represents a region by its summary statistics. This tradition is
*firm* on what it predicts (visual-search cost, crowding) and genuinely multiscale, but it is
observer-independent by construction — the number does not know who is looking.

**2.2 Perceptual dimensions (psychophysical).** When you ask people directly and let the structure emerge,
complexity is not one thing. [Oliva, Mack, Shrestha & Peeper
(2004)](http://macklab.utoronto.ca/uploads/8/1/8/3/8183/olivaetal2004.pdf) recovered multiple dimensions
of scene complexity — roughly **quantity of elements, variety, and organization/symmetry** (with openness
distinct). This inherits Berlyne's *collative variables* (complexity, novelty, incongruity, and — crucially
— *order*), and it is now standard that **subjective** complexity diverges from any single objective proxy
([Visual Complexity and Affect, 2017](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2017.02368/full)).
A very recent decomposition, "[Complexity in Complexity](https://arxiv.org/html/2501.15890v3)" (2025),
splits perceived visual complexity into **structure, color, and surprise** — an explicit move to a
component vector, and evidence the field is converging on exactly the reframing proposed here.

**2.3 Structure and meaning (scene grammar).** The "kind of thing making the clutter" is addressed most
directly by **scene grammar**: scenes have **anchor objects** (large, positionally predictive, they
scaffold the layout) and **local objects** (small, populate surfaces), and violations come in two flavors —
*syntactic* (wrong position/arrangement) and *semantic* (wrong identity) ([Võ et al., scene
grammar](https://pmc.ncbi.nlm.nih.gov/articles/PMC5705766/); [Turini & Võ 2022, hierarchical object
organization](https://www.nature.com/articles/s41598-022-24505-x)). This maps almost one-to-one onto the
distinction you drew: *furniture disarray* is **anchor-level syntactic disorder**; *junk-covered surfaces*
is **high local-object density**. They feel incommensurable because they are different constructs at
different levels of a hierarchy.

Running underneath all three, the **environmental-aesthetics** tradition has always paired complexity with
its opposite: Kaplan's framework scores a scene on **complexity *and* coherence** (and legibility,
mystery), coherence being the order/readability counterweight ([Stamps meta-analysis, *Mystery,
complexity, legibility and coherence*](https://www.researchgate.net/publication/223244399_Mystery_complexity_legibility_and_coherence_A_meta-analysis)).
Order is not the absence of complexity; it is a separate axis that can cancel complexity's cost.

## 3. The two axes, made precise

**Scale.** Coarse-structural clutter (how the big, layout-defining elements are arranged) and fine-surface
clutter (how densely small elements populate surfaces) are separable, and the natural formalism is
multiscale: Feature Congestion already lives on a pyramid, and a 2024 measure keeps the **per-scale
profile** rather than collapsing it ([Multi-scale structural complexity](https://arxiv.org/html/2408.04076v1)).
The practical move is to *read clutter out at coarse vs fine bands* instead of pooling to one scalar.

**Order/kind.** The tempting formalization of "regimented vs random" is information-theoretic: **order =
compressibility**. A regular grid of chairs has a short description; chairs strewn at random do not, even
at equal count ([Donderi 2006, information-theoretic analysis of visual
complexity](https://journals.sagepub.com/doi/abs/10.1068/p5249)). This cleanly separates arrangement order
from mere density — and it is exactly where the observer-relative problem enters.

## 4. Why clutter is not a purely syntactic (compression) notion — the core problem

Your objection is correct and, we think, the paper's central thesis. Algorithmic (Kolmogorov) complexity is
**only defined relative to a description language / universal machine**, and the relevant quantity for a
viewer is the *conditional* complexity **K(x | M)** — the cost of describing scene *x* **given the model M
the viewer already holds**. A scene that looks maximally disarrayed has *low* K(x | M) for the observer
whose M explains it. Compressibility is therefore not a property of the image; it is a property of the
image *paired with a decoder*.

Two literatures make this rigorous rather than hand-wavy. **Effective complexity** (Gell-Mann & Lloyd)
separates a system's description into its **regularities** and its **incidental randomness**, and explicitly
requires a judgment — a model — of *which* features count as regularity ([Ay, Müller & Szkoła, *Effective
Complexity and its Relation to Logical Depth*](https://arxiv.org/abs/0810.5663)). There is no
model-free fact about how much of your desk is "signal." And **Schmidhuber's compression-progress**
principle makes subjective beauty, novelty, and interestingness explicitly relative to *the observer's
current compressor* — what is interesting/complex is what your present model cannot yet compress but is
learning to ([Schmidhuber 2009, *Driven by Compression
Progress*](https://arxiv.org/abs/0812.4360)). Perceived order just is compression *by this observer's
model*.

The cognitive realization is **expertise as learned chunking**. Since Chase & Simon's chess work, we have
known experts encode domain scenes into **chunks/templates** that novices lack, so the expert literally
sees structure where the novice sees noise (the effect generalizes to radiology, circuit diagrams, sport,
and — by your example — a personal filing system). Familiarity supplies M. Hence:

> **Perceived clutter = residual disorder after the viewer applies their best generative model of the
> scene.** Image-only measures approximate this with a *shared, typical-scene prior*; the gap between an
> image-statistic clutter score and a given viewer's judgment *is* the observer-model term — and it is
> measurable (expert vs novice, familiar vs unfamiliar category).

This is not a counsel of despair; it is an experimental handle. It also tells the tagger exactly what it
is: an **image-only null model**. Its clutter score is a defensible lower bound on disorder assuming no
special knowledge; the residual to human judgment *estimates the knowledge contribution* rather than being
error to hide. That stance fits the program's honesty discipline (report the residual, don't paper over it).

## 5. Codifying the clutter vector (v1)

We therefore replace the scalar with a small **vector**, each component carrying a definition, an
image-side predicate the tagger can compute, a subject-facing 2AFC facet question, and a flag for whether
it is observer-relative.

| Dim | Construct | Image-side predicate (engine) | Facet question | Observer-relative? |
|----|-----------|-------------------------------|----------------|--------------------|
| **D1** | Fine-scale **surface density** (local-object congestion) | Feature Congestion (fine subbands), edge density | "Which has more *stuff on the surfaces*?" | low |
| **D2** | Coarse-scale **arrangement (dis)order** | anchor-layout regularity / compressibility of large-element positions | "Which layout is more *haphazard / disorganized*?" | medium |
| **D3** | **Variety / heterogeneity** | subband entropy, color/material palette variety | "Which has a greater *variety of different things*?" | low |
| **D4** | **Semantic incongruity** (scene-grammar violation) | object–context expectancy (out-of-place objects) | "Which has things that *don't belong / seem out of place*?" | high |
| **D5** | **Legibility to the observer** (model-relative order) | *not image-only* — estimated via familiarity/expertise | "How *readable / organized* is this to you?" + rate familiarity | very high |
| **H** | **Holistic** umbrella | (learned weighting of D1–D5) | "Which is *more cluttered*?" | mixed |

The overall judgment H is some (possibly observer- and task-dependent) weighting of D1–D5. The empirical
questions are then sharp: **how many dimensions do people actually use** (is a 2- or 3-vector enough, or is
the full set separable?), **what are the weights**, **how much does D5 move with expertise**, and **which
components can an image-only tagger recover** (D1, D3 likely; D4, D5 only partially). Note this vector is a
hypothesis to be tested, not a settled taxonomy — which is the point of §6.

## 6. A research program: comparing vectors across observers

The publishable contribution you floated — "compare different-sized vectors reflecting different positions"
— is precisely a **dimensionality-and-observer study**, and, to our reading, largely undone: prior work
either keeps complexity scalar or proposes a *fixed* multi-component model without empirically estimating
how many dimensions viewers use or how that changes with expertise.

**Design.** A crowdsourced 2AFC/rating study over a stimulus set deliberately spanning the D1–D4 axes
(orthogonalized as far as possible: high-density/low-disorder, low-density/high-disorder, etc.), collecting
the holistic judgment **and** the facet judgments, from raters stratified by **expertise/familiarity**
(lay crowd via Prolific; domain experts; plus a within-subject *familiar vs unfamiliar scene-category*
manipulation). Existing benchmarks (e.g. the crowdsourced [SAVOIAS](https://cs-people.bu.edu/esaraee/mydocs/SAVOIAS.pdf)
multi-category complexity dataset) supply comparison points and additional stimuli.

**Analysis.** Fit models of increasing dimensionality (1-D holistic Thurstonian/Bradley-Terry → k-D factor
/ ideal-point models) and select the **effective dimensionality by cross-validation / information
criteria**; regress human facet scales on the tagger's image-side predictors to see *which components are
image-recoverable*; and localize the **observer term** as the systematic tagger–human residual that grows
with knowledge-encoded order.

**Predictions (pre-registerable).** (i) >1 dimension is required. (ii) Agreement drops and
stochastic-transitivity violations concentrate on *cross-type* pairs (D1-heavy vs D2-heavy) — the direct
signature of incommensurability. (iii) Expertise/familiarity raises perceived order (D5) and *widens* the
tagger–human gap on knowledge-structured scenes. (iv) Recovered structure partly matches the
structure/color/surprise decomposition and the Oliva dimensions — convergence would be reassuring, not
redundant, because we add the *observer-relativity* estimate they lack.

## 7. What this means for the tagger and the validation harness

Concretely: `perceived_clutter` stops being one predicate and becomes a **vector of facet predicates**, and
its ledger entry becomes a **vector of validities** (a Spearman ρ per facet), each promoted or failed
independently. The tagger declares itself an **image-only null model** and *reports the human residual*
rather than absorbing it — the residual is the estimated observer/knowledge contribution and is a result,
not noise. Stimulus curation must span the axes and include knowledge-variable categories so D5 is
identifiable. This is the multidimensional analogue of the validation slice already underway.

## 8. Open problems

The definition of "regularity" in effective complexity is itself model-relative (a feature, not a bug, but
it must be stated). Individual and cultural differences in M; task-dependence (clutter-for-search vs
clutter-for-calm vs clutter-for-competence); dynamic and embodied clutter (a desk is legible partly because
you *act* in it); and the risk that facet questions themselves prime dimensions that are not spontaneously
used. Each is a section the full paper should own rather than wave past.

## 9. One-paragraph thesis (for the abstract)

Perceived clutter has been operationalized as a scalar image statistic, but both everyday phenomenology and
the empirical record show it is multidimensional — separable at least into fine-scale surface density,
coarse-scale arrangement order, variety, and semantic incongruity — and, decisively, **partly
observer-relative**: apparent disorder is incompressibility with respect to the viewer's learned scene
model, so expertise and familiarity change felt clutter with no change to the image. We codify clutter as a
vector, show that its "order" components cannot be reduced to observer-independent compression, and propose
a crowdsourcing study that estimates the effective dimensionality of clutter and isolates its
observer-relative component across levels of expertise. An image-only model is best understood not as a
clutter *detector* but as a null model whose residual against human judgment measures what knowledge adds.

## References

- Rosenholtz, Li & Nakano (2007), *Measuring Visual Clutter*, J. Vision — https://pubmed.ncbi.nlm.nih.gov/18217832/
- Rosenholtz et al., pooling/summary-statistic account of crowding (Texture Tiling Model) — https://pmc.ncbi.nlm.nih.gov/articles/PMC4790193/
- Oliva, Mack, Shrestha & Peeper (2004), *Identifying the Perceptual Dimensions of Visual Complexity of Scenes* — http://macklab.utoronto.ca/uploads/8/1/8/3/8183/olivaetal2004.pdf
- Donderi (2006), *An Information Theory Analysis of Visual Complexity and Dissimilarity* — https://journals.sagepub.com/doi/abs/10.1068/p5249
- *Multi-scale structural complexity as a quantitative measure of visual complexity* (2024) — https://arxiv.org/html/2408.04076v1
- *Complexity in Complexity: Understanding Visual Complexity Through Structure, Color, and Surprise* (2025) — https://arxiv.org/html/2501.15890v3
- Turini & Võ (2022), *Hierarchical organization of objects in scenes…*, Sci. Reports — https://www.nature.com/articles/s41598-022-24505-x
- Võ et al., scene grammar / anchor objects — https://pmc.ncbi.nlm.nih.gov/articles/PMC5705766/
- Stamps, *Mystery, complexity, legibility and coherence: A meta-analysis* — https://www.researchgate.net/publication/223244399_Mystery_complexity_legibility_and_coherence_A_meta-analysis
- *Visual Complexity and Affect: Ratings Reflect More Than Meets the Eye* (2017) — https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2017.02368/full
- Ay, Müller & Szkoła, *Effective Complexity and its Relation to Logical Depth* (Gell-Mann & Lloyd effective complexity) — https://arxiv.org/abs/0810.5663
- Schmidhuber (2009), *Driven by Compression Progress…* — https://arxiv.org/abs/0812.4360
- Saraee et al., *SAVOIAS: A Diverse, Multi-Category Visual Complexity Dataset* — https://cs-people.bu.edu/esaraee/mydocs/SAVOIAS.pdf
- Chase & Simon (1973), *Perception in chess* (chunking/expertise) — foundational; Gobet & Simon on templates.

*Status: working draft. Next passes: expand §2–§4 with figures and the search/UX literature (Miniukovich &
De Angeli on interface clutter), add a methods appendix for §6 (power, stimulus orthogonalization,
transitivity tests), and typeset for submission.*
