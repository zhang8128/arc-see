"""Relational lenses: proximity, color_correspondence, size_count."""

from __future__ import annotations

import math
from collections import Counter

import numpy as np

from arc_see.lenses import (
    RegionLabels,
    ProximityGraph,
    ColorCorrespondence,
    SizeCount,
    register,
)


class Proximity:
    """Centroid distance graph between all object pairs."""

    name = "proximity"
    depends_on = "connected_components"

    def __call__(self, grid: np.ndarray, dependency: RegionLabels) -> ProximityGraph:
        labels = dependency.labels
        count = dependency.count

        # Compute centroid for each region
        centroids: dict[int, tuple[float, float]] = {}
        for region_id in range(1, count + 1):
            ys, xs = np.where(labels == region_id)
            if len(ys) == 0:
                continue
            centroids[region_id] = (float(np.mean(ys)), float(np.mean(xs)))

        # Compute pairwise distances for all a < b pairs
        distances: dict[tuple[int, int], float] = {}
        region_ids = sorted(centroids.keys())
        for i, a in enumerate(region_ids):
            for b in region_ids[i + 1:]:
                cy_a, cx_a = centroids[a]
                cy_b, cx_b = centroids[b]
                dist = math.sqrt((cy_b - cy_a) ** 2 + (cx_b - cx_a) ** 2)
                distances[(a, b)] = dist

        return ProximityGraph(distances=distances)


class ColorCorrespondenceL:
    """Maps colors to objects and vice versa."""

    name = "color_correspondence"
    depends_on = "connected_components"

    def __call__(self, grid: np.ndarray, dependency: RegionLabels) -> ColorCorrespondence:
        labels = dependency.labels
        count = dependency.count

        color_to_objects: dict[int, list[int]] = {}
        object_to_color: dict[int, int] = {}

        for region_id in range(1, count + 1):
            ys, xs = np.where(labels == region_id)
            if len(ys) == 0:
                continue
            # Get all pixel colors for this region
            pixel_colors = grid[ys, xs]
            # Find most common non-zero color
            counts = Counter(c for c in pixel_colors if c != 0)
            if not counts:
                continue
            dominant_color = counts.most_common(1)[0][0]
            object_to_color[region_id] = dominant_color
            color_to_objects.setdefault(dominant_color, []).append(region_id)

        return ColorCorrespondence(
            color_to_objects=color_to_objects,
            object_to_color=object_to_color,
        )


class SizeCountL:
    """Pixel count per object and count-by-size histogram."""

    name = "size_count"
    depends_on = "connected_components"

    def __call__(self, grid: np.ndarray, dependency: RegionLabels) -> SizeCount:
        labels = dependency.labels
        count = dependency.count

        sizes: dict[int, int] = {}
        for region_id in range(1, count + 1):
            pixel_count = int(np.sum(labels == region_id))
            sizes[region_id] = pixel_count

        count_by_size: dict[int, int] = {}
        for pixel_count in sizes.values():
            count_by_size[pixel_count] = count_by_size.get(pixel_count, 0) + 1

        return SizeCount(sizes=sizes, count_by_size=count_by_size)


# Instantiate and register
proximity = Proximity()
color_correspondence = ColorCorrespondenceL()
size_count = SizeCountL()

register(proximity)
register(color_correspondence)
register(size_count)
