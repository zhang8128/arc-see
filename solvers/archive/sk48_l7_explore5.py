#!/usr/bin/env python3
"""SK48 L7 — Test cage15 horizontal block pushing."""

import numpy as np
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

def row_str(grid, r, c_start=0, c_end=64):
    return ''.join(CHARS[grid[r,c]] for c in range(c_start, min(c_end, grid.shape[1])))

def find_blocks(grid, color):
    """Find bounding boxes of connected blocks of given color."""
    mask = grid == color
    if not mask.any():
        return []
    rows, cols = np.where(mask)
    # Simple: return min/max bounds
    return [(rows.min(), cols.min(), rows.max(), cols.max())]

def show_block_positions(grid, label=""):
    if label:
        print(f"  {label}")
    for color, name in [(8, '8'), (9, '9'), (14, 'e')]:
        positions = list(zip(*np.where(grid == color)))
        if positions:
            rs = [p[0] for p in positions]
            cs = [p[1] for p in positions]
            # Group by contiguous regions
            unique_row_ranges = []
            sorted_rs = sorted(set(rs))
            if sorted_rs:
                start = sorted_rs[0]
                end = sorted_rs[0]
                for r in sorted_rs[1:]:
                    if r <= end + 1:
                        end = r
                    else:
                        unique_row_ranges.append((start, end))
                        start = end = r
                unique_row_ranges.append((start, end))

            sorted_cs = sorted(set(cs))
            unique_col_ranges = []
            if sorted_cs:
                start = sorted_cs[0]
                end = sorted_cs[0]
                for c in sorted_cs[1:]:
                    if c <= end + 1:
                        end = c
                    else:
                        unique_col_ranges.append((start, end))
                        start = end = c
                unique_col_ranges.append((start, end))

            print(f"    {name}: rows {unique_row_ranges}, cols {unique_col_ranges}")

# Test 1: Use cage15 to push blocks LEFT
print("=== TEST 1: Cage15 push blocks left ===")
env, g, obs = replay_to_l7()
grid = get_grid(obs)

print("Initial block positions:")
show_block_positions(grid)

# Switch to cage15
obs = env.step(GameAction.ACTION6, data={'x': 31, 'y': 4})
grid = get_grid(obs)
actions = 1
print(f"\nAfter click cage15 (switch):")
show_block_positions(grid)

# Move cage15 DOWN to cover block rows
for i in range(4):
    obs = env.step(GameAction.ACTION2, data={})
    grid = get_grid(obs)
    actions += 1
print(f"\nAfter 4x DOWN (extend scan to block area):")
show_block_positions(grid)

# Now move cage15 LEFT to push blocks left
for i in range(4):
    prev = grid.copy()
    obs = env.step(GameAction.ACTION3, data={})
    grid = get_grid(obs)
    actions += 1
    diff = np.sum(prev != grid)
    print(f"\n  ACTION3 (left) #{i+1}: {diff} cells changed")
    show_block_positions(grid)

# Test 2: Cage15 extend scan down, then move RIGHT to push blocks
print("\n\n=== TEST 2: Cage15 extend down, move RIGHT ===")
env, g, obs = replay_to_l7()
grid = get_grid(obs)

obs = env.step(GameAction.ACTION6, data={'x': 31, 'y': 4})
grid = get_grid(obs)

# Move down 4x
for _ in range(4):
    obs = env.step(GameAction.ACTION2, data={})

# Move right 4x
for i in range(4):
    obs = env.step(GameAction.ACTION4, data={})
    grid = get_grid(obs)
    print(f"  After RIGHT #{i+1}:")
    show_block_positions(grid)

# Test 3: Compare initial target to the IDEAL target
print("\n\n=== TEST 3: Target analysis ===")
env, g, obs = replay_to_l7()
grid = get_grid(obs)

print("Target left side (rows 57-60, cols 5-30):")
for r in range(57, 61):
    print(f"  {r}: {row_str(grid, r, 5, 30)}")

print("\nTarget right side (rows 57-60, cols 35-60):")
for r in range(57, 61):
    print(f"  {r}: {row_str(grid, r, 35, 60)}")

print("\nCurrent upper field (rows 20-37, cols 5-55):")
for r in range(20, 38):
    print(f"  {r}: {row_str(grid, r, 5, 55)}")

