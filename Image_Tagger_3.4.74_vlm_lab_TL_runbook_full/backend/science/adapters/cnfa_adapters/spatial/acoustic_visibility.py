"""Acoustic prospect-refuge and eavesdropping zones.

The visual isovist and the *acoustic* field do not coincide: sound diffracts
around corners, leaks through apertures and reverberates, so a listener can sit
in your visual dead ground yet be acoustically connected to you. This module
computes that mismatch.

  * `audibility_field` — the sound level (dB) reaching every free cell from a
    source, via geodesic propagation through the connected air path (so it bends
    around corners) with spherical spreading. This is the acoustic analogue of
    the isovist / prospect (Blesser & Salter's "acoustic arena").
  * `eavesdropping_zones` — the cells that are BOTH in the source's visual dead
    ground (the source cannot see them) AND above the audibility threshold (they
    can hear the source): the eavesdropper's advantage zone.

This is a first-order propagation proxy (geodesic distance + spreading loss),
deliberately permissive and fast for mapping. The rigorous version replaces
`audibility_field` with a pyroomacoustics ray-trace / image-source simulation on
the same geometry (with real absorption + diffraction + wall transmission).
References: Blesser & Salter 2007 (acoustic arena/horizon); ISO 3382-3 / STI
(speech privacy); Neuhoff 2001 (auditory looming).
"""
from __future__ import annotations

import heapq
import math
from typing import Dict, Optional, Tuple

import numpy as np

from .isovist import Plan
from .prospect_refuge import visible_mask

Point = Tuple[float, float]

_SQRT2 = math.sqrt(2.0)
_NEIGH = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0),
          (1, 1, _SQRT2), (1, -1, _SQRT2), (-1, 1, _SQRT2), (-1, -1, _SQRT2)]


def geodesic_sound_distance(plan: Plan, source: Point) -> np.ndarray:
    """Shortest path length (in cells) from source to every free cell through
    connected air — captures sound bending around corners. inf where unreachable."""
    h, w = plan.h, plan.w
    dist = np.full((h, w), np.inf)
    sx, sy = int(round(source[0])), int(round(source[1]))
    if not (0 <= sx < w and 0 <= sy < h and plan.free[sy, sx]):
        return dist
    dist[sy, sx] = 0.0
    heap = [(0.0, (sx, sy))]
    while heap:
        d, (x, y) = heapq.heappop(heap)
        if d > dist[y, x]:
            continue
        for dx, dy, wt in _NEIGH:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and plan.free[ny, nx]:
                nd = d + wt
                if nd < dist[ny, nx]:
                    dist[ny, nx] = nd
                    heapq.heappush(heap, (nd, (nx, ny)))
    return dist


def audibility_field(plan: Plan, source: Point, source_db: float = 62.0,
                     ref_dist: float = 1.0) -> np.ndarray:
    """Sound level (dB) at every free cell from a source of `source_db` at 1 unit,
    via geodesic distance + spherical spreading (-6 dB per distance doubling).
    -inf where unreachable."""
    dist = geodesic_sound_distance(plan, source) * plan.cell_size
    level = np.full(dist.shape, -np.inf)
    reach = np.isfinite(dist)
    d = np.maximum(dist[reach], ref_dist)
    level[reach] = source_db - 20.0 * np.log10(d / ref_dist)
    return level


def eavesdropping_zones(plan: Plan, source: Point, source_db: float = 62.0,
                        background_db: float = 35.0):
    """Return (eavesdrop_mask, visible_mask, level_field).

    eavesdrop_mask = free & (NOT visible from source) & (audible above background):
    places a hidden listener can hear the source from."""
    vis = visible_mask(plan, source)
    level = audibility_field(plan, source, source_db=source_db)
    audible = level > background_db
    dead = plan.free & ~vis
    eavesdrop = dead & audible
    return eavesdrop, vis, level


