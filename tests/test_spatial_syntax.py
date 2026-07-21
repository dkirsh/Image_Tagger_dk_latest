"""
Unit tests for cnfa_algs.spatial_syntax on synthetic grids.

Tests verify:
  1. BEV grid construction from synthetic depth/planes
  2. VGA connectivity/integration on known geometries
  3. Agent simulation produces non-zero occupancy
  4. Rendering styles produce correct-sized outputs
  5. Attribute computation returns proper schema
"""
import numpy as np
import cv2
import pytest

from cnfa_algs.spatial_syntax import (
    floor_to_bev,
    compute_vga,
    simulate_agents,
    render_occupancy,
    compute_spatial_syntax_attributes,
    BEVGrid,
    _bresenham_clear,
)
from cnfa_algs.geometry import FLOOR, WALL, CEILING


# ── Fixtures ──────────────────────────────────────────────────────────

def _make_synthetic_scene(H: int = 240, W: int = 320):
    """Create a synthetic depth map and plane segmentation.

    Layout: floor in the bottom 60%, walls on sides and top,
    ceiling in the top 20%.
    """
    planes = np.full((H, W), WALL, dtype=np.int32)
    planes[int(H * 0.2):int(H * 0.4), :] = CEILING
    planes[int(H * 0.4):, :] = FLOOR

    # Synthetic depth: linear gradient (closer at bottom, farther at top)
    Z = np.full((H, W), 5.0, dtype=np.float32)
    for r in range(H):
        Z[r, :] = 1.0 + 8.0 * (1.0 - r / H)  # ~1m close, ~9m far

    img = np.random.randint(60, 200, (H, W, 3), dtype=np.uint8)
    return img, planes, Z


# ── Component 1: BEV Grid ────────────────────────────────────────────

class TestFloorToBEV:

    def test_basic_construction(self):
        _, planes, Z = _make_synthetic_scene()
        bev = floor_to_bev(planes, Z)
        assert isinstance(bev, BEVGrid)
        assert bev.grid.ndim == 2
        assert bev.grid.dtype == bool
        assert bev.grid.sum() > 10, "Should have significant walkable area"

    def test_no_floor(self):
        """When there's no floor, grid should be nearly empty."""
        H, W = 120, 160
        planes = np.full((H, W), WALL, dtype=np.int32)
        Z = np.ones((H, W), dtype=np.float32) * 3.0
        bev = floor_to_bev(planes, Z)
        assert bev.grid.sum() < 10

    def test_grid_resolution(self):
        _, planes, Z = _make_synthetic_scene()
        bev_fine = floor_to_bev(planes, Z, grid_res=0.1)
        bev_coarse = floor_to_bev(planes, Z, grid_res=0.5)
        # Finer grid should be larger
        assert bev_fine.grid.size >= bev_coarse.grid.size


# ── Component 2: VGA ─────────────────────────────────────────────────

class TestBresenham:

    def test_clear_line(self):
        grid = np.ones((10, 10), dtype=bool)
        assert _bresenham_clear(grid, 0, 0, 9, 9) is True

    def test_blocked_line(self):
        grid = np.ones((10, 10), dtype=bool)
        grid[5, 5] = False  # obstacle in the middle
        assert _bresenham_clear(grid, 0, 0, 9, 9) is False

    def test_adjacent_cells(self):
        grid = np.ones((5, 5), dtype=bool)
        assert _bresenham_clear(grid, 2, 2, 2, 3) is True


