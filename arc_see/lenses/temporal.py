"""Temporal lenses: movement, creation_destruction, state_change."""

from __future__ import annotations

import numpy as np
from scipy.ndimage import label

from arc_see.lenses import (
    RegionLabels,
    DisplacementField,
    ChangeMask,
    StateChangeMask,
    register,
)


def _centroids_by_color(grid: np.ndarray) -> dict[int, list[tuple[float, float, int]]]:
    """Return {color: [(cy, cx, region_label), ...]} for each color in grid."""
    result: dict[int, list[tuple[float, float, int]]] = {}
    region_label = 1
    for color in range(1, 16):
        mask = grid == color
        if not mask.any():
            continue
        labeled, num_features = label(mask)
        for idx in range(1, num_features + 1):
            ys, xs = np.where(labeled == idx)
            cy = float(ys.mean())
            cx = float(xs.mean())
            result.setdefault(color, []).append((cy, cx, region_label))
            region_label += 1
    return result


class _Movement:
    """Detect per-object displacement between frames. Depends on connected_components."""

    name = "movement"
    depends_on = "connected_components"

    def __call__(
        self,
        current: np.ndarray,
        history: list[np.ndarray],
        dependency: RegionLabels,
    ) -> DisplacementField:
        if not history:
            return DisplacementField(vectors={})

        prev = history[-1]

        # Build centroid maps for both frames, keyed by color
        prev_by_color = _centroids_by_color(prev)
        curr_by_color = _centroids_by_color(current)

        vectors: dict[int, tuple[float, float]] = {}
        obj_id = 1

        for color, prev_regions in prev_by_color.items():
            curr_regions = curr_by_color.get(color, [])
            if not curr_regions:
                continue

            for p_cy, p_cx, _ in prev_regions:
                # Find nearest centroid in current frame with same color
                best_dist = float("inf")
                best_c = None
                for c_cy, c_cx, _ in curr_regions:
                    dist = (c_cy - p_cy) ** 2 + (c_cx - p_cx) ** 2
                    if dist < best_dist:
                        best_dist = dist
                        best_c = (c_cy, c_cx)

                if best_c is not None:
                    dy = best_c[0] - p_cy
                    dx = best_c[1] - p_cx
                    vectors[obj_id] = (dy, dx)
                    obj_id += 1

        return DisplacementField(vectors=vectors)


class _CreationDestruction:
    """Detect appeared/disappeared pixels between current and previous frame."""

    name = "creation_destruction"

    def __call__(
        self,
        current: np.ndarray,
        history: list[np.ndarray],
    ) -> ChangeMask:
        shape = current.shape
        if not history:
            return ChangeMask(
                appeared=np.zeros(shape, dtype=bool),
                disappeared=np.zeros(shape, dtype=bool),
            )

        prev = history[-1]
        appeared = (current != 0) & (prev == 0)
        disappeared = (current == 0) & (prev != 0)
        return ChangeMask(appeared=appeared, disappeared=disappeared)


class _StateChange:
    """Detect same-position color changes between current and previous frame."""

    name = "state_change"

    def __call__(
        self,
        current: np.ndarray,
        history: list[np.ndarray],
    ) -> StateChangeMask:
        shape = current.shape
        if not history:
            return StateChangeMask(
                mask=np.zeros(shape, dtype=bool),
                old_colors=np.zeros(shape, dtype=np.int64),
                new_colors=np.zeros(shape, dtype=np.int64),
            )

        prev = history[-1]
        mask = (current != 0) & (prev != 0) & (current != prev)
        old_colors = np.where(mask, prev, 0).astype(np.int64)
        new_colors = np.where(mask, current, 0).astype(np.int64)
        return StateChangeMask(mask=mask, old_colors=old_colors, new_colors=new_colors)


# Instantiate and register
movement = _Movement()
creation_destruction = _CreationDestruction()
state_change = _StateChange()

register(movement)
register(creation_destruction)
register(state_change)
