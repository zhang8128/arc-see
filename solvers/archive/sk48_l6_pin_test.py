#!/usr/bin/env python3
"""SK48 L6 — Test: is target pinned by cross-rack seg at SAME position vs DESTINATION?"""

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

def get_targets(g):
    return {(t.x, t.y): int(t.pixels[1,1]) for t in g.vbelzuaian if t.y < 50}

def get_h_segs(g):
    for r, sl in g.mwfajkguqx.items():
        if r.rotation == 0 and r.y < 50:
            return set((s.x, s.y) for s in sl)
    return set()

# TEST: Push target where destination has cross-rack seg but source doesn't.
# If destination-blocking is the issue, push fails.
# If source-blocking is the issue, push succeeds (source is clean).

print("Test: Target at clean position, pushed TO cross-rack seg position")
print("=" * 60)

g = make_game()

# Setup: H-rack at y=20 with seg at (35,20). V-rack pushes target toward y=20.
# V-rack at x=35 with target at y=26 (9@(35,26)).
# Push target DOWN from y=26 to y=32 (away from H-seg at y=20). Check it works.
# Then push UP from y=26 toward y=20 (toward H-seg). Does it fail?

# Step 1: Move H-rack to y=20 and extend to cover x=35
act(g, GameAction.ACTION1)  # H to y=20
for _ in range(4): act(g, GameAction.ACTION4)  # H 6 segs: x=5..35

h_segs = get_h_segs(g)
print(f"H-segs: includes (35,20)? {(35,20) in h_segs}")

# Step 2: Switch to V-rack, move to x=35
switch_rack(g)
act(g, GameAction.ACTION4)  # V to x=35

# Step 3: Extend V to 5 segs (y=2..26). 9@(35,26) pushed to (35,32).
for _ in range(3): act(g, GameAction.ACTION2)  # V 5 segs

t = get_targets(g)
print(f"After V extend to 5: targets at x=35 = {[(k,v) for k,v in sorted(t.items()) if k[0]==35]}")
# 9 should be at (35,32) now.

# Step 4: Shrink V. This should push 9@(35,32) UP to (35,26).
# Source (35,32) has no H-seg (H at y=20, not y=32).
# Destination (35,26) has no H-seg either (H at y=20, not y=26).
act(g, GameAction.ACTION1)  # VU: 5→4 segs
t = get_targets(g)
print(f"After VU to 4: x=35 targets = {[(k,v) for k,v in sorted(t.items()) if k[0]==35]}")

# Step 5: Shrink again. Should push 9@(35,26) to (35,20).
# Source (35,26) has no H-seg.
# Destination (35,20) HAS H-seg!
act(g, GameAction.ACTION1)  # VU: 4→3 segs
t = get_targets(g)
print(f"After VU to 3: x=35 targets = {[(k,v) for k,v in sorted(t.items()) if k[0]==35]}")
print("  If 9 at (35,26): DESTINATION blocking confirmed")
print("  If 9 at (35,20): Neither blocking applies")
print("  If 9 at (35,14): Both passed through")

# Now test source blocking
print(f"\n\nTest: Source-blocking")
print("=" * 60)
# Can we create a state where target is ON a cross-rack seg?
# This happens when parallel push fails (target stays, segment passes through).
# H-rack at y=20 extends: if target at (35,20) exists and chain to (41,20) etc fails,
# the target stays at (35,20) and H-seg overlaps.
# But H-seg extend PUSHES targets, so target would be pushed right.

# Let me think differently. After V-rack pushes target to (35,32) and then
# H-rack has a seg at (35,32)... Actually this can't happen because
# adding H-seg at x=35 would push the target.

# The only way a target ends up ON a cross-rack seg is if:
# 1. Target was already there when the other rack extended to that position
# 2. The other rack's extension pushed it but push FAILED (parallel overlap)

# Case 2: V-rack at x=35 extends down, and at y=32 there's a target.
# V-rack pushes it DOWN. If push succeeds, target moves. If fails, target stays
# and V-seg at (35,32) overlaps with it. Now H-rack at y=32 has seg at (35,32).
# The target at (35,32) is overlapped by BOTH V-seg and H-seg.

# Actually this gets complicated. Let me just test the exact step 30 scenario
# more carefully to determine the blocking model.

# From the exact test: at step 30, V at x=41, 8 segs. H at y=32, 7 segs.
# H-seg at (41,32). Target 8@(41,32).
# VU: target stays at (41,32).

# Question: is target pinned because of H-seg at SOURCE (41,32)?
# Or because push chain to (41,26) fails due to H-seg at DESTINATION?
# Answer: (41,26) has no H-seg (H at y=32, not y=26). So destination is clear.
# Therefore it must be source-pinning.

# But wait — maybe (41,26) DOES have something. Let me check if V-rack seg at (41,26) counts.
# V-rack at x=41 with 8 segs includes y=26. V-seg at (41,26).
# The target at (41,32) is being pushed by V-rack. V-rack's OWN segments shouldn't block.
# And H-rack at y=32 doesn't have seg at y=26.

# So destination (41,26) is clear of cross-rack segs. Source (41,32) has H-seg. → Source blocking.

print("From step-30 analysis:")
print("  Target 8@(41,32): H-seg at (41,32), no H-seg at (41,26)")
print("  Push UP to (41,26) FAILED → source-blocking confirmed")
print("  (target is pinned by overlapping cross-rack segment)")
