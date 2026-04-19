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
    MechanicsMap,
    Annotation,
)
from arc_see.lenses.action_map import ActionMap
from arc_see.lenses.resources import ResourceTracker

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
        # Double reset: R11L (and possibly others) leak mutable game state
        # across single resets, causing corrupted arm behavior in L2+.
        # The second reset clears the residual state.
        self.env.reset()
        obs = self.env.reset()
        grid = np.array(obs.frame[-1], dtype=np.int64)

        # Reset per-episode state; clear learned to avoid stale assumptions
        self.learned = {}
        self.frames = [grid]
        self._action_history = []
        self.turn_count = 0
        self.last_state = GameState.NOT_FINISHED
        # env.reset() starts at L1 — mirror the engine's count (usually 0).
        self.levels_completed = int(getattr(obs, "levels_completed", 0))
        self._cells_changed_history = []

        # Reset stateful lenses
        from arc_see.lenses import get_all
        for lens in get_all().values():
            if hasattr(lens, 'reset'):
                lens.reset()

        self.annotations = self.composer.perceive(grid, [])
        return self._format_perception(self.annotations, grid)

    def perceive(self) -> str:
        """Run all lenses on the current frame and return text."""
        if not self.frames:
            return "No frame available. Call reset() first."
        grid = self.frames[-1]
        history = self.frames[-10:-1] if len(self.frames) > 1 else []
        self.annotations = self.composer.perceive(grid, history)
        return self._format_perception(self.annotations, grid)

    def step(
        self, action_name: str, x: int | None = None, y: int | None = None
    ) -> str:
        """Execute an action and return observation diff as text."""
        if not self.frames:
            return "No frame available. Call reset() first."

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
        if (x is None) != (y is None):
            return "Both x and y are required for coordinate actions."
        if x is not None and y is not None:
            data = {"x": x, "y": y}
        # Tell the action_map lens which action we're about to take
        from arc_see.lenses.action_map import action_map_lens
        action_map_lens.record_action(action_name)
        if "player_color" in self.learned:
            action_map_lens.set_player_color(int(self.learned["player_color"]))

        obs = self.env.step(game_action, data=data)
        grid = np.array(obs.frame[-1], dtype=np.int64)
        self.frames.append(grid)
        self._action_history.append(action_name)
        self.turn_count += 1
        self.total_turns += 1
        self.last_state = obs.state

        # Mirror the authoritative per-level counter from the game engine.
        # Note: obs.state stays NOT_FINISHED between levels — it only flips to
        # WIN when ALL levels are done. Using state as a trigger misses every
        # intermediate level advance.
        self.levels_completed = int(getattr(obs, "levels_completed", self.levels_completed))

        # Compute diff
        parts = [f"## Action: {action_name}"]
        parts.append(f"State: {obs.state.name}")
        parts.append(f"Turn: {self.turn_count} (total: {self.total_turns})")

        if prev_grid is not None:
            diff = self._detect_movement(prev_grid, grid)
            if diff:
                parts.append(f"Movement: {diff}")
            changed = int(np.sum(prev_grid != grid))
            parts.append(f"Cells changed: {changed}")
            self._cells_changed_history.append(changed)

        # Show before and after grids
        if prev_grid is not None:
            parts.append("")
            parts.append("### Before\n" + self._render_grid(prev_grid))
        parts.append("")
        parts.append("### After\n" + self._render_grid(grid))

        # Run perception on new frame
        history = self.frames[-10:-1] if len(self.frames) > 1 else []
        self.annotations = self.composer.perceive(grid, history)
        parts.append("")
        parts.append(self._format_perception(self.annotations, grid))

        return "\n".join(parts)

    def reflect(self) -> str:
        """Summarize the session history."""
        parts = ["## Session Reflection"]
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

        # Show non-standard learned keys (player/goal/physics have dedicated lines below)
        _dedicated_keys = {"player_color", "goal_color", "physics", "last_direction"}
        extra_learned = {k: v for k, v in self.learned.items() if k not in _dedicated_keys}
        if extra_learned:
            parts.append("Learned:")
            for k, v in extra_learned.items():
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
                    f"- {name}: {edge_count} edge cells"
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
                        f"- {name}: {changed} cells changed color"
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

        # Mechanics (pickups, blocking, interactions)
        mechanics_parts: list[str] = []
        for name, ann in annotations.items():
            if isinstance(ann, MechanicsMap):
                if ann.player_color is not None:
                    pos_str = f"row={ann.player_position[0]}, col={ann.player_position[1]}" if ann.player_position else "unknown"
                    mechanics_parts.append(f"- Player: color {ann.player_color}, position {pos_str}")
                if ann.total_collected > 0:
                    mechanics_parts.append(f"- Pickups collected: {ann.total_collected}")
                    recent = ann.collected[-3:] if len(ann.collected) > 3 else ann.collected
                    for event in recent:
                        mechanics_parts.append(
                            f"  - color {event.color} at ({event.position[0]}, {event.position[1]}) on turn {event.turn}"
                        )
                if ann.collectables:
                    total_remaining = sum(len(pos) for pos in ann.collectables.values())
                    mechanics_parts.append(f"- Remaining collectables: {total_remaining}")
                    for color, positions in ann.collectables.items():
                        mechanics_parts.append(f"  - color {color}: {len(positions)} cells")
                if ann.blocking_colors:
                    mechanics_parts.append(f"- Blocking colors (walls): {sorted(ann.blocking_colors)}")
                if ann.hypotheses:
                    mechanics_parts.append("- Causal hypotheses (what do pickups DO?):")
                    for h in ann.hypotheses[:5]:
                        mechanics_parts.append(
                            f"  - Collecting color {h.trigger_color} → {h.effect} "
                            f"({h.observations}x observed, confidence={h.confidence:.0%})"
                        )
        if mechanics_parts:
            sections.append("### Mechanics\n" + "\n".join(mechanics_parts))

        # Action Map
        action_parts: list[str] = []
        for name, ann in annotations.items():
            if isinstance(ann, ActionMap):
                if ann.summary:
                    action_parts.append("- Action effects learned so far:")
                    for act, desc in sorted(ann.summary.items()):
                        action_parts.append(f"  - {act}: {desc}")
        if action_parts:
            sections.append("### Action Map\n" + "\n".join(action_parts))

        # Resources
        resource_parts: list[str] = []
        for name, ann in annotations.items():
            if isinstance(ann, ResourceTracker):
                # Show non-stable trends
                changing = {c: t for c, t in ann.trends.items() if t != "stable"}
                if changing:
                    resource_parts.append("- Changing resources:")
                    for color, trend in sorted(changing.items()):
                        count = ann.counts.get(color, 0)
                        deltas = ann.deltas.get(color, [])
                        delta_str = ",".join(str(d) for d in deltas)
                        resource_parts.append(
                            f"  - color {color}: {count} cells, {trend} (recent: {delta_str})"
                        )
                if ann.possible_counters:
                    resource_parts.append(
                        f"- Possible counters: colors {ann.possible_counters}"
                    )
        if resource_parts:
            sections.append("### Resources\n" + "\n".join(resource_parts))

        # Game Semantics
        semantics = ["### Game Semantics"]
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

        # Full grid
        sections.append("### Grid\n" + self._render_grid(grid))

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

        # Pick the player as the moved color with the fewest cells
        # (players are typically small objects, not large backgrounds)
        color_sizes = {c: int((curr == c).sum()) for c in moved_colors}
        player_candidate = min(color_sizes, key=color_sizes.get)

        for color in moved_colors:
            prev_center = self._find_color_center(prev, color)
            curr_center = self._find_color_center(curr, color)
            if prev_center is not None and curr_center is not None:
                dy = curr_center[0] - prev_center[0]
                dx = curr_center[1] - prev_center[1]
                dist = float(np.sqrt(dy**2 + dx**2))
                direction = []
                if dy < -0.5:
                    direction.append("up")
                elif dy > 0.5:
                    direction.append("down")
                if dx < -0.5:
                    direction.append("left")
                elif dx > 0.5:
                    direction.append("right")
                dir_str = "+".join(direction) if direction else "minimal"
                parts.append(
                    f"Color {color} moved {dir_str} "
                    f"(dy={dy:.1f}, dx={dx:.1f})"
                )
                # Only learn from the player candidate
                if color == player_candidate:
                    self.learned["player_color"] = str(color)
                    self.learned["last_direction"] = dir_str
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
            if frac <= 0.05:
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
        """Count cells per color."""
        unique, counts = np.unique(grid, return_counts=True)
        lines = []
        for color, count in sorted(zip(unique, counts), key=lambda x: -x[1]):
            lines.append(f"  color {int(color)}: {int(count)} cells")
        return "Color census:\n" + "\n".join(lines)

    def _render_grid(self, grid: np.ndarray) -> str:
        """Render full grid as text. Single hex char per cell."""
        rows = []
        for r in range(grid.shape[0]):
            row_chars = []
            for c in range(grid.shape[1]):
                v = int(grid[r, c])
                if v == 0:
                    row_chars.append(".")
                else:
                    row_chars.append(format(v, "x"))
            rows.append("".join(row_chars))
        return "\n".join(rows)
