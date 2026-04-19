"""
Comprehensive BFS solver for all LS20 levels (indices 0-6).

State-space BFS with step counter tracking and refill awareness.
Boundary sprites (xfmluydglp tag) are NOT walls -- only ihdgageizm-tagged
sprites block movement. This was the bug in the previous solver.

Movement: x in {4,9,14,...,59}, y in {0,5,10,...,55}
ACTION1=up(dy=-5), ACTION2=down(dy=+5), ACTION3=left(dx=-5), ACTION4=right(dx=+5)
Wall collision: wall at (wx,wy) blocks player at (px,py) if px<=wx<px+5 AND py<=wy<py+5
Pickup collision: same overlap check, pickup at (rx,ry) triggers when player at (px,py)
Colors: [12,9,14,8] (indices 0-3); color pickup cycles +1 mod 4
Rotations: [0,90,180,270] (indices 0-3); rotation pickup cycles +1 mod 4
Shapes: 6 shapes (indices 0-5); shape pickup cycles +1 mod 6
Step counter: starts at StepCounter, decremented by StepsDecrement each move
Step refills reset counter to StepCounter (before decrement); sprite removed after collection
Goal blocks if (shape, color, rotation) don't all match; allows entry when they match
"""

import re
import sys
from collections import deque
from itertools import permutations

GRID_X = list(range(4, 64, 5))   # 4, 9, 14, ..., 59
GRID_Y = list(range(0, 60, 5))   # 0, 5, 10, ..., 55
GRID_X_SET = set(GRID_X)
GRID_Y_SET = set(GRID_Y)

ACTION_DELTAS = {
    "ACTION1": (0, -5),   # up
    "ACTION2": (0, 5),    # down
    "ACTION3": (-5, 0),   # left
    "ACTION4": (5, 0),    # right
}

OPPOSITES = {
    "ACTION1": "ACTION2", "ACTION2": "ACTION1",
    "ACTION3": "ACTION4", "ACTION4": "ACTION3",
}

COLORS = [12, 9, 14, 8]
ROTATIONS = [0, 90, 180, 270]
N_SHAPES = 6


# =============================================================================
# PARSING
# =============================================================================

