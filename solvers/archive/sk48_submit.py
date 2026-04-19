#!/usr/bin/env python3
"""SK48 — Submit solution for L1-L6 via arc_agi API."""

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

# L6 MCP sequence
L6_SEQ = [
    ('A', 'ACTION2'), ('A', 'ACTION4'), ('A', 'ACTION4'), ('A', 'ACTION4'),
    ('C', 31, 4),  # switch to V
    ('A', 'ACTION2'), ('A', 'ACTION2'), ('A', 'ACTION4'), ('A', 'ACTION2'),
    ('A', 'ACTION1'), ('A', 'ACTION4'), ('A', 'ACTION2'), ('A', 'ACTION1'),
    ('A', 'ACTION4'), ('A', 'ACTION2'),
    ('C', 7, 34),  # switch to H
    ('A', 'ACTION4'), ('A', 'ACTION4'), ('A', 'ACTION4'), ('A', 'ACTION3'),
    ('A', 'ACTION3'), ('A', 'ACTION3'), ('A', 'ACTION3'), ('A', 'ACTION2'),
    ('A', 'ACTION2'), ('A', 'ACTION4'), ('A', 'ACTION1'), ('A', 'ACTION3'),
    ('A', 'ACTION1'), ('A', 'ACTION4'),
    ('C', 49, 4),  # switch to V
    ('A', 'ACTION3'), ('A', 'ACTION3'), ('A', 'ACTION2'), ('A', 'ACTION2'),
    ('A', 'ACTION2'),
]

ACTION_MAP = {
    'ACTION1': GameAction.ACTION1,
    'ACTION2': GameAction.ACTION2,
    'ACTION3': GameAction.ACTION3,
    'ACTION4': GameAction.ACTION4,
}

arcade = arc_agi.Arcade()
env = arcade.make("sk48-41055498", render_mode=None)

# Solve L1-L5
for lvl in range(1, 6):
    obs = env.reset()
    for c in SOLUTIONS[lvl]:
        obs = env.step(GA[c])
    if obs.state == GameState.WIN:
        print(f"L{lvl}: SOLVED ({len(SOLUTIONS[lvl])} actions)")
    else:
        print(f"L{lvl}: FAILED ({obs.state.name})")
        exit(1)

# Solve L6
obs = env.reset()
l6_count = 0
for item in L6_SEQ:
    if item[0] == 'C':
        obs = env.step(GameAction.ACTION6, data={'x': item[1], 'y': item[2]})
    else:
        obs = env.step(ACTION_MAP[item[1]])
    l6_count += 1
    if obs.state == GameState.WIN:
        print(f"L6: SOLVED ({l6_count} actions)")
        break
else:
    print(f"L6: NOT YET WON after {l6_count} actions, state={obs.state.name}")

print(f"\nGame state after L6:")
print(f"  State: {obs.state.name}")
print(f"  Score info: {env.score if hasattr(env, 'score') else 'N/A'}")
