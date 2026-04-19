#!/usr/bin/env python3
"""SK48 L7 — Test loading and ejecting blocks."""

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

def print_rows(grid, rows, cols=None):
    for r in rows:
        if r < 0 or r >= grid.shape[0]:
            continue
        row_str = ''
        c_range = range(grid.shape[1]) if cols is None else cols
        for c in c_range:
            row_str += CHARS[grid[r, c]]
        print(f"  {r:2d}: {row_str}")

def print_target(grid):
    print("  Target (rows 56-61):")
    print_rows(grid, range(56, 62))

# Test A: Load rack with lower blocks, then eject
print("=== TEST A: Push lower blocks onto rack, then eject ===")
env, g, obs = replay_to_l7()
grid = get_grid(obs)
actions = 0

# The lower blocks (9 at cols 24-27, 8 at cols 30-33) are at rows 27-30
# (same as rack rows 28-29). Extend right to push them.
print("Extending right to push lower blocks onto rack:")
for i in range(6):
    obs = env.step(GameAction.ACTION4, data={})
    grid = get_grid(obs)
    actions += 1
    # Show rack row
    r28 = ''.join(CHARS[grid[28, c]] for c in range(64))
    print(f"  R#{i+1}: row28={r28[10:55]}")

# Now eject
print(f"\nRack before eject (row 28, cols 10-52):")
print(f"  {''.join(CHARS[grid[28,c]] for c in range(10, 53))}")
print(f"  {''.join(CHARS[grid[29,c]] for c in range(10, 53))}")

obs = env.step(GameAction.ACTION3, data={})
grid = get_grid(obs)
actions += 1
print(f"\nAfter eject (ACTION3):")
print(f"  Rack row 28: {''.join(CHARS[grid[28,c]] for c in range(5, 55))}")
print_target(grid)
print(f"  Actions used: {actions}")

# Check if target matches
print(f"\n  Level index: {g._current_level_index}")

# Test B: Move up to absorb upper blocks, then push with lower, then eject
print("\n\n=== TEST B: Move up to upper blocks, extend, move back down, extend, eject ===")
env, g, obs = replay_to_l7()
grid = get_grid(obs)
actions = 0

# Move up to align with upper blocks (rows 21-24: 8 at 24-27, 9 at 30-33)
obs = env.step(GameAction.ACTION1, data={})
grid = get_grid(obs)
actions += 1
print("After UP:")
print_rows(grid, range(20, 26))

# Extend right to push upper blocks
for i in range(3):
    obs = env.step(GameAction.ACTION4, data={})
    grid = get_grid(obs)
    actions += 1
print(f"\nAfter 3x RIGHT:")
print_rows(grid, range(20, 32))

# Move back down to original position
obs = env.step(GameAction.ACTION2, data={})
grid = get_grid(obs)
actions += 1
print(f"\nAfter DOWN:")
print_rows(grid, range(26, 32))

# The rack should now have the upper blocks loaded. Check:
r28 = ''.join(CHARS[grid[28, c]] for c in range(64))
print(f"\nRow 28 rack: {r28[10:45]}")

# Eject
obs = env.step(GameAction.ACTION3, data={})
grid = get_grid(obs)
actions += 1
print(f"\nAfter eject:")
print_target(grid)
print(f"  Actions: {actions}")

# Test C: What happens with repeated ejects?
print("\n\n=== TEST C: Multiple ejects from loaded rack ===")
env, g, obs = replay_to_l7()
grid = get_grid(obs)
actions = 0

# Extend right 4 times to load blocks
for _ in range(4):
    obs = env.step(GameAction.ACTION4, data={})
    actions += 1
grid = get_grid(obs)
print(f"Rack loaded (4x RIGHT):")
print(f"  row28: {''.join(CHARS[grid[28,c]] for c in range(10, 50))}")

# Eject multiple times
for i in range(4):
    obs = env.step(GameAction.ACTION3, data={})
    grid = get_grid(obs)
    actions += 1
    print(f"\nAfter eject #{i+1}:")
    print(f"  row28: {''.join(CHARS[grid[28,c]] for c in range(10, 50))}")
    print(f"  target row58: {''.join(CHARS[grid[58,c]] for c in range(5, 35))}")

# Test D: Switch to cage15 and explore
print("\n\n=== TEST D: Cage 15 exploration ===")
env, g, obs = replay_to_l7()
grid = get_grid(obs)
actions = 0

# Click cage15 to switch
obs = env.step(GameAction.ACTION6, data={'x': 31, 'y': 4})
grid = get_grid(obs)
actions += 1
print("After clicking cage15:")
print_rows(grid, range(2, 14))

# Find player
p1 = list(zip(*np.where(grid == 1)))
print(f"\nPlayer positions: {p1}")

# Try extending right (ACTION4)
obs = env.step(GameAction.ACTION4, data={})
grid = get_grid(obs)
actions += 1
print("\nAfter ACTION4 (right):")
print_rows(grid, range(2, 14))

# Try extending more
for i in range(5):
    obs = env.step(GameAction.ACTION4, data={})
    grid = get_grid(obs)
    actions += 1
print(f"\nAfter 5 more RIGHT:")
print_rows(grid, range(2, 14))

# Try ACTION1 (up = eject for top rack?)
obs = env.step(GameAction.ACTION1, data={})
grid = get_grid(obs)
actions += 1
print(f"\nAfter ACTION1 (up/eject?):")
print_rows(grid, range(2, 14))
print_target(grid)

# Try moving down with rack loaded
print("\n\n=== TEST E: Cage15 - load then eject ===")
env, g, obs = replay_to_l7()
grid = get_grid(obs)
actions = 0

# Switch to cage15
obs = env.step(GameAction.ACTION6, data={'x': 31, 'y': 4})
grid = get_grid(obs)
actions += 1

# Move down to reach e-block (rows 33-36)
obs = env.step(GameAction.ACTION2, data={})
grid = get_grid(obs)
actions += 1
print("Cage15 after DOWN:")
print_rows(grid, range(8, 20))

obs = env.step(GameAction.ACTION2, data={})
grid = get_grid(obs)
actions += 1
print("\nCage15 after 2nd DOWN:")
print_rows(grid, range(14, 26))

obs = env.step(GameAction.ACTION2, data={})
grid = get_grid(obs)
actions += 1
print("\nCage15 after 3rd DOWN:")
print_rows(grid, range(20, 32))

obs = env.step(GameAction.ACTION2, data={})
grid = get_grid(obs)
actions += 1
print("\nCage15 after 4th DOWN:")
print_rows(grid, range(26, 42))

# Now extend right to reach e-block
for i in range(5):
    obs = env.step(GameAction.ACTION4, data={})
    grid = get_grid(obs)
    actions += 1

p1 = list(zip(*np.where(grid == 1)))
print(f"\nAfter 5x RIGHT, player: {p1[:5]}...")
print_rows(grid, range(32, 42))
