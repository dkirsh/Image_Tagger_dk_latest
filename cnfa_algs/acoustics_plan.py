"""
cnfa_algs.acoustics_plan — ISO 3382-3 open-plan SPEECH-PRIVACY pack (CRITERIA.md C7, C8).

The synthesis says weight acoustics FIRST (STATE_OF_KNOWLEDGE G4, D1-D3: speech
privacy is the single largest empirical dissatisfier). This module converts the two
○ acoustic criteria into real algorithms on the PlanGrid:

  C8  distraction / privacy distances  — ISO 3382-3 single-number quantities:
        D2,S  spatial decay of A-weighted speech per distance doubling  (good >= 7 dB)
        Lp,A,S,4m  A-weighted speech level at 4 m                        (good <= 48 dB)
        r_D  distraction distance  (STI = 0.50)                          (good <= 5 m, poor > 10 m)
        r_P  privacy distance      (STI = 0.20)
  C7  focus-zone speech privacy        — an STI FIELD over the plan around a speech
        source, its r_D / r_P CONTOURS, and the key check: does any collaboration
        source's r_D contour reach a focus seat? (STI >= 0.50 at a focus seat = fail.)

METHOD (honest scope). This is the ISO 3382-3 *parametric engineering-prediction*
model used at early design, NOT a measured-impulse-response STI:
  - speech A-weighted level decays with distance:  L_S(r) = L_S(1m) - D2,S * log2(r)
  - STI from the speech-to-noise ratio (SNR) via the standard linear approximation
    STI ~= clip(0.5 + SNR/30, 0, 1)   [STI 0.50 at SNR 0 dB; 0.20 at SNR -9 dB]
  - on the plan, speech only reaches cells with line-of-sight to the talker (walls
    give privacy): STI = 0 where an OBST blocks the source, or beyond r_P.
The higher-fidelity path is a per-receiver RIR simulation (pyroomacoustics; see
adapters/acoustics_sim.py for the RT60 tier) — that is the L0+ upgrade; this tier is
the fast, plan-wide, contour-producing screen. D2,S can be passed in or crudely
estimated from mean absorption (flagged heuristic).

Self-test (analytic L0 ground truth):
    python -m cnfa_algs.acoustics_plan
"""
from __future__ import annotations
from typing import Dict, List, Optional, Sequence, Tuple
import numpy as np

try:
    from .plan import FREE, OBST
except Exception:
    FREE, OBST = 1, 2

RC = Tuple[int, int]

# ISO 3382-3 normal-speech reference (A-weighted, free field, 1 m) and defaults
L_SPEECH_1M_DEFAULT = 57.4      # dB(A), normal vocal effort (ISO 3382-3 reference talker)
L_NOISE_DEFAULT = 40.0          # dB(A) ambient/masking background (unmasked office ~35-45)
D2S_DEFAULT = 7.0               # dB per distance doubling (ISO 'good' boundary)


# ------------------------------------------------------------------ core acoustics
def sti_from_snr(snr_db: np.ndarray | float):
    """Standard linear STI approximation from speech-to-noise ratio.
    STI = 0.50 at SNR 0 dB, 0.20 at SNR -9 dB, saturates outside [-15, +15] dB."""
    return np.clip(0.5 + np.asarray(snr_db, float) / 30.0, 0.0, 1.0)


def speech_level(r_m: np.ndarray | float, L_s_1m: float = L_SPEECH_1M_DEFAULT,
                 d2s: float = D2S_DEFAULT):
    """A-weighted speech level at distance r (m). r<1 m clamped to the 1 m level."""
    r = np.maximum(np.asarray(r_m, float), 1.0)
    return L_s_1m - d2s * np.log2(r)


def sti_at(r_m: np.ndarray | float, L_s_1m: float = L_SPEECH_1M_DEFAULT,
           d2s: float = D2S_DEFAULT, L_noise: float = L_NOISE_DEFAULT):
    return sti_from_snr(speech_level(r_m, L_s_1m, d2s) - L_noise)


def _distance_for_sti(sti_target: float, L_s_1m: float, d2s: float, L_noise: float) -> float:
    """Analytic inverse: distance at which STI == sti_target."""
    snr = (sti_target - 0.5) * 30.0                 # invert STI = 0.5 + SNR/30
    # speech_level(r) - L_noise = snr  ->  L_s_1m - d2s*log2(r) - L_noise = snr
    log2r = (L_s_1m - L_noise - snr) / d2s
    return float(2.0 ** log2r)


