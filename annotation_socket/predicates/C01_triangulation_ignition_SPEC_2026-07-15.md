# SPEC — C01 `triangulation_ignition_field`
### First compound attribute wired as a night-nurse annotation-socket predicate · 2026-07-15

**Repo (verified): `/Users/davidusa/REPOS/Image_Tagger_dk_latest`**
**Files (this spec):**
- `annotation_socket/predicates/triangulation.py` — the predicate (compute + pure core)
- `annotation_socket/tests/test_c01_triangulation.py` — core + M1 + negative-control test (PASSES, evidence §7)
- `annotation_socket/predicates/C01_registry_and_wiring.patch.md` — registry entry + annotator wiring + double-count guard
- this spec

---

## 1. What C01 is (the compound claim)

Whyte's **triangulation** made computable: a salient shared **anchor** (fountain, art, a view,
a coffee point) ignites conversation between co-present strangers **only when it sits ON a path
people already take.** The value is neither anchor salience nor spatial integration — it is
their **threshold-gated spatial product**:

```
ignition = salience01(anchor) · integration01(anchor_cell) · gate(dist_to_desire_line)
gate(d)  = exp(-(d / D0)²)          # 1 on the desire-line ridge, → 0 by ~2·D0 off it
```

The gate **is** the compound. An average of salience and integration would score a beautiful
dead-alcove fountain highly; the co-location gate correctly zeros it. Verified numerically
(§7): identical fountain scores **0.749 on the cross-path** vs **0.000 in the dead alcove**,
where a non-compound average would report **0.57** for the alcove and wrongly pass it.

**Human effect & sign.** Raising C01 **raises the probability that fleeting co-presence becomes
a triggered conversation / chance encounter** for mobile strangers and loose acquaintances;
≈0 for solo focus; irrelevant to a formed private huddle.
**Social forms:** triggered conversation, chance encounter.
**Confidence in effectiveness: High** — six panel seats converged; Whyte 1980 (triangulation)
+ Hillier et al. 1993 (integration predicts natural movement) are bedrock and mutually
reinforcing. **Measurement ceiling: AMBER** (rides the inferred plan + cross-tier registration).

## 2. Base measures composed (never recomputed here)

| Base measure | Source (existing) | Role in C01 |
|---|---|---|
| `landmark_salience(img)` → bbox + Lab-contrast dE | `cnfa_algs/attributes.py:198` | the ANCHOR: what, where, how salient |
| `vga_metrics(pg).integration_score01` (C1) | `cnfa_algs/space_syntax.py:50` | per-cell desire-line strength |
| `integration_at(vga, [cell])` | `space_syntax.py:116` | integration at the anchor's cell |
| shared geometry chain vp→planes→depth→PlanGrid | `annotator.py` (computed once) | cross-tier registration of the anchor onto the plan |

## 3. The contract (socket properties)

- **UNITIZED** — one sub-unit = (image, `C01.triangulation_ignition`). Contract row in
  `registry.py`: `requires={plan}`, `audit_class=replayable_tol`, `tier_hint=AMBER`.
- **PROVENANCE-CARRYING** — every SCORED value ships a `plan_chain` evidence dict:
  `{grid_hash, anchor_cell, anchor_bbox, dist_to_ridge_m, gate, salience01, integration01,
  ridge_pctl}` + the 4-step geometry `upstream`. The declared constants (`DE_REF, D0_M,
  RIDGE_PCTL, SALIENCE_FLOOR, REG_FLOOR`) are emitted so replay is exact.
- **GATED FAIL-CLOSED / CHECKER≠AUTHOR** — built only through `derivation.scored/unknown`; a
  value with no/invalid evidence is structurally impossible (returns UNKNOWN → RED).
- **TIERED** — `tier_hint=AMBER` is a hard ceiling: C01 rides heuristic geometry, so it can
  never self-claim GREEN and always awaits the ≠-mind judge on the AMBER path.

## 4. Tri-state (success conditions, with the last-mile checks)

| State | Condition | Output |
|---|---|---|
| **SCORED (value)** | anchor dE ≥ `SALIENCE_FLOOR` AND registered to a plan cell with `reg_conf ≥ REG_FLOOR` | `value = sal01·integ01·gate ∈ [0,1]`, `plan_chain` evidence |
| **SCORED = 0.0** | no anchor above `SALIENCE_FLOOR` | a **genuine zero** (no triangulation prop present), `global_image` evidence naming the floor — NOT an abstention |
| **UNKNOWN** | anchor detected but cross-tier `reg_conf < REG_FLOOR` | fail closed → RED. **Skeptic's mandated fix: never guess the centroid onto the plan.** |
| **UNKNOWN** | geometry confidence `< GEOM_FLOOR`, or `landmark`/`vga` compute raises | fail closed → RED |

