#!/usr/bin/env python3
"""SK48 L7 — Test block loading mechanics."""

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

def print_rows(grid, rows, label=""):
    if label:
        print(f"  {label}")
    for r in rows:
        row_str = ''
        for c in range(grid.shape[1]):
            row_str += CHARS[grid[r, c]]
        print(f"  {r:2d}: {row_str}")

def find_color(grid, color):
    return list(zip(*np.where(grid == color)))

# Test 1: Extend rack right multiple times, then move up
print("=== TEST 1: Extend right 3x, then up ===")
env, g, obs = replay_to_l7()
grid = get_grid(obs)
print("Initial rows 27-30 (cage area + blocks):")
print_rows(grid, range(27, 31))

# Extend right 3 times
for i in range(3):
    obs = env.step(GameAction.ACTION4, data={})
    grid = get_grid(obs)
    print(f"\nAfter ACTION4 #{i+1}:")
    print_rows(grid, [28, 29])

# Now move up
obs = env.step(GameAction.ACTION1, data={})
grid = get_grid(obs)
print(f"\nAfter ACTION1 (up):")
print_rows(grid, range(20, 32))

# Move up again
obs = env.step(GameAction.ACTION1, data={})
grid = get_grid(obs)
print(f"\nAfter ACTION1 again:")
print_rows(grid, range(14, 28))

# Now try ACTION3 (eject left) to see what's on the rack
obs = env.step(GameAction.ACTION3, data={})
grid = get_grid(obs)
print(f"\nAfter ACTION3 (eject left):")
print_rows(grid, range(14, 28))
print("Target rows:")
print_rows(grid, range(56, 62))

# Test 2: Move up first (to block level), then extend right INTO block
print("\n\n=== TEST 2: Move up 1x, then extend right ===")
env, g, obs = replay_to_l7()
grid = get_grid(obs)

# Move up once to approach the block area
obs = env.step(GameAction.ACTION1, data={})
grid = get_grid(obs)
print("After ACTION1:")
print_rows(grid, range(20, 32))

# Extend right
obs = env.step(GameAction.ACTION4, data={})
grid = get_grid(obs)
print("\nAfter ACTION4:")
print_rows(grid, range(20, 32))

# Extend right again
obs = env.step(GameAction.ACTION4, data={})
grid = get_grid(obs)
print("\nAfter ACTION4 again:")
print_rows(grid, range(20, 32))

# Test 3: Down to check lower area
print("\n\n=== TEST 3: Move down, explore ===")
env, g, obs = replay_to_l7()
grid = get_grid(obs)

obs = env.step(GameAction.ACTION2, data={})
grid = get_grid(obs)
print("After ACTION2 (down):")
print_rows(grid, range(30, 42))

obs = env.step(GameAction.ACTION2, data={})
grid = get_grid(obs)
print("\nAfter ACTION2 again:")
print_rows(grid, range(36, 48))

# Test 4: Click on the 8 block itself
print("\n\n=== TEST 4: Various clicks ===")
for desc, cx, cy in [
    ("8 block top-left (21,24)", 24, 21),
    ("9 block top-left (21,30)", 30, 21),
    ("scan column 2 (10,7)", 7, 10),
    ("scan column 3 (12,7)", 7, 12),
    ("empty field (14,24)", 24, 14),
    ("background 5 (0,0)", 0, 0),
]:
    env, g, obs = replay_to_l7()
    grid0 = get_grid(obs)
    obs = env.step(GameAction.ACTION6, data={'x': cx, 'y': cy})
    grid = get_grid(obs)
    diff = np.sum(grid0 != grid)
    print(f"  Click {desc}: {diff} cells changed")
    if diff > 0 and diff <= 20:
        changed = list(zip(*np.where(grid0 != grid)))
        for r, c in changed:
            print(f"    ({r},{c}): {CHARS[grid0[r,c]]} -> {CHARS[grid[r,c]]}")

# Test 5: Try multiple RIGHT extensions to see how far the rack goes
print("\n\n=== TEST 5: Extend rack as far as possible ===")
env, g, obs = replay_to_l7()
grid = get_grid(obs)

for i in range(8):
    prev = grid.copy()
    obs = env.step(GameAction.ACTION4, data={})
    grid = get_grid(obs)
    diff = np.sum(prev != grid)
    # Find rightmost color 1 or 2 in rows 28-29
    right_edge = 0
    for c in range(63, -1, -1):
        if grid[28, c] in [1, 2] or grid[29, c] in [1, 2]:
            right_edge = c
            break
    print(f"  ACTION4 #{i+1}: {diff} cells changed, rack right edge at col {right_edge}")
    if diff == 0:
        print("    (no more extension possible)")
        break

# Show final rack state
print("\nFinal rack state:")
print_rows(grid, [28, 29])
