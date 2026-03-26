"""Test MCP server tools via direct invocation."""

import numpy as np
import pytest
from unittest.mock import MagicMock
from arcengine import GameAction, GameState


class FakeObs:
    def __init__(self, frame, state=GameState.NOT_FINISHED):
        self.frame = [frame]
        self.state = state


def make_grid():
    grid = np.full((64, 64), 4, dtype=np.int64)
    grid[10:50, 10:50] = 3
    grid[40:42, 30:32] = 12
    grid[20:21, 20:21] = 1
    return grid


def make_moved_grid():
    grid = make_grid()
    grid[40:42, 30:32] = 3
    grid[35:37, 30:32] = 12
    return grid


@pytest.fixture
def mock_session(monkeypatch):
    """Patch the global _session in mcp_server with a real GameSession using a mock env."""
    from arc_see.session import GameSession
    import arc_see.mcp_server as server

    grid = make_grid()
    moved = make_moved_grid()

    env = MagicMock()
    env.action_space = [GameAction.ACTION1, GameAction.ACTION2,
                        GameAction.ACTION3, GameAction.ACTION4]
    env.environment_info = MagicMock()
    env.environment_info.game_id = "test-game"
    env.environment_info.title = "TEST"
    env.environment_info.tags = ["keyboard"]
    env.environment_info.baseline_actions = [20]

    env.reset.return_value = FakeObs(grid)
    env.step.return_value = FakeObs(moved)

    session = GameSession(env)
    monkeypatch.setattr(server, "_session", session)
    return session


class TestMCPTools:
    def test_reset(self, mock_session):
        from arc_see.mcp_server import reset
        result = reset()
        assert "Spatial" in result

    def test_perceive(self, mock_session):
        from arc_see.mcp_server import reset, perceive
        reset()
        result = perceive()
        assert "Spatial" in result
        assert "Grid" in result

    def test_step(self, mock_session):
        from arc_see.mcp_server import reset, step
        reset()
        result = step("ACTION1")
        assert "ACTION1" in result

    def test_reflect(self, mock_session):
        from arc_see.mcp_server import reset, step, reflect
        reset()
        step("ACTION1")
        result = reflect()
        assert "ACTION1" in result

    def test_status(self, mock_session):
        from arc_see.mcp_server import reset, status
        reset()
        result = status()
        assert "test-game" in result.lower() or "TEST" in result
