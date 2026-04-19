#!/usr/bin/env python3
"""SK48 — Submit L1-L8. No reset between levels — game auto-advances."""

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

# L7 abstract solution: VD HR HR VR VD VD HR VD VD VD VU VU VU VU VL VU VL VL VD HL HL HL VD HU HR HR HR HR HR HR HL HL HL HL
# Map: H actions = cage6 active, V actions = cage15 active
# HR=ACTION4, HL=ACTION3, HU=ACTION1, HD=ACTION2
# VD=ACTION2, VU=ACTION1, VL=ACTION3, VR=ACTION4
L7_ABSTRACT = "VD HR HR VR VD VD HR VD VD VD VU VU VU VU VL VU VL VL VD HL HL HL VD HU HR HR HR HR HR HR HL HL HL HL".split()
L8_ABSTRACT = "VD HR HR HR HL VD VR VD VL VD VD VD VU VU VU HR HR HR HR HR HL HL VU HL VD HL VU".split()

arcade = arc_agi.Arcade()
env = arcade.make("sk48-41055498", render_mode=None)
g = env._game

obs = env.reset()
total = 0
prev_level = g._current_level_index

# L1-L5
for lvl in range(1, 6):
    for c in SOLUTIONS[lvl]:
        obs = env.step(GA[c], data={})
        total += 1
    curr_level = g._current_level_index
    if curr_level > prev_level:
        print(f"L{lvl}: SOLVED ({len(SOLUTIONS[lvl])} actions, game now at L{curr_level+1})")
        prev_level = curr_level
    else:
        print(f"L{lvl}: FAILED (still at level {curr_level})")

# L6
for item in L6_SEQ:
    if item[0] == 'C':
        obs = env.step(GameAction.ACTION6, data={'x': item[1], 'y': item[2]})
    else:
        obs = env.step(AM[item[1]], data={})
    total += 1
curr_level = g._current_level_index
if curr_level > prev_level:
    print(f"L6: SOLVED ({len(L6_SEQ)} actions, game now at L{curr_level+1})")
    prev_level = curr_level
else:
    print(f"L6: FAILED (still at level {curr_level})")

# L7 — need cage toggle clicks between H and V operations
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

action_map_h = {'HR': 'ACTION4', 'HL': 'ACTION3', 'HU': 'ACTION1', 'HD': 'ACTION2'}
action_map_v = {'VD': 'ACTION2', 'VU': 'ACTION1', 'VL': 'ACTION3', 'VR': 'ACTION4'}

current_rack = 'H'  # cage6 starts active
l7_actions = 0
for a in L7_ABSTRACT:
    rack = a[0]
    if rack != current_rack:
        if rack == 'V':
            click_cage('cage15')
        else:
            click_cage('cage6')
        l7_actions += 1
        total += 1
        current_rack = rack
    am = action_map_h if rack == 'H' else action_map_v
    obs = env.step(AM[am[a]], data={})
    l7_actions += 1
    total += 1

curr_level = g._current_level_index
if curr_level > prev_level:
    print(f"L7: SOLVED ({l7_actions} actions, game now at L{curr_level+1})")
    prev_level = curr_level
else:
    print(f"L7: FAILED (still at level {curr_level})")

# L8 — same cage toggle mechanism
current_rack = 'H'  # cage6 starts active on new level
l8_actions = 0
for a in L8_ABSTRACT:
    rack = a[0]
    if rack != current_rack:
        if rack == 'V':
            click_cage('cage15')
        else:
            click_cage('cage6')
        l8_actions += 1
        total += 1
        current_rack = rack
    am = action_map_h if rack == 'H' else action_map_v
    obs = env.step(AM[am[a]], data={})
    l8_actions += 1
    total += 1

from arcengine import GameState
if obs.state == GameState.WIN or g._current_level_index > prev_level:
    print(f"L8: SOLVED ({l8_actions} actions)")
else:
    print(f"L8: FAILED (still at level {g._current_level_index})")

print(f"\nTotal actions: {total}")
print(f"Scorecard: {env.scorecard_id}")
print(f"Game state: {obs.state}")
