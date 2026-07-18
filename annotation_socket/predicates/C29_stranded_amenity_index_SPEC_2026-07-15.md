# SPEC — C29 `stranded_amenity_index`  (the next attribute, recommended)
### Second compound predicate for the annotation socket · 2026-07-15

**Repo (verified): `/Users/davidusa/REPOS/Image_Tagger_dk_latest`**
**Why this one next:** it reuses the *exact* machinery C01 just proved in-sandbox (landmark
salience + desire-line ridge + cross-tier registration), so marginal build cost is low and
confidence is inherited; it rests on Whyte's single most-replicated observation (**High**
confidence); and it is C01's **diagnostic inverse** — C01 says *where talk ignites*, C29 says
*where beautiful design is wasted* — so the two together are the sharpest region-A-vs-B pair the
panel produced. Impact-plan rank #2 (Wave 1).

---

## 1. The compound claim

Whyte's finding: an attractive amenity (lounge, feature seat, art, coffee point) delivers social
life **only if it sits where people already move**; the same amenity off the desire line is
admired and empty. C29 is a **warning flag** — high value = high appeal but near-zero delivered
encounter:

```
stranded = appeal01 · (1 − gate(dist_to_desire_line)) · seat_affordance01
```

where `appeal01` = salience/amenity strength, `gate` is C01's Gaussian co-location gate, and
`(1 − gate)` is high exactly when the amenity is FAR from the ridge. `seat_affordance01` (a
sittable/usable-surface cue) keeps the flag from firing on a mere picture on a back wall.
**The interaction is the point:** appeal alone, or off-ridge distance alone, cannot fire it — a
plain sculpture in a busy hall (appeal high, distance ~0 → `1−gate`≈0 → not stranded) and a bare
dead-end (distance high, appeal ~0 → not stranded) both correctly read ≈0. Only *appeal AND
off-path AND usable* co-occurring flags a genuine stranded amenity.

**Human effect & sign.** Raising C29 **WORSENS realized social outcomes** — it marks design
investment that will NOT convert to encounter. A high value is *bad news*, a redesign flag (move
the amenity onto the spine, or bring a path to it).
**Social forms:** the *absence* of fleeting co-presence / triggered conversation despite apparent
affordance.
**Confidence in effectiveness: High** — Whyte 1980 (empty well-appointed plazas), Gehl 2010
(life follows the desire line), and it inherits C01's verified ridge/registration mechanics.
**Measurement ceiling: AMBER** (same inferred-plan + cross-tier registration as C01).

## 2. Base measures composed (all already computed — none recomputed)

| Base measure | Source | Role |
|---|---|---|
| `landmark_salience(img)` scalar + bbox | `attributes.py:198` | amenity appeal + location |
| C1 integration ridge (`vga_metrics`) | `space_syntax.py:50` | the desire line |
| C01's `gate`, `ridge_cells`, `pixel_to_plan_cell` | `predicates/triangulation.py` | **reused verbatim** — shared, tested |
| seat/soft-surface affordance cue | `attributes.acoustic_absorption` material map / `affordance.py` | "is it actually usable/sittable" |

*Reuse note:* C29 imports `gate`, `ridge_cells`, `dist_to_ridge_m`, `pixel_to_plan_cell` from
`triangulation.py` — do not duplicate them (L9: shared function is a contract).

## 3. Tri-state (success conditions + last-mile checks)

| State | Condition | Output |
|---|---|---|
| **SCORED (value)** | amenity dE ≥ `SALIENCE_FLOOR`, registered to a plan cell (`reg_conf ≥ REG_FLOOR`), seat-affordance computable | `value ∈ [0,1]`, `plan_chain` evidence {anchor cell, dist_to_ridge_m, 1−gate, appeal01, seat_afford01} |
| **SCORED = 0.0** | no salient amenity (dE < floor) OR amenity is ON the ridge (`1−gate` ≈ 0) | genuine zero — nothing stranded; `global_image` or `plan_chain` evidence naming which |
| **UNKNOWN** | amenity detected but `reg_conf < REG_FLOOR`, or geometry `< GEOM_FLOOR` | fail closed → RED (never guess the location) |

**Last-mile validations:** (1) the flag must fire ONLY on the conjunction — unit-test that
on-ridge amenities and off-ridge blank walls both score ≈0 (a disguised `appeal × distance` sum
would mis-fire); (2) `seat_affordance01` prevents firing on wall art with no dwell surface;
(3) same cross-tier registration guard as C01 — `reg_conf < REG_FLOOR` ⇒ UNKNOWN.

## 4. Contract / evidence / M1

Registry: `_spec("C29.stranded_amenity_index", "plan_metric", PLAN, "replayable_tol", "AMBER", …)`.
Evidence = `plan_chain` with the amenity cell, `dist_to_ridge_m`, `1−gate`, `appeal01`,
`seat_afford01`, + geometry upstream. `audit_class=replayable_tol`: verify() re-derives from
image bytes, demands match within TOL. **Negative controls (unit test):** (a) a stored high value
on an amenity actually ON the ridge recomputes to ≈0 → RED; (b) a stored high value on a blank
off-ridge wall (appeal≈0) recomputes to ≈0 → RED. **Double-count guard:** own diagnostic field,
excluded from `score_layout` (shares salience + integration with C01 and the aggregate).

## 5. Region-A-vs-B demonstration (the deliverable claim)

> Beautifully furnished lounge at a dead-corridor end → **high stranded index** (appeal high,
> off the desire line, empty) vs a plain bench on the main spine → **low index** (appeal modest
> but constantly used). C29 is INVERSE to C01 on the same scene, so scoring both localizes both
> the *live* social nodes (high C01) and the *wasted* investment (high C29) in one pass — exactly
> the floor-plan-optimiser signal the cognitive code is for.

## 6. Build steps (mirror C01, which is done and green)

1. `predicates/stranded_amenity.py` — import the shared gate/ridge/registration from
   `triangulation.py`; add `appeal01` (from `landmark_salience.scalar`), `seat_affordance01`,
   the pure `stranded(appeal, one_minus_gate, seat)` core, and `decide()`/`compute()` through the
   `derivation` chokepoint.
2. `tests/test_c29_stranded.py` — pure core (conjunction fires only on appeal-AND-off-path-AND-
   usable), the two negative controls, M1 determinism. Run it (no ship untested).
3. Registry entry + annotator `compound_fns` binding (one line each, next to C01).
4. `run_stage` on the same 3 interiors; confirm 21/21 scored, gate + idempotency hold.
5. Exclude `C29.*` from `score_layout`.

*Estimated marginal effort: low — ~70% of the code (gate, ridge, registration, tri-state,
evidence, M1) is inherited verbatim from the C01 module already committed.*
