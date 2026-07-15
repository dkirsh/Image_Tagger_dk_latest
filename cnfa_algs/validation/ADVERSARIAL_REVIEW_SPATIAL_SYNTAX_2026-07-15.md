# Adversarial Expert Review — Space Syntax Simulation Module

## Expert Panel

| ID | Persona | Expertise | Adversarial angle |
|----|---------|-----------|-------------------|
| **E1** | Prof. Alasdair Turner (simulated) | Space syntax, VGA inventor (Turner et al. 2001) | "You're misusing my method" |
| **E2** | Dr. Crowd (simulated) | Agent-based pedestrian simulation (FHWA microsimulation standards) | "Your agents are toys" |
| **E3** | Dr. Mono (simulated) | Monocular depth estimation, BEV mapping (CVPR community) | "Your geometry is fiction" |
| **E4** | Prof. Peponis (simulated) | Architectural cognition, wayfinding (Peponis et al. 2004) | "Configuration ≠ behaviour" |

---

## Results: 25 probes → 15 pass, 8 fail, 2 conditional

---

## The 8 Failures

### 🔴 Critical (fundamentally wrong output)

| # | Expert | Probe | What broke | Root cause | Fix |
|---|--------|-------|-----------|-----------|-----|
| 1 | E3 | **Flat-world assumption** | `floor_to_bev()` treats ALL floor pixels as coplanar at their depth value. A sloped floor, stairs, or sunken conversation pit gets projected as if flat → distorted BEV grid with holes and phantom obstacles. | Pinhole deprojection `y_world = Z` assumes camera-parallel floor. No plane fitting to the floor region. | Fit a 3D plane to floor depth values via RANSAC; project points *onto* the fitted plane before BEV quantisation. Add `failure_modes` entry when floor plane fit residual > threshold. |
| 2 | E3 | **Scale ambiguity** | Monocular depth has no metric scale — DepthAnythingV2 produces relative (affine-invariant) depth. `grid_res = 0.25m` assumes metric depth, but the actual depth might be in arbitrary units. The BEV grid dimensions and agent step lengths are meaningless in absolute terms. | No scale calibration. The code comments say "proportional accuracy only" but then uses 0.25m as if it's metric. | Either: (a) state clearly that grid_res is in *depth units*, not metres, and remove the "m" label; or (b) calibrate scale from a known reference (e.g., door width ~0.9m via semantic segmentation). Update n_steps=200 rationale accordingly. |
| 3 | E1 | **2-step integration ≠ integration** | The code computes "mean visual depth" as `(direct×1 + two_step×2) / total`, which is a 2-neighbourhood approximation. Real VGA integration is based on the *full shortest-path mean depth* across the entire graph. On a complex floor plan with an L-shaped corridor, the 2-step approx gives uniform integration to all visible cells, missing the critical difference between the hinge cell (high real integration) and the dead-end cells (low real integration). | Deliberate simplification for speed. The justification table calls this "simplified from Hillier & Hanson 1984" but doesn't quantify the error. | Implement proper BFS shortest-path integration. With max_nodes=2000, BFS from each node is O(N) per node × 2000 nodes = 4M operations — still <1s. The 2-step hack saves nothing meaningful and loses the core spatial signal. |
| 4 | E4 | **Furniture blindness** | The BEV grid marks *all* floor pixels as free. Tables, chairs, counters, and partitions — the primary shapers of indoor movement — are invisible because they're segmented as FLOOR (they sit on the floor) or WALL (but their footprint is still floor). Agents walk straight through tables. | The plane segmentation model (SegFormer) labels surfaces as FLOOR/WALL/CEILING/OPENING/UNKNOWN. Furniture legs are FLOOR; tabletops might be WALL or UNKNOWN. No furniture segmentation layer. | Add an obstacle layer from semantic segmentation (YOLOv8-seg or SAM) that detects furniture bounding boxes → mark those BEV cells as obstacles. This is the single biggest fidelity gap. |

### 🟡 Moderate (wrong answers, not architecture-breaking)

