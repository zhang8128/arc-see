#!/usr/bin/env python3
"""SK48 L6 — Definitive cross-rack blocking test."""

import sys, copy
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

def get_h_segs(g):
    for r, sl in g.mwfajkguqx.items():
        if r.rotation == 0 and r.y < 50:
            return [(s.x, s.y) for s in sl]
    return []

# Strategy: Create the SAME target positions via different paths,
# one with H-seg at target position, one without.

# Path A: Push 8@(29,32) to (35,32). H-rack STAYS at 5 segs (x=5..29).
# Then switch to V-rack, extend, VU. No H-seg at (35,32).
print("PATH A: No H-seg at (35,32)")
print("=" * 60)
g = make_game()
act(g, GameAction.ACTION2)  # H to y=32
for _ in range(3): act(g, GameAction.ACTION4)  # H 5 segs, 8→(35,32)
# H has segs at x=5,11,17,23,29. No seg at 35.

switch_rack(g)
act(g, GameAction.ACTION4)  # V to x=35
for _ in range(6): act(g, GameAction.ACTION2)  # V 8 segs

t = get_targets(g)
h = get_h_segs(g)
t35 = sorted([(k,v) for k,v in t.items() if k[0]==35])
print(f"  V at x=35, 8 segs. H-segs at y=32: {h}")
print(f"  x=35 targets: {t35}")
print(f"  H-seg at (35,32)? {(35,32) in h}")

# VU
act(g, GameAction.ACTION1)
t_after = get_targets(g)
t35a = sorted([(k,v) for k,v in t_after.items() if k[0]==35])
print(f"  After VU: x=35 targets = {t35a}")

changes = []
all_k = sorted(set([k for k,_ in t35] + [k for k,_ in t35a]))
for k in all_k:
    b = dict(t35).get(k, '-')
    a = dict(t35a).get(k, '-')
    if b != a:
        changes.append(f"    {k}: {b} -> {a}")
print(f"  Changes at x=35: {len(changes)}")
for c in changes: print(c)


# Path B: Push 8@(29,32) to (35,32). THEN extend H to 6 segs (adding x=35).
# This pushes 8@(35,32) to (41,32). So we need to re-push another 8 to (35,32).
# Tricky because extending pushes the target away.

# Alternative: Push 8@(29,38) to (35,38). Then have H at y=38 with seg at (35,38).
# Then V at x=35, extended, VU — does 8@(35,38) move?

print(f"\n\nPATH B: H-seg at (35,38) overlapping with target")
print("=" * 60)
g = make_game()

# Push 8@(29,38) to (35,38): H at y=38, extend to 5 segs
act(g, GameAction.ACTION2)  # H to y=32
act(g, GameAction.ACTION2)  # H to y=38
for _ in range(3): act(g, GameAction.ACTION4)  # H 5 segs, 8@(29,38)→(35,38)
# H at y=38, 5 segs: x=5,11,17,23,29. No seg at 35.

# But I need seg at 35 for the test. So extend one more:
act(g, GameAction.ACTION4)  # H 6 segs: x=5,...,35. 8@(35,38) pushed to (41,38)!

# Argh, same problem. Extending to x=35 pushes the target away.

# Key insight: a target can only exist ON an H-rack segment if it was
# pushed there by the H-rack (parallel push failure = overlap).
# When H extends and push FAILS (parallel), the target stays and overlaps.

# So I need a situation where H extends and the push FAILS at (35,38).
# Push fails if chain goes OOB. Need target at (41,38) blocking.

# Let me set it up: first push 8@(29,44) to (41,44) via H extending to 6 at y=44.
# Then put something at (41,38) to block the chain at y=38.

# Actually, let me try: push 9@(41,26) to (41,38) using V-rack first.
# Then H at y=38 extends: 8@(29,38)→(35,38)→(41,38). 9@(41,38) chains to (47,38)? Empty.
# So push succeeds, not what I want.

