"""Goal lens: detect small isolated patterns in corners/edges as goal indicators."""

from __future__ import annotations

import numpy as np

from arc_see.lenses import GoalCandidate, GoalDetection, register


# Thresholds
_CORNER_SIZE = 8          # corner regions are 8x8
_EDGE_STRIP = 4           # edge strips are 4 pixels wide
_MAX_FILL_PIXELS = 64     # skip regions with more than this many non-zero pixels
_MAX_FILL_RATIO = 0.5     # skip regions that are more than 50% filled
_CORNER_BONUS = 1.5       # score multiplier for corner regions
_MIN_SCORE = 0.05         # minimum isolation score to include a candidate


def _extract_region(grid: np.ndarray, y1: int, x1: int, y2: int, x2: int) -> np.ndarray:
    return grid[y1:y2, x1:x2]


def _compute_similarity(goal_pattern: np.ndarray, grid: np.ndarray,
                        goal_y1: int, goal_x1: int, goal_y2: int, goal_x2: int) -> float:
    """
    Compare goal pattern to the rest of the grid.
    Uses Jaccard color overlap and size ratio of nearest similarly-colored region.
    """
    goal_colors = set(int(c) for c in goal_pattern.flat if c != 0)
    if not goal_colors:
        return 0.0

    # Mask out the goal region itself when comparing
    mask = np.ones(grid.shape, dtype=bool)
    mask[goal_y1:goal_y2, goal_x1:goal_x2] = False
    rest = grid[mask]

    rest_colors = set(int(c) for c in rest if c != 0)

    if not rest_colors:
        return 0.0

    # Jaccard similarity on color sets
    intersection = goal_colors & rest_colors
    union = goal_colors | rest_colors
    jaccard = len(intersection) / len(union)

    # Size ratio: count pixels of matching colors in the rest vs goal
    goal_pixel_count = int(np.count_nonzero(goal_pattern))
    if goal_pixel_count == 0:
        return 0.0

    matching_pixels_in_rest = int(np.sum(np.isin(grid[mask], list(goal_colors))))
    # Ratio: how closely does the rest match the goal in size?
    # Cap at 1.0 to avoid penalizing having more matching pixels
    size_ratio = min(1.0, matching_pixels_in_rest / (goal_pixel_count * 4))

    return (jaccard + size_ratio) / 2.0


def _candidate_from_region(
    grid: np.ndarray,
    y1: int, x1: int, y2: int, x2: int,
    is_corner: bool,
) -> GoalCandidate | None:
    """Try to build a GoalCandidate from a region. Returns None if region is unsuitable."""
    region = _extract_region(grid, y1, x1, y2, x2)
    nonzero_count = int(np.count_nonzero(region))

    if nonzero_count == 0:
        return None

    region_size = (y2 - y1) * (x2 - x1)
    fill_ratio = nonzero_count / region_size

    if nonzero_count > _MAX_FILL_PIXELS:
        return None
    if fill_ratio > _MAX_FILL_RATIO:
        return None

    # Isolation score: lower fill = more isolated = higher score
    isolation = 1.0 - fill_ratio
    score = isolation * (_CORNER_BONUS if is_corner else 1.0)

    if score < _MIN_SCORE:
        return None

    similarity = _compute_similarity(grid, grid, y1, x1, y2, x2)
    return GoalCandidate(
        pattern=region.copy(),
        location=(y1, x1, y2, x2),
        similarity=float(similarity),
    )


class GoalLens:
    """Detects small isolated patterns in corner/edge regions as goal candidates."""

    name = "goal"

    def __call__(self, grid: np.ndarray) -> GoalDetection:
        h, w = grid.shape
        cs = _CORNER_SIZE
        es = _EDGE_STRIP

        # Define corner regions (y1, x1, y2, x2, is_corner)
        regions: list[tuple[int, int, int, int, bool]] = [
            # Corners
            (0,    0,    cs,   cs,   True),   # top-left
            (0,    w-cs, cs,   w,    True),   # top-right
            (h-cs, 0,    h,    cs,   True),   # bottom-left
            (h-cs, w-cs, h,    w,    True),   # bottom-right
            # Edges (strips, excluding corners to avoid double-counting)
            (0,    cs,   es,   w-cs, False),  # top strip (middle)
            (h-es, cs,   h,    w-cs, False),  # bottom strip (middle)
            (cs,   0,    h-cs, es,   False),  # left strip (middle)
            (cs,   w-es, h-cs, w,    False),  # right strip (middle)
        ]

        candidates: list[tuple[float, GoalCandidate]] = []

        for y1, x1, y2, x2, is_corner in regions:
            # Guard against degenerate regions on small grids
            if y2 <= y1 or x2 <= x1:
                continue
            candidate = _candidate_from_region(grid, y1, x1, y2, x2, is_corner)
            if candidate is not None:
                # Score for sorting: isolation-based
                region = grid[y1:y2, x1:x2]
                nonzero_count = int(np.count_nonzero(region))
                region_size = (y2 - y1) * (x2 - x1)
                fill_ratio = nonzero_count / region_size
                isolation = 1.0 - fill_ratio
                sort_score = isolation * (_CORNER_BONUS if is_corner else 1.0)
                candidates.append((sort_score, candidate))

        # Sort by score descending
        candidates.sort(key=lambda x: x[0], reverse=True)
        goals = [c for _, c in candidates]

        best_similarity = max((g.similarity for g in goals), default=0.0)
        return GoalDetection(goals=goals, best_similarity=best_similarity)


# Instantiate and register
goal_detection = GoalLens()
register(goal_detection)
