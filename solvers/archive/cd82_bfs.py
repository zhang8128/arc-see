"""Solver for CD82 — painting puzzle with 8 throw directions + 4 paddle throws.

Each throw paints a region of the 10x10 canvas. Order matters (later overwrites earlier).
Win condition: canvas matches target (ignoring both diagonals).

Throw regions (ACTION5, "full throws"):
  Dir 0 (horizontal, rot=180): rows 0:5, all cols  — TOP HALF
  Dir 4 (horizontal, rot=0):   rows 5:10, all cols — BOTTOM HALF
  Dir 6 (horizontal, rot=90):  all rows, cols 0:5  — LEFT HALF
  Dir 2 (horizontal, rot=270): all rows, cols 5:10 — RIGHT HALF
  Dir 1 (diagonal, rot=0):     row i → cols i:10   — UPPER-RIGHT TRIANGLE
  Dir 3 (diagonal, rot=90):    row i → cols 9-i:10 — LOWER-RIGHT TRIANGLE
  Dir 5 (diagonal, rot=180):   row i → cols 0:i+1  — LOWER-LEFT TRIANGLE
  Dir 7 (diagonal, rot=270):   row i → cols 0:10-i — UPPER-LEFT TRIANGLE

Paddle throws (click on paddle, only dirs 0,2,4,6):
  Dir 0: rows 0:3, cols 3:7
  Dir 4: rows 7:10, cols 3:7
  Dir 6: rows 3:7, cols 0:3
  Dir 2: rows 3:7, cols 7:10
"""
import numpy as np
from collections import deque
from itertools import product
import time
import importlib.util


# ─── Paint region definitions ───

def make_full_throw_mask(direction):
    """Return a 10x10 bool mask for the full throw (ACTION5) from given direction."""
    mask = np.zeros((10, 10), dtype=bool)
    nicoqsvlg = [
        ("horizontal", 180),  # 0
        ("diagonal", 0),      # 1
        ("horizontal", 270),  # 2
        ("diagonal", 90),     # 3
        ("horizontal", 0),    # 4
        ("diagonal", 180),    # 5
        ("horizontal", 90),   # 6
        ("diagonal", 270),    # 7
    ]
    btype, rotation = nicoqsvlg[direction]
    if btype == "horizontal":
        if rotation == 180:
            mask[0:5, :] = True
        elif rotation == 0:
            mask[5:10, :] = True
        elif rotation == 90:
            mask[:, 0:5] = True
        elif rotation == 270:
            mask[:, 5:10] = True
    else:  # diagonal
        if rotation == 0:      # dir 1: upper-right
            for i in range(10):
                mask[i, i:10] = True
        elif rotation == 90:   # dir 3: lower-right
            for i in range(10):
                mask[i, 9-i:10] = True
        elif rotation == 180:  # dir 5: lower-left
            for i in range(10):
                mask[i, 0:i+1] = True
        elif rotation == 270:  # dir 7: upper-left
            for i in range(10):
                mask[i, 0:10-i] = True
    return mask


def make_paddle_throw_mask(direction):
    """Return a 10x10 bool mask for the paddle throw (click) from given direction."""
    mask = np.zeros((10, 10), dtype=bool)
    if direction == 0:
        mask[0:3, 3:7] = True
    elif direction == 4:
        mask[7:10, 3:7] = True
    elif direction == 6:
        mask[3:7, 0:3] = True
    elif direction == 2:
        mask[3:7, 7:10] = True
    else:
        return None  # paddle only for dirs 0,2,4,6
    return mask


# Precompute all throw masks
FULL_MASKS = {d: make_full_throw_mask(d) for d in range(8)}
PADDLE_MASKS = {}
for d in [0, 2, 4, 6]:
    PADDLE_MASKS[d] = make_paddle_throw_mask(d)

# Diagonal ignore mask
DIAG_MASK = np.ones((10, 10), dtype=bool)
for i in range(10):
    DIAG_MASK[i, i] = False
    DIAG_MASK[i, 9 - i] = False


# ─── Target patterns from game source ───

