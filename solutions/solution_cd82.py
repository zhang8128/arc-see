"""Complete solution for CD82 (cd82-fb555c5d) — all 6 levels.

Painting puzzle: navigate 3x3 throw grid, select colors, throw paint.
Each throw paints a region of the 10x10 canvas. Win when canvas matches target.

Actions:
  ACTION1-4: navigate throw grid (left/right/up/down)
  ACTION5: throw from current position (paints half-canvas)
  ACTION6 with {x,y}: click color button or paddle arrow
"""
import importlib.util
import numpy as np
from arcengine import GameAction, ActionInput

# Load game to get camera coordinate mapping
spec = importlib.util.spec_from_file_location('cd82', 'environment_files/cd82/fb555c5d/cd82.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def get_display_coords(g, grid_x, grid_y):
    """Convert grid coordinates to display coordinates."""
    scale, xoff, yoff = g.camera._calculate_scale_and_offset()
    return int(grid_x * scale + xoff), int(grid_y * scale + yoff)


def get_paddle_display_coords(g):
    """Get display coords of the paddle arrow sprite."""
    for s in g.current_level.get_sprites():
        if s.name == "ctwspzkygu":
            scale, xoff, yoff = g.camera._calculate_scale_and_offset()
            dx = int((s.x + s.width // 2) * scale + xoff)
            dy = int((s.y + s.height // 2) * scale + yoff)
            return dx, dy
    return None, None


# Grid navigation: direction -> (col, row) in 3x3 grid
DIR_GRID = {0: (0,1), 1: (0,2), 2: (1,2), 3: (2,2),
            4: (2,1), 5: (2,0), 6: (1,0), 7: (0,0)}

def nav_path(from_dir, to_dir):
    """BFS to find ACTION1-4 sequence between grid positions."""
    if from_dir == to_dir:
        return []
    from collections import deque
    fc, fr = DIR_GRID[from_dir]
    tc, tr = DIR_GRID[to_dir]
    moves = {(-1,0): GameAction.ACTION1, (1,0): GameAction.ACTION2,
             (0,-1): GameAction.ACTION3, (0,1): GameAction.ACTION4}
    visited = {(fc, fr): []}
    queue = deque([(fc, fr)])
    while queue:
        c, r = queue.popleft()
        for (dc, dr), act in moves.items():
            nc, nr = c+dc, r+dr
            if 0 <= nc <= 2 and 0 <= nr <= 2 and (nc,nr) != (1,1) and (nc,nr) not in visited:
                path = visited[(c,r)] + [act]
                if (nc, nr) == (tc, tr):
                    return path
                visited[(nc, nr)] = path
                queue.append((nc, nr))
    return []


# Color button grid positions: {color: grid_x} (center pixel = grid_x+2, grid_y=4)
COLOR_BUTTONS_L12 = None  # determined per level
COLOR_BUTTONS_L36 = {0: 21, 15: 27, 12: 33, 11: 39, 14: 45, 8: 51, 9: 57}


def build_action_sequence(throw_sequence, level_num, local_game):
    """
    Convert throw sequence to list of (GameAction, data_or_None) pairs.
    Uses local_game to get display coordinate mapping.
    """
    g = local_game
    actions = []
    current_dir = 0  # start at direction 0
    current_color = 15  # default

    has_paddle = level_num >= 3

    # Determine color buttons for this level
    if has_paddle:
        color_buttons = COLOR_BUTTONS_L36
    else:
        buttons = [s for s in g.current_level.get_sprites() if s.name.startswith("pqkenviek")]
        color_buttons = {int(b.pixels[2, 2]): b.x for b in buttons}

    for (direction, color, throw_type) in throw_sequence:
        # Select color if needed
        if color != current_color:
            gx = color_buttons[int(color)] + 2  # center of 5x5 button
            gy = 2 + 2
            dx, dy = get_display_coords(g, gx, gy)
            actions.append((GameAction.ACTION6, {"x": dx, "y": dy}))
            current_color = int(color)

        # Navigate to direction
        for act in nav_path(current_dir, direction):
            actions.append((act, None))
        current_dir = direction

        # Execute throw
        if throw_type == "full":
            actions.append((GameAction.ACTION5, None))
        else:
            # Paddle click — need current paddle coords
            # Paddle position depends on direction, computed from game layout
            paddle_offsets = {
                0: (4, -6),   # basket(25,24) + offset
                2: (10, 4),   # basket(38,32) + offset
                4: (4, 10),   # basket(25,45) + offset
                6: (-6, 4),   # basket(17,32) + offset
            }
            nicoqsvlg = [
                (25, 24), None, (38, 32), None,
                (25, 45), None, (17, 32), None,
            ]
            bx, by = nicoqsvlg[direction]
            ox, oy = paddle_offsets[direction]
            # Paddle sprite is ctwspzkygu (6 wide, 5 tall)
            px, py = bx + ox, by + oy
            # Click center of paddle
            pcx = px + 3  # width=6, center=3
            pcy = py + 2  # height=5, center=2
            dx, dy = get_display_coords(g, pcx, pcy)
            actions.append((GameAction.ACTION6, {"x": dx, "y": dy}))

    return actions


# ─── Solutions from BFS solver ───
# Each level: list of (direction, color, throw_type) tuples

def get_solutions():
    """Pre-computed throw sequences for all levels (from BFS solver)."""
    return {
        1: [(4, 15, "full"), (0, 0, "full")],
        2: [(4, 0, "full"), (0, 15, "full"), (3, 12, "full")],
        3: [(2, 14, "full"), (6, 8, "full"), (7, 15, "full"), (0, 12, "paddle")],
        4: [(0, 12, "full"), (3, 15, "full"), (6, 9, "full"), (6, 11, "paddle")],
        5: [(0, 9, "full"), (5, 14, "full"), (3, 12, "full"), (0, 8, "paddle")],
        6: [(2, 14, "full"), (7, 8, "full"), (0, 15, "paddle"), (6, 11, "paddle")],
    }


def verify_with_api():
    """Verify all solutions using the real arc_agi API."""
    import arc_agi

    solutions = get_solutions()
    assert len(solutions) == 6, f"Only solved {len(solutions)}/6 levels"

    print("Solutions found:")
    for lv, seq in solutions.items():
        print(f"  Level {lv}: {seq}")

    # Create game instances
    arcade = arc_agi.Arcade()
    env = arcade.make("cd82-fb555c5d", render_mode=None)
    env.reset()

    # Local game for coordinate mapping
    g = mod.Cd82()
    g.full_reset()
    g.set_level(0)

    total_actions = 0

    for level_num in range(1, 7):
        level_idx = level_num - 1
        throw_seq = solutions[level_num]

        # Build actions
        action_seq = build_action_sequence(throw_seq, level_num, g)
        level_actions = len(action_seq)

        # Execute on real API
        for act_id, data in action_seq:
            if data:
                result = env.step(act_id, data=data)
            else:
                result = env.step(act_id)

        total_actions += level_actions
        print(f"Level {level_num}: {level_actions:3d} actions, levels_completed={result.levels_completed}")

        # Sync local game for next level's coordinate mapping
        if result.levels_completed >= level_num and level_num < 6:
            g.set_level(level_num)

    print(f"\nTotal: {total_actions} actions")
    print(f"Final state: {result.state}")

    if str(result.state) == "GameState.WIN":
        print("ALL VERIFIED! ✓")
        return True
    else:
        print(f"NOT COMPLETE: {result.levels_completed}/6 levels")
        return False


if __name__ == "__main__":
    verify_with_api()
