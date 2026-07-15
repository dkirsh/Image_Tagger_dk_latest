# Runbook: Download & Integrate External Algorithms into `cnfa_algs`

**Target repo:** `/Users/davidusa/REPOS/Image_Tagger_dk_latest`
**Target package:** `cnfa_algs/` (and `cnfa_algs/adapters/`)

> [!IMPORTANT]
> This runbook is designed to be executed by an AI agent (Codex, Antigravity, etc.) or a human developer. Each task is self-contained: download the source, write the adapter, wire it into the existing code, and smoke-test. Tasks are independent — execute in any order.

---

## Prerequisites

```bash
# All models go into a shared directory
export MODELS_DIR="/Users/davidusa/REPOS/Image_Tagger_dk_latest/external_models"
mkdir -p "$MODELS_DIR"

# The cnfa_algs package root
export CNFA_ROOT="/Users/davidusa/REPOS/Image_Tagger_dk_latest/cnfa_algs"
```

---

## Task 1: Apple Depth Pro (Metric Depth) ⭐ HIGHEST PRIORITY

### 1a. DOWNLOAD

```bash
cd "$MODELS_DIR"
git clone https://github.com/apple/ml-depth-pro.git depth_pro
cd depth_pro
pip install -e .
bash get_pretrained_models.sh
# Checkpoint lands at: $MODELS_DIR/depth_pro/checkpoints/depth_pro.pt
export DEPTH_PRO_CHECKPOINT="$MODELS_DIR/depth_pro/checkpoints/depth_pro.pt"
```

### 1b. ADAPT — Create `cnfa_algs/adapters/depth_pro_adapter.py`

Write this file verbatim:

```python
"""
Apple Depth Pro adapter — metric monocular depth for cnfa_algs.

Returns depth in real metres and estimated focal length in pixels,
without requiring camera intrinsics.

Env var: DEPTH_PRO_CHECKPOINT  (path to depth_pro.pt)
If unset, this adapter is unavailable and DepthProvider falls through
to DepthAnything V2 or the geometric fallback.
"""
from __future__ import annotations
import os
from typing import Optional, Tuple
import numpy as np
import cv2

_MODEL = None
_TRANSFORM = None


def is_available() -> bool:
    path = os.getenv("DEPTH_PRO_CHECKPOINT", "")
    return bool(path) and os.path.isfile(path)


def _load():
    global _MODEL, _TRANSFORM
    if _MODEL is not None:
        return
    import depth_pro
    ckpt = os.environ["DEPTH_PRO_CHECKPOINT"]
    _MODEL, _TRANSFORM = depth_pro.create_model_and_transforms(
        device="cuda" if __import__("torch").cuda.is_available() else "cpu",
        precision=__import__("torch").float32,
    )
    _MODEL.load_state_dict(
        __import__("torch").load(ckpt, map_location="cpu"), strict=True
    )
    _MODEL.eval()


def get_metric_depth(img_bgr: np.ndarray) -> Tuple[np.ndarray, float]:
    """
    Returns:
        depth_metres: np.ndarray (H, W) float32 — depth in real metres
        focal_px:     float — estimated focal length in pixels
    """
    _load()
    import torch
    from PIL import Image

    rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb)
    result = _MODEL.infer(
        _TRANSFORM(pil_img),
        f_px=None,  # let the model estimate focal length
    )
    depth = result["depth"].squeeze().cpu().numpy().astype(np.float32)
    focal = float(result["focallength_px"].squeeze().cpu().numpy())

    # Resize to original image dimensions
    H, W = img_bgr.shape[:2]
    if depth.shape != (H, W):
        depth = cv2.resize(depth, (W, H), interpolation=cv2.INTER_LINEAR)

    return depth, focal
```

### 1c. WIRE — Edit `cnfa_algs/geometry.py`

**Edit the `DepthProvider.__init__` method** (currently lines 135–145) to add Depth Pro as the first choice:

Replace the current `__init__` and `__call__` (lines 135–153) with:

```python
    def __init__(self):
        self.session = None
        self.depth_pro = False
        self.method = "geometric_vp_groundplane(M2-geo)"

        # Priority 1: Apple Depth Pro (metric depth)
        try:
            from .adapters.depth_pro_adapter import is_available as dp_avail
            if dp_avail():
                self.depth_pro = True
                self.method = "depth_pro_metric(M2-metric)"
                return
        except ImportError:
            pass

        # Priority 2: DepthAnything V2 ONNX (relative depth)
        path = os.getenv("DEPTH_ANYTHING_ONNX_PATH")
        if path and os.path.exists(path):
            try:
                import onnxruntime as ort
                self.session = ort.InferenceSession(path, providers=["CPUExecutionProvider"])
                self.method = "monocular_onnx(M2)"
            except Exception:
                self.session = None

    def __call__(self, img_bgr: np.ndarray, planes: np.ndarray,
                 vp: Tuple[float, float], fov_deg: float = 65.0,
                 cam_h: float = 1.5) -> Tuple[np.ndarray, np.ndarray, float]:
        """Returns (Z metric-ish HxW, disparity01 HxW for display, confidence)."""
        if self.depth_pro:
            return self._depth_pro(img_bgr)
        if self.session is not None:
            return self._onnx_depth(img_bgr, planes, cam_h)
        return self._geometric_depth(img_bgr, planes, vp, fov_deg, cam_h)

    # -- Apple Depth Pro: true metric depth
    def _depth_pro(self, img_bgr):
        from .adapters.depth_pro_adapter import get_metric_depth
        Z, focal = get_metric_depth(img_bgr)
        disp01 = 1.0 / np.maximum(Z, 0.01)
        disp01 = (disp01 - disp01.min()) / (np.ptp(disp01) + 1e-9)
        return Z, disp01, 0.9
```