TARGETS = {
    1: np.array([
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [15, 15, 15, 15, 15, 15, 15, 15, 15, 15],
        [15, 15, 15, 15, 15, 15, 15, 15, 15, 15],
        [15, 15, 15, 15, 15, 15, 15, 15, 15, 15],
        [15, 15, 15, 15, 15, 15, 15, 15, 15, 15],
        [15, 15, 15, 15, 15, 15, 15, 15, 15, 15],
    ]),
    2: np.array([
        [15, 15, 15, 15, 15, 15, 15, 15, 15, 12],
        [15, 15, 15, 15, 15, 15, 15, 15, 12, 12],
        [15, 15, 15, 15, 15, 15, 15, 12, 12, 12],
        [15, 15, 15, 15, 15, 15, 12, 12, 12, 12],
        [15, 15, 15, 15, 15, 12, 12, 12, 12, 12],
        [0, 0, 0, 0, 12, 12, 12, 12, 12, 12],
        [0, 0, 0, 12, 12, 12, 12, 12, 12, 12],
        [0, 0, 12, 12, 12, 12, 12, 12, 12, 12],
        [0, 12, 12, 12, 12, 12, 12, 12, 12, 12],
        [12, 12, 12, 12, 12, 12, 12, 12, 12, 12],
    ]),
    3: np.array([
        [15, 15, 15, 12, 12, 12, 12, 15, 15, 15],
        [15, 15, 15, 12, 12, 12, 12, 15, 15, 14],
        [15, 15, 15, 12, 12, 12, 12, 15, 14, 14],
        [15, 15, 15, 15, 15, 15, 15, 14, 14, 14],
        [15, 15, 15, 15, 15, 15, 14, 14, 14, 14],
        [15, 15, 15, 15, 15, 14, 14, 14, 14, 14],
        [15, 15, 15, 15, 8, 14, 14, 14, 14, 14],
        [15, 15, 15, 8, 8, 14, 14, 14, 14, 14],
        [15, 15, 8, 8, 8, 14, 14, 14, 14, 14],
        [15, 8, 8, 8, 8, 14, 14, 14, 14, 14],
    ]),
    4: np.array([
        [9, 9, 9, 9, 9, 12, 12, 12, 12, 15],
        [9, 9, 9, 9, 9, 12, 12, 12, 15, 15],
        [9, 9, 9, 9, 9, 12, 12, 15, 15, 15],
        [11, 11, 11, 9, 9, 12, 15, 15, 15, 15],
        [11, 11, 11, 9, 9, 15, 15, 15, 15, 15],
        [11, 11, 11, 9, 9, 15, 15, 15, 15, 15],
        [11, 11, 11, 9, 9, 15, 15, 15, 15, 15],
        [9, 9, 9, 9, 9, 15, 15, 15, 15, 15],
        [9, 9, 9, 9, 9, 15, 15, 15, 15, 15],
        [9, 9, 9, 9, 9, 15, 15, 15, 15, 15],
    ]),
    5: np.array([
        [14, 9, 9, 8, 8, 8, 8, 9, 9, 12],
        [14, 14, 9, 8, 8, 8, 8, 9, 12, 12],
        [14, 14, 14, 8, 8, 8, 8, 12, 12, 12],
        [14, 14, 14, 14, 9, 9, 12, 12, 12, 12],
        [14, 14, 14, 14, 14, 12, 12, 12, 12, 12],
        [14, 14, 14, 14, 12, 12, 12, 12, 12, 12],
        [14, 14, 14, 12, 12, 12, 12, 12, 12, 12],
        [14, 14, 12, 12, 12, 12, 12, 12, 12, 12],
        [14, 12, 12, 12, 12, 12, 12, 12, 12, 12],
        [12, 12, 12, 12, 12, 12, 12, 12, 12, 12],
    ]),
    6: np.array([
        [8, 8, 8, 15, 15, 15, 15, 8, 8, 8],
        [8, 8, 8, 15, 15, 15, 15, 8, 8, 14],
        [8, 8, 8, 15, 15, 15, 15, 8, 14, 14],
        [11, 11, 11, 8, 8, 8, 8, 14, 14, 14],
        [11, 11, 11, 8, 8, 8, 14, 14, 14, 14],
        [11, 11, 11, 8, 8, 14, 14, 14, 14, 14],
        [11, 11, 11, 8, 0, 14, 14, 14, 14, 14],
        [8, 8, 8, 0, 0, 14, 14, 14, 14, 14],
        [8, 8, 0, 0, 0, 14, 14, 14, 14, 14],
        [8, 0, 0, 0, 0, 14, 14, 14, 14, 14],
    ]),
}


