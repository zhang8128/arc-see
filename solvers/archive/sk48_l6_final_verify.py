#!/usr/bin/env python3
"""SK48 L6 — Final verification of the cross-rack-aware solution."""

import sys
sys.path.insert(0, 'environment_files/sk48/41055498')

from sk48 import Sk48
from arcengine import GameAction
from arcengine.enums import ActionInput

def make_game(level=5):
    g = Sk48()
    g._current_level_index = level
    g.on_set_level(g._levels[level])
    return g

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

def get_active_type(g):
    return 'H' if g.vzvypfsnt.rotation == 0 else 'V'

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

abstract_sol = "HD HR HR HR VD VD VR VD VU VR VD VU VR VD HR HR HR HL HL HL HL HD HD HR HU HL HU HR VL VL VD VD VD".split()

g = make_game()
current = get_active_type(g)
total_actions = 0
prev_level = g._current_level_index

for i, a in enumerate(abstract_sol):
    needed, ga = AM[a]
    if needed != current:
        switch_rack(g)
        current = get_active_type(g)
        total_actions += 1

    act(g, ga)
    total_actions += 1

    # Check if level changed (= won)
    if g._current_level_index != prev_level:
        print(f"*** L6 WON at step {i+1} ({a})! Total game actions: {total_actions} ***")
        print(f"  Baseline: 42 actions")
        print(f"  We used: {total_actions} ({total_actions - 42} vs baseline)")

        # Check win check
        g2 = Sk48()
        g2._current_level_index = 5
        g2.on_set_level(g2._levels[5])
        # Replay but stop before the winning action
        curr2 = 'H' if g2.vzvypfsnt.rotation == 0 else 'V'
        for j in range(i+1):
            n2, ga2 = AM[abstract_sol[j]]
            if n2 != curr2:
                for rack in g2.xpmcmtbcv.keys():
                    if rack != g2.vzvypfsnt:
                        act(g2, GameAction.ACTION6, {'x': rack.x + 2, 'y': rack.y + 2})
                        break
                curr2 = 'H' if g2.vzvypfsnt.rotation == 0 else 'V'
            act(g2, ga2)

        g2.gvtmoopqgy()
        vj = {}
        for rack, ref in g2.xpmcmtbcv.items():
            rack_vals = [int(t.pixels[1,1]) for t in g2.vjfbwggsd.get(rack, [])]
            ref_vals = [int(t.pixels[1,1]) for t in g2.vjfbwggsd.get(ref, [])]
            rname = 'H' if rack.rotation == 0 else 'V'
            vj[rname] = {'rack': rack_vals, 'ref': ref_vals}
        print(f"  vjfbwggsd: {vj}")
        break
else:
    print("Did NOT win!")
    print(f"Total game actions used: {total_actions}")