def parse_levels(ls20_file: str):
    """Parse ls20.py and extract level data for all levels."""
    with open(ls20_file) as f:
        content = f.read()

    levels_start = content.index("levels = [")
    levels_section = content[levels_start:]

    level_blocks = []
    i = 0
    while True:
        idx = levels_section.find("Level(", i)
        if idx == -1:
            break
        depth = 0
        j = idx
        start = idx
        while j < len(levels_section):
            c = levels_section[j]
            if c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0:
                    level_blocks.append(levels_section[start:j+1])
                    i = j + 1
                    break
            j += 1
        else:
            break

    all_levels = []
    for level_idx, block in enumerate(level_blocks):
        walls = set()
        player = None
        rotation_pickups = []
        color_pickups = []
        shape_pickups = []
        goals = []
        step_refills = []

        pattern = r'sprites\["([^"]+)"\]\.clone\(\)\.set_position\((\d+),\s*(\d+)\)'
        for m in re.finditer(pattern, block):
            name = m.group(1)
            x = int(m.group(2))
            y = int(m.group(3))

            # Only ihdgageizm-tagged sprites are walls
            if name in ("ihdgageizm", "fesygzfqui", "krdypjjivz", "mxfhnkdzvf", "ubyunwkbpx"):
                walls.add((x, y, name))
            elif name == "sfqyzhzkij":
                player = (x, y)
            elif name == "rhsxkxzdjz":
                rotation_pickups.append((x, y))
            elif name == "soyhouuebz":
                color_pickups.append((x, y))
            elif name in ("ttfwljgohq", "mkjdaccuuf"):
                shape_pickups.append((x, y))
            elif name == "rjlbuycveu":
                goals.append((x, y))
            elif name == "npxgalaybz":
                step_refills.append((x, y))

        # Parse data fields
        step_counter_m = re.search(r'"StepCounter":\s*(\d+)', block)
        steps_decrement_m = re.search(r'"StepsDecrement":\s*(\d+)', block)
        goal_color_m = re.search(r'"GoalColor":\s*(\[[\d, ]+\]|\d+)', block)
        goal_rotation_m = re.search(r'"GoalRotation":\s*(\[[\d, ]+\]|\d+)', block)
        start_color_m = re.search(r'"StartColor":\s*(\d+)', block)
        start_rotation_m = re.search(r'"StartRotation":\s*(\d+)', block)
        start_shape_m = re.search(r'"StartShape":\s*(\d+)', block)
        kvynsvxbpi_m = re.search(r'"kvynsvxbpi":\s*(\[[\d, ]+\]|\d+)', block)

        step_counter = int(step_counter_m.group(1)) if step_counter_m else 0
        steps_decrement = int(steps_decrement_m.group(1)) if steps_decrement_m else 2

        def parse_val(m):
            if not m:
                return None
            s = m.group(1).strip()
            if s.startswith('['):
                return [int(v.strip()) for v in s[1:-1].split(',')]
            return int(s)

        goal_color = parse_val(goal_color_m)
        goal_rotation = parse_val(goal_rotation_m)
        start_color = int(start_color_m.group(1)) if start_color_m else 12
        start_rotation = int(start_rotation_m.group(1)) if start_rotation_m else 0
        start_shape = int(start_shape_m.group(1)) if start_shape_m else 0
        kvynsvxbpi = parse_val(kvynsvxbpi_m)

        all_levels.append({
            "index": level_idx,
            "walls": walls,
            "player": player,
            "rotation_pickups": rotation_pickups,
            "color_pickups": color_pickups,
            "shape_pickups": shape_pickups,
            "goals": goals,
            "step_refills": step_refills,
            "step_counter": step_counter,
            "steps_decrement": steps_decrement,
            "goal_color": goal_color if isinstance(goal_color, list) else ([goal_color] if goal_color is not None else []),
            "goal_rotation": goal_rotation if isinstance(goal_rotation, list) else ([goal_rotation] if goal_rotation is not None else []),
            "start_color": start_color,
            "start_rotation": start_rotation,
            "start_shape": start_shape,
            "kvynsvxbpi": kvynsvxbpi if isinstance(kvynsvxbpi, list) else ([kvynsvxbpi] if kvynsvxbpi is not None else []),
        })

    return all_levels


# =============================================================================
# GRID HELPERS
# =============================================================================

def get_wall_cells(walls):
    """
    Convert wall sprite positions to set of blocked grid cells.
    ONLY ihdgageizm-tagged sprites block. Boundary sprites do NOT block.
    Wall at (wx,wy) blocks player at (px,py) if px<=wx<px+5 AND py<=wy<py+5.
    """
    blocked = set()
    for (wx, wy, name) in walls:
        for px in GRID_X:
            if px <= wx < px + 5:
                for py in GRID_Y:
                    if py <= wy < py + 5:
                        blocked.add((px, py))
    return blocked


def get_pickup_grid_cells(pickup_pos):
    """Find all grid cells where the player would trigger pickup at (rx, ry)."""
    rx, ry = pickup_pos
    cells = []
    for px in GRID_X:
        if px <= rx < px + 5:
            for py in GRID_Y:
                if py <= ry < py + 5:
                    cells.append((px, py))
    return cells


def get_refill_map(step_refills):
    """Map grid cell -> refill sprite position. Multiple cells can trigger same refill."""
    refill_map = {}  # grid_cell -> refill_sprite_pos
    for (rx, ry) in step_refills:
        for px in GRID_X:
            if px <= rx < px + 5:
                for py in GRID_Y:
                    if py <= ry < py + 5:
                        refill_map[(px, py)] = (rx, ry)
    return refill_map


