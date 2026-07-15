"""
cnfa_algs.daylight_view — VIEW EQUITY & DAYLIGHT/CIRCADIAN proximity (CRITERIA.md C9, C10).

View and daylight are scarce, spatially-fixed resources to DISTRIBUTE, not to peak at a
favoured few (STATE_OF_KNOWLEDGE E2; WELLBEING B6). This module converts the two ○
criteria into plan algorithms:

  C9  view_equity        — fraction of seats with a qualifying line-of-sight to glazing
                           (LEED Quality Views target: >= 75% of occupied area). Per-seat
                           LOS to a window within a qualifying view depth.
  C10 daylight_proximity — per-desk distance-to-nearest-window as the daylight/circadian
                           OPPORTUNITY rank, and the core-deficit flag (desks beyond the
                           ~2-2.5x window-head-height useful-daylight penetration depth).

HONEST SCOPE. C9 view is directly computable (line-of-sight geometry). C10 here is a
geometric SCREEN / RANK, not a certified melanopic number: a defensible melanopic-EDI
value needs a spectral daylight simulation (Radiance/Lark/ALFA) with orientation, sky,
and glazing transmittance (WELLBEING B1/B6). Distance-to-window ranks desks and flags
the deficit zone; it does not certify >=250 melanopic-EDI. Both take the glazing cells
as input (known from a real plan/BIM; from an image, the OPENING regions on the
perimeter) — `windows_from_boundary` helps derive them.

Self-test (analytic L0):
    python -m cnfa_algs.daylight_view
"""
from __future__ import annotations
from typing import Dict, List, Optional, Sequence, Tuple
import numpy as np

try:
    from .plan import FREE, OBST
except Exception:
    FREE, OBST = 1, 2

RC = Tuple[int, int]


def _los(grid: np.ndarray, a: RC, b: RC) -> bool:
    r0, c0 = a; r1, c1 = b
    n = int(max(abs(r1 - r0), abs(c1 - c0))) + 1
    rs = np.linspace(r0, r1, n).round().astype(int)
    cs = np.linspace(c0, c1, n).round().astype(int)
    seg = grid[rs, cs]
    # allow the endpoints (seat cell, window cell) to be non-FREE; interior must be free
    if n <= 2:
        return True
    return bool(np.all(seg[1:-1] == FREE))


def windows_from_boundary(grid: np.ndarray, segments: Sequence[Tuple[RC, RC]]) -> List[RC]:
    """Helper: expand perimeter glazing SEGMENTS (each a (start_rc,end_rc) pair on the
    boundary) into a list of window cells. Use when a real plan marks glazing runs."""
    cells: List[RC] = []
    for a, b in segments:
        n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1]))) + 1
        rs = np.linspace(a[0], b[0], n).round().astype(int)
        cs = np.linspace(a[1], b[1], n).round().astype(int)
        cells.extend((int(r), int(c)) for r, c in zip(rs, cs))
    return cells


# --------------------------------------------------------------------- C9: view equity
def view_equity(pg, seats: Sequence[RC], windows: Sequence[RC],
                max_view_m: float = 7.5, target_fraction: float = 0.75) -> Dict:
    """C9 — per-seat qualifying view: line-of-sight to any window cell within
    `max_view_m`. Returns per-seat rows, the fraction with a qualifying view, and
    whether the floor meets the LEED-style >= 75% target."""
    grid = pg.grid if hasattr(pg, "grid") else np.asarray(pg)
    cell = float(getattr(pg, "cell_m", 1.0))
    wins = np.array(windows) if len(windows) else np.zeros((0, 2))
    rows = []
    for k, s in enumerate(seats):
        best = None
        if len(wins):
            d = np.hypot(wins[:, 0] - s[0], wins[:, 1] - s[1]) * cell
            order = np.argsort(d)
            for idx in order:
                if d[idx] > max_view_m:
                    break
                if _los(grid, s, (int(wins[idx, 0]), int(wins[idx, 1]))):
                    best = float(d[idx]); break
        rows.append({"seat": k, "has_view": best is not None,
                     "view_dist_m": (None if best is None else round(best, 2))})
    n_view = sum(1 for r in rows if r["has_view"])
    frac = (n_view / len(seats)) if seats else None
    return {"key": "cnfa.light.view_equity", "criterion": "C9",
            "rows": rows,
            "scalar": (None if frac is None else round(frac, 3)),
            "extras": {"n_seats": len(seats), "n_with_view": n_view,
                       "target_fraction": target_fraction,
                       "meets_target": (None if frac is None else bool(frac >= target_fraction)),
                       "max_view_m": max_view_m},
            "confidence": 0.65,
            "method": "per-seat line-of-sight to glazing within qualifying view depth (LEED-style)",
            "failure_modes": ["window cells are an input (known on real plan; OPENING regions from image)",
                              "2D LOS; ignores glazing VLT / view content class (score separately)",
                              "equity is about DISTRIBUTION — report the fraction, never the best seat"]}