class TestVGA:

    def test_open_grid(self):
        """Open grid should have uniform high connectivity."""
        grid = np.ones((10, 10), dtype=bool)
        conn, integ, ctrl = compute_vga(grid, max_nodes=100)
        assert conn.shape == (10, 10)
        assert conn[5, 5] > 0
        assert integ[5, 5] > 0
        # All cells should be roughly equally connected
        free_conn = conn[grid]
        cv = free_conn.std() / (free_conn.mean() + 1e-9)
        assert cv < 0.5, "Open grid should have low connectivity variance"

    def test_corridor(self):
        """Narrow corridor: centre should have higher integration than ends."""
        grid = np.zeros((3, 20), dtype=bool)
        grid[1, :] = True  # single-cell-wide corridor
        conn, integ, ctrl = compute_vga(grid, max_nodes=20)
        # Centre cell should be more integrated than endpoints
        assert integ[1, 10] >= integ[1, 0]

    def test_empty_grid(self):
        """Empty grid should return all zeros."""
        grid = np.zeros((5, 5), dtype=bool)
        conn, integ, ctrl = compute_vga(grid)
        assert conn.sum() == 0
        assert integ.sum() == 0


# ── Component 3: Agent Simulation ─────────────────────────────────────

class TestAgentSimulation:

    def test_basic_sim(self):
        grid = np.ones((10, 10), dtype=bool)
        _, integ, _ = compute_vga(grid, max_nodes=100)
        occ, traces = simulate_agents(grid, integ, n_agents=10, n_steps=50)
        assert occ.shape == (10, 10)
        assert occ.max() > 0, "At least some cells visited"
        assert len(traces) == 10
        for t in traces:
            assert t.shape[1] == 2  # (row, col) per step

    def test_deterministic(self):
        grid = np.ones((8, 8), dtype=bool)
        _, integ, _ = compute_vga(grid, max_nodes=64)
        occ1, _ = simulate_agents(grid, integ, seed=42)
        occ2, _ = simulate_agents(grid, integ, seed=42)
        np.testing.assert_array_equal(occ1, occ2)


# ── Component 4: Rendering ───────────────────────────────────────────

class TestRendering:

    def test_render_styles(self):
        img, planes, Z = _make_synthetic_scene()
        bev = floor_to_bev(planes, Z)
        _, integ, _ = compute_vga(bev.grid)
        occ, _ = simulate_agents(bev.grid, integ, n_agents=10, n_steps=50)

        for style in ("heatmap", "dots", "silhouettes"):
            out = render_occupancy(img, bev, occ, style=style)
            assert out.shape == img.shape, f"{style} output shape mismatch"
            assert out.dtype == np.uint8


# ── Component 5: Full Pipeline ────────────────────────────────────────

class TestFullPipeline:

    def test_attribute_schema(self):
        img, planes, Z = _make_synthetic_scene()
        results = compute_spatial_syntax_attributes(img, planes, Z)

        expected_keys = {
            "cnfa.social.predicted_occupancy",
            "cnfa.social.movement_traces",
            "cnfa.social.clustering_hotspots",
        }
        assert set(results.keys()) == expected_keys

        for key, attr in results.items():
            assert attr.key == key
            assert 0.0 <= attr.confidence <= 1.0
            assert isinstance(attr.method, str) and len(attr.method) > 0
            assert isinstance(attr.failure_modes, list)
            if attr.scalar is not None:
                assert 0.0 <= attr.scalar <= 1.0

    def test_insufficient_floor(self):
        """With no floor, all attributes should have low confidence."""
        H, W = 120, 160
        planes = np.full((H, W), WALL, dtype=np.int32)
        Z = np.ones((H, W), dtype=np.float32) * 3.0
        img = np.zeros((H, W, 3), dtype=np.uint8)
        results = compute_spatial_syntax_attributes(img, planes, Z)

        for attr in results.values():
            assert attr.confidence <= 0.1

    def test_render_style_parameter(self):
        """Render style should be passable to the full pipeline."""
        img, planes, Z = _make_synthetic_scene()
        for style in ("heatmap", "dots", "silhouettes"):
            results = compute_spatial_syntax_attributes(
                img, planes, Z, render_style=style
            )
            overlay = results["cnfa.social.predicted_occupancy"].extras.get("overlay")
            if overlay is not None:
                assert overlay.shape == img.shape
            assert results["cnfa.social.predicted_occupancy"].extras.get("render_style") == style
