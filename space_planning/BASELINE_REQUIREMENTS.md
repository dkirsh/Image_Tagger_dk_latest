# BASELINE_REQUIREMENTS.md — The Physical-Code Floor

*Space-planning workstream, `space_planning/`. Drafted 2026-07-15 (Fable/Claude Opus). This file holds the
**physical code**: the occupant-independent, code-mandated requirements a floor-plate layout must satisfy to be
**legal and safe to occupy at all** — egress, corridor and door widths, accessibility, occupant-load/area,
minimum ventilation and light, and the fixed structural/MEP obstacles of the shell. These are the **floor beneath
the optimization**: a layout that violates any of them is inadmissible and is never scored by `CRITERIA.md`,
regardless of how well it reads on the cognitive or well-being codes. Keeping them explicit and separate is the
whole discipline — we never optimize a layout that fails basic code, and we never confuse "compliant" with
"good."*

---

## 0. What this file is, and what it is emphatically not

**It is** the constraint set the optimizer treats as **hard**: masks and minimums on the `PlanGrid` that a
candidate layout must respect before any cognitive/well-being scoring runs. Egress paths that must stay clear,
corridor widths that must not narrow, accessible routes and clearances that must be preserved, occupant loads
that set exit capacity, and the columns/cores/shafts/risers that are simply immovable.

**It is not** a substitute for a licensed code review. Building codes are **jurisdiction-specific, version-
specific, and occupancy-specific**, and the Authority Having Jurisdiction (AHJ) is the final word. This file
encodes the **structure** of the physical code and the **typical governing values** from the model codes most
projects derive from (IBC, ADA/ANSI A117.1, ASHRAE 62.1/55, and — for David's likely California context — the
California Building Code Title 24, which amends the IBC and has its own accessibility chapter 11B). Every specific
number below is marked as a **typical model-code value to confirm with the project's AHJ and a licensed code
consultant**. Treat it as the shape of the gate, not the legal determination.

Framing discipline (from `README.md`): **physical code sets the admissible; cognitive/well-being codes rank
within it.** This file is the admissibility test. `CRITERIA.md` never sees a non-compliant plan.

---

## 1. Egress and life safety (usually the binding constraint on layout)

Egress is where the physical code most directly shapes a plan, because it sizes and locates the circulation the
rest of the layout must hang on.

**Occupant load** — the design population, computed from area ÷ an occupant-load factor, which then drives exit
count and width. Typical model value for business/office use: ~150 sq ft (≈13.9 m²) gross per occupant for the
*egress* calculation (IBC Table 1004.5; concentrated/assembly and other uses differ sharply). *Confirm factor by
use and jurisdiction.*

