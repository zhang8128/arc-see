import numpy as np
import pytest
from unittest.mock import MagicMock, patch
from arcengine import GameAction, GameState


class FakeObs:
    """Fake observation returned by env.step/reset."""
    def __init__(self, frame, state=GameState.NOT_FINISHED):
        self.frame = [frame]
        self.state = state


def make_env(initial_grid, action_results=None):
    """Create a mock env that returns predetermined frames."""
    env = MagicMock()
    env.action_space = [GameAction.ACTION1, GameAction.ACTION2,
                        GameAction.ACTION3, GameAction.ACTION4]
    env.environment_info = MagicMock()
    env.environment_info.game_id = "test-game"
    env.environment_info.title = "TEST"
    env.environment_info.tags = ["keyboard"]
    env.environment_info.baseline_actions = [20, 30]

    env.reset.return_value = FakeObs(initial_grid)

    if action_results:
        env.step.side_effect = [FakeObs(f, s) for f, s in action_results]
    else:
        env.step.return_value = FakeObs(initial_grid)

    return env


def make_sliding_grid():
    """Create a grid resembling a sliding puzzle."""
    grid = np.full((64, 64), 4, dtype=np.int64)
    grid[10:50, 10:50] = 3
    grid[40:42, 30:32] = 12
    grid[20:21, 20:21] = 1
    return grid


def make_moved_grid(player_pos):
    """Same as sliding grid but player at given (row, col)."""
    grid = make_sliding_grid()
    grid[40:42, 30:32] = 3
    r, c = player_pos
    grid[r:r+2, c:c+2] = 12
    return grid


class TestGameSession:
    def test_reset_returns_perception(self):
        from arc_see.session import GameSession
        grid = make_sliding_grid()
        env = make_env(grid)
        session = GameSession(env)
        result = session.reset()
        assert "Connected Components" in result or "Spatial" in result
        assert len(session.frames) == 1

    def test_perceive_returns_text(self):
        from arc_see.session import GameSession
        grid = make_sliding_grid()
        env = make_env(grid)
        session = GameSession(env)
        session.reset()
        result = session.perceive()
        assert "Spatial" in result or "Connected Components" in result
        assert isinstance(result, str)

    def test_step_returns_diff(self):
        from arc_see.session import GameSession
        initial = make_sliding_grid()
        moved = make_moved_grid((35, 30))
        env = make_env(initial, action_results=[(moved, GameState.NOT_FINISHED)])
        session = GameSession(env)
        session.reset()
        result = session.step("ACTION1")
        assert "ACTION1" in result
        assert "NOT_FINISHED" in result
        assert session.turn_count == 1
        assert session.total_turns == 1
        assert "Turn:" in result

    def test_step_invalid_action(self):
        from arc_see.session import GameSession
        grid = make_sliding_grid()
        env = make_env(grid)
        session = GameSession(env)
        session.reset()
        result = session.step("INVALID")
        assert "not available" in result.lower() or "invalid" in result.lower()

    def test_step_tracks_player_movement(self):
        from arc_see.session import GameSession
        initial = make_sliding_grid()
        moved = make_moved_grid((35, 30))
        env = make_env(initial, action_results=[(moved, GameState.NOT_FINISHED)])
        session = GameSession(env)
        session.reset()
        result = session.step("ACTION1")
        assert "moved" in result.lower() or "player" in result.lower() or "12" in result

    def test_reflect_summarizes_session(self):
        from arc_see.session import GameSession
        initial = make_sliding_grid()
        moved = make_moved_grid((35, 30))
        env = make_env(initial, action_results=[(moved, GameState.NOT_FINISHED)])
        session = GameSession(env)
        session.reset()
        session.step("ACTION1")
        result = session.reflect()
        assert "Turns" in result or "turns" in result
        assert "ACTION1" in result
        # Check for physics/positions in reflect output
        assert "Physics" in result or "physics" in result.lower()
        assert "Player position" in result or "player_color" in result

    def test_status_returns_state(self):
        from arc_see.session import GameSession
        grid = make_sliding_grid()
        env = make_env(grid)
        session = GameSession(env)
        session.reset()
        result = session.status()
        assert "NOT_FINISHED" in result or "not_finished" in result.lower()
        assert "test-game" in result.lower() or "TEST" in result
        assert "Available actions" in result or "available" in result.lower()

    def test_reset_preserves_learned(self):
        from arc_see.session import GameSession
        initial = make_sliding_grid()
        moved = make_moved_grid((35, 30))
        env = make_env(initial, action_results=[
            (moved, GameState.NOT_FINISHED),
        ])
        session = GameSession(env)
        session.reset()
        session.step("ACTION1")
        old_learned = dict(session.learned)
        env.reset.return_value = FakeObs(initial)
        session.reset()
        assert session.turn_count == 0
        assert len(session.frames) == 1
        assert session.learned == old_learned

    def test_win_increments_levels(self):
        from arc_see.session import GameSession
        initial = make_sliding_grid()
        win_grid = make_moved_grid((20, 20))
        env = make_env(initial, action_results=[
            (win_grid, GameState.WIN),
        ])
        session = GameSession(env)
        session.reset()
        result = session.step("ACTION1")
        assert session.levels_completed == 1
        assert "WIN" in result
