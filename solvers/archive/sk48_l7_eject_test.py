#!/usr/bin/env python3
"""SK48 L7 — Test ejection mechanics and win condition.

Key question: does ejecting from a loaded rack WRITE to the target area?
If so, the win condition is likely about the target area matching a goal pattern.
"""

import numpy as np
import arc_agi
from arcengine import GameAction, GameState

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

GA = {'U': GameAction.ACTION1, 'D': GameAction.ACTION2, 'L': GameAction.ACTION3, 'R': GameAction.ACTION4}
AM = {'ACTION1': GameAction.ACTION1, 'ACTION2': GameAction.ACTION2,
      'ACTION3': GameAction.ACTION3, 'ACTION4': GameAction.ACTION4, 'ACTION6': GameAction.ACTION6}

CHARS = '0123456789abcdef'

def create_env():
    arcade = arc_agi.Arcade()
    env = arcade.make("sk48-41055498", render_mode=None)
    obs = env.reset()
    for lvl in range(1, 6):
        for c in SOLUTIONS[lvl]:
            obs = env.step(GA[c], data={})
    for item in L6_SEQ:
        if item[0] == 'C':
            obs = env.step(GameAction.ACTION6, data={'x': item[1], 'y': item[2]})
        else:
            obs = env.step(AM[item[1]], data={})
    return env, obs

def show_target(grid, label=""):
    if label:
        print(f"  {label}")
    for r in range(56, 62):
        print(f"    {r}: {''.join(CHARS[grid[r,c]] for c in range(5, 60))}")

def show_hracks(grid, label=""):
    """Show H-rack area (rows around the cage6 area)."""
    if label:
        print(f"  {label}")
    for r in range(20, 32):
        s = ''.join(CHARS[grid[r,c]] for c in range(5, 45))
        print(f"    {r}: {s}")

# Test 1: Load H-rack with 9 at slot 0, then eject. See what happens to target.
print("=== TEST 1: Load 9 at H-rack slot 0, eject ===")
env, obs = create_env()
grid0 = np.array(obs.frame[-1], dtype=np.int64)
print("Initial target:")
show_target(grid0)

# Use the 24-step solution's first part to get 9 at H-rack slot 0
# From the trace: after steps 1-24, 9 is at (11,26) and (23,26)
# Let me use a shorter sequence: just get one 9 to slot 0

# Strategy: extend H to cover slot 2 (pushing 9 from slot 2), then eject left 2x
# HR HR HR HL HL -> puts 9 from (23,26) to (11,26)
actions = [
    GameAction.ACTION4,  # HR: hns=2
    GameAction.ACTION4,  # HR: hns=3, pushes 9 from (23,26) to (29,26) and 8 cascade
    GameAction.ACTION4,  # HR: hns=4, pushes 9 from (29,26) to (35,26)
    GameAction.ACTION3,  # HL: hns=3, pushes 9 from (29,26) back? No...
]

# Actually let me just use the known working sequence up to the point where 9s are placed
# From the 24-step trace: at step 24, blocks are at (11,26,9), (23,26,9) plus others
# Let me replay that exact sequence
seq24 = "HR HR HU VL VD VR VR VD HR HR HR HL VD VD VD HL HL HD HR HL VL VU VU VU".split()

action_map_h = {'HR': 'ACTION4', 'HL': 'ACTION3', 'HU': 'ACTION1', 'HD': 'ACTION2'}
action_map_v = {'VD': 'ACTION2', 'VU': 'ACTION1', 'VL': 'ACTION3', 'VR': 'ACTION4'}