**Number of exits** — generally ≥2 exits/exit-access doorways once occupant load or travel distance exceeds the
single-exit thresholds; ≥3 above ~500, ≥4 above ~1000 occupants (IBC 1006). Exits must be **remotely separated**
(≥ ½ the space's diagonal, or ⅓ with a sprinkler system).

**Egress width** — capacity per occupant: typical ~0.2 in/occupant for level components (corridors, doors),
~0.3 in/occupant for stairs, with sprinklers (IBC 1005). This sets minimum corridor and door capacity as a
function of the population served.

**Travel distance, common path, dead-ends** — maximum travel distance to an exit (commonly ~200–300 ft with
sprinklers, use-dependent); **common path of egress travel** limit (~75–100 ft) before two independent routes
must be available; **dead-end corridor** limit (commonly ~20–50 ft). These are the numbers that most often force
a second aisle or a through-route in an open plan. (IBC 1006/1017/1020.)

**Corridor fire rating & smoke** — corridors serving certain occupant loads require a fire-resistance rating and,
in larger floors, smoke compartments and areas of refuge (below). (IBC 1020, 1009.)

**Encoding for the optimizer:** required egress corridors become **protected clear-path masks** on the `PlanGrid`
(cells that must remain FREE and at minimum width); exits are fixed nodes; travel-distance and common-path limits
are checked as shortest-path constraints from every occupiable cell to the nearest two exits.

---

## 2. Corridors, doors, and circulation widths

Minimums that set the geometry every desk and room must leave clear:

- **Corridor minimum width** — commonly ≥44 in (1118 mm) for corridors serving an occupant load ≥50; ≥36 in for
  smaller loads (IBC 1020.2), but egress-capacity (§1) can require more. Accessible routes impose their own floor
  (below).
- **Door clear width** — ≥32 in (815 mm) clear at 90° for accessible doors (ADA 404); egress doors sized for
  their occupant load and generally ≥32 in clear.
- **Aisle/aisle-accessway widths** in open-plan workstation fields — governed by egress (a workstation cluster is
  a room with its own common-path and aisle requirements). Typical primary aisle ≥36 in, often wider by capacity.
- **Ceiling height** — habitable/occupiable spaces generally ≥7 ft 6 in (2286 mm) over the required area (IBC
  1208), with allowances for portions.

**Encoding:** these are **minimum-width constraints** on the free-space channels of the `PlanGrid`; the layout's
own walls and furniture may not pinch a required route below its floor.

---

## 3. Accessibility (ADA / ANSI A117.1 / CBC 11B)

Accessibility is a hard civil-rights constraint, not a comfort preference, and it shapes clearances everywhere:

- **Accessible route** — a continuous unobstructed path connecting all required spaces; ≥36 in clear width
  (≥48 in where two wheelchairs pass), with defined passing spaces (ADA 403).
- **Turning space** — a 60 in (1525 mm) diameter circle or T-turn in spaces requiring wheelchair maneuvering
  (ADA 304).
- **Clear floor space** — 30 × 48 in (760 × 1220 mm) at each accessible element; reach ranges 15–48 in (ADA 305,
  308).
- **Accessible workstations** — a proportion of workstations and all common-use elements must be accessible
  (ADA 226/902; percentage varies by element and jurisdiction — *confirm*).
- **Doors, thresholds, maneuvering clearances** — clear width, threshold height ≤ ½ in, and latch-/hinge-side
  maneuvering clearances (ADA 404). California CBC 11B is generally **more stringent** than federal ADA — use the
  governing one.

**Encoding:** turning circles and clear floor spaces are **required-clearance masks** attached to every accessible
element and along the accessible route; the optimizer may not place furniture into them.

---

## 4. Occupancy, area, and density minimums

Distinct from the *planning* densities the cognitive/well-being codes reason about, these are the code and lease
floors:

- **Occupant-load factor** (§1) both sizes egress and, inverted, sets a maximum defensible density for a given
  exit provision.
- **Minimum room/space areas** for specific functions (e.g., accessible toilet rooms, required break areas where
  mandated) — use- and jurisdiction-specific.
- **Plumbing fixture counts** — minimum water closets/lavatories per occupant by use (IPC/UPC Table 403.1) — a
  layout that seats N must be served by adequate fixtures on the floor or within travel distance.
- **Parking/loading, if in scope** — typically out of interior-layout scope but noted where a floor's program
  triggers it.

**Encoding:** density is checked against the exit provision (a layout may not seat more than the egress supports);
fixture adequacy is a floor-level count check, not a per-cell mask.

---

## 5. Minimum light, ventilation, and thermal (the code floor, not the cognitive target)

These overlap in *subject* with `CRITERIA.md` C9/C10/C18/C21 but differ in *role*: here they are **code minimums
that gate**, there they are **quality targets that rank**. The distinction is the whole point — the physical code
asks "is there enough outdoor air / light to be legal?"; the cognitive/well-being codes ask "is the daylight
distributed equitably and is the melanopic dose enough to support circadian health?"

- **Ventilation / outdoor air** — minimum outdoor-air rates per ASHRAE 62.1 (office ~5 L/s/person + an area
  component; *confirm by zone*) and mechanical-code minimums. CO₂ is a *proxy* the cognitive code uses; the code
  floor is the delivered outdoor-air rate.
- **Natural light / window area** — some jurisdictions mandate a minimum glazing area or an equivalent artificial
  minimum for occupiable spaces; many commercial offices meet it artificially. *Confirm.*
- **Illuminance minimums** — maintained task-illuminance floors (from the mechanical/energy code and IES
  practice) — a *minimum*, whereas the cognitive code cares about distribution, glare, and daylight quality.
- **Thermal** — ASHRAE 55 is the comfort *standard* (not usually a hard life-safety code, but often contractually
  binding); the energy code (Title 24 Part 6 in California) constrains the systems. C21 in `CRITERIA.md` ranks
  comfort; here we note only the mandated system capacity and any minimum.

**Encoding:** these are mostly **floor-level or zone-level minimum checks**, not geometry masks — except window
access, which (where mandated) becomes a required seat-to-glazing constraint that also happens to serve C9.

---

## 6. Fixed shell — the immovable geometry every layout inherits

Not "requirements" in the regulatory sense but **hard constraints** the optimizer must treat identically: the
structure and services that cannot move within a tenant fit-out.

- **Structural columns and grid, core walls, shear walls** — fixed obstacles.
- **Elevator/stair cores, shafts, mechanical/electrical/plumbing risers, restrooms** — fixed; they also anchor
  egress (§1) and fixtures (§4).
- **Fixed façade and glazing lines** — set the daylight/view resource the cognitive/well-being codes distribute
  (C9/C10) and cannot be relocated in a fit-out.
- **Slab-to-slab height, structural depth, raised-floor/plenum** — set achievable ceiling height (§2) and
  services routing.
- **Fire-separation and smoke-compartment lines, areas of refuge** — fixed protected zones.

**Encoding:** the fixed shell is the **base obstacle map** of the `PlanGrid` (OBST cells the layout is built
around), loaded before any candidate layout is generated. `../cnfa_algs/plan.py` already represents a plan as
FREE/OBST cells; the shell is the immutable OBST layer, tenant partitions the mutable one.

---

## 7. How the optimizer consumes this file

In order, before any `CRITERIA.md` scoring:

1. **Load the fixed shell** (§6) as the base `PlanGrid` obstacle map.
2. **Stamp the required-clearance and protected-path masks** — egress corridors at capacity width (§1), accessible
   routes/turning/clear-floor spaces (§3), minimum circulation widths (§2).
3. **Reject any candidate** that occupies a masked cell, pinches a required route below its floor, exceeds
   travel-distance/common-path/dead-end limits, seats more than the egress supports, or fails a floor-level
   minimum (fixtures, outdoor air, mandated light) — **inadmissible, not scored**.
4. **Only then** pass the admissible candidate to `CRITERIA.md` for cognitive/well-being ranking.

This ordering guarantees the property the framing demands: **the cognitive and well-being codes only ever choose
among plans that are already legal and safe.** A brilliant cognitive-code layout that blocks an exit is not a
trade-off to weigh — it is disqualified.

---

## 8. Verification boundary (RULE 0)

Every specific numeric value in this file (occupant-load factor ~150 gross ft², corridor 44 in, door 32 in clear,
turning circle 60 in, common-path/dead-end/travel-distance limits, ASHRAE outdoor-air rates) is a **typical
model-code value stated to fix the structure of the constraint**, and each is explicitly flagged for confirmation
against the project's governing code, edition, occupancy classification, sprinkler status, and AHJ. Model codes
referenced are the IBC, ADA Standards / ANSI A117.1, ASHRAE 62.1 and 55, IPC/UPC, and — for California — Title 24
including CBC Chapter 11B (generally more stringent than federal ADA). **This file has not been checked against
any specific jurisdiction's adopted code for any specific project, and it is not a substitute for a licensed code
review.** Its correctness claim is limited to: the *categories* of physical-code constraint that bind an interior
layout, their *role as a hard gate* ahead of cognitive/well-being scoring, and their *encoding* onto the
`PlanGrid`. The exact governing numbers are the code consultant's determination, not this document's.
