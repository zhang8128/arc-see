#!/usr/bin/env python3
"""SK48 L6 — Reproduce exact step 30 state and test VU."""

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

def get_targets(g):
    return {(t.x, t.y): int(t.pixels[1,1]) for t in g.vbelzuaian if t.y < 50}

def get_segs(g):
    return {(r.x, r.y, r.rotation): len(sl) for r, sl in g.mwfajkguqx.items()}

# Replay first 30 steps of the A* solution
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

sol = "HD HR HR VD VD VR VD HR HL HD HR HL HD HR HR HU HU VU VR VD VU VR VD HR HR HL VD VL VD VD".split()

g = make_game()
current_type = get_active_type(g)

for i, a in enumerate(sol):
    needed, ga = AM[a]
    if needed != current_type:
        switch_rack(g)
        current_type = get_active_type(g)
    act(g, ga)

print(f"After 30 steps:")
print(f"Active: {get_active_type(g)}")
print(f"Segs: {get_segs(g)}")
print(f"Targets: {get_targets(g)}")

# Now examine what each target sprite looks like
print(f"\nSprite details at x=41:")
for t in sorted(g.vbelzuaian, key=lambda s: (s.x, s.y)):
    if t.x == 41 and t.y < 50:
        print(f"  ({t.x},{t.y}): color={int(t.pixels[1,1])}, size=({t.pixels.shape}), tags={getattr(t, 'tags', [])}")

# Check the opqqwmrfcn set and related
print(f"\nV-rack segments at x=41:")
for r, sl in g.mwfajkguqx.items():
    if r.x == 41:
        for j, seg in enumerate(sl):
            print(f"  seg[{j}]: ({seg.x},{seg.y})")

# Now do VU and trace what happens
print(f"\n=== Executing VU ===")

# Let's check targets DURING the action
before_targets = get_targets(g)
print(f"Before VU: {before_targets}")

# Check if there's something at (41,26) that might block
# Check H-rack segments that might be at y=32 conflicting with V-rack push
print(f"\nH-rack state:")
for r, sl in g.mwfajkguqx.items():
    if r.rotation == 0 and r.y < 50:
        print(f"  H-rack at ({r.x},{r.y}): {len(sl)} segs")
        for j, seg in enumerate(sl):
            print(f"    seg[{j}]: ({seg.x},{seg.y})")
            if seg.x == 41:
                print(f"    *** H-seg at x=41! Possible interference ***")

act(g, GameAction.ACTION1)  # VU
print(f"\nAfter VU:")
print(f"Targets: {get_targets(g)}")

# Compare
after_targets = get_targets(g)
print(f"\nChanges:")
for k in set(list(before_targets.keys()) + list(after_targets.keys())):
    b = before_targets.get(k, '-')
    a = after_targets.get(k, '-')
    if b != a:
        print(f"  {k}: {b} -> {a}")