# ─── Navigation cost computation ───

# Grid position (col, row) for each direction
DIR_TO_GRID = {
    0: (0, 1), 1: (0, 2), 2: (1, 2), 3: (2, 2),
    4: (2, 1), 5: (2, 0), 6: (1, 0), 7: (0, 0),
}

def nav_cost(from_dir, to_dir):
    """Minimum ACTION1-4 presses to navigate from from_dir to to_dir on the 3x3 grid."""
    if from_dir == to_dir:
        return 0
    fc, fr = DIR_TO_GRID[from_dir]
    tc, tr = DIR_TO_GRID[to_dir]
    # BFS on 3x3 grid avoiding center (1,1)
    from collections import deque as dq
    visited = {(fc, fr)}
    queue = dq([(fc, fr, 0)])
    while queue:
        c, r, d = queue.popleft()
        for dc, dr in [(-1,0),(1,0),(0,-1),(0,1)]:
            nc, nr = c+dc, r+dr
            if 0 <= nc <= 2 and 0 <= nr <= 2 and (nc, nr) != (1, 1) and (nc, nr) not in visited:
                if (nc, nr) == (tc, tr):
                    return d + 1
                visited.add((nc, nr))
                queue.append((nc, nr, d + 1))
    return 99  # unreachable


# ─── Color button positions ───

# Levels 3-6: colors at x positions [21, 27, 33, 39, 45, 51, 57]
# pqkenviek with color_remap(0, X): pixel[2,2] = X
# Colors: [0, 15, 12, 11, 14, 8, 9] (default 0 button + 6 remapped)
LEVEL_COLORS = {
    1: [0, 15],
    2: [0, 15, 12],
    3: [0, 15, 12, 11, 14, 8, 9],
    4: [0, 15, 12, 11, 14, 8, 9],
    5: [0, 15, 12, 11, 14, 8, 9],
    6: [0, 15, 12, 11, 14, 8, 9],
}


# ─── Canvas simulation ───

def apply_throw(canvas, direction, color, throw_type="full"):
    """Apply a throw to canvas (modifies in place)."""
    if throw_type == "full":
        mask = FULL_MASKS[direction]
    else:
        mask = PADDLE_MASKS.get(direction)
        if mask is None:
            return
    canvas[mask] = color


def check_win(canvas, target):
    """Check if canvas matches target (ignoring diagonals)."""
    return np.array_equal(canvas[DIAG_MASK], target[DIAG_MASK])


# ─── Solver ───

def solve_level(level_num, max_throws=12, verbose=True):
    """
    Find optimal throw sequence for a level.
    Uses iterative deepening DFS over throw sequences.
    """
    target = TARGETS[level_num]
    colors = LEVEL_COLORS[level_num]

    # Determine which colors appear in target (ignoring diagonals)
    target_colors = set(target[DIAG_MASK].flatten())
    if verbose:
        print(f"\nLevel {level_num}: target uses colors {target_colors}")

    # Build all possible throws
    throws = []
    for d in range(8):
        for c in colors:
            if c not in target_colors:
                continue  # skip colors not in target
            throws.append((d, c, "full"))
    for d in [0, 2, 4, 6]:
        for c in colors:
            if c not in target_colors:
                continue
            throws.append((d, c, "paddle"))

    if verbose:
        print(f"  {len(throws)} possible throws (filtered to target colors)")

    # Try increasing number of throws
    for n_throws in range(1, max_throws + 1):
        if verbose:
            print(f"  Trying {n_throws} throws...", end=" ", flush=True)

        start_time = time.time()
        result = dfs_solve(target, throws, n_throws, colors)
        elapsed = time.time() - start_time

        if result is not None:
            if verbose:
                print(f"FOUND in {elapsed:.1f}s")
                for t in result:
                    print(f"    {t}")
            return result
        else:
            if verbose:
                print(f"no solution ({elapsed:.1f}s)")

    return None


