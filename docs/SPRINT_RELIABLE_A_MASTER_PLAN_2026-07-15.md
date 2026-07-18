# SPRINT "RELIABLE-A" — MASTER PLAN (with periodic adversarial validation)
### Image_Tagger CNfA · drafted + executed 2026-07-15 (Cowork)

## 0. Intent

Build the **most reliable** attributes — the GREEN, Tier-A, deterministic, exact-replay
primitives that do NOT ride the heuristic inferred plan — as socket predicates, each fully
tested, with **adversarial validation gates every two predicates** and a **commit/push step at
each gate**. Then hand a single batch to Fable to attack (decisions + code + reviews). This plan
is executed autonomously; every non-obvious choice is logged with pros/cons in
`DECISIONS_LOG_RELIABLE_A.md` and a default taken so work never blocks.

## 1. Backlog (reliability-ranked; C01/C29/V9 already done)

| Ticket | Attribute | Ceiling | Effort | Status |
|---|---|---|---|---|
| done | C01 triangulation_ignition (compound) | AMBER | — | ✅ built+tested |
| done | C29 stranded_amenity_index (compound) | AMBER | — | ✅ built+tested |
| done | V9 fractal_mid_d_band_score | GREEN | XS | ✅ built+tested |
| T-R2 | V2 spectral_discomfort_deviation | GREEN | S | this sprint |
| T-R3 | V13 edge_orientation_entropy | GREEN | S | this sprint |
| T-R4 | V1 contour_angularity_index | GREEN | M | this sprint |
| T-R5 | V6/V7 Rosenholtz clutter + consolidation | GREEN | M | this sprint |
| T-R6 | Tier-A-only GREEN pass mode | — | S | this sprint |

## 2. The per-predicate recipe (proven on C01/C29/V9)

1. `cnfa_algs` function — pure numpy/OpenCV, deterministic (seed; restrict FFT bands off Nyquist).
2. Registry entry — `image_attr`, `replayable`/`replayable_tol`, `GREEN`.
3. Route through the `derivation` chokepoint (scored/abstain/unknown).
4. Pure-core unit test + M1 exact-replay + a negative control — **run it** (no ship untested).
5. Annotator binding (cache shared upstreams so nothing computes twice).
6. `run_stage` on ≥3 real interiors → SCORED + traceable + determinism across 3 runs.

## 3. Periodic adversarial validation — the GATES

The sprint is punctuated by validation gates. Because Fable is OFF now (a big batch runs later),
each gate PACKAGES an adversarial review item rather than running it live. The gate artifact is a
self-contained attack brief the Fable panel will execute.

- **Gate G1 — after V2+V13:** package review item `REVIEW_G1` (attack V2/V13: is the computation
  what it claims? are the anchors real? does GREEN survive exact replay? hidden confounds?).
  **Commit + push.**
- **Gate G2 — after V1+V6/V7:** package `REVIEW_G2` (attack V1 curvature + the clutter
  consolidation / legacy-proxy-retirement decision — the highest-risk call in the sprint).
  **Commit + push.**
- **Gate G3 — after Tier-A pass mode + all decisions:** assemble the **master Fable batch**
  (`FABLE_REVIEW_BATCH`): every predicate (C01,C29,V9,V2,V13,V1,V6/V7) + the full decisions log,
  with the two-layer instruction — (a) review the decisions and advise David; (b) ATTACK the
  reviews themselves (adversary-of-the-adversary). **Commit + push.**

Each gate also runs the **existing mechanical gate** (`run_stage`) as the machine floor before the
human/Fable layer — fail-closed RED on any fabrication, per the socket contract.

## 4. Commit / push step (run in Mac Terminal at every gate)

```bash
cd /Users/davidusa/REPOS/Image_Tagger_dk_latest
rm -f .git/index.lock
git add annotation_socket cnfa_algs docs README.md
git commit -m "sprint reliable-A: GREEN Tier-A predicates + adversarial-gate packages"
git push latest cnfa-algs-2026-07-14
git push origin cnfa-algs-2026-07-14
```
(`git add` names dirs so all new predicate/test/doc files are swept in; root-level zips/_to_delete
stay untracked. `-f` never used. If a push is rejected: `git pull --rebase latest cnfa-algs-2026-07-14`
then push again.)

## 5. Definition of done (sprint)

- V2, V13, V1, V6/V7 each: unit test PASSES (run), `run_stage` SCORED + traceable, determinism
  ×3, negative control REJECTED. Tier-A pass mode returns GREEN-eligible units.
- Every non-obvious choice in `DECISIONS_LOG_RELIABLE_A.md` with pros/cons + default taken.
- Three gate review packages written; master Fable batch assembled and ready to run.
- All committed + pushed to both GitHub remotes.
- **Owed after the sprint (explicitly not claimed done):** cross-environment (Mac↔sandbox) exact-
  replay check per predicate (lesson L10); Article_Eater anchor grounding; the live Fable panel
  run. These are the batch David triggers next.

## 6. Risks
- GREEN over-claim → GREEN is earned by exact replay; any Mac↔sandbox drift demotes to
  replayable_tol (checked in the owed cross-env pass).
- Photographic-style confounds (exposure/JPEG/defocus shift FFT/fractal/clutter) → each predicate
  emits an image-quality caveat.
- Double-counting into hedonics (V6/V7 vs legacy clutter) → see Decision D2 (consolidate, do NOT
  delete without corpus proof — RULE 0).