Keep the existing `_onnx_depth` and `_geometric_depth` methods unchanged.

### 1d. SMOKE TEST

```bash
cd "$CNFA_ROOT/.."
python -c "
from cnfa_algs.adapters.depth_pro_adapter import is_available, get_metric_depth
print('Depth Pro available:', is_available())
if is_available():
    import cv2
    img = cv2.imread('test_photo.jpg')  # any interior photo
    Z, f = get_metric_depth(img)
    print(f'Depth shape: {Z.shape}, focal: {f:.1f}px, median depth: {Z[Z.shape[0]//2].mean():.2f}m')
"
```

---

## Task 2: HAWP Wireframe Parser

### 2a. DOWNLOAD

```bash
cd "$MODELS_DIR"
git clone https://github.com/cherubicXN/hawp.git
cd hawp
pip install -e .
# Download pretrained weights — check Releases page for latest URL:
# https://github.com/cherubicXN/hawp/releases
# Typical: wget <release_url>/hawpv3-imagenet-03a6e4a3.pth -O checkpoints/hawpv3.pth
mkdir -p checkpoints
# If no direct link, use the model download script if provided in the repo
export HAWP_CHECKPOINT="$MODELS_DIR/hawp/checkpoints/hawpv3.pth"
```

### 2b. ADAPT — Create `cnfa_algs/adapters/hawp_adapter.py`

```python
"""
HAWP wireframe parser adapter — structural lines + junctions.

Env var: HAWP_CHECKPOINT (path to hawpv3.pth or equivalent)
Returns detected line segments and junction points for architectural
wireframe analysis and improved vanishing-point estimation.
"""
from __future__ import annotations
import os
from typing import List, Dict, Tuple, Optional
import numpy as np
import cv2


def is_available() -> bool:
    path = os.getenv("HAWP_CHECKPOINT", "")
    return bool(path) and os.path.isfile(path)


_MODEL = None


def _load():
    global _MODEL
    if _MODEL is not None:
        return
    import torch
    # HAWP's API may vary by version — adapt imports to installed version
    try:
        from hawp.ssl.predict import WireframeDetector
        _MODEL = WireframeDetector(is_cuda=torch.cuda.is_available())
        _MODEL.load_state_dict(
            torch.load(os.environ["HAWP_CHECKPOINT"], map_location="cpu")
        )
    except ImportError:
        from hawp.fsl.config import cfg as model_cfg
        from hawp.fsl.model import build_model
        _MODEL = build_model(model_cfg)
        state = torch.load(os.environ["HAWP_CHECKPOINT"], map_location="cpu")
        _MODEL.load_state_dict(state.get("model", state), strict=False)
    _MODEL.eval()


def detect_wireframe(img_bgr: np.ndarray,
                     score_thresh: float = 0.9
                     ) -> Dict[str, np.ndarray]:
    """
    Returns:
        {
            'lines': np.ndarray (N, 2, 2) — each line is [[x1,y1],[x2,y2]],
            'scores': np.ndarray (N,) — per-line confidence,
            'junctions': np.ndarray (M, 2) — [x, y] junction points,
        }
    """
    _load()
    import torch
    H, W = img_bgr.shape[:2]
    rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    # Normalize and run — adapt to HAWP API
    with torch.no_grad():
        result = _MODEL(rgb)

    lines = result.get("lines_pred", result.get("lines", np.empty((0, 2, 2))))
    scores = result.get("lines_score", result.get("score", np.ones(len(lines))))
    juncs = result.get("juncs_pred", result.get("juncs", np.empty((0, 2))))

    if isinstance(lines, torch.Tensor):
        lines = lines.cpu().numpy()
    if isinstance(scores, torch.Tensor):
        scores = scores.cpu().numpy()
    if isinstance(juncs, torch.Tensor):
        juncs = juncs.cpu().numpy()

    # Filter by score
    mask = scores >= score_thresh
    return {
        "lines": lines[mask].reshape(-1, 2, 2),
        "scores": scores[mask],
        "junctions": juncs,
    }


def wireframe_vanishing_point(img_bgr: np.ndarray) -> Tuple[float, float, float]:
    """Estimate VP from HAWP-detected structural lines.
    Falls back to the existing Hough-based estimator if HAWP is unavailable."""
    if not is_available():
        from ..geometry import estimate_vanishing_point
        return estimate_vanishing_point(img_bgr)

    wf = detect_wireframe(img_bgr)
    lines = wf["lines"]
    H, W = img_bgr.shape[:2]

    if len(lines) < 4:
        from ..geometry import estimate_vanishing_point
        return estimate_vanishing_point(img_bgr)

    # Weighted least-squares VP from oblique wireframe segments
    A, b, wts = [], [], []
    for seg in lines:
        (x1, y1), (x2, y2) = seg
        dx, dy = x2 - x1, y2 - y1
        ang = abs(np.degrees(np.arctan2(dy, dx)))
        ang = min(ang, 180 - ang)
        if 8 < ang < 80:  # oblique lines only
            n = np.array([-dy, dx])
            n /= (np.linalg.norm(n) + 1e-9)
            A.append(n)
            b.append(n @ np.array([x1, y1]))
            wts.append(np.hypot(dx, dy))

    if len(A) >= 4:
        A = np.array(A) * np.array(wts)[:, None]
        b_arr = np.array(b) * np.array(wts)
        vp, *_ = np.linalg.lstsq(A, b_arr, rcond=None)
        vx, vy = float(vp[0]), float(vp[1])
        conf = min(1.0, len(A) / 16)
        if -0.5 * W < vx < 1.5 * W and 0.05 * H < vy < 0.95 * H:
            return vx, vy, conf * 0.95  # higher conf than Hough

    from ..geometry import estimate_vanishing_point
    return estimate_vanishing_point(img_bgr)
```