def dfs_solve(target, throws, max_depth, colors):
    """DFS with pruning to find a throw sequence that produces the target."""
    canvas = np.zeros((10, 10), dtype=np.int32)

    def dfs(depth, sequence, current_dir):
        nonlocal canvas
        if depth == max_depth:
            return check_win(canvas, target)

        for throw in throws:
            d, c, ttype = throw
            mask = FULL_MASKS[d] if ttype == "full" else PADDLE_MASKS.get(d)
            if mask is None:
                continue

            # Save old values under mask
            old_vals = canvas[mask].copy()

            # Apply throw
            canvas[mask] = c

            if dfs(depth + 1, sequence + [throw], d):
                sequence.append(throw)
                return True

            # Undo throw
            canvas[mask] = old_vals

        return False

    sequence = []
    if dfs(0, sequence, 0):
        # sequence was built in reverse (appended during unwinding)
        # Actually the way I wrote it, it's appended during return, so it IS reversed
        # Let me fix: collect properly
        pass

    # Better approach: collect sequence properly
    result = [None] * max_depth

    def dfs2(depth, current_dir):
        nonlocal canvas
        if depth == max_depth:
            return check_win(canvas, target)

        for throw in throws:
            d, c, ttype = throw
            mask = FULL_MASKS[d] if ttype == "full" else PADDLE_MASKS.get(d)
            if mask is None:
                continue

            old_vals = canvas[mask].copy()
            canvas[mask] = c

            if dfs2(depth + 1, d):
                result[depth] = throw
                return True

            canvas[mask] = old_vals

        return False

    canvas = np.zeros((10, 10), dtype=np.int32)
    if dfs2(0, 0):
        return [r for r in result if r is not None]
    return None


def compute_action_sequence(throw_sequence, level_num, start_dir=0):
    """
    Convert a throw sequence into actual game actions.
    Returns list of (action_type, data) pairs.
    """
    colors = LEVEL_COLORS[level_num]
    # Color button x-positions
    if level_num >= 3:
        color_x = {0: 21, 15: 27, 12: 33, 11: 39, 14: 45, 8: 51, 9: 57}
    elif level_num == 2:
        color_x = {0: 32, 15: 38, 12: 44}
    else:
        color_x = {0: 35, 15: 41}
    color_y = 2  # all at y=2

    actions = []
    current_dir = start_dir
    current_color = 15  # default color

    for (direction, color, throw_type) in throw_sequence:
        # Select color if needed
        if color != current_color:
            actions.append(("ACTION6", {"x_grid": color_x[color] + 2, "y_grid": color_y + 2}))
            current_color = color

        if throw_type == "full":
            # Navigate to direction
            # Build nav path
            nav = get_nav_actions(current_dir, direction)
            actions.extend(nav)
            current_dir = direction
            # Throw
            actions.append(("ACTION5", {}))
        else:
            # Paddle throw: need to be at the horizontal direction, then click paddle
            nav = get_nav_actions(current_dir, direction)
            actions.extend(nav)
            current_dir = direction
            # Click the paddle sprite
            actions.append(("PADDLE_CLICK", {"direction": direction}))

    return actions


def get_nav_actions(from_dir, to_dir):
    """Get ACTION1-4 sequence to navigate from from_dir to to_dir."""
    if from_dir == to_dir:
        return []
    fc, fr = DIR_TO_GRID[from_dir]
    tc, tr = DIR_TO_GRID[to_dir]
    # BFS
    from collections import deque as dq
    visited = {(fc, fr): []}
    queue = dq([(fc, fr)])
    moves = {(-1, 0): "ACTION1", (1, 0): "ACTION2", (0, -1): "ACTION3", (0, 1): "ACTION4"}
    while queue:
        c, r = queue.popleft()
        for (dc, dr), action in moves.items():
            nc, nr = c + dc, r + dr
            if 0 <= nc <= 2 and 0 <= nr <= 2 and (nc, nr) != (1, 1) and (nc, nr) not in visited:
                path = visited[(c, r)] + [(action, {})]
                if (nc, nr) == (tc, tr):
                    return path
                visited[(nc, nr)] = path
                queue.append((nc, nr))
    return []


