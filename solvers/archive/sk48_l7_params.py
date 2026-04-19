#!/usr/bin/env python3
"""SK48 L7 — Extract exact game parameters for pure-Python solver."""

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

def replay_to_l7():
    arcade = arc_agi.Arcade()
    env = arcade.make("sk48-41055498", render_mode=None)
    g = env._game
    obs = env.reset()
    for lvl in range(1, 6):
        for c in SOLUTIONS[lvl]:
            obs = env.step(GA[c], data={})
    for item in L6_SEQ:
        if item[0] == 'C':
            obs = env.step(GameAction.ACTION6, data={'x': item[1], 'y': item[2]})
        else:
            obs = env.step(AM[item[1]], data={})
    return env, g, obs

def get_grid(obs):
    return np.array(obs.frame[-1], dtype=np.int64)

def find_blocks_precise(grid, color, row_range=None):
    """Find individual blocks of given color, return list of (top_row, left_col)."""
    if row_range:
        rows, cols = np.where(grid[row_range[0]:row_range[1]] == color)
        rows = rows + row_range[0]
    else:
        rows, cols = np.where(grid == color)
    if len(rows) == 0:
        return []

    # Group into connected blocks
    blocks = []
    visited = set()
    for r, c in zip(rows, cols):
        if (r, c) in visited:
            continue
        # BFS to find the block
        queue = [(r, c)]
        block_cells = []
        while queue:
            cr, cc = queue.pop(0)
            if (cr, cc) in visited:
                continue
            if grid[cr, cc] != color:
                continue
            visited.add((cr, cc))
            block_cells.append((cr, cc))
            for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
                nr, nc = cr+dr, cc+dc
                if 0 <= nr < grid.shape[0] and 0 <= nc < grid.shape[1]:
                    queue.append((nr, nc))

        min_r = min(r for r, c in block_cells)
        min_c = min(c for r, c in block_cells)
        max_r = max(r for r, c in block_cells)
        max_c = max(c for r, c in block_cells)
        blocks.append((min_r, min_c, max_r - min_r + 1, max_c - min_c + 1))

    return blocks

# Get initial state
env, g, obs = replay_to_l7()
grid = get_grid(obs)

print("=== L7 BLOCK POSITIONS ===")
print("\nUpper field (rows 0-52):")
for color, name in [(8, '8'), (9, '9'), (14, 'e')]:
    blocks = find_blocks_precise(grid, color, (0, 53))
    for r, c, h, w in blocks:
        print(f"  {name}: top-left=({r},{c}), size={h}x{w}")

print("\nTarget area (rows 53-63):")
for color, name in [(8, '8'), (9, '9'), (14, 'e')]:
    blocks = find_blocks_precise(grid, color, (53, 64))
    for r, c, h, w in blocks:
        print(f"  {name}: top-left=({r},{c}), size={h}x{w}")

# Extract rack parameters
print("\n=== RACK PARAMETERS ===")

# H-rack: find scan line pattern (colors 1,2) on row 28
print("\nH-rack (cage6) scan on row 28:")
for c in range(64):
    if grid[28, c] in [1, 2]:
        print(f"  col {c}: color {grid[28,c]}")

# V-rack: after clicking cage15, find scan column pattern
print("\nSwitching to cage15...")
obs2 = env.step(GameAction.ACTION6, data={'x': 31, 'y': 4})
grid2 = get_grid(obs2)

print("V-rack (cage15) scan at col 31:")
for r in range(64):
    if grid2[r, 31] in [1, 2]:
        print(f"  row {r}: color {grid2[r,31]}")

print("\nV-rack scan at col 32:")
for r in range(64):
    if grid2[r, 32] in [1, 2]:
        print(f"  row {r}: color {grid2[r,32]}")

# Check: what happens with multiple extensions and the slot positions
print("\n=== SLOT POSITION VERIFICATION ===")
# Extend H-rack several times and note where new segments appear
env3, _, obs3 = replay_to_l7()
grid3 = get_grid(obs3)

# Track the rightmost scan position after each extend
print("\nH-rack extension tracking:")
for i in range(8):
    obs3 = env3.step(GameAction.ACTION4, data={})
    grid3 = get_grid(obs3)
    # Find rightmost col with value 1 or 2 on row 28
    rightmost = 0
    for c in range(63, -1, -1):
        if grid3[28, c] in [1, 2]:
            rightmost = c
            break
    # Find leftmost non-4 after col 10
    leftmost = 64
    for c in range(11, 64):
        if grid3[28, c] != 4 and grid3[28, c] != 5:
            leftmost = c
            break
    print(f"  Extend #{i+1}: scan {leftmost}-{rightmost}")

