from __future__ import annotations

import io
import os
from pathlib import Path
from typing import Optional, Union
import hashlib

import numpy as np

try:
    import cv2  # type: ignore
except Exception:  # pragma: no cover - cv2 may not be available in tiny CI images
    cv2 = None  # type: ignore

try:
    import requests
except Exception:
    requests = None  # type: ignore

from fastapi import APIRouter, Depends, HTTPException, Response, status
from backend.science import pipeline as science_pipeline
from backend.science.core import AnalysisFrame
from backend.science.spatial.depth import DepthAnalyzer
from backend.science.vision.segmentation import SegmentationAnalyzer
from backend.science.vision.room_detection import RoomDetectionAnalyzer, COARSE_CATEGORIES
from sqlalchemy.orm import Session

from backend.database.core import get_db
from backend.models.assets import Image  # type: ignore
from backend.services.auth import CurrentUser, require_tagger

router = APIRouter(prefix="/v1/debug", tags=["Debug / Science"])


def _is_url(path: str) -> bool:
    """Check if the path is a URL."""
    return path.startswith("http://") or path.startswith("https://")


def _load_image_from_url_or_path(storage_path: str) -> np.ndarray:
    """Load an image from either a URL or a local file path.
    
    Returns the image as a BGR numpy array (OpenCV format).
    Raises HTTPException if the image cannot be loaded.
    """
    if cv2 is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="cv2 (OpenCV) is not available.",
        )

    if _is_url(storage_path):
        # Download image from URL
        if requests is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="requests library is not available; cannot fetch remote images.",
            )
        try:
            response = requests.get(storage_path, timeout=10)
            response.raise_for_status()
            img_array = np.frombuffer(response.content, dtype=np.uint8)
            img_bgr = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if img_bgr is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Could not decode image from URL: {storage_path}",
                )
            return img_bgr
        except requests.RequestException as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to download image from URL: {storage_path} - {str(e)}",
            )
    else:
        # Load from local file
        path = _resolve_image_path(storage_path)
        if not path.is_file():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Image file not found on disk: {path}",
            )
        img_bgr = cv2.imread(str(path))
        if img_bgr is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Could not read image from storage: {path}",
            )
        return img_bgr


def _get_cache_key(storage_path: str) -> str:
    """Generate a cache key from a storage path (works for both URLs and local paths)."""
    if _is_url(storage_path):
        # Use hash of URL for cache key to avoid filesystem issues
        return hashlib.md5(storage_path.encode()).hexdigest()
    else:
        return Path(storage_path).stem


def _resolve_image_path(storage_path: str) -> Path:
    """Resolve the on-disk path for a stored image.

    The storage_path column is expected to contain either an absolute
    path or a path relative to the working directory / IMAGE_STORAGE_ROOT.
    We first try the path as-is; if it does not exist and is relative,
    we fall back to IMAGE_STORAGE_ROOT + storage_path.
    """
    raw = Path(storage_path)
    if raw.is_file():
        return raw

    # Try prefixing with IMAGE_STORAGE_ROOT if provided
    root = os.getenv("IMAGE_STORAGE_ROOT")
    if root:
        candidate = Path(root) / storage_path
        if candidate.is_file():
            return candidate

    return raw  # Best-effort; caller will handle missing file

def _compute_edge_map_bytes(storage_path: str, t1: int = 50, t2: int = 150, l2: bool = True) -> bytes:
    """Compute a Canny edge map PNG for the given image.

    This mirrors the logic in backend.science.core.AnalysisFrame.compute_derived,
    but is implemented locally to keep the debug endpoint self-contained.

    To keep things efficient in classroom settings, we maintain a tiny on-disk
    cache keyed by (image, thresholds, L2 flag). If a matching PNG already
    exists, we serve it directly instead of recomputing.
    
    Supports both local file paths and remote URLs.
    """
    if cv2 is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="cv2 (OpenCV) is not available; cannot compute edge maps.",
        )

    # Compute cache path
    cache_root = os.getenv("IMAGE_DEBUG_CACHE_ROOT") or os.path.join("backend", "data", "debug_edges")
    cache_root_path = Path(cache_root)
    cache_root_path.mkdir(parents=True, exist_ok=True)

    cache_key = _get_cache_key(storage_path)
    cache_name = f"{cache_key}_edges_{t1}_{t2}_{1 if l2 else 0}.png"
    cache_path = cache_root_path / cache_name

    if cache_path.is_file():
        try:
            return cache_path.read_bytes()
        except Exception:
            # Fall through to recomputation on any read error
            pass

    # Load image from URL or local path
    img_bgr = _load_image_from_url_or_path(storage_path)

    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    # Allow experimentation with thresholds and the L2gradient flag
    edges = cv2.Canny(gray, t1, t2, L2gradient=l2)

    ok, buf = cv2.imencode(".png", edges)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to encode edge map as PNG.",
        )

    data = buf.tobytes()
    try:
        cache_path.write_bytes(data)
    except Exception:
        # Cache write failure should not break the endpoint
        pass
    return data



