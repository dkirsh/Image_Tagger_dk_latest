"""cnfa_algs — operational CNfA attribute algorithms.

Tiers:
  A   (M1/M2)  image-plane heatmaps & overlays from pixels (+depth/seg)
  B   (M2.5)   inferred floor plan from a single image -> true plan fields
  C   (M3)     the same plan fields on a supplied floor plan, precise

Convention shared with Image_Tagger: set DEPTH_ANYTHING_ONNX_PATH to use a
real monocular depth model; otherwise a geometric ground-plane fallback runs
at reduced confidence.
"""
from .core import AttributeResult, heatmap_overlay, region_overlay, mask_overlay, \
    annotate_title, gallery, save_results_json, normalize01
from .geometry import estimate_vanishing_point, segment_planes, DepthProvider, \
    FLOOR, CEILING, WALL, OPENING, UNKNOWN, PLANE_PALETTE, PLANE_LEGEND
from . import attributes
from .plan import infer_plan_from_image, plan_from_floorplan_image, \
    isovist_fields, camera_isovist_polygon, render_plan_topo, PlanGrid
from .composition import rule_of_thirds, visual_balance

