"""
cnfa_algs.street_noise — street-noise intrusion + masking-privacy fields (Sprint COMP-CORRECT S2,
spec: docs/STREET_NOISE_ACOUSTIC_OPERATOR_SPEC_2026-07-19.md; prototype verified 2026-07-19).

Two fields over a PlanGrid with a street facade:
  noise_spl_field    — intruding street-noise dB(A) per FREE cell (loud vs quiet zones)
  huddle_suitability — privacy(masking) x within-pair comfort: the cost/resource duality; street
                       noise is a COST for focus but a RESOURCE for confidential talk, bounded
                       above (inverted-U).

Physics (declared, parametric — DESIGN-TIME ZONING, not measured SPL):
  facade transmission L = Leq_out - R' (EN 12354-3) · area-weighted Sabine diffuse floor ·
  facade patches as hemispherical sources anchored at d0=0.5m, LOS-blocked patches take a
  Maekawa-style diffraction penalty · privacy = 1 - STI(speech@eaves - noise) with the SAME
  ISO 3382-3 sti_from_snr law as acoustics_plan (C7/C8).

CONTRACT: Leq_out and R' are DECLARED INPUTS. Missing -> ABSTAINED result naming them. No default
masquerades as data. Tier AMBER (declared-input + parametric single-zone Sabine).

Self-test (ordering invariants + inverted-U + abstention + determinism):
    python3 -m cnfa_algs.street_noise
"""
from __future__ import annotations
from typing import Dict, Optional, Sequence
import numpy as np

try:
    from .plan import FREE, OBST
except Exception:
    FREE, OBST = 1, 2

from .acoustics_plan import sti_from_snr, L_SPEECH_1M_DEFAULT, D2S_DEFAULT

R_EAVES_M = 2.5          # bystander distance from a talking pair
COMFORT_MAX_DBA = 50.0   # above this the pair strains (within-pair cost ramp start)
COMFORT_RAMP_DB = 15.0   # comfort falls to 0 over this many dB above COMFORT_MAX
D0_M = 0.5               # near-field anchor distance for facade patch sources
DIFFRACTION_DB = 12.0    # Maekawa-style flat penalty behind a barrier (declared, single-value)


def _los_free(grid, r0, c0, r1, c1) -> bool:
    n = int(max(abs(r1 - r0), abs(c1 - c0)) * 2 + 2)
    rr = np.linspace(r0, r1, n).round().astype(int)
    cc = np.linspace(c0, c1, n).round().astype(int)
    for (r, c) in list(zip(rr, cc))[1:-1]:
        if grid[r, c] == OBST:
            return False
    return True


