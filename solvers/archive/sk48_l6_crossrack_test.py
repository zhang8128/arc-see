#!/usr/bin/env python3
"""SK48 L6 — Verify cross-rack segment blocking hypothesis."""

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
    result = {}
    for r, sl in g.mwfajkguqx.items():
        if r.y < 50:
            name = 'H' if r.rotation == 0 else 'V'
            result[name] = {'pos': (r.x, r.y), 'n': len(sl), 'seg_positions': [(s.x, s.y) for s in sl]}
    return result

# ================================================
# TEST A: V-rack shrink with NO H-rack interference
# Push target to x=35, V-rack at x=35, H-rack NOT covering x=35
# ================================================
print("TEST A: V-rack shrink WITHOUT H-rack segment overlap")
print("=" * 60)

g = make_game()

# Push 8@(29,32) to (35,32) using H-rack
act(g, GameAction.ACTION2)  # H down to y=32
for _ in range(3): act(g, GameAction.ACTION4)  # extend to 5 segs
for _ in range(3): act(g, GameAction.ACTION3)  # shrink back to 2

# Now H-rack at y=32, 2 segs (x=5,11). No seg at x=35.
segs = get_segs(g)
print(f"H-rack: {segs.get('H')}")

# Switch to V, move to x=35, extend to 6 segs
switch_rack(g)
act(g, GameAction.ACTION4)  # R: x=29→35

# Extend V to 8 segs
for _ in range(6): act(g, GameAction.ACTION2)

targets_before = get_targets(g)
print(f"Before VU: targets at x=35 = {[(k,v) for k,v in targets_before.items() if k[0]==35]}")

# Shrink V
act(g, GameAction.ACTION1)  # VU
targets_after = get_targets(g)
print(f"After VU:  targets at x=35 = {[(k,v) for k,v in targets_after.items() if k[0]==35]}")

# Check which targets moved
for k in sorted(set(list(targets_before.keys()) + list(targets_after.keys()))):
    if k[0] == 35:
        b = targets_before.get(k, '-')
        a = targets_after.get(k, '-')
        if b != a:
            print(f"  {k}: {b} -> {a}")

# ================================================
# TEST B: V-rack shrink WITH H-rack segment overlap
# Same setup but H-rack has segs covering V-rack targets
# ================================================
print(f"\n\nTEST B: V-rack shrink WITH H-rack segment overlap")
print("=" * 60)

g = make_game()

# Push 8@(29,32) to (35,32) using H-rack
act(g, GameAction.ACTION2)  # H down to y=32
for _ in range(3): act(g, GameAction.ACTION4)  # extend to 5 segs
# DON'T shrink — leave H-rack at 5 segs (x=5,...,29)
# Actually need seg at x=35 to test. Extend one more.
act(g, GameAction.ACTION4)  # 6 segs: x=5,...,35. 8@(35,32) pushed to (41,32)
# Need target at (35,32). Let me restart differently.

# RESTART: Push to (35,32), then extend H-rack to cover x=35
g = make_game()
act(g, GameAction.ACTION2)  # H down to y=32

# Push 8@(29,32) to (35,32): 3 extends
for _ in range(3): act(g, GameAction.ACTION4)  # 5 segs, 8@(35,32)
# Now H-rack has 5 segs at x=5,11,17,23,29. NO seg at x=35.

# Continue extending to get seg at x=35:
act(g, GameAction.ACTION4)  # 6 segs, x=5,...,35. Push 8@(35,32) to (41,32)!

# Hmm, extending adds seg at x=35 and pushes 8@(35,32) to (41,32).
# I need to test with 8 at (35,32) AND H-seg at x=35.
# That's impossible — extending to x=35 would push the target away.

# Alternative: put target at (35,38) where there IS an H-rack seg
# H at y=38 with seg at x=35
act(g, GameAction.ACTION3); act(g, GameAction.ACTION3); act(g, GameAction.ACTION3); act(g, GameAction.ACTION3)  # shrink to 2
act(g, GameAction.ACTION2)  # H to y=38
for _ in range(5): act(g, GameAction.ACTION4)  # 7 segs, push 8@(29,38) far right

