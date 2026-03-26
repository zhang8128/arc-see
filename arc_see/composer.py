"""Composer — orchestrates all lenses and scores pairwise combinations."""

from __future__ import annotations

import inspect
from itertools import combinations

import numpy as np

from arc_see.lenses import (
    Annotation,
    RegionLabels,
    EdgeMask,
    ContainmentTree,
    DisplacementField,
    ChangeMask,
    StateChangeMask,
    SymmetryResult,
    PeriodicityResult,
    AlignmentResult,
    ProximityGraph,
    ColorCorrespondence,
    SizeCount,
    GoalDetection,
    get_all,
)

# Ensure all lens modules are imported so they register themselves
import arc_see.lenses.spatial      # noqa: F401
import arc_see.lenses.temporal     # noqa: F401
import arc_see.lenses.structural   # noqa: F401
import arc_see.lenses.relational   # noqa: F401
import arc_see.lenses.goal         # noqa: F401


class Composer:
    """Orchestrates all lenses and scores pairwise combinations."""

    def perceive(
        self,
        grid: np.ndarray,
        history: list[np.ndarray],
    ) -> dict[str, Annotation]:
        """Run all registered lenses in dependency order.

        Phase 1: Independent lenses (single grid input, no depends_on).
        Phase 2: Temporal lenses (no depends_on, take current + history).
        Phase 3: Dependent lenses (have depends_on attribute).
        """
        lenses = get_all()
        annotations: dict[str, Annotation] = {}

        # Phase 1 & 2: lenses without depends_on
        for name, lens in lenses.items():
            if hasattr(lens, "depends_on"):
                continue

            sig = inspect.signature(lens.__call__)
            params = list(sig.parameters.keys())
            # params[0] is 'self' for bound methods, skip it
            # For callables, __call__ includes 'self'
            # Remove 'self' if present
            call_params = [p for p in params if p != "self"]

            if len(call_params) >= 2:
                # Temporal lens: __call__(current, history)
                annotations[name] = lens(grid, history)
            else:
                # Independent lens: __call__(grid)
                annotations[name] = lens(grid)

        # Phase 3: Dependent lenses
        for name, lens in lenses.items():
            if not hasattr(lens, "depends_on"):
                continue

            dep_name: str = lens.depends_on
            dep_output = annotations.get(dep_name)
            if dep_output is None:
                continue

            sig = inspect.signature(lens.__call__)
            params = [p for p in sig.parameters.keys() if p != "self"]

            # Check if lens needs history (movement lens: current, history, dependency)
            if "history" in params:
                annotations[name] = lens(grid, history, dep_output)
            else:
                annotations[name] = lens(grid, dep_output)

        return annotations

    def score_combinations(
        self,
        annotations: dict[str, Annotation],
    ) -> list[tuple[float, tuple[str, str]]]:
        """Score all pairwise annotation combinations by mutual information heuristics."""
        names = list(annotations.keys())
        scored: list[tuple[float, tuple[str, str]]] = []

        for a_name, b_name in combinations(names, 2):
            a = annotations[a_name]
            b = annotations[b_name]
            score = self._score_pair(a_name, a, b_name, b)
            scored.append((score, (a_name, b_name)))

        scored.sort(key=lambda x: x[0], reverse=True)
        return scored

    def top_k(
        self,
        annotations: dict[str, Annotation],
        k: int = 5,
    ) -> list[tuple[float, tuple[str, str]]]:
        """Return the top-k scoring annotation pairs."""
        return self.score_combinations(annotations)[:k]

    # ------------------------------------------------------------------
    # Scoring helpers
    # ------------------------------------------------------------------

    def _score_pair(
        self,
        a_name: str,
        a: Annotation,
        b_name: str,
        b: Annotation,
    ) -> float:
        """Score a pair of annotations by mutual information heuristics."""
        # Ensure (a, b) order is canonical for isinstance checks
        # Try both orderings

        score = self._score_ordered(a, b)
        if score is None:
            score = self._score_ordered(b, a)
        if score is None:
            # Default: both have content → 0.1, else 0.0
            score = 0.1 if (self._has_content(a) and self._has_content(b)) else 0.0

        return score

    def _score_ordered(
        self,
        a: Annotation,
        b: Annotation,
    ) -> float | None:
        """Score a specific ordered pair. Returns None if no rule matches."""

        # RegionLabels + ColorCorrespondence: 1:1 color→region = high MI
        if isinstance(a, RegionLabels) and isinstance(b, ColorCorrespondence):
            total = a.count
            if total == 0:
                return 0.0
            # Perfect 1:1: each color maps to exactly one object
            perfect = all(len(objs) == 1 for objs in b.color_to_objects.values())
            ratio = len(b.color_to_objects) / max(total, 1)
            return (1.0 if perfect else 0.5) * ratio

        # RegionLabels + ProximityGraph: low variance in distances = regular spacing
        if isinstance(a, RegionLabels) and isinstance(b, ProximityGraph):
            if not b.distances:
                return 0.0
            dists = list(b.distances.values())
            if len(dists) < 2:
                return 0.5
            mean = float(np.mean(dists))
            std = float(np.std(dists))
            if mean == 0:
                return 0.0
            cv = std / mean
            return float(max(0.0, 1.0 - cv))

        # RegionLabels + SizeCount: uniform sizes = structure
        if isinstance(a, RegionLabels) and isinstance(b, SizeCount):
            total = a.count
            if total == 0:
                return 0.0
            max_count = max(b.count_by_size.values(), default=0)
            return max_count / total

        # SymmetryResult + AlignmentResult: both = highly structured
        if isinstance(a, SymmetryResult) and isinstance(b, AlignmentResult):
            sym_score = (
                (1.0 if a.horizontal else 0.0)
                + (1.0 if a.vertical else 0.0)
                + (0.5 if a.rotational_order > 0 else 0.0)
            ) / 2.5
            align_score = 1.0 if (b.row_lines or b.col_lines) else 0.0
            return sym_score * align_score

        # DisplacementField + GoalDetection: movement toward goal
        if isinstance(a, DisplacementField) and isinstance(b, GoalDetection):
            if not a.vectors or not b.goals:
                return 0.0
            return b.best_similarity * 0.8

        # EdgeMask + ContainmentTree: edges that form containment
        if isinstance(a, EdgeMask) and isinstance(b, ContainmentTree):
            total = len(b.parent)
            if total == 0:
                return 0.0
            n_nested = sum(1 for par in b.parent.values() if par is not None)
            return n_nested / total

        return None

    def _has_content(self, annotation: Annotation) -> bool:
        """Check if an annotation found anything non-trivial."""
        if isinstance(annotation, RegionLabels):
            return annotation.count > 0
        if isinstance(annotation, EdgeMask):
            return bool(annotation.mask.any())
        if isinstance(annotation, ContainmentTree):
            return len(annotation.parent) > 0
        if isinstance(annotation, DisplacementField):
            return len(annotation.vectors) > 0
        if isinstance(annotation, ChangeMask):
            return bool(annotation.appeared.any() or annotation.disappeared.any())
        if isinstance(annotation, StateChangeMask):
            return bool(annotation.mask.any())
        if isinstance(annotation, SymmetryResult):
            return annotation.horizontal or annotation.vertical or annotation.rotational_order > 0
        if isinstance(annotation, PeriodicityResult):
            return annotation.row_period is not None or annotation.col_period is not None
        if isinstance(annotation, AlignmentResult):
            return len(annotation.row_lines) > 0 or len(annotation.col_lines) > 0
        if isinstance(annotation, ProximityGraph):
            return len(annotation.distances) > 0
        if isinstance(annotation, ColorCorrespondence):
            return len(annotation.color_to_objects) > 0
        if isinstance(annotation, SizeCount):
            return len(annotation.sizes) > 0
        if isinstance(annotation, GoalDetection):
            return len(annotation.goals) > 0
        return False
