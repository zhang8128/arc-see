"""KA59 L2 solver — 4 pieces, no enemies, complex push routing."""
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


def click_sprite(g, name):
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


def exec_seq(g, seq, verbose=False):
    """Execute a sequence like 'RRRLDLLL' or with Cn for clicks."""
    count = 0
    i = 0
    while i < len(seq):
        ch = seq[i]
        if ch in AM:
            g.perform_action(AM[ch])
            count += 1
        elif ch == 'C':
            i += 1
            name_idx = int(seq[i])
            pieces = sorted(g.current_level.get_sprites_by_tag('xlfuqjygey'), key=lambda s: s.name)
            ca = click_sprite(g, pieces[name_idx].name)
            if ca:
                g.perform_action(ca)
                count += 1
        i += 1
    if verbose:
        print(f"  After {count} actions: {state(g)}")
    return count


def test_push(start_seq, push_direction, piece_name=None):
    """Test: after start_seq, try pushing in push_direction."""
    g = mod.Ka59()
    g.set_level(1)
    n = exec_seq(g, start_seq, verbose=True)

    g_before = copy.deepcopy(g)
    g.perform_action(AM[push_direction])
    n += 1

    # Compare states
    pieces_before = {s.name: (s.x, s.y) for s in g_before.current_level.get_sprites_by_tag('xlfuqjygey')}
    pieces_after = {s.name: (s.x, s.y) for s in g.current_level.get_sprites_by_tag('xlfuqjygey')}

    for name in pieces_before:
        bx, by = pieces_before[name]
        ax, ay = pieces_after[name]
        if bx != ax or by != ay:
            print(f"  {push_direction}: {name} ({bx},{by}) → ({ax},{ay}) delta=({ax-bx},{ay-by})")

    print(f"  After push: {state(g)}")
    return g, n


# L2 Layout:
# P0 = cisjjwiopp (33,42) 3x6 → target (9,9)  [needs divider crossing LEFT]
# P1 = peoafdrnua (42,45) 6x6 → target (6,42)  [needs divider crossing LEFT]
# P2 = pomlugyufe (36,54) 3x3 → target (51,51) [easy, right side]
# P3 = sfcitxooao (39,33) 6x3 → target (54,39) [easy, right side]
#
# Vertical divider at x≈21-29 (f-type, crossable by push)
# Horizontal divider at y≈24-26
# P0 needs to go from (33,42) to (9,9) — must cross both dividers
# P1 needs to go from (42,45) to (6,42) — must cross vertical divider

print("=== Testing push mechanics in L2 ===\n")

# Test 1: Move P0 left to the divider boundary
print("Test 1: Move P0 left toward divider")
g = mod.Ka59()
g.set_level(1)
print(f"  Start: {state(g)}")

# Move P0 left as far as possible
for i in range(20):
    old = g.ascpmvdpwj.x
    g.perform_action(L)
    if g.ascpmvdpwj.x == old:
        print(f"  P0 blocked at x={old} after {i} LEFT moves")
        break
print(f"  State: {state(g)}")

print()

# Test 2: Can P3 push P0 left?
# P3 starts at (39,33), P0 at (33,42). Need to align them horizontally.
# Move P0 up to P3's row, then have P3 push P0 left
print("Test 2: Position P0 near P3, have P3 push P0")
g = mod.Ka59()
g.set_level(1)
# Move P0 up to row 33 (from 42, need 3 up moves = -9 units)
n = exec_seq(g, 'UUU', verbose=True)  # P0 at (33,33)
# Now P0 at (33,33), P3 at (39,33). Switch to P3 and push left.
print(f"  P0 at ({g.ascpmvdpwj.x},{g.ascpmvdpwj.y})")
# Switch to P3
n += exec_seq(g, 'C3', verbose=True)
# Move P3 left toward P0 — P3 is 6x3 at (39,33)
for i in range(5):
    old_state = {s.name: (s.x, s.y) for s in g.current_level.get_sprites_by_tag('xlfuqjygey')}
    g.perform_action(L)
    new_state = {s.name: (s.x, s.y) for s in g.current_level.get_sprites_by_tag('xlfuqjygey')}
    for name in old_state:
        ox, oy = old_state[name]
        nx, ny = new_state[name]
        if ox != nx or oy != ny:
            print(f"  L[{i}]: {name} ({ox},{oy}) → ({nx},{ny})")
    sel = g.ascpmvdpwj
    print(f"  After L[{i}]: selected={sel.name}({sel.x},{sel.y}), state={state(g)}")

print()

# Test 3: What happens when we push across the divider?
# First, let's find where exactly the divider is
print("Test 3: Find divider boundary by probing")
g = mod.Ka59()
g.set_level(1)
# Move P0 left step by step until blocked
positions = [(g.ascpmvdpwj.x, g.ascpmvdpwj.y)]
for i in range(20):
    old = g.ascpmvdpwj.x
    g.perform_action(L)
    positions.append((g.ascpmvdpwj.x, g.ascpmvdpwj.y))
    if g.ascpmvdpwj.x == old:
        print(f"  Blocked at x={old} on move {i+1}")
        break
print(f"  Position trace: {positions}")

# Now try UP from here
print("  Trying UP from blocked position:")
for i in range(20):
    old = (g.ascpmvdpwj.x, g.ascpmvdpwj.y)
    g.perform_action(U)
    new = (g.ascpmvdpwj.x, g.ascpmvdpwj.y)
    if new != old:
        print(f"  U[{i}]: {old} → {new}")
    else:
        print(f"  U[{i}]: blocked at {old}")
        break

print()

# Test 4: Try to push P0 across divider using P1
# P0 (3x6) at (33,42), P1 (6x6) at (42,45)
# Need to align them on same row and have P1 push P0 left
print("Test 4: Push P0 left using P1")
g = mod.Ka59()
g.set_level(1)
# Move P0 left as far as we can
n = exec_seq(g, 'L', verbose=True)  # P0 at (30,42)
# Switch to P1
n += exec_seq(g, 'C1', verbose=True)
# P1 at (42,45). Move up to align with P0's y
n += exec_seq(g, 'U', verbose=True)  # P1 at (42,42)
# Now push P1 left until it hits P0
print("  Pushing P1 left toward P0:")
for i in range(10):
    old_state = {s.name: (s.x, s.y) for s in g.current_level.get_sprites_by_tag('xlfuqjygey')}
    g.perform_action(L)
    new_state = {s.name: (s.x, s.y) for s in g.current_level.get_sprites_by_tag('xlfuqjygey')}
    changes = []
    for name in old_state:
        ox, oy = old_state[name]
        nx, ny = new_state[name]
        if ox != nx or oy != ny:
            changes.append(f"{name}({ox},{oy})→({nx},{ny})")
    if changes:
        print(f"  L[{i}]: {', '.join(changes)}")
    else:
        print(f"  L[{i}]: no movement")
        break
    sel = g.ascpmvdpwj
    won = g._current_level_index > 1
    if won:
        print("  WON!")
        break
print(f"  Final: {state(g)}")
