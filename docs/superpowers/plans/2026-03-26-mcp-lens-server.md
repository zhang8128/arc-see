# MCP Lens Server Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the heuristic agent with an MCP server that exposes lenses as tools, so Claude can be the reasoning layer for ARC-AGI-3 games.

**Architecture:** A FastMCP stdio server (`arc_see/mcp_server.py`) holds game state and exposes 5 tools (perceive, step, reflect, reset, status). The existing lenses and composer stay unchanged. The old agent.py, graph.py, runner.py, and their tests are deleted.

**Tech Stack:** Python 3.12, FastMCP (mcp package), arc_agi, arcengine, numpy, existing lens system

---

### Task 1: Add mcp dependency

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Add mcp to dependencies**

In `pyproject.toml`, add `"mcp>=1.0"` to the `dependencies` list:

```toml
dependencies = [
    "numpy>=2.0",
    "scipy>=1.14",
    "arc-agi>=0.9",
    "mcp>=1.0",
]
```

- [ ] **Step 2: Install and verify**

Run: `uv sync`
Then: `uv run python -c "from mcp.server.fastmcp import FastMCP; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "chore: add mcp dependency"
```

---

### Task 2: Build GameSession state container

**Files:**
- Create: `arc_see/session.py`
- Create: `tests/test_session.py`

The `GameSession` class holds all mutable game state. The MCP tools are thin wrappers that delegate to this class. This separation makes testing easy — tests create a GameSession directly without starting an MCP server.

- [ ] **Step 1: Write failing tests for GameSession**

Create `tests/test_session.py`:

```python
import numpy as np
import pytest
from unittest.mock import MagicMock, patch
from arcengine import GameAction, GameState


class FakeObs:
    """Fake observation returned by env.step/reset."""
    def __init__(self, frame, state=GameState.NOT_FINISHED):
        self.frame = [frame]
        self.state = state


def make_env(initial_grid, action_results=None):
    """Create a mock env that returns predetermined frames."""
    env = MagicMock()
    env.action_space = [GameAction.ACTION1, GameAction.ACTION2,
                        GameAction.ACTION3, GameAction.ACTION4]
    env.environment_info = MagicMock()
    env.environment_info.game_id = "test-game"
    env.environment_info.title = "TEST"
    env.environment_info.tags = ["keyboard"]
    env.environment_info.baseline_actions = [20, 30]

    env.reset.return_value = FakeObs(initial_grid)

    if action_results:
        env.step.side_effect = [FakeObs(f, s) for f, s in action_results]
    else:
        env.step.return_value = FakeObs(initial_grid)

    return env


def make_sliding_grid():
    """Create a grid resembling a sliding puzzle:
    - color 4 = walls (border)
    - color 3 = floor (interior)
    - color 12 = player (small block)
    - color 1 = goal (2 cells)
    """
    grid = np.full((64, 64), 4, dtype=np.int64)  # walls everywhere
    grid[10:50, 10:50] = 3  # floor
    grid[40:42, 30:32] = 12  # player at (40,30)
    grid[20:21, 20:21] = 1  # goal at (20,20)
    return grid


def make_moved_grid(player_pos):
    """Same as sliding grid but player at given (row, col)."""
    grid = make_sliding_grid()
    grid[40:42, 30:32] = 3  # clear old player
    r, c = player_pos
    grid[r:r+2, c:c+2] = 12
    return grid


class TestGameSession:
    def test_reset_returns_perception(self):
        from arc_see.session import GameSession
        grid = make_sliding_grid()
        env = make_env(grid)
        session = GameSession(env)
        result = session.reset()
        assert "Connected Components" in result
        assert len(session.frames) == 1

    def test_perceive_returns_text(self):
        from arc_see.session import GameSession
        grid = make_sliding_grid()
        env = make_env(grid)
        session = GameSession(env)
        session.reset()
        result = session.perceive()
        assert "Spatial" in result or "Connected Components" in result
        assert isinstance(result, str)

    def test_step_returns_diff(self):
        from arc_see.session import GameSession
        initial = make_sliding_grid()
        moved = make_moved_grid((35, 30))
        env = make_env(initial, action_results=[(moved, GameState.NOT_FINISHED)])
        session = GameSession(env)
        session.reset()
        result = session.step("ACTION1")
        assert "ACTION1" in result
        assert "NOT_FINISHED" in result
        assert session.turn_count == 1

    def test_step_invalid_action(self):
        from arc_see.session import GameSession
        grid = make_sliding_grid()
        env = make_env(grid)
        session = GameSession(env)
        session.reset()
        result = session.step("INVALID")
        assert "not available" in result.lower() or "invalid" in result.lower()

    def test_step_tracks_player_movement(self):
        from arc_see.session import GameSession
        initial = make_sliding_grid()
        moved = make_moved_grid((35, 30))
        env = make_env(initial, action_results=[(moved, GameState.NOT_FINISHED)])
        session = GameSession(env)
        session.reset()
        result = session.step("ACTION1")
        # Should mention player moved
        assert "moved" in result.lower() or "player" in result.lower() or "12" in result

    def test_reflect_summarizes_session(self):
        from arc_see.session import GameSession
        initial = make_sliding_grid()
        moved = make_moved_grid((35, 30))
        env = make_env(initial, action_results=[(moved, GameState.NOT_FINISHED)])
        session = GameSession(env)
        session.reset()
        session.step("ACTION1")
        result = session.reflect()
        assert "Turns" in result or "turns" in result
        assert "ACTION1" in result

    def test_status_returns_state(self):
        from arc_see.session import GameSession
        grid = make_sliding_grid()
        env = make_env(grid)
        session = GameSession(env)
        session.reset()
        result = session.status()
        assert "NOT_FINISHED" in result or "not_finished" in result.lower()
        assert "test-game" in result.lower() or "TEST" in result

    def test_reset_preserves_learned(self):
        from arc_see.session import GameSession
        initial = make_sliding_grid()
        moved = make_moved_grid((35, 30))
        env = make_env(initial, action_results=[
            (moved, GameState.NOT_FINISHED),
        ])
        session = GameSession(env)
        session.reset()
        session.step("ACTION1")
        # Learn something about the game
        old_learned = dict(session.learned)
        # Reset should preserve learned
        env.reset.return_value = FakeObs(initial)
        session.reset()
        assert session.turn_count == 0
        assert len(session.frames) == 1
        # Learned state should persist
        assert session.learned == old_learned

    def test_win_increments_levels(self):
        from arc_see.session import GameSession
        initial = make_sliding_grid()
        win_grid = make_moved_grid((20, 20))
        env = make_env(initial, action_results=[
            (win_grid, GameState.WIN),
        ])
        session = GameSession(env)
        session.reset()
        result = session.step("ACTION1")
        assert session.levels_completed == 1
        assert "WIN" in result
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_session.py -v`
Expected: All tests FAIL with `ModuleNotFoundError: No module named 'arc_see.session'`

