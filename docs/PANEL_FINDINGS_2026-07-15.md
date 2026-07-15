# Ruthless Panel — Findings on C1–C24 and the CNfA Engine

*Synthesis of a nine-seat adversarial review run 2026-07-15 (Fable panelists P1–P9 per `PANEL_REVIEW_PROMPT.md`). Every
panelist read AND executed the code in the sandbox; every finding below carries a concrete failing input and the wrong
output it produced. This document deduplicates across panelists, ranks by severity and leverage, gives a per-criterion
verdict for all of C1–C24, and states the overall verdict. It is not gentle by design — that was the assignment.*

**Headline verdict.** The core claim — *these attributes correctly compute the constructs they name* — is **NOT
SUPPORTED as shipped**, but the failure is not diffuse rot: it concentrates in (a) a few copy-pasted primitive bugs that
cascade through many criteria, (b) a set of "construct substitutions" where a metric measures something other than its
name, and (c) an aggregator that manufactures confidence the components have not earned. The *architecture*, the
*disclosure culture* (failure_modes, over-claim watchlists, the ✓/◐/○ map, "geometric screen not melanopic"), and the
*specification* are genuinely strong and above the average of research code. Most defects are fixable, and several are a
single shared-helper fix. But **the validation harness passed all batteries on the very code exhibiting every defect
below** — so the most important lesson is that the green checkmark certified that the code ran and ordered extremes, not
that the numbers are right.

---

## 1. Systemic issues (cross-cutting — fix these first; each one repairs many criteria)

**S1 — The diagonal-wall line-of-sight leak, copied into six modules. [CRITICAL]** (P3, P4, P5, P9)
`_los` / `_visible` / `_seat_isovist` sample the ray at `max(|Δr|,|Δc|)+1` points, so a one-cell-thick *diagonal* wall
is transparent. All six copies (movement, acoustics_plan, daylight_view, space_syntax, affordance, wellbeing_plan) share
it. Verified: on a grid split by a solid diagonal wall, speech STI reads **0.705 behind the wall** ("walls give privacy"
→ expect 0); a window view is reported **through** a solid partition; 244 sealed-off cells receive sound; VGA edges and
geodesic distances cross the wall (14.7 m "path" where none exists). Any rotated/rasterized floor plan produces exactly
these one-cell diagonal chains. **Fix:** one shared supercover LOS helper (test both orthogonal neighbours at each
diagonal step), replacing all six copies. This single fix touches C1–C12, C15, C19, C23.

**S2 — Unseeded `cv2.kmeans`: the geometry is nondeterministic and the published numbers are irreproducible. [CRITICAL]**
(P2, P9) `segment_planes` and `palette_entropy` call `cv2.kmeans` with `KMEANS_PP_CENTERS` and no `cv2.setRNGSeed`. Same
image, same process: plane labels change on **29% of pixels** between calls; `palette_entropy` returns 0.978 / 0.994 /
0.987; prospect on the corridor spans **{36.8, 52.2, 815.0} m** across runs. The worked-example `scalars.json` is
reproduced by *no* fresh run. The `failure_modes` claim "fixed seed" is false. Because segmentation feeds depth → plan →
every plan metric, the entire Tier-B chain is nondeterministic. **Fix:** `cv2.setRNGSeed(fixed)` before every kmeans;
regenerate and re-verify every published scalar.

**S3 — Within-plan percentile normalization inverts or destroys the signal. [CRITICAL]** (P1, P2, P3, P8)
`_norm` (feeding C1/C2), `integration_at` (feeding C14), the isovist fields, and the `normalize01` used in
`edge_clarity`/`landmark`/`processing_load` fields all normalize to a 2–98% *within-image* range. Consequences:
`integration_norm` is a skewness statistic — an **open studio (maximal integration) scores 0.0** while a **snake corridor
scores 0.378**, an outright ranking inversion at the COG profile's dominant weight; `edge_clarity`'s field is **all zeros
on the sharpest possible edge**; `landmark` hallucinates a bounding box on a blank wall; C14's "high-integration"
threshold collapses to 0.0 everywhere on a uniform plan, so it **passes the unzoned floor it exists to catch**. **Fix:**
remove within-plan normalization from every scoring path; use absolute / RRA-normalized quantities.

**S4 — Grid ignored: Euclidean-through-walls. [HIGH]** (P6, P9) `thermal_plan` fetches `pg.grid` and never uses it — a
seat fully walled off from glazing is flagged for radiant risk and awarded a sun patch (sun through a wall).
`wellbeing_plan` measures retreat/commons "reach" with straight-line `np.hypot` through walls; `restoration_nature`'s LOS
even requires the *nature cell itself* to be FREE, so on any real plan (glazing on the wall ring) **C19 is 0.0 for every
seat, silently**. **Fix:** gate all "reach"/"access" by LOS or geodesic distance; use the endpoint-exempt LOS.

