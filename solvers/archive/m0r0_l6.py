"""M0R0 Level 6 solver — full BFS with interleaved cvcer/piece movement.
L6 has no walls, 1 cvcer, dfnuk barriers, and wyiex death zones.
Key: (6,9) is the only safe crossing point in column 6. Cvcer blocks it."""
from collections import deque

BASELINE = 126

# Grid
GW, GH = 13, 13

# Wyiex death zones (exact from game engine)
WYIEX = set()
for x in range(13):
    WYIEX.add((x, 0))
    WYIEX.add((x, 12))
for y in range(1, 12):
    WYIEX.add((0, y))
    WYIEX.add((12, y))
for y in [1, 2, 3, 4, 5, 6, 7, 8, 10, 11]:
    WYIEX.add((6, y))
WYIEX.update([(5, 6), (1, 6), (7, 6), (11, 6)])

# Switches
HNUTP_RAIXB = frozenset([(9, 2), (3, 9)])
HNUTP_UJCZE = frozenset([(3, 2)])

# Barrier cells (when closed)
DFNUK_RAIXB = frozenset([(2, 6), (3, 6), (4, 6)])
DFNUK_UJCZE = frozenset([(8, 6), (9, 6), (10, 6)])

# Initial positions
INIT_A = (3, 4)
INIT_B = (9, 4)
INIT_CVCER = (6, 9)

DX = [0, 0, -1, 1]
DY = [-1, 1, 0, 0]
DIR_NAMES = ["U", "D", "L", "R"]


def compute_barriers(A, B, cancelled):
    """Which barrier colors are open based on piece positions on switches."""
    active = set()
    if A and "A" not in cancelled:
        active.add(A)
    if B and "B" not in cancelled:
        active.add(B)

    raixb_open = bool(active & HNUTP_RAIXB)
    ujcze_open = bool(active & HNUTP_UJCZE)
    return (raixb_open, ujcze_open)


def get_blocked(raixb_open, ujcze_open):
    """Get blocked cells from barriers."""
    blocked = set()
    if not raixb_open:
        blocked.update(DFNUK_RAIXB)
    if not ujcze_open:
        blocked.update(DFNUK_UJCZE)
    return blocked