def street_noise_fields(pg, facade_row: int, Rp: np.ndarray, alpha,
                        outdoor_leq: Optional[float] = None,
                        diffraction_db: float = DIFFRACTION_DB) -> Dict:
    """Compute both fields. pg = PlanGrid-like (grid, cell_m); facade_row = the wall row adjacent
    to the street; Rp = per-column facade sound reduction R' (dB); alpha = absorption map (HxW) or
    scalar. Returns a dict shaped like the other plan operators; status=abstained if inputs missing."""
    if outdoor_leq is None or Rp is None:
        return {"key": "cnfa.acoustic.street_noise_intrusion", "status": "abstained",
                "missing_inputs": [n for n, v in
                                   [("outdoor_leq", outdoor_leq), ("facade_Rp", Rp)] if v is None],
                "method": "ABSTAIN: street-noise fields need declared Leq_out and facade R'"}
    grid = pg.grid if hasattr(pg, "grid") else np.asarray(pg)
    cell_m = float(getattr(pg, "cell_m", 0.25))
    nr, nc = grid.shape
    Rp = np.asarray(Rp, float)
    if Rp.shape[0] != nc:
        raise ValueError(f"Rp must have one entry per column ({nc}), got {Rp.shape}")
    alpha = np.full((nr, nc), float(alpha)) if np.isscalar(alpha) else np.asarray(alpha, float)

    inner = facade_row + 1 if facade_row + 1 < nr else facade_row - 1
    facade_cells = [(inner, c) for c in range(1, nc - 1)]
    L_facade = {c: float(outdoor_leq) - Rp[c] for (_, c) in facade_cells}

    # area-weighted Sabine diffuse floor
    cell_area = cell_m ** 2
    W_in = sum(10 ** (L_facade[c] / 10) * cell_area for (_, c) in facade_cells)
    A = float((alpha * cell_area).sum())
    S = nr * nc * cell_area
    amean = min(A / S, 0.99)
    R_room = A / max(1e-6, (1 - amean))
    L_rev = 10 * np.log10(max(W_in, 1e-12)) + 10 * np.log10(4.0 / max(R_room, 1e-9))

    noise = np.full((nr, nc), np.nan)
    E_rev = 10 ** (L_rev / 10)
    for r in range(nr):
        for c in range(nc):
            if grid[r, c] != FREE:
                continue
            E = E_rev
            for (fr, fc) in facade_cells:
                d = max(np.hypot((r - fr), (c - fc)) * cell_m, D0_M)
                lvl = L_facade[fc] - 20 * np.log10(d / D0_M)
                if not _los_free(grid, r, c, fr, fc):
                    lvl -= diffraction_db
                E += 10 ** (lvl / 10)
            noise[r, c] = 10 * np.log10(E)

    speech_at_eaves = L_SPEECH_1M_DEFAULT - D2S_DEFAULT * np.log2(R_EAVES_M)
    privacy = 1.0 - sti_from_snr(speech_at_eaves - noise)
    within_ok = np.clip(1.0 - np.maximum(0.0, noise - COMFORT_MAX_DBA) / COMFORT_RAMP_DB, 0.0, 1.0)
    huddle = privacy * within_ok

    valid = ~np.isnan(noise)
    q = np.unravel_index(np.nanargmin(np.where(valid, noise, np.inf)), noise.shape)
    h = np.unravel_index(np.nanargmax(np.where(valid, huddle, -np.inf)), huddle.shape)
    return {
        "key": "cnfa.acoustic.street_noise_intrusion", "status": "scored",
        "scalar": round(float(np.nanmean(np.clip((noise - 45.0) / 15.0, 0, 1))), 4),
        "fields": {"noise_spl": noise, "privacy": privacy, "huddle": huddle},
        "extras": {"L_rev_dBA": round(float(L_rev), 2),
                   "noise_min_dBA": round(float(np.nanmin(noise)), 2),
                   "noise_max_dBA": round(float(np.nanmax(noise)), 2),
                   "quietest_cell": [int(q[0]), int(q[1])],
                   "best_huddle_cell": [int(h[0]), int(h[1])],
                   "best_huddle": round(float(np.nanmax(huddle)), 4),
                   "declared": {"outdoor_leq": float(outdoor_leq), "d0_m": D0_M,
                                "diffraction_db": diffraction_db, "r_eaves_m": R_EAVES_M,
                                "comfort_max_dba": COMFORT_MAX_DBA, "comfort_ramp_db": COMFORT_RAMP_DB,
                                "speech_at_eaves_dba": round(float(speech_at_eaves), 2)}},
        "confidence": 0.5,
        "method": ("parametric facade-transmission energy model (EN12354-3 R' + area-weighted Sabine "
                   "floor + Maekawa-ish diffraction) x ISO 3382-3 STI masking — DESIGN-TIME ZONING"),
        "failure_modes": ["single global Sabine floor: local absorption lowers EVERYONE'S floor, "
                          "does not carve a local quiet pocket (GREEN path = per-zone/RIR tier)",
                          "flat diffraction penalty; no reflection/flanking; A-weighted broadband only",
                          "COMFORT_MAX and ramp are engineering constants pending corpus calibration",
                          "AMBER: declared-input operator; Leq/R' are design values, not image reads"]}


