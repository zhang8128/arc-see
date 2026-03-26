"""Tests for temporal lenses: movement, creation_destruction, state_change."""

import numpy as np
import pytest
from arc_see.lenses import DisplacementField, ChangeMask, StateChangeMask
from arc_see.lenses.spatial import connected_components
from arc_see.lenses.temporal import movement, creation_destruction, state_change


class TestMovement:
    def test_no_movement(self, single_block):
        cc = connected_components(single_block)
        result = movement(single_block, [single_block], cc)
        assert isinstance(result, DisplacementField)
        for obj_id, (dy, dx) in result.vectors.items():
            assert dy == 0.0
            assert dx == 0.0

    def test_block_moved_right(self, moved_block):
        before, after = moved_block
        cc_before = connected_components(before)
        result = movement(after, [before], cc_before)
        assert len(result.vectors) >= 1
        obj_id = next(iter(result.vectors))
        dy, dx = result.vectors[obj_id]
        assert dy == 0.0
        assert dx == 2.0

    def test_empty_history(self, single_block):
        cc = connected_components(single_block)
        result = movement(single_block, [], cc)
        assert len(result.vectors) == 0


class TestCreationDestruction:
    def test_no_change(self, single_block):
        result = creation_destruction(single_block, [single_block])
        assert isinstance(result, ChangeMask)
        assert not result.appeared.any()
        assert not result.disappeared.any()

    def test_block_appears(self, blank_grid, single_block):
        result = creation_destruction(single_block, [blank_grid])
        assert result.appeared[10:14, 10:14].all()
        assert not result.disappeared.any()

    def test_block_disappears(self, blank_grid, single_block):
        result = creation_destruction(blank_grid, [single_block])
        assert not result.appeared.any()
        assert result.disappeared[10:14, 10:14].all()

    def test_empty_history(self, single_block):
        result = creation_destruction(single_block, [])
        assert not result.appeared.any()
        assert not result.disappeared.any()


class TestStateChange:
    def test_no_change(self, single_block):
        result = state_change(single_block, [single_block])
        assert isinstance(result, StateChangeMask)
        assert not result.mask.any()

    def test_color_change(self):
        before = np.zeros((64, 64), dtype=np.int64)
        before[10:14, 10:14] = 1
        after = np.zeros((64, 64), dtype=np.int64)
        after[10:14, 10:14] = 2
        result = state_change(after, [before])
        assert result.mask[10:14, 10:14].all()
        assert (result.old_colors[10:14, 10:14] == 1).all()
        assert (result.new_colors[10:14, 10:14] == 2).all()

    def test_empty_history(self, single_block):
        result = state_change(single_block, [])
        assert not result.mask.any()