segs = get_segs(g)
print(f"H-rack: {segs.get('H')}")
targets = get_targets(g)
print(f"Targets: {targets}")

# This is getting complicated. Let me try a cleaner approach:
# H-rack extends to have seg at (35,32), then V-rack tries to push target at (35,32)

# CLEAN TEST
print(f"\n\nCLEAN TEST: Does H-rack seg at (X,Y) prevent V-rack push of target at (X,Y)?")
print("=" * 60)

g = make_game()

# Phase 1: Push 8@(29,32) to (35,32)
act(g, GameAction.ACTION2)  # H to y=32
for _ in range(3): act(g, GameAction.ACTION4)  # 5 segs, 8@(35,32)
# H has 5 segs at x=5,11,17,23,29. No seg at 35. Good baseline.

targets = get_targets(g)
segs = get_segs(g)
print(f"Phase 1: H-segs cover x=5..29. Target 8@(35,32).")

# Switch to V, go to x=35, extend to cover y=32
switch_rack(g)
act(g, GameAction.ACTION4)  # V to x=35
for _ in range(5): act(g, GameAction.ACTION2)  # V to 7 segs (y=2..38)

# VU should push target at (35,32) UP to (35,26)
targets_before = get_targets(g)
t35 = {k:v for k,v in targets_before.items() if k[0]==35}
print(f"Before VU: x=35 targets = {t35}")

act(g, GameAction.ACTION1)  # VU
targets_after = get_targets(g)
t35_after = {k:v for k,v in targets_after.items() if k[0]==35}
print(f"After VU (no H-seg at 35,32): x=35 targets = {t35_after}")

# Now undo and add H-rack seg at x=35
act(g, GameAction.ACTION7)  # undo VU

# Switch to H, extend to 6 segs (adding x=35)
switch_rack(g)
act(g, GameAction.ACTION4)  # H: 5→6 segs. But wait, 8@(35,32) pushed to (41,32)!

# Need different approach. Let me track carefully.
targets = get_targets(g)
segs = get_segs(g)
print(f"\nAfter extending H to 6 segs:")
print(f"  H: {segs.get('H')}")
t35_2 = {k:v for k,v in targets.items() if k[0]==35}
t41_2 = {k:v for k,v in targets.items() if k[0]==41}
print(f"  x=35 targets: {t35_2}")
print(f"  x=41 targets: {t41_2}")
print("  (H extending to x=35 pushes target away, so we can't have both)")

# ================================================
# DEFINITIVE TEST: Compare V-rack push of target at position
#   where H-rack DOES vs DOES NOT have a segment
# ================================================
print(f"\n\nDEFINITIVE: V-rack push at y=26 (with/without H-rack seg)")
print("=" * 60)

# Test 1: V pushes 9@(35,26) with H-rack at y=26 with 4 segs (x=5..23, no seg at x=35)
g = make_game()
switch_rack(g)
act(g, GameAction.ACTION4)  # V to x=35
for _ in range(3): act(g, GameAction.ACTION2)  # V extend to 5 segs (y through 26)

targets = get_targets(g)
t35 = {k:v for k,v in targets.items() if k[0]==35}
print(f"Test 1: 9@(35,26) pushed by V-rack extension:")
print(f"  x=35 targets after V extend to y=26: {t35}")
print(f"  H-rack segs: {get_segs(g).get('H', {}).get('seg_positions', [])[:5]}")

# Test 2: H-rack at y=26 DOES overlap at x=35? H max 4 segs at y=26 (obstacle at x=29)
# H at y=26 can only have 4 segs (x=5,11,17,23). x=35 is unreachable. So no overlap possible at y=26.