def d2s_from_absorption(mean_alpha: float) -> float:
    """Crude, FLAGGED heuristic: map mean absorption (0..1) to a spatial-decay rate.
    Real D2,S is driven by ceiling absorption + screens, not RT60 alone — use a
    measured/simulated D2,S when available. Monotone map into ~[4, 11] dB."""
    return float(np.clip(4.0 + 9.0 * mean_alpha, 4.0, 11.0))


# ------------------------------------------------------------------ ISO single numbers (C8)
def iso3382_single_numbers(L_s_1m: float = L_SPEECH_1M_DEFAULT,
                           d2s: float = D2S_DEFAULT,
                           L_noise: float = L_NOISE_DEFAULT) -> Dict:
    """C8 — the ISO 3382-3 single-number quantities + their good/poor ratings."""
    r_D = _distance_for_sti(0.50, L_s_1m, d2s, L_noise)
    r_P = _distance_for_sti(0.20, L_s_1m, d2s, L_noise)
    Lp_4m = float(speech_level(4.0, L_s_1m, d2s))
    rating = {"D2S": "good" if d2s >= 7 else ("poor" if d2s < 5 else "fair"),
              "Lp_As_4m": "good" if Lp_4m <= 48 else ("poor" if Lp_4m > 52 else "fair"),
              "r_D": "good" if r_D <= 5 else ("poor" if r_D > 10 else "fair")}
    return {"key": "cnfa.acoustic.iso3382_3", "criterion": "C8",
            "scalar": round(r_D, 2),                 # r_D is the headline planning number
            "extras": {"D2S_dB": round(d2s, 2), "Lp_As_4m_dB": round(Lp_4m, 2),
                       "r_D_m": round(r_D, 2), "r_P_m": round(r_P, 2),
                       "L_speech_1m_dB": L_s_1m, "L_noise_dB": L_noise,
                       "ratings": rating,
                       "iso_targets": {"D2S_dB>=": 7, "Lp_As_4m_dB<=": 48,
                                       "r_D_m<=": 5, "r_D_poor>": 10}},
            "confidence": 0.55,
            "method": "ISO 3382-3 parametric spatial-decay + linear SNR->STI approximation",
            "failure_modes": ["parametric model, not measured-RIR STI (see acoustics_sim for RT60 tier)",
                              "D2,S assumed/estimated; real value needs screens+ceiling model or measurement",
                              "single talker, normal vocal effort; raise L_s_1m for raised voices"]}


# ------------------------------------------------------------------ STI field (C7)
from .los import segment_is_free as _los   # supercover LOS (diagonal walls block) — panel fix S1


def sti_field(pg, source: RC, L_s_1m: float = L_SPEECH_1M_DEFAULT,
              d2s: float = D2S_DEFAULT, L_noise: float = L_NOISE_DEFAULT) -> np.ndarray:
    """STI over the plan from a speech source: parametric decay on cells with
    line-of-sight to the talker, 0 where a wall blocks or beyond r_P. NaN off-region."""
    grid = pg.grid if hasattr(pg, "grid") else np.asarray(pg)
    cell = float(getattr(pg, "cell_m", 1.0))
    H, W = grid.shape
    out = np.full((H, W), np.nan)
    r_P = _distance_for_sti(0.20, L_s_1m, d2s, L_noise)
    r_max_cells = r_P / cell + 2
    rr, cc = np.mgrid[0:H, 0:W]
    dcell = np.hypot(rr - source[0], cc - source[1])
    free = (grid == FREE)
    cand = free & (dcell <= r_max_cells)
    for (ri, ci) in np.argwhere(cand):
        if _los(grid, source, (ri, ci)):
            d_m = max(dcell[ri, ci] * cell, 0.5)
            out[ri, ci] = float(sti_at(d_m, L_s_1m, d2s, L_noise))
    # free cells that are audible-region-excluded but in-region get STI 0 (private)
    out[free & np.isnan(out)] = 0.0
    return out


