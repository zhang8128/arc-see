"""KA59 interactive explorer — try actions and observe state changes."""
import sys
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


def click(g, sprite_name):
    """Click on a sprite by name."""
    for tag in ['xlfuqjygey', 'nnckfubbhi']:
        for s in g.current_level.get_sprites_by_tag(tag):
            if s.name == sprite_name:
                gx = s.x + s.width // 2
                gy = s.y + s.height // 2
                sc, ox, oy = g.camera._calculate_scale_and_offset()
                dx = int(gx * sc + ox)
                dy = int(gy * sc + oy)
                return ActionInput(id=GameAction.ACTION6, data={'x': dx, 'y': dy})
    return None


def click_piece(g, piece_idx):
    """Click on the idx-th piece (sorted by name)."""
    pieces = sorted(g.current_level.get_sprites_by_tag('xlfuqjygey'), key=lambda s: s.name)
    if piece_idx < len(pieces):
        return click(g, pieces[piece_idx].name)
    return None


def state_str(g):
    """Compact state string."""
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


def try_sequence(level_idx, seq_str, verbose=True):
    """Try a sequence of actions on a fresh level.

    seq_str format: "RRRLDLLLC0UR" where C0 = click piece 0, C1 = click piece 1, etc.
    Returns (game, action_count, won).
    """
    g = mod.Ka59()
    g.set_level(level_idx)

    if verbose:
        print(f"START: {state_str(g)}")

    actions = []
    i = 0
    count = 0
    while i < len(seq_str):
        ch = seq_str[i]
        if ch in AM:
            g.perform_action(AM[ch])
            count += 1
            actions.append(ch)
        elif ch == 'C':
            # Parse the piece index
            i += 1
            idx = int(seq_str[i])
            ca = click_piece(g, idx)
            if ca:
                g.perform_action(ca)
                count += 1
                actions.append(f'C{idx}')
        elif ch == '*':
            # Repeat the next character N times
            i += 1
            n = int(seq_str[i])
            i += 1
            ch2 = seq_str[i]
            for _ in range(n):
                if ch2 in AM:
                    g.perform_action(AM[ch2])
                    count += 1
                    actions.append(ch2)
        i += 1

        won = g._current_level_index > level_idx
        if won:
            if verbose:
                print(f"WON at action {count}! {state_str(g)}")
            return g, count, True

    if verbose:
        print(f"END ({count} actions): {state_str(g)}")
        print(f"Actions: {' '.join(actions)}")

    return g, count, False


def route_piece(g, level_idx, target_x, target_y, verbose=True):
    """Greedily move the selected piece toward a target position."""
    sel = g.ascpmvdpwj
    if sel is None:
        print("No piece selected!")
        return 0, False

    count = 0
    max_moves = 200

    while count < max_moves:
        dx = target_x - sel.x
        dy = target_y - sel.y

        if dx == 0 and dy == 0:
            if verbose:
                print(f"  Piece at target ({target_x},{target_y}) after {count} moves")
            won = g._current_level_index > level_idx
            return count, won

        # Try to move toward target
        old_x, old_y = sel.x, sel.y
        moved = False

        # Try the most needed direction first
        if abs(dx) >= abs(dy):
            # Prefer horizontal
            if dx > 0:
                tries = ['R', 'D' if dy > 0 else 'U', 'U' if dy > 0 else 'D', 'L']
            else:
                tries = ['L', 'D' if dy > 0 else 'U', 'U' if dy > 0 else 'D', 'R']
        else:
            # Prefer vertical
            if dy > 0:
                tries = ['D', 'R' if dx > 0 else 'L', 'L' if dx > 0 else 'R', 'U']
            else:
                tries = ['U', 'R' if dx > 0 else 'L', 'L' if dx > 0 else 'R', 'D']

        for d in tries:
            g_backup = copy.deepcopy(g)
            g.perform_action(AM[d])
            count += 1

            if sel.x != old_x or sel.y != old_y:
                # Moved!
                if verbose and count % 10 == 0:
                    print(f"  [{count}] {state_str(g)}")
                moved = True
                break
            else:
                # Didn't move, try next direction
                # Restore state
                g.__dict__.update(g_backup.__dict__)
                count -= 1  # Don't count blocked moves

        if not moved:
            if verbose:
                print(f"  STUCK at ({sel.x},{sel.y}) after {count} moves, target ({target_x},{target_y})")
            return count, False

        won = g._current_level_index > level_idx
        if won:
            if verbose:
                print(f"  WON at ({sel.x},{sel.y}) after {count} moves!")
            return count, True

    if verbose:
        print(f"  Max moves reached at ({sel.x},{sel.y})")
    return count, False