def count_actions(throw_sequence, level_num, start_dir=0):
    """Count total actions needed for a throw sequence."""
    current_dir = start_dir
    current_color = 15
    total = 0

    for (direction, color, throw_type) in throw_sequence:
        if color != current_color:
            total += 1  # ACTION6 for color
            current_color = color
        total += nav_cost(current_dir, direction)
        current_dir = direction
        total += 1  # ACTION5 or paddle click
    return total


# ─── Smarter solver: analyze target structure ───

def analyze_target(level_num):
    """Analyze what the target looks like after masking diagonals."""
    target = TARGETS[level_num]
    print(f"\nLevel {level_num} target (ignoring diagonals):")
    for i in range(10):
        row = []
        for j in range(10):
            if not DIAG_MASK[i, j]:
                row.append("  _")
            else:
                row.append(f"{target[i,j]:3d}")
        print("".join(row))

    colors = set(target[DIAG_MASK].flatten())
    print(f"Colors needed: {colors}")

    # Check which single throws cover entire color regions
    for color in colors:
        color_mask = (target == color) & DIAG_MASK
        n_cells = color_mask.sum()
        print(f"\n  Color {color}: {n_cells} cells")
        for d in range(8):
            full_mask = FULL_MASKS[d] & DIAG_MASK
            # Check if this throw's visible region is a superset of the color region
            if np.all(color_mask <= full_mask):
                print(f"    Full dir {d} covers all color-{color} cells")
        for d in [0, 2, 4, 6]:
            paddle_mask = PADDLE_MASKS[d] & DIAG_MASK
            if np.all(color_mask <= paddle_mask):
                print(f"    Paddle dir {d} covers all color-{color} cells")


# ─── Optimized solver using backwards analysis ───

def solve_level_backwards(level_num, verbose=True):
    """
    Solve by working backwards from the target.
    At each step, find a throw that, if applied last, would cover a maximal
    region of same-color cells. Remove that region and repeat.
    """
    target = TARGETS[level_num]
    colors = LEVEL_COLORS[level_num]
    target_colors = set(target[DIAG_MASK].flatten())

    # Cells we still need to paint (indexed by non-diagonal positions)
    remaining = np.copy(target)
    painted = np.zeros((10, 10), dtype=bool)  # cells already handled

    throws_reverse = []  # will be reversed at end

    for iteration in range(20):  # max iterations
        # Check if all non-diagonal cells are handled
        if np.all(painted | ~DIAG_MASK):
            break

        # Find best throw: covers most unpainted same-color cells
        best_throw = None
        best_score = -1

        all_throws = []
        for d in range(8):
            for c in target_colors:
                all_throws.append((d, c, "full"))
        for d in [0, 2, 4, 6]:
            for c in target_colors:
                all_throws.append((d, c, "paddle"))

        for throw in all_throws:
            d, c, ttype = throw
            mask = FULL_MASKS[d] if ttype == "full" else PADDLE_MASKS[d]
            # Cells this throw covers that need color c and aren't yet painted
            needed = (remaining == c) & DIAG_MASK & ~painted & mask
            # Cells this throw covers that DON'T need color c and aren't yet painted
            # (these would be wrong, but they'll be painted by a later throw in forward order)
            score = needed.sum()
            if score > best_score:
                best_score = score
                best_throw = throw

        if best_score <= 0:
            if verbose:
                print(f"  Stuck at iteration {iteration}, {(~painted & DIAG_MASK).sum()} cells remaining")
            return None

        d, c, ttype = best_throw
        mask = FULL_MASKS[d] if ttype == "full" else PADDLE_MASKS[d]
        # Mark all cells in this throw's region that need this color as painted
        newly_painted = (remaining == c) & DIAG_MASK & ~painted & mask
        painted |= newly_painted
        throws_reverse.append(best_throw)

        if verbose:
            print(f"  Step {iteration}: {best_throw} covers {newly_painted.sum()} cells, "
                  f"{(~painted & DIAG_MASK).sum()} remaining")

    # Reverse to get forward order
    throw_sequence = list(reversed(throws_reverse))

    # Verify
    canvas = np.zeros((10, 10), dtype=np.int32)
    for d, c, ttype in throw_sequence:
        apply_throw(canvas, d, c, ttype)

    if check_win(canvas, target):
        if verbose:
            print(f"  VERIFIED: {len(throw_sequence)} throws")
        return throw_sequence
    else:
        if verbose:
            print("  Backwards solution FAILED verification — trying exhaustive...")
        return None