def focus_zone_privacy(pg, sources: Sequence[RC], focus_seats: Sequence[RC],
                       L_s_1m: float = L_SPEECH_1M_DEFAULT, d2s: float = D2S_DEFAULT,
                       L_noise: float = L_NOISE_DEFAULT,
                       sti_focus_max: float = 0.50) -> Dict:
    """C7 — for each focus seat, the WORST (max) STI reaching it from any speech
    source. A focus seat with STI >= sti_focus_max (0.50) is a violation: a
    collaboration source's distraction contour crosses a seat meant for focus."""
    grid = pg.grid if hasattr(pg, "grid") else np.asarray(pg)
    cell = float(getattr(pg, "cell_m", 1.0))
    fields = [sti_field(pg, s, L_s_1m, d2s, L_noise) for s in sources]
    rows = []
    for k, seat in enumerate(focus_seats):
        vals = []
        for f in fields:
            v = f[seat[0], seat[1]]
            vals.append(0.0 if np.isnan(v) else float(v))
        worst = max(vals) if vals else 0.0
        rows.append({"focus_seat": k, "worst_sti": round(worst, 3),
                     "violation": bool(worst >= sti_focus_max)})
    n_viol = sum(1 for r in rows if r["violation"])
    return {"key": "cnfa.acoustic.focus_zone_privacy", "criterion": "C7",
            "rows": rows,
            "scalar": (round(1 - n_viol / len(rows), 3) if rows else None),  # fraction of focus seats protected
            "field": (fields[0] if fields else None),
            "extras": {"n_focus_seats": len(rows), "n_violations": n_viol,
                       "sti_focus_max": sti_focus_max, "n_sources": len(sources)},
            "confidence": 0.55,
            "method": "per-source ISO 3382-3 STI field (LOS-blocked) -> worst STI per focus seat",
            "failure_modes": ["parametric STI, LOS-only screening (no diffraction/reflection paths)",
                              "sources & focus seats must be tagged upstream (which zone is which)",
                              "masking (raising L_noise) pulls contours in without moving walls"]}


# ------------------------------------------------------------------ C20 chronic-stress soundscape
def chronic_stress_soundscape(pg, sources: Sequence[RC], L_src_1m: float = 60.0,
                              d2s: float = D2S_DEFAULT, L_floor: float = 40.0,
                              positive_zones: int = 0, stress_hi_db: float = 55.0,
                              comfort_db: float = 45.0) -> Dict:
    """C20 — sustained A-weighted sound LEVEL over the plan (distinct from C7 speech
    INTELLIGIBILITY): chronic level drives arousal/cortisol (WELLBEING C20), so this scores
    the area-weighted sustained level, not STI. Sources contribute by spatial decay;
    energy-summed; no LOS requirement (sustained noise wraps). Lower = better."""
    grid = pg.grid if hasattr(pg, "grid") else np.asarray(pg)
    cell = float(getattr(pg, "cell_m", 1.0))
    H, W = grid.shape
    free = (grid == FREE)
    rr, cc = np.mgrid[0:H, 0:W]
    energy = np.full((H, W), 10 ** (L_floor / 10.0))     # background floor (energy)
    for (sr, sc) in sources:
        d_m = np.maximum(np.hypot(rr - sr, cc - sc) * cell, 1.0)
        L = L_src_1m - d2s * np.log2(d_m)
        energy += 10 ** (L / 10.0)
    level = 10 * np.log10(energy)
    level = np.where(free, level, np.nan)
    mean_level = float(np.nanmean(level))
    # score: comfort_db -> 1, stress_hi_db -> 0; small bonus for positive soundscape zones
    base = float(np.clip((stress_hi_db - mean_level) / (stress_hi_db - comfort_db), 0, 1))
    score = float(np.clip(base + 0.05 * min(positive_zones, 2), 0, 1))
    return {"key": "cnfa.acoustic.chronic_soundscape", "criterion": "C20",
            "scalar": round(score, 3),
            "field": level,
            "extras": {"area_weighted_level_dbA": round(mean_level, 1),
                       "comfort_db": comfort_db, "stress_hi_db": stress_hi_db,
                       "n_sources": len(sources), "positive_zones": positive_zones},
            "confidence": 0.4,
            "method": "energy-summed spatial-decay sustained level (arousal, not intelligibility)",
            "failure_modes": ["distinct from C7 STI — this is absolute LEVEL (cortisol/arousal)",
                              "source levels & positive-soundscape zones are spec inputs",
                              "PROMISING evidence; direction (lower sustained level better) is the safe claim"]}


