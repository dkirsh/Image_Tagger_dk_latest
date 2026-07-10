"""IsovistAdapter — emit cnfa.spatial.* / cnfa.topology.* from a plan.

Unlike the image adapters, this one consumes a *plan* (occupancy grid) and a
*viewpoint*, not a photo — it is the space-side of the annotation system. It runs
in the 3D-model / floor-plan pipeline (where the geometry is known) and, later,
on the pseudo-plan recovered from a depth map. Attach a `Plan` as `frame.plan`
and a viewpoint as `frame.viewpoint = (x, y)`; or call `annotate_plan(...)`
directly.

Belongs to the OWNED build (clean-room, no GPL). The research build can wrap
depthmapX to cross-validate these numbers.
"""
from __future__ import annotations

from typing import Dict, Optional, Tuple

from ..base import AnalyzerAdapter, License
from .isovist import Plan, isovist_measures, visibility_graph

Point = Tuple[float, float]

# isovist measure key -> cnfa attribute
_ISOVIST_MAP = {
    "area": "cnfa.spatial.isovist_area",
    "perimeter": "cnfa.spatial.isovist_perimeter",
    "occlusivity": "cnfa.spatial.isovist_occlusivity",
    "compactness": "cnfa.spatial.isovist_compactness",
    "min_radial": "cnfa.spatial.isovist_min_radial",
    "max_radial": "cnfa.spatial.isovist_max_radial",
    "mean_radial": "cnfa.spatial.isovist_mean_radial",
    "radial_variance": "cnfa.spatial.isovist_variance",
    "radial_skewness": "cnfa.spatial.isovist_skewness",
    "drift_magnitude": "cnfa.spatial.isovist_drift",
    "elongation": "cnfa.spatial.isovist_elongation",
    "jaggedness": "cnfa.spatial.isovist_jaggedness",
    "dispersion": "cnfa.spatial.isovist_dispersion",
}


def annotate_plan(plan: Plan, viewpoint: Point, with_graph: bool = True,
                  n_rays: int = 720, graph_stride: int = 4) -> Dict[str, float]:
    """Return the cnfa.* isovist + visibility-graph attributes at `viewpoint`."""
    out: Dict[str, float] = {}
    m = isovist_measures(plan, viewpoint, n_rays=n_rays)
    for k, key in _ISOVIST_MAP.items():
        v = m.get(k)
        if v is not None and abs(v) != float("inf"):
            out[key] = float(v)

    if with_graph:
        vg = visibility_graph(plan, stride=graph_stride)
        # value at the sampled node nearest the viewpoint
        nodes = list(vg.connectivity.keys())
        if nodes:
            nx, ny = min(nodes, key=lambda p: (p[0] - viewpoint[0]) ** 2 + (p[1] - viewpoint[1]) ** 2)
            out["cnfa.topology.connectivity"] = float(vg.connectivity[(nx, ny)])
            out["cnfa.topology.mean_depth"] = float(vg.mean_depth[(nx, ny)])
            out["cnfa.topology.integration_value"] = float(vg.integration[(nx, ny)])
            out["cnfa.topology.clustering_coefficient"] = float(vg.clustering[(nx, ny)])
        out["cnfa.topology.intelligibility"] = float(vg.intelligibility)
        out["cnfa.topology.mean_integration"] = float(vg.mean_integration)
    return out


class IsovistAdapter(AnalyzerAdapter):
    name = "isovist"
    tool = "cnfa-isovist(clean-room)"
    tool_version = "1.0"
    license_class = License.PERMISSIVE
    enable_flag = "enable_isovist"
    requires = ()  # numpy only (checked via base)
    provides = tuple(_ISOVIST_MAP.values()) + (
        "cnfa.topology.connectivity",
        "cnfa.topology.mean_depth",
        "cnfa.topology.integration_value",
        "cnfa.topology.clustering_coefficient",
        "cnfa.topology.intelligibility",
        "cnfa.topology.mean_integration",
    )

    def _analyze(self, frame) -> None:
        plan: Optional[Plan] = getattr(frame, "plan", None)
        viewpoint: Optional[Point] = getattr(frame, "viewpoint", None)
        if plan is None or viewpoint is None:
            return  # image-only frame; nothing to do
        with_graph = getattr(frame, "isovist_with_graph", True)
        for key, value in annotate_plan(plan, viewpoint, with_graph=with_graph).items():
            self.emit(frame, key, value)