def eavesdrop_exposure(plan: Plan, source: Point, source_db: float = 62.0,
                       background_db: float = 35.0) -> Dict[str, float]:
    """Scalar summaries: eavesdrop area as a fraction of free space and of the
    visual dead ground (how much of your hidden surroundings can hear you)."""
    eavesdrop, vis, level = eavesdropping_zones(plan, source, source_db, background_db)
    free_n = int(plan.free.sum()) or 1
    dead = plan.free & ~vis
    dead_n = int(dead.sum()) or 1
    return {
        "cnfa.acoustic.eavesdrop_area_fraction": float(eavesdrop.sum()) / free_n,
        "cnfa.acoustic.eavesdrop_of_deadground": float(eavesdrop.sum()) / dead_n,
        "cnfa.acoustic.audible_area_fraction": float((level > background_db).sum()) / free_n,
    }


# ---------------------------------------------------------------------------
# Reflected / reverberant sound (diffuse-field proxy) + intelligibility.
#
# The geodesic model above is DIRECT sound only. In a real enclosure, walls
# reflect the conversation: a near-uniform reverberant field fills the room,
# raising the LEVEL everywhere (more audible), while late reflections smear
# speech and lower INTELLIGIBILITY. So "can hear a murmur" and "can make out
# words" diverge — the reverberation that makes you audible can also mask your
# words. Hard rooms (low absorption) have a high reverberant floor; absorptive
# rooms are direct-dominated. This is a phenomenological proxy controlled by an
# absorption coefficient alpha in (0,1); the calibrated version replaces it with
# a pyroomacoustics image-source/ray-trace RIR + ISO 3382-3 STI.
# ---------------------------------------------------------------------------

def reverberant_floor_db(source_db: float, absorption: float, offset: float = 18.0) -> float:
    """Near-uniform diffuse-field level. Low absorption -> high floor (hard,
    reverberant room); high absorption -> low floor (soft room)."""
    a = min(max(absorption, 0.02), 0.98)
    return source_db - offset + 10.0 * math.log10((1.0 - a) / a)


def _combine_db(a_db: np.ndarray, b_db: float) -> np.ndarray:
    """Energy-sum two dB fields (a is an array, b a scalar floor)."""
    out = np.full_like(a_db, -np.inf)
    finite = np.isfinite(a_db)
    out[finite] = 10.0 * np.log10(10.0 ** (a_db[finite] / 10.0) + 10.0 ** (b_db / 10.0))
    return out


def acoustic_eavesdrop(plan: Plan, source: Point, source_db: float = 62.0,
                       background_db: float = 40.0, absorption: Optional[float] = None,
                       mode: str = "audible", sti_threshold: float = 0.45):
    """Eavesdropping with reflected sound and an intelligibility option.

    Returns (eavesdrop_mask, visible_mask, total_level_db, sti_field).
      absorption=None -> direct sound only (as before).
      absorption in (0,1) -> add the reverberant floor.
      mode="audible"     -> hidden AND level > background (hear a murmur).
      mode="intelligible"-> hidden AND STI > sti_threshold (make out words).
    STI proxy = direct-to-(reverberant+noise) ratio mapped to [0,1]; reverberation
    RAISES level but LOWERS this ratio, so a hard room can be audible-but-unclear.
    """
    vis = visible_mask(plan, source)
    direct = audibility_field(plan, source, source_db=source_db)      # direct only
    reach = np.isfinite(direct)
    if absorption is not None:
        rfloor = reverberant_floor_db(source_db, absorption)
        total = _combine_db(direct, rfloor)                          # direct + reverb
    else:
        rfloor = -np.inf
        total = direct
    # STI-like intelligibility: signal (direct) vs late reverb + background noise
    sti = np.zeros(direct.shape)
    noise = 10.0 ** (background_db / 10.0) + (10.0 ** (rfloor / 10.0) if np.isfinite(rfloor) else 0.0)
    with np.errstate(divide="ignore", invalid="ignore"):
        snr_db = np.where(reach, direct - 10.0 * np.log10(noise), -np.inf)
    sti = np.clip((snr_db + 15.0) / 30.0, 0.0, 1.0)
    sti[~reach] = 0.0

    dead = plan.free & ~vis
    if mode == "intelligible":
        hearable = sti > sti_threshold
    else:
        hearable = total > background_db
    return dead & hearable, vis, total, sti
