import numpy as np
from arc_see.lenses import Annotation
from arc_see.composer import Composer


class TestComposer:
    def test_run_all_lenses(self, two_blocks):
        composer = Composer()
        annotations = composer.perceive(two_blocks, history=[])
        assert len(annotations) > 0
        assert "connected_components" in annotations
        assert "edges" in annotations

    def test_score_combinations(self, two_blocks):
        composer = Composer()
        annotations = composer.perceive(two_blocks, history=[])
        scored = composer.score_combinations(annotations)
        assert len(scored) > 0
        for score, (a, b) in scored:
            assert isinstance(score, float)
            assert a != b

    def test_top_k(self, two_blocks):
        composer = Composer()
        annotations = composer.perceive(two_blocks, history=[])
        top = composer.top_k(annotations, k=5)
        assert len(top) <= 5
        scores = [s for s, _ in top]
        assert scores == sorted(scores, reverse=True)

    def test_perceive_with_history(self, moved_block):
        before, after = moved_block
        composer = Composer()
        annotations = composer.perceive(after, history=[before])
        assert "movement" in annotations
        assert "creation_destruction" in annotations
        assert "state_change" in annotations
