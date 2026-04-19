#!/usr/bin/env python3
"""SK48 L7 — Replay L1-L6, then explore L7."""

import numpy as np
import arc_agi
from arcengine import GameAction

GA = {
    'U': GameAction.ACTION1, 'D': GameAction.ACTION2,
    'L': GameAction.ACTION3, 'R': GameAction.ACTION4,
}
AM = {
    'ACTION1': GameAction.ACTION1, 'ACTION2': GameAction.ACTION2,
    'ACTION3': GameAction.ACTION3, 'ACTION4': GameAction.ACTION4,
    'ACTION6': GameAction.ACTION6,
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

arcade = arc_agi.Arcade()
env = arcade.make("sk48-41055498", render_mode=None)
g = env._game

obs = env.reset()
total = 0

# Replay L1-L5
for lvl in range(1, 6):
    for c in SOLUTIONS[lvl]:
        obs = env.step(GA[c], data={})
        total += 1
    print(f"L{lvl}: done ({total} total)")

# Replay L6
for item in L6_SEQ:
    if item[0] == 'C':
        obs = env.step(GameAction.ACTION6, data={'x': item[1], 'y': item[2]})
    else:
        obs = env.step(AM[item[1]], data={})
    total += 1
print(f"L6: done ({total} total)")
print(f"Now at level index: {g._current_level_index}")

# --- L7 exploration ---
print("\n=== L7 INITIAL STATE ===")
grid = np.array(obs.frame[-1], dtype=np.int64)
print(f"Grid shape: {grid.shape}")

# Color census
unique, counts = np.unique(grid, return_counts=True)
print("\nColor census:")
for c, n in sorted(zip(unique, counts), key=lambda x: -x[1]):
    print(f"  color {c}: {n} cells")

# Print compact grid
CHARS = '0123456789abcdef'
print("\nGrid (row x col):")
for r in range(grid.shape[0]):
    row_str = ''
    for c in range(grid.shape[1]):
        v = grid[r, c]
        row_str += CHARS[v] if v < 16 else '?'
    print(f"  {r:2d}: {row_str}")

# Find player (color 1)
player_pos = list(zip(*np.where(grid == 1)))
print(f"\nPlayer (color 1) cells: {player_pos}")

# Find other important colors
for color in [0, 2, 3, 6, 8, 9, 15]:
    positions = list(zip(*np.where(grid == color)))
    if positions:
        print(f"Color {color} cells ({len(positions)}): {positions[:10]}{'...' if len(positions) > 10 else ''}")

# Try each action from a FRESH start at L7
# We need to replay to L7 each time to test independently
print("\n=== ACTION EXPLORATION (sequential, non-independent) ===")
print("Starting from L7 initial state, taking actions sequentially:")

ACTIONS = ['ACTION1', 'ACTION2', 'ACTION3', 'ACTION4']
base_grid = grid.copy()
base_player = player_pos[:]

for name in ACTIONS:
    action = AM[name]
    obs2 = env.step(action, data={})
    grid2 = np.array(obs2.frame[-1], dtype=np.int64)
    total += 1

    diff_mask = base_grid != grid2
    changed_cells = list(zip(*np.where(diff_mask)))
    player_after = list(zip(*np.where(grid2 == 1)))

    print(f"\n{name}:")
    print(f"  Player: {base_player} -> {player_after}")
    print(f"  Cells changed: {len(changed_cells)}")
    if len(changed_cells) <= 40:
        for r, c in changed_cells:
            print(f"    ({r},{c}): {base_grid[r,c]} -> {grid2[r,c]}")

    if g._current_level_index != 6:
        print(f"  *** LEVEL CHANGED to {g._current_level_index} ***")

    base_grid = grid2.copy()
    base_player = player_after

# Now try a click on various positions
print("\n=== CLICK EXPLORATION ===")
grid_now = base_grid.copy()

# Find cells of interesting colors to click
for color in [0, 8, 9, 6, 15, 2, 3]:
    positions = list(zip(*np.where(grid_now == color)))
    if positions:
        r, c = positions[0]
        print(f"\nClicking color {color} at ({r},{c}):")
        obs3 = env.step(GameAction.ACTION6, data={'x': c, 'y': r})
        grid3 = np.array(obs3.frame[-1], dtype=np.int64)
        total += 1

        diff_mask = grid_now != grid3
        changed = list(zip(*np.where(diff_mask)))
        print(f"  Cells changed: {len(changed)}")
        if len(changed) <= 20:
            for cr, cc in changed:
                print(f"    ({cr},{cc}): {grid_now[cr,cc]} -> {grid3[cr,cc]}")

        grid_now = grid3.copy()

# Also try ACTION7
print("\n=== ACTION7 ===")
obs4 = env.step(GameAction.ACTION7, data={})
grid4 = np.array(obs4.frame[-1], dtype=np.int64)
total += 1
diff_mask = grid_now != grid4
changed = list(zip(*np.where(diff_mask)))
print(f"Cells changed: {len(changed)}")
if len(changed) <= 20:
    for r, c in changed:
        print(f"  ({r},{c}): {grid_now[r,c]} -> {grid4[r,c]}")

print(f"\nTotal actions used: {total}")
print(f"Level index: {g._current_level_index}")
print(f"Game state: {obs4.state}")