# Test 4: Try to match target - push lower 9 LEFT to col 12-15
# The lower 9 is at cols 24-27. Need it at cols 12-15 (shift left 12 = 2 scan widths)
# Use cage15 vertical scan to push it
print("\n\n=== TEST 4: Push lower-9 left via cage15 scan ===")
env, g, obs = replay_to_l7()
grid = get_grid(obs)

# Switch to cage15
obs = env.step(GameAction.ACTION6, data={'x': 31, 'y': 4})
grid = get_grid(obs)
actions = 1

# Move cage15 LEFT until the scan column is just RIGHT of the 9-block
# Cage15 scan is at cols 31-32 initially. 9-block is at cols 24-27.
# Moving left 1x = 6 cols left -> scan at cols 25-26 (overlaps with 9-block!)
# Moving left 2x -> scan at cols 19-20
# Let's first move scan to be at col 28 (just right of 9-block): no need, it's already at 31-32 which is right of 24-27

# But wait, we need to EXTEND the scan DOWN first to reach the block rows
# The vertical scan starts at row 8 (just below cage frame). Block 9 is at rows 27-30.
# Need to extend down ~19 rows = about 3 extensions

# Actually, let me check: each DOWN extends by 6 rows? Let me measure.
# From Test E: after 1 DOWN, scan went from rows 8-13 to rows 14-19
# Each DOWN extends by 6 rows.

# Block 9 at rows 27-30. Need scan to reach row 27+.
# Initial scan: rows 8-13 (6 rows from cage bottom at row 7)
# After 1 DOWN: rows 8-19 (covers through row 19)
# After 2 DOWN: rows 8-25 (covers through row 25)
# After 3 DOWN: rows 8-31 (covers through row 31 - passes block!)
# After 4 DOWN: rows 8-37

# Extend scan down to cover blocks
for i in range(3):
    obs = env.step(GameAction.ACTION2, data={})
    grid = get_grid(obs)
    actions += 1

print(f"After 3x DOWN (actions: {actions}):")
print("  Scan column area (rows 25-32, cols 24-34):")
for r in range(25, 33):
    print(f"    {r}: {row_str(grid, r, 24, 35)}")
show_block_positions(grid)

# Now move cage15 LEFT to push the 9 block (at cols 24-27) leftward
# Cage scan at cols 31-32. Moving left 1x puts scan at cols 25-26.
# This should PUSH the 9-block at cols 24-27 leftward? Or does it just go past it?

for i in range(6):
    prev = grid.copy()
    obs = env.step(GameAction.ACTION3, data={})
    grid = get_grid(obs)
    actions += 1
    diff = np.sum(prev != grid)
    print(f"\n  LEFT #{i+1} (actions: {actions}): {diff} cells changed")
    # Show block positions
    for color, name in [(9, '9')]:
        positions = list(zip(*np.where(grid == color)))
        if positions:
            cs = sorted(set(p[1] for p in positions))
            rs = sorted(set(p[0] for p in positions))
            print(f"    {name} at cols: {cs[:8]}, rows: {rs[:8]}")

# Test 5: Try the opposite - use cage15 to push blocks from LEFT to RIGHT
print("\n\n=== TEST 5: Direct attempt - move cage15 to LEFT of block, push RIGHT ===")
env, g, obs = replay_to_l7()
grid = get_grid(obs)

# Switch to cage15
obs = env.step(GameAction.ACTION6, data={'x': 31, 'y': 4})

# Move cage15 left until scan is to the LEFT of the 9-block (cols 24-27)
# Initial scan at cols 31-32. Need scan at cols ~23 (left of 24).
# Move left 2x: scan goes to cols 19-20
# But we also need scan to extend down to block rows first

# First extend down 3x
for _ in range(3):
    obs = env.step(GameAction.ACTION2, data={})

# Then move left 2x to get scan to ~cols 19-20
for _ in range(2):
    obs = env.step(GameAction.ACTION3, data={})
grid = get_grid(obs)

print(f"After 3 DOWN + 2 LEFT:")
show_block_positions(grid)
print("  Rows 25-32, cols 15-35:")
for r in range(25, 33):
    print(f"    {r}: {row_str(grid, r, 15, 35)}")

# Now push RIGHT — this should push blocks right
for i in range(3):
    obs = env.step(GameAction.ACTION4, data={})
    grid = get_grid(obs)
    print(f"\n  RIGHT #{i+1}:")
    show_block_positions(grid)