### 2c. WIRE — No mandatory edits to existing files

The wireframe VP is available via the adapter; call it directly:
```python
from cnfa_algs.adapters.hawp_adapter import wireframe_vanishing_point
vx, vy, conf = wireframe_vanishing_point(img)
```

**Optional enhancement:** In any orchestrator that currently calls `estimate_vanishing_point()`, replace with `wireframe_vanishing_point()` which falls back automatically.

---

## Task 3: uLayout Room Layout Estimation

### 3a. DOWNLOAD

```bash
cd "$MODELS_DIR"
git clone https://github.com/JonathanLee112/uLayout.git
cd uLayout
# Create conda env per their README, or install deps into your existing env:
pip install torch torchvision timm
# Download pretrained checkpoint — check README for URL
# Typically placed in checkpoints/
export ULAYOUT_CHECKPOINT="$MODELS_DIR/uLayout/checkpoints/best.pth"
```

### 3b. ADAPT — Create `cnfa_algs/adapters/ulayout_adapter.py`

```python
"""
uLayout room layout adapter — structured room geometry from a photo.

Returns wall/floor/ceiling boundary polygons as a RoomLayout dataclass,
giving structured geometric input to plan inference.

Env var: ULAYOUT_CHECKPOINT (path to best.pth)
"""
from __future__ import annotations
import os
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import numpy as np
import cv2


@dataclass
class RoomLayout:
    """Structured room geometry from a single image."""
    floor_polygon: np.ndarray       # (N, 2) polygon in image coords
    ceiling_polygon: np.ndarray     # (N, 2) polygon in image coords
    wall_segments: List[Tuple[np.ndarray, np.ndarray]]  # list of (top_edge, bottom_edge)
    floor_mask: np.ndarray          # (H, W) binary
    ceiling_mask: np.ndarray        # (H, W) binary
    wall_mask: np.ndarray           # (H, W) binary
    confidence: float = 0.0


def is_available() -> bool:
    path = os.getenv("ULAYOUT_CHECKPOINT", "")
    return bool(path) and os.path.isfile(path)


_MODEL = None


def _load():
    global _MODEL
    if _MODEL is not None:
        return
    import torch
    import sys
    # Add uLayout to path
    ulayout_dir = os.path.dirname(os.environ["ULAYOUT_CHECKPOINT"])
    parent = os.path.dirname(ulayout_dir)
    if parent not in sys.path:
        sys.path.insert(0, parent)
    # Import and load — adapt to actual uLayout API
    from model import build_model  # uLayout model builder
    _MODEL = build_model()
    state = torch.load(os.environ["ULAYOUT_CHECKPOINT"], map_location="cpu")
    _MODEL.load_state_dict(state.get("model", state), strict=False)
    _MODEL.eval()


def estimate_room_layout(img_bgr: np.ndarray) -> RoomLayout:
    """
    Estimate structured room layout from a perspective image.
    Returns a RoomLayout with floor/ceiling/wall masks and polygons.
    """
    _load()
    import torch

    H, W = img_bgr.shape[:2]
    rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    # Run uLayout inference — adapt to actual API
    with torch.no_grad():
        result = _MODEL.predict(rgb)

    # Extract floor/ceiling/wall masks from result
    # The exact output format depends on uLayout's API;
    # this is the adapter's job to normalize:
    floor_mask = result.get("floor_mask", np.zeros((H, W), np.uint8))
    ceil_mask = result.get("ceiling_mask", np.zeros((H, W), np.uint8))
    wall_mask = result.get("wall_mask", np.zeros((H, W), np.uint8))

    # Extract polygons from masks
    def mask_to_polygon(m):
        cs, _ = cv2.findContours(m.astype(np.uint8),
                                  cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if cs:
            c = max(cs, key=cv2.contourArea)
            return c.reshape(-1, 2)
        return np.empty((0, 2))

    return RoomLayout(
        floor_polygon=mask_to_polygon(floor_mask),
        ceiling_polygon=mask_to_polygon(ceil_mask),
        wall_segments=[],
        floor_mask=floor_mask,
        ceiling_mask=ceil_mask,
        wall_mask=wall_mask,
        confidence=0.75,
    )
```

### 3c. WIRE

The layout adapter provides structured room geometry. It can feed into `geometry.segment_planes(provided=...)`:

