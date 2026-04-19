"""KA59 L4 — explore enemy push mechanics and board layout.

L4: 2 pieces (3x3) + 1 enemy (9x9)
  P0: (15,24) [SELECTED]
  P1: (24,27)
  Enemy: (15,45) 9x9
  Player frames: (44,23)→(45,24), (32,47)→(33,48)
  Enemy frame: (29,2)→(30,3) — enemy needs to reach (30,3)!
  Baseline: 47

From memory: enemies can ONLY be pushed L/R, not U/D in L4.
Enemy at (15,45) needs to reach (30,3) — that's +15 right, -42 up.
"""
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
    for tag in ['xlfuqjygey']:
        for s in g.current_level.get_sprites_by_tag(tag):
            if s.name == name:
                gx = s.x + s.width // 2
                gy = s.y + s.height // 2
                sc, ox, oy = g.camera._calculate_scale_and_offset()
                dx = int(gx * sc + ox)
                dy = int(gy * sc + oy)
                return ActionInput(id=GameAction.ACTION6, data={'x': dx, 'y': dy})
    return None


print("=== L4 Board Layout ===")
g = mod.Ka59()
g.set_level(3)
print(f"State: {state(g)}")

pieces = sorted(g.current_level.get_sprites_by_tag('xlfuqjygey'), key=lambda s: s.name)
enemies = sorted(g.current_level.get_sprites_by_tag('nnckfubbhi'), key=lambda s: s.name)
frames = sorted(g.current_level.get_sprites_by_tag('rktpmjcpkt'), key=lambda s: s.name)
eframes = sorted(g.current_level.get_sprites_by_tag('ucjzrlvfkb'), key=lambda s: s.name)

for s in pieces:
    print(f"Piece: {s.name} ({s.x},{s.y}) {s.width}x{s.height}")
for s in enemies:
    print(f"Enemy: {s.name} ({s.x},{s.y}) {s.width}x{s.height}")
for s in frames:
    print(f"PFrame: {s.name} ({s.x},{s.y}) {s.width}x{s.height} → target ({s.x+1},{s.y+1})")
for s in eframes:
    print(f"EFrame: {s.name} ({s.x},{s.y}) {s.width}x{s.height} → target ({s.x+1},{s.y+1})")

# Find all wall sprites (dividers)
dividers = g.current_level.get_sprites_by_tag('hrxbqacjad')
if dividers:
    print(f"\nDividers ({len(dividers)}):")
    for d in dividers[:10]:
        print(f"  {d.name} ({d.x},{d.y}) {d.width}x{d.height}")

# Check all tags in the level
all_sprites = g.current_level.get_sprites()
tags = set()
for s in all_sprites:
    for t in s.tags:
        tags.add(t)
print(f"\nAll tags: {tags}")

# Probe boundaries for P0
print("\n=== P0 Boundary Probe ===")
for d_name, d_act in [('L', L), ('R', R), ('U', U), ('D', D)]:
    g2 = copy.deepcopy(g)
    pos = [(g2.ascpmvdpwj.x, g2.ascpmvdpwj.y)]
    for i in range(20):
        old = (g2.ascpmvdpwj.x, g2.ascpmvdpwj.y)
        g2.perform_action(d_act)
        new = (g2.ascpmvdpwj.x, g2.ascpmvdpwj.y)
        pos.append(new)
        if new == old:
            break
    print(f"  {d_name}: {pos[:15]}")

# Test enemy push: move P0 toward enemy and push
print("\n=== Enemy Push Tests ===")

# Test push LEFT into enemy
print("Test: P0 moves DOWN toward enemy at (15,45)")
g = mod.Ka59()
g.set_level(3)
# P0 at (15,24). Enemy at (15,45). Same x!
# Move P0 down toward enemy
for i in range(10):
    old_p0 = (g.ascpmvdpwj.x, g.ascpmvdpwj.y)
    old_e = (enemies[0].x, enemies[0].y) if enemies else None
    g.perform_action(D)
    new_p0 = (g.ascpmvdpwj.x, g.ascpmvdpwj.y)
    # Re-read enemy position
    en = g.current_level.get_sprites_by_tag('nnckfubbhi')
    new_e = (en[0].x, en[0].y) if en else None
    if new_p0 != old_p0 or new_e != old_e:
        print(f"  D[{i}]: P0 {old_p0}→{new_p0}, E {old_e}→{new_e}")
    else:
        print(f"  D[{i}]: blocked, P0={new_p0}, E={new_e}")
        break
print(f"  Final: {state(g)}")

# Test push RIGHT from left of enemy
print("\nTest: Position P0 to LEFT of enemy, push RIGHT")
g = mod.Ka59()
g.set_level(3)
# P0 at (15,24). Need to move DOWN past enemy and then LEFT of enemy
# Enemy at (15,45), 9x9 → occupies (15-23, 45-53)
# Move P0 down, but it'll get blocked by enemy at y=45-9=36
# P0 at (15,24), width 3. Enemy at (15,45), width 9. Same x range.
# Moving DOWN: P0 bottom edge y+3=27. Enemy top at 45. Distance: 45-27=18 → 6 moves
# But at some point P0 will hit the enemy.

