"""KA59 L2 — systematic route planning with push mechanics.

Board: 4 quadrants separated by f-type dividers:
  - Vertical divider blocks at x=30 (from right side)
  - Horizontal divider blocks at y=? (TBD)
  - Push launches piece 15 units across divider

Pieces & targets:
  P0 cisjjwiopp (33,42) 3x6 → (9,9)
  P1 peoafdrnua (42,45) 6x6 → (6,42)
  P2 pomlugyufe (36,54) 3x3 → (51,51)
  P3 sfcitxooao (39,33) 6x3 → (54,39)
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


def do(g, action_str, label=""):
    """Execute one action."""
    g.perform_action(AM[action_str])
    if label:
        print(f"  {label}: {state(g)}")
    return 1


def select(g, name, label=""):
    """Click to select a piece."""
    ca = click_name(g, name)
    if ca:
        g.perform_action(ca)
        if label:
            print(f"  {label}: {state(g)}")
        return 1
    return 0


def move_to(g, target_x, target_y, max_steps=100, label=""):
    """Move selected piece toward target, return steps taken."""
    sel = g.ascpmvdpwj
    count = 0
    for _ in range(max_steps):
        if sel.x == target_x and sel.y == target_y:
            break
        dx = target_x - sel.x
        dy = target_y - sel.y
        old_x, old_y = sel.x, sel.y

        # Try the most needed direction
        moved = False
        for d in (['L'] if dx < 0 else ['R'] if dx > 0 else []) + \
                 (['U'] if dy < 0 else ['D'] if dy > 0 else []):
            g_backup = copy.deepcopy(g)
            g.perform_action(AM[d])
            count += 1
            if sel.x != old_x or sel.y != old_y:
                moved = True
                break
            # Restore
            g.__dict__.update(g_backup.__dict__)
            count -= 1

        if not moved:
            print(f"  {label} STUCK at ({sel.x},{sel.y}), target ({target_x},{target_y})")
            return count
    if label:
        print(f"  {label} → ({sel.x},{sel.y}) in {count} steps")
    return count


def probe_boundaries(level_idx):
    """Find exact boundary positions by probing in all directions from various points."""
    g = mod.Ka59()
    g.set_level(level_idx)

    # Test boundaries from each piece's starting position
    pieces = sorted(g.current_level.get_sprites_by_tag('xlfuqjygey'), key=lambda s: s.name)

    for pi, p in enumerate(pieces):
        print(f"\nP{pi} {p.name} ({p.x},{p.y}) {p.width}x{p.height}:")

        # Find LEFT boundary
        g2 = copy.deepcopy(g)
        if g2.ascpmvdpwj.name != p.name:
            ca = click_name(g2, p.name)
            if ca:
                g2.perform_action(ca)
        for i in range(30):
            old = g2.ascpmvdpwj.x
            g2.perform_action(L)
            if g2.ascpmvdpwj.x == old:
                print(f"  LEFT blocked at x={old} (after {i} moves from {p.x})")
                break

        # Find RIGHT boundary
        g2 = copy.deepcopy(g)
        if g2.ascpmvdpwj.name != p.name:
            ca = click_name(g2, p.name)
            if ca:
                g2.perform_action(ca)
        for i in range(30):
            old = g2.ascpmvdpwj.x
            g2.perform_action(R)
            if g2.ascpmvdpwj.x == old:
                print(f"  RIGHT blocked at x={old} (after {i} moves from {p.x})")
                break

        # Find UP boundary
        g2 = copy.deepcopy(g)
        if g2.ascpmvdpwj.name != p.name:
            ca = click_name(g2, p.name)
            if ca:
                g2.perform_action(ca)
        for i in range(30):
            old = g2.ascpmvdpwj.y
            g2.perform_action(U)
            if g2.ascpmvdpwj.y == old:
                print(f"  UP blocked at y={old} (after {i} moves from {p.y})")
                break

        # Find DOWN boundary
        g2 = copy.deepcopy(g)
        if g2.ascpmvdpwj.name != p.name:
            ca = click_name(g2, p.name)
            if ca:
                g2.perform_action(ca)
        for i in range(30):
            old = g2.ascpmvdpwj.y
            g2.perform_action(D)
            if g2.ascpmvdpwj.y == old:
                print(f"  DOWN blocked at y={old} (after {i} moves from {p.y})")
                break

    # Also probe from pushed position
    print("\n--- Probing from pushed position (P0 at left side) ---")
    g = mod.Ka59()
    g.set_level(level_idx)
    # Move P0 up to align with P3, then have P3 push
    for _ in range(3):
        g.perform_action(U)  # P0: 33,42 → 33,39 → 33,36 → 33,33
    # Switch to P3
    ca = click_name(g, 'sfcitxooao')
    g.perform_action(ca)
    # Push P3 left twice (second push launches P0)
    g.perform_action(L)  # P3: 39→36
    g.perform_action(L)  # P0 pushed: 33→18
    # Switch back to P0
    ca = click_name(g, 'cisjjwiopp')
    g.perform_action(ca)
    print(f"P0 at ({g.ascpmvdpwj.x},{g.ascpmvdpwj.y}) after push")

    # Probe all directions
    for d_name, d_act in [('LEFT', L), ('RIGHT', R), ('UP', U), ('DOWN', D)]:
        g2 = copy.deepcopy(g)
        positions = [(g2.ascpmvdpwj.x, g2.ascpmvdpwj.y)]
        for i in range(20):
            old = (g2.ascpmvdpwj.x, g2.ascpmvdpwj.y)
            g2.perform_action(d_act)
            new = (g2.ascpmvdpwj.x, g2.ascpmvdpwj.y)
            positions.append(new)
            if new == old:
                print(f"  {d_name} blocked at {old} after {i} moves")
                break
        print(f"  {d_name} trace: {positions[:10]}...")


if __name__ == '__main__':
    probe_boundaries(1)
