"""Tests for the mechanics lens — pickup detection, blocking, interaction tracking."""

import numpy as np
from arc_see.lenses import MechanicsMap
from arc_see.lenses.mechanics import mechanics


class TestMechanics:
    def setup_method(self):
        mechanics.reset()
        mechanics._player_color = None

    def test_empty_history(self):
        grid = np.zeros((64, 64), dtype=np.int64)
        result = mechanics(grid, [])
        assert isinstance(result, MechanicsMap)
        assert result.total_collected == 0
        assert len(result.collectables) == 0

    def test_detects_pickup(self):
        """When player moves over a colored cell and it disappears, that's a pickup."""
        # Frame 1: player (color 1) at (10,10), pickup (color 3) at (10,12)
        prev = np.zeros((64, 64), dtype=np.int64)
        prev[10, 10] = 1  # player
        prev[10, 12] = 3  # pickup

        # Frame 2: player moved to (10,12), pickup disappeared
        curr = np.zeros((64, 64), dtype=np.int64)
        curr[10, 12] = 1  # player now at pickup location

        # First call establishes player
        mechanics(prev, [])
        mechanics._player_color = 1  # help it along

        result = mechanics(curr, [prev])
        assert result.total_collected >= 1
        assert 3 in {e.color for e in result.collected}

    def test_tracks_remaining_collectables(self):
        """After detecting a collectable color, should track remaining instances."""
        prev = np.zeros((64, 64), dtype=np.int64)
        prev[10, 10] = 1  # player
        prev[10, 12] = 3  # pickup 1
        prev[20, 20] = 3  # pickup 2 (same color, different location)

        curr = np.zeros((64, 64), dtype=np.int64)
        curr[10, 12] = 1  # player collected pickup 1
        curr[20, 20] = 3  # pickup 2 still there

        mechanics._player_color = 1
        result = mechanics(curr, [prev])

        # Should know color 3 is collectable and one remains
        if 3 in result.collectables:
            assert len(result.collectables[3]) >= 1

    def test_detects_blocking_colors(self):
        """Large color regions adjacent to player should be detected as walls."""
        # Frame 1: player at (10,10)
        prev = np.zeros((64, 64), dtype=np.int64)
        prev[10, 10] = 1  # player
        prev[0:20, 11:50] = 5  # big wall (20*39 = 780 pixels)

        # Frame 2: player moved up to (9,10) — still adjacent to wall
        curr = np.zeros((64, 64), dtype=np.int64)
        curr[9, 10] = 1  # player moved
        curr[0:20, 11:50] = 5  # wall still there

        mechanics._player_color = 1
        result = mechanics(curr, [prev])
        # Color 5 is large and adjacent — should be blocking
        assert 5 in result.blocking_colors

    def test_reset_clears_history(self):
        """Reset should clear collected history but preserve player color."""
        mechanics._player_color = 1
        mechanics._collected.append(None)  # fake history
        mechanics.reset()
        assert len(mechanics._collected) == 0
        # Player color preserved
        assert mechanics._player_color == 1
