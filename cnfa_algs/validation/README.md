# cnfa_algs.validation — credibility harness for attribute operationalizations

Four validation levels (use all, trust none alone):
  L0 analytic ground truth  : synthetic rooms with known parameters
  L1 known-contrast probes  : matched pairs / expected orderings, frozen as regression tests
  L2 independent judges     : ordinary-language probes -> vision LLM (this module) and humans
  L3 behavior               : seat choice, eye-tracking, POE — for affective composites

Files: probes.py (ordinary-language battery: ordinal / pairwise / localization),
vlm_judge.py (Gemini/Anthropic runner; GEMINI_API_KEY as in GeminiMaterialAnalyzer),
stats.py (Spearman/Kendall vs algorithm scalars, judge test-retest SD, IoU).

Pre-registered bands: rho>=0.6 CONVERGING | 0.3-0.6 WEAK | <0.3 FAILING.
Rules: checker != author (judge model must differ from the authoring model);
never tune the algorithm to the judge; run repeats and audit judge variance
(see scripts/audit_vlm_variance.py) before trusting any rating.

## First live run (2026-07-13, N=8 example images, stand-in same-family judge —
## mechanics demo, author-contaminated; re-run with Gemini for the clean version)

  processing_load   rho=0.93  CONVERGING  clutter proxy tracks "visually busy"
  enclosure_index   rho=0.81  CONVERGING  ranks right despite range restriction
  acoustic_alpha    rho=0.34  WEAK        misses invisible absorbers (acoustic tile
                                          reads as plaster) — the in-situ gap
  prospect (abs)    rho=0.27  FAILING*    *cross-image scale is VP-dependent, as
                                          pre-flagged; within-image fields unaffected;
                                          fix = real depth model
  landmark_salience rho=-0.30 FAILING     bottom-up saliency != semantic landmark
                                          (stair rated 6/7 by judge, 0.26 by algo);
                                          fix = object/VLM semantics, per backlog
  warm_vs_cool      rho=0.04  FAILING     saturates ~1.0 on warm-WB photos; reformulate
                                          as mean Lab b* instead of pixel-count ratio
  glare-risk        rho=0.04  FAILING     overexposure mask misses adaptation context

The instrument discriminates: strong constructs converge, known limitations are
quantified, and two attributes are flagged for reformulation. That is what
credibility looks like — not uniform green.