def _compute_complexity_heatmap_bytes(
    storage_path: str, 
    patch_size: int = 64, 
    stride: int = 32,
    canny_low: int = 50,
    canny_high: int = 150,
) -> bytes:
    """Compute a regionalized complexity heatmap PNG for the given image.

    This implements the edge-density approach from complexity_regions_demo.py:
    For each patch in a sliding window, compute:
        complexity_score = edge_pixels / total_pixels
    
    The result is a heatmap overlaid on the original image, where:
    - Red/Yellow = High complexity (many edges)
    - Dark Red/Black = Low complexity (few edges)
    
    Supports both local file paths and remote URLs.
    """
    if cv2 is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="cv2 (OpenCV) is not available; cannot compute complexity heatmaps.",
        )

    # Compute cache path
    cache_root = os.getenv("IMAGE_COMPLEXITY_CACHE_ROOT") or os.path.join("backend", "data", "debug_complexity")
    cache_root_path = Path(cache_root)
    cache_root_path.mkdir(parents=True, exist_ok=True)

    cache_key = _get_cache_key(storage_path)
    cache_name = f"{cache_key}_complexity_{patch_size}_{stride}_{canny_low}_{canny_high}.png"
    cache_path = cache_root_path / cache_name

    if cache_path.is_file():
        try:
            return cache_path.read_bytes()
        except Exception:
            pass

    # Load image from URL or local path
    img_bgr = _load_image_from_url_or_path(storage_path)

    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape

    # Compute complexity for each patch using sliding window
    out_h = max(1, (h - patch_size) // stride + 1)
    out_w = max(1, (w - patch_size) // stride + 1)
    complexity_map = np.zeros((out_h, out_w), dtype=np.float32)

    for i in range(out_h):
        for j in range(out_w):
            y_start = i * stride
            x_start = j * stride
            patch = gray[y_start:y_start+patch_size, x_start:x_start+patch_size]
            
            # Apply Canny edge detector
            edges = cv2.Canny(patch, canny_low, canny_high)
            
            # Compute edge density = edge_pixels / total_pixels
            edge_pixels = np.count_nonzero(edges)
            total_pixels = edges.shape[0] * edges.shape[1]
            complexity_map[i, j] = edge_pixels / total_pixels if total_pixels > 0 else 0.0

    # Resize heatmap to match original image dimensions
    heatmap_resized = cv2.resize(complexity_map, (w, h), interpolation=cv2.INTER_LINEAR)

    # Normalize to 0-255 and apply colormap
    heatmap_normalized = (heatmap_resized * 255).astype(np.uint8)
    heatmap_colored = cv2.applyColorMap(heatmap_normalized, cv2.COLORMAP_HOT)

    # Blend with original image (50% opacity overlay)
    blended = cv2.addWeighted(img_bgr, 0.5, heatmap_colored, 0.5, 0)

    ok, buf = cv2.imencode(".png", blended)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to encode complexity heatmap as PNG.",
        )

    data = buf.tobytes()
    try:
        cache_path.write_bytes(data)
    except Exception:
        pass
    return data


def _compute_segmentation_overlay_bytes(
    storage_path: str,
    alpha: float = 0.5,
    conf: float = 0.25,
    show_labels: bool = True,
) -> bytes:
    """Compute an instance segmentation overlay PNG for the given image.

    Uses YOLO11m-seg to detect and segment objects, then overlays colored
    masks on the original image.
    
    Supports both local file paths and remote URLs.
    
    Args:
        storage_path: Path to image (local or URL)
        alpha: Mask transparency (0.0-1.0)
        conf: Minimum detection confidence (0.0-1.0)
        show_labels: Whether to draw class labels and confidence
        
    Returns:
        PNG image bytes with segmentation overlay
    """
    if cv2 is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="cv2 (OpenCV) is not available; cannot compute segmentation.",
        )

    # Compute cache path
    cache_root = os.getenv("IMAGE_SEGMENTATION_CACHE_ROOT") or os.path.join("backend", "data", "debug_segmentation")
    cache_root_path = Path(cache_root)
    cache_root_path.mkdir(parents=True, exist_ok=True)

    cache_key = _get_cache_key(storage_path)
    cache_name = f"{cache_key}_seg_{int(alpha*100)}_{int(conf*100)}_{1 if show_labels else 0}.png"
    cache_path = cache_root_path / cache_name

    if cache_path.is_file():
        try:
            return cache_path.read_bytes()
        except Exception:
            pass

    # Load image from URL or local path (BGR format)
    img_bgr = _load_image_from_url_or_path(storage_path)
    
    # Convert to RGB for YOLO/AnalysisFrame
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    
    # Create analysis frame and run segmentation
    frame = AnalysisFrame(image_id=-1, original_image=img_rgb)
    
    try:
        SegmentationAnalyzer.analyze(frame, confidence_threshold=conf)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Segmentation failed: {str(e)}. Ensure ultralytics is installed.",
        )
    
    # Get segmentation masks from frame metadata
    masks_data = frame.metadata.get("segmentation_masks", [])
    
    if not masks_data:
        # No objects detected - return original image with info text
        overlay = img_bgr.copy()
        cv2.putText(
            overlay, "No objects detected",
            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2
        )
    else:
        # Create overlay with colored masks
        overlay = img_bgr.copy()
        
        # Generate distinct colors for each class
        np.random.seed(42)  # Consistent colors
        class_colors = {}
        
        for class_name, mask, confidence, bbox in masks_data:
            # Get or generate color for this class
            if class_name not in class_colors:
                class_colors[class_name] = tuple(
                    int(c) for c in np.random.randint(100, 255, 3)
                )
            color = class_colors[class_name]
            
            # Apply colored mask (BGR format)
            colored_mask = np.zeros_like(overlay)
            colored_mask[mask > 0] = color
            overlay = cv2.addWeighted(overlay, 1, colored_mask, alpha, 0)
            
            # Draw bounding box
            x1, y1, x2, y2 = [int(c) for c in bbox]
            cv2.rectangle(overlay, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            if show_labels:
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
        
        # Add summary text
        total_objects = len(masks_data)
        scene_coverage = frame.attributes.get("segmentation.scene_coverage", 0)
        summary = f"Objects: {total_objects} | Coverage: {scene_coverage:.1%}"
        cv2.putText(
            overlay, summary,
            (10, overlay.shape[0] - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2
        )

    ok, buf = cv2.imencode(".png", overlay)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to encode segmentation overlay as PNG.",
        )

    data = buf.tobytes()
    try:
        cache_path.write_bytes(data)
    except Exception:
        pass
    return data


def _compute_depth_map_bytes(path: Path) -> bytes:
    """Compute a depth-map PNG for the given image path.

    This uses the DepthAnalyzer's monocular depth model if it is configured
    (via DEPTH_ANYTHING_ONNX_PATH and onnxruntime). If depth inference is
    not available, we surface a 503 so that the frontend can show a clear
    maintenance overlay rather than silently failing.

    The returned PNG is a single-channel grayscale image where lighter
    pixels correspond to *farther* regions and darker pixels to nearer
    regions, after a simple per-image normalisation.
    """
    if cv2 is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="cv2 (OpenCV) is not available; cannot compute depth maps.",
        )

    # Compute cache path
    cache_root = os.getenv("IMAGE_DEPTH_DEBUG_CACHE_ROOT") or os.path.join("backend", "data", "debug_depth")
    cache_root_path = Path(cache_root)
    cache_root_path.mkdir(parents=True, exist_ok=True)

    cache_name = f"{path.stem}_depth.png"
    cache_path = cache_root_path / cache_name

    if cache_path.is_file():
        try:
            return cache_path.read_bytes()
        except Exception:
            # Fall through to recomputation on any read error
            pass

    img_bgr = cv2.imread(str(path))
    if img_bgr is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not read image from storage: {path}",
        )

    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    # Minimal AnalysisFrame: we only need original_image and a dummy id.
    frame = AnalysisFrame(image_id=-1, original_image=img_rgb)

    depth = DepthAnalyzer._compute_depth_map(frame)
    if depth is None:
        # Surface as a 503 so clients know depth debug is temporarily
        # unavailable (e.g. missing model weights or onnxruntime).
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Depth debug is not configured. Ensure DEPTH_ANYTHING_ONNX_PATH "
                "is set and onnxruntime is installed."
            ),
        )

    import numpy as _np  # local alias to keep debug module dependency-light

    arr = _np.asarray(depth, dtype="float32")
    if arr.ndim == 3:
        arr = arr[..., 0]
    if arr.ndim != 2 or arr.size == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Depth model returned an invalid depth map.",
        )

    # Normalise depth to [0, 1] per-image to maximise visual contrast.
    d_min = float(_np.nanmin(arr))
    d_max = float(_np.nanmax(arr))
    if not _np.isfinite(d_min) or not _np.isfinite(d_max):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Depth map contained only NaN / Inf values.",
        )

    if d_max > d_min:
        norm = (arr - d_min) / (d_max - d_min)
    else:
        norm = _np.zeros_like(arr, dtype="float32")

    norm = _np.clip(norm, 0.0, 1.0)
    depth_uint8 = (norm * 255.0).astype("uint8")

    ok, buf = cv2.imencode(".png", depth_uint8)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to encode depth map as PNG.",
        )

    data = buf.tobytes()
    try:
        cache_path.write_bytes(data)
    except Exception:
        # Cache write failure should not break the endpoint
        pass
    return data


