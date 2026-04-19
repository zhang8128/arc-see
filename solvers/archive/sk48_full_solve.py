#!/usr/bin/env python3
"""SK48 — Full game solve: L1-L6 using discovered solutions."""

import sys
sys.path.insert(0, 'environment_files/sk48/41055498')

from sk48 import Sk48
from arcengine import GameAction
from arcengine.enums import ActionInput

def make_game():
    return Sk48()

def act(g, action, data=None):
    ai = ActionInput(id=action, data=data or {})
    g.perform_action(ai)
    for _ in range(500):
        if g.is_action_complete: break
        g.step()

def switch_rack(g):
    for rack in g.xpmcmtbcv.keys():
        if rack != g.vzvypfsnt:
            act(g, GameAction.ACTION6, {'x': rack.x + 2, 'y': rack.y + 2})
            return

# Action mapping
GA = {
    'U': GameAction.ACTION1,
    'D': GameAction.ACTION2,
    'L': GameAction.ACTION3,
    'R': GameAction.ACTION4,
}

# Known solutions for L1-L5 (single-rack, no switches needed)
SOLUTIONS = {
    1: "UUURRRRLDDRLUR",          # 14 actions
    2: "RRRRUUULLURRDDRURLLURRLLURR",  # 27 actions (confirmed by BFS)
    3: "RRUUUURDDLDRRRRLLLLUUUURDDDLUUUUR",  # 33 actions
    4: "RRUUUULLLLDRURDRURRDLLU",   # 23 actions
    5: "LULLRRRRRURRDLLLLDDLDRRRRLURDRLUR",  # 33 actions
}

# L6 abstract solution (needs switch handling)
L6_ABSTRACT = "HD HR HR HR VD VD VR VD VU VR VD VU VR VD HR HR HR HL HL HL HL HD HD HR HU HL HU HR VL VL VD VD VD"

AM = {
    'HR': ('H', GameAction.ACTION4),
    'HL': ('H', GameAction.ACTION3),
    'HU': ('H', GameAction.ACTION1),
    'HD': ('H', GameAction.ACTION2),
    'VD': ('V', GameAction.ACTION2),
    'VU': ('V', GameAction.ACTION1),
    'VL': ('V', GameAction.ACTION3),
    'VR': ('V', GameAction.ACTION4),
}

g = make_game()
total_used = 0

# Solve L1-L5
for lvl in range(1, 6):
    prev = g._current_level_index
    seq = SOLUTIONS[lvl]
    for c in seq:
        act(g, GA[c])
    total_used += len(seq)

    if g._current_level_index != prev:
        print(f"L{lvl}: SOLVED ({len(seq)} actions)")
    else:
        print(f"L{lvl}: FAILED!")
        sys.exit(1)

# Solve L6
print(f"\nL6: Executing solution...")
current = 'H' if g.vzvypfsnt.rotation == 0 else 'V'
l6_actions = 0
prev = g._current_level_index

for a in L6_ABSTRACT.split():
    needed, ga = AM[a]
    if needed != current:
        switch_rack(g)
        current = 'H' if g.vzvypfsnt.rotation == 0 else 'V'
        l6_actions += 1
    act(g, ga)
    l6_actions += 1

    if g._current_level_index != prev:
        print(f"L6: SOLVED ({l6_actions} actions)")
        break
else:
    print(f"L6: FAILED!")
    sys.exit(1)

total_used += l6_actions

print(f"\nTotal: L1-L6 solved using {total_used} actions")
print(f"L6 used {l6_actions} actions (baseline: 42)")

# Generate MCP action sequence for L6
print(f"\n=== MCP Action Sequence for L6 ===")
# Replay to get switch coordinates
g2 = Sk48()
g2._current_level_index = 5
g2.on_set_level(g2._levels[5])
curr2 = 'H' if g2.vzvypfsnt.rotation == 0 else 'V'
mcp_seq = []

for a in L6_ABSTRACT.split():
    needed, ga = AM[a]
    if needed != curr2:
        # Find the other rack's position for click
        for rack in g2.xpmcmtbcv.keys():
            if rack != g2.vzvypfsnt:
                click_x = rack.x + 2
                click_y = rack.y + 2
                act(g2, GameAction.ACTION6, {'x': click_x, 'y': click_y})
                mcp_seq.append(f"ACTION6(x={click_x},y={click_y})")
                break
        curr2 = 'H' if g2.vzvypfsnt.rotation == 0 else 'V'

    act(g2, ga)
    action_name = {GameAction.ACTION1: 'ACTION1', GameAction.ACTION2: 'ACTION2',
                   GameAction.ACTION3: 'ACTION3', GameAction.ACTION4: 'ACTION4'}[ga]
    mcp_seq.append(action_name)

print('\n'.join(mcp_seq))
