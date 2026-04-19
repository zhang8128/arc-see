#!/usr/bin/env python3
"""SK48 L6 Explorer — use game engine directly to test ACTION7 and search."""

import sys
import copy
sys.path.insert(0, 'environment_files/sk48/41055498')

from sk48 import Sk48
from arcengine import GameAction
from arcengine.enums import ActionInput

AM = {
    'U': GameAction.ACTION1,
    'D': GameAction.ACTION2,
    'L': GameAction.ACTION3,
    'R': GameAction.ACTION4,
    '7': GameAction.ACTION7,
}

def make_game(level=0):
    """Create game at specific level."""
    g = Sk48()
    g._current_level_index = level
    g.on_set_level(g._levels[level])
    return g

def act(g, action, data=None):
    """Execute action and wait for completion."""
    ai = ActionInput(id=action, data=data or {})
    g.perform_action(ai)
    for _ in range(500):
        if g.is_action_complete:
            break
        g.step()

def switch_rack(g):
    """Switch to the other rack via ACTION6 click."""
    for rack in g.xpmcmtbcv.keys():
        if rack != g.vzvypfsnt:
            act(g, GameAction.ACTION6, {'x': rack.x + 2, 'y': rack.y + 2})
            return rack
    return None

def get_state(g):
    """Get human-readable state."""
    active = g.vzvypfsnt
    active_info = f"({active.x},{active.y},rot={active.rotation})" if active else "None"
    segs = {}
    for r, sl in g.mwfajkguqx.items():
        segs[f"({r.x},{r.y},r={r.rotation})"] = len(sl)
    targets = {(t.x, t.y): int(t.pixels[1, 1]) for t in g.vbelzuaian}
    return active_info, segs, targets

def is_won(g):
    g.gvtmoopqgy()
    return g.lgdrixfno >= 0

def play_seq(g, seq, log=True):
    """Play a string of UDLR7S actions. S=switch."""
    actions_used = 0
    for c in seq:
        if c == 'S':
            switch_rack(g)
            actions_used += 1
        else:
            act(g, AM[c])
            actions_used += 1
    return actions_used

def check_vjfbwggsd(g):
    """Check the match scores for each rack pair."""
    g.gvtmoopqgy()
    results = {}
    for rack, ref in g.xpmcmtbcv.items():
        rack_vals = [int(t.pixels[1,1]) for t in g.vjfbwggsd.get(rack, [])]
        ref_vals = [int(t.pixels[1,1]) for t in g.vjfbwggsd.get(ref, [])]
        rname = 'H' if rack.rotation == 0 else 'V'
        results[rname] = {'rack': rack_vals, 'ref': ref_vals}
    return results

print("SK48 L6 Explorer - Direct Engine")
print("=" * 60)

# Create game at L6 directly
g = make_game(level=5)
active, segs, targets = get_state(g)
print(f"Active rack: {active}")
print(f"Segments: {segs}")
print(f"Targets: {targets}")
print(f"Remaining actions: {g.qiercdohl}")
print(f"Rack pairs (xpmcmtbcv):")
for rack, ref in g.xpmcmtbcv.items():
    print(f"  rack({rack.x},{rack.y},r={rack.rotation}) → ref({ref.x},{ref.y},r={ref.rotation})")
print()

# ===== TEST ACTION7 =====
print("=== ACTION7 Test ===")

# From fresh state, do R, R then ACTION7
g = make_game(level=5)
print(f"Initial state:")
print(f"  Active: {get_state(g)[0]}")
print(f"  Segs: {get_state(g)[1]}")
print(f"  Targets: {get_state(g)[2]}")

act(g, GameAction.ACTION4)  # R (extend)
print(f"\nAfter R:")
print(f"  Active: {get_state(g)[0]}")
print(f"  Segs: {get_state(g)[1]}")
print(f"  Targets: {get_state(g)[2]}")

act(g, GameAction.ACTION4)  # R (extend again)
print(f"\nAfter R,R:")
print(f"  Active: {get_state(g)[0]}")
print(f"  Segs: {get_state(g)[1]}")
print(f"  Targets: {get_state(g)[2]}")

# Now try ACTION7
act(g, GameAction.ACTION7)
print(f"\nAfter R,R,ACTION7:")
print(f"  Active: {get_state(g)[0]}")
print(f"  Segs: {get_state(g)[1]}")
print(f"  Targets: {get_state(g)[2]}")
print(f"  Remaining: {g.qiercdohl}")

# Try ACTION7 again
act(g, GameAction.ACTION7)
print(f"\nAfter R,R,ACTION7,ACTION7:")
print(f"  Active: {get_state(g)[0]}")
print(f"  Segs: {get_state(g)[1]}")
print(f"  Targets: {get_state(g)[2]}")

# Move down and test
act(g, GameAction.ACTION2)  # D
print(f"\nAfter D:")
print(f"  Active: {get_state(g)[0]}")
print(f"  Segs: {get_state(g)[1]}")
print(f"  Targets: {get_state(g)[2]}")

# ACTION7 after perpendicular move
act(g, GameAction.ACTION7)
print(f"\nAfter D,ACTION7:")
print(f"  Active: {get_state(g)[0]}")
print(f"  Segs: {get_state(g)[1]}")
print(f"  Targets: {get_state(g)[2]}")

# ===== TEST ACTION7 FROM FRESH =====
print("\n=== ACTION7 from fresh state ===")
g = make_game(level=5)
act(g, GameAction.ACTION7)
a1, s1, t1 = get_state(g)
print(f"After single ACTION7:")
print(f"  Active: {a1}")
print(f"  Segs: {s1}")
print(f"  Targets: {t1}")

# ===== CHECK WIN CONDITIONS =====
print("\n=== Win condition check ===")
g = make_game(level=5)
vj = check_vjfbwggsd(g)
for rname, info in vj.items():
    print(f"  {rname}-rack: vals={info['rack']}, ref={info['ref']}")

print("\n=== Check if ACTION7 is just switch ===")
g = make_game(level=5)
initial_active = g.vzvypfsnt
print(f"Initial active: ({initial_active.x},{initial_active.y},rot={initial_active.rotation})")
act(g, GameAction.ACTION7)
after_active = g.vzvypfsnt
print(f"After ACTION7: ({after_active.x},{after_active.y},rot={after_active.rotation})")
if initial_active != after_active:
    print("ACTION7 switches the active rack!")
else:
    print("ACTION7 does NOT switch rack")
