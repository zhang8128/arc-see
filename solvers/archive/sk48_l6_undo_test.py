#!/usr/bin/env python3
"""SK48 L6 — Test if undo reverses target pushes."""

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

def get_targets(g):
    return {(t.x, t.y): int(t.pixels[1, 1]) for t in g.vbelzuaian}

def get_segs(g):
    return {f"({r.x},{r.y},r={r.rotation})": len(sl) for r, sl in g.mwfajkguqx.items()}

def get_active(g):
    r = g.vzvypfsnt
    return f"({r.x},{r.y},r={r.rotation})"

# ============================================
# TEST 1: Push 8-target at y=32, then undo
# ============================================
print("TEST 1: Push target then undo")
print("=" * 60)

g = make_game()

# Move H-rack down to y=32
act(g, GameAction.ACTION2)  # D: y=26 → y=32
print(f"After D: active={get_active(g)}, segs={get_segs(g)}")
print(f"  Targets: {get_targets(g)}")

# Now extend R three times to reach x=29 and push 8-target
act(g, GameAction.ACTION4)  # R: 2→3 segs
print(f"After R(1): segs={get_segs(g)}")
act(g, GameAction.ACTION4)  # R: 3→4 segs
print(f"After R(2): segs={get_segs(g)}")
act(g, GameAction.ACTION4)  # R: 4→5 segs, should push (29,32) to (35,32)
print(f"After R(3): segs={get_segs(g)}")

play_targets = {k:v for k,v in get_targets(g).items() if k[1] < 50}
print(f"  Play targets: {play_targets}")
print(f"  Expected: 8-target at (35,32) instead of (29,32)")

# Now UNDO
print(f"\n--- ACTION7 (undo) ---")
act(g, GameAction.ACTION7)
print(f"After undo: segs={get_segs(g)}")
play_targets = {k:v for k,v in get_targets(g).items() if k[1] < 50}
print(f"  Play targets: {play_targets}")
print(f"  If 8 at (29,32): undo reversed the push")
print(f"  If 8 at (35,32): undo did NOT reverse the push! (TRICK!)")

# ============================================
# TEST 2: Multiple pushes then multiple undos
# ============================================
print("\n\nTEST 2: Extend to push, undo all, check targets")
print("=" * 60)

g = make_game()

# Move down to y=32
act(g, GameAction.ACTION2)

# Extend 5 times (push target far right, maybe chain)
for i in range(5):
    act(g, GameAction.ACTION4)
    pt = {k:v for k,v in get_targets(g).items() if k[1] < 50}
    s = get_segs(g)
    print(f"After R({i+1}): segs={s}")
    print(f"  Play targets: {pt}")

# Undo 5 times
print("\n--- Undoing 5 times ---")
for i in range(5):
    act(g, GameAction.ACTION7)
    pt = {k:v for k,v in get_targets(g).items() if k[1] < 50}
    s = get_segs(g)
    print(f"After undo({i+1}): segs={s}")
    print(f"  Play targets: {pt}")

# ============================================
# TEST 3: Push perpendicular (V-rack pushing horizontally), then undo
# ============================================
print("\n\nTEST 3: V-rack perpendicular push + undo")
print("=" * 60)

g = make_game()

# Switch to V-rack
for rack in g.xpmcmtbcv.keys():
    if rack != g.vzvypfsnt:
        act(g, GameAction.ACTION6, {'x': rack.x + 2, 'y': rack.y + 2})
        break

print(f"Active: {get_active(g)}")

# V-rack at x=29. Extend down to push towards y=26 obstacle
# V-rack has 2 segs at y=2,8. Extending adds y=14,20,26...
# But (29,26) is obstacle! Extension to 5th seg should fail.
for i in range(6):
    act(g, GameAction.ACTION2)  # D = extend down for V-rack
    pt = {k:v for k,v in get_targets(g).items() if k[1] < 50}
    s = get_segs(g)
    print(f"After D({i+1}): segs={s}, targets={pt}")

# ============================================
# TEST 4: Can V-rack move RIGHT past obstacle if few segs?
# ============================================
print("\n\nTEST 4: V-rack move to x=35")
print("=" * 60)

g = make_game()

# Switch to V-rack
for rack in g.xpmcmtbcv.keys():
    if rack != g.vzvypfsnt:
        act(g, GameAction.ACTION6, {'x': rack.x + 2, 'y': rack.y + 2})
        break

print(f"Active: {get_active(g)}")
print(f"V-rack segs: 2 (at y=2,8)")

# Move V-rack RIGHT
act(g, GameAction.ACTION4)  # R: x=29 → x=35
print(f"After R: active={get_active(g)}, segs={get_segs(g)}")

# Extend down
for i in range(6):
    act(g, GameAction.ACTION2)  # D = extend
    pt = {k:v for k,v in get_targets(g).items() if k[1] < 50}
    s = get_segs(g)
    print(f"After D({i+1}): segs={s}")
    changed = {k:v for k,v in pt.items() if k[0] == 35}
    print(f"  x=35 targets: {changed}")

# Check vjfbwggsd
g.gvtmoopqgy()
vj = {}
for rack, ref in g.xpmcmtbcv.items():
    rack_vals = [int(t.pixels[1,1]) for t in g.vjfbwggsd.get(rack, [])]
    ref_vals = [int(t.pixels[1,1]) for t in g.vjfbwggsd.get(ref, [])]
    rname = 'H' if rack.rotation == 0 else 'V'
    vj[rname] = {'rack': rack_vals, 'ref': ref_vals}
print(f"\nvjfbwggsd check: {vj}")
