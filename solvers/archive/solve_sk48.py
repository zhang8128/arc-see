#!/usr/bin/env python3
"""
SK48 Solver — Pure-Python BFS for Level 2.

Key insight: targets (elmjchdqcn) are PUSHED by segments during cascade.
The puzzle is about rearranging targets into the reference order by
pushing them with rack segments.

Game mechanics (L2):
- Rack at x=5, starts at y=42, rotation=0 (RIGHT-facing)
- Segments are horizontal, contiguous at (5+6*i, rack_y) for i=0..n-1
- 6 ramps at x=7, y={8,14,20,26,32,38} enable UP/DOWN cascade
- 4 targets initially at y=24: (29,24)=14, (35,24)=9, (41,24)=12, (47,24)=8
- Reference order: [8, 12, 9, 14]
- Boundary frame at (11,6), 7x7 tiles = x:11-52, y:6-47 (inner area)
- Turn limit: 196

Actions:
- RIGHT: add segment at rack base, push all right by 6
  - Rightmost segment pushes targets if present
- LEFT: pop leftmost segment, shift all left by 6
  - Must have >1 segment
- UP: move rack and all segments up by 6 (requires ramp)
  - Segments push targets vertically
- DOWN: move rack and all segments down by 6 (requires ramp)
  - Segments push targets vertically
"""

from collections import deque
import sys

# Constants
CELL = 6  # pixels per grid cell
RACK_X = 5  # rack base x position
RAMP_X = 7  # ramps at x=7
RAMP_YS = {8, 14, 20, 26, 32, 38}  # ramp y positions
RAMP_HEIGHT = 8  # ramp sprite height

# Boundary frame: (11, 6) with 7x7 tiles
FRAME_X_MIN = 11
FRAME_X_MAX = 11 + 7 * CELL - CELL  # 11 + 36 = 47 (last valid x)
FRAME_Y_MIN = 6
FRAME_Y_MAX = 6 + 7 * CELL - CELL  # 6 + 36 = 42 (last valid y)

# Initial state for L2
INITIAL_RACK_Y = 42
INITIAL_NUM_SEGMENTS = 2  # segments at x=5, x=11

# Targets: (x, y, color)
INITIAL_TARGETS = (
    (29, 24, 14),  # EE
    (35, 24, 9),   # 99
    (41, 24, 12),  # CC
    (47, 24, 8),   # 88
)

# Reference order (colors that segments must sit on, left-to-right)
REFERENCE = (8, 12, 9, 14)

# Max segment count practical limit
MAX_SEGMENTS = 12


def has_ramp(rack_y, direction):
    """Check if there's a ramp allowing cascade in given direction.

    direction: -1 for UP, +1 for DOWN
    Check position: (RAMP_X, rack_y + 2 + direction * 3)
    Actually from code: (rack.x + 2 + dx//2, rack.y + 2 + dy//2)
    where dx=0, dy=direction*6
    So check_y = rack_y + 2 + direction*3
    """
    check_y = rack_y + 2 + direction * 3
    # Check if any ramp sprite covers this position
    for ry in RAMP_YS:
        if ry <= check_y < ry + RAMP_HEIGHT:
            return True
    return False


def target_at(targets, x, y):
    """Find target index at position (x, y), or -1."""
    for i, (tx, ty, tc) in enumerate(targets):
        if tx == x and ty == y:
            return i
    return -1


def can_push_target(targets, idx, dx, dy):
    """Check if target at idx can be pushed by (dx, dy).

    Returns new targets tuple if push succeeds, or None if blocked.
    Targets can push other targets recursively.

    KEY: Targets do NOT have boundary checks in the game engine!
    They can be pushed outside the frame. Only other targets block them.
    """
    tx, ty, tc = targets[idx]
    new_x = tx + dx
    new_y = ty + dy

    # NO boundary check for targets! They can go anywhere.

    # Check if another target is at the destination
    targets_list = list(targets)
    blocking = target_at(targets, new_x, new_y)
    if blocking >= 0:
        # Try to push the blocking target too
        result = can_push_target(tuple(targets_list), blocking, dx, dy)
        if result is None:
            return None
        targets_list = list(result)

    targets_list[idx] = (new_x, new_y, tc)
    return tuple(targets_list)


def check_win(rack_y, num_segments, targets):
    """Check if current state satisfies WIN condition.

    For each segment (left-to-right), find target at segment position.
    Collect target colors in order. Compare with REFERENCE.
    """
    found_colors = []
    for i in range(num_segments):
        seg_x = RACK_X + CELL * i
        seg_y = rack_y
        tidx = target_at(targets, seg_x, seg_y)
        if tidx >= 0:
            found_colors.append(targets[tidx][2])

    if len(found_colors) != len(REFERENCE):
        return False
    return tuple(found_colors) == REFERENCE


