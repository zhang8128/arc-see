import numpy as np
from arc_see.graph import MemoryGraph


class TestMemoryGraph:
    def test_record_transition(self):
        graph = MemoryGraph()
        state_vec = np.random.rand(20).astype(np.float32)
        next_vec = np.random.rand(20).astype(np.float32)
        graph.record(
            state_vec=state_vec,
            action="ACTION1",
            next_state_vec=next_vec,
            state_changed=True,
            goal_delta=0.1,
            active_lenses=[("edges", "connected_components")],
        )
        assert graph.size == 1

    def test_query_empty(self):
        graph = MemoryGraph()
        state_vec = np.random.rand(20).astype(np.float32)
        results = graph.query(state_vec)
        assert results == []

    def test_query_returns_similar(self):
        graph = MemoryGraph()
        state_vec = np.array([1.0, 0.0, 0.0, 0.0, 0.0], dtype=np.float32)
        next_vec = np.array([0.0, 1.0, 0.0, 0.0, 0.0], dtype=np.float32)
        graph.record(
            state_vec=state_vec, action="ACTION1", next_state_vec=next_vec,
            state_changed=True, goal_delta=0.0, active_lenses=[],
        )
        query = np.array([0.9, 0.1, 0.0, 0.0, 0.0], dtype=np.float32)
        results = graph.query(query)
        assert len(results) == 1
        assert results[0].action == "ACTION1"

    def test_query_ranks_by_goal_progress(self):
        graph = MemoryGraph()
        base = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        graph.record(base, "ACTION1", base, True, goal_delta=0.5, active_lenses=[])
        graph.record(base, "ACTION2", base, True, goal_delta=0.1, active_lenses=[])
        results = graph.query(base)
        assert len(results) == 2
        assert results[0].action == "ACTION1"

    def test_query_prefers_novelty(self):
        graph = MemoryGraph()
        base = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        same = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        diff = np.array([0.0, 0.0, 1.0], dtype=np.float32)
        graph.record(base, "ACTION1", same, False, goal_delta=0.0, active_lenses=[])
        graph.record(base, "ACTION2", diff, True, goal_delta=0.0, active_lenses=[])
        results = graph.query(base)
        assert results[0].action == "ACTION2"

    def test_confidence(self):
        graph = MemoryGraph()
        assert graph.confidence(np.zeros(5, dtype=np.float32)) == 0.0
        base = np.zeros(5, dtype=np.float32)
        graph.record(base, "ACTION1", base, True, 0.0, [])
        assert graph.confidence(base) > 0.0
