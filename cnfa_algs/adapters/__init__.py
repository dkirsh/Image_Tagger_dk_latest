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
  depth_pro_adapter     Apple Depth Pro metric monocular depth
                        -> geometry.DepthProvider priority-1 backend
  hawp_adapter          HAWP wireframe lines + junctions
                        -> improved vanishing-point estimation
  ulayout_adapter       uLayout room layout boundaries
                        -> plane label map for geometry.segment_planes(provided=)
  esanet_adapter        ESANet RGB-D semantic segmentation
                        -> plane label map using fused depth+RGB
  marigold_adapter      Marigold diffusion relative depth
                        -> geometry.DepthProvider (visual quality tier)
  saliency_adapter      TranSalNet deep fixation saliency
                        -> attributes.landmark_salience deep saliency backend
"""
