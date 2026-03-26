import numpy as np
from arc_see.agent import Agent


class TestAgent:
    def test_creation(self):
        agent = Agent()
        assert agent is not None

    def test_observe(self):
        grid = np.zeros((64, 64), dtype=np.int64)
        grid[10:14, 10:14] = 1
        agent = Agent()
        agent.observe(grid)
        assert len(agent.history) == 1

    def test_perceive(self):
        grid = np.zeros((64, 64), dtype=np.int64)
        grid[10:14, 10:14] = 1
        agent = Agent()
        agent.observe(grid)
        annotations = agent.perceive()
        assert "connected_components" in annotations
        assert "edges" in annotations

    def test_select_action_cold_start(self):
        grid = np.zeros((64, 64), dtype=np.int64)
        grid[10:14, 10:14] = 1
        agent = Agent()
        agent.observe(grid)
        agent.perceive()
        action, data = agent.select_action(
            available_actions=["ACTION1", "ACTION2", "ACTION3", "ACTION4", "ACTION5"]
        )
        assert action in ["ACTION1", "ACTION2", "ACTION3", "ACTION4", "ACTION5"]

    def test_record_updates_graph(self):
        grid1 = np.zeros((64, 64), dtype=np.int64)
        grid1[10:14, 10:14] = 1
        grid2 = np.zeros((64, 64), dtype=np.int64)
        grid2[10:14, 12:16] = 1

        agent = Agent()
        agent.observe(grid1)
        agent.perceive()
        agent.observe(grid2)
        agent.perceive()
        agent.record("ACTION1", {})
        assert agent.graph.size == 1

    def test_full_loop(self):
        """Run 5 turns of observe → perceive → select → record."""
        frames = []
        for i in range(6):
            grid = np.zeros((64, 64), dtype=np.int64)
            grid[10:14, 10+i:14+i] = 1
            frames.append(grid)

        agent = Agent()
        actions = ["ACTION1", "ACTION2", "ACTION3", "ACTION4", "ACTION5"]

        for i in range(5):
            agent.observe(frames[i])
            agent.perceive()
            action, data = agent.select_action(actions)
            agent.observe(frames[i+1])
            agent.perceive()
            agent.record(action, data)

        assert agent.graph.size == 5
        assert len(agent.history) == 10  # 2 observations per step
