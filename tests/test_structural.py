# tests/test_structural.py
import numpy as np
from arc_see.lenses import SymmetryResult, PeriodicityResult, AlignmentResult
from arc_see.lenses.structural import symmetry, periodicity, alignment


class TestSymmetry:
    def test_blank_grid(self, blank_grid):
        result = symmetry(blank_grid)
        assert isinstance(result, SymmetryResult)
        assert result.horizontal
        assert result.vertical

    def test_symmetric_grid(self, symmetric_grid):
        result = symmetry(symmetric_grid)
        assert result.horizontal
        assert result.vertical

    def test_asymmetric(self):
        grid = np.zeros((64, 64), dtype=np.int64)
        grid[5:10, 5:10] = 1
        result = symmetry(grid)
        assert not result.horizontal
        assert not result.vertical

    def test_horizontal_only(self):
        grid = np.zeros((64, 64), dtype=np.int64)
        grid[10:14, 30:34] = 1
        grid[50:54, 30:34] = 1
        result = symmetry(grid)
        assert result.horizontal


class TestPeriodicity:
    def test_no_pattern(self, single_block):
        result = periodicity(single_block)
        assert isinstance(result, PeriodicityResult)
        assert result.row_period is None
        assert result.col_period is None

    def test_row_repeating(self):
        grid = np.zeros((64, 64), dtype=np.int64)
        for row in range(0, 64, 8):
            grid[row, :] = 1
        result = periodicity(grid)
        assert result.row_period == 8

    def test_col_repeating(self):
        grid = np.zeros((64, 64), dtype=np.int64)
        for col in range(0, 64, 4):
            grid[:, col] = 2
        result = periodicity(grid)
        assert result.col_period == 4


class TestAlignment:
    def test_no_alignment(self, single_block):
        result = alignment(single_block)
        assert isinstance(result, AlignmentResult)

    def test_grid_of_blocks(self):
        grid = np.zeros((64, 64), dtype=np.int64)
        for r in range(4):
            for c in range(4):
                grid[r*16+2:r*16+14, c*16+2:c*16+14] = 1
        result = alignment(grid)
        assert len(result.row_lines) >= 3
        assert len(result.col_lines) >= 3