current = 'H'
total = 0
for a in seq24:
    rack = a[0]
    if rack != current:
        # Click to switch
        if rack == 'V':
            level = env._game._levels[env._game._current_level_index]
            for s in level._sprites:
                if hasattr(s, 'tags') and 'sys_click' in s.tags and s.y < 54:
                    colors = {int(px) for row in s.pixels for px in row if px != -1}
                    if 15 in colors:
                        obs = env.step(GameAction.ACTION6, data={'x': s.x+2, 'y': s.y+2})
                        total += 1
                        break
        else:
            level = env._game._levels[env._game._current_level_index]
            for s in level._sprites:
                if hasattr(s, 'tags') and 'sys_click' in s.tags and s.y < 54:
                    colors = {int(px) for row in s.pixels for px in row if px != -1}
                    if 6 in colors:
                        obs = env.step(GameAction.ACTION6, data={'x': s.x+2, 'y': s.y+2})
                        total += 1
                        break
        current = rack

    am = action_map_h if rack == 'H' else action_map_v
    obs = env.step(AM[am[a]], data={})
    total += 1

grid24 = np.array(obs.frame[-1], dtype=np.int64)
print(f"\nAfter 24-step solution ({total} game actions):")
print(f"  State: {obs.state}")
show_hracks(grid24, "H-rack area:")
show_target(grid24, "Target:")

# Now the 9s are at (11,26) and (23,26). Try additional actions:

# Test 2: From this state, try HL (eject left) to see if it writes to target
print("\n=== TEST 2: HL (eject) from state with 9s at correct H positions ===")
# Need to switch back to H-rack if not already
if current != 'H':
    level = env._game._levels[env._game._current_level_index]
    for s in level._sprites:
        if hasattr(s, 'tags') and 'sys_click' in s.tags and s.y < 54:
            colors = {int(px) for row in s.pixels for px in row if px != -1}
            if 6 in colors:
                obs = env.step(GameAction.ACTION6, data={'x': s.x+2, 'y': s.y+2})
                total += 1
                current = 'H'
                break

# First extend rack to cover slots
for _ in range(2):
    obs = env.step(GameAction.ACTION4, data={})  # HR
    total += 1

grid_before_eject = np.array(obs.frame[-1], dtype=np.int64)
show_hracks(grid_before_eject, "Before eject (H extended):")
show_target(grid_before_eject, "Target before eject:")

# Eject
obs = env.step(GameAction.ACTION3, data={})  # HL
total += 1
grid_after_eject = np.array(obs.frame[-1], dtype=np.int64)
show_hracks(grid_after_eject, "After 1 HL (eject):")
show_target(grid_after_eject, "Target after eject:")

print(f"\n  State: {obs.state}, Level: {env._game._current_level_index}")

# Compare target before and after eject
diff = np.where(grid_before_eject[54:64] != grid_after_eject[54:64])
if len(diff[0]) > 0:
    print(f"\n  Target area changes ({len(diff[0])} cells):")
    for i in range(min(20, len(diff[0]))):
        r, c = diff[0][i] + 54, diff[1][i]
        print(f"    ({r},{c}): {CHARS[grid_before_eject[r,c]]} -> {CHARS[grid_after_eject[r,c]]}")

# Test 3: Try ACTION7 at various points
print("\n\n=== TEST 3: ACTION7 effect ===")
env2, obs2 = create_env()
grid_before = np.array(obs2.frame[-1], dtype=np.int64)
obs2 = env2.step(GameAction.ACTION7, data={})
grid_after = np.array(obs2.frame[-1], dtype=np.int64)
diff = np.sum(grid_before != grid_after)
print(f"  ACTION7 from initial: {diff} cells changed")

# Try ACTION7 after loading rack
env2, obs2 = create_env()
for _ in range(3):
    obs2 = env2.step(GameAction.ACTION4, data={})  # 3x HR
obs2 = env2.step(GameAction.ACTION7, data={})
grid7 = np.array(obs2.frame[-1], dtype=np.int64)
diff2 = np.sum(np.array(obs2.frame[-2], dtype=np.int64) != grid7) if len(obs2.frame) > 1 else -1
print(f"  ACTION7 after 3xHR: checking for effect...")
show_hracks(grid7, "After 3xHR + ACTION7:")