@router.get("/images/{image_id}/edges", summary="Return edge-map debug view for an image")
def get_image_edge_map(
    image_id: int,
    t1: int = 50,
    t2: int = 150,
    l2: bool = True,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tagger),
) -> Response:
    """Serve a PNG edge map for the requested image.

    This endpoint is intended purely for *debug / teaching* purposes. It
    allows Explorer (and other tools) to show "what the algorithm sees"
    when computing complexity and related metrics.
    
    Supports both local file paths and remote URLs.
    """
    image: Optional[Image] = db.query(Image).filter(Image.id == image_id).first()
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")

    storage_path = getattr(image, "storage_path", None)
    if not storage_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image has no storage_path configured",
        )

    data = _compute_edge_map_bytes(storage_path, t1=t1, t2=t2, l2=l2)
    return Response(content=data, media_type="image/png")


@router.get("/images/{image_id}/depth", summary="Return depth-map debug view for an image")
def get_image_depth_map(
    image_id: int,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tagger),
) -> Response:
    """Serve a PNG depth map for the requested image.

    This endpoint is intended purely for *debug / teaching* purposes. It
    exposes the monocular depth prediction used by the spatial metrics so
    that students can see "what the model thinks is near vs far".

    If the depth model is not configured, the endpoint returns HTTP 503 so
    that the frontend can surface a clear maintenance overlay instead of
    a generic network error.
    """
    from backend.models.assets import Image  # local import to avoid circularity

    session: Session = db
    image = session.query(Image).filter(Image.id == image_id).one_or_none()
    if image is None or not image.storage_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image {image_id} not found or has no storage_path.",
        )

    path = _resolve_image_path(image.storage_path)

    data = _compute_depth_map_bytes(path)
    return Response(content=data, media_type="image/png")
