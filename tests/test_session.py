import numpy as np
import pytest
from unittest.mock import MagicMock, patch
from arcengine import GameAction, GameState


class FakeObs:
    """Fake observation returned by env.step/reset."""
    def __init__(self, frame, state=GameState.NOT_FINISHED, levels_completed=0):
        self.frame = [frame]
        self.state = state
        self.levels_completed = levels_completed


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
        env.step.side_effect = [
            FakeObs(*r) if isinstance(r, tuple) else r for r in action_results
        ]
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
        assert "Spatial" in result
        assert len(session.frames) == 1

    def test_perceive_returns_text(self):
        from arc_see.session import GameSession
        grid = make_sliding_grid()
        env = make_env(grid)
        session = GameSession(env)
        session.reset()
        result = session.perceive()
        assert "Spatial" in result
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
        # Player color 12 should be detected and learned
        assert session.learned.get("player_color") == "12"
        assert "moved" in result.lower()

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

    def test_reset_clears_learned(self):
        from arc_see.session import GameSession
        initial = make_sliding_grid()
        moved = make_moved_grid((35, 30))
        env = make_env(initial, action_results=[
            (moved, GameState.NOT_FINISHED),
        ])
        session = GameSession(env)
        session.reset()
        session.step("ACTION1")
        assert session.learned  # something was learned
        env.reset.return_value = FakeObs(initial)
        session.reset()
        assert session.turn_count == 0
        assert len(session.frames) == 1
        assert session.learned == {}  # cleared on reset

    def test_win_increments_levels(self):
        from arc_see.session import GameSession
        initial = make_sliding_grid()
        win_grid = make_moved_grid((20, 20))
        # On final-level win, game engine sets levels_completed to the total.
        env = make_env(initial, action_results=[
            FakeObs(win_grid, GameState.WIN, levels_completed=1),
        ])
        session = GameSession(env)
        session.reset()
        result = session.step("ACTION1")
        assert session.levels_completed == 1
        assert "WIN" in result

    def test_step_mirrors_obs_levels_completed_mid_game(self):
        """Regression: session.levels_completed must mirror obs.levels_completed
        even when obs.state is still NOT_FINISHED. The game engine keeps state
        = NOT_FINISHED until ALL levels are done; intermediate level advances
        are only visible via obs.levels_completed. The old code gated the
        increment on GameState.WIN and missed every intermediate advance."""
        from arc_see.session import GameSession
        initial = make_sliding_grid()
        mid_grid = make_moved_grid((35, 30))
        env = make_env(initial, action_results=[
            # Simulating L1 just finished — engine reports levels_completed=1
            # while still NOT_FINISHED because L2..L6 remain.
            FakeObs(mid_grid, GameState.NOT_FINISHED, levels_completed=1),
        ])
        session = GameSession(env)
        session.reset()
        assert session.levels_completed == 0
        session.step("ACTION1")
        assert session.levels_completed == 1, (
            "session should mirror obs.levels_completed even when state is "
            "still NOT_FINISHED — regression test for r11l L1-advance bug"
        )
