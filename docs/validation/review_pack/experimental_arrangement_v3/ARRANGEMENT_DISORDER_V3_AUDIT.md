# Arrangement-disorder v3 candidate audit

**Run date:** 2026-07-31 PDT

**Status:** AMBER experimental candidate; **not promoted over the canonical v2 review pack**

**Producer commits:** `aeca2181` (measure) and `623040cf` (zero-confidence replay abstention)

## What changed

The v2 arrangement proxy compared the PNG byte size of a 48 x 48 grayscale image with a
pixel-shuffled copy. It never identified furniture or measured placement. Texture, tonal noise, and
resampling could therefore dominate the result.

The v3 candidate:

1. smooths the image and detects coarse edge-bounded regions;
2. removes nested duplicate contours;
3. selects the largest family of similarly sized and shaped regions;
4. scores irregularity of alignment, nearest-neighbour spacing, neighbour directions, and element
   orientations;
5. abstains when it finds fewer than four repeated regions or when fine-edge density dominates; and
6. retains the v2 compressibility ratio only as a named legacy diagnostic.

It remains an uncalibrated hypothesis. Its regions are not semantic furniture instances.

## Fail-then-pass controls

The old implementation failed the new contract tests because it had no region evidence, no abstention,
and no placement measure. The candidate passes:

- deterministic output and explicit weak-evidence disclosure;
- fine random texture -> `texture_dominated_abstention`, severity `0.5`, confidence `0.0`;
- same-element regular grid scores below same-element scattered placement;
- the hand-built teaching sequence orders low < intermediate < high; and
- the intentional clustered layout scores below the scattered layout.

Teaching-schematic scores:

| panel | severity | repeated elements |
|---|---:|---:|
| low, regimented | 0.001304 | 8 |
| intermediate, slightly off | 0.243817 | 8 |
| high, scattered | 0.351673 | 8 |
| ambiguous, intentional clusters | 0.226538 | 8 |

The complete annotation suite passed: **55 passed in 120.00 s**. After the replay-abstention repair,
the two focused files passed **5/5** and **13/13** tests respectively. The replay was run twice and all
three outputs were byte-identical.

## Corpus replay

The replay covered all 540 `corpus_L6` images and emitted 3,240 image-species rows.

| arrangement evidence/result | count |
|---|---:|
| measured repeated elements | 328 |
| insufficient repeated elements | 139 |
| texture-dominated abstention | 73 |
| flattened absent | 128 |
| flattened present | 200 |
| flattened abstain | 212 |

The v2 proxy classified 534/540 images as present. V3 removes that gross imbalance, but it does so partly
by abstaining on 39.3% of the corpus. Among measured images, evidence quality ranges from 0.069565 to 1.0
(median 0.557778). New placement scores correlate only 0.184111 with the retired compressibility ratio,
which confirms that the candidate is measuring a substantially different signal.

## Adversarial findings

### 1. Perspective false positive

`interiors/sun397_conference_center__a3b0eef184_conference_center.png` is visually regimented: repeated
chairs are arranged in rows. V3 nevertheless scores it `0.829909`, near the corpus maximum. Perspective
changes apparent size, spacing, and orientation; the edge-family detector also cannot prove that all of
its selected regions are chairs.

### 2. Photometric non-invariance

The 82 A-base/B-variant pairs preserve layout while changing glare, contrast, daylight, or warmth. V3
score differences were:

| statistic | absolute difference |
|---|---:|
| mean | 0.0542 |
| median | 0.0012 |
| p95 | 0.2221 |
| maximum | 0.4581 |
| evidence-status flips | 6 |

The worst pair was `gab_743e4df7_A_base` versus `gab_743e4df7_B_warmth`: `0.4730` versus `0.0150`.
Thus the candidate is usually stable but fails badly on a minority of photometric transformations.

### 3. Extreme-rank contamination

Several highest-ranked images plausibly contain disarray, including the fast-food restaurant and cluttered
office. Others are false or doubtful: the regimented conference room, and glare variants whose geometry
did not change. The extreme list is therefore not an answer key.

## Decision and next gate

Keep v3 as an **experimental HITL hypothesis generator**, not a production measure. The canonical v2
review pack remains untouched because v3 failed the perspective and photometric controls. V2 is not thereby
endorsed; it remains texture-confounded and highly imbalanced.

A credible next version needs semantic instance segmentation for furniture or other layout anchors, plus
perspective normalization (depth/ground-plane projection where reliable). Before promotion it must:

1. preserve the teaching ordering;
2. abstain on texture-only controls;
3. score the regimented conference room below the scattered teaching case;
4. pass the 82-pair invariance gate with no evidence-status flips, p95 absolute difference <= 0.10, and
   maximum <= 0.20; and
5. survive David/Stephan review of matched real-photo low/intermediate/high anchors.

## Experimental artifacts

- `hypotheses_corpusL6.jsonl`: SHA-256
  `4e0bcb03647e243c03148df20c302b859002ef5ac55bbb8e880460618e759881`
- `queues.json`: SHA-256
  `af486ed9ffc0a61561fc3550e5ad21c610cdac62eb17eb42b64460ad4de2a4db`
- `replay_manifest.json`: file SHA-256
  `f35250fc449e71c8051dfd420d990753cec036405508b5e4743b781ebedf470d`;
  canonical manifest hash
  `3fe5bf47a2289e0ca55d6f16076512a31143417d44a117e4a5df3dd7c9f9068f`