# Now track V-rack extensions
print("\nV-rack extension tracking:")
env4, _, obs4 = replay_to_l7()
obs4 = env4.step(GameAction.ACTION6, data={'x': 31, 'y': 4})
grid4 = get_grid(obs4)

for i in range(8):
    obs4 = env4.step(GameAction.ACTION2, data={})
    grid4 = get_grid(obs4)
    # Find bottommost row with value 1 or 2 on col 31
    bottommost = 0
    for r in range(63, -1, -1):
        if grid4[r, 31] in [1, 2]:
            bottommost = r
            break
    topmost = 64
    for r in range(8, 64):
        if grid4[r, 31] in [1, 2]:
            topmost = r
            break
    print(f"  Extend #{i+1}: scan rows {topmost}-{bottommost}")

# Check field bounds precisely
print("\n=== FIELD BOUNDS ===")
# Find the extent of color 4 (field/background)
for r in range(64):
    row_4 = [c for c in range(64) if grid[r, c] == 4]
    if row_4:
        print(f"  Row {r}: color4 cols {min(row_4)}-{max(row_4)}")
        break

# Find field boundaries more precisely by looking at wall/boundary cells
print("\nField boundary detection:")
# Row range: find rows where the horizontal 4-field exists
field_rows = []
for r in range(64):
    count_4 = sum(1 for c in range(10, 55) if grid[r, c] == 4)
    if count_4 > 30:
        field_rows.append(r)
if field_rows:
    print(f"  Field rows: {min(field_rows)}-{max(field_rows)}")

# Col range
field_cols = []
for c in range(64):
    count_4 = sum(1 for r in range(8, 50) if grid[r, c] == 4)
    if count_4 > 20:
        field_cols.append(c)
if field_cols:
    print(f"  Field cols: {min(field_cols)}-{max(field_cols)}")

# Test: try a full solve sequence and check if it works
print("\n=== ATTEMPT SOLUTION ===")
env5, g5, obs5 = replay_to_l7()

# Strategy based on exploration:
# Phase 1: Use cage15 to position blocks
# Phase 2: Eject from both racks to fill target

# Phase 1: click cage15, down 3x, left 2x
steps = [
    ('C1', GameAction.ACTION6, {'x': 31, 'y': 4}),  # switch to cage15
    ('VD', GameAction.ACTION2, {}),  # extend V down
    ('VD', GameAction.ACTION2, {}),
    ('VD', GameAction.ACTION2, {}),
    ('VL', GameAction.ACTION3, {}),  # move V left
    ('VL', GameAction.ACTION3, {}),
]

total = 0
for name, action, data in steps:
    obs5 = env5.step(action, data=data)
    total += 1

grid5 = get_grid(obs5)
print(f"After Phase 1 ({total} actions):")
print("  Upper field blocks:")
for color, cname in [(8, '8'), (9, '9'), (14, 'e')]:
    blocks = find_blocks_precise(grid5, color, (0, 53))
    for r, c, h, w in blocks:
        print(f"    {cname}: ({r},{c}) {h}x{w}")

print(f"  Level: {g5._current_level_index}, State: {obs5.state}")

# Now switch back to cage6 and try extending + ejecting
obs5 = env5.step(GameAction.ACTION6, data={'x': 7, 'y': 28})
total += 1
grid5 = get_grid(obs5)

# Check if that worked (clicking cage6 interior when cage15 is active)
diff = np.sum(get_grid(obs5) != grid5)
print(f"\nAfter click cage6 ({total} actions): {diff} cells changed")

# Try extending H-rack to cover the blocks
for i in range(3):
    obs5 = env5.step(GameAction.ACTION4, data={})
    total += 1

grid5 = get_grid(obs5)
print(f"\nAfter 3x RIGHT ({total} actions):")
print(f"  Row 28 scan area: {''.join(CHARS[grid5[28,c]] for c in range(10, 30))}")

# Try ejecting
obs5 = env5.step(GameAction.ACTION3, data={})
total += 1
grid5 = get_grid(obs5)
print(f"\nAfter LEFT/eject ({total} actions):")
print(f"  Target row 58: {''.join(CHARS[grid5[58,c]] for c in range(5, 35))}")
print(f"  Level: {g5._current_level_index}, State: {obs5.state}")