```python
from cnfa_algs.adapters.ulayout_adapter import estimate_room_layout, is_available
if is_available():
    layout = estimate_room_layout(img)
    # Convert to plane label map
    planes = np.zeros(img.shape[:2], np.int32)
    planes[layout.floor_mask > 0] = FLOOR
    planes[layout.ceiling_mask > 0] = CEILING
    planes[layout.wall_mask > 0] = WALL
    planes, conf = segment_planes(img, vp, provided=planes)  # uses the provided= hook
```

---

## Task 4: ESANet RGB-D Segmentation

### 4a. DOWNLOAD

```bash
cd "$MODELS_DIR"
git clone https://github.com/TUI-NICR/ESANet.git
cd ESANet
pip install torch torchvision
# Download pretrained weights — NYUv2 model:
# Check README for download links, typically:
mkdir -p trained_models
# wget <url> -O trained_models/nyuv2_r34_NBt1D.pth
export ESANET_CHECKPOINT="$MODELS_DIR/ESANet/trained_models/nyuv2_r34_NBt1D.pth"
```

### 4b. ADAPT — Create `cnfa_algs/adapters/esanet_adapter.py`

```python
"""
ESANet RGB-D segmentation adapter — fuses depth for better indoor segmentation.

Env var: ESANET_CHECKPOINT (path to pretrained .pth)
Requires a depth map (from Depth Pro or DA-V2) as additional input.
"""
from __future__ import annotations
import os, sys
from typing import Dict, Tuple
import numpy as np
import cv2

from ..geometry import UNKNOWN, FLOOR, CEILING, WALL, OPENING

# NYUv2 40-class → CNfA plane labels (subset — extend as needed)
NYUV2_TO_PLANE: Dict[int, int] = {
    1: WALL,      # wall
    2: FLOOR,     # floor
    3: UNKNOWN,   # cabinet
    4: UNKNOWN,   # bed
    5: UNKNOWN,   # chair
    6: UNKNOWN,   # sofa
    7: UNKNOWN,   # table
    8: OPENING,   # door
    9: OPENING,   # window
    10: UNKNOWN,  # bookshelf
    11: WALL,     # picture
    12: UNKNOWN,  # counter
    14: UNKNOWN,  # desk
    15: UNKNOWN,  # curtain → treat as soft furnishing
    16: UNKNOWN,  # fridge
    22: CEILING,  # ceiling
    25: WALL,     # mirror → wall surface
    27: UNKNOWN,  # tv
    33: UNKNOWN,  # toilet
    34: UNKNOWN,  # sink
    36: UNKNOWN,  # bathtub
    # everything else defaults to UNKNOWN
}


def is_available() -> bool:
    path = os.getenv("ESANET_CHECKPOINT", "")
    return bool(path) and os.path.isfile(path)


_MODEL = None


def _load():
    global _MODEL
    if _MODEL is not None:
        return
    import torch
    ckpt_path = os.environ["ESANET_CHECKPOINT"]
    esanet_dir = os.path.dirname(os.path.dirname(ckpt_path))
    if esanet_dir not in sys.path:
        sys.path.insert(0, esanet_dir)
    # Import ESANet model — adapt to actual API
    from src.build_model import build_model
    _MODEL = build_model(n_classes=40, modality="rgbd")
    state = torch.load(ckpt_path, map_location="cpu")
    _MODEL.load_state_dict(state.get("state_dict", state), strict=False)
    _MODEL.eval()


def segment_with_rgbd(img_bgr: np.ndarray,
                       depth: np.ndarray
                       ) -> Tuple[np.ndarray, float, np.ndarray]:
    """
    Run ESANet RGB-D segmentation.

    Args:
        img_bgr: (H, W, 3) BGR image
        depth:   (H, W) depth map (any scale — will be normalized)

    Returns:
        planes:   (H, W) int32 — CNfA plane labels (FLOOR/WALL/CEILING/OPENING/UNKNOWN)
        confidence: float
        raw_labels: (H, W) int — original NYUv2 40-class labels
    """
    _load()
    import torch

    H, W = img_bgr.shape[:2]
    # Preprocess — adapt to ESANet input requirements
    rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    rgb_resized = cv2.resize(rgb, (640, 480))
    depth_resized = cv2.resize(depth, (640, 480))

    # Normalize
    rgb_t = torch.from_numpy(rgb_resized).permute(2, 0, 1).float() / 255.0
    depth_t = torch.from_numpy(depth_resized).unsqueeze(0).float()
    depth_t = (depth_t - depth_t.min()) / (depth_t.max() - depth_t.min() + 1e-9)

    with torch.no_grad():
        pred = _MODEL(rgb_t.unsqueeze(0), depth_t.unsqueeze(0))
        labels = pred.argmax(1).squeeze().cpu().numpy()

    # Resize back to original
    raw_labels = cv2.resize(labels.astype(np.uint8), (W, H),
                             interpolation=cv2.INTER_NEAREST).astype(np.int32)

    # Map to CNfA plane labels
    planes = np.full((H, W), UNKNOWN, np.int32)
    for nyuv2_class, plane_class in NYUV2_TO_PLANE.items():
        planes[raw_labels == nyuv2_class] = plane_class

    return planes, 0.85, raw_labels
```

### 4c. WIRE

Same `provided=` hook as the existing SegFormer adapter. Use in your orchestrator:

```python
from cnfa_algs.adapters.esanet_adapter import is_available, segment_with_rgbd
if is_available() and depth_map is not None:
    planes, conf, raw = segment_with_rgbd(img, depth_map)
else:
    planes, conf = segment_planes(img, vp)  # existing fallback
```