# =============================================================================
# SIMPLE BFS (no state, just pathfinding)
# =============================================================================

def bfs(start, goal, blocked):
    """BFS from start to goal avoiding blocked cells. Returns list of actions or None."""
    if start == goal:
        return []
    queue = deque([(start, [])])
    visited = {start}
    while queue:
        (cx, cy), path = queue.popleft()
        for action, (dx, dy) in ACTION_DELTAS.items():
            nx, ny = cx + dx, cy + dy
            if nx not in GRID_X_SET or ny not in GRID_Y_SET:
                continue
            if (nx, ny) in blocked or (nx, ny) in visited:
                continue
            new_path = path + [action]
            if (nx, ny) == goal:
                return new_path
            visited.add((nx, ny))
            queue.append(((nx, ny), new_path))
    return None


def bfs_distance(start, goal, blocked):
    """Return BFS distance or None if unreachable."""
    path = bfs(start, goal, blocked)
    return len(path) if path is not None else None


def find_adjacent_cells(pos, blocked):
    """Find all non-blocked grid-aligned adjacent cells."""
    cx, cy = pos
    result = []
    for action, (dx, dy) in ACTION_DELTAS.items():
        nx, ny = cx + dx, cy + dy
        if nx in GRID_X_SET and ny in GRID_Y_SET and (nx, ny) not in blocked:
            result.append(((nx, ny), action))
    return result


# =============================================================================
# STEP COUNTER SIMULATION
# =============================================================================

def simulate_counter(actions, start_pos, step_counter, steps_decrement, refill_map):
    """
    Simulate step counter along action sequence.
    Key: on a refill step, counter resets to step_counter and is NOT decremented.
    On non-refill steps, counter is decremented by steps_decrement.
    Life lost when counter < 0 after decrement.
    Returns (life_lost_count, final_counter, refill_count).
    """
    counter = step_counter
    pos = start_pos
    remaining_refills = dict(refill_map)
    life_losses = 0
    refills_collected = 0
    for act in actions:
        dx, dy = ACTION_DELTAS[act]
        pos = (pos[0] + dx, pos[1] + dy)
        if pos in remaining_refills:
            counter = step_counter  # reset; no decrement on refill step
            del remaining_refills[pos]
            refills_collected += 1
        else:
            counter -= steps_decrement
            if counter < 0:
                life_losses += 1
    return life_losses, counter, refills_collected


# =============================================================================
# WAYPOINT ROUTING WITH REFILL INSERTION
# =============================================================================

def make_oscillation(pickup_cell, blocked, n_times):
    """
    Build actions to visit pickup_cell n_times total.
    Assumes player is already AT pickup_cell (1st visit).
    Returns (actions, final_pos=pickup_cell).
    """
    if n_times <= 1:
        return [], pickup_cell
    adj = find_adjacent_cells(pickup_cell, blocked)
    if not adj:
        return [], pickup_cell
    (adj_pos, away_action) = adj[0]
    back_action = OPPOSITES[away_action]
    actions = []
    for _ in range(n_times - 1):
        actions.append(away_action)
        actions.append(back_action)
    return actions, pickup_cell


def route_waypoints(start, waypoints, blocked):
    """
    Route through ordered waypoints. Each waypoint is (cell, n_visits).
    Returns (actions, final_pos) or (None, None) if any segment fails.
    """
    all_actions = []
    pos = start
    for (cell, n_visits) in waypoints:
        path = bfs(pos, cell, blocked)
        if path is None:
            return None, None
        all_actions.extend(path)
        pos = cell
        if n_visits > 1:
            osc, pos = make_oscillation(cell, blocked, n_visits)
            all_actions.extend(osc)
    return all_actions, pos


