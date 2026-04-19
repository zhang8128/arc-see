#!/usr/bin/env python3
"""
SK48 L2 Solver — IDDFS with game engine undo.
Uses ACTION7 (undo) for backtracking, no deepcopy needed.
"""
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'environment_files', 'sk48', '41055498'))

from sk48 import Sk48
from arcengine import GameAction
from arcengine.enums import ActionInput

ACTION_MAP = {
    'U': ActionInput(id=GameAction.ACTION1),
    'D': ActionInput(id=GameAction.ACTION2),
    'L': ActionInput(id=GameAction.ACTION3),
    'R': ActionInput(id=GameAction.ACTION4),
}
UNDO = ActionInput(id=GameAction.ACTION7)


def get_state_key(game):
    """Fast state key from game internals."""
    rack = game.vzvypfsnt
    segs = game.mwfajkguqx[rack]
    seg_key = (rack.x, rack.y, len(segs))
    # We also need the rightmost segment x (or just len is enough since they're contiguous)
    target_key = tuple(sorted((t.x, t.y, int(t.pixels[1, 1])) for t in game.vbelzuaian if t.y < 53))
    return (seg_key, target_key)


def is_won(game):
    return game.gvtmoopqgy()


def do_action(game, action_name):
    """Apply action. Returns True if state changed."""
    old_key = get_state_key(game)
    game.perform_action(ACTION_MAP[action_name])
    new_key = get_state_key(game)
    return new_key != old_key


def undo_action(game):
    """Undo last action."""
    game.perform_action(UNDO)


iterations = 0
best_solution = None


def dfs(game, depth, max_depth, path, visited_at_depth):
    """DFS with visited set per depth level to avoid cycles."""
    global iterations, best_solution

    if best_solution is not None and len(path) >= len(best_solution):
        return

    iterations += 1
    if iterations % 100000 == 0:
        print(f"  iter={iterations}, depth={len(path)}/{max_depth}, path={''.join(path[:20])}")

    if is_won(game):
        print(f"\n*** SOLUTION: {''.join(path)} ({len(path)} actions) ***")
        best_solution = list(path)
        return

    if depth >= max_depth:
        return

    state_key = get_state_key(game)

    for action_name in ['U', 'D', 'L', 'R']:
        # Skip obviously bad moves
        if len(path) >= 1:
            last = path[-1]
            # Don't undo the last move
            if (action_name == 'U' and last == 'D') or (action_name == 'D' and last == 'U'):
                continue
            if (action_name == 'L' and last == 'R') or (action_name == 'R' and last == 'L'):
                continue

        changed = do_action(game, action_name)
        if not changed:
            undo_action(game)
            continue

        new_key = get_state_key(game)
        if new_key not in visited_at_depth or visited_at_depth[new_key] > len(path) + 1:
            visited_at_depth[new_key] = len(path) + 1
            path.append(action_name)
            dfs(game, depth + 1, max_depth, path, visited_at_depth)
            path.pop()

        undo_action(game)

        if best_solution is not None and len(best_solution) <= len(path) + 1:
            return


def solve():
    global iterations, best_solution

    game = Sk48()
    game._current_level_index = 1
    game.on_set_level(game._levels[1])

    print("SK48 L2 IDDFS Solver")
    print(f"Rack: ({game.vzvypfsnt.x}, {game.vzvypfsnt.y})")
    targets = sorted([(t.x, t.y, int(t.pixels[1, 1])) for t in game.vbelzuaian if t.y < 53])
    print(f"Targets: {targets}")

    for max_depth in range(10, 36):
        iterations = 0
        best_solution = None
        visited = {get_state_key(game): 0}
        t0 = time.time()

        print(f"\n--- Depth limit: {max_depth} ---")
        dfs(game, 0, max_depth, [], visited)

        elapsed = time.time() - t0
        print(f"  Explored {iterations} nodes in {elapsed:.1f}s ({iterations/elapsed:.0f} nodes/s)")
        print(f"  Unique states: {len(visited)}")

        if best_solution:
            print(f"\nFinal solution: {''.join(best_solution)} ({len(best_solution)} actions)")
            return best_solution

    print("\nNo solution found!")
    return None


if __name__ == "__main__":
    solve()
