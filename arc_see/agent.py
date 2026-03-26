"""Core agent loop: observe → perceive → consult → act → record."""

import numpy as np
import random

from arc_see.composer import Composer
from arc_see.graph import MemoryGraph
from arc_see.lenses import Annotation, RegionLabels, EdgeMask, GoalDetection


class Agent:
    def __init__(self):
        self.composer = Composer()
        self.graph = MemoryGraph()
        self.history: list[np.ndarray] = []          # all frames ever seen
        self._annotations: dict[str, Annotation] = {}      # current frame annotations
        self._prev_annotations: dict[str, Annotation] = {} # previous frame annotations
        self._exploration_actions = ["ACTION1", "ACTION2", "ACTION3", "ACTION4", "ACTION5"]
        self._exploration_idx = 0

    def observe(self, grid: np.ndarray) -> None:
        """Store a new frame."""
        self.history.append(grid.copy())

    def perceive(self) -> dict[str, Annotation]:
        """Run all lenses on current frame."""
        if not self.history:
            return {}
        self._prev_annotations = self._annotations
        self._annotations = self.composer.perceive(
            self.history[-1],
            self.history[:-1],   # all prior frames as history
        )
        return self._annotations

    def select_action(self, available_actions: list[str]) -> tuple[str, dict]:
        """Pick action based on graph confidence."""
        state_vec = self._vectorize(self._annotations)
        confidence = self.graph.confidence(state_vec)

        if confidence > 0.5:
            # Exploitation: ask the graph
            results = self.graph.query(state_vec, max_results=5)
            for r in results:
                if r.action in available_actions:
                    data = {}
                    if r.action == "ACTION6":
                        data = self._pick_click_target()
                    return r.action, data

        # Exploration: cycle simple actions, then structured clicks
        return self._explore(available_actions)

    def record(self, action: str, data: dict) -> None:
        """Record the transition in the memory graph."""
        if len(self.history) < 2:
            return
        prev_vec = self._vectorize(self._prev_annotations) if self._prev_annotations else np.zeros(1, dtype=np.float32)
        curr_vec = self._vectorize(self._annotations)
        prev_grid = self.history[-2]
        curr_grid = self.history[-1]
        state_changed = not np.array_equal(prev_grid, curr_grid)
        goal_delta = self._goal_delta()
        top = self.composer.top_k(self._annotations, k=3)
        active_lenses = [pair for _, pair in top]
        self.graph.record(
            state_vec=prev_vec, action=action, next_state_vec=curr_vec,
            state_changed=state_changed, goal_delta=goal_delta,
            active_lenses=active_lenses,
        )

    def _explore(self, available_actions: list[str]) -> tuple[str, dict]:
        """Cycle simple actions first, then structured clicks."""
        while self._exploration_idx < len(self._exploration_actions):
            action = self._exploration_actions[self._exploration_idx]
            self._exploration_idx += 1
            if action in available_actions:
                return action, {}
        if "ACTION6" in available_actions:
            return "ACTION6", self._pick_click_target()
        action = random.choice(available_actions)
        data = {"x": random.randint(0, 63), "y": random.randint(0, 63)} if action == "ACTION6" else {}
        return action, data

    def _pick_click_target(self) -> dict:
        """Pick click target based on edges or random."""
        edges = self._annotations.get("edges")
        if isinstance(edges, EdgeMask) and edges.mask.any():
            ys, xs = np.where(edges.mask)
            idx = random.randint(0, len(ys) - 1)
            return {"x": int(xs[idx]), "y": int(ys[idx])}
        return {"x": random.randint(0, 63), "y": random.randint(0, 63)}

    def _vectorize(self, annotations: dict[str, Annotation]) -> np.ndarray:
        """Convert annotations to fixed-size feature vector for graph lookups."""
        features: list[float] = []
        # Region count
        cc = annotations.get("connected_components")
        features.append(float(cc.count) if isinstance(cc, RegionLabels) else 0.0)
        # Edge density
        edges = annotations.get("edges")
        features.append(float(edges.mask.sum()) / (64*64) if isinstance(edges, EdgeMask) else 0.0)
        # Symmetry flags
        sym = annotations.get("symmetry")
        if sym and hasattr(sym, 'horizontal'):
            features.extend([float(sym.horizontal), float(sym.vertical), float(sym.rotational_order) / 4.0])
        else:
            features.extend([0.0, 0.0, 0.0])
        # Goal similarity (use best_similarity from multi-goal GoalDetection)
        goal = annotations.get("goal")
        if isinstance(goal, GoalDetection):
            features.append(goal.best_similarity)
        else:
            features.append(0.0)
        # Periodicity
        per = annotations.get("periodicity")
        if per and hasattr(per, 'row_period'):
            features.append(float(per.row_period or 0) / 64.0)
            features.append(float(per.col_period or 0) / 64.0)
        else:
            features.extend([0.0, 0.0])
        # Movement magnitude
        mov = annotations.get("movement")
        if mov and hasattr(mov, 'vectors') and mov.vectors:
            magnitudes = [(dy**2 + dx**2)**0.5 for dy, dx in mov.vectors.values()]
            features.append(float(np.mean(magnitudes)) / 64.0)
        else:
            features.append(0.0)
        # Change density
        change = annotations.get("creation_destruction")
        if change and hasattr(change, 'appeared'):
            features.append(float(change.appeared.sum() + change.disappeared.sum()) / (64*64))
        else:
            features.append(0.0)
        return np.array(features, dtype=np.float32)

    def _goal_delta(self) -> float:
        """How much did goal similarity change?"""
        prev_goal = self._prev_annotations.get("goal")
        curr_goal = self._annotations.get("goal")
        prev_sim = prev_goal.best_similarity if isinstance(prev_goal, GoalDetection) else 0.0
        curr_sim = curr_goal.best_similarity if isinstance(curr_goal, GoalDetection) else 0.0
        return curr_sim - prev_sim