- [ ] **Step 3: Implement GameSession**

Create `arc_see/session.py`:

```python
"""GameSession — holds game state and provides text-based tools for Claude."""

from __future__ import annotations

import numpy as np
from arcengine import GameAction, GameState

from arc_see.composer import Composer
from arc_see.lenses import (
    RegionLabels, EdgeMask, ContainmentTree, DisplacementField,
    ChangeMask, StateChangeMask, SymmetryResult, PeriodicityResult,
    AlignmentResult, ProximityGraph, ColorCorrespondence, SizeCount,
    GoalDetection,
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
_REVERSE_MAP = {v: k for k, v in _ACTION_MAP.items()}


class GameSession:
    """Holds game state and exposes text-based perception/action methods."""

    def __init__(self, env):
        self.env = env
        self.composer = Composer()
        self.frames: list[np.ndarray] = []
        self.turn_count: int = 0
        self.total_turns: int = 0
        self.levels_completed: int = 0
        self.last_state: str = "NOT_FINISHED"
        self.learned: dict = {}
        self._action_history: list[dict] = []
        self._annotations: dict = {}

    @property
    def _available_actions(self) -> list[str]:
        return [_REVERSE_MAP[a] for a in self.env.action_space if a in _REVERSE_MAP]

    def reset(self) -> str:
        """Reset current level, return perception of fresh frame."""
        obs = self.env.reset()
        grid = np.array(obs.frame[-1], dtype=np.int64)
        self.frames = [grid]
        self.turn_count = 0
        self._action_history = []
        self._annotations = self.composer.perceive(grid, [])
        return self._format_perception()

    def perceive(self) -> str:
        """Run all lenses on current frame, return text summary."""
        if not self.frames:
            return "No frame available. Call reset() first."
        grid = self.frames[-1]
        history = self.frames[:-1]
        self._annotations = self.composer.perceive(grid, history)
        return self._format_perception()

    def step(self, action: str, x: int | None = None, y: int | None = None) -> str:
        """Take a game action, return what happened."""
        if action not in _ACTION_MAP or _ACTION_MAP[action] not in {a for a in self.env.action_space}:
            return f"Action '{action}' is not available. Available: {self._available_actions}"

        prev_grid = self.frames[-1] if self.frames else None
        game_action = _ACTION_MAP[action]
        data = {}
        if x is not None and y is not None:
            data = {"x": x, "y": y}

        obs = self.env.step(game_action, data=data if data else None)
        grid = np.array(obs.frame[-1], dtype=np.int64)
        self.frames.append(grid)
        self.turn_count += 1
        self.total_turns += 1
        self.last_state = str(obs.state).replace("GameState.", "")

        if obs.state == GameState.WIN:
            self.levels_completed += 1

        # Compute diff
        diff_count = 0
        player_info = ""
        if prev_grid is not None:
            diff_mask = grid != prev_grid
            diff_count = int(diff_mask.sum())
            player_info = self._detect_movement(prev_grid, grid, action)

        # Record action
        direction = self.learned.get("directions", {}).get(action, "")
        self._action_history.append({
            "action": action,
            "direction": direction,
            "cells_changed": diff_count,
            "state": self.last_state,
        })

        lines = []
        dir_label = f" ({direction})" if direction else ""
        lines.append(f"Action: {action}{dir_label}")
        if player_info:
            lines.append(player_info)
        lines.append(f"Cells changed: {diff_count}")
        lines.append(f"State: {self.last_state}")
        lines.append(f"Turns used: {self.turn_count} (total: {self.total_turns})")
        return "\n".join(lines)

    def reflect(self) -> str:
        """Summarize everything learned in this game session."""
        lines = []
        lines.append(f"## Session Summary")
        lines.append(f"Turns: {self.turn_count} | Total: {self.total_turns} | Levels completed: {self.levels_completed}")
        lines.append(f"State: {self.last_state}")
        lines.append("")

        # Actions tried
        if self._action_history:
            lines.append("## Actions Tried")
            action_counts: dict[str, int] = {}
            for entry in self._action_history:
                a = entry["action"]
                d = entry.get("direction", "")
                label = f"{a} ({d})" if d else a
                action_counts[label] = action_counts.get(label, 0) + 1
            for label, count in action_counts.items():
                lines.append(f"- {label}: {count} times")
            lines.append("")

        # Learned directions
        directions = self.learned.get("directions", {})
        if directions:
            lines.append("## Known Action Directions")
            for action, direction in directions.items():
                lines.append(f"- {action} = {direction}")
            lines.append("")

        # Physics
        physics = self.learned.get("physics", "UNKNOWN")
        lines.append(f"## Physics: {physics}")
        lines.append("")

        # Player/goal
        player_color = self.learned.get("player_color")
        goal_color = self.learned.get("goal_color")
        if player_color is not None:
            lines.append(f"## Player: color {player_color}")
            if self.frames:
                pos = self._find_color_center(self.frames[-1], player_color)
                if pos:
                    lines.append(f"  Position: ({pos[0]}, {pos[1]})")
        if goal_color is not None:
            lines.append(f"## Goal: color {goal_color}")
            if self.frames:
                pos = self._find_color_center(self.frames[-1], goal_color)
                if pos:
                    lines.append(f"  Position: ({pos[0]}, {pos[1]})")
        lines.append("")

        # Stuck detection
        if len(self._action_history) >= 3:
            recent = self._action_history[-3:]
            if all(h["cells_changed"] == 0 for h in recent):
                lines.append("WARNING: Last 3 actions produced no state change — possibly stuck")

        # Top lens combinations
        if self._annotations:
            top = self.composer.top_k(self._annotations, k=5)
            if top:
                lines.append("## Top Lens Combinations")
                for score, pair in top:
                    lines.append(f"- {pair[0]} + {pair[1]}: {score:.3f}")

        return "\n".join(lines)

    def status(self) -> str:
        """Lightweight state check."""
        info = self.env.environment_info
        lines = [
            f"Game: {info.game_id} ({info.title})",
            f"Tags: {info.tags}",
            f"State: {self.last_state}",
            f"Turns: {self.turn_count} (total: {self.total_turns})",
            f"Levels completed: {self.levels_completed}",
            f"Baseline actions per level: {info.baseline_actions}",
            f"Available actions: {self._available_actions}",
        ]
        return "\n".join(lines)

    # --- Private helpers ---

    def _format_perception(self) -> str:
        """Format annotations as human-readable text."""
        ann = self._annotations
        grid = self.frames[-1] if self.frames else None
        lines = []

        # Spatial
        cc = ann.get("connected_components")
        edges = ann.get("edges")
        enclosure = ann.get("enclosure")
        lines.append("## Spatial")
        if isinstance(cc, RegionLabels):
            lines.append(f"- Connected components: {cc.count} regions")
        if isinstance(edges, EdgeMask):
            density = float(edges.mask.sum()) / (64 * 64) * 100
            lines.append(f"- Edge density: {density:.1f}%")
        if isinstance(enclosure, ContainmentTree) and enclosure.parent:
            nested = sum(1 for p in enclosure.parent.values() if p is not None)
            lines.append(f"- Containment: {nested} nested regions")
        lines.append("")

        # Structural
        sym = ann.get("symmetry")
        per = ann.get("periodicity")
        align = ann.get("alignment")
        lines.append("## Structural")
        if isinstance(sym, SymmetryResult):
            axes = []
            if sym.horizontal:
                axes.append("horizontal")
            if sym.vertical:
                axes.append("vertical")
            if sym.rotational_order > 0:
                axes.append(f"rotational(order={sym.rotational_order})")
            lines.append(f"- Symmetry: {', '.join(axes) if axes else 'none'}")
        if isinstance(per, PeriodicityResult):
            if per.row_period or per.col_period:
                lines.append(f"- Periodicity: row={per.row_period}, col={per.col_period}")
            else:
                lines.append("- Periodicity: none")
        if isinstance(align, AlignmentResult):
            if align.row_lines or align.col_lines:
                lines.append(f"- Alignment: {len(align.row_lines)} row lines, {len(align.col_lines)} col lines")
        lines.append("")

        # Temporal
        mov = ann.get("movement")
        change = ann.get("creation_destruction")
        state_change = ann.get("state_change")
        lines.append("## Temporal")
        if isinstance(mov, DisplacementField) and mov.vectors:
            lines.append(f"- Movement: {len(mov.vectors)} objects moved")
            for obj_id, (dy, dx) in list(mov.vectors.items())[:5]:
                lines.append(f"  object {obj_id}: dy={dy:.0f}, dx={dx:.0f}")
        else:
            lines.append("- Movement: none detected")
        if isinstance(change, ChangeMask):
            appeared = int(change.appeared.sum())
            disappeared = int(change.disappeared.sum())
            if appeared or disappeared:
                lines.append(f"- Changes: {appeared} cells appeared, {disappeared} disappeared")
        if isinstance(state_change, StateChangeMask) and state_change.mask.any():
            lines.append(f"- Color changes: {int(state_change.mask.sum())} cells changed color")
        lines.append("")

        # Relational
        prox = ann.get("proximity")
        color_corr = ann.get("color_correspondence")
        size = ann.get("size_count")
        lines.append("## Relational")
        if isinstance(color_corr, ColorCorrespondence) and color_corr.color_to_objects:
            for color, objs in sorted(color_corr.color_to_objects.items()):
                lines.append(f"- Color {color}: {len(objs)} objects")
        if isinstance(size, SizeCount) and size.count_by_size:
            for sz, count in sorted(size.count_by_size.items(), reverse=True)[:5]:
                lines.append(f"- Size {sz}px: {count} objects")
        lines.append("")

        # Goal
        goal = ann.get("goal")
        lines.append("## Goal Detection")
        if isinstance(goal, GoalDetection) and goal.goals:
            for g in goal.goals:
                lines.append(f"- Candidate at {g.location}, similarity={g.similarity:.2f}")
        else:
            lines.append("- No goal candidates from corner/edge detection")
        lines.append("")

        # Game semantics
        lines.append("## Game Semantics")
        if grid is not None:
            lines.append(self._format_color_census(grid))
            player_color = self.learned.get("player_color")
            goal_color = self.learned.get("goal_color")
            if player_color is not None:
                pos = self._find_color_center(grid, player_color)
                lines.append(f"- Player: color {player_color} at {pos}")
            if goal_color is not None:
                pos = self._find_color_center(grid, goal_color)
                lines.append(f"- Goal: color {goal_color} at {pos}")
            physics = self.learned.get("physics", "UNKNOWN")
            lines.append(f"- Physics: {physics}")
        lines.append("")

        # Compact grid rendering
        lines.append("## Grid (4x downsampled)")
        if grid is not None:
            lines.append(self._render_grid_compact(grid))

        return "\n".join(lines)

    def _format_color_census(self, grid: np.ndarray) -> str:
        """Count pixels per color."""
        parts = ["- Color census:"]
        for color in sorted(np.unique(grid)):
            count = int((grid == color).sum())
            pct = count / (64 * 64) * 100
            parts.append(f"  color {color}: {count} cells ({pct:.1f}%)")
        return "\n".join(parts)

    def _render_grid_compact(self, grid: np.ndarray) -> str:
        """Render grid at 4x downsampled resolution."""
        cmap = "0123456789abcdef"
        lines = []
        for r in range(0, 64, 4):
            row = ""
            for c in range(0, 64, 4):
                block = grid[r:r+4, c:c+4]
                vals, counts = np.unique(block, return_counts=True)
                dominant = vals[counts.argmax()]
                row += cmap[dominant] if dominant < len(cmap) else "?"
            lines.append(row)
        return "\n".join(lines)

    def _detect_movement(self, prev: np.ndarray, curr: np.ndarray, action: str) -> str:
        """Detect what moved between frames and update learned state."""
        diff_mask = prev != curr
        if not diff_mask.any():
            return "No change detected"

        # Find colors that relocated (appeared in new spots, disappeared from old)
        old_vals = prev[diff_mask]
        new_vals = curr[diff_mask]

        # Colors that gained cells
        gained: dict[int, int] = {}
        lost: dict[int, int] = {}
        for ov, nv in zip(old_vals.flat, new_vals.flat):
            ov, nv = int(ov), int(nv)
            if ov != nv:
                lost[ov] = lost.get(ov, 0) + 1
                gained[nv] = gained.get(nv, 0) + 1

        # Player = color that both gained and lost cells (relocated)
        relocated = set(gained.keys()) & set(lost.keys())
        # Exclude very common colors (walls/floor)
        total = 64 * 64
        relocated = {c for c in relocated if int((curr == c).sum()) < total * 0.3}

        info_parts = []

        if relocated:
            player_color = max(relocated, key=lambda c: min(gained.get(c, 0), lost.get(c, 0)))
            self.learned["player_color"] = player_color

            prev_pos = self._find_color_center(prev, player_color)
            curr_pos = self._find_color_center(curr, player_color)

            if prev_pos and curr_pos:
                dy = curr_pos[0] - prev_pos[0]
                dx = curr_pos[1] - prev_pos[1]
                dist = (dy**2 + dx**2) ** 0.5
                info_parts.append(f"Player (color {player_color}): ({prev_pos[0]},{prev_pos[1]}) -> ({curr_pos[0]},{curr_pos[1]}), distance={dist:.1f}")

                # Infer direction
                direction = ""
                if abs(dy) > abs(dx):
                    direction = "UP" if dy < 0 else "DOWN"
                elif abs(dx) > abs(dy):
                    direction = "LEFT" if dx < 0 else "RIGHT"
                if direction:
                    if "directions" not in self.learned:
                        self.learned["directions"] = {}
                    self.learned["directions"][action] = direction
                    info_parts.append(f"Direction: {action} = {direction}")

                # Infer physics
                if dist > 2.0:
                    self.learned["physics"] = "SLIDING"
                elif dist > 0:
                    self.learned["physics"] = "STEPPING"

        # Detect goal color (rarest non-player, non-wall color)
        if "goal_color" not in self.learned:
            player_c = self.learned.get("player_color")
            color_counts = {}
            for c in np.unique(curr):
                c = int(c)
                if c == 0:
                    continue
                count = int((curr == c).sum())
                if count < total * 0.05 and c != player_c:
                    color_counts[c] = count
            if color_counts:
                goal_color = min(color_counts, key=color_counts.get)
                self.learned["goal_color"] = goal_color
                pos = self._find_color_center(curr, goal_color)
                info_parts.append(f"Goal candidate: color {goal_color} at {pos} ({color_counts[goal_color]} cells)")

        return "\n".join(info_parts)

    def _find_color_center(self, grid: np.ndarray, color: int) -> tuple[int, int] | None:
        """Find the centroid of a color cluster."""
        positions = np.argwhere(grid == color)
        if len(positions) == 0:
            return None
        return (int(positions[:, 0].mean()), int(positions[:, 1].mean()))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_session.py -v`
