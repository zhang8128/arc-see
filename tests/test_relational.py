"""Tests for relational lenses: proximity, color_correspondence, size_count."""

import numpy as np
import pytest

from arc_see.lenses import ProximityGraph, ColorCorrespondence, SizeCount
from arc_see.lenses.spatial import connected_components
from arc_see.lenses.relational import proximity, color_correspondence, size_count


class TestProximity:
    def test_two_blocks(self, two_blocks):
        cc = connected_components(two_blocks)
        result = proximity(two_blocks, cc)
        assert isinstance(result, ProximityGraph)
        assert len(result.distances) == 1
        pair = next(iter(result.distances))
        dist = result.distances[pair]
        # Centroids at ~(12,12) and ~(32,32), distance ~28.28
        assert 28.0 < dist < 29.0

    def test_single_block(self, single_block):
        cc = connected_components(single_block)
        result = proximity(single_block, cc)
        assert len(result.distances) == 0


class TestColorCorrespondence:
    def test_two_colors(self, two_blocks):
        cc = connected_components(two_blocks)
        result = color_correspondence(two_blocks, cc)
        assert isinstance(result, ColorCorrespondence)
        assert 1 in result.color_to_objects
        assert 2 in result.color_to_objects
        assert len(result.color_to_objects[1]) == 1
        assert len(result.color_to_objects[2]) == 1

    def test_same_color_multiple_objects(self):
        grid = np.zeros((64, 64), dtype=np.int64)
        grid[10:14, 10:14] = 1
        grid[30:34, 30:34] = 1
        cc = connected_components(grid)
        result = color_correspondence(grid, cc)
        assert len(result.color_to_objects[1]) == 2


class TestSizeCount:
    def test_two_equal_blocks(self, two_blocks):
        cc = connected_components(two_blocks)
        result = size_count(two_blocks, cc)
        assert isinstance(result, SizeCount)
        for obj_id in result.sizes:
            assert result.sizes[obj_id] == 16
        assert result.count_by_size[16] == 2

    def test_different_sizes(self):
        grid = np.zeros((64, 64), dtype=np.int64)
        grid[10:14, 10:14] = 1     # 16 pixels
        grid[30:38, 30:38] = 2     # 64 pixels
        cc = connected_components(grid)
        result = size_count(grid, cc)
        assert result.count_by_size[16] == 1
        assert result.count_by_size[64] == 1
