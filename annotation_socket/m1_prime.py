"""
annotation_socket.m1_prime — M1' SUFFICIENT-STATISTIC REPLAY (the Layer-2 upgrade Codex specced,
CNFA_DEEPENED_CONSTRUCTION_PLAN_CODEX_2026-07-18.md §"M1' Sufficient-Statistic Replay").

M1 (verify._replay) re-derives the final SCALAR and demands a match — that catches a fabricated or
defaulted number, but NOT a scalar that happens to equal the pipeline output by a DIFFERENT procedure
(a faithful-method failure). M1' additionally emits, per SCORED value, the *sufficient statistics* that
make the scalar defensible, and the checker recomputes those stats from the image bytes and compares a
canonical digest. A scalar-match with a stats-mismatch is demoted; a stats-match with a scalar-mismatch
is RED.

This module is PURE and standalone (no controller/queue import) so it can be unit-tested and dispatched
from verify.py by `audit_class`. It ships two real audit classes first (the two most-used pixel operators):
  - luminance_field  (brightness_variance: 31px local-SD, matches cnfa_algs.attributes)
  - radial_fft       (spectral_slope_deviation / V2 proxy: Hann-windowed radial power slope)
Adding an audit class = add a pure `stats_<class>(gray, **params)` fn + a row in AUDIT_CLASSES.

Determinism: fixed rounding (canonical_json) makes the digest reproducible across machines; that IS the
Mac<->sandbox exact-replay check for these statistics.

Self-test (proves genuine->MATCH, tampered-stat->caught, determinism):
    python3 annotation_socket/m1_prime.py
"""
from __future__ import annotations
import hashlib
import json
from typing import Dict, Optional, Tuple

import numpy as np

STATS_VERSION = "cnfa-m1p-2026-07-19"

# verdict tokens (mirror verify.py's M1_PRIME:* convention)
MATCH = "MATCH"
STATS_MISMATCH = "stats_mismatch"      # scalar ok, sufficient stats differ  -> AMBER/RED
SCALAR_MISMATCH = "scalar_mismatch"    # stats ok, scalar differs            -> RED
MISSING_M1P = "missing_m1_prime"       # no m1_prime block emitted


# ------------------------------------------------------------------ canonicalization + digest
def _canon(obj):
    """Deterministic, machine-independent canonical form: floats rounded to a fixed grid, arrays as
    rounded nested lists with an explicit shape tag, dict keys sorted. This fixed rounding is what makes
    the digest survive Mac<->sandbox float jitter (the cross-environment replay guarantee)."""
    if isinstance(obj, (np.floating, float)):
        # round to 6 sig-figs-ish absolute grid; -0.0 -> 0.0
        r = round(float(obj), 6)
        return 0.0 if r == 0 else r
    if isinstance(obj, (np.integer, int)):
        return int(obj)
    if isinstance(obj, (np.ndarray,)):
        return {"__shape__": list(obj.shape), "__data__": [_canon(x) for x in obj.ravel().tolist()]}
    if isinstance(obj, (list, tuple)):
        return [_canon(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _canon(obj[k]) for k in sorted(obj)}
    return obj


def canonical_json(stats: Dict) -> str:
    return json.dumps(_canon(stats), separators=(",", ":"), ensure_ascii=True, sort_keys=True)


def digest(stats: Dict) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(stats).encode("ascii")).hexdigest()


# ------------------------------------------------------------------ audit-class statistic computers
def _to_gray(img) -> np.ndarray:
    """BT.601 luminance from an HxWx3 uint8/float array, or pass through a 2-D array. Fixed weights so
    the 'conversion' tag is exact and replayable."""
    a = np.asarray(img, dtype=np.float64)
    if a.ndim == 2:
        return a
    w = np.array([0.299, 0.587, 0.114])
    return a[..., :3] @ w