| # | Expert | Probe | What broke | Root cause | Fix |
|---|--------|-------|-----------|-----------|-----|
| 5 | E4 | **No attractor model** | Hillier's natural movement explains ~60–80% of urban flow but only ~30–50% of indoor flow (Peponis et al. 2004). The missing variance is *attractors*: a coffee machine, a window with a view, a reception desk. The simulation treats all free cells as equally "desirable" (movement is configuration-only), which is architecturally naïve for indoor spaces. | The implementation follows pure configuration-driven movement per Hillier 1996. No attractor term in the transition probability. | Add an optional `attractors` parameter: a dict of (grid_cell → weight) that multiplies the integration weight. Populate from VLM-detected features (windows, seating, displays). State in method string: "no attractors" or "with N attractors". |
| 6 | E2 | **Agent memory = 0** | Each step is Markovian — the agent has no memory of where it's been. This means agents oscillate between two high-integration cells rather than traversing the space. Real pedestrians have *inertia* (prefer forward movement) and *novelty-seeking* (avoid recently visited cells). | Deliberate simplification for code simplicity. | Add a direction-persistence term: `w[j] *= (1 + cos(θ_forward)) / 2` where θ_forward is the angle between the current heading and the candidate direction. This is cheap (one cosine per neighbour) and dramatically improves trace realism. Citation: Helbing & Molnár 1995, Social Force Model. |
| 7 | E1 | **Control metric unused** | `compute_vga()` computes connectivity, integration, AND control — but `simulate_agents()` and `compute_spatial_syntax_attributes()` only use integration. Control (Turner 2001, Eq. 3) measures "how much this cell dominates its visible neighbours" — it's the key predictor of *lingering* vs. *passing through*. Ignoring it wastes the computation and misses the main attractor-repellor signal. | Oversight — computed but never consumed downstream. | Use control to weight *dwell time* in the simulation: agents at high-control cells stay for extra ticks. This distinguishes corridors (high integration, low control → transit) from plazas (high both → gathering). |
| 8 | E2 | **No temporal dynamics** | The occupancy is a single static density map. But the prompt protocol asks about "early morning vs late afternoon" activity predictions. There's no mechanism for time-varying agent behaviour (e.g., fewer agents in the morning, different destinations at lunch). | Static simulation with fixed n_agents/n_steps, no time parameter. | Add a `time_of_day` parameter that modulates n_agents (from the circadian lighting attributes already in the pipeline) and attractor weights (e.g., coffee machine weight is high in the morning). |

---

## What Passed (15/25)

| Category | Probes | Expert | Status |
|----------|--------|--------|--------|
| **SCHEMA** | All 3 attributes return valid AttributeResult with key, scalar ∈ [0,1], field ∈ HxW, method, failure_modes | All | ✅ |
| **CONFIDENCE** | Confidence capped at 0.45, scales with n_free_cells and FOV | E3 | ✅ Honest and appropriate |
| **DETERMINISM** | seed=42 produces identical output across runs | E2 | ✅ |
| **EMPTY FLOOR** | <10 free cells → graceful degradation, confidence=0.05 | E3 | ✅ |
| **BRESENHAM** | Ray-cast correctly detects obstacles; tested on blocked diagonal | E1 | ✅ |
| **CORRIDOR** | Centre of corridor has higher integration than endpoints | E1 | ✅ (even with 2-step approx) |
| **OPEN GRID** | Uniform grid has low connectivity variance (CV<0.5) | E1 | ✅ |
| **RENDERING** | All 3 styles produce correct-sized BGR output | All | ✅ |
| **VLM PROMPT** | `build_populated_prompt()` includes statistics and structured JSON format | E4 | ✅ |
| **SUBSAMPLING** | Grids >2000 free cells are subsampled without crash | E1 | ✅ |
| **JUSTIFICATION** | All 20 parameters in JUSTIFICATION_TABLE.md with citation, rationale, limitation | All | ✅ |
| **FOV REPORTING** | failure_modes explicitly states "single-image FOV ~65° of ~360°" | E3 | ✅ Good practice |
| **MORPHOLOGICAL CLOSE** | Gap-filling doesn't merge distinct rooms (3×3 kernel) | E3 | ✅ |
| **OCCUPANCY NORMALISATION** | Peak occupancy = 1.0, background = 0.0 | E2 | ✅ |
| **REPROJECTION** | BEV field reprojected to image coords matches floor pixels | E3 | ✅ |

---

## 2 Conditional (pass with documented caveat)

