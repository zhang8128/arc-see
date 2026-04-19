"""Resource lens: track quantities that change over time.

Detects counters, timers, inventories — anything where a cell count
changes monotonically or in response to actions. These are the rules
talking to you through the frame.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from arc_see.lenses import register


@dataclass(frozen=True)
class ResourceTracker:
    """Tracked resources — colors whose cell counts change meaningfully."""
    counts: dict[int, int]                    # color → current cell count
    deltas: dict[int, list[int]]              # color → recent count changes
    trends: dict[int, str]                    # color → "increasing", "decreasing", "stable", "fluctuating"
    possible_counters: list[int]              # colors that look like counters (small, monotonic change)


class _ResourceLens:
    """Stateful lens: tracks cell count per color over time."""
    name = "resources"

    def __init__(self):
        self._history: list[dict[int, int]] = []  # census per frame
        self._max_history = 20

    def reset(self):
        self._history = []

    def __call__(self, current: np.ndarray, history: list[np.ndarray]) -> ResourceTracker:
        census = self._census(current)
        self._history.append(census)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

        # Build deltas for each color
        all_colors = set()
        for h in self._history:
            all_colors.update(h.keys())
        all_colors.discard(0)  # ignore background

        deltas: dict[int, list[int]] = {}
        trends: dict[int, str] = {}
        possible_counters: list[int] = []

        for color in sorted(all_colors):
            color_counts = [h.get(color, 0) for h in self._history]
            if len(color_counts) < 2:
                continue

            # Compute deltas
            d = [color_counts[i] - color_counts[i - 1] for i in range(1, len(color_counts))]
            deltas[color] = d[-5:]  # last 5 deltas

            # Classify trend
            nonzero = [x for x in d if x != 0]
            if not nonzero:
                trends[color] = "stable"
            elif all(x > 0 for x in nonzero):
                trends[color] = "increasing"
            elif all(x < 0 for x in nonzero):
                trends[color] = "decreasing"
            else:
                trends[color] = "fluctuating"

            # Possible counter: small total count, changes by consistent amount
            current_count = census.get(color, 0)
            if current_count <= 50 and len(nonzero) >= 2:
                # Check if changes are consistent (same delta each time)
                steps = [abs(x) for x in nonzero]
                if len(set(steps)) <= 2:  # at most 2 different step sizes
                    possible_counters.append(color)

        return ResourceTracker(
            counts={c: n for c, n in census.items() if c != 0},
            deltas=deltas,
            trends=trends,
            possible_counters=possible_counters,
        )

    @staticmethod
    def _census(grid: np.ndarray) -> dict[int, int]:
        unique, counts = np.unique(grid, return_counts=True)
        return {int(c): int(n) for c, n in zip(unique, counts)}


resource_lens = _ResourceLens()
register(resource_lens)
