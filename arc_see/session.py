"""GameSession — state container with text-based perception/action."""

from __future__ import annotations

import numpy as np
from arcengine import GameAction, GameState

from arc_see.composer import Composer
from arc_see.lenses import (
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
    Annotation,
)

_ACTION_MAP = {
    "ACTION1": GameAction.ACTION1,
    "ACTION2": GameAction.ACTION2,
    "ACTION3": GameAction.ACTION3,
    "ACTION4": GameAction.ACTION4,
    "ACTION5": GameAction.ACTION5,
    "ACTION6": GameAction.ACTION6,
    "ACTION7": GameAction.ACTION7,
}


class GameSession:
    """Holds all mutable game state. MCP tools delegate to this class."""

    def __init__(self, env) -> None:
        self.env = env
        self.composer = Composer()
        self.frames: list[np.ndarray] = []
        self.annotations: dict[str, Annotation] = {}
        self._action_history: list[str] = []
        self.turn_count: int = 0
        self.total_turns: int = 0
        self.levels_completed: int = 0
        self.last_state: GameState = GameState.NOT_FINISHED
        self.learned: dict[str, str] = {}
        self._cells_changed_history: list[int] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def reset(self) -> str:
        """Reset the environment and return initial perception."""
        obs = self.env.reset()
        grid = np.array(obs.frame[-1], dtype=np.int64)

        # Reset per-episode state but preserve learned
        self.frames = [grid]
        self._action_history = []
        self.turn_count = 0
        self.last_state = GameState.NOT_FINISHED
        self._cells_changed_history = []

        self.annotations = self.composer.perceive(grid, [])
        return self._format_perception(self.annotations, grid)

    def perceive(self) -> str:
        """Run all lenses on the current frame and return text."""
        if not self.frames:
            return "No frame available. Call reset() first."
        grid = self.frames[-1]
        history = self.frames[:-1]
        self.annotations = self.composer.perceive(grid, history)
        return self._format_perception(self.annotations, grid)

    def step(
        self, action_name: str, x: int | None = None, y: int | None = None
    ) -> str:
        """Execute an action and return observation diff as text."""
        # Validate action
        available = {
            k for k, v in _ACTION_MAP.items()
            if v in self.env.action_space
        }
        if action_name not in available:
            return (
                f"Action '{action_name}' is not available. "
                f"Valid actions: {sorted(available)}"
            )

        game_action = _ACTION_MAP[action_name]
        prev_grid = self.frames[-1] if self.frames else None

        data: dict = {}
        if x is not None and y is not None:
            data = {"x": x, "y": y}
        obs = self.env.step(game_action, data=data)
        grid = np.array(obs.frame[-1], dtype=np.int64)
        self.frames.append(grid)
        self._action_history.append(action_name)
        self.turn_count += 1
        self.total_turns += 1
        self.last_state = obs.state

        if obs.state == GameState.WIN:
            self.levels_completed += 1

        # Compute diff
        parts = [f"## Action: {action_name}"]
        parts.append(f"State: {obs.state.name}")
        parts.append(f"Turn: {self.turn_count} (total: {self.total_turns})")

        if prev_grid is not None:
            diff = self._detect_movement(prev_grid, grid)
            if diff:
                parts.append(f"Movement: {diff}")
            changed = int(np.sum(prev_grid != grid))
            parts.append(f"Pixels changed: {changed}")
            self._cells_changed_history.append(changed)

        # Run perception on new frame
        history = self.frames[:-1]
        self.annotations = self.composer.perceive(grid, history)

        return "\n".join(parts)

    def reflect(self) -> str:
        """Summarize the session history."""
        parts = [f"## Session Reflection"]
        parts.append(f"Turns: {self.turn_count} (total: {self.total_turns})")
        parts.append(f"Levels completed: {self.levels_completed}")
        parts.append(f"Game state: {self.last_state.name}")

        if self._action_history:
            parts.append(f"Actions taken: {', '.join(self._action_history)}")
            # Action frequency
            freq: dict[str, int] = {}
            for a in self._action_history:
                freq[a] = freq.get(a, 0) + 1
            parts.append(f"Action frequency: {freq}")

        if self.learned:
            parts.append("Learned:")
            for k, v in self.learned.items():
                parts.append(f"  {k}: {v}")

        # Player/goal positions from learned colors + current frame
        if self.frames:
            grid = self.frames[-1]
            if "player_color" in self.learned:
                pc = int(self.learned["player_color"])
                pos = self._find_color_center(grid, pc)
                if pos is not None:
                    parts.append(f"Player position: row={pos[0]:.0f}, col={pos[1]:.0f}")
            if "goal_color" in self.learned:
                gc = int(self.learned["goal_color"])
                pos = self._find_color_center(grid, gc)
                if pos is not None:
                    parts.append(f"Goal position: row={pos[0]:.0f}, col={pos[1]:.0f}")

        # Physics model
        if "physics" in self.learned:
            parts.append(f"Physics: {self.learned['physics']}")

        # Stuck detection
        if len(self._cells_changed_history) >= 3:
            if all(c == 0 for c in self._cells_changed_history[-3:]):
                parts.append("WARNING: Stuck — last 3 actions had 0 cells changed")

        # Top lens combinations
        if self.annotations:
            top = self.composer.top_k(self.annotations, k=3)
            if top:
                combo_strs = [
                    f"  {a}+{b} (score={s:.2f})" for s, (a, b) in top
                ]
                parts.append("Top lens combinations:\n" + "\n".join(combo_strs))

        return "\n".join(parts)

    def status(self) -> str:
        """Return lightweight state info."""
        info = self.env.environment_info
        available = sorted(
            k for k, v in _ACTION_MAP.items()
            if v in self.env.action_space
        )
        parts = [
            f"Game: {info.game_id} ({info.title})",
            f"State: {self.last_state.name}",
            f"Turn: {self.turn_count}",
            f"Levels completed: {self.levels_completed}",
            f"Tags: {info.tags}",
            f"Baseline actions: {info.baseline_actions}",
            f"Available actions: {available}",
        ]
        return "\n".join(parts)

    # ------------------------------------------------------------------
    # Formatting helpers
    # ------------------------------------------------------------------

    def _format_perception(
        self, annotations: dict[str, Annotation], grid: np.ndarray
    ) -> str:
        """Render all lens annotations as markdown text."""
        sections: list[str] = []

        # Spatial
        spatial_parts: list[str] = []
        for name, ann in annotations.items():
            if isinstance(ann, RegionLabels):
                spatial_parts.append(
                    f"- {name}: {ann.count} regions"
                )
            elif isinstance(ann, EdgeMask):
                edge_count = int(ann.mask.sum())
                spatial_parts.append(
                    f"- {name}: {edge_count} edge pixels"
                )
        if spatial_parts:
            sections.append("### Spatial\n" + "\n".join(spatial_parts))

        # Structural
        structural_parts: list[str] = []
        for name, ann in annotations.items():
            if isinstance(ann, ContainmentTree):
                nested = sum(1 for p in ann.parent.values() if p is not None)
                structural_parts.append(
                    f"- {name}: {len(ann.parent)} objects, {nested} nested"
                )
            elif isinstance(ann, SymmetryResult):
                axes = []
                if ann.horizontal:
                    axes.append("horizontal")
                if ann.vertical:
                    axes.append("vertical")
                if ann.rotational_order > 0:
                    axes.append(f"rot-{ann.rotational_order}")
                structural_parts.append(
                    f"- {name}: {', '.join(axes) if axes else 'none'}"
                )
            elif isinstance(ann, PeriodicityResult):
                structural_parts.append(
                    f"- {name}: row={ann.row_period}, col={ann.col_period}"
                )
            elif isinstance(ann, AlignmentResult):
                structural_parts.append(
                    f"- {name}: {len(ann.row_lines)} rows, {len(ann.col_lines)} cols"
                )
        if structural_parts:
            sections.append("### Structural\n" + "\n".join(structural_parts))

        # Temporal
        temporal_parts: list[str] = []
        for name, ann in annotations.items():
            if isinstance(ann, DisplacementField):
                if ann.vectors:
                    temporal_parts.append(
                        f"- {name}: {len(ann.vectors)} objects displaced"
                    )
            elif isinstance(ann, ChangeMask):
                app = int(ann.appeared.sum())
                dis = int(ann.disappeared.sum())
                if app or dis:
                    temporal_parts.append(
                        f"- {name}: {app} appeared, {dis} disappeared"
                    )
            elif isinstance(ann, StateChangeMask):
                changed = int(ann.mask.sum())
                if changed:
                    temporal_parts.append(
                        f"- {name}: {changed} pixels changed color"
                    )
        if temporal_parts:
            sections.append("### Temporal\n" + "\n".join(temporal_parts))

        # Relational
        relational_parts: list[str] = []
        for name, ann in annotations.items():
            if isinstance(ann, ProximityGraph):
                if ann.distances:
                    relational_parts.append(
                        f"- {name}: {len(ann.distances)} pairs"
                    )
            elif isinstance(ann, ColorCorrespondence):
                relational_parts.append(
                    f"- {name}: {len(ann.color_to_objects)} colors"
                )
            elif isinstance(ann, SizeCount):
                relational_parts.append(
                    f"- {name}: {len(ann.sizes)} objects"
                )
        if relational_parts:
            sections.append("### Relational\n" + "\n".join(relational_parts))

        # Goal Detection
        goal_parts: list[str] = []
        for name, ann in annotations.items():
            if isinstance(ann, GoalDetection):
                goal_parts.append(
                    f"- {name}: {len(ann.goals)} candidates, "
                    f"best_similarity={ann.best_similarity:.2f}"
                )
        if goal_parts:
            sections.append("### Goal Detection\n" + "\n".join(goal_parts))

        # Game Semantics
        semantics = [f"### Game Semantics"]
        semantics.append(self._format_color_census(grid))
        if "player_color" in self.learned:
            pc = int(self.learned["player_color"])
            pos = self._find_color_center(grid, pc)
            pos_str = f"row={pos[0]:.0f}, col={pos[1]:.0f}" if pos else "not found"
            semantics.append(f"Player: color {pc}, position {pos_str}")
        if "goal_color" in self.learned:
            gc = int(self.learned["goal_color"])
            pos = self._find_color_center(grid, gc)
            pos_str = f"row={pos[0]:.0f}, col={pos[1]:.0f}" if pos else "not found"
            semantics.append(f"Goal: color {gc}, position {pos_str}")
        if "physics" in self.learned:
            semantics.append(f"Physics: {self.learned['physics']}")
        sections.append("\n".join(semantics))

        # Compact grid
        sections.append("### Grid (4x downsampled)\n" + self._render_grid_compact(grid))

        # Connected Components summary (always include for test assertions)
        for name, ann in annotations.items():
            if isinstance(ann, RegionLabels) and "Connected Components" in name:
                sections.insert(0, f"**Connected Components**: {ann.count} regions found")
                break

        return "\n\n".join(sections)

    def _detect_movement(
        self, prev: np.ndarray, curr: np.ndarray
    ) -> str:
        """Find relocated colors, infer player, direction, physics."""
        diff_mask = prev != curr
        if not diff_mask.any():
            return ""

        # Find colors that moved
        moved_colors: list[int] = []
        unique_colors = set(np.unique(prev)) | set(np.unique(curr))
        for color in unique_colors:
            if color == 0:
                continue
            prev_pos = np.argwhere(prev == color)
            curr_pos = np.argwhere(curr == color)
            if len(prev_pos) > 0 and len(curr_pos) > 0:
                prev_center = prev_pos.mean(axis=0)
                curr_center = curr_pos.mean(axis=0)
                dist = np.linalg.norm(curr_center - prev_center)
                if dist > 1.0:
                    moved_colors.append(int(color))

        if not moved_colors:
            return ""

        total_cells = curr.shape[0] * curr.shape[1]
        parts = []
        for color in moved_colors:
            prev_center = self._find_color_center(prev, color)
            curr_center = self._find_color_center(curr, color)
            if prev_center is not None and curr_center is not None:
                dy = curr_center[0] - prev_center[0]
                dx = curr_center[1] - prev_center[1]
                dist = float(np.sqrt(dy**2 + dx**2))
                direction = []
                if dy < -1:
                    direction.append("up")
                elif dy > 1:
                    direction.append("down")
                if dx < -1:
                    direction.append("left")
                elif dx > 1:
                    direction.append("right")
                dir_str = "+".join(direction) if direction else "stationary"
                parts.append(
                    f"Color {color} moved {dir_str} "
                    f"(dy={dy:.1f}, dx={dx:.1f})"
                )
                # Learn player color
                self.learned["player_color"] = str(color)
                self.learned["last_direction"] = dir_str
                # Physics inference
                if dist > 2.0:
                    self.learned["physics"] = "SLIDING"
                elif dist > 0:
                    self.learned["physics"] = "STEPPING"

        # Goal color detection: rarest non-bg, non-player, non-wall color <5%
        player_color = int(self.learned.get("player_color", -1))
        unique_c, counts_c = np.unique(curr, return_counts=True)
        for c, cnt in sorted(zip(unique_c, counts_c), key=lambda x: x[1]):
            c_int = int(c)
            frac = cnt / total_cells
            if c_int == 0:
                continue
            if c_int == player_color:
                continue
            # Skip wall-like colors (>30% of grid)
            if frac > 0.30:
                continue
            if frac < 0.05:
                self.learned["goal_color"] = str(c_int)
                break

        return "; ".join(parts)

    def _find_color_center(
        self, grid: np.ndarray, color: int
    ) -> tuple[float, float] | None:
        """Return centroid of a color."""
        positions = np.argwhere(grid == color)
        if len(positions) == 0:
            return None
        return (float(positions[:, 0].mean()), float(positions[:, 1].mean()))

    def _format_color_census(self, grid: np.ndarray) -> str:
        """Count pixels per color."""
        unique, counts = np.unique(grid, return_counts=True)
        lines = []
        for color, count in sorted(zip(unique, counts), key=lambda x: -x[1]):
            lines.append(f"  color {int(color)}: {int(count)} px")
        return "Color census:\n" + "\n".join(lines)

    def _render_grid_compact(self, grid: np.ndarray, factor: int = 4) -> str:
        """Render 4x downsampled grid as text."""
        h, w = grid.shape
        rows = []
        for r in range(0, h, factor):
            row_chars = []
            for c in range(0, w, factor):
                block = grid[r:r+factor, c:c+factor]
                # Most common value in block
                vals, cnts = np.unique(block, return_counts=True)
                dominant = vals[cnts.argmax()]
                if dominant == 0:
                    row_chars.append(".")
                else:
                    row_chars.append(format(int(dominant), "x"))
            rows.append("".join(row_chars))
        return "\n".join(rows)
