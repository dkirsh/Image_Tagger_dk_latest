"""cnfa_algs.adapters — drop-in front ends from external (downloadable) models.

Each adapter converts an external model's output into the structures our
attribute layer already consumes, so the behavioral functions never change:

  segmentation_adapter  ADE20K semantic segmentation (SegFormer et al.)
                        -> plane label map for geometry.segment_planes(provided=)
                        + material softness map for the acoustic proxy
  spatiallm_adapter     SpatialLM structured layout text (walls/doors/windows/bboxes)
                        -> plan.PlanGrid + seat list for sociopetal_seating
  structured3d_adapter  Structured3D annotation_3d.json ground truth
                        -> plan.PlanGrid (the L0 validator's reference plan)
"""
