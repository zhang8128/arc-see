#!/usr/bin/env python3
"""SK48 L7 — Independent action tests from fresh L7 state."""

import numpy as np
import copy
import arc_agi
from arcengine import GameAction, GameState

GA = {
    'U': GameAction.ACTION1, 'D': GameAction.ACTION2,
    'L': GameAction.ACTION3, 'R': GameAction.ACTION4,
}
AM = {
    'ACTION1': GameAction.ACTION1, 'ACTION2': GameAction.ACTION2,
    'ACTION3': GameAction.ACTION3, 'ACTION4': GameAction.ACTION4,
    'ACTION6': GameAction.ACTION6, 'ACTION7': GameAction.ACTION7,
}

SOLUTIONS = {
    1: "UUURRRRLDDRLUR",
    2: "RRRRUUULLURRDDRURLLURRLLURR",
    3: "RRUUUURDDLDRRRRLLLLUUUURDDDLUUUUR",
    4: "RRUUUULLLLDRURDRURRDLLU",
    5: "LULLRRRRRURRDLLLLDDLDRRRRLURDRLUR",
}

L6_SEQ = [
    ('A', 'ACTION2'), ('A', 'ACTION4'), ('A', 'ACTION4'), ('A', 'ACTION4'),
    ('C', 31, 4),
    ('A', 'ACTION2'), ('A', 'ACTION2'), ('A', 'ACTION4'), ('A', 'ACTION2'),
    ('A', 'ACTION1'), ('A', 'ACTION4'), ('A', 'ACTION2'), ('A', 'ACTION1'),
    ('A', 'ACTION4'), ('A', 'ACTION2'),
    ('C', 7, 34),
    ('A', 'ACTION4'), ('A', 'ACTION4'), ('A', 'ACTION4'), ('A', 'ACTION3'),
    ('A', 'ACTION3'), ('A', 'ACTION3'), ('A', 'ACTION3'), ('A', 'ACTION2'),
    ('A', 'ACTION2'), ('A', 'ACTION4'), ('A', 'ACTION1'), ('A', 'ACTION3'),
    ('A', 'ACTION1'), ('A', 'ACTION4'),
    ('C', 49, 4),
    ('A', 'ACTION3'), ('A', 'ACTION3'), ('A', 'ACTION2'), ('A', 'ACTION2'),
    ('A', 'ACTION2'),
]

CHARS = '0123456789abcdef'

def grid_str(grid):
    lines = []
    for r in range(grid.shape[0]):
        row_str = ''
        for c in range(grid.shape[1]):
            v = grid[r, c]
            row_str += CHARS[v] if v < 16 else '?'
        lines.append(f"  {r:2d}: {row_str}")
    return '\n'.join(lines)

def replay_to_l7():
    """Create a fresh env and replay to L7. Returns (env, game, obs, total_actions)."""
    arcade = arc_agi.Arcade()
    env = arcade.make("sk48-41055498", render_mode=None)
    g = env._game
    obs = env.reset()
    total = 0
    for lvl in range(1, 6):
        for c in SOLUTIONS[lvl]:
            obs = env.step(GA[c], data={})
            total += 1
    for item in L6_SEQ:
        if item[0] == 'C':
            obs = env.step(GameAction.ACTION6, data={'x': item[1], 'y': item[2]})
        else:
            obs = env.step(AM[item[1]], data={})
        total += 1
    return env, g, obs, total

def get_grid(obs):
    return np.array(obs.frame[-1], dtype=np.int64)

def diff_grids(g1, g2, label=""):
    mask = g1 != g2
    changed = list(zip(*np.where(mask)))
    print(f"  Cells changed: {len(changed)}")
    if len(changed) <= 50:
        for r, c in changed:
            print(f"    ({r:2d},{c:2d}): {CHARS[g1[r,c]]} -> {CHARS[g2[r,c]]}")
    return changed

def find_color(grid, color):
    return list(zip(*np.where(grid == color)))

# Get L7 initial state
print("Replaying to L7...")
env, g, obs, total = replay_to_l7()
init_grid = get_grid(obs)
print(f"At L7, {total} actions used for replay")