# I need the chain to fail. Need OOB or obstacle at the end.
# For chain at y=38: push right → (35,38)→(41,38)→(47,38)→(53,38).
# (53,38): x+6=59 > 53=FXX. OOB! So if there are targets at (35,38),(41,38),(47,38),
# the 4th push to (53,38) fails.

# Let me create this scenario:
# Need 3 targets at x=35,41,47 on y=38, then H extending pushes 8@(29,38)→(35,38)
# Chain: (35,38)→(41,38)→(47,38)→(53,38) OOB. Push fails. 8@(29,38) stays. Overlap!

# This is hard to set up. Let me try a simpler approach.

# ================================================
# MINIMAL DEFINITIVE TEST
# ================================================
print(f"\n\nMINIMAL: V-rack extend/shrink with single target, vary H-seg overlap")
print("=" * 60)

# Setup: V-rack at x=35, push 9@(35,26) down then back up.
# Test 1: H-rack has NO seg at (35,26) — should move freely
# Test 2: H-rack HAS seg at (35,26) — blocked?

# But H-rack can't have seg at (35,26) because obstacle at (29,26) limits to 4 segs.
# H at y=26: max 4 segs (x=5,11,17,23). Can't reach x=35.

# Try different row. H-rack at y=20 with seg at (35,20).
# V-rack at x=35 pushing a target through y=20.

# Setup: push 9@(35,26) UP past y=20 using V extend/shrink.
# With H-rack having seg at (35,20): does the push get blocked?

print("Test 1: V-rack push through y=20, H-rack at y=20 with 2 segs (no x=35)")
g = make_game()

# Move H to y=20 (UP from y=26)
act(g, GameAction.ACTION1)  # H to y=20
h = get_h_segs(g)
print(f"  H-segs: {h}")

# Switch to V, move to x=35, extend to 8 then shrink to push 9 up
switch_rack(g)
act(g, GameAction.ACTION4)  # V to x=35
# Extend to 8 (pushes 9@(35,26) down to (35,44))
for _ in range(6): act(g, GameAction.ACTION2)
t = get_targets(g)
print(f"  After V extend to 8: x=35 targets = {[(k,v) for k,v in t.items() if k[0]==35]}")

# Shrink to 2 (pushes targets up through y=20)
for _ in range(6): act(g, GameAction.ACTION1)
t = get_targets(g)
print(f"  After V shrink to 2: x=35 targets = {[(k,v) for k,v in t.items() if k[0]==35]}")
# Target should have been pushed up through y=20,14,8
# H-rack at y=20 has segs at x=5,11 — NOT x=35. So no blocking.


print(f"\nTest 2: V-rack push through y=20, H-rack at y=20 with 6 segs (includes x=35)")
g = make_game()

# Move H to y=20 and extend to 6 segs
act(g, GameAction.ACTION1)  # H to y=20
for _ in range(4): act(g, GameAction.ACTION4)  # H 6 segs: x=5,...,35

h = get_h_segs(g)
print(f"  H-segs: {h}")
print(f"  H-seg at (35,20)? {(35,20) in h}")

t = get_targets(g)
print(f"  Targets: {[(k,v) for k,v in sorted(t.items()) if k[0]==35]}")

# Switch to V, move to x=35, extend to 8
switch_rack(g)
act(g, GameAction.ACTION4)  # V to x=35
for _ in range(6): act(g, GameAction.ACTION2)
t = get_targets(g)
print(f"  After V extend to 8: x=35 targets = {[(k,v) for k,v in sorted(t.items()) if k[0]==35]}")

# Shrink to 2
for _ in range(6): act(g, GameAction.ACTION1)
t = get_targets(g)
print(f"  After V shrink to 2: x=35 targets = {[(k,v) for k,v in sorted(t.items()) if k[0]==35]}")
# If H-seg at (35,20) blocks, target should stop at y=26 (one above y=20)
