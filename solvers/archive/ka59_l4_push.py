"""KA59 L4 — test cross-divider push mechanics."""
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


def state(g):
    pieces = sorted(g.current_level.get_sprites_by_tag('xlfuqjygey'), key=lambda s: s.name)
    enemies = sorted(g.current_level.get_sprites_by_tag('nnckfubbhi'), key=lambda s: s.name)
    sel = g.ascpmvdpwj
    parts = []
    for i, s in enumerate(pieces):
        mark = '*' if s is sel else ''
        parts.append(f"P{i}{mark}({s.x},{s.y})")
    for i, s in enumerate(enemies):
        parts.append(f"E{i}({s.x},{s.y})")
    return ' '.join(parts)


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


def get_pieces(g):
    return sorted(g.current_level.get_sprites_by_tag('xlfuqjygey'), key=lambda s: s.name)


# Test 1: Push P0 DOWN across horizontal divider using P1
print("=== Test 1: Push P0 DOWN across divider ===")
g = mod.Ka59()
g.set_level(3)
print(f"Start: {state(g)}")

# P0 at (15,24), P1 at (24,27)
# Move P0 down to boundary
for _ in range(2):
    g.perform_action(D)  # P0: 24→27→30
print(f"P0 at boundary: {state(g)}")

# Switch to P1
p = get_pieces(g)
ca = click_name(g, p[1].name)
g.perform_action(ca)

# Move P1 to same x as P0 (x=15) and above P0 (y<30)
# P1 at (24,27). Move left: 24→21→18→15 = 3L
for _ in range(3):
    g.perform_action(L)
print(f"P1 aligned: {state(g)}")

# Now P1 at (15,27) pushes P0 at (15,30) by moving DOWN
old_p0 = (p[0].x, p[0].y)
g.perform_action(D)
for s in g.current_level.get_sprites_by_tag('xlfuqjygey'):
    if s.name == p[0].name:
        new_p0 = (s.x, s.y)
print(f"DOWN PUSH: P0 {old_p0} → {new_p0}")
print(f"State: {state(g)}")

# Test 2: After push, probe P0's movement in bottom section
print("\n=== Test 2: P0 in bottom section ===")
ca = click_name(g, p[0].name)
if ca:
    g.perform_action(ca)

print(f"P0 at ({g.ascpmvdpwj.x},{g.ascpmvdpwj.y})")

for d_name, d_act in [('L', L), ('R', R), ('U', U), ('D', D)]:
    g2 = copy.deepcopy(g)
    positions = [(g2.ascpmvdpwj.x, g2.ascpmvdpwj.y)]
    for i in range(20):
        old = (g2.ascpmvdpwj.x, g2.ascpmvdpwj.y)
        g2.perform_action(d_act)
        new = (g2.ascpmvdpwj.x, g2.ascpmvdpwj.y)
        positions.append(new)
        if new == old:
            break
    print(f"  {d_name}: {positions[:15]}")

# Test 3: Push enemy RIGHT from bottom section
print("\n=== Test 3: Push enemy RIGHT ===")
# P0 in bottom section. Position next to enemy and push.
p0 = g.ascpmvdpwj
print(f"P0 at ({p0.x},{p0.y}), Enemy at (15,45)")

