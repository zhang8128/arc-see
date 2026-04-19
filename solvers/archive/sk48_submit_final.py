#!/usr/bin/env python3
"""SK48 — Submit L1-L6 solution via arc_agi API.

The env.step() handles game advancement automatically.
Check state == WIN to detect level completion.
"""

import arc_agi
from arcengine import GameAction, GameState

GA = {
    'U': GameAction.ACTION1,
    'D': GameAction.ACTION2,
    'L': GameAction.ACTION3,
    'R': GameAction.ACTION4,
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

AM = {
    'ACTION1': GameAction.ACTION1, 'ACTION2': GameAction.ACTION2,
    'ACTION3': GameAction.ACTION3, 'ACTION4': GameAction.ACTION4,
}

arcade = arc_agi.Arcade()
env = arcade.make("sk48-41055498", render_mode=None)

# Solve L1-L5
for lvl in range(1, 6):
    obs = env.reset()
    won = False
    for i, c in enumerate(SOLUTIONS[lvl]):
        obs = env.step(GA[c])
        if obs.state == GameState.WIN:
            print(f"L{lvl}: SOLVED at step {i+1}/{len(SOLUTIONS[lvl])}")
            won = True
            break
    if not won:
        print(f"L{lvl}: FAILED ({obs.state.name})")
        exit(1)

# Solve L6
obs = env.reset()
l6_count = 0
won = False
for item in L6_SEQ:
    if item[0] == 'C':
        obs = env.step(GameAction.ACTION6, data={'x': item[1], 'y': item[2]})
    else:
        obs = env.step(AM[item[1]])
    l6_count += 1
    if obs.state == GameState.WIN:
        print(f"L6: SOLVED at step {l6_count}/36")
        won = True
        break

if not won:
    print(f"L6: FAILED ({obs.state.name}) after {l6_count} actions")

print(f"\nScorecard: {env.scorecard_id}")