**S5 — The aggregator manufactures confidence. [HIGH]** (P8, P5) `score_layout` violates three of its own stated
disciplines: the headline is a **weighted mean** while docstring and CRITERIA §1.2 call it "min-not-mean, never lifted by
the best" (COG headline 0.627 sits *above* its weakest criterion 0.042 and worst-served type 0.2); a **missing dominant
criterion silently renormalizes away**, and C14 is **fabricated as 1.0** when C7 is absent (default STI 0 = perfect
privacy), so a layout is rewarded for withholding its worst evidence (+0.114 COG); **C8 is layout-invariant** (a pure
function of two scalar defaults → 0.88 for every layout on earth) yet carries co-dominant weight; the promised
"provenance ledger" does not exist and **C10/C22 double-count** the same distance-to-window (C22 is an affine copy of
C10, recomputed); the evidence-tag "cap" and the non-additivity "caveat" are **prose, not mechanism** (the caveat is a
grepped hard-coded string with zero computational role). **Fix:** report scored-weight coverage and refuse to compare
layouts at different coverage; never fabricate from a default; implement min-bounding, the ledger, and the cap — or stop
claiming them.

**S6 — The validation harness has structural blind spots; "ALL BATTERIES PASS" over-certifies. [HIGH]** (all panelists)
Every wall in every battery is axis-aligned (misses S1); every glazing/nature/seat cell is FREE (misses C19-always-0,
seat-in-wall, talker-on-OBST); the determinism battery tests only `score_layout` on a plan-only scenario and excludes the
image tier where the nondeterminism lives (misses S2) while its title claims "no hidden randomness in the metrics"; the
discrimination battery is mostly saturated 1.0-vs-0.0 endpoint pairs, **tests transforms the aggregator doesn't use**
(C8's `1−r_D/20` and C1/C2's raw connectivity, not the aggregated `integration_norm`), **omits C3/C4/C14 entirely**, and
never exercises hedonics; several module self-tests assert trivially-true things or use *different seats for the two
functions* to sidestep the overlap they should test. **Of the panel's ~40 distinct findings, the harness as written
catches zero.** **Fix:** an adversarial battery — diagonal walls, wall-adjacent targets, invalid/NaN/empty inputs,
determinism on the image tier, mid-range discrimination with a minimum margin, and the aggregator's real transforms.

