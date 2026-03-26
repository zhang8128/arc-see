from dataclasses import dataclass, field
import numpy as np


@dataclass
class Transition:
    state_vec: np.ndarray
    action: str
    next_state_vec: np.ndarray
    state_changed: bool
    goal_delta: float
    active_lenses: list[tuple[str, ...]]
    turn: int


@dataclass
class QueryResult:
    action: str
    score: float
    state_changed: bool
    goal_delta: float
    similarity: float


class MemoryGraph:
    def __init__(self, similarity_threshold=0.7, confidence_threshold=5):
        self._transitions: list[Transition] = []
        self._turn = 0
        self._similarity_threshold = similarity_threshold
        self._confidence_threshold = confidence_threshold

    @property
    def size(self) -> int:
        return len(self._transitions)

    def record(self, state_vec, action, next_state_vec, state_changed, goal_delta, active_lenses):
        self._transitions.append(Transition(
            state_vec=state_vec,
            action=action,
            next_state_vec=next_state_vec,
            state_changed=state_changed,
            goal_delta=goal_delta,
            active_lenses=list(active_lenses),
            turn=self._turn,
        ))
        self._turn += 1

    def query(self, state_vec, max_results=10) -> list[QueryResult]:
        if not self._transitions:
            return []

        max_turn = max(t.turn for t in self._transitions) if self._transitions else 1
        if max_turn == 0:
            max_turn = 1

        results = []
        for t in self._transitions:
            sim = self._cosine_similarity(state_vec, t.state_vec)
            if sim < self._similarity_threshold:
                continue
            novelty = 1.0 if t.state_changed else 0.0
            recency = t.turn / max_turn
            score = t.goal_delta * 3.0 + novelty * 2.0 + recency * 0.5 + sim * 0.5
            results.append(QueryResult(
                action=t.action,
                score=score,
                state_changed=t.state_changed,
                goal_delta=t.goal_delta,
                similarity=sim,
            ))

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:max_results]

    def confidence(self, state_vec) -> float:
        if not self._transitions:
            return 0.0
        count = sum(
            1 for t in self._transitions
            if self._cosine_similarity(state_vec, t.state_vec) >= self._similarity_threshold
        )
        return min(count / self._confidence_threshold, 1.0)

    def _cosine_similarity(self, a, b) -> float:
        norm_a = float(np.linalg.norm(a))
        norm_b = float(np.linalg.norm(b))
        if norm_a == 0.0 and norm_b == 0.0:
            return 1.0
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))