def stats_luminance_field(img, window: int = 31) -> Dict:
    """Sufficient stats for the brightness_variance operator (scalar = global luminance SD).
    Emits global mean/std, local-SD quantiles, bright-pixel fraction — the pre-scalar signature."""
    g = _to_gray(img)
    # local SD via integral-image box filter (deterministic, no cv2 dependency)
    H, W = g.shape
    k = window
    pad = k // 2
    gp = np.pad(g, pad, mode="reflect")                # (H+2pad, W+2pad)

    def _integral(a):
        ii = np.zeros((a.shape[0] + 1, a.shape[1] + 1), dtype=np.float64)
        ii[1:, 1:] = np.cumsum(np.cumsum(a, 0), 1)     # leading zero row/col -> exclusive prefix sums
        return ii

    def _boxsum(integ):
        r0 = np.arange(H); c0 = np.arange(W)
        r1 = r0 + k; c1 = c0 + k                        # window [i, i+k) x [j, j+k) in padded coords
        S = lambda rr, cc: integ[np.ix_(rr, cc)]
        return S(r1, c1) - S(r0, c1) - S(r1, c0) + S(r0, c0)

    n = k * k
    s1 = _boxsum(_integral(gp))
    s2 = _boxsum(_integral(gp * gp))
    local_var = np.maximum(s2 / n - (s1 / n) ** 2, 0.0)
    local_sd = np.sqrt(local_var)
    thr = float(g.mean() + 2.0 * g.std())
    return {
        "audit_class": "luminance_field",
        "conversion": "BT601",
        "window": int(window),
        "global_mean": float(g.mean()),
        "global_std": float(g.std()),
        "local_sd_q": {"p5": float(np.percentile(local_sd, 5)),
                       "p50": float(np.percentile(local_sd, 50)),
                       "p95": float(np.percentile(local_sd, 95)),
                       "p99": float(np.percentile(local_sd, 99))},
        "bright_fraction": float((g > thr).mean()),
        "shape": [int(g.shape[0]), int(g.shape[1])],
    }


def stats_radial_fft(img, n_bins: int = 32, fit_lo: float = 0.10, fit_hi: float = 0.80) -> Dict:
    """Sufficient stats for the spectral_slope_deviation / V2 radial-1/f proxy: Hann-windowed 2-D FFT,
    radially-binned log power, and the log-log slope/intercept/R2 over a fit band. The radial profile
    digest is the faithfulness check — a different procedure that hits the same slope fails here."""
    g = _to_gray(img)
    g = g - g.mean()
    H, W = g.shape
    wr = np.hanning(H)[:, None]
    wc = np.hanning(W)[None, :]
    gw = g * wr * wc
    F = np.fft.fftshift(np.fft.fft2(gw))
    P = (np.abs(F) ** 2)
    cy, cx = H / 2.0, W / 2.0
    yy, xx = np.mgrid[0:H, 0:W]
    rad = np.sqrt((yy - cy) ** 2 + (xx - cx) ** 2)
    rad = rad / rad.max()
    bins = np.linspace(0, 1, n_bins + 1)
    idx = np.clip(np.digitize(rad.ravel(), bins) - 1, 0, n_bins - 1)
    prof = np.zeros(n_bins)
    cnt = np.zeros(n_bins)
    np.add.at(prof, idx, P.ravel())
    np.add.at(cnt, idx, 1.0)
    prof = prof / np.maximum(cnt, 1.0)
    centers = 0.5 * (bins[:-1] + bins[1:])
    band = (centers >= fit_lo) & (centers <= fit_hi) & (prof > 0)
    x = np.log(centers[band])
    y = np.log(prof[band])
    A = np.vstack([x, np.ones_like(x)]).T
    (slope, intercept), *_ = np.linalg.lstsq(A, y, rcond=None)
    yhat = A @ np.array([slope, intercept])
    ss_res = float(((y - yhat) ** 2).sum())
    ss_tot = float(((y - y.mean()) ** 2).sum())
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return {
        "audit_class": "radial_fft",
        "conversion": "BT601",
        "window_fn": "hann2d",
        "n_bins": int(n_bins),
        "fit_band": [float(fit_lo), float(fit_hi)],
        "radial_logpower": [float(v) for v in np.log(np.maximum(prof, 1e-12))],
        "slope": float(slope),
        "intercept": float(intercept),
        "r2": float(r2),
        "shape": [int(H), int(W)],
    }


AUDIT_CLASSES = {
    "luminance_field": stats_luminance_field,
    "radial_fft": stats_radial_fft,
}


# ------------------------------------------------------------------ emit + replay
def emit(audit_class: str, img, **params) -> Dict:
    """Producer side: compute the sufficient stats and package the M1' block for AttributeResult.extras."""
    if audit_class not in AUDIT_CLASSES:
        raise KeyError(f"unknown audit_class {audit_class!r}; known: {sorted(AUDIT_CLASSES)}")
    stats = AUDIT_CLASSES[audit_class](img, **params)
    return {"audit_class": audit_class, "stats_version": STATS_VERSION,
            "stats": stats, "digest": digest(stats)}