def insert_refills_greedy(start, actions, step_counter, steps_decrement, refill_map, blocked):
    """
    Given a base action sequence, check if step counter runs out.
    If so, try to insert refill detours at optimal points.
    Returns improved action sequence or original if no improvement needed/possible.
    """
    life_losses, _, _ = simulate_counter(actions, start, step_counter, steps_decrement, refill_map)
    if life_losses == 0:
        return actions

    # Find all positions along the path and where the counter goes negative
    counter = step_counter
    pos = start
    remaining = dict(refill_map)
    positions = [pos]
    for act in actions:
        dx, dy = ACTION_DELTAS[act]
        pos = (pos[0] + dx, pos[1] + dy)
        if pos in remaining:
            counter = step_counter
            del remaining[pos]
        counter -= steps_decrement
        positions.append(pos)

    # Can't easily fix -- need full re-routing
    return None


def solve_level_segmented(lv, verbose=True):
    """
    Solve a level using segment-by-segment BFS with refill insertion.
    Handles single-goal and multi-goal levels.

    Strategy:
    1. Determine required pickup visits for each goal
    2. Plan waypoint order
    3. Insert refills between segments to stay within budget
    4. Use BFS for each segment
    """
    player = lv['player']
    goals = lv['goals']
    step_counter = lv['step_counter']
    steps_decrement = lv['steps_decrement']
    walls = lv['walls']
    blocked = get_wall_cells(walls)
    refill_map = get_refill_map(lv['step_refills'])

    budget = step_counter // steps_decrement  # moves before counter goes negative

    # Parse goal requirements
    goal_colors = lv['goal_color']       # list of color values
    goal_rotations = lv['goal_rotation'] # list of rotation values
    goal_shapes = lv['kvynsvxbpi']       # list of shape indices

    n_goals = len(goals)

    # Current state
    color_idx = COLORS.index(lv['start_color'])
    rot_idx = ROTATIONS.index(lv['start_rotation'])
    shape_idx = lv['start_shape']

    # Find pickup cells
    color_cell = None
    if lv['color_pickups']:
        cp = lv['color_pickups'][0]
        cells = get_pickup_grid_cells(cp)
        color_cell = next((c for c in cells if c not in blocked), cells[0] if cells else None)

    rot_cell = None
    if lv['rotation_pickups']:
        rp = lv['rotation_pickups'][0]
        cells = get_pickup_grid_cells(rp)
        rot_cell = next((c for c in cells if c not in blocked), cells[0] if cells else None)

    shape_cell = None
    if lv['shape_pickups']:
        sp = lv['shape_pickups'][0]
        cells = get_pickup_grid_cells(sp)
        shape_cell = next((c for c in cells if c not in blocked), cells[0] if cells else None)

    # Refill cells
    refill_cells = sorted(refill_map.keys())

    if verbose:
        print(f"  Player: {player}, Goals: {goals}")
        print(f"  Color pickup: {color_cell}, Rotation pickup: {rot_cell}, Shape pickup: {shape_cell}")
        print(f"  Refill cells: {refill_cells}")
        print(f"  Budget: {step_counter}/{steps_decrement} = {budget} moves per period")
        print(f"  Start state: color_idx={color_idx}, rot_idx={rot_idx}, shape_idx={shape_idx}")
        print(f"  Goal colors: {goal_colors}, Goal rotations: {goal_rotations}, Goal shapes: {goal_shapes}")

    all_actions = []
    pos = player
    used_refills = set()

    for gi in range(n_goals):
        goal = goals[gi]
        target_color_idx = COLORS.index(goal_colors[gi])
        target_rot_idx = ROTATIONS.index(goal_rotations[gi])
        target_shape_idx = goal_shapes[gi]

        n_color = (target_color_idx - color_idx) % 4
        n_rot = (target_rot_idx - rot_idx) % 4
        n_shape = (target_shape_idx - shape_idx) % N_SHAPES

        if verbose:
            print(f"\n  Goal {gi}: {goal}")
            print(f"    Need: color={n_color} visits, rot={n_rot} visits, shape={n_shape} visits")

        # Build waypoint list for this goal phase
        # Order: shape -> color -> rotation -> goal (can be optimized per level)
        pickup_waypoints = []
        if n_shape > 0 and shape_cell:
            pickup_waypoints.append(('shape', shape_cell, n_shape))
        if n_color > 0 and color_cell:
            pickup_waypoints.append(('color', color_cell, n_color))
        if n_rot > 0 and rot_cell:
            pickup_waypoints.append(('rot', rot_cell, n_rot))

        # Try all orderings of pickups to find shortest total path
        best_actions = None
        best_len = float('inf')

        orderings = list(permutations(pickup_waypoints)) if pickup_waypoints else [()]
        # Limit permutations for performance
        if len(orderings) > 24:
            orderings = orderings[:24]

        for ordering in orderings:
            # For each ordering, try inserting refills
            candidate = try_route_with_refills(
                pos, list(ordering), goal, blocked, refill_cells,
                refill_map, used_refills, step_counter, steps_decrement,
                len(all_actions), player, all_actions
            )
            if candidate is not None and len(candidate) < best_len:
                best_actions = candidate
                best_len = len(candidate)

        if best_actions is None:
            if verbose:
                print(f"    FAILED to find route for goal {gi}")
            return None, None

        # Simulate to track refills used
        sim_pos = pos
        sim_remaining = {k: v for k, v in refill_map.items() if k not in used_refills}
        for act in best_actions:
            dx, dy = ACTION_DELTAS[act]
            sim_pos = (sim_pos[0] + dx, sim_pos[1] + dy)
            if sim_pos in sim_remaining:
                used_refills.add(sim_pos)
                del sim_remaining[sim_pos]

        all_actions.extend(best_actions)
        pos = goal  # Should be at goal after best_actions

        # Update state
        color_idx = target_color_idx
        rot_idx = target_rot_idx
        shape_idx = target_shape_idx

    # Final validation
    sim_pos = player
    for act in all_actions:
        dx, dy = ACTION_DELTAS[act]
        sim_pos = (sim_pos[0] + dx, sim_pos[1] + dy)

    life_losses, final_counter, refills_collected = simulate_counter(
        all_actions, player, step_counter, steps_decrement, refill_map
    )

    if verbose:
        print(f"\n  Total actions: {len(all_actions)}")
        print(f"  Final position: {sim_pos}")
        print(f"  Life losses: {life_losses}, Refills collected: {refills_collected}")
        if life_losses == 0:
            print(f"  Counter OK. Final: {final_counter}")

    return all_actions, life_losses