def bfs_solve():
    limit = min(BASELINE + 10, 150)

    init_barriers = compute_barriers(INIT_A, INIT_B, frozenset())

    # State: (A, B, cvcer, cancelled, barriers, mode)
    # mode: -1 = player, 0 = cvcer selected
    init_state = (INIT_A, INIT_B, INIT_CVCER, frozenset(), init_barriers, -1)

    queue = deque([(init_state, [])])
    visited = {init_state}
    iters = 0

    while queue:
        state, path = queue.popleft()
        iters += 1
        if iters % 500000 == 0:
            print(f"  iter={iters} q={len(queue)} d={len(path)} v={len(visited)}", flush=True)
        if len(path) >= limit:
            continue

        A, B, cvcer, cancelled, barriers, mode = state
        raixb_open, ujcze_open = barriers
        barrier_blocked = get_blocked(raixb_open, ujcze_open)

        actions = []  # (new_state, action_name)

        if mode == -1:  # Player mode
            for d in range(4):
                dx, dy = DX[d], DY[d]

                # Piece A: (dx, dy)
                if A and "A" not in cancelled:
                    nax, nay = A[0] + dx, A[1] + dy
                    # Blocked by: grid bounds, cvcer, barriers (no walls in L6)
                    if (nax < 0 or nax >= GW or nay < 0 or nay >= GH or
                        (nax, nay) == cvcer or (nax, nay) in barrier_blocked):
                        nax, nay = A
                    new_A = (nax, nay)
                else:
                    new_A = A

                # Piece B: (-dx, dy)
                if B and "B" not in cancelled:
                    nbx, nby = B[0] - dx, B[1] + dy
                    if (nbx < 0 or nbx >= GW or nby < 0 or nby >= GH or
                        (nbx, nby) == cvcer or (nbx, nby) in barrier_blocked):
                        nbx, nby = B
                    new_B = (nbx, nby)
                else:
                    new_B = B

                # Check wyiex death
                hit_death = False
                if new_A and "A" not in cancelled and new_A in WYIEX:
                    hit_death = True
                if new_B and "B" not in cancelled and new_B in WYIEX:
                    hit_death = True

                if hit_death:
                    # Reset ALL to initial — including cvcer
                    new_barriers = compute_barriers(INIT_A, INIT_B, frozenset())
                    new_state = (INIT_A, INIT_B, INIT_CVCER, frozenset(), new_barriers, -1)
                    if new_state not in visited:
                        visited.add(new_state)
                        queue.append((new_state, path + [DIR_NAMES[d]]))
                    continue

                # Check merge
                new_cancelled = set(cancelled)
                if (new_A and "A" not in new_cancelled and
                    new_B and "B" not in new_cancelled):
                    old_A, old_B = A, B
                    if (old_A and old_B and
                        abs(old_A[0] - old_B[0]) == 1 and old_A[1] == old_B[1]):
                        if ((new_A[0] == old_B[0] and new_A[1] == old_B[1]) or
                            (new_B[0] == old_A[0] and new_B[1] == old_A[1])):
                            mx = (new_A[0] + new_B[0]) // 2
                            my = (new_A[1] + new_B[1]) // 2
                            new_A = (mx, my)
                            new_B = (mx, my)
                    if new_A == new_B:
                        new_cancelled.add("A")
                        new_cancelled.add("B")

                new_cancelled = frozenset(new_cancelled)

                # Win check
                active = sum(1 for p in ["A", "B"] if p not in new_cancelled)
                if active == 0:
                    result = path + [DIR_NAMES[d]]
                    print(f"  FOUND! {len(result)} moves ({iters} iters)")
                    return result

                new_barriers = compute_barriers(new_A, new_B, new_cancelled)
                new_state = (new_A, new_B, cvcer, new_cancelled, new_barriers, -1)
                if new_state not in visited:
                    visited.add(new_state)
                    queue.append((new_state, path + [DIR_NAMES[d]]))

            # Click cvcer to select
            new_state = (A, B, cvcer, cancelled, barriers, 0)
            if new_state not in visited:
                visited.add(new_state)
                queue.append((new_state, path + ["S"]))  # S = select

        else:  # Cvcer selected (mode = 0)
            for d in range(4):
                dx, dy = DX[d], DY[d]
                nx, ny = cvcer[0] + dx, cvcer[1] + dy
                if nx < 0 or nx >= GW or ny < 0 or ny >= GH:
                    continue
                # Cvcer blocked by: wyiex (collidable), barriers, pieces
                if (nx, ny) in WYIEX:
                    continue
                if (nx, ny) in barrier_blocked:
                    continue
                # Check collision with pieces
                if A and "A" not in cancelled and (nx, ny) == A:
                    continue
                if B and "B" not in cancelled and (nx, ny) == B:
                    continue

                new_state = (A, B, (nx, ny), cancelled, barriers, 0)
                if new_state not in visited:
                    visited.add(new_state)
                    queue.append((new_state, path + [DIR_NAMES[d]]))

            # Click to deselect
            new_state = (A, B, cvcer, cancelled, barriers, -1)
            if new_state not in visited:
                visited.add(new_state)
                queue.append((new_state, path + ["X"]))

    print(f"  No solution ({iters} iters, {len(visited)} states)", flush=True)
    return None


if __name__ == "__main__":
    print(f"Level 6 (baseline={BASELINE}):", flush=True)
    result = bfs_solve()
    if result:
        print(f"  Solution: {len(result)} moves")
        print(f"  Path: {' '.join(result)}")
    else:
        print("  FAILED")