Expected: All 9 tests PASS

- [ ] **Step 5: Commit**

```bash
git add arc_see/session.py tests/test_session.py
git commit -m "feat: GameSession — state container with text-based perception/action"
```

---

### Task 3: Build MCP server

**Files:**
- Create: `arc_see/mcp_server.py`

The MCP server is a thin wrapper over GameSession. It creates the Arcade and env, then delegates each tool call to the session.

- [ ] **Step 1: Write the MCP server**

Create `arc_see/mcp_server.py`:

```python
"""MCP server — exposes ARC-AGI-3 lenses and game actions as tools for Claude."""

from __future__ import annotations

import sys
import arc_agi
from mcp.server.fastmcp import FastMCP

from arc_see.session import GameSession

mcp = FastMCP("arc-see")

_session: GameSession | None = None


def _get_session() -> GameSession:
    if _session is None:
        raise RuntimeError("No game loaded. Start the server with a game_id argument.")
    return _session


@mcp.tool()
def perceive() -> str:
    """Run all 13 perceptual lenses on the current frame.

    Returns structured annotations: spatial (components, edges, enclosure),
    structural (symmetry, periodicity, alignment), temporal (movement, changes),
    relational (proximity, colors, sizes), goal detection, game semantics
    (player/goal/walls), and a compact grid visualization.

    Call this after reset() or step() to understand the current board state.
    """
    return _get_session().perceive()


@mcp.tool()
def step(action: str, x: int | None = None, y: int | None = None) -> str:
    """Take a game action and see what happens.

    Args:
        action: One of the available actions (e.g. ACTION1, ACTION2, ...).
        x: X coordinate for click actions (optional).
        y: Y coordinate for click actions (optional).

    Returns what changed: player movement, cells changed, game state, turns used.
    Automatically detects player color, movement direction, and physics model.
    """
    return _get_session().step(action, x, y)


@mcp.tool()
def reflect() -> str:
    """Summarize everything learned in this game session.

    Returns: turns used, actions tried and their effects, inferred physics,
    player/goal positions, direction to goal, top lens combinations,
    and stuck detection warnings.
    """
    return _get_session().reflect()


@mcp.tool()
def reset() -> str:
    """Reset the current level and get a fresh perception.

    Clears frame history and turn counter. Preserves learned game semantics
    (player color, goal color, physics, action directions) across resets.

    Returns the same output as perceive() on the fresh frame.
    """
    return _get_session().reset()


@mcp.tool()
def status() -> str:
    """Quick check: game state, turns, levels, score, available actions."""
    return _get_session().status()


def main():
    game_id = sys.argv[1] if len(sys.argv) > 1 else None
    if game_id is None:
        print("Usage: python -m arc_see.mcp_server <game_id>", file=sys.stderr)
        sys.exit(1)

    global _session
    arcade = arc_agi.Arcade()
    env = arcade.make(game_id, render_mode=None)
    if env is None:
        print(f"Failed to create environment for {game_id}", file=sys.stderr)
        sys.exit(1)

    _session = GameSession(env)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Verify the server can be imported**

Run: `uv run python -c "from arc_see.mcp_server import mcp; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add arc_see/mcp_server.py
git commit -m "feat: MCP server — exposes lenses as tools for Claude"
```

---

### Task 4: Test MCP server end-to-end

**Files:**
- Create: `tests/test_mcp_server.py`

Test the MCP tools by calling them through the FastMCP test interface.

- [ ] **Step 1: Write MCP server tests**

Create `tests/test_mcp_server.py`:

```python
"""Test MCP server tools via direct invocation."""