def replay(m1p: Optional[Dict], img, scalar: Optional[float] = None,
           recomputed_scalar: Optional[float] = None, tol: float = 0.02,
           **params) -> Tuple[str, Dict]:
    """Checker side. Recompute the stats from image bytes, compare the canonical digest, and (if given)
    compare the scalar. Returns (verdict_token, detail). Pure over its inputs + the recompute."""
    if not m1p:
        return MISSING_M1P, {"reason": "no m1_prime block emitted"}
    ac = m1p.get("audit_class")
    if ac not in AUDIT_CLASSES:
        return STATS_MISMATCH, {"reason": f"unknown audit_class {ac!r}"}
    fresh = AUDIT_CLASSES[ac](img, **params)
    fresh_digest = digest(fresh)
    claimed_digest = m1p.get("digest")
    stats_ok = (fresh_digest == claimed_digest)
    # also verify the claimed digest actually matches the claimed stats (anti-forgery of the digest field)
    self_consistent = (claimed_digest == digest(m1p.get("stats", {})))
    scalar_ok = True
    if scalar is not None and recomputed_scalar is not None:
        scalar_ok = abs(float(scalar) - float(recomputed_scalar)) <= tol
    detail = {"audit_class": ac, "claimed_digest": claimed_digest, "fresh_digest": fresh_digest,
              "digest_self_consistent": self_consistent, "stats_ok": stats_ok, "scalar_ok": scalar_ok}
    if not scalar_ok:
        return SCALAR_MISMATCH, detail
    if not stats_ok:
        return STATS_MISMATCH, detail
    return MATCH, detail


# ------------------------------------------------------------------ self-test
if __name__ == "__main__":
    print("m1_prime self-test\n" + "-" * 48)
    rng = np.random.RandomState(0)
    # a deterministic synthetic image with structure (gradient + a bright patch + texture)
    H, W = 128, 160
    yy, xx = np.mgrid[0:H, 0:W]
    base = 40 + 120 * (xx / W)
    base[20:50, 100:140] = 250.0                       # bright patch
    base = base + 15 * np.sin(xx / 3.0) * np.cos(yy / 4.0)
    img = np.clip(np.stack([base, base * 0.9, base * 0.8], -1), 0, 255).astype(np.uint8)

    for ac in ("luminance_field", "radial_fft"):
        m = emit(ac, img)
        # 1. genuine record replays MATCH
        v, d = replay(m, img)
        assert v == MATCH, (ac, v, d)
        # 2. determinism: recompute digest twice
        assert digest(AUDIT_CLASSES[ac](img)) == m["digest"]
        # 3. a TAMPERED statistic (keep the old digest) is caught as stats_mismatch
        tampered = json.loads(json.dumps(m))
        if ac == "luminance_field":
            tampered["stats"]["global_std"] = float(tampered["stats"]["global_std"]) + 5.0
        else:
            tampered["stats"]["slope"] = float(tampered["stats"]["slope"]) + 0.5
        # attacker forges a matching digest for the tampered stats -> caught because RECOMPUTE differs
        tampered["digest"] = digest(tampered["stats"])
        v2, d2 = replay(tampered, img)
        assert v2 == STATS_MISMATCH, (ac, "tamper not caught", v2, d2)
        # 4. a DIFFERENT image must not replay-match the original stats
        v3, _ = replay(m, np.roll(img, 7, axis=1))
        assert v3 == STATS_MISMATCH, (ac, "different image matched!", v3)
        print(f"  {ac:16s}  genuine->MATCH  tamper->caught  diff-image->caught   "
              f"digest={m['digest'][:14]}...")

    # scalar path: stats ok but scalar disagrees -> RED (scalar_mismatch)
    m = emit("luminance_field", img)
    v, d = replay(m, img, scalar=10.0, recomputed_scalar=99.0)
    assert v == SCALAR_MISMATCH, (v, d)
    print("  scalar disagreement (stats ok) -> scalar_mismatch  OK")
    # missing block
    assert replay(None, img)[0] == MISSING_M1P
    print("  missing m1_prime block -> flagged  OK")
    print("-" * 48 + "\nm1_prime self-test: PASS")
