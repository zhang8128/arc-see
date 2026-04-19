#!/usr/bin/env python3
"""SK48 L7 — Final test: run solution, switch to cage6, check win."""

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

def click_cage(env, cage_name):
    level = env._game._levels[env._game._current_level_index]
    for s in level._sprites:
        if hasattr(s, 'tags') and 'sys_click' in s.tags and s.y < 54:
            colors = {int(px) for row in s.pixels for px in row if px != -1}
            if cage_name == 'cage15' and 15 in colors:
                return env.step(GameAction.ACTION6, data={'x': s.x+2, 'y': s.y+2})
            elif cage_name == 'cage6' and 6 in colors:
                return env.step(GameAction.ACTION6, data={'x': s.x+2, 'y': s.y+2})
    return None

abstract_path = "HR HR HU VL VD VR HD HD VD HR HR VR VD VL HR HR HL HL HL HL HL HU HR HR VD VU HL VU".split()
action_map_h = {'HR': 'ACTION4', 'HL': 'ACTION3', 'HU': 'ACTION1', 'HD': 'ACTION2'}
action_map_v = {'VD': 'ACTION2', 'VU': 'ACTION1', 'VL': 'ACTION3', 'VR': 'ACTION4'}

env, obs = create_env()
g = env._game

current = 'H'
total = 0
for a in abstract_path:
    rack = a[0]
    if rack != current:
        if rack == 'V':
            obs = click_cage(env, 'cage15')
        else:
            obs = click_cage(env, 'cage6')
        total += 1
        current = rack
    am = action_map_h if rack == 'H' else action_map_v
    obs = env.step(AM[am[a]], data={})
    total += 1

print(f"After solution: {total} actions, state={obs.state}, level={g._current_level_index}")

# Now try clicking cage6 (currently cage15 is active after VU)
obs = click_cage(env, 'cage6')
total += 1
print(f"After click cage6: {total} actions, state={obs.state}, level={g._current_level_index}")

if obs.state == GameState.WIN or g._current_level_index > 6:
    print("\n*** WIN! ***")
else:
    # Try various additional actions
    for name, action, data in [
        ("ACTION7 (undo)", GameAction.ACTION7, {}),
        ("HR", GameAction.ACTION4, {}),
        ("HL", GameAction.ACTION3, {}),
        ("HU", GameAction.ACTION1, {}),
        ("HD", GameAction.ACTION2, {}),
    ]:
        env2, obs2 = create_env()
        g2 = env2._game
        curr = 'H'
        for a in abstract_path:
            rack = a[0]
            if rack != curr:
                if rack == 'V': click_cage(env2, 'cage15')
                else: click_cage(env2, 'cage6')
                curr = rack
            am = action_map_h if rack == 'H' else action_map_v
            obs2 = env2.step(AM[am[a]], data={})
        # Switch to cage6
        click_cage(env2, 'cage6')
        # Try additional action
        obs2 = env2.step(action, data=data)
        print(f"  +{name}: state={obs2.state}, level={g2._current_level_index}")
        if obs2.state == GameState.WIN or g2._current_level_index > 6:
            print(f"  *** WIN with {name}! ***")
