"""KA59 BFS solver — checkpoint-based with optimized deepcopy.

Two BFS strategies:
1. CHECKPOINT: Store game snapshots at regular depth intervals. To expand
   a node, deepcopy nearest checkpoint and replay remaining actions. Saves
   memory vs storing game objects per node.
2. DEEPCOPY: Standard BFS storing deepcopy'd game objects per node. Simpler,
   faster per-iteration, but uses more memory.

State hash includes: piece positions, enemy positions, selection,
zhcrzgpwcp momentum, msbtawvatm counter.

Usage:
  uv run python solvers/ka59_pure_bfs.py 3        # L4 (level index 3)
  uv run python solvers/ka59_pure_bfs.py 3 60     # L4, max depth 60
  uv run python solvers/ka59_pure_bfs.py 6 350    # L7, max depth 350
  uv run python solvers/ka59_pure_bfs.py 4 --method deepcopy
"""
import sys
import copy
import time
import importlib.util
from collections import deque
from arcengine import GameAction, ActionInput

sys.stdout.reconfigure(line_buffering=True)

# Load game module
spec = importlib.util.spec_from_file_location(
    'ka59', 'environment_files/ka59/9f096b4a/ka59.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# Actions
ACT_U = ActionInput(id=GameAction.ACTION1, data={})
ACT_D = ActionInput(id=GameAction.ACTION2, data={})
ACT_L = ActionInput(id=GameAction.ACTION3, data={})
ACT_R = ActionInput(id=GameAction.ACTION4, data={})
DIR_ACTIONS = [ACT_U, ACT_D, ACT_L, ACT_R]
DIR_NAMES = ['U', 'D', 'L', 'R']

BASELINES = [39, 175, 86, 47, 21, 132, 326]
CHECKPOINT_INTERVAL = 10


def click_action(g, sprite):
    """Create a click action targeting a sprite's center."""
    gx = sprite.x + sprite.width // 2
    gy = sprite.y + sprite.height // 2
    sc, ox, oy = g.camera._calculate_scale_and_offset()
    return ActionInput(id=GameAction.ACTION6,
                       data={'x': int(gx * sc + ox), 'y': int(gy * sc + oy)})


def get_actions(g, use_clicks=True):
    """Get all available ActionInput objects. Indices 0-3=UDLR, 4+=clicks.
    Clicks sorted by sprite name for deterministic ordering."""
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

    # zhcrzgpwcp momentum
    z = 0
    if hasattr(g, 'zhcrzgpwcp') and g.zhcrzgpwcp:
        z = tuple(sorted((k.name, v) for k, v in g.zhcrzgpwcp.items()))

    # msbtawvatm counter
    m = getattr(g, 'msbtawvatm', 0)

    return (tuple(parts), z, m)


def is_won(g, level_idx):
    return g._current_level_index > level_idx


def action_name(a):
    if a.id == GameAction.ACTION6:
        return f"C({a.data.get('x')},{a.data.get('y')})"
    try:
        idx = [GameAction.ACTION1, GameAction.ACTION2,
               GameAction.ACTION3, GameAction.ACTION4].index(a.id)
        return DIR_NAMES[idx]
    except ValueError:
        return str(a.id)


def describe_level(g, level_idx):
    pieces = g.current_level.get_sprites_by_tag('xlfuqjygey')
    frames = g.current_level.get_sprites_by_tag('rktpmjcpkt')
    enemies = g.current_level.get_sprites_by_tag('nnckfubbhi')
    eframes = g.current_level.get_sprites_by_tag('ucjzrlvfkb')
    sel = g.ascpmvdpwj

    print(f"  Pieces ({len(pieces)}):")
    for s in sorted(pieces, key=lambda s: s.name):
        mark = ' [SEL]' if s is sel else ''
        print(f"    {s.name}: ({s.x},{s.y}) {s.width}x{s.height}{mark}")
    print(f"  Frames ({len(frames)}):")
    for s in sorted(frames, key=lambda s: s.name):
        print(f"    ({s.x},{s.y}) {s.width}x{s.height} -> target ({s.x+1},{s.y+1})")
    if enemies:
        print(f"  Enemies ({len(enemies)}):")
        for s in sorted(enemies, key=lambda s: s.name):
            print(f"    {s.name}: ({s.x},{s.y}) {s.width}x{s.height}")
    if eframes:
        print(f"  Enemy frames ({len(eframes)}):")
        for s in sorted(eframes, key=lambda s: s.name):
            print(f"    ({s.x},{s.y}) {s.width}x{s.height} -> target ({s.x+1},{s.y+1})")


def replay_indices(level_idx, indices):
    """Replay a tuple of action indices on a fresh game. Return game object."""
    g = mod.Ka59()
    g.set_level(level_idx)
    for ai in indices:
        act = resolve_action(g, ai)
        g.perform_action(act)
    return g


def indices_to_actions(level_idx, indices):
    """Convert action indices to ActionInput objects by replaying."""
    g = mod.Ka59()
    g.set_level(level_idx)
    actions = []
    for ai in indices:
        act = resolve_action(g, ai)
        actions.append(act)
        g.perform_action(act)
    return actions


def indices_to_names(level_idx, indices):
    """Convert action indices to human-readable names by replaying."""
    g = mod.Ka59()
    g.set_level(level_idx)
    names = []
    for ai in indices:
        act = resolve_action(g, ai)
        names.append(action_name(act))
        g.perform_action(act)
    return ' '.join(names)


# -----------------------------------------------------------------------
# BFS Method 1: Checkpoint-based
# -----------------------------------------------------------------------

def bfs_checkpoint(level_idx, max_depth=None, max_iters=2000000,
                   use_clicks=True, checkpoint_interval=None):
    """BFS with checkpoint-based replay.

    Queue stores action index tuples (no game objects). Checkpoints are
    deepcopy'd game snapshots stored every `ci` depths. To expand a node
    at depth D, deepcopy the checkpoint at floor(D/ci)*ci and replay the
    remaining D%ci actions.

    Memory: O(visited + checkpoints) instead of O(visited + queue_game_objects).
    """
    ci = checkpoint_interval or CHECKPOINT_INTERVAL
    baseline = BASELINES[level_idx]
    limit = max_depth or min(baseline + 10, 400)

    g0 = mod.Ka59()
    g0.set_level(level_idx)

    print(f"\n{'='*60}")
    print(f"Level {level_idx+1} — CHECKPOINT BFS")
    print(f"  baseline={baseline} limit={limit} ckpt_interval={ci}")
    print(f"{'='*60}")
    describe_level(g0, level_idx)

    start_state = get_state(g0)
    print(f"  Start: {start_state}")

    visited = {start_state}
    queue = deque()
    queue.append(())  # empty tuple = root path

    # Checkpoints: action_tuple -> deepcopy'd game
    checkpoints = {(): copy.deepcopy(g0)}

    iters = 0
    start_time = time.time()
    last_report = start_time
    max_depth_seen = 0

    while queue:
        path = queue.popleft()
        depth = len(path)
        iters += 1

        if depth > max_depth_seen:
            max_depth_seen = depth

        now = time.time()
        if now - last_report >= 10.0:
            elapsed = now - start_time
            rate = iters / elapsed if elapsed > 0 else 0
            print(f"  iter={iters:,} q={len(queue):,} d={depth} "
                  f"maxd={max_depth_seen} v={len(visited):,} "
                  f"ckpt={len(checkpoints)} rate={rate:.0f}/s "
                  f"time={elapsed:.0f}s")
            last_report = now

        if iters > max_iters:
            elapsed = time.time() - start_time
            print(f"  HIT MAX ITERS ({max_iters:,}) d={depth} "
                  f"v={len(visited):,} time={elapsed:.0f}s")
            return None

        if depth >= limit:
            continue

        # Reconstruct parent game from nearest checkpoint
        ckpt_depth = (depth // ci) * ci
        ckpt_key = path[:ckpt_depth]
        ckpt = checkpoints.get(ckpt_key)
        if ckpt is not None:
            g = copy.deepcopy(ckpt)
            for ai_idx in range(ckpt_depth, depth):
                act = resolve_action(g, path[ai_idx])
                g.perform_action(act)
        else:
            # Fallback: replay from scratch
            g = mod.Ka59()
            g.set_level(level_idx)
            for ai_idx in range(depth):
                act = resolve_action(g, path[ai_idx])
                g.perform_action(act)

        # Check win (shouldn't happen at expansion time, but be safe)
        if is_won(g, level_idx):
            elapsed = time.time() - start_time
            names = indices_to_names(level_idx, path)
            print(f"\n  SOLVED! {depth} actions ({iters:,} iters, "
                  f"{len(visited):,} states, {elapsed:.1f}s)")
            print(f"  Path: {names}")
            return indices_to_actions(level_idx, path)

        # Expand children
        all_actions = get_actions(g, use_clicks)
        n_actions = len(all_actions)

        for i in range(n_actions):
            new_path = path + (i,)
            new_depth = depth + 1

            # Apply action to get child state
            if i < n_actions - 1:
                g2 = copy.deepcopy(g)
            else:
                g2 = g  # reuse parent for last child (parent no longer needed)

            g2.perform_action(all_actions[i])
            state = get_state(g2)

            if state not in visited:
                visited.add(state)

                # Check immediate win
                if is_won(g2, level_idx):
                    elapsed = time.time() - start_time
                    names = indices_to_names(level_idx, new_path)
                    print(f"\n  SOLVED! {new_depth} actions ({iters:,} iters, "
                          f"{len(visited):,} states, {elapsed:.1f}s)")
                    print(f"  Path: {names}")
                    return indices_to_actions(level_idx, new_path)

                # Store checkpoint if at checkpoint boundary
                if new_depth % ci == 0:
                    if i == n_actions - 1:
                        # g2 is the reused parent — deepcopy for checkpoint
                        checkpoints[new_path] = copy.deepcopy(g2)
                    else:
                        # g2 is already a deepcopy — safe to store
                        checkpoints[new_path] = g2

                queue.append(new_path)

    elapsed = time.time() - start_time
    print(f"  EXHAUSTED. v={len(visited):,} time={elapsed:.0f}s")
    return None


# -----------------------------------------------------------------------
# BFS Method 2: Standard deepcopy
# -----------------------------------------------------------------------

def bfs_deepcopy(level_idx, max_depth=None, max_iters=2000000,
                 use_clicks=True):
    """Standard BFS storing deepcopy'd game objects per node."""
    baseline = BASELINES[level_idx]
    limit = max_depth or min(baseline + 10, 400)

    g0 = mod.Ka59()
    g0.set_level(level_idx)

    print(f"\n{'='*60}")
    print(f"Level {level_idx+1} — DEEPCOPY BFS")
    print(f"  baseline={baseline} limit={limit}")
    print(f"{'='*60}")
    describe_level(g0, level_idx)

    start_state = get_state(g0)
    visited = {start_state}
    queue = deque()
    queue.append((g0, []))

    iters = 0
    start_time = time.time()
    last_report = start_time

    while queue:
        g, path = queue.popleft()
        depth = len(path)
        iters += 1

        now = time.time()
        if now - last_report >= 10.0:
            elapsed = now - start_time
            rate = iters / elapsed if elapsed > 0 else 0
            print(f"  iter={iters:,} q={len(queue):,} d={depth} "
                  f"v={len(visited):,} rate={rate:.0f}/s time={elapsed:.0f}s")
            last_report = now

        if iters > max_iters:
            elapsed = time.time() - start_time
            print(f"  HIT MAX ITERS ({max_iters:,}) d={depth} "
                  f"v={len(visited):,} time={elapsed:.0f}s")
            return None

        if depth >= limit:
            continue

        if is_won(g, level_idx):
            elapsed = time.time() - start_time
            print(f"\n  SOLVED! {depth} actions ({iters:,} iters, "
                  f"{len(visited):,} states, {elapsed:.1f}s)")
            print(f"  Path: {' '.join(action_name(a) for a in path)}")
            return path

        all_actions = get_actions(g, use_clicks)
        n = len(all_actions)

        for i, act in enumerate(all_actions):
            if i < n - 1:
                g2 = copy.deepcopy(g)
            else:
                g2 = g  # reuse for last child

            g2.perform_action(act)
            state = get_state(g2)
            if state not in visited:
                visited.add(state)

                # Check immediate win
                if is_won(g2, level_idx):
                    elapsed = time.time() - start_time
                    new_path = path + [act]
                    print(f"\n  SOLVED! {len(new_path)} actions ({iters:,} iters, "
                          f"{len(visited):,} states, {elapsed:.1f}s)")
                    print(f"  Path: {' '.join(action_name(a) for a in new_path)}")
                    return new_path

                if i == n - 1:
                    g2 = copy.deepcopy(g2)  # must copy since we reused parent
                queue.append((g2, path + [act]))

    elapsed = time.time() - start_time
    print(f"  EXHAUSTED. v={len(visited):,} time={elapsed:.0f}s")
    return None


# -----------------------------------------------------------------------
# Verification
# -----------------------------------------------------------------------

def verify_solution(level_idx, path):
    """Verify a solution by replaying through the game engine."""
    g = mod.Ka59()
    g.set_level(level_idx)
    for a in path:
        g.perform_action(a)
    won = g._current_level_index > level_idx
    print(f"  Verification: {'PASS' if won else 'FAIL'}")
    return won


def verify_via_api(solutions):
    """Verify all solutions through the official ARC-AGI API."""
    import arc_agi
    arcade = arc_agi.Arcade()
    env = arcade.make('ka59-9f096b4a', render_mode=None)
    env.reset()

    total = 0
    for lv_idx in sorted(solutions.keys()):
        for a in solutions[lv_idx]:
            result = env.step(a.id)
        total += len(solutions[lv_idx])
        print(f"  Level {lv_idx+1}: {len(solutions[lv_idx]):3d} actions, "
              f"completed={result.levels_completed}")

    print(f"\n  Total: {total} actions, State: {result.state}")
    return result


# -----------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------

def solve_all(method='deepcopy', max_iters=2000000, use_clicks=True,
              checkpoint_interval=None):
    """Attempt to solve all 7 levels sequentially."""
    solutions = {}

    for level_idx in range(7):
        if method == 'checkpoint':
            path = bfs_checkpoint(level_idx, None, max_iters,
                                  use_clicks, checkpoint_interval)
        else:
            path = bfs_deepcopy(level_idx, None, max_iters, use_clicks)

        if path:
            solutions[level_idx] = path
            print(f"\n  Level {level_idx+1}: SOLVED ({len(path)} actions, "
                  f"baseline {BASELINES[level_idx]})")
        else:
            print(f"\n  Level {level_idx+1}: UNSOLVED (baseline {BASELINES[level_idx]})")

    print(f"\n{'='*60}")
    print(f"SUMMARY: {len(solutions)}/7 levels solved")
    if solutions:
        total = sum(len(p) for p in solutions.values())
        print(f"Total actions: {total}")
    print(f"{'='*60}")

    return solutions


def main():
    import argparse
    parser = argparse.ArgumentParser(description='KA59 BFS Solver')
    parser.add_argument('level', type=int, nargs='?', default=None,
                        help='Level index (0-6). Omit to solve all.')
    parser.add_argument('max_depth', type=int, nargs='?', default=None,
                        help='Max search depth (default: baseline+10)')
    parser.add_argument('--max-iters', type=int, default=2000000,
                        help='Max iterations (default: 2M)')
    parser.add_argument('--no-clicks', action='store_true',
                        help='Disable click/swap actions')
    parser.add_argument('--method', choices=['checkpoint', 'deepcopy'],
                        default='deepcopy',
                        help='BFS method (default: deepcopy)')
    parser.add_argument('--ckpt-interval', type=int, default=None,
                        help=f'Checkpoint interval (default: {CHECKPOINT_INTERVAL})')
    args = parser.parse_args()

    use_clicks = not args.no_clicks

    if args.level is None:
        solve_all(args.method, args.max_iters, use_clicks, args.ckpt_interval)
        return

    if args.method == 'checkpoint':
        path = bfs_checkpoint(args.level, args.max_depth, args.max_iters,
                              use_clicks, args.ckpt_interval)
    else:
        path = bfs_deepcopy(args.level, args.max_depth, args.max_iters,
                            use_clicks)

    if path:
        print(f"\nSolution: {len(path)} actions")
        print(f"Actions: {' '.join(action_name(a) for a in path)}")
        verify_solution(args.level, path)
    else:
        print("\nNo solution found.")


if __name__ == '__main__':
    main()