# --------------------------------------------------------------------------- self-test
if __name__ == "__main__":
    print("cnfa_algs.acoustics_plan self-test (analytic L0)\n" + "-" * 48)

    # --- 1. STI/SNR anchor points ---
    assert abs(float(sti_from_snr(0.0)) - 0.5) < 1e-9
    assert abs(float(sti_from_snr(-9.0)) - 0.2) < 1e-9
    assert float(sti_from_snr(20)) == 1.0 and float(sti_from_snr(-20)) == 0.0
    print("STI(SNR): 0dB->0.50, -9dB->0.20, sat ok")

    # --- 2. single numbers with known inputs ---
    iso = iso3382_single_numbers(L_s_1m=57.4, d2s=7.0, L_noise=45.0)
    rD = iso["extras"]["r_D_m"]; Lp4 = iso["extras"]["Lp_As_4m_dB"]
    # analytic: r_D = 2^((57.4-45)/7) = 2^1.7714 = 3.41 m; Lp,4m = 57.4-2*7 = 43.4
    print(f"single #: r_D={rD} m (expect 3.41), Lp,4m={Lp4} dB (expect 43.4), ratings={iso['extras']['ratings']}")
    assert abs(rD - 3.41) < 0.05, "r_D analytic mismatch"
    assert abs(Lp4 - 43.4) < 0.05, "Lp,4m mismatch"
    assert iso["extras"]["ratings"]["r_D"] == "good" and iso["extras"]["ratings"]["Lp_As_4m"] == "good"

    # --- 3. field-derived r_D matches analytic; STI at source high, decays ---
    grid = np.full((81, 81), FREE, np.int8)
    pg = type("PG", (), {"grid": grid, "cell_m": 0.25})()   # 25 cm cells
    src = (40, 40)
    f = sti_field(pg, src, L_s_1m=57.4, d2s=7.0, L_noise=45.0)
    # distance where field STI crosses 0.5 along a row == r_D
    row = f[40, 40:]                       # STI along +col from source
    dcol = np.arange(len(row)) * 0.25
    below = np.where(row < 0.5)[0]
    rD_field = dcol[below[0]] if len(below) else np.nan
    print(f"field   : STI at source={f[src]:.2f} (~1.0), field r_D~{rD_field:.2f} m (analytic {rD})")
    assert f[src] > 0.9, "STI at talker should be near 1"
    assert abs(rD_field - rD) < 0.5, "field r_D should match analytic r_D"

    # --- 4. a wall gives privacy: STI behind a wall == 0 (blocked LOS) ---
    g2 = np.full((41, 41), FREE, np.int8)
    g2[0:41, 20] = OBST                    # full vertical wall at col 20
    pg2 = type("PG", (), {"grid": g2, "cell_m": 0.3})()
    f2 = sti_field(pg2, (20, 10), L_s_1m=60, d2s=6, L_noise=40)   # source left of wall
    behind = f2[20, 30]                    # a cell right of the wall, LOS blocked
    near_src = f2[20, 12]
    print(f"privacy : STI near source(left)={near_src:.2f}, STI behind wall(right)={behind:.2f} (expect 0)")
    assert behind == 0.0 and near_src > 0.5, "wall must block speech (privacy)"

    # --- 5. C7 focus-seat check: seat inside vs outside r_D ---
    g3 = np.full((61, 61), FREE, np.int8)
    pg3 = type("PG", (), {"grid": g3, "cell_m": 0.5})()
    coll_src = (30, 30)
    # near seat within r_D -> violation; far seat beyond r_P -> protected
    res7 = focus_zone_privacy(pg3, sources=[coll_src],
                              focus_seats=[(30, 33), (30, 58)],   # 1.5 m and 14 m away
                              L_s_1m=57.4, d2s=7.0, L_noise=45.0)
    print("C7 rows :", [(r["focus_seat"], r["worst_sti"], r["violation"]) for r in res7["rows"]])
    assert res7["rows"][0]["violation"] is True, "near focus seat should be violated"
    assert res7["rows"][1]["violation"] is False, "far focus seat should be protected"

    # --- 6. C20 chronic soundscape: quiet room scores high, loud multi-source room low ---
    grid2 = np.full((40, 40), FREE, np.int8)
    pgq = type("PG", (), {"grid": grid2, "cell_m": 0.5})()
    quiet = chronic_stress_soundscape(pgq, sources=[(20, 20)], L_src_1m=55, L_floor=38)
    loud = chronic_stress_soundscape(pgq, sources=[(10, 10), (10, 30), (30, 20)], L_src_1m=68, L_floor=45)
    print(f"C20 soundscape: quiet level={quiet['extras']['area_weighted_level_dbA']}dB score={quiet['scalar']} | "
          f"loud level={loud['extras']['area_weighted_level_dbA']}dB score={loud['scalar']}")
    assert quiet["scalar"] > loud["scalar"], "quieter sustained soundscape should score higher"

    print("-" * 48 + "\nacoustics_plan self-test: PASS")
