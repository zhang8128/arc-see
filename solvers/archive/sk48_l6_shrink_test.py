#!/usr/bin/env python3
"""SK48 L6 — Test shrink push chain behavior in engine."""

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

def get_state(g):
    targets = {}
    for t in g.vbelzuaian:
        if t.y < 50:
            targets[(t.x, t.y)] = int(t.pixels[1, 1])
    segs = {}
    for r, sl in g.mwfajkguqx.items():
        segs[(r.x, r.y, r.rotation)] = len(sl)
    return segs, targets

# ==========================================
# Test: V-rack shrink with chain of targets
# ==========================================
print("TEST: V-rack shrink with multiple targets on column")
print("=" * 60)

# Set up: push 8-targets to x=41 using H-rack, then test V-rack shrink
g = make_game()

# Step 1: H-rack pushes 8-targets from x=29 to x=41
# Move H down to y=32, extend to push
act(g, GameAction.ACTION2)  # D: y=26→32
for _ in range(4): act(g, GameAction.ACTION4)  # R×4: extend to 6 segs, push 8@(29,32)→(41,32)
for _ in range(4): act(g, GameAction.ACTION3)  # L×4: shrink back to 2

# Move to y=38
act(g, GameAction.ACTION2)  # D: y=32→38
for _ in range(4): act(g, GameAction.ACTION4)
for _ in range(4): act(g, GameAction.ACTION3)

# Move to y=44
act(g, GameAction.ACTION2)  # D: y=38→44
for _ in range(4): act(g, GameAction.ACTION4)
for _ in range(4): act(g, GameAction.ACTION3)

segs, targets = get_state(g)
print(f"After pushing 8s to x=41:")
print(f"  Segs: {segs}")
x41_targets = {k:v for k,v in targets.items() if k[0] == 41}
print(f"  x=41 targets: {x41_targets}")
other_targets = {k:v for k,v in targets.items() if k[0] != 41}
print(f"  Other targets: {other_targets}")

# Step 2: Switch to V-rack, move to x=41, extend to 8 segs
switch_rack(g)  # Switch to V
act(g, GameAction.ACTION4)  # R: x=29→35
act(g, GameAction.ACTION4)  # R: x=35→41
for _ in range(6): act(g, GameAction.ACTION2)  # D×6: extend to 8 segs

segs, targets = get_state(g)
print(f"\nAfter V-rack at x=41, 8 segs:")
print(f"  Segs: {segs}")
x41_targets = {k:v for k,v in targets.items() if k[0] == 41}
print(f"  x=41 targets: {x41_targets}")

# Step 3: Shrink V-rack and watch what happens to targets
print(f"\nShrinking V-rack (VU):")
for i in range(6):
    act(g, GameAction.ACTION1)  # U: shrink
    segs, targets = get_state(g)
    x41_targets = {k:v for k,v in targets.items() if k[0] == 41}
    v_segs = [v for k,v in segs.items() if k[2] == 90]
    print(f"  After VU({i+1}): V-segs={v_segs[0] if v_segs else '?'}, x=41 targets={x41_targets}")

# ==========================================
# SIMPLER TEST: Just 2 adjacent targets
# ==========================================
print("\n\nSIMPLER TEST: 2 adjacent targets on V-rack column")
print("=" * 60)

g = make_game()

# Just push 8@(29,32) to (35,32) using H-rack
act(g, GameAction.ACTION2)  # D: y=26→32
for _ in range(3): act(g, GameAction.ACTION4)  # R×3: extend to 5 segs, push to (35,32)
for _ in range(3): act(g, GameAction.ACTION3)  # L×3: back to 2

segs, targets = get_state(g)
print(f"After push: targets = {targets}")

# Switch to V, move to x=35
switch_rack(g)
act(g, GameAction.ACTION4)  # R: x=29→35

# Now 9@(35,26) is on y=26. 8@(35,32) is on y=32.
# Extend V to 6 segs (y=2,...,32). During extension:
# D(3): seg y=26 → push 9@(35,26) to (35,32). 8@(35,32) chains to (35,38).
#        Is (35,38) empty? No, 8@(29,38) is at x=29 not x=35. Yes empty.
# D(4): seg y=32 → push 8@(35,32)... wait, 9 was pushed there. What's at (35,32)?

print(f"\nExtending V-rack at x=35:")
for i in range(6):
    act(g, GameAction.ACTION2)  # D: extend
    segs, targets = get_state(g)
    x35_targets = {k:v for k,v in targets.items() if k[0] == 35}
    v_segs = [v for k,v in segs.items() if k[2] == 90]
    print(f"  After VD({i+1}): V-segs={v_segs[0] if v_segs else '?'}, x=35 targets={x35_targets}")

# Now shrink
print(f"\nShrinking V-rack at x=35:")
for i in range(6):
    act(g, GameAction.ACTION1)  # U: shrink
    segs, targets = get_state(g)
    x35_targets = {k:v for k,v in targets.items() if k[0] == 35}
    v_segs = [v for k,v in segs.items() if k[2] == 90]
    print(f"  After VU({i+1}): V-segs={v_segs[0] if v_segs else '?'}, x=35 targets={x35_targets}")

# ==========================================
# MINIMAL TEST: H-rack shrink with pushed targets
# ==========================================
print("\n\nMINIMAL TEST: H-rack extend pushes target, then shrink")
print("=" * 60)

g = make_game()

# H-rack at y=32
act(g, GameAction.ACTION2)  # D: y=26→32

# Extend to 5 (push 8 from 29 to 35)
for _ in range(3): act(g, GameAction.ACTION4)
segs, targets = get_state(g)
print(f"After 5 segs: targets={targets}")

# Now shrink with L
act(g, GameAction.ACTION3)
segs, targets = get_state(g)
print(f"After L (shrink to 4): targets={targets}")

act(g, GameAction.ACTION3)
segs, targets = get_state(g)
print(f"After L (shrink to 3): targets={targets}")

act(g, GameAction.ACTION3)
segs, targets = get_state(g)
print(f"After L (shrink to 2): targets={targets}")