@router.get("/images/{image_id}/complexity", summary="Return complexity heatmap debug view for an image")
def get_image_complexity_heatmap(
    image_id: int,
    patch_size: int = 64,
    stride: int = 32,
    t1: int = 50,
    t2: int = 150,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tagger),
) -> Response:
    """Serve a PNG complexity heatmap for the requested image.

    This endpoint shows regionalized edge density across the image:
    - Each patch is analyzed using Canny edge detection
    - complexity_score = edge_pixels / total_pixels
    - Results are displayed as a heatmap overlay (red=high, dark=low)

    Supports both local file paths and remote URLs.

    Parameters:
    - patch_size: Size of each analysis region (default 64)
    - stride: Step size between regions (default 32)
    - t1, t2: Canny edge detection thresholds
    """
    image: Optional[Image] = db.query(Image).filter(Image.id == image_id).first()
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")

    storage_path = getattr(image, "storage_path", None)
    if not storage_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image has no storage_path configured",
        )

    data = _compute_complexity_heatmap_bytes(
        storage_path, 
        patch_size=patch_size, 
        stride=stride,
        canny_low=t1,
        canny_high=t2,
    )
    return Response(content=data, media_type="image/png")


@router.get("/images/{image_id}/segmentation", summary="Return instance segmentation overlay for an image")
def get_image_segmentation(
    image_id: int,
    alpha: float = 0.5,
    conf: float = 0.25,
    labels: bool = True,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tagger),
) -> Response:
    """Serve a PNG instance segmentation overlay for the requested image.

    This endpoint uses YOLO11m-seg to detect and segment objects in the image,
    then overlays colored masks showing each detected instance.

    The overlay includes:
    - Colored masks for each detected object
    - Bounding boxes around objects
    - Class labels with confidence scores (optional)
    - Summary of total objects and scene coverage

    Supports both local file paths and remote URLs.

    Parameters:
    - alpha: Mask transparency (0.0-1.0, default 0.5)
    - conf: Minimum detection confidence (0.0-1.0, default 0.25)
    - labels: Whether to show class labels (default True)
    """
    image: Optional[Image] = db.query(Image).filter(Image.id == image_id).first()
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")

    storage_path = getattr(image, "storage_path", None)
    if not storage_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image has no storage_path configured",
        )

    data = _compute_segmentation_overlay_bytes(
        storage_path,
        alpha=alpha,
        conf=conf,
        show_labels=labels,
    )
    return Response(content=data, media_type="image/png")