def try_route_with_refills(start_pos, pickup_ordering, goal, blocked, refill_cells,
                           refill_map, used_refills, step_counter, steps_decrement,
                           actions_before_count, orig_start, actions_before):
    """
    Try to route through pickups in given order, then to goal.
    Insert refills as needed to stay within step budget.
    Returns action list for this phase, or None if impossible.
    """
    # Build flat waypoint list: [(cell, n_visits), ...]
    flat = []
    for (ptype, cell, n_visits) in pickup_ordering:
        flat.append((cell, n_visits))
    flat.append((goal, 1))

    # First try without refills
    actions, final = route_waypoints(start_pos, flat, blocked)
    if actions is None:
        return None

    # Check step counter
    full_actions = actions_before + actions
    life_losses, _, _ = simulate_counter(full_actions, orig_start, step_counter, steps_decrement, refill_map)
    if life_losses == 0:
        return actions

    # Need to insert refills. Use greedy approach: find where counter goes negative,
    # insert a refill detour before that point.
    return try_with_refill_insertion(
        start_pos, flat, blocked, refill_cells, refill_map, used_refills,
        step_counter, steps_decrement, actions_before, orig_start
    )


def try_with_refill_insertion(start_pos, flat_waypoints, blocked, refill_cells,
                               refill_map, used_refills, step_counter, steps_decrement,
                               actions_before, orig_start):
    """
    Try all possible refill insertion points between waypoints.
    For each segment, optionally route through a refill.
    """
    available_refills = [rc for rc in refill_cells if rc not in used_refills]

    # Generate segments: each is (from_pos, to_cell, n_visits_at_to)
    segments = []
    prev = start_pos
    for (cell, n_visits) in flat_waypoints:
        segments.append((prev, cell, n_visits))
        prev = cell

    n_segments = len(segments)

    # Try inserting 0, 1, or 2 refills per segment
    # Use recursive/iterative approach with pruning
    best = _try_refill_combos(segments, 0, start_pos, blocked, available_refills,
                               set(), step_counter, steps_decrement,
                               actions_before, orig_start, refill_map)
    return best


