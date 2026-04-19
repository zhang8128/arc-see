"""KA59 Level 7 solver — A* with checkpoint replay and aggressive pruning.

The standard deepcopy BFS is ~50 iter/sec which is too slow for depth 200+.
This solver uses:
1. Checkpoint every N depths: store deepcopy'd games at intervals, queue holds
   only (checkpoint_key, actions_since_checkpoint) tuples.
2. A* with Manhattan distance heuristic to targets.
3. Aggressive enemy pruning: drop states where enemy drifts too far from target.
4. Click optimization: only generate click actions when useful.

Targets:
  P0 cisjjwiopp -> (27, 45)
  P1 sfcitxooao -> (24, 24)
  Enemy yxphjztrgf -> (9, 36)

Win condition: g._current_level_index > 6

Usage:
  uv run python solvers/ka59_l7_solver.py
"""
import sys
import copy
import time
import heapq
import importlib.util
from arcengine import GameAction, ActionInput

sys.stdout.reconfigure(line_buffering=True)

# ---------------------------------------------------------------------------
# Load game module
# ---------------------------------------------------------------------------
spec = importlib.util.spec_from_file_location(
    'ka59', 'environment_files/ka59/9f096b4a/ka59.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------
ACT_U = ActionInput(id=GameAction.ACTION1, data={})
ACT_D = ActionInput(id=GameAction.ACTION2, data={})
ACT_L = ActionInput(id=GameAction.ACTION3, data={})
ACT_R = ActionInput(id=GameAction.ACTION4, data={})
DIR_ACTIONS = [ACT_U, ACT_D, ACT_L, ACT_R]
DIR_NAMES = ['U', 'D', 'L', 'R']

LEVEL_IDX = 6
CHECKPOINT_INTERVAL = 10
MAX_DEPTH = 350
MAX_ITERS = 10_000_000

# Targets
P0_TARGET = (27, 45)  # cisjjwiopp
P1_TARGET = (24, 24)  # sfcitxooao
ENEMY_TARGET = (9, 36)  # yxphjztrgf

# Enemy pruning: disabled — enemy may need to move in unexpected directions
ENEMY_Y_SLACK = 999


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def click_action(g, sprite):
    """Create a click action targeting a sprite's center."""
    gx = sprite.x + sprite.width // 2
    gy = sprite.y + sprite.height // 2
    sc, ox, oy = g.camera._calculate_scale_and_offset()
    return ActionInput(id=GameAction.ACTION6,
                       data={'x': int(gx * sc + ox), 'y': int(gy * sc + oy)})


def get_actions(g, use_clicks=True):
    """Get available actions. Indices 0-3=UDLR, 4+=clicks."""
    actions = list(DIR_ACTIONS)
    if use_clicks:
        pieces = sorted(g.current_level.get_sprites_by_tag('xlfuqjygey'),
                        key=lambda s: s.name)
        sel = g.ascpmvdpwj
        for s in pieces:
            if s is not sel:
                actions.append(click_action(g, s))
    return actions


def resolve_action(g, action_idx):
    """Resolve an action index to ActionInput for the current game state."""
    if action_idx < 4:
        return DIR_ACTIONS[action_idx]
    pieces = sorted(g.current_level.get_sprites_by_tag('xlfuqjygey'),
                    key=lambda s: s.name)
    sel = g.ascpmvdpwj
    non_sel = [s for s in pieces if s is not sel]
    click_idx = action_idx - 4
    if click_idx < len(non_sel):
        return click_action(g, non_sel[click_idx])
    return DIR_ACTIONS[0]


def get_state(g):
    """Compact state hash."""
    pieces = sorted(
        g.current_level.get_sprites_by_tag('xlfuqjygey'),
        key=lambda s: s.name)
    enemies = sorted(
        g.current_level.get_sprites_by_tag('nnckfubbhi'),
        key=lambda s: s.name)
    sel = g.ascpmvdpwj

    parts = []
    for s in pieces:
        parts.append(s.x)
        parts.append(s.y)
        parts.append(1 if s is sel else 0)
    for s in enemies:
        parts.append(s.x)
        parts.append(s.y)

    z = 0
    if hasattr(g, 'zhcrzgpwcp') and g.zhcrzgpwcp:
        z = tuple(sorted((k.name, v) for k, v in g.zhcrzgpwcp.items()))

    m = getattr(g, 'msbtawvatm', 0)
    return (tuple(parts), z, m)


def get_positions(g):
    """Extract piece and enemy positions for heuristic/pruning."""
    pieces = sorted(
        g.current_level.get_sprites_by_tag('xlfuqjygey'),
        key=lambda s: s.name)
    enemies = sorted(
        g.current_level.get_sprites_by_tag('nnckfubbhi'),
        key=lambda s: s.name)

    p0 = (pieces[0].x, pieces[0].y) if len(pieces) > 0 else None
    p1 = (pieces[1].x, pieces[1].y) if len(pieces) > 1 else None
    e0 = (enemies[0].x, enemies[0].y) if len(enemies) > 0 else None
    return p0, p1, e0


def manhattan(a, b):
    """Manhattan distance between two (x, y) tuples."""
    if a is None or b is None:
        return 0
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def heuristic(g):
    """Heuristic: enemy distance weighted heavily (enemy push is the bottleneck).
    Piece routing is easy (10-20 acts), enemy push requires complex multi-phase path."""
    p0, p1, e0 = get_positions(g)
    h = 0
    h += manhattan(p0, P0_TARGET)
    h += manhattan(p1, P1_TARGET)
    # Weight enemy distance 5x — finding the enemy push path is the hard part
    h += manhattan(e0, ENEMY_TARGET) * 5
    return h


def is_won(g):
    return g._current_level_index > LEVEL_IDX


def action_name(a):
    if a.id == GameAction.ACTION6:
        return f"C({a.data.get('x')},{a.data.get('y')})"
    try:
        idx = [GameAction.ACTION1, GameAction.ACTION2,
               GameAction.ACTION3, GameAction.ACTION4].index(a.id)
        return DIR_NAMES[idx]
    except ValueError:
        return str(a.id)


def replay_path(level_idx, indices):
    """Replay action indices on a fresh game and return game + action list."""
    g = mod.Ka59()
    g.set_level(level_idx)
    actions = []
    for ai in indices:
        act = resolve_action(g, ai)
        actions.append(act)
        g.perform_action(act)
    return g, actions


# ---------------------------------------------------------------------------
# A* Solver with checkpoints
# ---------------------------------------------------------------------------

def solve():
    g0 = mod.Ka59()
    g0.set_level(LEVEL_IDX)

    # Describe initial state
    pieces = sorted(g0.current_level.get_sprites_by_tag('xlfuqjygey'),
                    key=lambda s: s.name)
    enemies = sorted(g0.current_level.get_sprites_by_tag('nnckfubbhi'),
                     key=lambda s: s.name)
    sel = g0.ascpmvdpwj

    print(f"KA59 Level 7 A* Solver")
    print(f"{'='*60}")
    print(f"Pieces:")
    for s in pieces:
        mark = ' [SEL]' if s is sel else ''
        print(f"  {s.name}: ({s.x},{s.y}){mark}")
    print(f"Enemies:")
    for s in enemies:
        print(f"  {s.name}: ({s.x},{s.y})")
    print(f"Targets: P0->(27,45) P1->(24,24) Enemy->(9,36)")
    print(f"Max depth: {MAX_DEPTH}, Checkpoint interval: {CHECKPOINT_INTERVAL}")
    print(f"{'='*60}")

    start_state = get_state(g0)
    h0 = heuristic(g0)
    print(f"Initial heuristic: {h0}")

    # Priority queue: (f_score, tie_breaker, path_tuple)
    # f_score = depth + heuristic
    counter = 0
    pq = []
    heapq.heappush(pq, (h0, counter, ()))
    counter += 1

    visited = {start_state}

    # Checkpoints: path_tuple -> deepcopy'd game
    checkpoints = {(): copy.deepcopy(g0)}

    # Track best enemy y seen (enemy needs to move from y=9 toward y=36)
    best_enemy_y = 9

    iters = 0
    start_time = time.time()
    last_report = start_time
    max_depth_seen = 0
    best_h = h0

    while pq:
        f_score, _, path = heapq.heappop(pq)
        depth = len(path)
        iters += 1

        if depth > max_depth_seen:
            max_depth_seen = depth

        now = time.time()
        if iters % 10000 == 0 or now - last_report >= 15.0:
            elapsed = now - start_time
            rate = iters / elapsed if elapsed > 0 else 0
            print(f"  iter={iters:,} pq={len(pq):,} d={depth} "
                  f"maxd={max_depth_seen} f={f_score} best_h={best_h} "
                  f"v={len(visited):,} ckpt={len(checkpoints)} "
                  f"best_ey={best_enemy_y} rate={rate:.0f}/s "
                  f"time={elapsed:.0f}s")
            last_report = now

        if iters > MAX_ITERS:
            elapsed = time.time() - start_time
            print(f"HIT MAX ITERS ({MAX_ITERS:,}) after {elapsed:.0f}s")
            return None

        if depth >= MAX_DEPTH:
            continue

        # Reconstruct game from nearest checkpoint
        ci = CHECKPOINT_INTERVAL
        ckpt_depth = (depth // ci) * ci
        ckpt_key = path[:ckpt_depth]
        ckpt = checkpoints.get(ckpt_key)
        if ckpt is not None:
            g = copy.deepcopy(ckpt)
            for ai_idx in range(ckpt_depth, depth):
                act = resolve_action(g, path[ai_idx])
                g.perform_action(act)
        else:
            # Fallback: full replay
            g = mod.Ka59()
            g.set_level(LEVEL_IDX)
            for ai_idx in range(depth):
                act = resolve_action(g, path[ai_idx])
                g.perform_action(act)

        # Check win
        if is_won(g):
            elapsed = time.time() - start_time
            _, actions = replay_path(LEVEL_IDX, path)
            names = ' '.join(action_name(a) for a in actions)
            print(f"\nSOLVED! {depth} actions ({iters:,} iters, "
                  f"{len(visited):,} states, {elapsed:.1f}s)")
            print(f"Path: {names}")
            # Verify
            g_verify = mod.Ka59()
            g_verify.set_level(LEVEL_IDX)
            for a in actions:
                g_verify.perform_action(a)
            print(f"Verification: {'PASS' if g_verify._current_level_index > LEVEL_IDX else 'FAIL'}")
            return actions

        # Expand children
        all_actions = get_actions(g, use_clicks=True)
        n_actions = len(all_actions)

        for i in range(n_actions):
            new_path = path + (i,)
            new_depth = depth + 1

            # Apply action
            if i < n_actions - 1:
                g2 = copy.deepcopy(g)
            else:
                g2 = g  # reuse parent for last child

            g2.perform_action(all_actions[i])

            # Check immediate win
            if is_won(g2):
                elapsed = time.time() - start_time
                _, actions = replay_path(LEVEL_IDX, new_path)
                names = ' '.join(action_name(a) for a in actions)
                print(f"\nSOLVED! {new_depth} actions ({iters:,} iters, "
                      f"{len(visited):,} states, {elapsed:.1f}s)")
                print(f"Path: {names}")
                # Verify
                g_verify = mod.Ka59()
                g_verify.set_level(LEVEL_IDX)
                for a in actions:
                    g_verify.perform_action(a)
                print(f"Verification: {'PASS' if g_verify._current_level_index > LEVEL_IDX else 'FAIL'}")
                return actions

            state = get_state(g2)
            if state in visited:
                continue

            # Enemy pruning: check enemy hasn't drifted too far back
            p0, p1, e0 = get_positions(g2)
            if e0 is not None:
                ey = e0[1]
                if ey < best_enemy_y - ENEMY_Y_SLACK:
                    continue  # prune: enemy went too far backward
                if ey > best_enemy_y:
                    best_enemy_y = ey
                    elapsed = time.time() - start_time
                    print(f"  ** enemy_y advanced to {ey} at d={new_depth} "
                          f"iter={iters:,} time={elapsed:.0f}s")

            visited.add(state)

            # Compute heuristic
            h = manhattan(p0, P0_TARGET) + manhattan(p1, P1_TARGET)
            if e0 is not None:
                h += manhattan(e0, ENEMY_TARGET)
            f = new_depth + h

            if h < best_h:
                best_h = h
                elapsed = time.time() - start_time
                print(f"  ** new best_h={h} f={f} d={new_depth} "
                      f"p0={p0} p1={p1} e={e0} "
                      f"iter={iters:,} time={elapsed:.0f}s")

            # Store checkpoint if at boundary
            if new_depth % ci == 0:
                if i == n_actions - 1:
                    checkpoints[new_path] = copy.deepcopy(g2)
                else:
                    checkpoints[new_path] = g2
                    # We already deepcopy'd g2 above, so it's safe to store

            heapq.heappush(pq, (f, counter, new_path))
            counter += 1

    elapsed = time.time() - start_time
    print(f"EXHAUSTED. v={len(visited):,} time={elapsed:.0f}s")
    return None


if __name__ == '__main__':
    print(f"Starting KA59 L7 solver...")
    result = solve()
    if result:
        print(f"\nFinal solution: {len(result)} actions")
    else:
        print("\nNo solution found.")
