#!/usr/bin/env python3
"""AR25 — Full solution: all 8 levels (262 actions, baselines 577).

Mechanics: Two movable dividers + pieces. A5 cycles through objects.
L1-L2: mirrored movement mode. L3+: independent cycling, dividers create
4-fold reflections (original + H-reflect + V-reflect + 180° rotation).
Win: piece cells + reflections cover all target positions.

Strategy: position dividers at target center, brute-force piece placements
via abstract 4-copy model, verify with game engine.
"""

import arc_agi
from arcengine import GameAction, GameState

GA = {'U': GameAction.ACTION1, 'D': GameAction.ACTION2,
      'L': GameAction.ACTION3, 'R': GameAction.ACTION4,
      '5': GameAction.ACTION5}

SOLUTIONS = {
    1: "DDDDDDDDDDLLLLL",                                          # 15 (baseline 17)
    2: "LL5DDDDDDDD",                                               # 11 (baseline 22)
    3: "5LLLLLLLLLLLLDDDDD5RRRRRRRDDDDDDD5UUUUUUU",                # 41 (baseline 103)
    4: "5RRRRRRR5RRRRRRRUUUUUUU5DDDDDD",                           # 30 (baseline 29)
    5: "DDDD5RRRRR5LLLLLLLLLLUUUUUUU",                              # 28 (baseline 29)
    6: "DDDDDDDDDDD5L5LLLLLLLDDDDDDDDDDDD5LLLLLLLLLLLLLLLDDDD",   # 53 (baseline 159)
    7: "DD5RRRRRRRRR5RRRUUUUUU5LLUUUUUUUUUUUU",                    # 37 (baseline 152)
    8: "DDDDDD5RRRRRRRRR5RRRRRRRRRUUUU5LLLLLLLLLUUUUUUU",          # 47 (baseline 66)
}

BASELINES = [17, 22, 103, 29, 29, 159, 152, 66]

arcade = arc_agi.Arcade()
env = arcade.make("ar25-e3c63847", render_mode=None)
game = env._game
obs = env.reset()

total = 0
for lvl in range(1, 9):
    level_idx = game._current_level_index
    sol = SOLUTIONS[lvl]
    for c in sol:
        obs = env.step(GA[c], data={})

    if game._current_level_index > level_idx or obs.state == GameState.WIN:
        total += len(sol)
        print(f"  ✓ L{lvl}: {len(sol)} actions (baseline {BASELINES[lvl-1]})")
    else:
        print(f"  ✗ L{lvl} FAILED")
        break

    if obs.state == GameState.WIN:
        break

print(f"\nTotal: {total} actions (baselines: {sum(BASELINES)})")