**S7 — Construct substitution: metrics that name one thing and compute another (and cite a safeguard they don't run).
[HIGH]** (P3, P4, P6, P7) `perceived_crowding_risk` (C12) has **no density term** though CRITERIA.md's formula names one,
and measures LOS visibility instead — a 60 m-apart pair in an airy hall scores *maximally crowded* (0.0), packed
partitioned desks score *perfectly uncrowded* (1.0); `social_connectedness` (C23) advertises F6's refuge-pairing
("exposure ≠ connectedness") in its docstring and **does not implement it**, so a maximally exposed zero-refuge seat
scores 0.917 connected; `solar_patch_opportunity` claims a summer-overheat guard that **does not exist** (a seat is
simultaneously at-risk and an opportunity); `prospect_refuge_quality` (C11) rewards **entrapment** (a sealed booth
out-scores an ideal back-to-wall seat on refuge). A named safeguard that isn't run is the most corrosive over-claim,
because the honesty banner itself becomes false.

**S8 — The ✓/◐/○ status map is inaccurate in both directions. [MEDIUM]** (P3, P6, P8) CRITERIA.md §3/§7 still mark
C5, C7–C10, C13, C21 as ○ "not yet built" — they *are* built and scored; meanwhile C14 (marked ○) is live in the scorer
at weight 0.7 tagged STRONG, and C24 (defined as needing a Tier-C height field) is scored from a 2D proxy. The
programme's credibility rests on this map being accurate; regenerate §3 from the code.

---

## 2. Per-criterion verdict — all of C1–C24

| # | Criterion | Verdict | The decisive finding (executed) |
|---|---|---|---|
| C1 | visual integration | **WRONG** | `_norm` skewness → open studio 0.0 < snake corridor 0.378; no RRA; 1e6 sentinel inverts ranks on any isolated pocket |
| C2 | connectivity / movement | **WRONG (as scored)** | raw counts are fair, but `connectivity_norm` inverts (studio 0.0 vs corridor 0.814) |
| C3 | intelligibility | **CRUDE-BUT-HONEST (formula) / WRONG (stability)** | genuinely Hillier's R², but ±0.05 with stride and emits unflagged 0.002 when the sample disconnects at the default stride |
| C4 | wayfinding load | **WRONG** | every interior cell is a "junction" → easiest plan scored near-worst (0.08); flips 0.08→1.0 on an optional argument |
| C5 | collaborator proximity | **CRUDE-BUT-HONEST (orthogonal) / WRONG (diagonal)** | geodesics exact to 1e-4 m on axis-aligned plans; 14.7 m "path" through a sealed diagonal wall (S1) |
| C6 | path overlap (opportunity) | **CRUDE-BUT-HONEST** | fair Kabo-style proxy, honestly weight-0; inherits S1 |
| C7 | focus speech privacy | **CRUDE-BUT-HONEST on face / anti-conservative in effect** | binary privacy: a single 0.3 m obstacle → STI 0; talker-on-OBST → whole field 0 → "all protected" 1.0 |
| C8 | distraction distance r_D | **WRONG** | 1 m-anchored single slope ≠ ISO's two-DOF regression (r_D 4.52 "good" vs real 8.72 "fair"); **layout-invariant** at dominant weight |
| C9 | view equity | **CRUDE-BUT-HONEST + WRONG specifics** | honest LEED-style hedge; but LOS leaks through diagonal walls and 7.5 m conflates LEED's two distances (vs CRITERIA's own 3×head-height) |
| C10 | daylight / circadian | **CRUDE-BUT-HONEST** | the melanopic over-claim is *not* there — disclosure is honest throughout; defects are the S1 LOS leak and a default at the generous end of its own range |
| C11 | prospect–refuge quality | **WRONG** | refuge rewards entrapment (sealed booth 0.609 > ideal seat 0.484); not prospect-led at realistic values; seat-in-wall scores best |
| C12 | perceived-crowding risk | **WRONG** | no density term (CRITERIA demands it); LOS-visibility inverts (60 m hall = worst, packed desks = best); junk off-site retreats launder the score |
| C13 | setting variety / fit | **WRONG** | enclosure conflated with smallness (a 30 m² focus room = "open_field"); fit-matrix cells are hand-set constants identical across layouts |
| C14 | focus:collaboration separation | **WRONG** | relative-percentile threshold passes the exact unzoned plan it exists to catch (1.0); fabricated 1.0 when C7 absent; marked ○ yet scored 0.7/STRONG |
| C15 | active-design movement | **CRUDE-BUT-HONEST** | stair/amenity logic is sound; inherits S1 |
| C16 | territory provision | **CRUDE-BUT-HONEST** | honest spec calc; headcount=0 silently reads as pure hot-desking |
| C17 | functioning local control | **CRUDE-BUT-HONEST** | correctly credits control only vs the binding stressor (the whole point of C17) |
| C18 | air-quality spec | **CRUDE-BUT-HONEST + WRONG edges** | CO₂-as-proxy honest, watchlist cited; but Q=0 → 5.2 billion ppm reported as-is, NaN propagates into the blended score, headcount decorative |
| C19 | restoration / nature | **CRUDE-BUT-HONEST (saturation) / WRONG (real plans)** | retreat-OR saturates ("67% restorative" with zero nature); nature-on-wall LOS → **C19 = 0.0 on every realistic plan** (S4) |
| C20 | chronic-stress soundscape | **CORRECT construct / WRONG for enclosure** | genuinely distinct from C7; but walls transmit at 0 dB, so enclosing the source — the one containing move — earns no credit |
| C21 | thermal comfort / zoning | **WRONG** | radiant misses the <1 m cold-glazing rule (ASHRAE ordering inverted); zone-mismatch passes E+W and N+INT textbook failures; sun through walls; doc says ○/PMV, scored at weight 1.0 |
| C22 | circadian day–night | **WRONG** | additive where B1 is conjunctive (windowless basement = 0.3); an affine copy of C10 double-counted in the WB profile |
| C23 | social connectedness | **WRONG** | claims F6 refuge-pairing it does not implement (max exposure = 0.917 "connected"); empty office scores 0.5 |
| C24 | awe / spatial generosity | **CRUDE-BUT-HONEST (under-disclosed)** | 2D openness ratio labelled "awe"; a flat warehouse (0.206) out-scores its own cathedral example (0.195); no-height honestly flagged, near-zero discrimination not |

Tally: **11 WRONG** (C1, C2, C4, C8, C11, C12, C13, C14, C21, C22, C23), **3 mixed/WRONG-on-real-inputs** (C3, C5, C19),
**8 CRUDE-BUT-HONEST** (C6, C7, C9, C10, C15, C16, C17, C24), **1 CORRECT-construct-with-a-bug** (C20), plus C18
honest-with-edges. No criterion was found fully CORRECT end-to-end; the closest are C6, C10, C16, C17.

