#!/usr/bin/env python3
"""
SK48 L2 Solver v3 — Correct simultaneous-move mechanics.

Key insight: ALL sprites in opqqwmrfcn move simultaneously by (dx,dy).
Target pushes use ORIGINAL positions. Once in opqqwmrfcn, a sprite isn't
re-pushed — it just returns True immediately.
"""
from collections import deque

CELL = 6
RACK_X = 5
RAMP_YS = {8, 14, 20, 26, 32, 38}
RAMP_HEIGHT = 8
FRAME_X_MIN = 11
FRAME_X_MAX_BOUND = 53
FRAME_Y_MIN = 6
FRAME_Y_MAX_BOUND = 48
INITIAL_RACK_Y = 42
INITIAL_NUM_SEGMENTS = 2
INITIAL_TARGETS = ((29, 24, 14), (35, 24, 9), (41, 24, 12), (47, 24, 8))
REFERENCE = (8, 12, 9, 14)
MAX_SEGMENTS = 12


def in_bounds(x, y):
    return FRAME_X_MIN <= x and x + 6 <= FRAME_X_MAX_BOUND and \
           FRAME_Y_MIN <= y and y + 6 <= FRAME_Y_MAX_BOUND


def has_ramp(rack_y, direction):
    check_y = rack_y + 2 + direction * 3
    for ry in RAMP_YS:
        if ry <= check_y < ry + RAMP_HEIGHT:
            return True
    return False


def target_at(targets, x, y):
    for i, (tx, ty, tc) in enumerate(targets):
        if tx == x and ty == y:
            return i
    return -1


def try_push_chain(targets, idx, dx, dy, to_move):
    """Try to add target idx and its blocking chain to to_move.
    Uses ORIGINAL positions only. Returns True if chain succeeds."""
    if idx in to_move:
        return True

    tx, ty, tc = targets[idx]
    new_x, new_y = tx + dx, ty + dy

    if not in_bounds(new_x, new_y):
        return False

    blocking = target_at(targets, new_x, new_y)
    if blocking >= 0:
        if not try_push_chain(targets, blocking, dx, dy, to_move):
            return False

    to_move.add(idx)
    return True


def do_move(targets, rack_y, num_segments, dx, dy, perpendicular):
    """Process a move. Returns new targets or None if blocked (perpendicular case).

    All sprites move simultaneously by (dx, dy). Build to_move set from
    original positions, then apply all at once.
    """
    to_move = set()

    for i in range(num_segments):
        seg_x = RACK_X + CELL * i
        for cx, cy in [(seg_x, rack_y), (seg_x + dx, rack_y + dy)]:
            tidx = target_at(targets, cx, cy)
            if tidx >= 0 and tidx not in to_move:
                ok = try_push_chain(targets, tidx, dx, dy, to_move)
                if not ok and perpendicular:
                    return None

    new_targets = list(targets)
    for idx in to_move:
        tx, ty, tc = targets[idx]
        new_targets[idx] = (tx + dx, ty + dy, tc)
    return tuple(new_targets)


def check_win(rack_y, num_segments, targets):
    found = []
    for i in range(num_segments):
        tidx = target_at(targets, RACK_X + CELL * i, rack_y)
        if tidx >= 0:
            found.append(targets[tidx][2])
    return len(found) == len(REFERENCE) and tuple(found) == REFERENCE