import numpy as np
import pytest
from unittest.mock import MagicMock
from arcengine import GameAction, GameState


class FakeObs:
    def __init__(self, frame, state=GameState.NOT_FINISHED):
        self.frame = [frame]
        self.state = state


def make_grid():
    grid = np.full((64, 64), 4, dtype=np.int64)
    grid[10:50, 10:50] = 3
    grid[40:42, 30:32] = 12
    grid[20:21, 20:21] = 1
    return grid


def make_moved_grid():
    grid = make_grid()
    grid[40:42, 30:32] = 3
    grid[35:37, 30:32] = 12
    return grid


@pytest.fixture
def mock_session(monkeypatch):
    """Patch the global _session in mcp_server with a real GameSession using a mock env."""
    from arc_see.session import GameSession
    import arc_see.mcp_server as server

    grid = make_grid()
    moved = make_moved_grid()

    env = MagicMock()
    env.action_space = [GameAction.ACTION1, GameAction.ACTION2,
                        GameAction.ACTION3, GameAction.ACTION4]
    env.environment_info = MagicMock()
    env.environment_info.game_id = "test-game"
    env.environment_info.title = "TEST"
    env.environment_info.tags = ["keyboard"]
    env.environment_info.baseline_actions = [20]

    env.reset.return_value = FakeObs(grid)
    env.step.return_value = FakeObs(moved)

    session = GameSession(env)
    monkeypatch.setattr(server, "_session", session)
    return session


