"""Specular self-visibility and seen-via-reflection — the optics of feeling watched.

Reflective interior surfaces (glass curtain walls, polished stone, mirror
cladding) do two cognitively distinct things that matte surfaces do not:

  1. **Self-exposure.** They show you *yourself*. Catching your own reflection
     turns attention inward onto the self as an object — the trigger of
     *objective self-awareness* (Duval & Wicklund, 1972) and of the public
     self-consciousness a mirror reliably induces (Carver & Scheier, 1978;
     Fenigstein et al., 1975). A foyer walled in dark glass can make a person
     feel *on display to themselves* even when no one else is present.

  2. **Seen-via-reflection.** They let *other* people see you along a bounced
     sightline — around a corner, through the geometry a matte wall would have
     hidden. This extends visual exposure (and so degrades privacy) beyond the
     direct isovist.

Both follow from one piece of classical optics — the *mirror-image (catoptric)
construction*. The reflection of a point E in a planar surface S is the point E'
obtained by reflecting E across the line of S. A viewer sees E's reflection at
the point P where the segment (viewer -> E') crosses S, provided P lies on the
physical surface, the viewer is on the reflective side, and both optical legs
are unobstructed. For *self*-view the viewer is E itself, so P is simply the
foot of the perpendicular from E onto S, and the reflection sits a round-trip
distance 2d behind the glass (d = perpendicular distance E->S).

This module is clean-room and permissive (pure geometry, NumPy only). It is the
optical companion to `acoustic_pyroom` (which does the acoustic version of the
same "who can sense you here" question) and to `prospect_refuge` (the direct
visual version).

Coordinates: (x, y) in plan metres. Surfaces are directed segments A->B; the
room interior is identified by an `interior_point` so we can tell the reflective
(front) side from the back.

References: Duval & Wicklund (1972); Fenigstein, Scheier & Buss (1975); Carver &
Scheier (1978); Silvia & Duval (2001, review). Optics: the method of images
(any geometrical-optics text).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

Point = Tuple[float, float]

# ---------------------------------------------------------------------------
# Material OPTICAL specular reflectance — distinct from acoustic absorption.
# ---------------------------------------------------------------------------
# This is a *mirror-quality* coefficient in [0, 1]: the fraction of incident
# light a surface returns specularly (as a coherent image) rather than
# scattering diffusely. It is NOT the acoustic-absorption number in
# acoustic_pyroom — a surface can be acoustically hard yet optically matte
# (raw concrete) or acoustically soft yet optically mirror-like (a fabric-backed
# glass panel is neither; a dark glass panel is optically near-mirror but
# acoustically hard). Keeping the two tables separate is the whole point: the
# same wall can flip speech privacy and self-exposure in opposite directions.
OPTICAL_REFLECTANCE: Dict[str, float] = {
    "mirror": 0.95,
    "dark_glass": 0.80,          # glass over a dark/nighttime backing -> near mirror
    "glass_window": 0.45,        # clear glazing: partial specular (Fresnel + interior)
    "polished_metal": 0.60,
    "polished_marble": 0.35,
    "polished_stone": 0.28,
    "brushed_metal": 0.30,
    "glossy_paint": 0.18,
    "wood_polished": 0.15,
    "wet_floor": 0.25,
    "wood_matte": 0.04,
    "concrete": 0.05,
    "plaster_matte": 0.03,
    "brick": 0.02,
    "carpet": 0.0,
    "fabric": 0.0,
    "acoustic_panel": 0.0,
}

# Two-arm presets for the reflective-vs-matte contrast (the study manipulation).
REFLECTIVE_PRESETS: Dict[str, str] = {
    "mirror_glass": "dark_glass",     # the reflective arm
    "clear_glass": "glass_window",
    "polished_stone": "polished_marble",
    "matte_plaster": "plaster_matte",  # the matte arm
    "raw_concrete": "concrete",
}


def optical_reflectance(material) -> float:
    """Resolve a material spec to a specular reflectance in [0, 1].

    Accepts a float (used directly), a REFLECTIVE_PRESETS name, or an
    OPTICAL_REFLECTANCE material name. Unknown strings fall back to a low
    diffuse value (0.05) rather than raising.
    """
    if isinstance(material, (int, float)):
        return max(0.0, min(1.0, float(material)))
    if material in REFLECTIVE_PRESETS:
        material = REFLECTIVE_PRESETS[material]
    return float(OPTICAL_REFLECTANCE.get(material, 0.05))


# ---------------------------------------------------------------------------
# Surfaces and the room.
# ---------------------------------------------------------------------------
@dataclass
class Surface:
    """A planar interior surface segment A->B with an optical reflectance."""
    a: Point
    b: Point
    reflectance: float = 0.0
    name: str = ""


def surfaces_from_corners(corners: Sequence[Point], materials=0.0) -> List[Surface]:
    """Wrap a room polygon's edges as Surfaces.

    `materials` is either one spec applied to every wall, or a list of specs
    (one per edge). Each spec is a float/preset/material-name resolved by
    `optical_reflectance`.
    """
    n = len(corners)
    if not isinstance(materials, (list, tuple)):
        materials = [materials] * n
    out = []
    for i in range(n):
        a = tuple(map(float, corners[i]))
        b = tuple(map(float, corners[(i + 1) % n]))
        out.append(Surface(a, b, optical_reflectance(materials[i]), name=f"wall_{i}"))
    return out


def _reflect_across_line(p: Point, a: Point, b: Point) -> Point:
    """Mirror point p across the infinite line through a, b (method of images)."""
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    if L2 == 0:
        return p
    # projection scalar of (p - a) on the line direction
    t = ((p[0] - ax) * dx + (p[1] - ay) * dy) / L2
    foot = (ax + t * dx, ay + t * dy)
    return (2 * foot[0] - p[0], 2 * foot[1] - p[1])


def _perp_foot(p: Point, a: Point, b: Point):
    """Foot of the perpendicular from p to line a-b; return (foot, t, dist).

    t is the parameter along a->b (0 at a, 1 at b); dist is the perpendicular
    distance. Points with t in [0, 1] have their foot on the physical segment.
    """
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    if L2 == 0:
        return a, 0.0, math.hypot(p[0] - ax, p[1] - ay)
    t = ((p[0] - ax) * dx + (p[1] - ay) * dy) / L2
    foot = (ax + t * dx, ay + t * dy)
    dist = math.hypot(p[0] - foot[0], p[1] - foot[1])
    return foot, t, dist


def _side(p: Point, a: Point, b: Point) -> float:
    """Signed side of p relative to directed line a->b (2D cross product)."""
    return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])


def _seg_intersect(p1: Point, p2: Point, p3: Point, p4: Point) -> bool:
    """True if open segments p1p2 and p3p4 properly cross (shared endpoints and
    collinear grazes do NOT count as blocking)."""
    d1 = _side(p3, p4, p1)
    d2 = _side(p3, p4, p2)
    d3 = _side(p1, p2, p3)
    d4 = _side(p1, p2, p4)
    if ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)):
        return True
    return False


def _unobstructed(p: Point, q: Point, occluders: Sequence[Surface],
                  skip: Optional[Surface] = None, eps: float = 1e-6) -> bool:
    """True if segment p->q crosses no occluder (except `skip`, the surface the
    ray terminates on). The endpoints are pulled inward by `eps` so a ray that
    lands *on* a wall is not counted as blocked by that wall."""
    # shrink toward the midpoint so shared endpoints don't register
    mx, my = (p[0] + q[0]) / 2.0, (p[1] + q[1]) / 2.0
    p2 = (p[0] + (mx - p[0]) * eps, p[1] + (my - p[1]) * eps)
    q2 = (q[0] + (mx - q[0]) * eps, q[1] + (my - q[1]) * eps)
    for s in occluders:
        if s is skip:
            continue
        if _seg_intersect(p2, q2, s.a, s.b):
            return False
    return True


# ---------------------------------------------------------------------------
# Self-exposure: seeing yourself.
# ---------------------------------------------------------------------------
def self_images(eye: Point, surfaces: Sequence[Surface], interior_point: Point,
                occluders: Optional[Sequence[Surface]] = None,
                person_size: float = 1.7, min_reflectance: float = 0.06
                ) -> List[dict]:
    """Every surface in which `eye` sees its own reflection, with the geometry.

    For self-view the reflection point is the perpendicular foot from the eye
    onto the surface (that is the point on a plane mirror where you meet your
    own gaze). A self-image exists when the foot lies on the physical segment,
    the eye is on the reflective (interior) side, the surface is reflective
    enough, and the eye->foot path is unobstructed.

    Each record: surface name, reflectance, foot point, perpendicular distance
    d, round-trip (image) distance 2d, subtended size (person_size/2d), and the
    weighted intensity reflectance*subtended.
    """
    occluders = list(occluders) if occluders is not None else list(surfaces)
    out = []
    interior_ref = None
    for s in surfaces:
        if s.reflectance < min_reflectance:
            continue
        foot, t, d = _perp_foot(eye, s.a, s.b)
        if not (0.0 <= t <= 1.0) or d < 1e-6:
            continue
        # eye must be on the same side as the interior (the reflective face)
        if _side(interior_point, s.a, s.b) * _side(eye, s.a, s.b) < 0:
            continue
        if not _unobstructed(eye, foot, occluders, skip=s):
            continue
        subtended = person_size / (2.0 * d)          # visual angle of the image (small-angle)
        out.append({
            "surface": s.name,
            "reflectance": s.reflectance,
            "foot": foot,
            "distance": d,
            "image_distance": 2.0 * d,
            "subtended": subtended,
            "intensity": s.reflectance * subtended,
        })
    return out


def self_exposure(eye: Point, surfaces: Sequence[Surface], interior_point: Point,
                  occluders: Optional[Sequence[Surface]] = None,
                  person_size: float = 1.7) -> dict:
    """Scalar self-exposure at `eye`: how strongly the space shows you yourself.

    Returns a dict with:
      self_exposure          — Sum of reflectance*subtended over self-images (raw)
      self_exposure_index    — 1 - exp(-raw / scale), squashed to [0, 1)
      n_self_images          — how many surfaces return a reflection
      nearest_image_distance — smallest round-trip distance (looming reflection); None if none
      images                 — the per-surface breakdown
    """
    imgs = self_images(eye, surfaces, interior_point, occluders, person_size)
    raw = float(sum(i["intensity"] for i in imgs))
    nearest = min((i["image_distance"] for i in imgs), default=None)
    # scale ~ reflectance(1.0) * person_size/2d at d=1.5 m -> ~0.57; index ~0.6 there
    scale = 0.6
    index = 1.0 - math.exp(-raw / scale)
    return {
        "self_exposure": raw,
        "self_exposure_index": float(index),
        "n_self_images": len(imgs),
        "nearest_image_distance": nearest,
        "images": imgs,
    }


def floor_grid(corners: Sequence[Point], step: float = 0.8, margin: float = 0.5):
    """Interior sample points on a regular grid (points inside the polygon).

    Returns (points, xs, ys) where points aligns row-major with the (ys, xs)
    meshgrid for contour plotting; exterior cells are still returned (callers
    mask by `inside`)."""
    xs_all = [c[0] for c in corners]
    ys_all = [c[1] for c in corners]
    x0, x1 = min(xs_all) + margin, max(xs_all) - margin
    y0, y1 = min(ys_all) + margin, max(ys_all) - margin
    xs = np.arange(x0, x1 + 1e-9, step)
    ys = np.arange(y0, y1 + 1e-9, step)
    pts = [(float(x), float(y)) for y in ys for x in xs]
    return pts, xs, ys


def _point_in_polygon(p: Point, corners: Sequence[Point]) -> bool:
    x, y = p
    n = len(corners)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = corners[i]
        xj, yj = corners[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi):
            inside = not inside
        j = i
    return inside


def self_exposure_field(corners: Sequence[Point], materials,
                        occluders: Optional[Sequence[Surface]] = None,
                        step: float = 0.8, person_size: float = 1.7,
                        interior_point: Optional[Point] = None):
    """Self-exposure topography over the room floor.

    Returns (field, xs, ys, surfaces) where field is a 1-D array aligned to the
    floor_grid points (NaN outside the polygon). `materials` is one spec or a
    per-edge list (see surfaces_from_corners).
    """
    surfaces = surfaces_from_corners(corners, materials)
    occ = list(occluders) if occluders is not None else []
    all_occ = surfaces + occ
    if interior_point is None:
        interior_point = (float(np.mean([c[0] for c in corners])),
                          float(np.mean([c[1] for c in corners])))
    pts, xs, ys = floor_grid(corners, step=step, margin=0.0)
    field = np.full(len(pts), np.nan)
    for k, p in enumerate(pts):
        if not _point_in_polygon(p, corners):
            continue
        field[k] = self_exposure(p, surfaces, interior_point, all_occ, person_size)["self_exposure_index"]
    return field, xs, ys, surfaces


# ---------------------------------------------------------------------------
# Seen-via-reflection: other people seeing you around a corner.
# ---------------------------------------------------------------------------
def seen_via_reflection(target: Point, observers: Sequence[Point],
                        surfaces: Sequence[Surface], interior_point: Point,
                        occluders: Optional[Sequence[Surface]] = None,
                        min_reflectance: float = 0.05) -> dict:
    """How many observers gain a *bounced* sightline to `target`.

    For each observer O and reflective surface S: reflect the target across S to
    T'; a mirror path O->P->target exists if segment O->T' crosses S at a point
    P on the physical segment, both O and target are on the reflective side, and
    both legs O->P and P->target are unobstructed. This is exposure the direct
    isovist misses — being visible around a corner via glass.

    Returns dict with reflected_visible (bool per observer), reflected_fraction
    (share of observers with a bounced view), and n_reflected.
    """
    occluders = list(occluders) if occluders is not None else list(surfaces)
    flags = []
    for o in observers:
        seen = False
        for s in surfaces:
            if s.reflectance < min_reflectance:
                continue
            # both must face the reflective side
            if _side(interior_point, s.a, s.b) * _side(o, s.a, s.b) < 0:
                continue
            if _side(interior_point, s.a, s.b) * _side(target, s.a, s.b) < 0:
                continue
            t_img = _reflect_across_line(target, s.a, s.b)
            # reflection point = where O->T' crosses S
            if not _seg_intersect(o, t_img, s.a, s.b):
                continue
            # compute the actual crossing point P of O->T' with line S
            P = _line_cross(o, t_img, s.a, s.b)
            if P is None:
                continue
            if not _unobstructed(o, P, occluders, skip=s):
                continue
            if not _unobstructed(P, target, occluders, skip=s):
                continue
            seen = True
            break
        flags.append(seen)
    n = len(observers)
    return {
        "reflected_visible": flags,
        "n_reflected": int(sum(flags)),
        "reflected_fraction": float(sum(flags)) / n if n else 0.0,
    }


def _line_cross(p1: Point, p2: Point, a: Point, b: Point) -> Optional[Point]:
    """Intersection point of segment p1p2 with the segment a-b, or None."""
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = a
    x4, y4 = b
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(den) < 1e-12:
        return None
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
    u = ((x1 - x3) * (y1 - y2) - (y1 - y3) * (x1 - x2)) / den
    if 0.0 <= t <= 1.0 and 0.0 <= u <= 1.0:
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
    return None


def annotate_reflection(corners: Sequence[Point], viewpoint: Point, materials,
                        observers: Optional[Sequence[Point]] = None,
                        occluders: Optional[Sequence[Surface]] = None,
                        person_size: float = 1.7) -> Dict[str, float]:
    """The full reflection bundle at one gathering point."""
    surfaces = surfaces_from_corners(corners, materials)
    occ = list(occluders) if occluders is not None else []
    all_occ = surfaces + occ
    interior_point = (float(np.mean([c[0] for c in corners])),
                      float(np.mean([c[1] for c in corners])))
    se = self_exposure(viewpoint, surfaces, interior_point, all_occ, person_size)
    out: Dict[str, float] = {
        "cnfa.reflection.self_exposure": se["self_exposure"],
        "cnfa.reflection.self_exposure_index": se["self_exposure_index"],
        "cnfa.reflection.self_image_count": float(se["n_self_images"]),
    }
    if se["nearest_image_distance"] is not None:
        out["cnfa.reflection.nearest_self_image_distance"] = float(se["nearest_image_distance"])
    if observers:
        rv = seen_via_reflection(viewpoint, observers, surfaces, interior_point, all_occ)
        out["cnfa.reflection.reflected_exposure"] = rv["reflected_fraction"]
    return out
