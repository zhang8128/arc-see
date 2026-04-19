#!/usr/bin/env python3
"""SK48 L7 — Test various click positions for submit/win trigger."""

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
      'ACTION3': GameAction.ACTION3, 'ACTION4': GameAction.ACTION4,
      'ACTION6': GameAction.ACTION6, 'ACTION7': GameAction.ACTION7}

def create_env_and_solve():
    """Create env, replay to L7, execute the 28-step solution."""
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

    # Execute 28-step solution
    abstract_path = "HR HR HU VL VD VR HD HD VD HR HR VR VD VL HR HR HL HL HL HL HL HU HR HR VD VU HL VU".split()
    action_map_h = {'HR': 'ACTION4', 'HL': 'ACTION3', 'HU': 'ACTION1', 'HD': 'ACTION2'}
    action_map_v = {'VD': 'ACTION2', 'VU': 'ACTION1', 'VL': 'ACTION3', 'VR': 'ACTION4'}

    current = 'H'
    def click_cage(cage_name):
        level = env._game._levels[env._game._current_level_index]
        for s in level._sprites:
            if hasattr(s, 'tags') and 'sys_click' in s.tags and s.y < 54:
                colors = {int(px) for row in s.pixels for px in row if px != -1}
                if cage_name == 'cage15' and 15 in colors:
                    return env.step(GameAction.ACTION6, data={'x': s.x+2, 'y': s.y+2})
                elif cage_name == 'cage6' and 6 in colors:
                    return env.step(GameAction.ACTION6, data={'x': s.x+2, 'y': s.y+2})
        return None

    for a in abstract_path:
        rack = a[0]
        if rack != current:
            if rack == 'V': click_cage('cage15')
            else: click_cage('cage6')
            current = rack
        am = action_map_h if rack == 'H' else action_map_v
        obs = env.step(AM[am[a]], data={})

    # Switch back to cage6
    if current != 'H':
        click_cage('cage6')

    return env, obs

# Test various click positions
print("Testing click positions after solution...")

click_targets = [
    (49, 4, "L6 submit position"),
    (31, 4, "cage15 initial"),
    (7, 28, "cage6 interior"),
    (7, 34, "L6 scan click"),
    (11, 56, "target slot"),
    (32, 32, "center field"),
    (7, 8, "top-left scan"),
    (29, 8, "V-rack block pos"),
    (17, 26, "e-block pos"),
    (11, 26, "9-block pos"),
    (23, 26, "9-block pos 2"),
]

for cx, cy, desc in click_targets:
    env, obs = create_env_and_solve()
    g = env._game
    grid_before = np.array(obs.frame[-1], dtype=np.int64)
    obs = env.step(GameAction.ACTION6, data={'x': cx, 'y': cy})
    grid_after = np.array(obs.frame[-1], dtype=np.int64)
    diff = np.sum(grid_before != grid_after)
    print(f"  Click ({cx:2d},{cy:2d}) {desc}: {diff} cells changed, state={obs.state}, level={g._current_level_index}")
    if obs.state == GameState.WIN or g._current_level_index > 6:
        print(f"  *** WIN! ***")
        break

# Also test: what if we need hns and vns to be exactly right?
# L6 had a specific segment count for win. Let me try adjusting.
print("\n\nTesting different hns/vns values...")
# After solution: hns=3, vns=3. Try reducing to hns=1, vns=1 (like initial)
env, obs = create_env_and_solve()
g = env._game
# HL twice to reduce hns from 3 to 1
obs = env.step(AM['ACTION3'], data={})  # HL
obs = env.step(AM['ACTION3'], data={})  # HL
grid = np.array(obs.frame[-1], dtype=np.int64)
print(f"After 2x HL (hns=1): state={obs.state}")

# Switch to V, VU twice to reduce vns from 3 to 1
env2, obs2 = create_env_and_solve()
g2 = env2._game
level = g2._levels[g2._current_level_index]
for s in level._sprites:
    if hasattr(s, 'tags') and 'sys_click' in s.tags and s.y < 54:
        colors = {int(px) for row in s.pixels for px in row if px != -1}
        if 15 in colors:
            obs2 = env2.step(GameAction.ACTION6, data={'x': s.x+2, 'y': s.y+2})
            break
obs2 = env2.step(AM['ACTION1'], data={})  # VU
obs2 = env2.step(AM['ACTION1'], data={})  # VU
print(f"After 2x VU (vns=1): state={obs2.state}")
