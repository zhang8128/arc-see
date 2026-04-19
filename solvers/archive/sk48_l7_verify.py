#!/usr/bin/env python3
"""SK48 L7 — Translate abstract solution to game actions and verify."""

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

GA = {
    'U': GameAction.ACTION1, 'D': GameAction.ACTION2,
    'L': GameAction.ACTION3, 'R': GameAction.ACTION4,
}
AM = {
    'ACTION1': GameAction.ACTION1, 'ACTION2': GameAction.ACTION2,
    'ACTION3': GameAction.ACTION3, 'ACTION4': GameAction.ACTION4,
    'ACTION6': GameAction.ACTION6,
}

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

# Abstract solution: VD VR VD VD VL HR HR HL HU HR VU VU VL VU VL VD VD VD VU
abstract_path = "VD VR VD VD VL HR HR HL HU HR VU VU VL VU VL VD VD VD VU".split()

# Map abstract actions to game actions
# H-rack actions (cage6 active):
#   HR = ACTION4 (extend right)
#   HL = ACTION3 (eject left)
#   HU = ACTION1 (move up)
#   HD = ACTION2 (move down)
# V-rack actions (cage15 active):
#   VD = ACTION2 (extend V down)
#   VU = ACTION1 (eject V up)
#   VL = ACTION3 (move V left)
#   VR = ACTION4 (move V right)

# We need to track which cage is active and add clicks to switch.
# Start: cage6 is active (H-rack)
# When we encounter a V action and H is active, click cage15 to switch.
# When we encounter an H action and V is active, click cage6 to switch.

# Click targets:
# cage15: initially at sprite (29,2) = grid (30,3). Click at (x=31, y=4).
# cage6: initially at sprite (5,20) = grid (6,21). Click at (x=7, y=22).
# But cage15 moves! After VL/VR, the cage15 position changes.
# We need to track cage15's position and click accordingly.

# For now, let's use fixed click positions and hope they work.
# If cage15 has moved, the click position needs to update.

# Actually, from the L6 solver, clicks were at specific positions.
# Let me try using the scan column click approach from L6.
# In L6: click at (7,34) switched from V back to H rack.

# Let's trace: cage15 starts at vrx=29 (sprite) = grid col 30.
# After VR: vrx=35 (sprite) = grid col 36.
# The cage15 frame is at x=vrx-2 to vrx+3 in sprite coords = col vrx-1 to vrx+4 in grid.
# At vrx=35: cage15 frame at grid cols 34-39. Click target at center = grid (36-37, 3-4)?
# But cage15 scan is at vrx+2 = 37 in sprite = grid 38.

# This is getting complicated. Let me try a different approach:
# Use the sys_click sprites to find the click targets dynamically.

def find_click_target(env, cage_name):
    """Find the click target for switching to a specific cage.
    Uses sys_click sprites from the UPPER field only (y < 54)."""
    g = env._game
    level = g._levels[g._current_level_index]
    for s in level._sprites:
        if not (hasattr(s, 'tags') and 'sys_click' in s.tags):
            continue
        if s.y >= 54:  # skip target area sprites
            continue
        colors = set()
        if hasattr(s, 'pixels'):
            for row in s.pixels:
                for px in row:
                    if px != -1:
                        colors.add(int(px))
        # cage15 has colors {4, 15}, cage6 has colors {0, 6}
        if cage_name == 'cage15' and 15 in colors:
            return s.x + 2, s.y + 2  # center of cage
        elif cage_name == 'cage6' and 6 in colors:
            return s.x + 2, s.y + 2
    return None

# Build the game action sequence
print("Building game action sequence...")
env, obs = create_env()
g = env._game

current_rack = 'H'  # Start with H-rack active (cage6)
game_actions = []
total = 0

for abstract_action in abstract_path:
    rack_type = abstract_action[0]  # 'H' or 'V'

    # Switch if needed
    if rack_type == 'V' and current_rack == 'H':
        # Need to switch to V-rack (click cage15)
        target = find_click_target(env, 'cage15')
        if target:
            cx, cy = target
            print(f"  Click cage15 at ({cx},{cy})")
            obs = env.step(GameAction.ACTION6, data={'x': cx, 'y': cy})
            game_actions.append(('C', cx, cy))
            total += 1
            current_rack = 'V'
        else:
            print("  ERROR: can't find cage15 click target!")
            break
    elif rack_type == 'H' and current_rack == 'V':
        # Need to switch to H-rack (click cage6)
        target = find_click_target(env, 'cage6')
        if target:
            cx, cy = target
            print(f"  Click cage6 at ({cx},{cy})")
            obs = env.step(GameAction.ACTION6, data={'x': cx, 'y': cy})
            game_actions.append(('C', cx, cy))
            total += 1
            current_rack = 'H'
        else:
            print("  ERROR: can't find cage6 click target!")
            break

    # Execute the action
    action_map = {
        'HR': 'ACTION4', 'HL': 'ACTION3', 'HU': 'ACTION1', 'HD': 'ACTION2',
        'VD': 'ACTION2', 'VU': 'ACTION1', 'VL': 'ACTION3', 'VR': 'ACTION4',
    }
    action_name = action_map[abstract_action]
    print(f"  {abstract_action} -> {action_name}")
    obs = env.step(AM[action_name], data={})
    game_actions.append(('A', action_name))
    total += 1

    # Check for win
    if obs.state == GameState.WIN or g._current_level_index > 6:
        print(f"\n*** WIN after {total} game actions! ***")
        break

print(f"\nTotal game actions: {total} (abstract: {len(abstract_path)}, clicks added)")
print(f"Final state: {obs.state}")
print(f"Level: {g._current_level_index}")

# Show the game action sequence
print("\nGame action sequence:")
for i, ga in enumerate(game_actions):
    if ga[0] == 'C':
        print(f"  {i+1}. Click ({ga[1]}, {ga[2]})")
    else:
        print(f"  {i+1}. {ga[1]}")

# Show final grid
CHARS = '0123456789abcdef'
grid = np.array(obs.frame[-1], dtype=np.int64)
print("\nFinal grid (rows 20-37):")
for r in range(20, 38):
    print(f"  {r}: {''.join(CHARS[grid[r,c]] for c in range(5, 55))}")