# Let me test y=32 instead
print(f"\nTest 2: H-rack at y=32 with/without seg at x=35")
g = make_game()

# Push 8@(29,32) to (35,32)
act(g, GameAction.ACTION2)  # H to y=32
for _ in range(3): act(g, GameAction.ACTION4)  # 5 segs
for _ in range(3): act(g, GameAction.ACTION3)  # back to 2

# Now 8@(35,32), H at y=32 with 2 segs (x=5,11)
# Switch to V at x=35, extend to 6 segs
switch_rack(g)
act(g, GameAction.ACTION4)  # V to x=35
for _ in range(4): act(g, GameAction.ACTION2)  # V 6 segs (y through 32)

targets = get_targets(g)
segs = get_segs(g)
t35 = {k:v for k,v in targets.items() if k[0]==35}
print(f"  H has 2 segs at y=32 (x=5,11). V at x=35, 6 segs.")
print(f"  x=35 targets: {t35}")

# VU: push targets at x=35 up
act(g, GameAction.ACTION1)
t35_after = {k:v for k,v in targets.items() if k[0]==35}
targets_after = get_targets(g)
t35_after = {k:v for k,v in targets_after.items() if k[0]==35}
print(f"  After VU: x=35 targets = {t35_after} (should have pushed up)")
# No H-seg at x=35,y=32 (only at x=5 and x=11). Target should move.

# Now test WITH H-seg at x=35,y=32
print(f"\nTest 3: Same but with H at y=32 with 6 segs (covering x=35)")
g = make_game()

act(g, GameAction.ACTION2)  # H to y=32
for _ in range(3): act(g, GameAction.ACTION4)  # 5 segs, 8@(35,32)
# DON'T shrink. H has 5 segs at x=5,...,29. seg at x=29 but not x=35.
# Extend one more: H 6 segs, pushes 8@(35,32) to (41,32). H-seg at x=35.
act(g, GameAction.ACTION4)  # 6 segs: x=5,...,35

targets = get_targets(g)
t35 = {k:v for k,v in targets.items() if k[0]==35}
t41 = {k:v for k,v in targets.items() if k[0]==41}
print(f"  After H 6 segs: x=35 targets={t35}, x=41 targets={t41}")
print(f"  8 was pushed to (41,32). H-seg at (35,32). No target at (35,32).")

# Push another target to (35,38) — the other 8@(29,38) can be pushed using H at y=38
# But that requires moving H down, which we can do
act(g, GameAction.ACTION3); act(g, GameAction.ACTION3)  # shrink to 4
act(g, GameAction.ACTION2)  # H to y=38
for _ in range(3): act(g, GameAction.ACTION4)  # 7 segs at y=38, push 8@(29,38) to (35,38)

targets = get_targets(g)
segs = get_segs(g)
h_segs = segs.get('H', {}).get('seg_positions', [])
print(f"\n  H at y=38, 7 segs. H-seg at (35,38)={any(s==(35,38) for s in h_segs)}")
t35 = {k:v for k,v in targets.items() if k[0]==35}
print(f"  x=35 targets: {t35}")

# Switch to V at x=35, extend to cover y=38
switch_rack(g)
# V-rack was at x=29. Move to x=35
act(g, GameAction.ACTION4)
for _ in range(6): act(g, GameAction.ACTION2)  # V 8 segs

targets = get_targets(g)
t35 = {k:v for k,v in targets.items() if k[0]==35}
print(f"  V at x=35, 8 segs. x=35 targets: {t35}")

# VU
act(g, GameAction.ACTION1)
targets_after = get_targets(g)
t35_after = {k:v for k,v in targets_after.items() if k[0]==35}
print(f"  After VU: x=35 targets = {t35_after}")
print(f"  Compare with before: {t35}")
for k in sorted(set(list(t35.keys()) + list(t35_after.keys()))):
    b = t35.get(k, '-')
    a = t35_after.get(k, '-')
    if b != a:
        print(f"    {k}: {b} -> {a}")