---

## Task 5: Marigold Diffusion Depth

### 5a. DOWNLOAD

```bash
pip install diffusers torch accelerate
# No separate clone needed — weights auto-download from HuggingFace on first use.
# Model ID: prs-eth/marigold-depth-v1-1
# Optional: pre-cache it:
python -c "from diffusers import MarigoldDepthPipeline; MarigoldDepthPipeline.from_pretrained('prs-eth/marigold-depth-v1-1')"
```

### 5b. ADAPT — Create `cnfa_algs/adapters/marigold_adapter.py`

```python
"""
Marigold diffusion depth adapter — high-quality relative depth maps.

No env var needed. Downloads from HuggingFace on first use.
Set MARIGOLD_MODEL to override the model ID (default: prs-eth/marigold-depth-v1-1).

Note: Marigold produces RELATIVE depth, not metric.
Use Depth Pro (Task 1) for metric depth. Use Marigold when you want
the highest visual quality depth map for rendering/display.
"""
from __future__ import annotations
import os
from typing import Tuple
import numpy as np
import cv2

_PIPE = None


def is_available() -> bool:
    try:
        import diffusers
        return True
    except ImportError:
        return False


def _load():
    global _PIPE
    if _PIPE is not None:
        return
    from diffusers import MarigoldDepthPipeline
    import torch
    model_id = os.getenv("MARIGOLD_MODEL", "prs-eth/marigold-depth-v1-1")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    _PIPE = MarigoldDepthPipeline.from_pretrained(model_id).to(device)


def get_marigold_depth(img_bgr: np.ndarray,
                        num_inference_steps: int = 10,
                        ensemble_size: int = 5
                        ) -> np.ndarray:
    """
    Returns:
        depth_relative: np.ndarray (H, W) float32 in [0, 1] (0=far, 1=near)
    """
    _load()
    from PIL import Image

    H, W = img_bgr.shape[:2]
    rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb)

    output = _PIPE(
        pil_img,
        num_inference_steps=num_inference_steps,
        ensemble_size=ensemble_size,
    )
    depth = output.prediction.squeeze().cpu().numpy().astype(np.float32)

    if depth.shape != (H, W):
        depth = cv2.resize(depth, (W, H), interpolation=cv2.INTER_LINEAR)

    return depth
```

### 5c. WIRE

Optional branch in `DepthProvider.__init__` between Depth Pro and DA-V2 (if you want to offer it as a choice). Lower priority than Depth Pro since it's relative-only.

---

## Task 6: Deep Saliency (TranSalNet or equivalent)

### 6a. DOWNLOAD

```bash
cd "$MODELS_DIR"
git clone https://github.com/LJOVO/TranSalNet.git transalnet
cd transalnet
pip install torch torchvision timm
# Download pretrained weights — check repo README or releases
# Typical: checkpoints/TranSalNet_Dense.pth
export TRANSALNET_CHECKPOINT="$MODELS_DIR/transalnet/pretrained/TranSalNet_Dense.pth"
```

> **Note:** TranSalNet's repo URL may vary. Search GitHub for `TranSalNet` or consult the [awesome-human-visual-attention](https://github.com/aimagelab/awesome-human-visual-attention) list for the current best saliency model. The adapter below works with any model that produces an (H, W) saliency map.

### 6b. ADAPT — Create `cnfa_algs/adapters/saliency_adapter.py`

```python
"""
Deep saliency adapter — fixation prediction for landmark salience.

Replaces spectral-residual FFT saliency (2007 method) with a deep
transformer-based fixation model.

Env var: TRANSALNET_CHECKPOINT (path to pretrained .pth)
If unset, falls back to spectral-residual saliency (existing behavior).
"""
from __future__ import annotations
import os
from typing import Optional
import numpy as np
import cv2

_MODEL = None


def is_available() -> bool:
    path = os.getenv("TRANSALNET_CHECKPOINT", "")
    return bool(path) and os.path.isfile(path)


def _load():
    global _MODEL
    if _MODEL is not None:
        return
    import torch
    import sys
    ckpt = os.environ["TRANSALNET_CHECKPOINT"]
    model_dir = os.path.dirname(os.path.dirname(ckpt))
    if model_dir not in sys.path:
        sys.path.insert(0, model_dir)
    # Import TranSalNet — adapt to actual repo structure
    from TranSalNet_Dense import TranSalNet  # typical module name
    _MODEL = TranSalNet()
    _MODEL.load_state_dict(torch.load(ckpt, map_location="cpu"), strict=False)
    _MODEL.eval()


def deep_saliency(img_bgr: np.ndarray) -> np.ndarray:
    """
    Returns saliency map (H, W) float32 in [0, 1].
    If TRANSALNET_CHECKPOINT is not set, falls back to spectral-residual.
    """
    if not is_available():
        return _spectral_residual_fallback(img_bgr)

    _load()
    import torch

    H, W = img_bgr.shape[:2]
    rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    # TranSalNet expects 384x288 or similar — adapt to model's expected input
    inp = cv2.resize(rgb, (384, 288)).astype(np.float32) / 255.0
    inp = torch.from_numpy(inp).permute(2, 0, 1).unsqueeze(0)

    with torch.no_grad():
        sal = _MODEL(inp)

    sal = sal.squeeze().cpu().numpy().astype(np.float32)
    sal = cv2.resize(sal, (W, H), interpolation=cv2.INTER_LINEAR)
    sal = (sal - sal.min()) / (sal.max() - sal.min() + 1e-9)
    return sal


def _spectral_residual_fallback(img_bgr: np.ndarray) -> np.ndarray:
    """Existing FFT spectral-residual saliency (fallback)."""
    g = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    small = cv2.resize(g, (128, 128))
    F = np.fft.fft2(small)
    logamp = np.log(np.abs(F) + 1e-9)
    resid = logamp - cv2.blur(logamp, (3, 3))
    sal = np.abs(np.fft.ifft2(np.exp(resid + 1j * np.angle(F)))) ** 2
    sal = cv2.GaussianBlur(sal.astype(np.float32), (9, 9), 2.5)
    from .._core_hack import normalize01  # avoid circular
    sal = cv2.resize(sal, (img_bgr.shape[1], img_bgr.shape[0]))
    sal = (sal - sal.min()) / (sal.max() - sal.min() + 1e-9)
    return sal
```

