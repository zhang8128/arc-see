"""Mechanics lens: infer game rules from player-environment interactions.

Tracks what happens when the player contacts different colored cells:
- Pickups: cells that disappear when the player moves over them
- Blocking: colors the player can't move through
- Remaining collectables and their positions

This lens is stateful — it accumulates observations across turns.
"""

from __future__ import annotations

import numpy as np

from arc_see.lenses import MechanicsMap, InteractionEvent, register


class _Mechanics:
    """Infer game mechanics from frame-to-frame player interactions.

    Unlike other lenses (pure functions), this one is stateful:
    it accumulates interaction history across turns to build
    a mechanics model.
    """
    name = "mechanics"

    def __init__(self):
        self._collected: list[InteractionEvent] = []
        self._collectable_colors: set[int] = set()
        self._blocking_colors: set[int] = set()
        self._player_color: int | None = None
        self._turn: int = 0

    def reset(self):
        """Clear interaction history (call on level reset)."""
        self._collected = []
        self._collectable_colors = set()
        self._blocking_colors = set()
        self._turn = 0
        # Keep player_color across resets — it's usually consistent

    def __call__(self, current: np.ndarray, history: list[np.ndarray]) -> MechanicsMap:
        self._turn += 1

        if not history:
            return self._build_result(current)

        prev = history[-1]

        # Find player: the smallest non-background object that moved
        player_color, player_pos = self._find_player(prev, current)
        if player_color is not None:
            self._player_color = player_color

        # Detect pickups: cells that existed in prev but disappeared in current,
        # AND the player is now at or near that position
        if player_pos is not None and self._player_color is not None:
            self._detect_pickups(prev, current, player_pos)
            self._detect_blocking(prev, current, player_pos)

        return self._build_result(current)

    def _find_player(
        self, prev: np.ndarray, curr: np.ndarray
    ) -> tuple[int | None, tuple[int, int] | None]:
        """Find the player: smallest moved non-background color."""
        if self._player_color is not None:
            # Already know the player — just find current position
            positions = np.argwhere(curr == self._player_color)
            if len(positions) > 0:
                center = (int(positions[:, 0].mean()), int(positions[:, 1].mean()))
                return self._player_color, center
            return self._player_color, None

        # Discover player: find colors that moved, pick smallest
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

        # Player is the smallest moving object
        moved.sort(key=lambda x: x[1])
        color, _, center = moved[0]
        return color, (int(center[0]), int(center[1]))

    def _detect_pickups(
        self,
        prev: np.ndarray,
        curr: np.ndarray,
        player_pos: tuple[int, int],
    ) -> None:
        """Detect cells that disappeared when the player moved over them."""
        py, px = player_pos

        # Check a region around the player position
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

                # Cell had a color before, now it's either background or player
                if prev_color != curr_color and (curr_color == 0 or curr_color == self._player_color):
                    self._collectable_colors.add(prev_color)
                    self._collected.append(InteractionEvent(
                        position=(y, x),
                        color=prev_color,
                        event_type="pickup",
                        turn=self._turn,
                    ))

    def _detect_blocking(
        self,
        prev: np.ndarray,
        curr: np.ndarray,
        player_pos: tuple[int, int],
    ) -> None:
        """Detect colors that the player repeatedly fails to move through.

        Heuristic: if the player is adjacent to a color and hasn't moved
        into it across multiple attempts, it's probably blocking.
        """
        # This is a simple version — check if player is adjacent to a
        # non-background, non-collectable color that takes up lots of space
        py, px = player_pos
        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ny, nx = py + dy, px + dx
            if 0 <= ny < 64 and 0 <= nx < 64:
                color = int(curr[ny, nx])
                if color == 0 or color == self._player_color:
                    continue
                if color in self._collectable_colors:
                    continue
                # Large color regions are likely walls
                pixel_count = int((curr == color).sum())
                if pixel_count > 200:  # >~5% of grid
                    self._blocking_colors.add(color)

    def _build_result(self, grid: np.ndarray) -> MechanicsMap:
        """Build the current mechanics map from accumulated observations."""
        # Find remaining collectables on the grid
        collectables: dict[int, list[tuple[int, int]]] = {}
        for color in self._collectable_colors:
            positions = np.argwhere(grid == color)
            if len(positions) > 0:
                collectables[color] = [(int(p[0]), int(p[1])) for p in positions]

        # Player position
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
        )


mechanics = _Mechanics()
register(mechanics)
