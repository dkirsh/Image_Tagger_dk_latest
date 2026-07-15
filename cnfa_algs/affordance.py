"""
cnfa_algs.affordance — spatial-affordance plan metrics (CRITERIA.md C11, C12, C24).

The keystone paper's dimension 6 (prospect/refuge/crowding/territory) and dimension 7
(awe/spatial generosity) made computable on the plan, per-seat where it matters:

  C11 prospect_refuge_quality — per-seat prospect (forward outlook) + refuge (protected
                                back), prospect-led (0.65/0.35), with a back-to-wall bonus.
  C12 perceived_crowding_risk — per-seat: visible co-occupants in the isovist, weighted
                                by lack of refuge and retreat availability (crowding is
                                density-appraised-as-loss-of-control, not raw density).
  C24 spatial_generosity      — awe as a COMPRESSION->RELEASE contrast: openness variation
                                across the floor + a generous 'release' space, NOT uniform
                                bigness (proxy; true awe wants ceiling height = Tier C).

Each casts a per-seat isovist directly (cheaper than the full field for a seat set) and is
honestly a 2D visibility model: no height, no furniture. C24 has no real volume/height
(Tier A/B), so it is an openness-contrast proxy, flagged.

Self-test (analytic L0):
    python -m cnfa_algs.affordance
"""
from __future__ import annotations
from typing import Dict, List, Optional, Sequence, Tuple
import numpy as np

try:
    from .plan import FREE, OBST
except Exception:
    FREE, OBST = 1, 2

RC = Tuple[int, int]


def _seat_isovist(grid: np.ndarray, seat: RC, n_rays: int, cell_m: float,
                  refuge_radius_m: float = 1.0):
    """Cast n_rays from a seat; return (radii_m array, prospect_m, refuge_frac).
    prospect = mean radial distance; refuge = fraction of directions blocked within
    refuge_radius (a protected back/side)."""
    H, W = grid.shape
    r0, c0 = seat
    ang = np.linspace(0, 2 * np.pi, n_rays, endpoint=False)
    dirs = np.stack([np.sin(ang), np.cos(ang)], 1)   # (dr, dc)
    radii = np.empty(n_rays)
    for k in range(n_rays):
        dr, dc = dirs[k]
        rr, cc, step = float(r0), float(c0), 0
        while True:
            step += 1
            rr += dr; cc += dc
            ri, ci = int(rr), int(cc)
            if ri < 0 or ri >= H or ci < 0 or ci >= W or grid[ri, ci] != FREE:
                break
        radii[k] = step
    radii_m = radii * cell_m
    prospect_m = float(radii_m.mean())
    rref = refuge_radius_m
    refuge_frac = float((radii_m <= rref).mean())     # directions with a close boundary
    return radii_m, prospect_m, refuge_frac


from .los import segment_is_free as _los   # supercover LOS (diagonal walls block) — panel fix S1


# ------------------------------------------------------------------ C11 prospect-refuge
def prospect_refuge_quality(pg, seats: Sequence[RC], n_rays: int = 64,
                            refuge_radius_m: float = 1.0, prospect_ref_m: float = 10.0) -> Dict:
    """C11 — per-seat prospect-refuge quality, prospect-led (0.65 prospect + 0.35 refuge,
    STATE_OF_KNOWLEDGE F1). Prospect is normalized to an ABSOLUTE reference outlook
    (`prospect_ref_m`, a generous indoor sightline), NOT to the seat set — a seat-set-
    relative normalization silently zeros the prospect term for a single seat or a uniform
    set (caught by validate_pipeline C11 discrimination, 2026-07-15). Refuge is the
    protected-back fraction. Returns per-seat rows + the mean quality."""
    grid = pg.grid if hasattr(pg, "grid") else np.asarray(pg)
    cell = float(getattr(pg, "cell_m", 1.0))
    prosp, refug = [], []
    for s in seats:
        _, p, rf = _seat_isovist(grid, s, n_rays, cell, refuge_radius_m)
        prosp.append(p); refug.append(rf)
    prosp = np.array(prosp); refug = np.array(refug)
    # absolute prospect normalization -> robust to seat-set size (prospect-led metric)
    p_norm = np.clip(prosp / max(prospect_ref_m, 1e-6), 0, 1)
    pr = 0.65 * p_norm + 0.35 * refug
    rows = [{"seat": k, "prospect_m": round(float(prosp[k]), 2),
             "refuge_frac": round(float(refug[k]), 3),
             "pr_quality": round(float(pr[k]), 3),
             "exposed": bool(refug[k] < 0.15)} for k in range(len(seats))]
    return {"key": "cnfa.spatial.prospect_refuge", "criterion": "C11",
            "rows": rows,
            "scalar": (round(float(pr.mean()), 3) if len(seats) else None),
            "extras": {"n_seats": len(seats), "n_exposed": int((refug < 0.15).sum()),
                       "mean_prospect_m": round(float(prosp.mean()), 2) if len(seats) else None},
            "confidence": 0.5,
            "method": "per-seat isovist: 0.65*prospect(norm) + 0.35*refuge (prospect-led, F1)",
            "failure_modes": ["2D visibility, no height/furniture; prospect normalized within the seat set",
                              "refuge = close-boundary fraction (a proxy for a protected back)",
                              "prospect STRONG, refuge weak indoors (weight reflects it)"]}