def _compute_room_detection_overlay_bytes(
    storage_path: str,
) -> bytes:
    """Compute a room detection overlay PNG for the given image.

    Uses Places365 classifier to identify room type and displays the
    classification results overlaid on the original image.
    
    Args:
        storage_path: Path to image (local or URL)
        
    Returns:
        PNG image bytes with room detection overlay
    """
    if cv2 is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="cv2 (OpenCV) is not available; cannot compute room detection.",
        )

    # Load image from URL or local path (BGR format)
    img_bgr = _load_image_from_url_or_path(storage_path)
    
    # Convert to RGB for analysis
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    
    # Create analysis frame and run room detection
    frame = AnalysisFrame(image_id=-1, original_image=img_rgb)
    
    try:
        result = RoomDetectionAnalyzer.analyze(frame, top_k=5, apply_object_consistency=False)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Room detection failed: {str(e)}. Ensure torch/torchvision is installed.",
        )
    
    # Create overlay
    overlay = img_bgr.copy()
    h, w = overlay.shape[:2]
    
    # Semi-transparent background for text
    panel_height = 180
    panel = np.zeros((panel_height, w, 3), dtype=np.uint8)
    panel[:] = (40, 40, 40)  # Dark gray
    
    # Blend panel at bottom
    overlay[-panel_height:] = cv2.addWeighted(
        overlay[-panel_height:], 0.3, panel, 0.7, 0
    )
    
    # Draw coarse prediction (main result)
    top_coarse = result.get("top_coarse", {})
    coarse_label = top_coarse.get("label", "unknown")
    coarse_prob = top_coarse.get("probability", 0.0)
    
    text = f"Room Type: {coarse_label.upper()}"
    cv2.putText(overlay, text, (15, h - panel_height + 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
    
    conf_text = f"Confidence: {coarse_prob:.1%}"
    cv2.putText(overlay, conf_text, (15, h - panel_height + 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 1)
    
    # Draw fine-grained top-5
    cv2.putText(overlay, "Fine-grained predictions:", (15, h - panel_height + 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
    
    fine_preds = result.get("room_type_fine", [])[:5]
    y_offset = h - panel_height + 110
    for i, (label, prob) in enumerate(fine_preds):
        text = f"{i+1}. {label}: {prob:.1%}"
        cv2.putText(overlay, text, (25, y_offset + i * 18),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
    
    # Draw coarse distribution bar chart on the right
    coarse_probs = result.get("room_type_coarse", {})
    sorted_coarse = sorted(coarse_probs.items(), key=lambda x: x[1], reverse=True)[:6]
    
    bar_x = w - 250
    bar_y = h - panel_height + 25
    bar_width = 200
    bar_height = 15
    
    cv2.putText(overlay, "Coarse distribution:", (bar_x, bar_y - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (150, 150, 150), 1)
    
    for i, (cat, prob) in enumerate(sorted_coarse):
        y = bar_y + 10 + i * 22
        # Draw bar background
        cv2.rectangle(overlay, (bar_x, y), (bar_x + bar_width, y + bar_height),
                      (60, 60, 60), -1)
        # Draw bar fill
        fill_width = int(bar_width * prob)
        color = (100, 200, 100) if i == 0 else (100, 150, 200)
        cv2.rectangle(overlay, (bar_x, y), (bar_x + fill_width, y + bar_height),
                      color, -1)
        # Draw label
        cv2.putText(overlay, f"{cat[:10]}: {prob:.0%}", (bar_x + 5, y + 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)

    ok, buf = cv2.imencode(".png", overlay)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to encode room detection overlay as PNG.",
        )

    return buf.tobytes()


@router.get("/images/{image_id}/room", summary="Return room type detection overlay for an image")
def get_image_room_detection(
    image_id: int,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tagger),
) -> Response:
    """Serve a PNG room type detection overlay for the requested image.

    This endpoint uses Places365 classifier to identify the room type,
    then displays the results overlaid on the original image.

    The overlay includes:
    - Primary coarse room type (bathroom, bedroom, kitchen, etc.)
    - Confidence score
    - Top-5 fine-grained Places365 predictions
    - Coarse category distribution bar chart

    Supports both local file paths and remote URLs.
    """
    image: Optional[Image] = db.query(Image).filter(Image.id == image_id).first()
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")

    storage_path = getattr(image, "storage_path", None)
    if not storage_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image has no storage_path configured",
        )

    data = _compute_room_detection_overlay_bytes(storage_path)
    return Response(content=data, media_type="image/png")


@router.get("/pipeline_health")
def pipeline_health() -> dict:
    """Return a lightweight view of the science pipeline health.

    This avoids hitting the database and instead instantiates the
    configured analyzers directly, grouping them by tier and
    reporting their requires/provides contracts.
    """
    summary: dict = {
        "import_ok": True,
        "cv2_available": getattr(science_pipeline, "cv2", None) is not None,
        "analyzers_by_tier": {},
        "warnings": [],
    }

    analyzer_class_names = [
        "ColorAnalyzer",
        "ComplexityAnalyzer",
        "TextureAnalyzer",
        "FractalAnalyzer",
        "SymmetryAnalyzer",
        "NaturalnessAnalyzer",
        "DepthAnalyzer",
        "CognitiveStateAnalyzer",
        "SegmentationAnalyzer",
        "RoomDetectionAnalyzer",
    ]

    analyzer_classes = []
    for name in analyzer_class_names:
        cls = getattr(science_pipeline, name, None)
        if cls is None:
            summary["warnings"].append(f"Analyzer class {name} missing from pipeline module.")
            continue
        analyzer_classes.append(cls)

    for cls in analyzer_classes:
        try:
            inst = cls()
        except Exception as exc:  # pragma: no cover - defensive
            summary.setdefault("analyzer_errors", []).append(
                {"analyzer": cls.__name__, "error": repr(exc)}
            )
            continue
        tier = getattr(inst, "tier", "unknown")
        requires = list(getattr(inst, "requires", []))
        provides = list(getattr(inst, "provides", []))
        entry = {
            "name": getattr(inst, "name", cls.__name__),
            "tier": tier,
            "requires": requires,
            "provides": provides,
        }
        summary["analyzers_by_tier"].setdefault(tier, []).append(entry)

    return summary