# Move P0 down
pos_trace = [(g.ascpmvdpwj.x, g.ascpmvdpwj.y)]
for i in range(10):
    old = (g.ascpmvdpwj.x, g.ascpmvdpwj.y)
    g.perform_action(D)
    new = (g.ascpmvdpwj.x, g.ascpmvdpwj.y)
    pos_trace.append(new)
    if new == old:
        break
print(f"  P0 down trace: {pos_trace}")

# Now move P0 LEFT, then RIGHT to push enemy
print(f"  State: {state(g)}")
# Move left a lot
for i in range(5):
    g.perform_action(L)
print(f"  After 5L: {state(g)}")

# Now move DOWN more
for i in range(10):
    old = (g.ascpmvdpwj.x, g.ascpmvdpwj.y)
    g.perform_action(D)
    new = (g.ascpmvdpwj.x, g.ascpmvdpwj.y)
    if new != old:
        pass
    else:
        break
print(f"  After more D: {state(g)}")

# Now push RIGHT into enemy
print(f"\nNow pushing RIGHT toward enemy:")
for i in range(15):
    old_p0 = (g.ascpmvdpwj.x, g.ascpmvdpwj.y)
    en = g.current_level.get_sprites_by_tag('nnckfubbhi')
    old_e = (en[0].x, en[0].y) if en else None
    g.perform_action(R)
    new_p0 = (g.ascpmvdpwj.x, g.ascpmvdpwj.y)
    en = g.current_level.get_sprites_by_tag('nnckfubbhi')
    new_e = (en[0].x, en[0].y) if en else None
    if old_e != new_e:
        print(f"  R[{i}]: P0 {old_p0}→{new_p0}, ENEMY PUSHED {old_e}→{new_e}")
    elif new_p0 != old_p0:
        print(f"  R[{i}]: P0 {old_p0}→{new_p0}, E unchanged {old_e}")
    else:
        print(f"  R[{i}]: blocked, P0={new_p0}")
        break
print(f"  Final: {state(g)}")

# Test push LEFT into enemy
print(f"\nTest: Push enemy LEFT")
g = mod.Ka59()
g.set_level(3)
# Move P0 right to be to the RIGHT of the enemy
# P0 at (15,24), enemy at (15,45). Need P0 at right of enemy at same row.
# Enemy occupies x=15-23. P0 needs to be at x>=24.
# Move P0 right then down to enemy's row.
for _ in range(3):
    g.perform_action(R)  # P0: 15→18→21→24
print(f"  P0 right: ({g.ascpmvdpwj.x},{g.ascpmvdpwj.y})")
for _ in range(7):
    g.perform_action(D)  # Move down
print(f"  P0 down: ({g.ascpmvdpwj.x},{g.ascpmvdpwj.y})")
# Now push LEFT
for i in range(5):
    old_p0 = (g.ascpmvdpwj.x, g.ascpmvdpwj.y)
    en = g.current_level.get_sprites_by_tag('nnckfubbhi')
    old_e = (en[0].x, en[0].y) if en else None
    g.perform_action(L)
    new_p0 = (g.ascpmvdpwj.x, g.ascpmvdpwj.y)
    en = g.current_level.get_sprites_by_tag('nnckfubbhi')
    new_e = (en[0].x, en[0].y) if en else None
    if old_e != new_e:
        print(f"  L[{i}]: ENEMY PUSHED {old_e}→{new_e}, P0 {old_p0}→{new_p0}")
    elif new_p0 != old_p0:
        print(f"  L[{i}]: P0 {old_p0}→{new_p0}")
print(f"  Final: {state(g)}")

# Test UP push on enemy
print(f"\nTest: Can we push enemy UP?")
g = mod.Ka59()
g.set_level(3)
# Position P0 below enemy: enemy at (15,45), P0 needs to be at (15,54) or below
# P0 at (15,24). Move right to clear enemy, then down past enemy, then left, then UP
# Move right to x=27 (past enemy's right edge at 24)
for _ in range(4):
    g.perform_action(R)  # 15→18→21→24→27
# Move down past enemy
for _ in range(15):
    g.perform_action(D)
print(f"  P0 past enemy: ({g.ascpmvdpwj.x},{g.ascpmvdpwj.y})")
# Move left to enemy's x
for _ in range(4):
    g.perform_action(L)  # 27→24→21→18→15
print(f"  P0 aligned: ({g.ascpmvdpwj.x},{g.ascpmvdpwj.y})")
# Now move UP into enemy
for i in range(5):
    old_p0 = (g.ascpmvdpwj.x, g.ascpmvdpwj.y)
    en = g.current_level.get_sprites_by_tag('nnckfubbhi')
    old_e = (en[0].x, en[0].y) if en else None
    g.perform_action(U)
    new_p0 = (g.ascpmvdpwj.x, g.ascpmvdpwj.y)
    en = g.current_level.get_sprites_by_tag('nnckfubbhi')
    new_e = (en[0].x, en[0].y) if en else None
    if old_e != new_e:
        print(f"  U[{i}]: ENEMY PUSHED UP {old_e}→{new_e}")
    elif new_p0 != old_p0:
        print(f"  U[{i}]: P0 moved {old_p0}→{new_p0}, E={old_e}")
    else:
        print(f"  U[{i}]: blocked P0={new_p0}, E={old_e}")
print(f"  Final: {state(g)}")
