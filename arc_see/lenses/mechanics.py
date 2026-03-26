"""Mechanics lens: infer game rules from player-environment interactions.

Tracks what happens when the player contacts different colored cells:
- Pickups: cells that disappear when the player moves over them
- Blocking: colors the player can't move through
- Remaining collectables and their positions
- Causal hypotheses: what EFFECT did each pickup have on the game state?

This lens is stateful — it accumulates observations across turns.
"""

from __future__ import annotations

from collections import defaultdict

import numpy as np

from arc_see.lenses import MechanicsMap, InteractionEvent, CausalHypothesis, register


class _Mechanics:
    """Infer game mechanics from frame-to-frame player interactions.

    Unlike other lenses (pure functions), this one is stateful:
    it accumulates interaction history across turns to build
    a mechanics model, including causal hypotheses about what
    interactions DO (not just that they happened).
    """
    name = "mechanics"

    def __init__(self):
        self._collected: list[InteractionEvent] = []
        self._collectable_colors: set[int] = set()
        self._blocking_colors: set[int] = set()
        self._player_color: int | None = None
        self._turn: int = 0
        # Consequence tracking
        self._color_census_before: dict[int, int] = {}  # color -> pixel count before step
        self._pending_pickup_color: int | None = None     # color of pickup from previous frame
        # Hypothesis accumulation: (trigger_color, effect_description) -> count
        self._effect_counts: dict[tuple[int, str], int] = defaultdict(int)
        self._trigger_counts: dict[int, int] = defaultdict(int)  # how many times each color was collected

    def reset(self):
        """Clear interaction history (call on level reset)."""
        self._collected = []
        self._collectable_colors = set()
        self._blocking_colors = set()
        self._turn = 0
        self._color_census_before = {}
        self._pending_pickup_color = None
        self._effect_counts = defaultdict(int)
        self._trigger_counts = defaultdict(int)
        # Keep player_color across resets — it's usually consistent

    def __call__(self, current: np.ndarray, history: list[np.ndarray]) -> MechanicsMap:
        self._turn += 1

        if not history:
            self._color_census_before = self._census(current)
            return self._build_result(current)

        prev = history[-1]

        # Check consequences of PREVIOUS pickup (comparing prev→current)
        if self._pending_pickup_color is not None:
            self._analyze_consequences(prev, current, self._pending_pickup_color)
            self._pending_pickup_color = None

        # Find player
        player_color, player_pos = self._find_player(prev, current)
        if player_color is not None:
            self._player_color = player_color

        # Detect new pickups and blocking
        if player_pos is not None and self._player_color is not None:
            new_pickups = self._detect_pickups(prev, current, player_pos)
            self._detect_blocking(prev, current, player_pos)

            # If we collected something this turn, flag it for consequence
            # analysis on the NEXT call (consequences may be delayed one frame)
            if new_pickups:
                self._pending_pickup_color = new_pickups[0]

        # Snapshot current census for next comparison
        self._color_census_before = self._census(current)

        return self._build_result(current)

    def _census(self, grid: np.ndarray) -> dict[int, int]:
        """Count pixels per color."""
        unique, counts = np.unique(grid, return_counts=True)
        return {int(c): int(n) for c, n in zip(unique, counts)}

    def _analyze_consequences(
        self, prev: np.ndarray, curr: np.ndarray, trigger_color: int
    ) -> None:
        """Compare game state before/after a pickup to infer what it did.

        Looks for:
        - New cells appearing (new color or more pixels of existing color)
        - Cells disappearing (a barrier removed?)
        - Color changes (state transitions)
        - No visible change (effect might be invisible — score, turns, etc.)
        """
        self._trigger_counts[trigger_color] += 1

        prev_census = self._census(prev)
        curr_census = self._census(curr)
        effects_found = False

        # Check each color for changes
        all_colors = set(prev_census.keys()) | set(curr_census.keys())
        for color in all_colors:
            if color == 0:
                continue
            if color == self._player_color:
                continue
            if color == trigger_color:
                continue  # the pickup itself disappearing isn't a consequence

            prev_count = prev_census.get(color, 0)
            curr_count = curr_census.get(color, 0)
            delta = curr_count - prev_count

            if delta > 5:  # significant appearance
                effect = f"cells_appeared:{color}(+{delta})"
                self._effect_counts[(trigger_color, effect)] += 1
                effects_found = True
            elif delta < -5:  # significant disappearance
                effect = f"cells_removed:{color}({delta})"
                self._effect_counts[(trigger_color, effect)] += 1
                effects_found = True

        # Check if new colors appeared that weren't there before
        new_colors = set(curr_census.keys()) - set(prev_census.keys()) - {0}
        for nc in new_colors:
            if curr_census[nc] > 3:
                effect = f"new_color_appeared:{nc}"
                self._effect_counts[(trigger_color, effect)] += 1
                effects_found = True

        # Check if colors disappeared entirely
        gone_colors = set(prev_census.keys()) - set(curr_census.keys()) - {0}
        for gc in gone_colors:
            if gc != trigger_color:
                effect = f"color_gone:{gc}"
                self._effect_counts[(trigger_color, effect)] += 1
                effects_found = True

        if not effects_found:
            # No visible change — effect is invisible (turns? score? internal state?)
            self._effect_counts[(trigger_color, "no_visible_change")] += 1

    def _find_player(
        self, prev: np.ndarray, curr: np.ndarray
    ) -> tuple[int | None, tuple[int, int] | None]:
        """Find the player: smallest moved non-background color."""
        if self._player_color is not None:
            positions = np.argwhere(curr == self._player_color)
            if len(positions) > 0:
                center = (int(positions[:, 0].mean()), int(positions[:, 1].mean()))
                return self._player_color, center
            return self._player_color, None

        moved = []
        for color in range(1, 16):
            prev_mask = prev == color
            curr_mask = curr == color
            if not prev_mask.any() or not curr_mask.any():
                continue
            prev_center = np.argwhere(prev_mask).mean(axis=0)
            curr_center = np.argwhere(curr_mask).mean(axis=0)
            dist = np.linalg.norm(curr_center - prev_center)
            if dist > 0.5:
                pixel_count = int(curr_mask.sum())
                moved.append((color, pixel_count, curr_center))

        if not moved:
            return None, None

        moved.sort(key=lambda x: x[1])
        color, _, center = moved[0]
        return color, (int(center[0]), int(center[1]))

    def _detect_pickups(
        self,
        prev: np.ndarray,
        curr: np.ndarray,
        player_pos: tuple[int, int],
    ) -> list[int]:
        """Detect cells that disappeared when the player moved over them.
        Returns list of collected colors this turn."""
        py, px = player_pos
        collected_colors: list[int] = []

        radius = 3
        y_min = max(0, py - radius)
        y_max = min(64, py + radius + 1)
        x_min = max(0, px - radius)
        x_max = min(64, px + radius + 1)

        for y in range(y_min, y_max):
            for x in range(x_min, x_max):
                prev_color = int(prev[y, x])
                curr_color = int(curr[y, x])

                if prev_color == 0 or prev_color == self._player_color:
                    continue

                if prev_color != curr_color and (curr_color == 0 or curr_color == self._player_color):
                    self._collectable_colors.add(prev_color)
                    self._collected.append(InteractionEvent(
                        position=(y, x),
                        color=prev_color,
                        event_type="pickup",
                        turn=self._turn,
                    ))
                    if prev_color not in collected_colors:
                        collected_colors.append(prev_color)

        return collected_colors

    def _detect_blocking(
        self,
        prev: np.ndarray,
        curr: np.ndarray,
        player_pos: tuple[int, int],
    ) -> None:
        """Detect colors that the player can't move through."""
        py, px = player_pos
        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ny, nx = py + dy, px + dx
            if 0 <= ny < 64 and 0 <= nx < 64:
                color = int(curr[ny, nx])
                if color == 0 or color == self._player_color:
                    continue
                if color in self._collectable_colors:
                    continue
                pixel_count = int((curr == color).sum())
                if pixel_count > 200:
                    self._blocking_colors.add(color)

    def _build_hypotheses(self) -> list[CausalHypothesis]:
        """Build causal hypotheses from accumulated effect observations."""
        hypotheses: list[CausalHypothesis] = []

        for (trigger_color, effect), count in self._effect_counts.items():
            total_triggers = self._trigger_counts.get(trigger_color, 1)
            confidence = count / total_triggers

            hypotheses.append(CausalHypothesis(
                trigger_color=trigger_color,
                trigger_type="pickup",
                effect=effect,
                observations=count,
                confidence=confidence,
            ))

        # Sort by confidence * observations (most reliable first)
        hypotheses.sort(key=lambda h: h.confidence * h.observations, reverse=True)
        return hypotheses

    def _build_result(self, grid: np.ndarray) -> MechanicsMap:
        """Build the current mechanics map from accumulated observations."""
        collectables: dict[int, list[tuple[int, int]]] = {}
        for color in self._collectable_colors:
            positions = np.argwhere(grid == color)
            if len(positions) > 0:
                collectables[color] = [(int(p[0]), int(p[1])) for p in positions]

        player_pos = None
        if self._player_color is not None:
            positions = np.argwhere(grid == self._player_color)
            if len(positions) > 0:
                player_pos = (int(positions[:, 0].mean()), int(positions[:, 1].mean()))

        return MechanicsMap(
            collectables=collectables,
            collected=list(self._collected),
            blocking_colors=frozenset(self._blocking_colors),
            total_collected=len(self._collected),
            player_color=self._player_color,
            player_position=player_pos,
            hypotheses=self._build_hypotheses(),
        )


mechanics = _Mechanics()
register(mechanics)
