# Measuring Visual Clutter (Rosenholtz, Li & Nakano 2007) — summary, aftermath, and verdict for CNfA
### 2026-07-19 (Cowork/Fable) · one-page brief for David · paper record for the processing queue

**Citation:** Rosenholtz, R., Li, Y., & Nakano, L. (2007). Measuring visual clutter. *Journal of
Vision, 7*(2):17, 1–22. doi:10.1167/7.2.17 · [full text](https://jov.arvojournals.org/article.aspx?articleid=2122001) · PDF acquisition: `pip3`/browser one-liner below; file this record under `reference/papers/` until the PDF lands in the Zotero/CNFA_PDFs pipeline.

## What the paper says
Clutter is defined operationally: the state in which excess items, or their representation, degrade
task performance — measured without needing to segment "objects." Three computable measures:
**Feature Congestion** (the one we are porting): at 3 Gaussian-pyramid scales in CIELab, local
covariance "ellipsoid volume" of color (a,b), local bandpass-contrast variability, and oriented
opponent-energy variability; scales collapsed by max (5-tap kernel), features combined as
color/0.2088 + contrast/0.0660 + orientation/0.0269 (weights fit to judgments), Minkowski-pooled
(p=1). Intuition: clutter = how hard it is for a new item to grab attention — the display's feature
space is "congested." **Subband Entropy**: Shannon entropy of steerable-pyramid subband coefficients
(wlevels=3, chroma weight 0.0625) — clutter as unpredictability/encoding cost. **Edge Density**:
Canny (0.11/0.27, σ=1) pixel fraction — the workhorse baseline. Validation: subjective clutter
rankings of maps and search-time data; FC correlates r≈.77 with median clutter judgments (edge
density r≈.83 on indoor scenes in related work), with intersubject agreement r≈.61–.70 acting as the
practical ceiling — the three measures were statistically indistinguishable at n available. Honest
limitations stated in-paper: no objects, no grouping/organization, global weights hand-fit.

## What happened since (the reconsiderations)
1. **Proto-object segmentation beats FC** on clutter judgments ([Yu, Samaras & Zelinsky 2014, JoV](https://jov.arvojournals.org/article.aspx?articleid=2194016); NeurIPS 2013): merging superpixels into proto-objects and *counting* them predicts human clutter better than feature congestion — evidence that clutter is substantially about **numerosity of perceptual units**, not feature variance alone. Clutter is also ~size-invariant ([Vision Research 2015](https://pmc.ncbi.nlm.nih.gov/articles/PMC4644518/)), which pure pixel-statistics measures do not guarantee.
2. **Supervised deep models dominate in-distribution**: IC9600 (Feng et al. 2023) reaches r≈.92–.95 on its own categories — but is a trained black box with unknown transfer.
3. **The 2025 synthesis** ([“Complexity in Complexity”, arXiv 2501.15890](https://arxiv.org/html/2501.15890v3)): an interpretable model of segmentation counts + multi-scale Sobel gradient + multi-scale unique color reaches r≈.84–.87 *across* 16 datasets without retraining, beating edge density on 5/16 and losing on only 2; and **semantic "surprise"** (LLM-scored) explains variance no image statistic captures (partial r=.48 after regressing out segmentation/object counts). Complexity/clutter has (at least) structural, chromatic, and *semantic* dimensions.
4. Rosenholtz's own trajectory (texture-tiling/crowding models) effectively concedes the 2007 framing was a first-order statistic of a deeper peripheral-encoding story.

## Evaluation for CNfA — adequate, or time for a better account?
**Keep FC/SE — but demote their role.** They remain the best *deterministic, training-free,
replayable* clutter statistics available, which is exactly what our M1′/GREEN machinery wants; the
faithful port stays worth finishing. But three critiques bite for our use: (a) **domain transfer is
unvalidated** — RLN2007 validated on maps/UI, not architectural interiors; our A/B corpus should
test FC vs. alternatives *on interiors* before any construct claim; (b) the 2014–2025 evidence says
**proto-object/segment count** is the stronger single predictor — and we already plan a pinned
segmentation model in Wave 3, so a `segment_count_clutter` operator is nearly free and should ride
alongside FC; (c) **the semantic dimension is real** (surprise), reachable only via a VLM-tier AMBER
operator — worth a Wave-3 candidate slot, never licensed into hedonics without calibration.
**Verdict:** the 2007 account is *incomplete rather than wrong* — a defensible lower layer. The
better account is a three-layer clutter stack: pixel-statistics (FC/SE/edge, GREEN-capable) →
proto-object count (segmentation-tier, AMBER) → semantic surprise (VLM-tier, AMBER), adjudicated on
our own labeled interiors. Recommend: add the two new operators to the construction table as
candidates C-CLUT-2 / C-CLUT-3, and make the corpus's clutter A/B pairs score all three layers.

**PDF acquisition (David, either):** browser-save from the [JoV page](https://jov.arvojournals.org/article.aspx?articleid=2122001) into `CNFA_PDFs/`, or have any Codex run: download to
`/Users/davidusa/REPOS/Image_Tagger_dk_latest/reference/papers/Rosenholtz_Li_Nakano_2007_Measuring_Visual_Clutter.pdf` and commit (per the CLAUDE.md artifact contract).