# ─── BFS solver with canvas hashing ───

def solve_level_bfs(level_num, max_throws=8, verbose=True):
    """BFS over throw sequences with canvas hashing."""
    target = TARGETS[level_num]
    colors = LEVEL_COLORS[level_num]
    target_colors = set(target[DIAG_MASK].flatten())

    # Build throw list
    throws = []
    for d in range(8):
        for c in target_colors:
            throws.append((d, c, "full"))
    for d in [0, 2, 4, 6]:
        for c in target_colors:
            throws.append((d, c, "paddle"))

    if verbose:
        print(f"\nLevel {level_num} BFS: {len(throws)} throws, target colors {target_colors}")

    # BFS: state = canvas hash
    canvas0 = np.zeros((10, 10), dtype=np.int32)

    # Check if empty canvas already wins (unlikely)
    if check_win(canvas0, target):
        return []

    # BFS queue: (canvas_bytes, throw_sequence)
    visited = set()
    initial_hash = canvas0.tobytes()
    visited.add(initial_hash)
    queue = deque([(canvas0, [])])

    start_time = time.time()
    states_explored = 0

    while queue:
        canvas, seq = queue.popleft()
        states_explored += 1

        if states_explored % 100000 == 0 and verbose:
            elapsed = time.time() - start_time
            print(f"  {states_explored} states, depth {len(seq)}, {elapsed:.0f}s")

        if len(seq) >= max_throws:
            continue

        for throw in throws:
            d, c, ttype = throw
            mask = FULL_MASKS[d] if ttype == "full" else PADDLE_MASKS[d]

            new_canvas = canvas.copy()
            new_canvas[mask] = c

            if check_win(new_canvas, target):
                new_seq = seq + [throw]
                if verbose:
                    elapsed = time.time() - start_time
                    print(f"  SOLVED in {len(new_seq)} throws, {states_explored} states, {elapsed:.1f}s")
                return new_seq

            h = new_canvas.tobytes()
            if h not in visited:
                visited.add(h)
                queue.append((new_canvas, seq + [throw]))

    if verbose:
        print(f"  NO SOLUTION found within {max_throws} throws ({states_explored} states)")
    return None


# ─── Generate API actions ───

def generate_api_actions(throw_sequence, level_num):
    """Convert throw sequence to actual API actions (with navigation and color selection)."""
    if level_num >= 3:
        color_x = {0: 21, 15: 27, 12: 33, 11: 39, 14: 45, 8: 51, 9: 57}
    elif level_num == 2:
        color_x = {0: 32, 15: 38, 12: 44}
    else:
        color_x = {0: 35, 15: 41}

    actions = []
    current_dir = 0  # start at direction 0
    current_color = 15  # default

    for (direction, color, throw_type) in throw_sequence:
        # Select color
        if color != current_color:
            cx = color_x[color] + 2  # center of button
            cy = 2 + 2
            actions.append(f"ACTION6:{cx},{cy}")
            current_color = color

        # Navigate
        nav = get_nav_actions(current_dir, direction)
        for (act, _) in nav:
            actions.append(act)
        current_dir = direction

        if throw_type == "full":
            actions.append("ACTION5")
        else:
            actions.append(f"PADDLE:{direction}")

    return actions


# ─── Main ───

if __name__ == "__main__":
    # Analyze all levels
    for lv in range(1, 7):
        analyze_target(lv)

    print("\n" + "=" * 60)
    print("SOLVING")
    print("=" * 60)

    for lv in range(1, 7):
        print(f"\n--- Level {lv} ---")

        # Try backwards analysis first
        result = solve_level_backwards(lv)
        if result is None:
            # Try BFS
            result = solve_level_bfs(lv, max_throws=6)

        if result:
            total_actions = count_actions(result, lv)
            print(f"  Solution: {len(result)} throws, ~{total_actions} actions")
            api_actions = generate_api_actions(result, lv)
            print(f"  API actions ({len(api_actions)}): {' → '.join(api_actions[:20])}")