# ------------------------------------------------------------------ C12 perceived crowding
def perceived_crowding_risk(pg, seats: Sequence[RC], occupied: Optional[Sequence[int]] = None,
                            retreats: Optional[Sequence[RC]] = None, n_rays: int = 48) -> Dict:
    """C12 — per-seat crowding RISK = visible co-occupants (in the seat's isovist) weighted
    by lack of refuge, divided by retreat availability. Crowding is density appraised as
    loss of control (F2), so it rises with visible others and falls with a protected back
    and nearby retreats."""
    grid = pg.grid if hasattr(pg, "grid") else np.asarray(pg)
    cell = float(getattr(pg, "cell_m", 1.0))
    occ = set(range(len(seats))) if occupied is None else set(occupied)
    n_retreat = len(retreats) if retreats else 0
    retreat_per_occ = (n_retreat / max(len(occ), 1))
    rows = []
    risks = []
    R_density_m = 5.0                    # crowding is a LOCAL-density phenomenon
    for i, s in enumerate(seats):
        _, _, refuge = _seat_isovist(grid, s, n_rays, cell)
        visible = sum(1 for j in occ if j != i and _los(grid, s, seats[j]))
        vis_frac = visible / max(len(occ) - 1, 1)
        # PANEL FIX S7/C12: add the LOCAL DENSITY term CRITERIA.md names. Crowding is
        # density appraised as loss of control (F2) — so it is GATED by density: two
        # occupants 60 m apart in a hall are highly *visible* but not *crowded*. Density =
        # occupied seats within R_density_m, normalized (4 within 5 m = high).
        near = sum(1 for j in occ if j != i
                   and np.hypot(seats[j][0] - s[0], seats[j][1] - s[1]) * cell <= R_density_m)
        density_norm = min(near / 4.0, 1.0)
        risk = density_norm * (0.5 + 0.5 * vis_frac) * (1.0 - 0.5 * refuge) / (1.0 + retreat_per_occ)
        risks.append(risk)
        rows.append({"seat": i, "visible_occupants": visible, "local_density": near,
                     "refuge_frac": round(refuge, 3),
                     "crowding_risk": round(float(risk), 3), "at_risk": bool(risk >= 0.4)})
    risks = np.array(risks)
    n_risk = int((risks >= 0.4).sum())
    return {"key": "cnfa.spatial.perceived_crowding", "criterion": "C12",
            "rows": rows,
            "scalar": (round(float(1 - risks.mean()), 3) if len(seats) else None),  # higher=better (less crowded)
            "extras": {"n_seats": len(seats), "n_at_risk": n_risk,
                       "retreats_per_occupant": round(retreat_per_occ, 3)},
            "confidence": 0.4,
            "method": "local-density x (0.5+0.5*visible) x (1-0.5*refuge) / (1+retreats-per-occ) (F2 control)",
            "failure_modes": ["occupancy is a spec input (which seats filled)",
                              "density gates the risk so spread-out-but-visible seats are not 'crowded'",
                              "retreat set is a spec input (which spaces are withdrawal spaces)"]}


