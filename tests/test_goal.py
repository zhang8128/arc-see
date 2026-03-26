"""Tests for the goal lens: multi-goal detection in corner/edge regions."""

import numpy as np
from arc_see.lenses import GoalDetection, GoalCandidate
from arc_see.lenses.goal import goal_detection


class TestGoalDetection:
    def test_blank_grid(self, blank_grid):
        result = goal_detection(blank_grid)
        assert isinstance(result, GoalDetection)
        assert len(result.goals) == 0
        assert result.best_similarity == 0.0

    def test_corner_goal(self, grid_with_corner_goal):
        result = goal_detection(grid_with_corner_goal)
        assert len(result.goals) >= 1
        # At least one goal should be in the top-right area
        found_corner = False
        for g in result.goals:
            y1, x1, y2, x2 = g.location
            if y1 < 10 and x1 > 50:
                found_corner = True
        assert found_corner

    def test_multiple_goals(self):
        """Grid with patterns in two different corners."""
        grid = np.zeros((64, 64), dtype=np.int64)
        grid[28:36, 28:36] = 3  # main content
        grid[0:3, 0:3] = 5      # goal in top-left
        grid[61:64, 61:64] = 7  # goal in bottom-right
        result = goal_detection(grid)
        assert len(result.goals) >= 2

    def test_similarity_with_matching_content(self):
        """Goal similarity should be higher when grid content resembles goal."""
        grid_far = np.zeros((64, 64), dtype=np.int64)
        grid_far[0:2, 62:64] = 3       # goal: small block of color 3
        grid_far[30:34, 30:34] = 1     # content: wrong color

        grid_close = np.zeros((64, 64), dtype=np.int64)
        grid_close[0:2, 62:64] = 3     # same goal
        grid_close[30:32, 30:32] = 3   # content: same color, similar size

        result_far = goal_detection(grid_far)
        result_close = goal_detection(grid_close)
        assert result_close.best_similarity >= result_far.best_similarity

    def test_no_false_positive_center(self, single_block):
        """Block in the middle shouldn't be detected as a goal."""
        result = goal_detection(single_block)
        for g in result.goals:
            y1, x1, y2, x2 = g.location
            # Should not claim center content is a goal
            assert y1 < 10 or y2 > 54 or x1 < 10 or x2 > 54