def _try_refill_combos(segments, seg_idx, pos, blocked, available_refills,
                        used_in_this_route, step_counter, steps_decrement,
                        actions_before, orig_start, refill_map):
    """
    Recursively try refill insertion for each segment.
    Returns best action list or None.
    """
    if seg_idx >= len(segments):
        return []

    (from_pos, to_cell, n_visits) = segments[seg_idx]

    # Option 1: go directly to target
    options = []

    # Direct route
    direct = _build_segment(from_pos, to_cell, n_visits, blocked)
    if direct is not None:
        rest = _try_refill_combos(segments, seg_idx + 1, to_cell, blocked,
                                   available_refills, used_in_this_route,
                                   step_counter, steps_decrement,
                                   actions_before + direct, orig_start, refill_map)
        if rest is not None:
            candidate = direct + rest
            ll, _, _ = simulate_counter(actions_before + candidate, orig_start,
                                        step_counter, steps_decrement, refill_map)
            if ll == 0:
                options.append(candidate)

    # Option 2: go via a refill first
    for rc in available_refills:
        if rc in used_in_this_route:
            continue
        path1 = bfs(from_pos, rc, blocked)
        if path1 is None:
            continue
        path2 = bfs(rc, to_cell, blocked)
        if path2 is None:
            continue
        via_refill = path1 + path2
        # Add oscillation at target
        if n_visits > 1:
            osc, _ = make_oscillation(to_cell, blocked, n_visits)
            via_refill = via_refill + osc

        new_used = used_in_this_route | {rc}
        new_available = [r for r in available_refills if r not in new_used]
        rest = _try_refill_combos(segments, seg_idx + 1, to_cell, blocked,
                                   new_available, new_used,
                                   step_counter, steps_decrement,
                                   actions_before + via_refill, orig_start, refill_map)
        if rest is not None:
            candidate = via_refill + rest
            ll, _, _ = simulate_counter(actions_before + candidate, orig_start,
                                        step_counter, steps_decrement, refill_map)
            if ll == 0:
                options.append(candidate)

    if not options:
        return None
    return min(options, key=len)


def _build_segment(from_pos, to_cell, n_visits, blocked):
    """Build segment: BFS to cell + oscillation for n_visits."""
    path = bfs(from_pos, to_cell, blocked)
    if path is None:
        return None
    if n_visits > 1:
        osc, _ = make_oscillation(to_cell, blocked, n_visits)
        path = path + osc
    return path


# =============================================================================
# FULL STATE BFS (for complex levels)
# =============================================================================

