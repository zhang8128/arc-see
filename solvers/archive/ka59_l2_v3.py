"""KA59 L2 solver v3 — correct push chain without stranding pieces.

Strategy:
1. Route P2 (3x3) → (51,51) and P3 (6x3) → (54,39) FIRST (right side, no divider needed)
   WAIT — P3 is needed to push P1. Route P2 first, keep P3 as pusher.

Actually, revised plan:
1. P1 pushes P0 LEFT across vertical divider
2. P0 moves UP to horizontal divider boundary (y=30)
3. P3 pushes P1 LEFT across vertical divider
4. P1 moves UP to position below P0 on left side
5. P1 pushes P0 UP across horizontal divider
6. Route P0 to target (9,9)
7. Route P1 to target (6,42)
8. Route P2 to (51,51) — stays on right side
9. Route P3 to (54,39) — stays on right side
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

NAMES = {0: 'cisjjwiopp', 1: 'peoafdrnua', 2: 'pomlugyufe', 3: 'sfcitxooao'}
TARGETS = {0: (9, 9), 1: (6, 42), 2: (51, 51), 3: (54, 39)}


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


def sel(g, idx):
    ca = click_name(g, NAMES[idx])
    if ca:
        g.perform_action(ca)
        return 1
    return 0


def m(g, d, n=1):
    for _ in range(n):
        g.perform_action(AM[d])
    return n


def pos(g, idx):
    for s in g.current_level.get_sprites_by_tag('xlfuqjygey'):
        if s.name == NAMES[idx]:
            return (s.x, s.y)
    return None


def move_toward(g, tx, ty, max_steps=100):
    """Move selected piece toward target. Returns steps taken."""
    count = 0
    for _ in range(max_steps):
        p = g.ascpmvdpwj
        if p.x == tx and p.y == ty:
            return count
        dx, dy = tx - p.x, ty - p.y
        old_x, old_y = p.x, p.y
        if dx < 0:
            g.perform_action(L); count += 1
        elif dx > 0:
            g.perform_action(R); count += 1
        elif dy < 0:
            g.perform_action(U); count += 1
        elif dy > 0:
            g.perform_action(D); count += 1
        if p.x == old_x and p.y == old_y:
            print(f"  STUCK at ({p.x},{p.y}), target ({tx},{ty})")
            return count
    return count


def solve_l2():
    g = mod.Ka59()
    g.set_level(1)
    total = 0
    print(f"START: {state(g)}")
    # P0(33,42) P1(42,45) P2(36,54) P3(39,33)

    # === PHASE 1: Push P0 LEFT using P1 ===
    # Move P0 left to divider boundary
    total += sel(g, 0)     # Already selected
    total -= 1             # P0 is already selected at start
    total += m(g, 'L', 1)  # P0: 33→30
    print(f"1a. P0 at divider: {state(g)}, total={total}")

    # Move P1 to push position: P1(42,45) needs to be at same row as P0(30,42)
    total += sel(g, 1)
    total += m(g, 'U', 1)  # P1: (42,45)→(42,42)
    total += m(g, 'L', 4)  # P1: (42→39→36→33)→push P0 at 30! P0→left side
    print(f"1b. P1 pushed P0: {state(g)}, total={total}")
    print(f"    P0 at: {pos(g, 0)}, P1 at: {pos(g, 1)}")

    # === PHASE 2: P0 moves UP to horizontal divider boundary ===
    total += sel(g, 0)
    p0 = pos(g, 0)
    up_to_30 = (p0[1] - 30) // 3
    total += m(g, 'U', up_to_30)
    print(f"2. P0 at boundary: {state(g)}, total={total}")

    # === PHASE 3: Push P1 LEFT using P3 ===
    # First move P1 left to divider boundary
    total += sel(g, 1)
    p1 = pos(g, 1)
    left_to_30 = (p1[0] - 30) // 3
    total += m(g, 'L', left_to_30)
    print(f"3a. P1 at divider: {state(g)}, total={total}")

    # Move P3 to push position: align with P1's row, then push left
    total += sel(g, 3)
    p3 = pos(g, 3)
    p1 = pos(g, 1)
    # Move P3 to P1's row
    dy = p1[1] - p3[1]
    if dy > 0:
        total += m(g, 'D', dy // 3)
    elif dy < 0:
        total += m(g, 'U', (-dy) // 3)
    # Move P3 left until it pushes P1
    p3 = pos(g, 3)
    old_p1 = pos(g, 1)
    while True:
        total += m(g, 'L', 1)
        new_p1 = pos(g, 1)
        if new_p1 != old_p1:
            print(f"3b. P3 pushed P1: P1 {old_p1}→{new_p1}")
            break
        p3_new = pos(g, 3)
        if p3_new == p3:
            print(f"3b. P3 stuck at {p3}")
            break
        p3 = p3_new
        old_p1 = new_p1
    print(f"3c. After push: {state(g)}, total={total}")

    # === PHASE 4: Position P1 below P0 to push UP ===
    total += sel(g, 1)
    p0 = pos(g, 0)
    p1 = pos(g, 1)
    print(f"4a. P0 at {p0}, P1 at {p1}")

    # P1 needs to be at same x as P0 (or overlapping) and below P0
    # Move P1 to align x with P0
    dx = p0[0] - p1[0]
    if dx > 0:
        total += m(g, 'R', dx // 3)
    elif dx < 0:
        total += m(g, 'L', (-dx) // 3)

    p1 = pos(g, 1)
    print(f"4b. P1 x-aligned: {state(g)}")

    # Move P1 up to just below P0 (P0.y + P0.height = P0.y + 6)
    # P1 needs y such that P1's range overlaps with P0's range when P1 moves UP
    # P0 at (x,30) height 6: occupies y=30-35. P1 needs to be at y=33 (occupies 33-38 if 6x6)
    # When P1 at (x,33) moves UP → tries (x,30). Collides with P0 at y=30-35. Push!
    target_y = p0[1] + 3  # P1 should be 3 below P0
    dy = p1[1] - target_y
    if dy > 0:
        total += m(g, 'U', dy // 3)
    elif dy < 0:
        total += m(g, 'D', (-dy) // 3)

    p1 = pos(g, 1)
    print(f"4c. P1 positioned: {state(g)}")

    # Push P0 UP!
    old_p0 = pos(g, 0)
    total += m(g, 'U', 1)
    new_p0 = pos(g, 0)
    print(f"4d. UP PUSH: P0 {old_p0}→{new_p0}, {state(g)}, total={total}")

    # === PHASE 5: Route P0 to (9,9) ===
    total += sel(g, 0)
    total += move_toward(g, 9, 9)
    p0 = pos(g, 0)
    print(f"5. P0 routed: {p0}, total={total}")
    if p0 == (9, 9):
        print("   P0 TARGET REACHED!")

    # === PHASE 6: Route P1 to (6,42) ===
    total += sel(g, 1)
    total += move_toward(g, 6, 42)
    p1 = pos(g, 1)
    print(f"6. P1 routed: {p1}, total={total}")
    if p1 == (6, 42):
        print("   P1 TARGET REACHED!")

    # === PHASE 7: Route P2 to (51,51) ===
    total += sel(g, 2)
    total += move_toward(g, 51, 51)
    p2 = pos(g, 2)
    print(f"7. P2 routed: {p2}, total={total}")
    if p2 == (51, 51):
        print("   P2 TARGET REACHED!")

    # === PHASE 8: Route P3 to (54,39) ===
    total += sel(g, 3)
    total += move_toward(g, 54, 39)
    p3 = pos(g, 3)
    print(f"8. P3 routed: {p3}, total={total}")
    if p3 == (54, 39):
        print("   P3 TARGET REACHED!")

    won = g._current_level_index > 1
    print(f"\n{'='*40}")
    print(f"TOTAL: {total} actions (baseline 175)")
    print(f"WON: {won}")
    print(f"Final: {state(g)}")

    return g, total, won


g, total, won = solve_l2()