def get_successors(rack_y, num_segments, targets):
    """Generate all valid successor states from current state.

    Returns list of (new_rack_y, new_num_segments, new_targets, action_name)
    """
    successors = []

    # RIGHT: push all segments right, add new at base
    if num_segments < MAX_SEGMENTS:
        can_push = True

        # Rightmost segment moves to x + CELL. Check SEGMENT boundary only.
        rightmost_x = RACK_X + CELL * (num_segments - 1)
        new_rightmost_x = rightmost_x + CELL

        # Segment boundary: new position + width must fit in frame
        if new_rightmost_x + CELL > FRAME_X_MAX + CELL:  # x + 6 > 53
            can_push = False

        if can_push:
            # Check if each segment's destination has a target that needs pushing
            # Targets have NO boundary check — they can be pushed anywhere.
            # Process from rightmost to leftmost.
            new_targets_list = list(targets)
            for i in range(num_segments - 1, -1, -1):
                seg_x = RACK_X + CELL * i
                new_seg_x = seg_x + CELL
                # Check current position AND destination for targets (game checks both)
                for check_x in [seg_x, new_seg_x]:
                    tidx = target_at(tuple(new_targets_list), check_x, rack_y)
                    if tidx >= 0:
                        result = can_push_target(tuple(new_targets_list), tidx, CELL, 0)
                        if result is None:
                            can_push = False
                            break
                        new_targets_list = list(result)
                if not can_push:
                    break

            if can_push:
                successors.append((rack_y, num_segments + 1, tuple(new_targets_list), 'R'))

    # LEFT: pop leftmost segment, shift remaining left
    if num_segments > 1:
        can_pop = True
        new_targets_list = list(targets)

        # Remaining segments (index 1..n-1) shift left by CELL.
        # Check both current pos and destination for targets.
        for i in range(1, num_segments):
            seg_x = RACK_X + CELL * i
            new_seg_x = seg_x - CELL
            for check_x in [seg_x, new_seg_x]:
                tidx = target_at(tuple(new_targets_list), check_x, rack_y)
                if tidx >= 0:
                    result = can_push_target(tuple(new_targets_list), tidx, -CELL, 0)
                    if result is None:
                        can_pop = False
                        break
                    new_targets_list = list(result)
            if not can_pop:
                break

        if can_pop:
            successors.append((rack_y, num_segments - 1, tuple(new_targets_list), 'L'))

    # UP: cascade rack and all segments up by CELL
    if has_ramp(rack_y, -1):
        new_rack_y = rack_y - CELL
        if new_rack_y >= FRAME_Y_MIN:
            new_targets_list = list(targets)
            can_cascade = True

            # All segments move up. Check current pos and destination for targets.
            for i in range(num_segments):
                seg_x = RACK_X + CELL * i
                for check_y in [rack_y, new_rack_y]:
                    tidx = target_at(tuple(new_targets_list), seg_x, check_y)
                    if tidx >= 0:
                        result = can_push_target(tuple(new_targets_list), tidx, 0, -CELL)
                        if result is None:
                            can_cascade = False
                            break
                        new_targets_list = list(result)
                if not can_cascade:
                    break

            if can_cascade:
                successors.append((new_rack_y, num_segments, tuple(new_targets_list), 'U'))

    # DOWN: cascade rack and all segments down by CELL
    if has_ramp(rack_y, +1):
        new_rack_y = rack_y + CELL
        if new_rack_y <= FRAME_Y_MAX:
            new_targets_list = list(targets)
            can_cascade = True

            for i in range(num_segments):
                seg_x = RACK_X + CELL * i
                for check_y in [rack_y, new_rack_y]:
                    tidx = target_at(tuple(new_targets_list), seg_x, check_y)
                    if tidx >= 0:
                        result = can_push_target(tuple(new_targets_list), tidx, 0, CELL)
                        if result is None:
                            can_cascade = False
                            break
                        new_targets_list = list(result)
                if not can_cascade:
                    break

            if can_cascade:
                successors.append((new_rack_y, num_segments, tuple(new_targets_list), 'D'))

    return successors


def solve():
    """BFS solver for SK48 L2."""
    initial_state = (INITIAL_RACK_Y, INITIAL_NUM_SEGMENTS, INITIAL_TARGETS)

    if check_win(*initial_state):
        print("Already won!")
        return

    queue = deque()
    queue.append((initial_state, []))
    visited = {initial_state}

    max_depth = 35  # baseline is 32
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

                # Convert to game actions
                action_map = {'U': 'ACTION1', 'D': 'ACTION2', 'L': 'ACTION3', 'R': 'ACTION4'}
                print(f"\nGame actions: {[action_map[a] for a in new_path]}")

                # Print final state
                print(f"\nFinal state: rack_y={new_ry}, segments={new_ns}")
                for i, (tx, ty, tc) in enumerate(new_t):
                    print(f"  Target {i}: ({tx}, {ty}) color={tc}")
                return new_path

            queue.append((new_state, new_path))

    print(f"\nNo solution found within depth {max_depth}")
    print(f"Iterations: {iterations}")
    print(f"States visited: {len(visited)}")
    return None


if __name__ == "__main__":
    print("SK48 L2 Solver — Pure Python BFS")
    print(f"Initial: rack_y={INITIAL_RACK_Y}, segments={INITIAL_NUM_SEGMENTS}")
    print(f"Targets: {INITIAL_TARGETS}")
    print(f"Reference: {REFERENCE}")
    print(f"Frame: x=[{FRAME_X_MIN},{FRAME_X_MAX}], y=[{FRAME_Y_MIN},{FRAME_Y_MAX}]")
    print()

    result = solve()
    if result:
        print(f"\nSolution: {''.join(result)} ({len(result)} actions)")
