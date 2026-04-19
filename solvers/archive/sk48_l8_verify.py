#!/usr/bin/env python3
"""SK48 L8 — Verify solution in game engine."""

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
    ('C', 31, 4), ('A', 'ACTION2'), ('A', 'ACTION2'), ('A', 'ACTION4'), ('A', 'ACTION2'),
    ('A', 'ACTION1'), ('A', 'ACTION4'), ('A', 'ACTION2'), ('A', 'ACTION1'),
    ('A', 'ACTION4'), ('A', 'ACTION2'), ('C', 7, 34),
    ('A', 'ACTION4'), ('A', 'ACTION4'), ('A', 'ACTION4'), ('A', 'ACTION3'),
    ('A', 'ACTION3'), ('A', 'ACTION3'), ('A', 'ACTION3'), ('A', 'ACTION2'),
    ('A', 'ACTION2'), ('A', 'ACTION4'), ('A', 'ACTION1'), ('A', 'ACTION3'),
    ('A', 'ACTION1'), ('A', 'ACTION4'), ('C', 49, 4),
    ('A', 'ACTION3'), ('A', 'ACTION3'), ('A', 'ACTION2'), ('A', 'ACTION2'),
    ('A', 'ACTION2'),
]

L7_ABSTRACT = "VD HR HR VR VD VD HR VD VD VD VU VU VU VU VL VU VL VL VD HL HL HL VD HU HR HR HR HR HR HR HL HL HL HL".split()
L8_ABSTRACT = "VD HR HR HR HL VD VR VD VL VD VD VD VU VU VU HR HR HR HR HR HL HL VU HL VD HL VU".split()

GA = {'U': GameAction.ACTION1, 'D': GameAction.ACTION2, 'L': GameAction.ACTION3, 'R': GameAction.ACTION4}
AM = {'ACTION1': GameAction.ACTION1, 'ACTION2': GameAction.ACTION2,
      'ACTION3': GameAction.ACTION3, 'ACTION4': GameAction.ACTION4, 'ACTION6': GameAction.ACTION6}

arcade = arc_agi.Arcade()
env = arcade.make("sk48-41055498", render_mode=None)
g = env._game
obs = env.reset()

# Replay L1-L5
for lvl in range(1, 6):
    for c in SOLUTIONS[lvl]:
        obs = env.step(GA[c], data={})
# L6
for item in L6_SEQ:
    if item[0] == 'C':
        obs = env.step(GameAction.ACTION6, data={'x': item[1], 'y': item[2]})
    else:
        obs = env.step(AM[item[1]], data={})

# Helper
action_map_h = {'HR': 'ACTION4', 'HL': 'ACTION3', 'HU': 'ACTION1', 'HD': 'ACTION2'}
action_map_v = {'VD': 'ACTION2', 'VU': 'ACTION1', 'VL': 'ACTION3', 'VR': 'ACTION4'}

def click_cage(cage_name):
    level = g._levels[g._current_level_index]
    for s in level._sprites:
        if hasattr(s, 'tags') and 'sys_click' in s.tags and s.y < 54:
            colors = {int(px) for row in s.pixels for px in row if px != -1}
            if cage_name == 'cage15' and 15 in colors:
                return env.step(GameAction.ACTION6, data={'x': s.x+2, 'y': s.y+2})
            elif cage_name == 'cage6' and 6 in colors:
                return env.step(GameAction.ACTION6, data={'x': s.x+2, 'y': s.y+2})
    return None

def run_abstract(abstract_path):
    current = 'H'
    total = 0
    for a in abstract_path:
        rack = a[0]
        if rack != current:
            if rack == 'V': click_cage('cage15')
            else: click_cage('cage6')
            total += 1
            current = rack
        am = action_map_h if rack == 'H' else action_map_v
        obs = env.step(AM[am[a]], data={})
        total += 1
    return obs, total

# L7
obs, l7_total = run_abstract(L7_ABSTRACT)
print(f"L7: {l7_total} actions, level={g._current_level_index}")

# L8
obs, l8_total = run_abstract(L8_ABSTRACT)
print(f"L8: {l8_total} actions, level={g._current_level_index}, state={obs.state}")

if g._current_level_index > 7:
    print(f"\n*** L8 SOLVED! Game at L{g._current_level_index+1}! ***")
else:
    print("\nL8 NOT solved. Checking blocks...")
    level = g._levels[g._current_level_index]
    for s in level._sprites:
        if hasattr(s, 'name') and s.name == 'elmjchdqcn' and s.y < 54:
            colors = {int(px) for row in s.pixels for px in row if px != -1 and px != -2}
            print(f"  Block at ({s.x},{s.y}) color={max(colors) if colors else '?'}")