# --------------------------------------------------------------- C10: daylight/circadian proximity
def daylight_proximity(pg, seats: Sequence[RC], windows: Sequence[RC],
                       head_height_m: float = 2.7,
                       penetration_factor: float = 2.5) -> Dict:
    """C10 (geometric screen) — per-desk distance to the nearest window with line-of-
    sight = daylight/circadian OPPORTUNITY. Desks beyond the useful-daylight
    penetration depth (~penetration_factor x window head-height) are core-deficit
    seats needing electric circadian supplement. NOT a certified melanopic number."""
    grid = pg.grid if hasattr(pg, "grid") else np.asarray(pg)
    cell = float(getattr(pg, "cell_m", 1.0))
    wins = np.array(windows) if len(windows) else np.zeros((0, 2))
    penetration_m = penetration_factor * head_height_m
    rows, dists = [], []
    for k, s in enumerate(seats):
        nd = np.inf
        if len(wins):
            d = np.hypot(wins[:, 0] - s[0], wins[:, 1] - s[1]) * cell
            for idx in np.argsort(d):
                if _los(grid, s, (int(wins[idx, 0]), int(wins[idx, 1]))):
                    nd = float(d[idx]); break
        in_zone = bool(np.isfinite(nd) and nd <= penetration_m)
        rows.append({"seat": k, "nearest_window_m": (None if not np.isfinite(nd) else round(nd, 2)),
                     "in_daylight_zone": in_zone})
        if np.isfinite(nd):
            dists.append(nd)
    n_zone = sum(1 for r in rows if r["in_daylight_zone"])
    return {"key": "cnfa.light.daylight_proximity", "criterion": "C10",
            "rows": rows,
            "scalar": (round(n_zone / len(seats), 3) if seats else None),  # fraction in useful-daylight zone
            "extras": {"n_seats": len(seats), "n_in_daylight_zone": n_zone,
                       "penetration_depth_m": round(penetration_m, 2),
                       "mean_window_dist_m": (round(float(np.mean(dists)), 2) if dists else None)},
            "confidence": 0.45,
            "method": "per-seat LOS distance-to-window (geometric daylight rank; NOT spectral melanopic)",
            "failure_modes": ["geometric screen only — certified melanopic-EDI needs spectral daylight sim",
                              "ignores orientation/sky/glazing transmittance and the daily trajectory",
                              "penetration depth is a rule-of-thumb, not a compliance value"]}


# --------------------------------------------------------------------------- self-test
if __name__ == "__main__":
    print("cnfa_algs.daylight_view self-test (analytic L0)\n" + "-" * 47)

    # room: 40 cols wide, windows along the LEFT wall (col 0); interior wall blocks part
    grid = np.full((20, 40), FREE, np.int8)
    pg = type("PG", (), {"grid": grid, "cell_m": 0.5})()   # 0.5 m cells -> room 20 m wide
    windows = [(r, 0) for r in range(20)]                    # full-height glazing on left

    # seats at increasing distance from the window wall
    seats = [(10, 2), (10, 10), (10, 30)]                    # 1 m, 5 m, 15 m from glazing
    v = view_equity(pg, seats, windows, max_view_m=7.5)
    print("C9 view :", [(r["seat"], r["has_view"], r["view_dist_m"]) for r in v["rows"]], "frac=", v["scalar"])
    assert v["rows"][0]["has_view"] and v["rows"][1]["has_view"], "near/mid seats see the window"
    assert not v["rows"][2]["has_view"], "far seat (15 m > 7.5 m) has no qualifying view"

    d = daylight_proximity(pg, seats, windows, head_height_m=2.7, penetration_factor=2.5)  # depth 6.75 m
    print("C10 dayl:", [(r["seat"], r["nearest_window_m"], r["in_daylight_zone"]) for r in d["rows"]],
          "frac in zone=", d["scalar"])
    assert d["rows"][0]["in_daylight_zone"] and not d["rows"][2]["in_daylight_zone"], "near in zone, far deficit"
    assert abs(d["rows"][1]["nearest_window_m"] - 5.0) < 0.6, "mid seat ~5 m from glazing"

    # a FULL partition wall between the seat and the whole glazing wall removes the view
    g2 = grid.copy(); g2[:, 5] = OBST                        # full-height wall at col 5
    pg2 = type("PG", (), {"grid": g2, "cell_m": 0.5})()
    v2 = view_equity(pg2, [(10, 10)], windows, max_view_m=15)  # seat is behind the wall
    print("C9 walled-off seat has_view:", v2["rows"][0]["has_view"], "(expect False)")
    assert v2["rows"][0]["has_view"] is False, "full partition should block all window views"

    print("-" * 47 + "\ndaylight_view self-test: PASS")
