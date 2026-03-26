"""Integration test: full pipeline on synthetic grids."""

import numpy as np
from arc_see.agent import Agent


class TestIntegration:
    def test_full_pipeline_static(self):
        """Run full pipeline on a single frame — no temporal data."""
        grid = np.zeros((64, 64), dtype=np.int64)
        grid[10:20, 10:20] = 1       # outer box
        grid[13:17, 13:17] = 2       # inner box
        grid[40:44, 40:44] = 1       # separate block, same color as outer

        agent = Agent()
        agent.observe(grid)
        annotations = agent.perceive()

        # Spatial lenses found things
        assert annotations["connected_components"].count == 3
        assert annotations["edges"].mask.any()

        # Structural lenses ran
        assert "symmetry" in annotations
        assert "periodicity" in annotations
        assert "alignment" in annotations

        # Relational lenses ran
        assert "proximity" in annotations
        assert "color_correspondence" in annotations
        assert "size_count" in annotations

        # Composer can score combinations
        top = agent.composer.top_k(annotations, k=5)
        assert len(top) > 0

        # Agent can select an action
        action, data = agent.select_action(
            ["ACTION1", "ACTION2", "ACTION3", "ACTION4", "ACTION5"]
        )
        assert action in ["ACTION1", "ACTION2", "ACTION3", "ACTION4", "ACTION5"]

    def test_full_pipeline_temporal(self):
        """Run full pipeline with frame history."""
        frames = []
        for i in range(5):
            grid = np.zeros((64, 64), dtype=np.int64)
            grid[10:14, 10+i*2:14+i*2] = 1   # block moves right
            grid[0:2, 62:64] = 3               # goal in corner
            frames.append(grid)

        agent = Agent()
        for i, frame in enumerate(frames):
            agent.observe(frame)
            annotations = agent.perceive()
            if i > 0:
                action, data = agent.select_action(
                    ["ACTION1", "ACTION2", "ACTION3", "ACTION4", "ACTION5"]
                )
                agent.observe(frames[min(i+1, len(frames)-1)] if i+1 < len(frames) else frame)
                agent.perceive()
                agent.record(action, data)

        # After transitions, graph should have data
        assert agent.graph.size >= 1

        # Temporal lenses should have detected movement
        assert "movement" in annotations
        assert "creation_destruction" in annotations

        # Goal lens should have found the corner pattern
        goal = annotations.get("goal")
        if goal and len(goal.goals) > 0:
            found_corner = any(g.location[0] < 10 for g in goal.goals)
            assert found_corner

    def test_vectorization_consistency(self):
        """Same grid should produce same vector."""
        grid = np.zeros((64, 64), dtype=np.int64)
        grid[10:14, 10:14] = 1

        agent = Agent()
        agent.observe(grid)
        ann = agent.perceive()
        vec1 = agent._vectorize(ann)

        agent2 = Agent()
        agent2.observe(grid.copy())
        ann2 = agent2.perceive()
        vec2 = agent2._vectorize(ann2)

        np.testing.assert_array_equal(vec1, vec2)
