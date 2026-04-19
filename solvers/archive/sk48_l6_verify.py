#!/usr/bin/env python3
"""SK48 L6 — Verify the A* solution using the game engine."""

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
        if g.is_action_complete:
            break
        g.step()

def switch_rack(g):
    for rack in g.xpmcmtbcv.keys():
        if rack != g.vzvypfsnt:
            act(g, GameAction.ACTION6, {'x': rack.x + 2, 'y': rack.y + 2})
            return

def get_active_type(g):
    return 'H' if g.vzvypfsnt.rotation == 0 else 'V'

def get_targets(g):
    return {(t.x, t.y): int(t.pixels[1, 1]) for t in g.vbelzuaian}

def get_segs(g):
    return {f"({r.x},{r.y},r={r.rotation})": len(sl) for r, sl in g.mwfajkguqx.items()}

# Abstract solution from A* solver
abstract_sol = "HD HR HR HR VD VD VR VD VU VR VD VU VR VD HR HR HR HL HL HL HL HD HD HR HU HL HU HR VL VL VD VD VD".split()

# Convert to game actions with switches
# H actions: HR=ACTION4, HL=ACTION3, HU=ACTION1, HD=ACTION2
# V actions: VD=ACTION2, VU=ACTION1, VL=ACTION3, VR=ACTION4
ACTION_MAP = {
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
print(f"Initial: active={get_active_type(g)}, segs={get_segs(g)}")
print(f"Targets: {get_targets(g)}")
print(f"Remaining: {g.qiercdohl}")

game_actions = []
current_type = get_active_type(g)

for i, abstract_act in enumerate(abstract_sol):
    needed_type, game_act = ACTION_MAP[abstract_act]

    if needed_type != current_type:
        switch_rack(g)
        game_actions.append('SWITCH')
        current_type = get_active_type(g)
        assert current_type == needed_type, f"Switch failed! Got {current_type}, need {needed_type}"

    act(g, game_act)
    game_actions.append(abstract_act)

    # Check win
    g.gvtmoopqgy()
    if g.lgdrixfno >= 0:
        print(f"\n*** WIN after step {i+1}! ***")
        print(f"Total game actions: {len(game_actions)} ({len([a for a in game_actions if a == 'SWITCH'])} switches)")
        print(f"Remaining actions: {g.qiercdohl}")
        break

    # Periodic state dump
    play_targets = {k:v for k,v in get_targets(g).items() if k[1] < 50}
    if (i+1) % 5 == 0:
        print(f"Step {i+1}: {abstract_act}, active={current_type}")
        print(f"  Segs: {get_segs(g)}")
        print(f"  Play targets: {play_targets}")

else:
    print(f"\nDid NOT win after all {len(abstract_sol)} steps")
    play_targets = {k:v for k,v in get_targets(g).items() if k[1] < 50}
    print(f"Final segs: {get_segs(g)}")
    print(f"Final targets: {play_targets}")
    print(f"Remaining: {g.qiercdohl}")

    # Check vjfbwggsd
    vj = {}
    for rack, ref in g.xpmcmtbcv.items():
        rack_vals = [int(t.pixels[1,1]) for t in g.vjfbwggsd.get(rack, [])]
        ref_vals = [int(t.pixels[1,1]) for t in g.vjfbwggsd.get(ref, [])]
        rname = 'H' if rack.rotation == 0 else 'V'
        vj[rname] = {'rack': rack_vals, 'ref': ref_vals}
    print(f"vjfbwggsd: {vj}")

print(f"\nFull game action sequence:")
print(' '.join(game_actions))

# Count switches
switches = sum(1 for a in game_actions if a == 'SWITCH')
non_switch = sum(1 for a in game_actions if a != 'SWITCH')
print(f"\nAbstract actions: {non_switch}, Switches: {switches}, Total: {len(game_actions)}")
print(f"Baseline: 42")