# ------------------------------------------------------------------ C24 spatial generosity / awe
def spatial_generosity(pg, stride: int = 3, release_pct: float = 90.0) -> Dict:
    """C24 — awe as spatial COMPRESSION->RELEASE contrast, not uniform bigness. Compute the
    per-cell openness (mean radial isovist), then: generosity = the contrast between the
    compressed circulation (low openness) and a generous 'release' zone (high openness).
    Score rewards a floor that HAS a release much more open than its tightest circulation;
    a uniform floor (all-tight or all-open) scores low. PROXY: no ceiling height (Tier C)."""
    grid = pg.grid if hasattr(pg, "grid") else np.asarray(pg)
    cell = float(getattr(pg, "cell_m", 1.0))
    H, W = grid.shape
    free = np.argwhere(grid == FREE)[::stride]
    if len(free) < 8:
        return {"key": "cnfa.spatial.generosity", "criterion": "C24", "scalar": None,
                "extras": {"n_cells": len(free)}, "confidence": 0.0,
                "method": "too few cells", "failure_modes": ["degenerate plan"]}
    open_m = []
    n_rays = 32
    ang = np.linspace(0, 2 * np.pi, n_rays, endpoint=False)
    dirs = np.stack([np.sin(ang), np.cos(ang)], 1)
    for (r0, c0) in free:
        rad = np.empty(n_rays)
        for k in range(n_rays):
            dr, dc = dirs[k]; rr, cc, step = float(r0), float(c0), 0
            while True:
                step += 1; rr += dr; cc += dc
                ri, ci = int(rr), int(cc)
                if ri < 0 or ri >= H or ci < 0 or ci >= W or grid[ri, ci] != FREE:
                    break
            rad[k] = step
        open_m.append(rad.mean() * cell)
    open_m = np.array(open_m)
    tight = float(np.percentile(open_m, 10))       # compressed circulation
    release = float(np.percentile(open_m, release_pct))  # the generous release
    # contrast ratio (release / tight); normalize to a score (ratio 1 = uniform -> 0; >=3 -> ~1)
    ratio = release / max(tight, 1e-6)
    score = float(np.clip((ratio - 1.0) / 2.0, 0, 1))   # ratio 1->0, 3->1
    return {"key": "cnfa.spatial.generosity", "criterion": "C24",
            "scalar": round(score, 3),
            "extras": {"n_cells": len(free), "tight_openness_m": round(tight, 2),
                       "release_openness_m": round(release, 2),
                       "compression_release_ratio": round(ratio, 2)},
            "confidence": 0.3,
            "method": "compression->release openness contrast (awe as gradient, not bigness) — PROXY, no height",
            "failure_modes": ["no ceiling height / volume (Tier C) — openness is a 2D proxy for generosity",
                              "awe is selective & sequenced; a global scalar cannot locate the release moment",
                              "promising-import: architectural awe is lab/thin-evidenced (WELLBEING E4)"]}


# --------------------------------------------------------------------------- self-test
if __name__ == "__main__":
    print("cnfa_algs.affordance self-test (analytic L0)\n" + "-" * 44)

    # C11: an open-centre seat (high prospect, low refuge) vs a niche seat (low prospect, high refuge)
    g = np.full((30, 30), FREE, np.int8)
    g[0:30, 0:2] = OBST; g[0:2, :] = OBST            # walls on left & top
    pg = type("PG", (), {"grid": g, "cell_m": 0.5})()
    open_seat = (15, 15)                              # middle of the room
    niche_seat = (3, 3)                               # tucked into the top-left corner
    r11 = prospect_refuge_quality(pg, [open_seat, niche_seat])
    print("C11 rows:", [(x["seat"], x["prospect_m"], x["refuge_frac"], x["pr_quality"]) for x in r11["rows"]])
    assert r11["rows"][0]["prospect_m"] > r11["rows"][1]["prospect_m"], "open seat has more prospect"
    assert r11["rows"][1]["refuge_frac"] > r11["rows"][0]["refuge_frac"], "niche seat has more refuge"

    # C12: a seat that sees many others (open) vs one screened from others -> crowding risk higher for exposed
    g2 = np.full((20, 40), FREE, np.int8)
    pg2 = type("PG", (), {"grid": g2, "cell_m": 0.5})()
    seats = [(10, 5), (10, 10), (10, 15), (10, 20)]   # all in a row, mutually visible
    r12 = perceived_crowding_risk(pg2, seats, retreats=[(2, 2)])
    print("C12 rows:", [(x["seat"], x["visible_occupants"], x["crowding_risk"]) for x in r12["rows"]])
    assert r12["rows"][1]["visible_occupants"] >= 2, "interior seat sees multiple others (open row)"
    # add a wall to screen one seat -> its visible count drops
    g3 = g2.copy(); g3[:, 12] = OBST
    pg3 = type("PG", (), {"grid": g3, "cell_m": 0.5})()
    r12b = perceived_crowding_risk(pg3, seats, retreats=[(2, 2)])
    assert r12b["rows"][0]["visible_occupants"] < r12["rows"][0]["visible_occupants"], "wall reduces visible co-occupants"

    # C24: a floor with a big release + tight corridor scores > a uniform floor
    g_uni = np.full((30, 30), FREE, np.int8)          # uniform open -> low contrast
    pg_uni = type("PG", (), {"grid": g_uni, "cell_m": 0.5})()
    s_uni = spatial_generosity(pg_uni, stride=3)
    g_cr = np.full((40, 40), OBST, np.int8)
    g_cr[5:35, 5:35] = FREE                            # big release room
    g_cr[18:22, 0:5] = FREE                            # tight corridor feeding it
    pg_cr = type("PG", (), {"grid": g_cr, "cell_m": 0.5})()
    s_cr = spatial_generosity(pg_cr, stride=2)
    print(f"C24 uniform ratio={s_uni['extras']['compression_release_ratio']} score={s_uni['scalar']} | "
          f"compress->release ratio={s_cr['extras']['compression_release_ratio']} score={s_cr['scalar']}")
    assert s_cr["scalar"] > s_uni["scalar"], "compression->release floor should out-score a uniform one"

    print("-" * 44 + "\naffordance self-test: PASS")
