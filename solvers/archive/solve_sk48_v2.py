#!/usr/bin/env python3
"""
SK48 L2 Solver v2 — Correct mechanics.

Key: When target push fails (boundary), segment OVERLAPS the target.
Targets stay put, segments move over them. They coexist.
"""
from collections import deque

CELL = 6
RACK_X = 5
RAMP_YS = {8, 14, 20, 26, 32, 38}
RAMP_HEIGHT = 8

# Frame boundary: sprite at (11,6), 7x7 tiles, each 6px
# Collision: x + 6 > 53 or x < 11, y + 6 > 48 or y < 6
FRAME_X_MIN = 11
FRAME_X_MAX_BOUND = 53  # x + width must be <= this
FRAME_Y_MIN = 6
FRAME_Y_MAX_BOUND = 48

INITIAL_RACK_Y = 42
INITIAL_NUM_SEGMENTS = 2
INITIAL_TARGETS = (
    (29, 24, 14), (35, 24, 9), (41, 24, 12), (47, 24, 8),
)
REFERENCE = (8, 12, 9, 14)
MAX_SEGMENTS = 12


def in_bounds(x, y, w=6, h=6):
    """Check if sprite fits within frame."""
    return x >= FRAME_X_MIN and x + w <= FRAME_X_MAX_BOUND and \
           y >= FRAME_Y_MIN and y + h <= FRAME_Y_MAX_BOUND


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


def push_target_chain(targets, idx, dx, dy):
    """Try to push target chain. Returns new targets if ALL can move, else None."""
    tx, ty, tc = targets[idx]
    new_x, new_y = tx + dx, ty + dy

    if not in_bounds(new_x, new_y):
        return None  # Target can't move outside bounds

    targets_list = list(targets)
    blocking = target_at(targets, new_x, new_y)
    if blocking >= 0:
        result = push_target_chain(tuple(targets_list), blocking, dx, dy)
        if result is None:
            return None
        targets_list = list(result)

    targets_list[idx] = (new_x, new_y, tc)
    return tuple(targets_list)


def try_push_targets(targets, rack_y, seg_x, dx, dy, perpendicular=False):
    """Try to push targets at seg position and destination.

    For PARALLEL moves (R/L): push failure → segment overlaps target (OK)
    For PERPENDICULAR moves (U/D): push failure → BLOCKS cascade (returns None)

    Game tracks already-pushed targets via opqqwmrfcn to avoid double-pushing.
    We track pushed target indices to match this behavior.
    """
    new_targets = list(targets)
    pushed = set()  # Track pushed target indices

    for check_x, check_y in [(seg_x, rack_y), (seg_x + dx, rack_y + dy)]:
        tidx = target_at(tuple(new_targets), check_x, check_y)
        if tidx >= 0 and tidx not in pushed:
            result = push_target_chain(tuple(new_targets), tidx, dx, dy)
            if result is not None:
                # Track all targets that moved in the chain
                old_targets = tuple(new_targets)
                new_targets = list(result)
                for j in range(len(new_targets)):
                    if new_targets[j] != old_targets[j]:
                        pushed.add(j)
            elif perpendicular:
                return None  # Cascade blocked!

    return tuple(new_targets)


def check_win(rack_y, num_segments, targets):
    """Check WIN condition.

    For each segment (left-to-right), find target at segment position.
    Collect target colors. Compare with REFERENCE.
    """
    found_colors = []
    for i in range(num_segments):
        seg_x = RACK_X + CELL * i
        tidx = target_at(targets, seg_x, rack_y)
        if tidx >= 0:
            found_colors.append(targets[tidx][2])

    return len(found_colors) == len(REFERENCE) and tuple(found_colors) == REFERENCE