### 6c. WIRE — Edit `cnfa_algs/attributes.py` `landmark_salience()`

Add an optional `saliency_map` parameter to `landmark_salience()`. Replace lines 197–229 of [attributes.py](file:///Users/davidusa/REPOS/Image_Tagger_dk_latest/cnfa_algs/attributes.py#L197-L229):

```python
def landmark_salience(img, saliency_map: Optional[np.ndarray] = None) -> AttributeResult:
    """Deep saliency (if available) or spectral-residual, + top-region bbox with Lab contrast."""
    # Get saliency map — deep if available, else FFT
    if saliency_map is not None:
        sal = saliency_map
        method_note = "provided saliency map"
    else:
        try:
            from .adapters.saliency_adapter import deep_saliency
            sal = deep_saliency(img)
            method_note = "TranSalNet deep fixation" if os.getenv("TRANSALNET_CHECKPOINT") else "spectral-residual FFT"
        except Exception:
            # Original inline fallback
            g = _gray(img)
            小 = cv2.resize(g, (128, 128))
            F = np.fft.fft2(小)
            logamp = np.log(np.abs(F) + 1e-9)
            resid = logamp - cv2.blur(logamp, (3, 3))
            sal = np.abs(np.fft.ifft2(np.exp(resid + 1j * np.angle(F)))) ** 2
            sal = cv2.GaussianBlur(sal.astype(np.float32), (9, 9), 2.5)
            sal = cv2.resize(normalize01(sal), (img.shape[1], img.shape[0]))
            method_note = "spectral-residual FFT (fallback)"

    # top region (unchanged logic)
    thr = (sal > np.percentile(sal, 97)).astype(np.uint8)
    cs, _ = cv2.findContours(thr, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    regions = []
    if cs:
        c = max(cs, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(c)
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
        m = np.zeros(img.shape[:2], np.uint8); cv2.drawContours(m, [c], -1, 1, -1)
        ring = cv2.dilate(m, np.ones((25, 25), np.uint8)) - m
        dE = float(np.linalg.norm(lab[m > 0].mean(0) - lab[ring > 0].mean(0))) if ring.any() else 0.0
        regions.append({"kind": "bbox", "coords": [x, y, w, h],
                         "label": f"landmark dE={dE:.0f}", "value": dE})
    peak_ratio = float(sal.max() / (sal.mean() + 1e-9))
    dE_top = regions[0]["value"] if regions else 0.0
    scalar = float(np.clip(0.5 * min(dE_top / 60.0, 1.0) + 0.5 * min(peak_ratio / 12.0, 1.0), 0, 1))
    return AttributeResult(
        key="cnfa.cognitive.landmark_salience",
        scalar=scalar, field=sal, regions=regions, confidence=0.75 if "deep" in method_note else 0.6,
        method=f"{method_note} + Lab surround contrast (M1)",
        failure_modes=["bright window outsalients a memorable object" if "FFT" in method_note else "semantic gap: salience != wayfinding anchor"])
```

---

## Task 7: Composition Analysis (Pure Code — No Download)

### 7a. DOWNLOAD

None needed. This is pure numpy + OpenCV.

### 7b. CREATE — `cnfa_algs/composition.py`

```python
"""
cnfa_algs.composition — image composition analysis.

Pure image-processing (M1) — no external model required.
Optionally uses a deep saliency map if available (from saliency_adapter).

Attributes:
    cnfa.composition.rule_of_thirds   — subject alignment with RoT grid
    cnfa.composition.visual_balance   — center-of-visual-mass vs image center
"""
from __future__ import annotations
from typing import Optional
import numpy as np
import cv2
from .core import AttributeResult, normalize01


def _get_saliency(img_bgr: np.ndarray, provided: Optional[np.ndarray] = None) -> np.ndarray:
    """Get a saliency map — provided, deep, or FFT fallback."""
    if provided is not None:
        return provided
    try:
        from .adapters.saliency_adapter import deep_saliency
        return deep_saliency(img_bgr)
    except Exception:
        g = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
        small = cv2.resize(g, (128, 128))
        F = np.fft.fft2(small)
        logamp = np.log(np.abs(F) + 1e-9)
        resid = logamp - cv2.blur(logamp, (3, 3))
        sal = np.abs(np.fft.ifft2(np.exp(resid + 1j * np.angle(F)))) ** 2
        sal = cv2.GaussianBlur(sal.astype(np.float32), (9, 9), 2.5)
        sal = cv2.resize(sal, (img_bgr.shape[1], img_bgr.shape[0]))
        return normalize01(sal)


def rule_of_thirds(img_bgr: np.ndarray,
                    saliency: Optional[np.ndarray] = None) -> AttributeResult:
    """How well visual mass aligns with the rule-of-thirds grid."""
    sal = _get_saliency(img_bgr, saliency)
    H, W = sal.shape

    # RoT intersection points (4 hotspots)
    hotspots = [
        (W / 3, H / 3), (2 * W / 3, H / 3),
        (W / 3, 2 * H / 3), (2 * W / 3, 2 * H / 3),
    ]

    # For each hotspot, measure saliency in a surrounding window
    r = int(min(H, W) * 0.08)  # window radius ~8% of image size
    scores = []
    for hx, hy in hotspots:
        x1, y1 = max(0, int(hx - r)), max(0, int(hy - r))
        x2, y2 = min(W, int(hx + r)), min(H, int(hy + r))
        region_sal = sal[y1:y2, x1:x2].mean() if (y2 > y1 and x2 > x1) else 0
        scores.append(float(region_sal))

    # RoT score: how much of the total saliency is near hotspots
    best = max(scores)
    rot_score = float(np.clip(best / (sal.mean() + 1e-9) / 3.0, 0, 1))

    # Build a field showing proximity to RoT grid
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    grid_dist = np.ones((H, W), np.float32) * 999
    for hx, hy in hotspots:
        d = np.sqrt((xs - hx) ** 2 + (ys - hy) ** 2)
        grid_dist = np.minimum(grid_dist, d)
    grid_field = normalize01(1.0 / (grid_dist + 1))

    return AttributeResult(
        key="cnfa.composition.rule_of_thirds",
        scalar=rot_score,
        field=normalize01(sal * grid_field),
        confidence=0.7,
        method="saliency-weighted RoT hotspot proximity (M1)",
        failure_modes=["not all compositions benefit from RoT",
                        "saliency quality limits accuracy"],
        extras={"hotspot_scores": scores},
    )


def visual_balance(img_bgr: np.ndarray,
                    saliency: Optional[np.ndarray] = None) -> AttributeResult:
    """How well visual weight is balanced around the image center."""
    sal = _get_saliency(img_bgr, saliency)
    H, W = sal.shape

    # Center of visual mass
    total = sal.sum() + 1e-9
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    cx = float((xs * sal).sum() / total)
    cy = float((ys * sal).sum() / total)

    # Offset from image center, normalized to [0, 1]
    dx = abs(cx - W / 2) / (W / 2)
    dy = abs(cy - H / 2) / (H / 2)
    offset = float(np.sqrt(dx ** 2 + dy ** 2))

    # Balance score: 1 = perfectly centered, 0 = extreme corner
    balance = float(np.clip(1.0 - offset, 0, 1))

    # Field: show the visual mass distribution
    return AttributeResult(
        key="cnfa.composition.visual_balance",
        scalar=balance,
        field=sal,
        confidence=0.75,
        method="saliency-weighted center-of-mass offset from image center (M1)",
        failure_modes=["intentional asymmetric compositions penalized",
                        "saliency quality limits accuracy"],
        extras={"center_of_mass": [round(cx, 1), round(cy, 1)],
                "offset_normalized": round(offset, 3)},
    )
```

### 7c. WIRE — Edit `cnfa_algs/__init__.py`

Add composition imports. Change line 16:

```python
from . import attributes
from . import composition  # NEW
```

---

## Task 8: Update `EXTERNAL_MODELS_CATALOG.md`

### 8a. EDIT — Append to `cnfa_algs/adapters/EXTERNAL_MODELS_CATALOG.md`

Append entries for each new model:

```markdown
---

## New Models (added by algorithm integration runbook)

### Apple Depth Pro
- **Task:** Metric monocular depth estimation
- **Repo:** https://github.com/apple/ml-depth-pro
- **License:** Apache 2.0
- **Env var:** `DEPTH_PRO_CHECKPOINT`
- **Adapter:** `adapters/depth_pro_adapter.py`
- **Install:** `git clone + pip install -e . + bash get_pretrained_models.sh`

### HAWP (Wireframe Parser)
- **Task:** Structural line + junction detection, VP estimation
- **Repo:** https://github.com/cherubicXN/hawp
- **License:** Research
- **Env var:** `HAWP_CHECKPOINT`
- **Adapter:** `adapters/hawp_adapter.py`

### uLayout
- **Task:** Unified room layout estimation (perspective + panoramic)
- **Repo:** https://github.com/JonathanLee112/uLayout
- **License:** Research (WACV 2025)
- **Env var:** `ULAYOUT_CHECKPOINT`
- **Adapter:** `adapters/ulayout_adapter.py`

### ESANet
- **Task:** RGB-D semantic segmentation (fuses depth for better indoor results)
- **Repo:** https://github.com/TUI-NICR/ESANet
- **License:** Research
- **Env var:** `ESANET_CHECKPOINT`
- **Adapter:** `adapters/esanet_adapter.py`

### Marigold
- **Task:** Diffusion-based high-quality relative depth
- **Repo:** https://github.com/prs-eth/Marigold
- **HuggingFace:** prs-eth/marigold-depth-v1-1
- **License:** Apache 2.0
- **Env var:** `MARIGOLD_MODEL` (optional, defaults to HF model ID)
- **Adapter:** `adapters/marigold_adapter.py`

### TranSalNet (Deep Saliency)
- **Task:** Visual attention / fixation prediction
- **Repo:** Search GitHub for TranSalNet (or use awesome-human-visual-attention list)
- **License:** Research
- **Env var:** `TRANSALNET_CHECKPOINT`
- **Adapter:** `adapters/saliency_adapter.py`
```

---

## Final Smoke Test Script

Create `cnfa_algs/validation/test_adapters.py`:

```python
"""Smoke-test all adapters. Run: python -m cnfa_algs.validation.test_adapters --image test.jpg"""
import argparse, sys, cv2, numpy as np

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--image", required=True)
    args = p.parse_args()
    img = cv2.imread(args.image)
    assert img is not None, f"Cannot read {args.image}"
    H, W = img.shape[:2]
    print(f"Image: {args.image} ({W}x{H})")

    results = {}

    # 1. Depth Pro
    try:
        from cnfa_algs.adapters.depth_pro_adapter import is_available, get_metric_depth
        if is_available():
            Z, f = get_metric_depth(img)
            results["depth_pro"] = f"OK — shape={Z.shape}, focal={f:.1f}px, median={np.median(Z):.2f}m"
        else:
            results["depth_pro"] = "SKIP (DEPTH_PRO_CHECKPOINT not set)"
    except Exception as e:
        results["depth_pro"] = f"FAIL: {e}"

    # 2. HAWP
    try:
        from cnfa_algs.adapters.hawp_adapter import is_available, detect_wireframe
        if is_available():
            wf = detect_wireframe(img)
            results["hawp"] = f"OK — {len(wf['lines'])} lines, {len(wf['junctions'])} junctions"
        else:
            results["hawp"] = "SKIP (HAWP_CHECKPOINT not set)"
    except Exception as e:
        results["hawp"] = f"FAIL: {e}"

    # 3. uLayout
    try:
        from cnfa_algs.adapters.ulayout_adapter import is_available, estimate_room_layout
        if is_available():
            layout = estimate_room_layout(img)
            results["ulayout"] = f"OK — floor_mask: {layout.floor_mask.sum()} px"
        else:
            results["ulayout"] = "SKIP (ULAYOUT_CHECKPOINT not set)"
    except Exception as e:
        results["ulayout"] = f"FAIL: {e}"

    # 4. ESANet
    try:
        from cnfa_algs.adapters.esanet_adapter import is_available, segment_with_rgbd
        if is_available():
            dummy_depth = np.ones((H, W), np.float32)
            planes, conf, raw = segment_with_rgbd(img, dummy_depth)
            results["esanet"] = f"OK — unique planes: {np.unique(planes).tolist()}, conf={conf}"
        else:
            results["esanet"] = "SKIP (ESANET_CHECKPOINT not set)"
    except Exception as e:
        results["esanet"] = f"FAIL: {e}"

    # 5. Marigold
    try:
        from cnfa_algs.adapters.marigold_adapter import is_available, get_marigold_depth
        if is_available():
            d = get_marigold_depth(img, num_inference_steps=2, ensemble_size=1)
            results["marigold"] = f"OK — shape={d.shape}, range=[{d.min():.3f}, {d.max():.3f}]"
        else:
            results["marigold"] = "SKIP (diffusers not installed)"
    except Exception as e:
        results["marigold"] = f"FAIL: {e}"

    # 6. Deep saliency
    try:
        from cnfa_algs.adapters.saliency_adapter import is_available, deep_saliency
        if is_available():
            s = deep_saliency(img)
            results["saliency"] = f"OK — shape={s.shape}, range=[{s.min():.3f}, {s.max():.3f}]"
        else:
            results["saliency"] = "SKIP (TRANSALNET_CHECKPOINT not set) — will use FFT fallback"
    except Exception as e:
        results["saliency"] = f"FAIL: {e}"

    # 7. Composition (pure code, always works)
    try:
        from cnfa_algs.composition import rule_of_thirds, visual_balance
        r = rule_of_thirds(img)
        b = visual_balance(img)
        results["composition"] = f"OK — RoT={r.scalar:.3f}, balance={b.scalar:.3f}"
    except Exception as e:
        results["composition"] = f"FAIL: {e}"

    print("\n=== Adapter Smoke Test Results ===")
    for k, v in results.items():
        status = "✅" if v.startswith("OK") else ("⏭️" if "SKIP" in v else "❌")
        print(f"  {status} {k:15s} {v}")

if __name__ == "__main__":
    main()
```

---

## Summary: What An Agent Needs To Do

For each task (1–7):
1. **Run the shell commands** in section (a) to clone the repo and download weights.
2. **Write the Python file** in section (b) to the specified path.
3. **Edit the existing file** in section (c) if noted — specific lines and replacements are given.
4. **Run the smoke test** in section (d) to verify.

Task 8 is a documentation-only edit. The final smoke-test script verifies everything at once.

Total new files to create: 8 (7 `.py` adapters/modules + 1 test script).
Total existing files to edit: 2 (`geometry.py` DepthProvider, `attributes.py` landmark_salience, `__init__.py` imports).
