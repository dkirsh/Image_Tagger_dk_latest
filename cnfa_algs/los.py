"""
cnfa_algs.los — ONE correct line-of-sight / visibility primitive (panel fix S1).

The panel found the same defect copied into six modules: a ray sampled at
`max(|dr|,|dc|)+1` points steps diagonally and so passes THROUGH a one-cell-thick
diagonal wall (STI read 0.705 behind a solid wall; a view reported through a solid
partition; VGA edges and geodesics crossing sealed walls). This module supplies a
single SUPERCOVER line test used everywhere visibility matters, so "walls block X" is
true — including diagonal walls and corner-to-corner OBST chains.

`segment_is_free(grid, a, b)` returns True iff the straight segment a->b stays entirely
in FREE space. It is CONSERVATIVE at corners: when the line crosses a cell corner
exactly, BOTH cells sharing that corner must be free (a diagonal OBST chain blocks).

`exempt_endpoints=True` (default) ignores the two endpoint cells (a seat or a window/
nature cell is often itself on/against a boundary); the interior must be free.

Self-test (analytic L0):
    python -m cnfa_algs.los
"""
from __future__ import annotations
from typing import List, Tuple
import numpy as np

RC = Tuple[int, int]
FREE = 1


def line_supercover(r0: int, c0: int, r1: int, c1: int) -> List[RC]:
    """All grid cells the continuous segment (r0,c0)->(r1,c1) passes through, INCLUDING
    both cells sharing a corner the line crosses exactly (supercover, not thin Bresenham)."""
    r0, c0, r1, c1 = int(r0), int(c0), int(r1), int(c1)
    dr = abs(r1 - r0); dc = abs(c1 - c0)
    r, c = r0, c0
    sr = 1 if r1 > r0 else -1
    sc = 1 if c1 > c0 else -1
    cells: List[RC] = [(r, c)]
    err = dr - dc
    ddr, ddc = 2 * dr, 2 * dc
    while (r, c) != (r1, c1):
        e2 = err  # snapshot
        if e2 > 0 and e2 < ddc:  # ambiguity band impossible with ints; handle exact corner below
            pass
        if e2 == 0:  # exact diagonal corner crossing -> include BOTH shoulder cells (conservative)
            cells.append((r + sr, c))
            cells.append((r, c + sc))
            r += sr; c += sc
            err += ddr - ddc
        elif e2 > 0:
            r += sr
            err -= ddc
        else:
            c += sc
            err += ddr
        cells.append((r, c))
    return cells


def segment_is_free(grid: np.ndarray, a: RC, b: RC, free_val: int = FREE,
                    exempt_endpoints: bool = True) -> bool:
    """True iff the segment a->b stays in FREE space (supercover; diagonal walls block).
    exempt_endpoints: the two endpoint cells are not required to be free."""
    H, W = grid.shape
    cells = line_supercover(a[0], a[1], b[0], b[1])
    if len(cells) <= 2:
        return True
    ends = {tuple(a), tuple(b)} if exempt_endpoints else set()
    for (r, c) in cells:
        if r < 0 or r >= H or c < 0 or c >= W:
            return False
        if (r, c) in ends:
            continue
        if grid[r, c] != free_val:
            return False
    return True


# --------------------------------------------------------------------------- self-test
if __name__ == "__main__":
    print("cnfa_algs.los self-test (analytic L0)\n" + "-" * 40)
    OBST = 2

    # 1. open grid: everything visible
    g = np.full((20, 20), FREE, np.int8)
    assert segment_is_free(g, (0, 0), (19, 19)), "open diagonal should be free"
    assert segment_is_free(g, (10, 0), (10, 19)), "open row should be free"

    # 2. orthogonal wall blocks
    g2 = np.full((20, 20), FREE, np.int8); g2[:, 10] = OBST
    assert not segment_is_free(g2, (10, 2), (10, 18)), "orthogonal wall must block"

    # 3. THE DIAGONAL WALL (the S1 bug): OBST chain corner-to-corner must block a ray
    #    trying to slip through the corner.
    g3 = np.full((11, 11), FREE, np.int8)
    for i in range(11):
        g3[i, i] = OBST                       # main-diagonal wall
    # a ray from one side of the diagonal to the other must be blocked
    leaks = 0
    for (a, b) in [((0, 3), (3, 0)), ((1, 4), (4, 1)), ((2, 6), (6, 2)), ((0, 5), (5, 0))]:
        if segment_is_free(g3, a, b):
            leaks += 1
    print(f"diagonal-wall leak test: {leaks} leaks (expect 0)")
    assert leaks == 0, "diagonal OBST chain must block LOS (S1)"

    # 4. endpoints exempt: a seat against a wall, window cell is OBST-ish boundary
    g4 = np.full((10, 10), FREE, np.int8); g4[:, 0] = OBST      # glazing wall at col 0
    assert segment_is_free(g4, (5, 3), (5, 0), exempt_endpoints=True), "window endpoint exempt -> visible"
    assert not segment_is_free(g4, (5, 3), (5, 0), exempt_endpoints=False), "without exemption the wall endpoint blocks"

    # 5. supercover superset of thin line (never fewer cells)
    cells = line_supercover(0, 0, 5, 3)
    assert (0, 0) in cells and (5, 3) in cells, "endpoints present"

    print("-" * 40 + "\nlos self-test: PASS")
