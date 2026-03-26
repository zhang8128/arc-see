"""Structural lenses: symmetry, periodicity, alignment."""

from __future__ import annotations

import numpy as np

from arc_see.lenses import (
    SymmetryResult,
    PeriodicityResult,
    AlignmentResult,
    register,
)


class Symmetry:
    """Checks horizontal, vertical, and rotational symmetry."""

    name = "symmetry"

    def __call__(self, grid: np.ndarray) -> SymmetryResult:
        horizontal = bool(np.array_equal(grid, grid[::-1, :]))
        vertical = bool(np.array_equal(grid, grid[:, ::-1]))

        rot180 = bool(np.array_equal(grid, np.rot90(grid, 2)))
        rot90 = bool(np.array_equal(grid, np.rot90(grid, 1)))

        if rot90:
            rotational_order = 4
        elif rot180:
            rotational_order = 2
        else:
            rotational_order = 0

        return SymmetryResult(
            horizontal=horizontal,
            vertical=vertical,
            rotational_order=rotational_order,
        )


class Periodicity:
    """Finds the smallest repeating period along each axis."""

    name = "periodicity"

    def __call__(self, grid: np.ndarray) -> PeriodicityResult:
        rows, cols = grid.shape

        row_period = self._find_period(grid, axis=0, size=rows)
        col_period = self._find_period(grid, axis=1, size=cols)

        return PeriodicityResult(row_period=row_period, col_period=col_period)

    def _find_period(self, grid: np.ndarray, axis: int, size: int) -> int | None:
        for period in range(2, size // 2 + 1):
            if size % period != 0:
                continue
            if self._check_period(grid, axis, period, size):
                return period
        return None

    def _check_period(
        self, grid: np.ndarray, axis: int, period: int, size: int
    ) -> bool:
        if axis == 0:
            tile = grid[:period, :]
            for start in range(period, size, period):
                if not np.array_equal(tile, grid[start : start + period, :]):
                    return False
        else:
            tile = grid[:, :period]
            for start in range(period, size, period):
                if not np.array_equal(tile, grid[:, start : start + period]):
                    return False
        return True


class Alignment:
    """Finds divider lines: uniform rows/cols with non-uniform content on both sides."""

    name = "alignment"

    def __call__(self, grid: np.ndarray) -> AlignmentResult:
        rows, cols = grid.shape

        row_lines = []
        for r in range(1, rows - 1):
            row = grid[r, :]
            if np.all(row == row[0]):  # uniform row
                # Check non-uniform content on both sides
                above = grid[:r, :]
                below = grid[r + 1 :, :]
                if not np.all(above == above[0, 0]) and not np.all(below == below[0, 0]):
                    row_lines.append(r)

        col_lines = []
        for c in range(1, cols - 1):
            col = grid[:, c]
            if np.all(col == col[0]):  # uniform column
                # Check non-uniform content on both sides
                left = grid[:, :c]
                right = grid[:, c + 1 :]
                if not np.all(left == left[0, 0]) and not np.all(right == right[0, 0]):
                    col_lines.append(c)

        return AlignmentResult(row_lines=row_lines, col_lines=col_lines)


# Instantiate and register
symmetry = Symmetry()
periodicity = Periodicity()
alignment = Alignment()

register(symmetry)
register(periodicity)
register(alignment)