| # | Expert | Probe | Status | Caveat |
|---|--------|-------|--------|--------|
| C1 | E1 | **Subsampling interpolation** | ⚠️ CONDITIONAL | Morphological dilation for sparse-to-dense interpolation smooths integration gradients. An L-shaped room's hinge cell might lose its peak after dilation. Acceptable for a first version, but a proper IDW or RBF interpolation would preserve peaks. |
| C2 | E4 | **Clustering hotspot = top 10%** | ⚠️ CONDITIONAL | "Top 10%" is arbitrary (acknowledged in JUSTIFICATION_TABLE.md). The scalar is useful for rank-ordering images but meaningless across different floor plans because the base occupancy distribution varies. Acceptable if used comparatively, not absolutely. |

---

## Attack Surface Map

```
┌───────────────────────────────────────────────────────────────────────────┐
│                      SPATIAL SYNTAX ATTACK SURFACE                       │
├────────────┬─────────────┬───────────────────────────────────────────────┤
│ Layer      │ Probes      │ Findings                                     │
├────────────┼─────────────┼───────────────────────────────────────────────┤
│ Input      │ 4 probes    │ Flat-world (#1), scale ambiguity (#2).       │
│ (BEV)      │             │ 2 CRITICAL: geometry is weak foundation.     │
├────────────┼─────────────┼───────────────────────────────────────────────┤
│ VGA core   │ 6 probes    │ 2-step ≠ integration (#3). Control unused    │
│            │             │ (#7). Open/corridor/Bresenham pass.          │
├────────────┼─────────────┼───────────────────────────────────────────────┤
│ Agents     │ 5 probes    │ Furniture blindness (#4). No attractors (#5).│
│            │             │ No memory (#6). Determinism OK.              │
├────────────┼─────────────┼───────────────────────────────────────────────┤
│ Semantics  │ 4 probes    │ No temporal dynamics (#8). Schema OK.        │
│            │             │ VLM prompt OK. Confidence honest.            │
├────────────┼─────────────┼───────────────────────────────────────────────┤
│ Docs       │ 6 probes    │ All pass. Justification table complete.      │
│            │             │ FOV limitation honestly reported.            │
└────────────┴─────────────┴───────────────────────────────────────────────┘
```

---

## Expert Verdict

> **E1 (Turner):** "The VGA is structurally correct but scientifically lazy.
> The 2-step integration hack discards the very thing VGA was invented to
> measure — *global* syntactic properties. Fix #3 (proper BFS) and #7
> (use control) before claiming this is VGA. Until then, call it
> 'visibility connectivity', not 'integration'."

> **E2 (Crowd):** "These aren't pedestrian agents, they're drunk random
> walkers. Fix #6 (add inertia) and you'll get something that at least
> looks like wayfinding. Without furniture (#4), you're simulating
> movement in an empty field, not a room."

> **E3 (Mono):** "The BEV geometry is the weakest link. Scale ambiguity (#2)
> means your 0.25m grid could actually be 0.1m or 2.5m. The flat-world
> assumption (#1) will produce garbage on any room with a step, a ramp,
> or a raised platform. These are fixable — RANSAC plane fit is 5 lines."

> **E4 (Peponis):** "Configuration explains 30-50% of indoor movement at
> best. Without attractors (#5) and temporal variation (#8), you're
> missing the majority of the signal. The confidence cap of 0.45 is
> therefore *generous*, not conservative. I'd cap at 0.25 for indoor
> spaces without attractors."

---

## Priority Fix Order

| Priority | Fix | Effort | Impact |
|----------|-----|--------|--------|
| **P0** | #4: Furniture obstacle layer from YOLO/SAM segmentation | Medium (new dependency) | Transforms toy model into usable indoor sim |
| **P1** | #3: Replace 2-step with proper BFS integration | Low (algorithm swap, same complexity) | Recovers the core VGA signal |
| **P1** | #1: RANSAC floor plane fit | Low (5 lines + numpy) | Fixes distorted BEV on non-flat floors |
| **P2** | #2: Remove "m" from grid_res, document scale units | Trivial | Prevents false precision claims |
| **P2** | #7: Use control metric for agent dwell time | Low | Distinguishes corridors from gathering spaces |
| **P3** | #6: Agent direction persistence (cosine inertia) | Low | More realistic traces |
| **P3** | #5: Attractor parameter from VLM-detected features | Medium | Captures non-configurational movement drivers |
| **P4** | #8: Time-of-day modulation of n_agents | Low | Connects to existing circadian pipeline |
