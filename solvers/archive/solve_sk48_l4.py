#!/usr/bin/env python3
"""SK48 L4 Solver — Two vertical rack pairs need targets pushed to x=23 and x=35.

Horizontal rack (5,42) is standalone — just a tool.
Vertical rack (23,0) paired with ref (35,56) — needs [9,14] at x=23
Vertical rack (35,0) paired with ref (11,56) — needs [8,12] at x=35

Targets start at y=42: (11,9), (17,14), (23,8), (29,12)
Vertical segs at x=23: y=0,6,12,18 and x=35: y=0,6,12,18
These block horizontal pushes ONLY at their y positions (y<=18).
At y>=24, no vertical segments → horizontal pushes work freely.
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
INITIAL_NUM_SEGMENTS = 5  # x=5,11,17,23,29
INITIAL_TARGETS = ((11, 42, 9), (17, 42, 14), (23, 42, 8), (29, 42, 12))
MAX_SEGMENTS = 12

# Vertical segments block horizontal pushes at these positions
VERTICAL_SEGS = set()
for y in [0, 6, 12, 18]:
    VERTICAL_SEGS.add((23, y))
    VERTICAL_SEGS.add((35, y))


def check_win(rack_y, num_segments, targets):
    """WIN: vertical rack segments sitting on targets match reference.

    Rack (23,0) segments at y=0,6,12,18 → need vjfbwggsd matching [9,14]
    Rack (35,0) segments at y=0,6,12,18 → need vjfbwggsd matching [8,12]
    """
    # Build target lookup
    tmap = {(t[0], t[1]): t[2] for t in targets}

    # Check rack (23,0): segments at (23,0),(23,6),(23,12),(23,18)
    colors_23 = []
    for y in [0, 6, 12, 18]:
        if (23, y) in tmap:
            colors_23.append(tmap[(23, y)])
    ref_23 = (9, 14)  # reference order
    match_23 = len(colors_23) >= len(ref_23) and tuple(colors_23[:len(ref_23)]) == ref_23

    # Check rack (35,0): segments at (35,0),(35,6),(35,12),(35,18)
    colors_35 = []
    for y in [0, 6, 12, 18]:
        if (35, y) in tmap:
            colors_35.append(tmap[(35, y)])
    ref_35 = (8, 12)  # reference order
    match_35 = len(colors_35) >= len(ref_35) and tuple(colors_35[:len(ref_35)]) == ref_35

    return match_23 and match_35


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
    if idx in to_move:
        return True
    tx, ty, tc = targets[idx]
    new_x, new_y = tx + dx, ty + dy
    if not in_bounds(new_x, new_y):
        return False
    # Vertical segments block HORIZONTAL pushes at current pos OR destination
    if dx != 0 and ((tx, ty) in VERTICAL_SEGS or (new_x, new_y) in VERTICAL_SEGS):
        return False
    blocking = target_at(targets, new_x, new_y)
    if blocking >= 0:
        if not try_push_chain(targets, blocking, dx, dy, to_move):
            return False
    to_move.add(idx)
    return True


def do_move(targets, rack_y, num_segments, dx, dy, perpendicular):
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


def get_successors(rack_y, num_segments, targets):
    succs = []

    # RIGHT
    if num_segments < MAX_SEGMENTS:
        rx = RACK_X + CELL * (num_segments - 1) + CELL
        if in_bounds(rx, rack_y) or not in_bounds(RACK_X + CELL * (num_segments - 1), rack_y):
            new_t = do_move(targets, rack_y, num_segments, CELL, 0, False)
            if new_t is not None:
                succs.append((rack_y, num_segments + 1, new_t, 'R'))

    # LEFT
    if num_segments > 1:
        new_t = do_move(targets, rack_y, num_segments, -CELL, 0, False)
        if new_t is not None:
            succs.append((rack_y, num_segments - 1, new_t, 'L'))

    # UP
    if has_ramp(rack_y, -1):
        new_y = rack_y - CELL
        if new_y >= FRAME_Y_MIN:
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
    max_depth = 120  # baseline is 113
    iters = 0

    while queue:
        (ry, ns, t), path = queue.popleft()
        if len(path) >= max_depth:
            continue
        iters += 1
        if iters % 500000 == 0:
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
    print("SK48 L4 Solver")
    print(f"Targets: {INITIAL_TARGETS}")
    print(f"Vertical segs: {sorted(VERTICAL_SEGS)}")
    print(f"Need: [9,14] at x=23, [8,12] at x=35")
    print()

    # Quick check: is initial state a win?
    print(f"Initial win: {check_win(*((INITIAL_RACK_Y, INITIAL_NUM_SEGMENTS, INITIAL_TARGETS)))}")
    print()

    solve()
