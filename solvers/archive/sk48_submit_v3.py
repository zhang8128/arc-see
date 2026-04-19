#!/usr/bin/env python3
"""SK48 — Submit L1-L6. No reset between levels — game auto-advances."""

import arc_agi
from arcengine import GameAction

GA = {
    'U': GameAction.ACTION1, 'D': GameAction.ACTION2,
    'L': GameAction.ACTION3, 'R': GameAction.ACTION4,
}
AM = {
    'ACTION1': GameAction.ACTION1, 'ACTION2': GameAction.ACTION2,
    'ACTION3': GameAction.ACTION3, 'ACTION4': GameAction.ACTION4,
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

arcade = arc_agi.Arcade()
env = arcade.make("sk48-41055498", render_mode=None)
g = env._game

# Initial reset to start
obs = env.reset()
total = 0
prev_level = g._current_level_index

# L1-L5: play each solution. Game auto-advances on win. No reset().
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

print(f"\nTotal actions: {total}")
print(f"Scorecard: {env.scorecard_id}")
print(f"Game level: {g._current_level_index}")
print(f"Levels completed: {prev_level}")
