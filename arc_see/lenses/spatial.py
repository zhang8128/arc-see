"""Spatial lenses: connected_components, edges, enclosure."""

from __future__ import annotations

import numpy as np
from scipy.ndimage import label

from arc_see.lenses import (
    RegionLabels,
    EdgeMask,
    ContainmentTree,
    register,
)


class ConnectedComponents:
    """Labels each contiguous non-zero region. Different colors = different objects."""

    name = "connected_components"

    def __call__(self, grid: np.ndarray) -> RegionLabels:
        result = np.zeros_like(grid, dtype=np.int64)
        next_label = 1

        for color in range(1, 16):
            mask = grid == color
            if not mask.any():
                continue
            labeled, num_features = label(mask)
            for region_idx in range(1, num_features + 1):
                result[labeled == region_idx] = next_label
                next_label += 1

        count = next_label - 1
        return RegionLabels(labels=result, count=count)


class Edges:
    """A cell is an edge if any 4-neighbor has a different color."""

    name = "edges"

    def __call__(self, grid: np.ndarray) -> EdgeMask:
        # Pad with the grid's own border values using edge-pad so borders detect edges
        # Actually pad with a sentinel (0) so border non-zero cells are edges
        padded = np.pad(grid, pad_width=1, mode="constant", constant_values=0)
        # Compare each cell to its 4 neighbors
        center = padded[1:-1, 1:-1]
        up    = padded[0:-2, 1:-1]
        down  = padded[2:,   1:-1]
        left  = padded[1:-1, 0:-2]
        right = padded[1:-1, 2:  ]

        # A cell is an edge if it differs from any neighbor
        # Background cells (0) that differ from neighbors are also "edges" —
        # but we only want edges ON non-zero cells or at color boundaries.
        # The spec says "a cell is an edge if any 4-neighbor has a different color"
        # This applies to all cells including zero.
        mask = (
            (center != up) |
            (center != down) |
            (center != left) |
            (center != right)
        )

        return EdgeMask(mask=mask)


class Enclosure:
    """Detects nesting via bounding box containment. DependentLens."""

    name = "enclosure"
    depends_on = "connected_components"

    def __call__(self, grid: np.ndarray, dependency: RegionLabels) -> ContainmentTree:
        labels = dependency.labels
        count = dependency.count

        if count == 0:
            return ContainmentTree(parent={}, children={})

        # Compute bounding box for each region label
        bboxes: dict[int, tuple[int, int, int, int]] = {}
        for region_id in range(1, count + 1):
            ys, xs = np.where(labels == region_id)
            if len(ys) == 0:
                continue
            bboxes[region_id] = (int(ys.min()), int(xs.min()), int(ys.max()), int(xs.max()))

        region_ids = list(bboxes.keys())

        # For each region, find the smallest containing region
        parent: dict[int, int | None] = {rid: None for rid in region_ids}
        children: dict[int, list[int]] = {rid: [] for rid in region_ids}

        for rid in region_ids:
            r_y1, r_x1, r_y2, r_x2 = bboxes[rid]
            best_parent = None
            best_area = float("inf")

            for other in region_ids:
                if other == rid:
                    continue
                o_y1, o_x1, o_y2, o_x2 = bboxes[other]
                # Check if other's bbox fully contains rid's bbox
                if o_y1 <= r_y1 and o_x1 <= r_x1 and o_y2 >= r_y2 and o_x2 >= r_x2:
                    area = (o_y2 - o_y1) * (o_x2 - o_x1)
                    if area < best_area:
                        best_area = area
                        best_parent = other

            parent[rid] = best_parent

        for rid, par in parent.items():
            if par is not None:
                children[par].append(rid)

        return ContainmentTree(parent=parent, children=children)


# Instantiate and register
connected_components = ConnectedComponents()
edges = Edges()
enclosure = Enclosure()

register(connected_components)
register(edges)
register(enclosure)