def solve_level_full_bfs(lv, verbose=True):
    """
    Full state-space BFS. State = (pos, color_idx, rot_idx, shape_idx, collected_refills, goals_done).
    Used as fallback for levels where segment approach fails.
    """
    player = lv['player']
    goals = lv['goals']
    step_counter = lv['step_counter']
    steps_decrement = lv['steps_decrement']
    walls = lv['walls']
    blocked = get_wall_cells(walls)
    refill_map = get_refill_map(lv['step_refills'])

    goal_colors = lv['goal_color']
    goal_rotations = lv['goal_rotation']
    goal_shapes = lv['kvynsvxbpi']

    color_idx = COLORS.index(lv['start_color'])
    rot_idx = ROTATIONS.index(lv['start_rotation'])
    shape_idx = lv['start_shape']

    # Find pickup cells -> pickup type
    pickup_at = {}  # grid_cell -> list of ('color'|'rot'|'shape')
    for cp in lv['color_pickups']:
        for cell in get_pickup_grid_cells(cp):
            pickup_at.setdefault(cell, []).append('color')
    for rp in lv['rotation_pickups']:
        for cell in get_pickup_grid_cells(rp):
            pickup_at.setdefault(cell, []).append('rot')
    for sp in lv['shape_pickups']:
        for cell in get_pickup_grid_cells(sp):
            pickup_at.setdefault(cell, []).append('shape')

    # Refill cells -> refill_id (index into step_refills list)
    refill_at = {}  # grid_cell -> refill_id
    for i, (rx, ry) in enumerate(lv['step_refills']):
        for cell in get_pickup_grid_cells((rx, ry)):
            refill_at[cell] = i

    n_refills = len(lv['step_refills'])
    n_goals = len(goals)
    budget = step_counter // steps_decrement

    # Goal check function
    def goals_match(ci, ri, si, goals_done_mask):
        """Check which goals the player could enter with current properties."""
        matching = 0
        for gi in range(n_goals):
            if goals_done_mask & (1 << gi):
                continue
            if (ci == COLORS.index(goal_colors[gi]) and
                ri == ROTATIONS.index(goal_rotations[gi]) and
                si == goal_shapes[gi]):
                matching |= (1 << gi)
        return matching

    # State: (x, y, color_idx, rot_idx, shape_idx, refills_collected_bitmask, goals_done_bitmask)
    # Counter is derived from steps since last refill/start

    # BFS with step counter integrated
    # State: (x, y, ci, ri, si, refills_mask, goals_mask, counter)
    # This could be huge. Prune by: counter can be reset to step_counter at refills.
    # Max counter value = step_counter. Minimum meaningful = 0.
    # Counter states: step_counter // steps_decrement + 1 values (but actually continuous)

    # Simplify: track counter as integer
    all_goals_mask = (1 << n_goals) - 1

    start_state = (player[0], player[1], color_idx, rot_idx, shape_idx,
                   0, 0, step_counter)
    # visited: without counter (allow revisit with higher counter)
    # Actually we need counter in state for proper BFS
    # But state space is: 12*12 * 4 * 4 * 6 * 2^n_refills * 2^n_goals * counter_range
    # counter_range = step_counter // steps_decrement + 1 (at most ~22 values)

    queue = deque([(start_state, [])])
    visited = {}  # (x,y,ci,ri,si,refills,goals) -> best counter seen
    visited_key = (player[0], player[1], color_idx, rot_idx, shape_idx, 0, 0)
    visited[visited_key] = step_counter

    if verbose:
        print(f"  Full BFS: {n_refills} refills, {n_goals} goals")

    while queue:
        state, path = queue.popleft()
        x, y, ci, ri, si, ref_mask, goal_mask, counter = state

        if goal_mask == all_goals_mask:
            if verbose:
                print(f"  Found solution: {len(path)} actions")
            return path, 0

        for action, (dx, dy) in ACTION_DELTAS.items():
            nx, ny = x + dx, y + dy
            if nx not in GRID_X_SET or ny not in GRID_Y_SET:
                continue
            if (nx, ny) in blocked:
                continue

            new_ci, new_ri, new_si = ci, ri, si
            new_ref_mask = ref_mask
            new_goal_mask = goal_mask
            new_counter = counter
            move_blocked = False

            # Check if it's a goal cell
            for gi in range(n_goals):
                if new_goal_mask & (1 << gi):
                    continue
                if (nx, ny) == goals[gi]:
                    # Check if properties match
                    if (new_ci == COLORS.index(goal_colors[gi]) and
                        new_ri == ROTATIONS.index(goal_rotations[gi]) and
                        new_si == goal_shapes[gi]):
                        new_goal_mask |= (1 << gi)
                    else:
                        move_blocked = True

            if move_blocked:
                continue

            # Check refill
            collected_refill = False
            if (nx, ny) in refill_at:
                rid = refill_at[(nx, ny)]
                if not (new_ref_mask & (1 << rid)):
                    new_ref_mask |= (1 << rid)
                    new_counter = step_counter  # reset; no decrement on refill step
                    collected_refill = True

            # Check pickups
            if (nx, ny) in pickup_at:
                for ptype in pickup_at[(nx, ny)]:
                    if ptype == 'color':
                        new_ci = (new_ci + 1) % 4
                    elif ptype == 'rot':
                        new_ri = (new_ri + 1) % 4
                    elif ptype == 'shape':
                        new_si = (new_si + 1) % N_SHAPES

            # Decrement counter (only if no refill collected this step)
            if not collected_refill:
                new_counter -= steps_decrement
                if new_counter < 0:
                    continue  # life lost, skip

            # Check visited
            vkey = (nx, ny, new_ci, new_ri, new_si, new_ref_mask, new_goal_mask)
            if vkey in visited and visited[vkey] >= new_counter:
                continue
            visited[vkey] = new_counter

            new_state = (nx, ny, new_ci, new_ri, new_si, new_ref_mask, new_goal_mask, new_counter)
            queue.append((new_state, path + [action]))

    if verbose:
        print("  Full BFS: NO SOLUTION FOUND")
    return None, None


