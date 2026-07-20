"""
annotation_socket.predicates.fractal_band — V9 `fractal_mid_d_band_score`.

Committee rank 8.3. AMBER (Fable F5 / Codex 2026-07-18): the R2 fit does NOT prove a valid
scale range, and the plateau/falloff constants are engineering — construct-validation owed. Fractal fluency:
human preference and physiological calm peak when a scene's fractal dimension sits in a mid-D
band (~1.3-1.5), falling off toward sterile blankness (low D) and chaotic overload (high D).
The existing engine computes D but never SCORES it against that response curve — V9 adds the
curve, reading the fractal output rather than recomputing it (M3 no-double-work).

    band_score = trapezoid_response(D_global)         # inverted-U peaked on [1.3, 1.5]
    coverage   = fraction of RAW per-tile D in [1.25, 1.55]

DETERMINISTIC, pure numpy over already-computed values -> ceiling AMBER, audit_class
replayable_tol (float polyfit accumulation upstream). Low-confidence flag when the global
box-count fit R^2 < 0.98 (broken/absent scaling — the D is not trustworthy).

HONESTY (skeptic caveats, carried in metadata):
  - the trapezoid falloff constants OUTSIDE [1.3,1.5] are declared engineering, not literature.
  - construct stretch: preference/EEG studies used isolated fractals/silhouettes; whole-interior
    edge-map D mixes pattern-D with scene composition (Abboushi 2019 narrows, not closes).
  - the STRESS-reduction leg is preliminary (Taylor 2006 is a perspective piece); the PREFERENCE
    leg is strong. Metadata says so.
"""
from __future__ import annotations
from typing import Dict, Optional, Tuple

from .. import derivation as D

PRED_ID = "cnfa.fluency.fractal_mid_d_band"
TIER_HINT = "AMBER"        # Codex-2 F5 fix: was GREEN — split-brain with the AMBER registry note

# declared response constants (emitted with every score so replay is exact)
D_LO, D_HI = 1.30, 1.50          # preferred/calming band (Spehar 2003; Hagerhall 2004)
D_FALL = 0.55                    # trapezoid half-width of the linear falloff outside the band
COV_LO, COV_HI = 1.25, 1.55      # band for per-tile coverage
R2_FLOOR = 0.98                  # box-count fit below this => broken scaling => low-confidence
TOL = 1e-3


# ============================================================ PURE CORE (unit-tested)
def band_response(d: float, lo: float = D_LO, hi: float = D_HI, fall: float = D_FALL) -> float:
    """Asymmetric trapezoid: 1.0 on [lo,hi], linear to 0 across `fall` on each side, clamped."""
    d = float(d)
    if lo <= d <= hi:
        return 1.0
    if d < lo:
        return max(0.0, 1.0 - (lo - d) / fall)
    return max(0.0, 1.0 - (d - hi) / fall)


def band_coverage(fld_raw, lo: float = COV_LO, hi: float = COV_HI) -> float:
    """Fraction of per-tile D values inside the coverage band (ignoring empty/zero tiles)."""
    import numpy as np
    f = np.asarray(fld_raw, float).ravel()
    valid = f[f > 0.01]                      # zero tiles = no edges, not "D=0"
    if valid.size == 0:
        return 0.0
    return float(((valid >= lo) & (valid <= hi)).mean())


def score(d_global: float, fld_raw) -> Tuple[float, float]:
    """Return (band_score, coverage). band_score is the headline; coverage is the localization."""
    return band_response(d_global), band_coverage(fld_raw)


# ============================================================ COMPUTE (pipeline entry)
def compute(img, frac_result) -> Dict:
    """Read the ALREADY-COMPUTED fractal result (never recompute) and score it against the band.
    `frac_result` is the AttributeResult from attributes.fractal_dimension_local."""
    ex = getattr(frac_result, "extras", None) or {}
    d_global = ex.get("D_global", getattr(frac_result, "scalar", None))
    fld_raw = ex.get("fld_raw")
    r2 = ex.get("R2_global", 1.0)
    if d_global is None or fld_raw is None:
        return D.unknown(PRED_ID, "fractal_extras_missing")     # dependency absent -> fail closed
    bscore, cov = score(float(d_global), fld_raw)
    conf = 0.75 if r2 >= R2_FLOOR else 0.3                       # broken scaling -> low confidence
    signal = (f"mid-D band response(D={float(d_global):.3f})={bscore:.3f}, "
              f"coverage[{COV_LO},{COV_HI}]={cov:.3f}, R2={r2:.3f}"
              + (" [broken-scaling]" if r2 < R2_FLOOR else "") + " (M1)")
    ev = D.evidence_image("global_image", "full_frame", signal, conf,
                          upstream=[{"step": "fractal_dimension", "D_global": round(float(d_global), 3),
                                     "R2": round(float(r2), 3), "coverage": round(cov, 3)}])
    return D.scored(PRED_ID, bscore, ev, TIER_HINT, img.shape)