# Show initial grid
print("\n=== L7 INITIAL GRID ===")
print(grid_str(init_grid))

# Annotate the grid
print("\n=== L7 STRUCTURE ===")
print("Upper playing field (rows 0-52):")
print("  Cage 15 (f): rows 2-7, cols 29-34 — top structure")
print("  Left rack: rows 4-5, sequence of 2/3 blocks")
print("  Vertical scan column: rows 8-48, cols 7-8 (alternating 2/3)")
print("  Player cage (6/0): rows 26-31, cols 5-10")
print(f"  Player (1) at: {find_color(init_grid, 1)[:5]}...")
print(f"  Block 8 positions: {find_color(init_grid, 8)[:5]}...")
print(f"  Block 9 positions: {find_color(init_grid, 9)[:5]}...")
print(f"  Block 14 positions: {find_color(init_grid, 14)[:5]}...")

print("\nTarget (rows 53-63):")
print("  Row 53 border")
for r in range(54, 64):
    row = ''
    for c in range(64):
        row += CHARS[init_grid[r, c]]
    print(f"  {r}: {row}")

# Test each action INDEPENDENTLY from fresh L7 state
print("\n=== INDEPENDENT ACTION TESTS ===")

for action_name in ['ACTION1', 'ACTION2', 'ACTION3', 'ACTION4', 'ACTION7']:
    print(f"\n--- {action_name} from initial state ---")
    env2, g2, obs2, _ = replay_to_l7()
    base = get_grid(obs2)

    obs3 = env2.step(AM[action_name], data={})
    after = get_grid(obs3)

    print(f"  Player before: {find_color(base, 1)[:5]}")
    print(f"  Player after:  {find_color(after, 1)[:5]}")
    diff_grids(base, after)

    if g2._current_level_index != 6:
        print(f"  *** LEVEL CHANGED ***")

# Test clicks on each cage/structure
print("\n=== CLICK TESTS ===")

# Click on cage 15 (top cage)
for target_label, click_y, click_x in [
    ("cage 15 interior", 4, 31),  # inside the f-cage
    ("cage 6 interior", 28, 7),   # inside the 6-cage
    ("block 8", 21, 24),          # 8 block
    ("block 9", 21, 30),          # 9 block
    ("block 14", 33, 36),         # e block
    ("target area", 58, 12),      # target 9 block area
]:
    print(f"\n--- Click {target_label} at (y={click_y}, x={click_x}) ---")
    env2, g2, obs2, _ = replay_to_l7()
    base = get_grid(obs2)

    obs3 = env2.step(GameAction.ACTION6, data={'x': click_x, 'y': click_y})
    after = get_grid(obs3)
    diff_grids(base, after)

# Test: ACTION1 then ACTION3 (up then left = push up, then pop left)
print("\n=== COMBO: UP then LEFT ===")
env2, g2, obs2, _ = replay_to_l7()
base = get_grid(obs2)

obs3 = env2.step(GameAction.ACTION1, data={})
mid = get_grid(obs3)
print("After ACTION1 (up):")
print(f"  Player: {find_color(mid, 1)[:5]}")

obs4 = env2.step(GameAction.ACTION3, data={})
after = get_grid(obs4)
print("After ACTION3 (left):")
print(f"  Player: {find_color(after, 1)[:5]}")
diff_grids(mid, after)

# Print the full grid after combo
print("\nGrid after UP+LEFT:")
print(grid_str(after))

# Test: click cage15, then move
print("\n=== COMBO: Click cage15 then ACTION1 ===")
env2, g2, obs2, _ = replay_to_l7()
base = get_grid(obs2)

obs3 = env2.step(GameAction.ACTION6, data={'x': 31, 'y': 4})
mid = get_grid(obs3)
print("After click cage15 at (4,31):")
diff_grids(base, mid)
print(f"  Player: {find_color(mid, 1)[:5]}")

obs4 = env2.step(GameAction.ACTION1, data={})
after = get_grid(obs4)
print("After ACTION1 (up):")
print(f"  Player: {find_color(after, 1)[:5]}")
diff_grids(mid, after)