# =============================================================================
# MAIN SOLVER
# =============================================================================

def solve_level(lv, verbose=True):
    """Solve a single level. Try segmented approach first, fall back to full BFS."""
    level_idx = lv['index']
    print(f"\n{'='*60}")
    print(f"LEVEL {level_idx + 1} (index {level_idx})")
    print(f"{'='*60}")

    # Try segmented approach first
    actions, losses = solve_level_segmented(lv, verbose)
    if actions is not None and losses == 0:
        print(f"  [Segmented solver] SUCCESS: {len(actions)} actions")
        return actions

    print(f"  [Segmented solver] failed or has life losses, trying full BFS...")

    # Fall back to full BFS
    actions, losses = solve_level_full_bfs(lv, verbose)
    if actions is not None:
        if losses == 0:
            print(f"  [Full BFS] SUCCESS: {len(actions)} actions")
            return actions
        else:
            print(f"  [Full BFS] returned with {losses} life losses")
            return actions

    print(f"  FAILED to solve level {level_idx + 1}")
    return None


def main():
    ls20_file = "/Users/kairos/Projects/arc-see/environment_files/ls20/9607627b/ls20.py"
    print("Parsing LS20 levels...")
    levels = parse_levels(ls20_file)
    print(f"Found {len(levels)} levels\n")

    results = {}
    for i in range(len(levels)):
        lv = levels[i]
        actions = solve_level(lv, verbose=True)
        results[i] = actions

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY - Action Sequences for All Levels")
    print("=" * 60)
    all_success = True
    for i in range(len(levels)):
        actions = results[i]
        if actions:
            # Verify
            lv = levels[i]
            refill_map = get_refill_map(lv['step_refills'])
            ll, fc, rc = simulate_counter(actions, lv['player'], lv['step_counter'],
                                          lv['steps_decrement'], refill_map)
            status = "OK" if ll == 0 else f"LIFE LOSSES: {ll}"
            print(f"\nLevel {i+1} (index {i}): {len(actions)} actions [{status}]")
            print(" ".join(actions))
            if ll > 0:
                all_success = False
        else:
            print(f"\nLevel {i+1} (index {i}): FAILED")
            all_success = False

    if all_success:
        print("\n*** ALL LEVELS SOLVED SUCCESSFULLY ***")
    else:
        print("\n*** SOME LEVELS FAILED ***")


if __name__ == "__main__":
    main()