class TestMCPTools:
    def test_reset(self, mock_session):
        from arc_see.mcp_server import reset
        result = reset()
        assert "Connected Components" in result or "Spatial" in result

    def test_perceive(self, mock_session):
        from arc_see.mcp_server import reset, perceive
        reset()
        result = perceive()
        assert "Spatial" in result
        assert "Grid" in result

    def test_step(self, mock_session):
        from arc_see.mcp_server import reset, step
        reset()
        result = step("ACTION1")
        assert "ACTION1" in result

    def test_reflect(self, mock_session):
        from arc_see.mcp_server import reset, step, reflect
        reset()
        step("ACTION1")
        result = reflect()
        assert "ACTION1" in result

    def test_status(self, mock_session):
        from arc_see.mcp_server import reset, status
        reset()
        result = status()
        assert "test-game" in result.lower() or "TEST" in result
```

- [ ] **Step 2: Run tests**

Run: `uv run pytest tests/test_mcp_server.py -v`
Expected: All 5 tests PASS

- [ ] **Step 3: Commit**

```bash
git add tests/test_mcp_server.py
git commit -m "test: MCP server tool tests"
```

---

### Task 5: Delete old agent/graph/runner and their tests

**Files:**
- Delete: `arc_see/agent.py`
- Delete: `arc_see/graph.py`
- Delete: `arc_see/runner.py`
- Delete: `tests/test_agent.py`
- Delete: `tests/test_graph.py`
- Delete: `tests/test_integration.py`

- [ ] **Step 1: Delete the files**

```bash
git rm arc_see/agent.py arc_see/graph.py arc_see/runner.py
git rm tests/test_agent.py tests/test_graph.py tests/test_integration.py
```

- [ ] **Step 2: Verify remaining tests still pass**

Run: `uv run pytest tests/ -v`
Expected: All remaining tests pass (lens tests + new session/mcp tests). No imports of agent/graph/runner.

- [ ] **Step 3: Commit**

```bash
git commit -m "refactor: remove heuristic agent, graph, runner — replaced by MCP server"
```

---

### Task 6: Add MCP server configuration for Claude Code

**Files:**
- Create: `.mcp.json` (project-level MCP config so Claude Code auto-connects)

- [ ] **Step 1: Create .mcp.json**

Create `.mcp.json` in the project root:

```json
{
  "mcpServers": {
    "arc-see": {
      "command": "uv",
      "args": ["run", "python", "-m", "arc_see.mcp_server", "ls20-9607627b"],
      "type": "stdio"
    }
  }
}
```

Note: The game_id is hardcoded to `ls20-9607627b` for initial testing. Change it to play other games.

- [ ] **Step 2: Verify the full test suite passes**

Run: `uv run pytest tests/ -q`
Expected: All tests pass.

- [ ] **Step 3: Commit**

```bash
git add .mcp.json
git commit -m "feat: MCP config — Claude Code auto-connects to arc-see server"
```
