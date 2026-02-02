"""
Instance Segmentation Analyzer using YOLO11m-seg.

This module provides instance segmentation capabilities for the science pipeline,
identifying and segmenting individual objects within architectural/interior images.

The segmentation model detects objects and provides pixel-level masks for each
instance, enabling detailed spatial analysis of scenes.

Architecture:
- Uses YOLOv11 medium segmentation model (yolo11m-seg.pt)
- Lazy loading pattern to minimize startup overhead
- Integrates with AnalysisFrame for pipeline compatibility
- Stores both counts and coverage metrics as attributes
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
import numpy as np

from backend.science.core import AnalysisFrame

# Lazy load ultralytics to keep startup fast if not used
YOLO_SEG_MODEL = None

logger = logging.getLogger("v3.science.segmentation")


class SegmentationAnalyzer:
    """
    Instance Segmentation Analyzer using YOLO11m-seg.
    
    Performs instance segmentation on images to:
    1. Identify objects with pixel-level masks
    2. Compute coverage metrics (what % of image is occupied by each class)
    3. Extract object counts by class
    4. Store segmentation masks for downstream analysis
    
    Attributes computed:
    - segmentation.{class_name}_count: Number of instances of each class
    - segmentation.{class_name}_coverage: Fraction of image covered by class
    - segmentation.total_objects: Total number of detected objects
    - segmentation.scene_coverage: Total fraction of image with detected objects
    """
    
    # COCO classes relevant to interior/architectural analysis
    ARCHITECTURAL_CLASSES = {
        'chair', 'couch', 'bed', 'dining table', 'toilet', 'tv', 'laptop',
        'refrigerator', 'oven', 'sink', 'potted plant', 'vase', 'clock',
        'book', 'bottle', 'cup', 'bowl', 'person', 'dog', 'cat', 'backpack',
        'umbrella', 'handbag', 'tie', 'suitcase', 'bench'
    }
    
    # Mapping to semantic groups for aggregation
    CLASS_GROUPS = {
        'seating': ['chair', 'couch', 'bench'],
        'surfaces': ['dining table', 'bed'],
        'appliances': ['refrigerator', 'oven', 'sink', 'tv', 'laptop'],
        'biophilia': ['potted plant', 'vase'],
        'occupants': ['person'],
        'pets': ['dog', 'cat'],
        'decor': ['clock', 'book', 'bottle', 'cup', 'bowl'],
    }

    @staticmethod
    def load_model():
        """
        Load the YOLO segmentation model (lazy loading).
        
        Uses yolo11m-seg (medium size) for a balance of accuracy and speed.
        The model will be downloaded automatically on first use (~50MB).
        """
        global YOLO_SEG_MODEL
        if YOLO_SEG_MODEL is None:
            from ultralytics import YOLO
            # yolo11m-seg provides good accuracy while being reasonably fast
            # Use 'yolo26x-seg' for maximum accuracy (slower, ~130MB)
            # Use 'yolo26n-seg' for fastest inference (~12MB)
            logger.info("Loading YOLO26l-seg model for instance segmentation...")
            YOLO_SEG_MODEL = YOLO("yolo26l-seg.pt")
            logger.info("YOLO26m-seg model loaded successfully")
    
    @staticmethod
    def analyze(frame: AnalysisFrame, confidence_threshold: float = 0.25) -> Dict[str, Any]:
        """
        Run instance segmentation on the image and extract metrics.
        
        Args:
            frame: AnalysisFrame containing the image to analyze
            confidence_threshold: Minimum confidence for detections (0.0-1.0)
            
        Returns:
            Dictionary containing:
            - counts: Dict of class -> count
            - coverages: Dict of class -> coverage fraction
            - masks: List of (class_name, mask_array, confidence, bbox) tuples
            - total_objects: Total number of detected objects
            - scene_coverage: Total image coverage by detected objects
        """
        SegmentationAnalyzer.load_model()
        
        # Run inference
        results = YOLO_SEG_MODEL(
            frame.original_image, 
            verbose=False,
            conf=confidence_threshold
        )
        
        # Initialize metrics
        counts: Dict[str, int] = {}
        coverages: Dict[str, float] = {}
        masks_data: List[Tuple[str, np.ndarray, float, List[float]]] = []
        
        img_h, img_w = frame.original_image.shape[:2]
        total_pixels = img_h * img_w
        
        # Combined mask for computing total scene coverage
        combined_mask = np.zeros((img_h, img_w), dtype=np.uint8)
        
        # Process results
        for result in results:
            if result.masks is None:
                continue
                
            masks = result.masks.data.cpu().numpy()  # (N, H, W)
            boxes = result.boxes
            
            for i, (mask, box) in enumerate(zip(masks, boxes)):
                cls_id = int(box.cls[0])
                confidence = float(box.conf[0])
                class_name = YOLO_SEG_MODEL.names[cls_id]
                
                # Skip low-relevance classes if not in our architectural set
                # (we still detect them, just don't aggregate)
                
                # Resize mask to image dimensions if needed
                if mask.shape != (img_h, img_w):
                    import cv2
                    mask = cv2.resize(
                        mask.astype(np.float32), 
                        (img_w, img_h), 
                        interpolation=cv2.INTER_LINEAR
                    )
                    mask = (mask > 0.5).astype(np.uint8)
                else:
                    mask = (mask > 0.5).astype(np.uint8)
                
                # Update counts
                counts[class_name] = counts.get(class_name, 0) + 1
                
                # Update coverage (accumulate for multiple instances)
                mask_pixels = np.count_nonzero(mask)
                coverage = mask_pixels / total_pixels
                coverages[class_name] = coverages.get(class_name, 0.0) + coverage
                
                # Update combined mask
                combined_mask = np.maximum(combined_mask, mask)
                
                # Store mask data for potential visualization
                bbox = box.xyxy[0].cpu().numpy().tolist()
                masks_data.append((class_name, mask, confidence, bbox))
        
        # Compute total scene coverage
        scene_coverage = np.count_nonzero(combined_mask) / total_pixels
        total_objects = sum(counts.values())
        
        # Store results in frame attributes
        # Object counts
        for class_name, count in counts.items():
            safe_name = class_name.replace(' ', '_')
            frame.add_attribute(f"segmentation.{safe_name}_count", count)
        
        # Coverage metrics
        for class_name, coverage in coverages.items():
            safe_name = class_name.replace(' ', '_')
            frame.add_attribute(f"segmentation.{safe_name}_coverage", coverage)
        
        # Aggregate metrics
        frame.add_attribute("segmentation.total_objects", total_objects)
        frame.add_attribute("segmentation.scene_coverage", scene_coverage)
        
        # Compute group-level metrics
        for group_name, class_list in SegmentationAnalyzer.CLASS_GROUPS.items():
            group_count = sum(counts.get(c, 0) for c in class_list)
            group_coverage = sum(coverages.get(c, 0.0) for c in class_list)
            frame.add_attribute(f"segmentation.group_{group_name}_count", group_count)
            frame.add_attribute(f"segmentation.group_{group_name}_coverage", group_coverage)
        
        # Store masks in frame metadata for downstream use
        frame.metadata["segmentation_masks"] = masks_data
        frame.metadata["segmentation_combined_mask"] = combined_mask
        
        logger.info(
            f"Segmentation complete: {total_objects} objects, "
            f"{scene_coverage:.1%} scene coverage"
        )
        
        return {
            "counts": counts,
            "coverages": coverages,
            "masks": masks_data,
            "total_objects": total_objects,
            "scene_coverage": scene_coverage,
        }
    
    @staticmethod
    def get_segmentation_overlay(
        frame: AnalysisFrame,
        alpha: float = 0.5,
        show_labels: bool = True,
        show_confidence: bool = True,
    ) -> Optional[np.ndarray]:
        """
        Generate a visualization overlay showing segmentation masks.
        
        Args:
            frame: AnalysisFrame with segmentation results
            alpha: Transparency of mask overlay (0.0-1.0)
            show_labels: Whether to draw class labels
            show_confidence: Whether to show confidence scores
            
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
        np.random.seed(42)  # Consistent colors across runs
        class_colors = {}
        
        for class_name, mask, confidence, bbox in masks_data:
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
            
            # Draw bounding box
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
