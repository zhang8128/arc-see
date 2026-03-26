"""Shared test fixtures: sample grids and frame histories."""

import numpy as np
import pytest


@pytest.fixture
def blank_grid():
    """64x64 grid of zeros (background)."""
    return np.zeros((64, 64), dtype=np.int64)


@pytest.fixture
def single_block():
    """Grid with one 4x4 block of color 1 at position (10, 10)."""
    grid = np.zeros((64, 64), dtype=np.int64)
    grid[10:14, 10:14] = 1
    return grid


@pytest.fixture
def two_blocks():
    """Grid with two blocks: color 1 at (10,10) and color 2 at (30,30)."""
    grid = np.zeros((64, 64), dtype=np.int64)
    grid[10:14, 10:14] = 1
    grid[30:34, 30:34] = 2
    return grid


@pytest.fixture
def nested_boxes():
    """Grid with a box inside a box. Outer=color 1 (8x8), inner=color 2 (4x4)."""
    grid = np.zeros((64, 64), dtype=np.int64)
    grid[10:18, 10:18] = 1
    grid[12:16, 12:16] = 2
    return grid


@pytest.fixture
def symmetric_grid():
    """Grid with horizontal and vertical symmetry."""
    grid = np.zeros((64, 64), dtype=np.int64)
    # Place symmetric blocks
    grid[10:14, 10:14] = 1
    grid[10:14, 50:54] = 1
    grid[50:54, 10:14] = 1
    grid[50:54, 50:54] = 1
    return grid


@pytest.fixture
def moved_block():
    """Pair of grids: a block that moved from (10,10) to (10,12)."""
    before = np.zeros((64, 64), dtype=np.int64)
    before[10:14, 10:14] = 1
    after = np.zeros((64, 64), dtype=np.int64)
    after[10:14, 12:16] = 1
    return before, after


@pytest.fixture
def grid_with_corner_goal():
    """Grid with a small pattern in top-right corner (goal indicator)."""
    grid = np.zeros((64, 64), dtype=np.int64)
    # Main content: block in the middle
    grid[28:36, 28:36] = 3
    # Goal pattern: small L-shape in top-right corner
    grid[0:3, 60:63] = 5
    grid[0, 59] = 5
    return grid
