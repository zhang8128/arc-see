#!/usr/bin/env python3
"""SK48 — Submit L1-L6 solution. Don't check WIN state, just play through."""

import arc_agi
from arcengine import GameAction, GameState

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

total = 0

# L1-L5
for lvl in range(1, 6):
    obs = env.reset()
    for c in SOLUTIONS[lvl]:
        obs = env.step(GA[c], data={})
    total += len(SOLUTIONS[lvl])
    # Check if game advanced by looking at internal game state
    g = env._game
    print(f"L{lvl}: played {len(SOLUTIONS[lvl])} actions, game now at level {g._current_level_index}")

# L6
obs = env.reset()
for item in L6_SEQ:
    if item[0] == 'C':
        obs = env.step(GameAction.ACTION6, data={'x': item[1], 'y': item[2]})
    else:
        obs = env.step(AM[item[1]], data={})
total += len(L6_SEQ)

g = env._game
print(f"L6: played {len(L6_SEQ)} actions, game now at level {g._current_level_index}")
print(f"\nTotal actions: {total}")
print(f"Scorecard: {env.scorecard_id}")
print(f"Final game level: {g._current_level_index}")

# Check score
info = env.info()
print(f"Info: {info}")
