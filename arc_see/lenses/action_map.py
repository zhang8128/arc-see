"""Action map lens: learn what each action does by observing outcomes.

Tracks per-action statistics: what typically happens when you press each button.
After a few observations per action, builds a reliable action→effect map.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

import numpy as np

from arc_see.lenses import register


@dataclass(frozen=True)
class ActionEffect:
    """Observed effect of a single action."""
    direction: tuple[int, int] | None  # (dy, dx) player moved, or None if no movement
    cells_changed: int                  # how many cells changed
    blocked: bool                       # player didn't move


@dataclass(frozen=True)
class ActionMap:
    """What each action does, learned from observation."""
    effects: dict[str, list[ActionEffect]]   # action_name → observed effects
    summary: dict[str, str]                  # action_name → human-readable summary


class _ActionMapLens:
    """Stateful lens: accumulates action→outcome observations across turns."""
    name = "action_map"

    def __init__(self):
        self._effects: dict[str, list[ActionEffect]] = defaultdict(list)
        self._last_action: str | None = None
        self._player_color: int | None = None

    def reset(self):
        self._effects = defaultdict(list)
        self._last_action = None
        self._player_color = None

    def record_action(self, action: str):
        """Called by session before step() to record which action is being taken."""
        self._last_action = action

    def set_player_color(self, color: int):
        self._player_color = color

    def __call__(self, current: np.ndarray, history: list[np.ndarray]) -> ActionMap:
        if history and self._last_action is not None:
            prev = history[-1]
            effect = self._observe(prev, current)
            self._effects[self._last_action].append(effect)
            self._last_action = None

        return ActionMap(
            effects=dict(self._effects),
            summary=self._summarize(),
        )

    def _observe(self, prev: np.ndarray, curr: np.ndarray) -> ActionEffect:
        """Observe what happened between two frames."""
        cells_changed = int(np.sum(prev != curr))

        # Track player movement
        direction = None
        blocked = True
        if self._player_color is not None:
            prev_pos = np.argwhere(prev == self._player_color)
            curr_pos = np.argwhere(curr == self._player_color)
            if len(prev_pos) > 0 and len(curr_pos) > 0:
                prev_center = prev_pos.mean(axis=0)
                curr_center = curr_pos.mean(axis=0)
                dy = int(round(curr_center[0] - prev_center[0]))
                dx = int(round(curr_center[1] - prev_center[1]))
                if dy != 0 or dx != 0:
                    direction = (dy, dx)
                    blocked = False

        return ActionEffect(
            direction=direction,
            cells_changed=cells_changed,
            blocked=blocked,
        )

    def _summarize(self) -> dict[str, str]:
        """Build human-readable summary of each action."""
        summary = {}
        for action, effects in self._effects.items():
            if not effects:
                continue

            # Most common direction
            directions = [e.direction for e in effects if e.direction is not None]
            blocked_count = sum(1 for e in effects if e.blocked)
            total = len(effects)

            if directions:
                # Find most common direction
                dir_counts: dict[tuple[int, int], int] = defaultdict(int)
                for d in directions:
                    dir_counts[d] += 1
                most_common = max(dir_counts, key=dir_counts.get)
                dy, dx = most_common
                dir_name = self._direction_name(dy, dx)
                reliability = dir_counts[most_common] / total
                blocked_pct = blocked_count / total

                parts = [f"moves {dir_name}"]
                if reliability < 1.0:
                    parts.append(f"({reliability:.0%} of the time)")
                if blocked_pct > 0:
                    parts.append(f"blocked {blocked_pct:.0%}")
                summary[action] = ", ".join(parts)
            elif blocked_count == total:
                summary[action] = "no visible effect"
            else:
                summary[action] = f"unclear ({total} observations)"

        return summary

    @staticmethod
    def _direction_name(dy: int, dx: int) -> str:
        parts = []
        if dy < 0:
            parts.append("up")
        elif dy > 0:
            parts.append("down")
        if dx < 0:
            parts.append("left")
        elif dx > 0:
            parts.append("right")
        return "+".join(parts) if parts else "nowhere"


action_map_lens = _ActionMapLens()
register(action_map_lens)
