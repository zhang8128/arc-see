"""KA59 L2 solver v2 — push chains across both dividers."""
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


def sel(g, name):
    ca = click_name(g, name)
    if ca:
        g.perform_action(ca)
        return 1
    return 0


def move(g, direction, count=1):
    for _ in range(count):
        g.perform_action(AM[direction])
    return count


def won(g, level=1):
    return g._current_level_index > level


# Strategy for L2:
# P0 cisjjwiopp (33,42) 3x6 → target (9,9)
# P1 peoafdrnua (42,45) 6x6 → target (6,42)
# P2 pomlugyufe (36,54) 3x3 → target (51,51)
# P3 sfcitxooao (39,33) 6x3 → target (54,39)

def attempt():
    g = mod.Ka59()
    g.set_level(1)
    total = 0
    print(f"START: {state(g)}")

    # Phase 1: Push P0 LEFT across vertical divider using P3
    # Move P0 up to P3's row y=33
    total += move(g, 'U', 3)  # P0: (33,42)→(33,33)
    print(f"P0 moved up: {state(g)}, total={total}")

    # Switch to P3, push P0 LEFT
    total += sel(g, 'sfcitxooao')
    total += move(g, 'L', 2)  # P3: (39,33)→(36,33), push P0: (33,33)→(18,33)
    print(f"P3 pushed P0 left: {state(g)}, total={total}")

    # Phase 2: Move P0 up to horizontal divider boundary (y=30)
    total += sel(g, 'cisjjwiopp')
    total += move(g, 'U', 1)  # P0: (18,33)→(18,30)
    print(f"P0 at divider: {state(g)}, total={total}")

    # Phase 3: Push P2 LEFT across vertical divider using P1
    # Move P1 down to P2's row y=54
    total += sel(g, 'peoafdrnua')
    total += move(g, 'D', 3)  # P1: (42,45)→(42,54)
    # Push P1 LEFT to push P2
    total += move(g, 'L', 2)  # First L: P1(42→39). Second L: P1 at 39 pushes P2 at 36 → P2 to left side
    print(f"P2 pushed left: {state(g)}, total={total}")

    # Phase 4: Position P2 directly below P0 and push P0 UP
    total += sel(g, 'pomlugyufe')
    # P2 should be at (18,54) or similar on left side
    p2 = g.ascpmvdpwj
    print(f"P2 at ({p2.x},{p2.y})")

    # Move P2 UP to y=33 (just below P0 at y=30)
    # P0 is 3x6, bottom at y=30+6=36. P2 is 3x3.
    # For UP push: P2 needs to be at y=33 (P2 top at 33, P0 bottom at 36... overlap at 33-35? P0 is y=30 to 35, P2 at y=33 is y=33-35. Overlap in y.
    # But P2 x must overlap with P0 x too. P0 at x=18 (width 3), P2 at x=18 (width 3). Same x = perfect.
    up_moves = (p2.y - 33) // 3
    total += move(g, 'U', up_moves)  # P2 up to y=33
    print(f"P2 positioned: {state(g)}, total={total}")

    # Now push UP — P2 at (18,33) pushes P0 at (18,30)
    old_p0 = None
    for s in g.current_level.get_sprites_by_tag('xlfuqjygey'):
        if s.name == 'cisjjwiopp':
            old_p0 = (s.x, s.y)
    total += move(g, 'U', 1)  # PUSH!
    for s in g.current_level.get_sprites_by_tag('xlfuqjygey'):
        if s.name == 'cisjjwiopp':
            new_p0 = (s.x, s.y)
    print(f"UP PUSH: P0 {old_p0} → {new_p0}, {state(g)}, total={total}")

    # Phase 5: Route P0 to target (9,9)
    total += sel(g, 'cisjjwiopp')
    p0 = g.ascpmvdpwj
    print(f"P0 at ({p0.x},{p0.y}), target (9,9)")

    # Probe: can P0 move freely to (9,9)?
    # Move left to x=9
    left_moves = (p0.x - 9) // 3
    total += move(g, 'L', left_moves)
    p0 = g.ascpmvdpwj
    print(f"P0 after left: ({p0.x},{p0.y})")

    # Move down to y=9 (if P0 is above y=9) or up
    if p0.y > 9:
        down_moves = (p0.y - 9) // 3
        total += move(g, 'U', down_moves)
    elif p0.y < 9:
        up_moves = (9 - p0.y) // 3
        total += move(g, 'D', up_moves)
    p0 = g.ascpmvdpwj
    print(f"P0 at ({p0.x},{p0.y}), target (9,9), total={total}")

    if p0.x == 9 and p0.y == 9:
        print("P0 REACHED TARGET!")

    # Phase 6: Route P1 to target (6,42)
    # P1 is on right side. Needs LEFT push across divider.
    # P3 is at (36,33). Use P3 to push P1.
    # First position P1 near divider
    total += sel(g, 'peoafdrnua')
    p1 = g.ascpmvdpwj
    print(f"\nP1 at ({p1.x},{p1.y}), target (6,42)")

    # Move P1 up to a row where P3 can push it left
    # P3 at (36,33). P1 needs to be at x>36 (P3's left edge is at 36, width 6).
    # P3 at x=36, P1 needs to be at x<36 and same y as P3.
    # Actually: P3 pushes P1 by moving INTO P1. So P3 needs to be to the RIGHT of P1.
    # P3 at (36,33), P1 at (39,54). P1 needs to be at same row as P3 (y=33) and left of P3 (x<36).
    # P1 is 6x6. At x=33, P1's right edge is 33+6=39. P3 at x=36 left edge is 36. P1 right edge at 39 > P3 left at 36. So P3 trying to move LEFT from 36 would collide with P1 at 33.
    # But wait, P1 at x=33 going LEFT hits divider at x=30. Then push: P1 from 30 → 15?

    # Move P1 up to y=33 (from current position)
    if p1.y > 33:
        total += move(g, 'U', (p1.y - 33) // 3)
    p1 = g.ascpmvdpwj
    print(f"P1 after up: ({p1.x},{p1.y})")

    # Move P1 left toward divider
    while p1.x > 33:
        total += move(g, 'L', 1)
        if g.ascpmvdpwj.x == p1.x:
            break
        p1 = g.ascpmvdpwj
    print(f"P1 near divider: ({p1.x},{p1.y})")

    # Now use P3 to push P1 left
    total += sel(g, 'sfcitxooao')
    p3 = g.ascpmvdpwj
    print(f"P3 at ({p3.x},{p3.y})")

    # Move P3 to right of P1 at same y
    if p3.y != p1.y:
        if p3.y > p1.y:
            total += move(g, 'U', (p3.y - p1.y) // 3)
        else:
            total += move(g, 'D', (p1.y - p3.y) // 3)

    # Move P3 left to push P1
    p3 = g.ascpmvdpwj
    print(f"P3 aligned: ({p3.x},{p3.y})")
    old_p1 = None
    for s in g.current_level.get_sprites_by_tag('xlfuqjygey'):
        if s.name == 'peoafdrnua':
            old_p1 = (s.x, s.y)

    while True:
        total += move(g, 'L', 1)
        for s in g.current_level.get_sprites_by_tag('xlfuqjygey'):
            if s.name == 'peoafdrnua':
                new_p1 = (s.x, s.y)
        if new_p1 != old_p1:
            print(f"P3 pushed P1: {old_p1} → {new_p1}")
            break
        old_p1 = new_p1
        if g.ascpmvdpwj.x <= 30:
            print("P3 stuck at divider without pushing P1")
            break

    print(f"State: {state(g)}, total={total}")

    # Now route P1 to (6,42)
    total += sel(g, 'peoafdrnua')
    p1 = g.ascpmvdpwj
    print(f"P1 at ({p1.x},{p1.y}), target (6,42)")

    # Move left to x=6
    if p1.x > 6:
        total += move(g, 'L', (p1.x - 6) // 3)
    p1 = g.ascpmvdpwj
    print(f"P1 after left: ({p1.x},{p1.y})")

    # Move down to y=42
    if p1.y < 42:
        total += move(g, 'D', (42 - p1.y) // 3)
    elif p1.y > 42:
        total += move(g, 'U', (p1.y - 42) // 3)
    p1 = g.ascpmvdpwj
    print(f"P1 after vert: ({p1.x},{p1.y})")

    if p1.x == 6 and p1.y == 42:
        print("P1 REACHED TARGET!")

    # Phase 7: Route P2 to target (51,51)
    # P2 is on left side now. Can it get back to right side?
    # From probing: RIGHT is blocked from left side. So P2 is stuck on left side.
    # P2 target is (51,51) which is on the right side. Problem!
    # We need to push P2 back RIGHT, or route P2 before pushing it left.

    # RETHINK: Don't push P2 left if its target is on the right side!
    print(f"\nState: {state(g)}, total={total}")
    print("NOTE: P2 target (51,51) is on right side but P2 is stuck on left side!")
    print("Need to rethink the approach.")

    return g, total, won(g)


attempt()