def solve_l2_greedy():
    """Try to solve L2 by routing each piece to its target frame."""
    g = mod.Ka59()
    g.set_level(1)

    # Piece-to-frame matching by size:
    # cisjjwiopp (3x6) → sxasgylpxm (5x8) → target (9,9)
    # peoafdrnua (6x6) → pyqqacvnjx (8x8) → target (6,42)
    # pomlugyufe (3x3) → wewoeeghkd (5x5) → target (51,51)
    # sfcitxooao (6x3) → xozzfidseo (8x5) → target (54,39)

    pieces = sorted(g.current_level.get_sprites_by_tag('xlfuqjygey'), key=lambda s: s.name)
    print("Pieces:")
    for i, s in enumerate(pieces):
        sel_mark = ' [SEL]' if s is g.ascpmvdpwj else ''
        print(f"  {i}: {s.name} ({s.x},{s.y}) {s.width}x{s.height}{sel_mark}")

    # Route order: farthest from others first, to avoid collisions
    # P3 (pomlugyufe 3x3) → (51,51) — bottom-right, far away
    # P4 (sfcitxooao 6x3) → (54,39) — bottom-right
    # P1 (cisjjwiopp 3x6) → (9,9) — top-left
    # P2 (peoafdrnua 6x6) → (6,42) — left middle

    targets = {
        'pomlugyufe': (51, 51),
        'sfcitxooao': (54, 39),
        'cisjjwiopp': (9, 9),
        'peoafdrnua': (6, 42),
    }

    order = ['pomlugyufe', 'sfcitxooao', 'cisjjwiopp', 'peoafdrnua']

    total = 0
    for name in order:
        tx, ty = targets[name]
        # Find piece index
        pieces = sorted(g.current_level.get_sprites_by_tag('xlfuqjygey'), key=lambda s: s.name)
        idx = None
        for i, s in enumerate(pieces):
            if s.name == name:
                idx = i
                break

        if idx is None:
            print(f"  Piece {name} not found!")
            continue

        # Select if not already selected
        if g.ascpmvdpwj is None or g.ascpmvdpwj.name != name:
            ca = click(g, name)
            if ca:
                g.perform_action(ca)
                total += 1
                print(f"\nSelected {name} ({g.ascpmvdpwj.x},{g.ascpmvdpwj.y}) → target ({tx},{ty})")

        count, won = route_piece(g, 1, tx, ty)
        total += count

        if won:
            print(f"\n=== L2 SOLVED! Total: {total} actions ===")
            return total, True

        print(f"  Routed {name}: {count} moves, total={total}")
        print(f"  State: {state_str(g)}")

    print(f"\nFinal state: {state_str(g)}")
    print(f"Total actions: {total}")
    return total, False


def test_push_mechanics(level_idx):
    """Test what happens when pieces collide with each other and with dividers."""
    g = mod.Ka59()
    g.set_level(level_idx)

    print(f"Initial: {state_str(g)}")

    # Try each direction and see what happens
    for d_name, d_act in [('U', U), ('D', D), ('L', L), ('R', R)]:
        g2 = copy.deepcopy(g)
        sel = g2.ascpmvdpwj
        old_x, old_y = sel.x, sel.y
        g2.perform_action(d_act)
        new_x, new_y = sel.x, sel.y
        print(f"  {d_name}: ({old_x},{old_y}) → ({new_x},{new_y}) delta=({new_x-old_x},{new_y-old_y})")
        print(f"    State: {state_str(g2)}")


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'l2'

    if cmd == 'l2':
        solve_l2_greedy()
    elif cmd == 'push':
        level = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        test_push_mechanics(level)
    elif cmd == 'try':
        level = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        seq = sys.argv[3] if len(sys.argv) > 3 else ''
        try_sequence(level, seq)
    elif cmd == 'state':
        level = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        g = mod.Ka59()
        g.set_level(level)
        print(state_str(g))
