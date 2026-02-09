"""
Instance and Semantic Segmentation Analyzer using OneFormer.

This module provides comprehensive segmentation capabilities for the science pipeline,
identifying and segmenting individual objects and semantic regions within architectural/interior images.

The OneFormer model provides:
- Semantic segmentation (scene understanding)
- Instance segmentation (individual object detection)
- Panoptic segmentation (combined semantic + instance)

Architecture:
- Uses Hugging Face OneFormer model (shi-labs/oneformer_ade20k_swin_large)
- Lazy loading pattern to minimize startup overhead
- Integrates with AnalysisFrame for pipeline compatibility
- Stores both counts and coverage metrics as attributes
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict
import numpy as np
from PIL import Image

from backend.science.core import AnalysisFrame

# Lazy load transformers and torch to keep startup fast
ONEFORMER_MODEL = None
ONEFORMER_PROCESSOR = None

logger = logging.getLogger("v3.science.segmentation")


class SegmentationAnalyzer:
    """
    Segmentation Analyzer using OneFormer.
    
    Performs semantic and instance segmentation on images to:
    1. Identify semantic regions (walls, floors, ceilings, furniture)
    2. Detect individual object instances with pixel-level masks
    3. Compute coverage metrics (what % of image is occupied by each class)
    4. Extract object counts by class
    5. Store segmentation masks for downstream analysis
    
    All class labels are dynamically determined from model.config.id2label.
    No hardcoded class lists or groupings.
    
    Attributes computed:
    - segmentation.{class_name}_count: Number of instances of each class
    - segmentation.{class_name}_coverage: Fraction of image covered by class
    - segmentation.total_objects: Total number of detected instances
    - segmentation.scene_coverage: Total fraction of image with detected objects
    - segmentation.semantic_*: Semantic region metrics
    """

    @staticmethod
    def load_model():
        """
        Load the OneFormer model (lazy loading).
        
        Uses shi-labs/oneformer_ade20k_swin_large for high-quality segmentation.
        The model will be downloaded automatically on first use (~1.5GB).
        
        Alternative models:
        - shi-labs/oneformer_ade20k_swin_tiny (faster, smaller)
        - shi-labs/oneformer_coco_swin_large (COCO dataset)
        """
        global ONEFORMER_MODEL, ONEFORMER_PROCESSOR
        if ONEFORMER_MODEL is None:
            from transformers import OneFormerProcessor, OneFormerForUniversalSegmentation
            
            model_name = "shi-labs/oneformer_ade20k_swin_tiny"
            logger.info(f"Loading OneFormer model: {model_name}")
            
            ONEFORMER_PROCESSOR = OneFormerProcessor.from_pretrained(model_name)
            ONEFORMER_MODEL = OneFormerForUniversalSegmentation.from_pretrained(model_name)
            
            logger.info("OneFormer model loaded successfully")
    
    @staticmethod
    def _semantic_to_metrics(semantic_map: np.ndarray, id2label: Dict) -> Tuple[Dict, Dict]:
        """
        Convert semantic segmentation map to counts and coverage metrics.
        
        Args:
            semantic_map: HxW array of class IDs
            id2label: Mapping from class ID to label name
            
        Returns:
            counts: Dict of class -> count (always 1 for semantic)
            coverages: Dict of class -> coverage fraction
        """
        unique_classes = np.unique(semantic_map)
        total_pixels = semantic_map.size
        
        counts = {}
        coverages = {}
        
        for class_id in unique_classes:
            mask = (semantic_map == class_id)
            pixel_count = mask.sum()
            
            if pixel_count > 100:  # Filter tiny segments
                class_name = id2label.get(int(class_id), f'class_{class_id}')
                counts[class_name] = 1  # Semantic only has one segment per class
                coverages[class_name] = pixel_count / total_pixels
        
        return counts, coverages
    
    @staticmethod
    def _panoptic_to_metrics(panoptic_result: Dict, id2label: Dict) -> Tuple[Dict, Dict, List]:
        """
        Convert panoptic segmentation to instance counts and coverage metrics.
        
        Args:
            panoptic_result: Panoptic segmentation result from processor
            id2label: Mapping from class ID to label name
            
        Returns:
            counts: Dict of class -> instance count
            coverages: Dict of class -> total coverage fraction
            masks_data: List of (class_name, mask, confidence, bbox, is_thing)
        """
        seg_map = panoptic_result['segmentation'].numpy()
        segments = panoptic_result['segments_info']
        total_pixels = seg_map.size
        
        counts = {}
        coverages = {}
        masks_data = []
        
        for segment in segments:
            mask = (seg_map == segment['id'])
            pixel_count = mask.sum()
            
            if pixel_count > 100:  # Filter tiny segments
                class_name = id2label.get(segment['label_id'], f"class_{segment['label_id']}")
                is_thing = segment.get('isthing', True)
                confidence = segment.get('score', 1.0)
                
                # Update counts (only for instances, not stuff)
                if is_thing:
                    counts[class_name] = counts.get(class_name, 0) + 1
                else:
                    counts[class_name] = counts.get(class_name, 0)
                
                # Update coverage (accumulate for multiple instances)
                coverage = pixel_count / total_pixels
                coverages[class_name] = coverages.get(class_name, 0.0) + coverage
                
                # Compute bounding box
                ys, xs = np.where(mask)
                if len(ys) > 0:
                    bbox = [float(xs.min()), float(ys.min()), 
                           float(xs.max()), float(ys.max())]
                else:
                    bbox = [0, 0, 0, 0]
                
                masks_data.append((class_name, mask.astype(np.uint8), confidence, bbox, is_thing))
        
        return counts, coverages, masks_data
    
    @staticmethod
    def analyze(frame: AnalysisFrame, use_semantic: bool = True, use_panoptic: bool = True) -> Dict[str, Any]:
        """
        Run segmentation on the image and extract metrics.
        
        Args:
            frame: AnalysisFrame containing the image to analyze
            use_semantic: Whether to run semantic segmentation
            use_panoptic: Whether to run panoptic (instance) segmentation
            
        Returns:
            Dictionary containing:
            - semantic_counts: Dict of class -> 1 (semantic regions)
            - semantic_coverages: Dict of class -> coverage fraction
            - instance_counts: Dict of class -> instance count
            - instance_coverages: Dict of class -> coverage fraction
            - masks: List of mask data tuples
            - total_instances: Total number of detected instances
            - scene_coverage: Total image coverage
        """
        SegmentationAnalyzer.load_model()
        
        # Convert numpy array to PIL Image if needed
        if isinstance(frame.original_image, np.ndarray):
            image_pil = Image.fromarray(frame.original_image)
        else:
            image_pil = frame.original_image
        
        id2label = ONEFORMER_MODEL.config.id2label
        results = {}
        
        # Semantic segmentation
        if use_semantic:
            logger.info("Running semantic segmentation...")
            semantic_inputs = ONEFORMER_PROCESSOR(
                images=image_pil, 
                task_inputs=["semantic"], 
                return_tensors="pt"
            )
            
            import torch
            with torch.no_grad():
                semantic_outputs = ONEFORMER_MODEL(**semantic_inputs)
            
            semantic_map = ONEFORMER_PROCESSOR.post_process_semantic_segmentation(
                semantic_outputs, target_sizes=[image_pil.size[::-1]]
            )[0]
            
            semantic_counts, semantic_coverages = SegmentationAnalyzer._semantic_to_metrics(
                semantic_map.numpy(), id2label
            )
            
            results['semantic_counts'] = semantic_counts
            results['semantic_coverages'] = semantic_coverages
            results['semantic_map'] = semantic_map.numpy()
            
            # Store semantic metrics in frame
            for class_name, coverage in semantic_coverages.items():
                safe_name = class_name.replace(' ', '_')
                frame.add_attribute(f"segmentation.semantic_{safe_name}_coverage", coverage)
        
        # Panoptic segmentation (for instances)
        if use_panoptic:
            logger.info("Running panoptic segmentation...")
            panoptic_inputs = ONEFORMER_PROCESSOR(
                images=image_pil,
                task_inputs=["panoptic"],
                return_tensors="pt"
            )
            
            import torch
            with torch.no_grad():
                panoptic_outputs = ONEFORMER_MODEL(**panoptic_inputs)
            
            panoptic_result = ONEFORMER_PROCESSOR.post_process_panoptic_segmentation(
                panoptic_outputs,
                target_sizes=[image_pil.size[::-1]],
                label_ids_to_fuse=set()
            )[0]
            
            instance_counts, instance_coverages, masks_data = SegmentationAnalyzer._panoptic_to_metrics(
                panoptic_result, id2label
            )
            
            results['instance_counts'] = instance_counts
            results['instance_coverages'] = instance_coverages
            results['masks'] = masks_data
            
            # Compute combined mask for scene coverage
            seg_map = panoptic_result['segmentation'].numpy()
            combined_mask = (seg_map > 0).astype(np.uint8)
            scene_coverage = combined_mask.sum() / combined_mask.size
            
            results['total_instances'] = sum(instance_counts.values())
            results['scene_coverage'] = scene_coverage
            
            # Store instance metrics in frame
            for class_name, count in instance_counts.items():
                safe_name = class_name.replace(' ', '_')
                frame.add_attribute(f"segmentation.{safe_name}_count", count)
            
            for class_name, coverage in instance_coverages.items():
                safe_name = class_name.replace(' ', '_')
                frame.add_attribute(f"segmentation.{safe_name}_coverage", coverage)
            
            frame.add_attribute("segmentation.total_objects", results['total_instances'])
            frame.add_attribute("segmentation.scene_coverage", scene_coverage)
            
            # Store masks in frame metadata
            frame.metadata["segmentation_masks"] = masks_data
            frame.metadata["segmentation_combined_mask"] = combined_mask
            
            logger.info(
                f"Segmentation complete: {results['total_instances']} instances, "
                f"{scene_coverage:.1%} scene coverage"
            )
        
        return results
    
    @staticmethod
    def get_segmentation_overlay(
        frame: AnalysisFrame,
        alpha: float = 0.5,
        show_labels: bool = True,
        show_confidence: bool = True,
        filter_stuff: bool = False
    ) -> Optional[np.ndarray]:
        """
        Generate a visualization overlay showing segmentation masks.
        
        Args:
            frame: AnalysisFrame with segmentation results
            alpha: Transparency of mask overlay (0.0-1.0)
            show_labels: Whether to draw class labels
            show_confidence: Whether to show confidence scores
            filter_stuff: Only show instance segments (not semantic stuff)
            
        Returns:
            RGB image with segmentation overlay, or None if no masks
        """
        masks_data = frame.metadata.get("segmentation_masks")
        if not masks_data:
            return None
        
        import cv2
        
        # Create overlay image
        overlay = frame.original_image.copy()
        
        # Generate distinct colors for each class
        np.random.seed(42)
        class_colors = {}
        
        for class_name, mask, confidence, bbox, is_thing in masks_data:
            # Skip stuff categories if filtering
            if filter_stuff and not is_thing:
                continue
            
            # Get or generate color for this class
            if class_name not in class_colors:
                class_colors[class_name] = tuple(
                    int(c) for c in np.random.randint(100, 255, 3)
                )
            color = class_colors[class_name]
            
            # Apply colored mask
            colored_mask = np.zeros_like(overlay)
            colored_mask[mask > 0] = color
            overlay = cv2.addWeighted(overlay, 1, colored_mask, alpha, 0)
            
            # Draw bounding box (only for instances)
            if is_thing:
                x1, y1, x2, y2 = [int(c) for c in bbox]
                cv2.rectangle(overlay, (x1, y1), (x2, y2), color, 2)
                
                # Draw label
                if show_labels:
                    label = class_name
                    if show_confidence:
                        label = f"{class_name} {confidence:.0%}"
                    
                    # Label background
                    (label_w, label_h), baseline = cv2.getTextSize(
                        label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
                    )
                    cv2.rectangle(
                        overlay,
                        (x1, y1 - label_h - baseline - 5),
                        (x1 + label_w + 5, y1),
                        color,
                        -1
                    )
                    # Label text
                    cv2.putText(
                        overlay, label,
                        (x1 + 2, y1 - baseline - 2),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (255, 255, 255), 1
                    )
        
        return overlay


def run_segmentation_on_image(image: np.ndarray, image_id: int = -1) -> Dict[str, Any]:
    """
    Convenience function to run segmentation on a single image.
    
    Args:
        image: RGB numpy array (H, W, 3)
        image_id: Optional image ID for tracking
        
    Returns:
        Dictionary with segmentation results
    """
    frame = AnalysisFrame(image_id=image_id, original_image=image)
    return SegmentationAnalyzer.analyze(frame)