**Last-mile validations** (the checks that make the number trustworthy, not merely present):
1. **Cross-tier registration is proven, not assumed** — the anchor's floor-contact pixel is
   back-projected via the same depth/FOV mapping as the plan; `reg_conf` = fraction of the
   anchor footprint landing on **known FREE floor**. Below `REG_FLOOR` ⇒ UNKNOWN.
2. **The gate must actually gate** — a stored high value on an anchor far from the ridge is a
   contradiction M1 replay catches (§6, negative control).
3. **Zero is a finding, not a gap** — an image with no salient prop yields SCORED 0.0 with
   evidence, distinct from UNKNOWN (compute failure). The checker audits which is which.
4. **Double-count guard** — C01 is excluded from `score_layout` aggregation; it is consumed
   only as its own social field (its base measures already feed the aggregate).

## 5. Evidence chain (what a believed C01 ships)

```
image bytes
  └─ vanishing_point (conf)            ┐
  └─ segment_planes  kmeans seed1234   │  geometry upstream (shared, cited by every plan metric)
  └─ depth           (conf)            │
  └─ PlanGrid grid_hash, cell_m        ┘
      └─ anchor_bbox (image) → floor-contact px → plan cell  (reg_conf)
      └─ desire-line ridge = cells ≥ P85 integration
      └─ value = sal01 · integ01 · gate(dist_to_ridge_m)
```

## 6. M1 replay (the author-neutral mechanical check)

`audit_class = replayable_tol`. `verify()` re-derives C01 from the image bytes — landmark
salience (spectral-residual, deterministic), plan inference (seeded kmeans), Turner VGA
(deterministic) — and demands `|replay − stored| ≤ TOL` (1e-3). A fabricated value cannot match.
**Negative control (in the test, PASSES):** a stored `0.90` on an anchor actually 9 m off the
ridge recomputes to `0.000` (gate→0) → `|0.90−0.000| > TOL` → RED. Plus M3 dependency: a C01
SCORED record with no `geometry_chain` present is fabrication → RED before replay runs.

## 7. Test evidence (run in sandbox 2026-07-15 — CLAUDE.md "no script ships untested")

**(a) Pure core** — `python3 annotation_socket/tests/test_c01_triangulation.py` → **ALL PASSED**:
```
gate: on-line=1.000, 1*D0=0.368, far=0.0000
A-vs-B: on-path ignition=0.749  dead-alcove=0.0000  (average would be 0.57)
ridge p85 selected 2/10 highest-integration cells
tri-state: UNKNOWN(geom) / ZERO(no-anchor) / UNKNOWN(reg) / SCORED=0.787
M1 replay: deterministic (|Δ|<=1e-03); fabricated 0.90 vs true 0.0000 -> REJECT
```

**(b) FULL CV PATH end-to-end** — `annotate_image()` on 3 real interiors (wired into the
annotator + registry, C01 now the 20th applicable predicate):
```
_open.png     C01 SCORED 0.4837  plan_chain  anchor_cell=[6,87] dist_to_ridge=0.233m gate=0.99 sal01=0.49 integ01=0.996
_corridor.png C01 SCORED 0.0     global_image  "no anchor above dE floor 8.0"   (genuine zero — a finding)
inv-04.jpg    C01 SCORED 0.2287  plan_chain  anchor_cell=[84,32] dist_to_ridge=0.684m gate=0.93 sal01=0.25 integ01=1.0
```
Determinism (M1 replayable_tol): C01 = **0.4837 across 3 runs** (|Δ|=0).

**(c) FULL GATE** — `python3 -m annotation_socket.run_stage`: all 3 units AMBER, scored **20/20**
applicable (C01 included), traceable; the seeded fabrication negative control REJECTED (RED);
second run zero-work (content-addressed); worker writes to `control/`+`accepted/` DENIED.

**Boundary (RULE 0):** pure core, full CV path, determinism (3 runs), and the full fail-closed
gate are all verified **in this sandbox**. **Not verified:** Mac-vs-sandbox replay determinism of
the salience/VGA stack (lesson L10 — run the harness on the Mac once before trusting skip); the
≠-mind AMBER inference judgment ("does the score follow from the cited region+cell?") — a
VLM/AG pass, still owed. Known AMBER driver: cross-tier registration (`pixel_to_plan_cell`) is a
heuristic mirror of the plan projection; it is ceilinged AMBER and fails closed to UNKNOWN when
`reg_conf < REG_FLOOR`, but the ≠-mind should spot-check that mapped anchor cells are right.

## 8. Region-A-vs-B demonstration (the deliverable claim)

> Fountain on the diagonal cross-path between two entrances → **ignites talk** (high C01) vs the
> **identical** fountain in a planted dead alcove off all circulation → **admired, no talk**
> (C01 ≈ 0). Same salience, opposite social outcome — the gate is what separates them, and no
> single primitive in the stack can.