# --------------------------------------------------------------------------- self-test
if __name__ == "__main__":
    print("street_noise self-test (ordering invariants + inverted-U)\n" + "-" * 56)

    class PG:
        def __init__(s, grid, cell): s.grid, s.cell_m = grid, cell

    nr, nc, cell = 40, 60, 0.25
    grid = np.full((nr, nc), FREE, np.int8)
    grid[0, :] = OBST; grid[-1, :] = OBST; grid[:, 0] = OBST; grid[:, -1] = OBST
    grid[18, 15:45] = OBST                                  # reception screen
    Rp = np.full(nc, 33.0); Rp[28:32] = 12.0                # glazing + 1m door
    alpha = np.full((nr, nc), 0.10); alpha[28:38, 2:14] = 0.75
    pg = PG(grid, cell)

    # abstention: missing declared inputs -> abstained naming them, never a number
    ab = street_noise_fields(pg, 0, None, alpha, outdoor_leq=None)
    assert ab["status"] == "abstained" and set(ab["missing_inputs"]) == {"outdoor_leq", "facade_Rp"}
    print("missing Leq+R' -> ABSTAINED naming both  OK")

    r68 = street_noise_fields(pg, 0, Rp, alpha, outdoor_leq=68.0)
    n68 = r68["fields"]["noise_spl"]
    print(f"Leq 68: L_rev={r68['extras']['L_rev_dBA']} range={r68['extras']['noise_min_dBA']}"
          f"..{r68['extras']['noise_max_dBA']} dBA")

    # invariant 1: raising Leq raises EVERY cell's noise
    r74 = street_noise_fields(pg, 0, Rp, alpha, outdoor_leq=74.0)
    d = r74["fields"]["noise_spl"] - n68
    assert np.nanmin(d) > 0
    print(f"Leq 68->74: every cell rises (min delta {np.nanmin(d):.2f} dB)  OK")

    # invariant 2: better glazing (higher R') lowers noise everywhere
    rglz = street_noise_fields(pg, 0, Rp + 6.0, alpha, outdoor_leq=68.0)
    assert np.nanmax(rglz["fields"]["noise_spl"] - n68) < 0
    print("R' +6 dB: every cell falls  OK")

    # invariant 3: cells behind the screen are quieter than mirror cells without it
    g2 = grid.copy(); g2[18, 15:45] = FREE
    rnoscr = street_noise_fields(PG(g2, cell), 0, Rp, alpha, outdoor_leq=68.0)
    behind = (25, 30)
    assert n68[behind] < rnoscr["fields"]["noise_spl"][behind]
    print(f"screen shields: {n68[behind]:.1f} < {rnoscr['fields']['noise_spl'][behind]:.1f} dBA  OK")

    # invariant 4 (the inverted-U): best-huddle noise strictly between quietest and loudest
    hud = r68["fields"]["huddle"]
    hc = tuple(r68["extras"]["best_huddle_cell"]); qc = tuple(r68["extras"]["quietest_cell"])
    n_h, n_q, n_max = n68[hc], n68[qc], np.nanmax(n68)
    assert n_q < n_h < n_max, (n_q, n_h, n_max)
    assert hud[hc] > hud[qc]                                # masking beats silence for privacy
    print(f"inverted-U: quietest {n_q:.1f} < best-huddle {n_h:.1f} < loudest {n_max:.1f} dBA; "
          f"huddle {hud[hc]:.2f} > {hud[qc]:.2f}  OK")

    # determinism x3
    for _ in range(2):
        r2 = street_noise_fields(pg, 0, Rp, alpha, outdoor_leq=68.0)
        assert np.nanmax(np.abs(r2["fields"]["noise_spl"] - n68)) == 0.0
    print("determinism x3: exact  OK")
    print("-" * 56 + "\nstreet_noise self-test: PASS")