def get_successors(rack_y, num_segments, targets):
    successors = []

    # RIGHT: push all segments right, add new at base
    if num_segments < MAX_SEGMENTS:
        rightmost_x = RACK_X + CELL * (num_segments - 1)
        new_rightmost_x = rightmost_x + CELL

        # Check if rightmost segment's destination is in bounds
        if in_bounds(new_rightmost_x, rack_y):
            new_targets = targets
            # Process each segment's target interactions (left to right, as game does)
            for i in range(num_segments):
                seg_x = RACK_X + CELL * i
                new_targets = try_push_targets(new_targets, rack_y, seg_x, CELL, 0)
            successors.append((rack_y, num_segments + 1, new_targets, 'R'))

    # LEFT: pop leftmost, shift remaining left
    if num_segments > 1:
        new_targets = targets
        # Remaining segments shift left
        for i in range(1, num_segments):
            seg_x = RACK_X + CELL * i
            new_targets = try_push_targets(new_targets, rack_y, seg_x, -CELL, 0)
        successors.append((rack_y, num_segments - 1, new_targets, 'L'))

    # UP
    if has_ramp(rack_y, -1):
        new_rack_y = rack_y - CELL
        if new_rack_y >= FRAME_Y_MIN:
            new_targets = targets
            can_cascade = True
            for i in range(num_segments):
                seg_x = RACK_X + CELL * i
                already_outside = not in_bounds(seg_x, rack_y)
                dest_ok = in_bounds(seg_x, new_rack_y) or already_outside
                if not dest_ok:
                    can_cascade = False
                    break
                result = try_push_targets(new_targets, rack_y, seg_x, 0, -CELL, perpendicular=True)
                if result is None:
                    can_cascade = False
                    break
                new_targets = result
            if can_cascade:
                successors.append((new_rack_y, num_segments, new_targets, 'U'))

    # DOWN
    if has_ramp(rack_y, +1):
        new_rack_y = rack_y + CELL
        if new_rack_y + CELL <= FRAME_Y_MAX_BOUND:
            new_targets = targets
            can_cascade = True
            for i in range(num_segments):
                seg_x = RACK_X + CELL * i
                already_outside = not in_bounds(seg_x, rack_y)
                dest_ok = in_bounds(seg_x, new_rack_y) or already_outside
                if not dest_ok:
                    can_cascade = False
                    break
                result = try_push_targets(new_targets, rack_y, seg_x, 0, CELL, perpendicular=True)
                if result is None:
                    can_cascade = False
                    break
                new_targets = result
            if can_cascade:
                successors.append((new_rack_y, num_segments, new_targets, 'D'))

    return successors


def solve():
    initial_state = (INITIAL_RACK_Y, INITIAL_NUM_SEGMENTS, INITIAL_TARGETS)

    if check_win(*initial_state):
        print("Already won!")
        return

    queue = deque()
    queue.append((initial_state, []))
    visited = {initial_state}

    max_depth = 35
    iterations = 0

    while queue:
        state, path = queue.popleft()
        rack_y, num_seg, targets = state

        if len(path) >= max_depth:
            continue

        iterations += 1
        if iterations % 100000 == 0:
            print(f"  iter={iterations}, depth={len(path)}, queue={len(queue)}, visited={len(visited)}")

        for new_ry, new_ns, new_t, action in get_successors(rack_y, num_seg, targets):
            new_state = (new_ry, new_ns, new_t)

            if new_state in visited:
                continue
            visited.add(new_state)

            new_path = path + [action]

            if check_win(new_ry, new_ns, new_t):
                print(f"\n*** SOLUTION FOUND! ***")
                print(f"Actions ({len(new_path)}): {''.join(new_path)}")
                print(f"Iterations: {iterations}")
                print(f"States visited: {len(visited)}")
                action_map = {'U': 'ACTION1', 'D': 'ACTION2', 'L': 'ACTION3', 'R': 'ACTION4'}
                print(f"Game actions: {[action_map[a] for a in new_path]}")
                return new_path

            queue.append((new_state, new_path))

    print(f"\nNo solution found within depth {max_depth}")
    print(f"Iterations: {iterations}, States: {len(visited)}")
    return None


if __name__ == "__main__":
    # Quick validation
    print("Validating against engine trace...")
    state = (42, 2, INITIAL_TARGETS)
    for a in 'RRRRRRUUU':
        for s in get_successors(*state):
            if s[3] == a:
                state = (s[0], s[1], s[2])
                break
    print(f"After RRRRRRUUU: {state}")
    # Expected: rack=24, segs=8, targets all at y=18

    for a in 'LLLUR':
        for s in get_successors(*state):
            if s[3] == a:
                state = (s[0], s[1], s[2])
                break
    print(f"After LLLUR: rack=({RACK_X},{state[0]}) segs={state[1]} targets={sorted(state[2])}")
    # Expected: rack=18, segs=6, targets at (29,12,14), (35,18,9), (41,18,12), (47,18,8)

    print()
    print("Starting BFS...")
    solve()
