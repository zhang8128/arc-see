"""Verify KA59 L2 solution — track exact win moment."""
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
NAMES = {0: 'cisjjwiopp', 1: 'peoafdrnua', 2: 'pomlugyufe', 3: 'sfcitxooao'}


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


def state(g, level_idx):
    try:
        pieces = sorted(g.current_level.get_sprites_by_tag('xlfuqjygey'), key=lambda s: s.name)
        sel = g.ascpmvdpwj
        return ' '.join(f"P{i}{'*' if s is sel else ''}({s.x},{s.y})" for i, s in enumerate(pieces))
    except:
        return "ERR"


def act(g, action, level=1):
    g.perform_action(action)
    won = g._current_level_index > level
    return won


actions = []

g = mod.Ka59()
g.set_level(1)
level = 1
total = 0

def do(action, label=""):
    global total
    total += 1
    actions.append(action)
    won = act(g, action, level)
    if won:
        print(f"  [{total}] {label}: *** WON *** {state(g, level)}")
    return won


def sel(idx):
    ca = click_name(g, NAMES[idx])
    if ca:
        return do(ca, f"SEL P{idx}")
    return False


def m(d, n=1, label=""):
    for i in range(n):
        won = do(AM[d], f"{d} ({label})" if label else d)
        if won:
            return True
    return False


# Execute the solution step by step with win checking
print(f"START: {state(g, 1)}")

# Phase 1: P0 left to divider
m('L', 1, "P0→divider")

# Phase 2: P1 pushes P0 left
sel(1)
m('U', 1, "P1 up")
if not m('L', 4, "P1 push P0"):
    print(f"  After push: {state(g, 1)}")

# Phase 3: P0 up to horizontal divider
sel(0)
m('U', 4, "P0 up")

# Phase 4: P1 left to divider
sel(1)
m('L', 1, "P1→divider")

# Phase 5: P3 pushes P1 left
sel(3)
m('D', 3, "P3 down")
if not m('L', 2, "P3 push P1"):
    print(f"  After push: {state(g, 1)}")

# Phase 6: P1 up to push position
sel(1)
m('U', 2, "P1 up to push pos")  # P1(15,42) → up → (15,33) or wherever

# Phase 7: P1 pushes P0 up
# Check current positions
p0 = p1 = None
for s in g.current_level.get_sprites_by_tag('xlfuqjygey'):
    if s.name == NAMES[0]:
        p0 = (s.x, s.y)
    elif s.name == NAMES[1]:
        p1 = (s.x, s.y)
print(f"  Before UP push: P0={p0}, P1={p1}")

# Move P1 UP until it pushes P0
while True:
    old_p0 = None
    for s in g.current_level.get_sprites_by_tag('xlfuqjygey'):
        if s.name == NAMES[0]:
            old_p0 = (s.x, s.y)

    won = m('U', 1, "P1→push P0 up")
    if won:
        break

    new_p0 = None
    for s in g.current_level.get_sprites_by_tag('xlfuqjygey'):
        if s.name == NAMES[0]:
            new_p0 = (s.x, s.y)

    if new_p0 != old_p0:
        print(f"  P0 pushed! {old_p0}→{new_p0}")
        break

    # Check if stuck
    for s in g.current_level.get_sprites_by_tag('xlfuqjygey'):
        if s.name == NAMES[1]:
            cur_p1 = (s.x, s.y)
    if cur_p1 == p1:
        print(f"  P1 stuck at {cur_p1}")
        break
    p1 = cur_p1

print(f"  State: {state(g, 1)}")

# Phase 8: Route P0 to (9,9)
sel(0)
p0 = g.ascpmvdpwj
print(f"  P0 at ({p0.x},{p0.y}), routing to (9,9)")
moves_l = (p0.x - 9) // 3
moves_u = (p0.y - 9) // 3
m('L', moves_l, "P0 left")
m('U', moves_u, "P0 up")
print(f"  P0 at ({g.ascpmvdpwj.x},{g.ascpmvdpwj.y})")

# Phase 9: Route P1 to (6,42)
sel(1)
p1 = g.ascpmvdpwj
print(f"  P1 at ({p1.x},{p1.y}), routing to (6,42)")
moves_l = (p1.x - 6) // 3
m('L', moves_l, "P1 left")
m('D', (42 - g.ascpmvdpwj.y) // 3, "P1 down")
print(f"  P1 at ({g.ascpmvdpwj.x},{g.ascpmvdpwj.y})")

# Phase 10: Route P2 to (51,51) — right side
sel(2)
p2 = g.ascpmvdpwj
print(f"  P2 at ({p2.x},{p2.y}), routing to (51,51)")
if p2.x < 51:
    m('R', (51 - p2.x) // 3, "P2 right")
if p2.y > 51:
    m('U', (g.ascpmvdpwj.y - 51) // 3, "P2 up")
elif g.ascpmvdpwj.y < 51:
    m('D', (51 - g.ascpmvdpwj.y) // 3, "P2 down")
print(f"  P2 at ({g.ascpmvdpwj.x},{g.ascpmvdpwj.y})")

# Phase 11: Route P3 to (54,39) — right side
won = g._current_level_index > 1
if not won:
    sel(3)
    p3 = g.ascpmvdpwj
    print(f"  P3 at ({p3.x},{p3.y}), routing to (54,39)")
    if p3.x < 54:
        m('R', (54 - p3.x) // 3, "P3 right")
    elif p3.x > 54:
        m('L', (p3.x - 54) // 3, "P3 left")
    if g.ascpmvdpwj.y > 39:
        m('U', (g.ascpmvdpwj.y - 39) // 3, "P3 up")
    elif g.ascpmvdpwj.y < 39:
        m('D', (39 - g.ascpmvdpwj.y) // 3, "P3 down")
    print(f"  P3 at ({g.ascpmvdpwj.x},{g.ascpmvdpwj.y})")

won = g._current_level_index > 1
print(f"\n{'='*50}")
print(f"Total: {total} actions (baseline 175)")
print(f"Level index: {g._current_level_index}")
print(f"WON: {won}")
