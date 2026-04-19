"""KA59 L2 — test UP push and divider crossing strategies."""
import copy
import importlib.util
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('ka59', 'environment_files/ka59/9f096b4a/ka59.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

U = ActionInput(id=GameAction.ACTION1, data={})
D = ActionInput(id=GameAction.ACTION2, data={})
L = ActionInput(id=GameAction.ACTION3, data={})
R = ActionInput(id=GameAction.ACTION4, data={})
AM = {'U': U, 'D': D, 'L': L, 'R': R}


def click_name(g, name):
    for s in g.current_level.get_sprites_by_tag('xlfuqjygey'):
        if s.name == name:
            gx = s.x + s.width // 2
            gy = s.y + s.height // 2
            sc, ox, oy = g.camera._calculate_scale_and_offset()
            dx = int(gx * sc + ox)
            dy = int(gy * sc + oy)
            return ActionInput(id=GameAction.ACTION6, data={'x': dx, 'y': dy})
    return None


def state(g):
    pieces = sorted(g.current_level.get_sprites_by_tag('xlfuqjygey'), key=lambda s: s.name)
    sel = g.ascpmvdpwj
    parts = []
    for i, s in enumerate(pieces):
        mark = '*' if s is sel else ''
        parts.append(f"P{i}{mark}({s.x},{s.y})")
    return ' '.join(parts)


def do_seq(g, actions_str, verbose=True):
    """Execute 'UUULLLC1RR' format. Cn = click piece n (sorted by name)."""
    count = 0
    i = 0
    while i < len(actions_str):
        ch = actions_str[i]
        if ch in AM:
            g.perform_action(AM[ch])
            count += 1
        elif ch == 'C':
            i += 1
            idx = int(actions_str[i])
            pieces = sorted(g.current_level.get_sprites_by_tag('xlfuqjygey'), key=lambda s: s.name)
            ca = click_name(g, pieces[idx].name)
            if ca:
                g.perform_action(ca)
                count += 1
        i += 1
    if verbose:
        print(f"  After {actions_str} ({count} acts): {state(g)}")
    won = g._current_level_index > 1
    if won and verbose:
        print("  *** WON! ***")
    return count, won


# Test 1: Can P3 push P0 UP?
print("=== Test 1: UP push using P3 ===")
g = mod.Ka59()
g.set_level(1)
print(f"Start: {state(g)}")
# P0 at (33,42), P3 at (39,33)
# Move P0 up to y=30 (4 UP = -12)
n, _ = do_seq(g, 'UUUU')  # P0 → (33,30)
# Move P3 left to x=33 (2 LEFT = -6)
n2, _ = do_seq(g, 'C3LL')  # P3 → (33,33)
# Now P3 UP should push P0
print("Pushing P3 UP (should push P0):")
old_state = {s.name: (s.x, s.y) for s in g.current_level.get_sprites_by_tag('xlfuqjygey')}
g.perform_action(U)
new_state = {s.name: (s.x, s.y) for s in g.current_level.get_sprites_by_tag('xlfuqjygey')}
for name in old_state:
    ox, oy = old_state[name]
    nx, ny = new_state[name]
    if ox != nx or oy != ny:
        print(f"  {name}: ({ox},{oy}) → ({nx},{ny}) delta=({nx-ox},{ny-oy})")
print(f"  Result: {state(g)}")


# Test 2: After UP push, probe P0's movement on the top side
print("\n=== Test 2: Probe P0 movement after UP push ===")
# P0 should be at (33,15) if push worked
ca = click_name(g, 'cisjjwiopp')
if ca:
    g.perform_action(ca)

print(f"P0 selected at ({g.ascpmvdpwj.x},{g.ascpmvdpwj.y})")

for d_name, d_act in [('LEFT', L), ('RIGHT', R), ('UP', U), ('DOWN', D)]:
    g2 = copy.deepcopy(g)
    positions = [(g2.ascpmvdpwj.x, g2.ascpmvdpwj.y)]
    for i in range(20):
        old = (g2.ascpmvdpwj.x, g2.ascpmvdpwj.y)
        g2.perform_action(d_act)
        new = (g2.ascpmvdpwj.x, g2.ascpmvdpwj.y)
        positions.append(new)
        if new == old:
            break
    print(f"  {d_name}: {positions}")


# Test 3: Full plan — push P0 UP then LEFT to target (9,9)
print("\n=== Test 3: Route P0 to target (9,9) ===")
g = mod.Ka59()
g.set_level(1)
total = 0

# Step 1: P0 up to y=30
n, _ = do_seq(g, 'UUUU')
total += n

# Step 2: P3 pushes P0 UP
n, _ = do_seq(g, 'C3LLU')
total += n

# Step 3: P0 should be at (33,15). Now need to push LEFT across vertical divider.
# Need someone to the right of P0. P3 is at (33,33), P1 at (42,45), P2 at (36,54)
# P3 at (33,33) — can P3 move up to (33,30)? Let's check.
n, _ = do_seq(g, 'U')  # P3 tries to go up
# Hmm, P3 is at y=33, moving up to y=30 — but the horizontal divider blocks at y=30?
# Actually P3 is on the right side (x=33 >= 30), so it should be blocked by the horizontal divider.

# Alternative: navigate P0 left from (33,15) — does the vertical divider block at y=15?
n, _ = do_seq(g, 'C0')  # Select P0
total += n
# Try moving left
print("Moving P0 left:")
for i in range(15):
    old = (g.ascpmvdpwj.x, g.ascpmvdpwj.y)
    g.perform_action(L)
    total += 1
    new = (g.ascpmvdpwj.x, g.ascpmvdpwj.y)
    if new != old:
        print(f"  L[{i}]: {old} → {new}")
    else:
        print(f"  L[{i}]: blocked at {old}")
        total -= 1  # Don't count if we're going to retry
        break
print(f"  P0 final: ({g.ascpmvdpwj.x},{g.ascpmvdpwj.y}), total={total}")

# Now move down to y=9
print("Moving P0 down to y=9:")
for i in range(10):
    old = (g.ascpmvdpwj.x, g.ascpmvdpwj.y)
    g.perform_action(D)
    total += 1
    new = (g.ascpmvdpwj.x, g.ascpmvdpwj.y)
    if new != old:
        if new[1] == 9:
            print(f"  D[{i}]: {old} → {new} REACHED TARGET Y!")
            break
    else:
        print(f"  D[{i}]: blocked at {old}")
        total -= 1
        break
print(f"  P0 at ({g.ascpmvdpwj.x},{g.ascpmvdpwj.y}), total={total}")
print(f"  Full state: {state(g)}")


# Test 4: Alternative — push P0 LEFT first, then UP
print("\n=== Test 4: Push P0 LEFT first, then try UP push from left side ===")
g = mod.Ka59()
g.set_level(1)
total = 0

# Move P0 up to P3's row
n, _ = do_seq(g, 'UUU')  # P0 → (33,33)
total += n

# P3 pushes P0 LEFT
n, _ = do_seq(g, 'C3LL')  # P3→(33,33), push P0→(18,33)
total += n

# Now P0 at (18,33) on left side. Move up to y=30 boundary
n, _ = do_seq(g, 'C0U')  # P0→(18,30)
total += n

# Now need to push P0 UP from (18,30). Need a piece at (18, 33).
# Push P2 (3x3 at 36,54) to left side at (18, 33)?
# First push P2 to left side: need P1 or P3 to push P2 LEFT
# P2 at (36,54), P1 at (42,45). To push P2, need a piece at right of P2 at same y.
# P1 at (42,45) — move P1 down to y=54? P1 is 6x6 at (42,45). Move down: 3 moves = y=45→48→51→54
# Then push P1 LEFT into P2.

n, _ = do_seq(g, 'C1DDD')  # P1→(42,54)
total += n
n, _ = do_seq(g, 'LL')  # P1→(36,54) — wait, P2 is at (36,54)! This should push P2!
total += n
print(f"  After push attempt: {state(g)}")

# How far did P2 go?
pieces = {s.name: (s.x, s.y) for s in g.current_level.get_sprites_by_tag('xlfuqjygey')}
print(f"  P2 (pomlugyufe) at: {pieces.get('pomlugyufe')}")

# Now position P2 to push P0 UP
# P2 should be somewhere on the left side now. Move P2 up to align with P0
n, _ = do_seq(g, 'C2')  # Select P2
total += n
print(f"  P2 at ({g.ascpmvdpwj.x},{g.ascpmvdpwj.y})")

# Move P2 left to x=18 (P0's x), then up to y=33 (just below P0 at y=30)
# But wait — does P2 need to be at x=18 exactly? P0 is 3x6, P2 is 3x3
# P0 occupies x=18-20. P2 occupies 3 wide. P2 needs to overlap in x with P0.

print("Moving P2 to align with P0:")
# Move P2 left to x=18
for i in range(20):
    old = g.ascpmvdpwj.x
    g.perform_action(L)
    total += 1
    if g.ascpmvdpwj.x == old:
        print(f"  P2 blocked LEFT at x={old}")
        total -= 1
        break
    if g.ascpmvdpwj.x == 18:
        print(f"  P2 reached x=18")
        break

# Move P2 up to y=33
for i in range(20):
    old = g.ascpmvdpwj.y
    g.perform_action(U)
    total += 1
    if g.ascpmvdpwj.y == old:
        print(f"  P2 blocked UP at y={old}")
        total -= 1
        break
    if g.ascpmvdpwj.y == 33:
        print(f"  P2 reached y=33")
        break

print(f"  P2 at ({g.ascpmvdpwj.x},{g.ascpmvdpwj.y})")
print(f"  Full state: {state(g)}")

# Now P2 pushes P0 UP
print("P2 pushes P0 UP:")
old_state = {s.name: (s.x, s.y) for s in g.current_level.get_sprites_by_tag('xlfuqjygey')}
g.perform_action(U)
total += 1
new_state = {s.name: (s.x, s.y) for s in g.current_level.get_sprites_by_tag('xlfuqjygey')}
for name in old_state:
    ox, oy = old_state[name]
    nx, ny = new_state[name]
    if ox != nx or oy != ny:
        print(f"  {name}: ({ox},{oy}) → ({nx},{ny}) delta=({nx-ox},{ny-oy})")
print(f"  State: {state(g)}")
print(f"  Total actions so far: {total}")