# Need P0 to the LEFT of enemy at same y.
# Move P0 down to enemy's row (y=45)
dy = 45 - p0.y
if dy > 0:
    for _ in range(dy // 3):
        g.perform_action(D)
p0 = g.ascpmvdpwj
print(f"P0 after down: ({p0.x},{p0.y})")

# Move P0 left to be LEFT of enemy
while p0.x > 6:
    g.perform_action(L)
    p0 = g.ascpmvdpwj
print(f"P0 to left of enemy: ({p0.x},{p0.y})")

# Push RIGHT toward enemy
for i in range(10):
    old_p0 = (g.ascpmvdpwj.x, g.ascpmvdpwj.y)
    en = g.current_level.get_sprites_by_tag('nnckfubbhi')
    old_e = (en[0].x, en[0].y) if en else None
    g.perform_action(R)
    new_p0 = (g.ascpmvdpwj.x, g.ascpmvdpwj.y)
    en = g.current_level.get_sprites_by_tag('nnckfubbhi')
    new_e = (en[0].x, en[0].y) if en else None
    if old_e != new_e:
        print(f"  R[{i}]: ENEMY PUSHED {old_e}→{new_e}, P0 {old_p0}→{new_p0}")
    elif new_p0 != old_p0:
        pass  # Normal move
    else:
        print(f"  R[{i}]: blocked P0={new_p0}")
        break
print(f"  State: {state(g)}")

# Test 4: Where does the enemy go when pushed right?
# If enemy crosses vertical divider, does it teleport?
en = g.current_level.get_sprites_by_tag('nnckfubbhi')
if en:
    print(f"\n  Enemy at ({en[0].x},{en[0].y}) — did it cross a divider?")

# Continue pushing to see if enemy crosses divider
print("\n  Continuing right push:")
for i in range(15):
    old_p0 = (g.ascpmvdpwj.x, g.ascpmvdpwj.y)
    en = g.current_level.get_sprites_by_tag('nnckfubbhi')
    old_e = (en[0].x, en[0].y) if en else None
    g.perform_action(R)
    new_p0 = (g.ascpmvdpwj.x, g.ascpmvdpwj.y)
    en = g.current_level.get_sprites_by_tag('nnckfubbhi')
    new_e = (en[0].x, en[0].y) if en else None
    if old_e != new_e:
        print(f"  R[{i}]: ENEMY PUSHED {old_e}→{new_e}")
    elif new_p0 == old_p0:
        print(f"  R[{i}]: blocked P0={new_p0}, E={old_e}")
        break
print(f"  Final: {state(g)}")

# Test 5: Push enemy UP?
print("\n=== Test 5: Push enemy UP from below ===")
g = mod.Ka59()
g.set_level(3)
# P0(15,24) P1(24,27) E(15,45)
# Push P0 down to bottom section first
for _ in range(2):
    g.perform_action(D)  # P0→(15,30)
ca = click_name(g, get_pieces(g)[1].name)
g.perform_action(ca)
for _ in range(3):
    g.perform_action(L)  # P1→(15,27)
g.perform_action(D)  # Push P0 down: (15,30)→bottom
ca = click_name(g, get_pieces(g)[0].name)
g.perform_action(ca)
p0 = g.ascpmvdpwj
print(f"P0 in bottom section: ({p0.x},{p0.y})")

# Move P0 below enemy: enemy at (15,45), 9x9 → bottom at 54
# Move P0 down to y=54+ then left to x=15
while p0.y < 54:
    g.perform_action(D)
    p0 = g.ascpmvdpwj
print(f"P0 below enemy: ({p0.x},{p0.y})")

# Now try UP into enemy
for i in range(5):
    old_p0 = (g.ascpmvdpwj.x, g.ascpmvdpwj.y)
    en = g.current_level.get_sprites_by_tag('nnckfubbhi')
    old_e = (en[0].x, en[0].y) if en else None
    g.perform_action(U)
    new_p0 = (g.ascpmvdpwj.x, g.ascpmvdpwj.y)
    en = g.current_level.get_sprites_by_tag('nnckfubbhi')
    new_e = (en[0].x, en[0].y) if en else None
    if old_e != new_e:
        print(f"  U[{i}]: ENEMY PUSHED UP {old_e}→{new_e}, P0={new_p0}")
    elif new_p0 != old_p0:
        print(f"  U[{i}]: P0 moved {old_p0}→{new_p0}, E={old_e}")
    else:
        print(f"  U[{i}]: blocked P0={new_p0}, E={old_e}")
print(f"  Final: {state(g)}")

# Test 6: Push enemy DOWN
print("\n=== Test 6: Push enemy DOWN from above ===")
g = mod.Ka59()
g.set_level(3)
# Push P0 to bottom section
for _ in range(2):
    g.perform_action(D)
ca = click_name(g, get_pieces(g)[1].name)
g.perform_action(ca)
for _ in range(3):
    g.perform_action(L)
g.perform_action(D)
ca = click_name(g, get_pieces(g)[0].name)
g.perform_action(ca)
p0 = g.ascpmvdpwj
print(f"P0: ({p0.x},{p0.y})")

# Move P0 to just above enemy
# Enemy top at y=45. P0 (3x3) needs bottom at y=45 → P0 at y=42
while p0.y < 42:
    g.perform_action(D)
    p0 = g.ascpmvdpwj
    if p0.y >= 42:
        break
print(f"P0 above enemy: ({p0.x},{p0.y})")

# Push DOWN
for i in range(3):
    old_p0 = (g.ascpmvdpwj.x, g.ascpmvdpwj.y)
    en = g.current_level.get_sprites_by_tag('nnckfubbhi')
    old_e = (en[0].x, en[0].y) if en else None
    g.perform_action(D)
    new_p0 = (g.ascpmvdpwj.x, g.ascpmvdpwj.y)
    en = g.current_level.get_sprites_by_tag('nnckfubbhi')
    new_e = (en[0].x, en[0].y) if en else None
    if old_e != new_e:
        print(f"  D[{i}]: ENEMY PUSHED DOWN {old_e}→{new_e}, P0={new_p0}")
    elif new_p0 != old_p0:
        print(f"  D[{i}]: P0 moved {old_p0}→{new_p0}, E={old_e}")
    else:
        print(f"  D[{i}]: blocked P0={new_p0}, E={old_e}")
print(f"  Final: {state(g)}")
