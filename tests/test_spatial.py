"""Tests for spatial lenses: connected_components, edges, enclosure."""

import numpy as np
import pytest
from arc_see.lenses import RegionLabels, EdgeMask, ContainmentTree
from arc_see.lenses.spatial import connected_components, edges, enclosure


class TestConnectedComponents:
    def test_blank_grid(self, blank_grid):
        result = connected_components(blank_grid)
        assert isinstance(result, RegionLabels)
        assert result.count == 0

    def test_single_block(self, single_block):
        result = connected_components(single_block)
        assert result.count == 1
        block_labels = result.labels[10:14, 10:14]
        assert np.all(block_labels == block_labels[0, 0])
        assert block_labels[0, 0] != 0

    def test_two_blocks(self, two_blocks):
        result = connected_components(two_blocks)
        assert result.count == 2
        label_a = result.labels[10, 10]
        label_b = result.labels[30, 30]
        assert label_a != label_b
        assert label_a != 0
        assert label_b != 0

    def test_background_is_zero(self, single_block):
        result = connected_components(single_block)
        assert result.labels[0, 0] == 0
        assert result.labels[63, 63] == 0


class TestEdges:
    def test_blank_grid(self, blank_grid):
        result = edges(blank_grid)
        assert isinstance(result, EdgeMask)
        assert not result.mask.any()

    def test_single_block(self, single_block):
        result = edges(single_block)
        assert result.mask[10, 10]    # corner of block is edge
        assert result.mask[13, 13]    # other corner
        assert not result.mask[11, 11]  # interior not edge
        assert not result.mask[0, 0]    # far from block

    def test_adjacent_colors(self):
        grid = np.zeros((64, 64), dtype=np.int64)
        grid[10:14, 10:14] = 1
        grid[10:14, 14:18] = 2
        result = edges(grid)
        assert result.mask[10, 13]
        assert result.mask[10, 14]


class TestEnclosure:
    def test_no_nesting(self, two_blocks):
        cc = connected_components(two_blocks)
        result = enclosure(two_blocks, cc)
        assert isinstance(result, ContainmentTree)
        for region_id, parent in result.parent.items():
            assert parent is None

    def test_nested_boxes(self, nested_boxes):
        cc = connected_components(nested_boxes)
        result = enclosure(nested_boxes, cc)
        inner_label = cc.labels[13, 13]
        outer_label = cc.labels[10, 10]
        assert result.parent[inner_label] == outer_label
        assert inner_label in result.children[outer_label]
