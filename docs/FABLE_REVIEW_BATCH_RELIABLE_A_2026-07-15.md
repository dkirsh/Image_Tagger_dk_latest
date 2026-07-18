# FABLE REVIEW BATCH — Sprint Reliable-A
### Two-layer adversarial brief · 2026-07-15 · to be run when Fable is activated

*David's instruction: "have Fable review the decisions and advise me, and have Fable attack and
evaluate the reviews." This batch is self-contained: it names every artifact (verified absolute
paths), the decisions to weigh, and the two-layer protocol.*

---

## 0. Absolute-path manifest (all verified present on the Mac after commit)

Repo root: `/Users/davidusa/REPOS/Image_Tagger_dk_latest`
- Predicates: `annotation_socket/predicates/triangulation.py` (C01), `.../stranded_amenity.py` (C29),
  `.../fractal_band.py` (V9); `cnfa_algs/reliable_attrs.py` (V2,V13,V1,V6,V7);
  edited `cnfa_algs/attributes.py` (fractal raw-field/R² exposure).
- Wiring: `annotation_socket/registry.py`, `annotation_socket/annotator.py`
  (incl. `tier_a_view`), `annotation_socket/verify.py` (mode-aware coverage).
- Tests (all PASS in sandbox): `annotation_socket/tests/test_c01_triangulation.py`,
  `test_c29_stranded.py`, `test_v9_fractal_band.py`, `test_reliable_attrs.py`.
- Specs/plans: `annotation_socket/predicates/C01_..._SPEC_...md`, `C29_..._SPEC_...md`;
  `docs/SPRINT_RELIABLE_A_MASTER_PLAN_2026-07-15.md`, `docs/DECISIONS_LOG_RELIABLE_A.md`,
  `docs/SPRINT_MOST_RELIABLE_ATTRIBUTES_2026-07-15.md`, and this file.

## 1. What was built (batch under review)

| ID | Attribute | Ceiling | Determinism | Core test |
|---|---|---|---|---|
| C01 | triangulation_ignition (compound) | AMBER | exact ×3 | on-path 0.484 vs corridor 0.0 |
| C29 | stranded_amenity_index (compound) | AMBER | exact ×3 | conjunction fires 0.73; on-path/wall ~0 |
| V9 | fractal_mid_d_band_score | GREEN | exact ×3 | inverted-U; chaotic D→0.09 |
| V2 | spectral_discomfort_deviation | GREEN* | exact | 1/f slope −1.97; stripes>natural |
| V13 | edge_orientation_entropy | GREEN | exact | isotropic 0.998>grid 0.301 |
| V1 | contour_angularity_index | GREEN | exact | curves 0.94>angles 0.13 |
| V6 | subband_entropy_clutter | GREEN | exact | cluttered>blank |
| V7 | feature_congestion_clutter | GREEN | exact | cluttered 0.72>blank 0.0 |
| — | Tier-A GREEN pass (`tier_a_view`) | — | — | `_open.png` → unit GREEN 15/15 |

*V2 self-gates to AMBER per-image when its 1/f fit R²<0.9 (honest).

## 2. LAYER 1 — Fable REVIEWS the work (advise David)

Run the standard 9-seat correctness panel (`docs/PANEL_REVIEW_PROMPT.md`) with a seat per
relevant expertise (spectral/psychophysics for V2; Redies/orientation for V13; Bar-Neta/curvature
for V1; Rosenholtz for V6/V7; Taylor/fractal for V9; Whyte/Hillier/space-syntax for C01/C29).
For EACH predicate, execute the code and answer:
1. **Does it compute what it claims?** Re-derive on ≥2 images; is the number the construct?
2. **Are the literature anchors real and correctly used?** Flag any invented/overclaimed (the V1
   Vartanian-approach clause was pre-stripped; V9 stress-leg pre-labeled preliminary — confirm).
3. **Is the GREEN/AMBER ceiling honest?** Especially: does V2's FOV=65° assumption (Decision D3)
   invalidate the discomfort magnitude? Should only the scale-free slope ship GREEN?
4. **Hidden confounds / double-counting?** V6/V7/legacy clutter redundancy (Decision D2); V1
   object-contour confound (D4); photographic-style confounds on all FFT/fractal measures.
5. **Would you certify it for the cognitive-code register?** GREEN-eligible or not, and why.

Then review the **DECISIONS** in `DECISIONS_LOG_RELIABLE_A.md` (D1–D7) and advise David on each:
is the default right, and what would change it? D2 (retire the legacy clutter proxy?) and D3
(V2 FOV) are the two highest-stakes calls.

## 3. LAYER 2 — Fable ATTACKS the reviews (adversary-of-the-adversary)

A second Fable pass takes Layer 1's reviews as INPUT and tries to REFUTE them:
- Where a Layer-1 seat said "VIABLE / certify," find the counter-case: an image or construct
  argument where the predicate misleads, that the reviewer missed.
- Where a Layer-1 seat said "KILL / demote," check it isn't over-cautious — is the objection real
  or a generic caveat dressed as a defect?
- Grade each Layer-1 review CONFIRMED / OVERTURNED / INCOMPLETE, with the specific miss.
- Special target: the **negative controls and M1 replay** — can a fabricated value be crafted that
  survives replay (a value computed from the image by a DIFFERENT procedure that happens to match)?
  That is the one attack the mechanical gate cannot self-run.

## 4. Ground truth still owed (do NOT let either layer assume these done)

- Cross-environment exact-replay (Mac↔sandbox OpenCV/numpy) per predicate — GREEN demotes to
  AMBER if it drifts (lesson L10). Run the harness once on the Mac.
- Article_Eater / Knowledge-Atlas grounding of every literature anchor.
- A labeled A-vs-B image set to calibrate C01/C29 gate thresholds (currently declared defaults).

## 5. Output Fable should return
A per-predicate verdict table (compute-correct? evidence-real? ceiling-honest? certify?), a per-
decision recommendation (D1–D7), and the Layer-2 grades of the Layer-1 reviews — so David gets
both the advice and the adversarial check on the advice in one artifact.