---

## 3. What is genuinely sound (credit where the panel gave it)

- **`hedonics.py` is the strongest, most honest component in the stack** (P1, P7). The response shapes are right
  (symmetry monotone-positive; complexity/entropy/fractal forced inverted-U per Berlyne/Graf-Landwehr/Taylor; hue
  *abstains* per Elliot & Maier), every licensed value is stamped `promising-import`, and `validate_hedonic_registry`
  blocks a complexity attribute from ever being monotone. This is exactly the lab→building honesty the review demanded.
- **The over-claim watchlists are load-bearing and verified effective** (P8). No watchlisted number (the 46-minute sleep,
  61/101% COGfx, 15% plants, 10,000 steps, smoking-equivalence, any melanopic value) survives into a coefficient;
  `air_quality` even cites the watchlist in its own failure_modes.
- **`movement.py` geodesics are the grid-honesty exemplar** (P3, P9): analytically exact on orthogonal plans, true
  network distance, seats snapped to FREE. (It still inherits S1 on diagonal geometry.)
- **The daylight/circadian disclosure is honest** (P5): the melanopic/sDA over-claim the reviewer was sent to find is
  not there — module, scorer, CRITERIA marks, and the worked example all state "geometric screen, not certified."
- **The disclosure culture overall** — failure_modes on nearly every result, confidence fields, the HONEST SCOPE headers
  (thermal especially), the ○ marks — is above the average of academic code, even where the numbers underneath are wrong.

---

## 4. Fix priority (highest leverage first)

1. **One shared supercover LOS helper** (S1) — repairs a slice of C1–C12, C15, C19, C23 at once, and makes "walls block
   X" true. Highest leverage single change in the codebase.
2. **Seed `cv2.kmeans`** (S2) — restores determinism, then regenerate and re-verify every published scalar (the worked
   example included).
3. **Remove within-plan percentile normalization from all scoring paths; use RRA / absolute quantities** (S3) — fixes the
   C1/C2/C14 rank inversions and the zeroed/hallucinated fields.
4. **Make the aggregator honest about coverage and absence** (S5) — never fabricate C14 from a default; drop unmeasured
   criteria and surface scored-weight fraction; make C8 plan-dependent or demote it; implement the provenance ledger and
   min-bounding, or delete those claims.
5. **Gate every "reach/access/radiant" by LOS/geodesic; use the grid the functions already take** (S4) — fixes C19 on
   real plans, thermal-through-walls, junk-retreat laundering.
6. **Repair the construct substitutions** (S7): add C12's density term; implement or strike C23's F6 refuge check;
   implement or strike C21's zone-phase and cold-glazing logic and solar_patch's overheat guard; re-parameterize C8/r_D
   on ISO's (D2,S, Lp,A,S,4m) pair.
7. **Replace the friendly-quadrant self-tests and the harness with the adversarial battery** (S6) — diagonal walls,
   wall-adjacent targets, invalid/NaN/empty inputs, image-tier determinism, mid-range discrimination with margins, and
   the aggregator's actual transforms. Until this exists, "all batteries pass" should not be quoted as verification.
8. **Regenerate the ✓/◐/○ map from the code** (S8); fix the image-attribute defects P1 detailed (chromatic-blind symmetry,
   k-means palette entropy, uncalibrated hedonic input scales, the processing_load field bugs, sentinel leaks).

---

## 5. Method and boundary (RULE 0)

Nine Fable panelists (P1 Oliva image-attributes, P2 Hoiem geometry/depth, P3 Sailer space-syntax, P4 Hongisto acoustics,
P5 Reinhart daylight, P6 de Dear thermal, P7 Vartanian affordance/aesthetics, P8 Gelman aggregation/validation, P9
numerical red-team) each ran `PANEL_REVIEW_PROMPT.md` against its assigned modules in the sandbox, reading and *executing*
the code with adversarial inputs. Every quantitative claim above was reproduced by execution this session on synthetic
and worked-example inputs; the panel did **not** re-derive ISO/LEED/ASHRAE thresholds against the priced primary
standards, did not run a spectral daylight or pyroomacoustics simulation (pyroomacoustics is absent from the sandbox, so
`acoustics_sim` execution claims are UNVERIFIABLE here), and did not test non-divisible image sizes for the
processing_load padding bug beyond arithmetic. Evidence-grade judgments are from the panelists' domain knowledge, not a
fresh literature pull. The findings are about the code as it stands on 2026-07-15 (branch `cnfa-algs-2026-07-14`); they
are a map of what to fix before any criterion is trusted as fact, not a dismissal of the programme — the specification
and disclosure culture that made this audit possible are themselves an asset most such systems lack.