def get_successors(rack_y, num_segments, targets):
    succs = []

    # RIGHT
    if num_segments < MAX_SEGMENTS:
        rx = RACK_X + CELL * (num_segments - 1) + CELL
        if in_bounds(rx, rack_y) or not in_bounds(RACK_X + CELL * (num_segments - 1), rack_y):
            # Rightmost dest in bounds, OR rightmost already out of bounds
            new_t = do_move(targets, rack_y, num_segments, CELL, 0, False)
            if new_t is not None:
                succs.append((rack_y, num_segments + 1, new_t, 'R'))

    # LEFT
    if num_segments > 1:
        # Remaining segments shift left
        new_t = do_move(targets, rack_y, num_segments, -CELL, 0, False)
        if new_t is not None:
            succs.append((rack_y, num_segments - 1, new_t, 'L'))

    # UP
    if has_ramp(rack_y, -1):
        new_y = rack_y - CELL
        if new_y >= FRAME_Y_MIN:
            # Check each segment can cascade (boundary, allowing already-outside)
            can = True
            for i in range(num_segments):
                sx = RACK_X + CELL * i
                if not in_bounds(sx, new_y) and in_bounds(sx, rack_y):
                    can = False
                    break
            if can:
                new_t = do_move(targets, rack_y, num_segments, 0, -CELL, True)
                if new_t is not None:
                    succs.append((new_y, num_segments, new_t, 'U'))

    # DOWN
    if has_ramp(rack_y, +1):
        new_y = rack_y + CELL
        if new_y + 6 <= FRAME_Y_MAX_BOUND:
            can = True
            for i in range(num_segments):
                sx = RACK_X + CELL * i
                if not in_bounds(sx, new_y) and in_bounds(sx, rack_y):
                    can = False
                    break
            if can:
                new_t = do_move(targets, rack_y, num_segments, 0, CELL, True)
                if new_t is not None:
                    succs.append((new_y, num_segments, new_t, 'D'))

    return succs


def solve():
    initial = (INITIAL_RACK_Y, INITIAL_NUM_SEGMENTS, INITIAL_TARGETS)
    queue = deque([(initial, [])])
    visited = {initial}
    max_depth = 35
    iters = 0

    while queue:
        (ry, ns, t), path = queue.popleft()
        if len(path) >= max_depth:
            continue
        iters += 1
        if iters % 100000 == 0:
            print(f"  i={iters} d={len(path)} q={len(queue)} v={len(visited)}")

        for nry, nns, nt, a in get_successors(ry, ns, t):
            st = (nry, nns, nt)
            if st in visited:
                continue
            visited.add(st)
            np_ = path + [a]
            if check_win(nry, nns, nt):
                print(f"\n*** SOLUTION: {''.join(np_)} ({len(np_)} actions) ***")
                print(f"Iterations: {iters}, States: {len(visited)}")
                am = {'U':'ACTION1','D':'ACTION2','L':'ACTION3','R':'ACTION4'}
                print(f"Game: {[am[x] for x in np_]}")
                return np_
            queue.append((st, np_))

    print(f"No solution (depth {max_depth}, iters {iters}, states {len(visited)})")
    return None


if __name__ == "__main__":
    # Validate
    print("Validating...")
    import sys
    sys.path.insert(0, 'environment_files/sk48/41055498')
    from sk48 import Sk48
    from arcengine import GameAction
    from arcengine.enums import ActionInput

    game = Sk48()
    game._current_level_index = 1
    game.on_set_level(game._levels[1])
    am = {'U': ActionInput(id=GameAction.ACTION1), 'D': ActionInput(id=GameAction.ACTION2),
          'L': ActionInput(id=GameAction.ACTION3), 'R': ActionInput(id=GameAction.ACTION4)}

    # Test sequence and compare
    test_seq = 'RRUUURRURLDDRURLL'
    model_state = (42, 2, INITIAL_TARGETS)
    for i, a in enumerate(test_seq):
        game.perform_action(am[a])
        for s in get_successors(*model_state):
            if s[3] == a:
                model_state = (s[0], s[1], s[2])
                break
        rack = game.vzvypfsnt
        et = tuple(sorted((t.x, t.y, int(t.pixels[1,1])) for t in game.vbelzuaian if t.y < 53))
        mt = tuple(sorted(model_state[2]))
        if mt != et or model_state[0] != rack.y:
            print(f'DIVERGE step {i+1} ({a}): engine={et} model={mt}')
            break
    else:
        print(f'All {len(test_seq)} steps match!')

    print("\nSolving...")
    solve()
