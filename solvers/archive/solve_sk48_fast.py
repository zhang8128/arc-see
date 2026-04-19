#!/usr/bin/env python3
"""
SK48 L2 Solver — Engine BFS with fast save/restore.
Uses the same save format as the game's undo system but restores manually.
"""
import sys
import os
import time
from collections import deque

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'environment_files', 'sk48', '41055498'))

from sk48 import Sk48, sprites, hhvuoijeua, udenqlsrfq
from arcengine import GameAction
from arcengine.enums import ActionInput

ACTIONS = {
    1: ActionInput(id=GameAction.ACTION1),
    2: ActionInput(id=GameAction.ACTION2),
    3: ActionInput(id=GameAction.ACTION3),
    4: ActionInput(id=GameAction.ACTION4),
}
ACTION_NAMES = {1: 'U', 2: 'D', 3: 'L', 4: 'R'}


def save_state(game):
    """Save game state as a hashable tuple."""
    data = []
    for rack, segs in game.mwfajkguqx.items():
        data.append(('R', rack.x, rack.y, len(segs)))
    for t in game.vbelzuaian:
        data.append(('T', t.x, t.y, int(t.pixels[1, 1])))
    data.append(('S', game.vzvypfsnt.x, game.vzvypfsnt.y, 0))
    return tuple(sorted(data))


def restore_state(game, state_data):
    """Restore game state from saved data.
    Uses the game's undo mechanism format.
    """
    # Parse state data
    racks = {}
    targets = {}
    sel = None

    for kind, x, y, val in state_data:
        if kind == 'R':
            racks[(x, y)] = val  # val = num_segments
        elif kind == 'T':
            targets[(x, y)] = val  # val = color
        elif kind == 'S':
            sel = (x, y)

    # Remove all existing segments
    for seg_list in game.mwfajkguqx.values():
        for seg in seg_list:
            game.current_level.remove_sprite(seg)
        seg_list.clear()

    # Restore rack positions and segments
    for rack in game.mwfajkguqx:
        key = None
        for k, v in racks.items():
            # Find matching rack
            if True:  # We only have one upper rack in L2
                pass
        # Set rack position
        for (rx, ry), num_segs in racks.items():
            if rack.name == 'ejlpqgojjt':  # Both racks have same name
                # Match by checking if this rack corresponds to this saved position
                pass

    # This is too complex — use the undo mechanism directly
    pass


def make_game():
    game = Sk48()
    game._current_level_index = 1
    game.on_set_level(game._levels[1])
    return game


def state_key(game):
    """Extract state key from game (for dedup)."""
    parts = []
    rack = game.vzvypfsnt
    segs = game.mwfajkguqx[rack]
    parts.append((rack.y, len(segs)))
    for t in game.vbelzuaian:
        if t.y < 53:
            parts.append((t.x, t.y, int(t.pixels[1, 1])))
    return tuple(sorted(parts))


def is_won(game):
    return game.gvtmoopqgy()


def solve():
    """BFS using deepcopy but with lightweight state key."""
    import copy

    game = make_game()
    print(f"SK48 L2 Engine BFS")
    print(f"Turn limit: {game.qiercdohl}")

    initial_key = state_key(game)
    queue = deque()
    queue.append((game, []))
    visited = {initial_key}

    max_depth = 35
    iterations = 0
    t0 = time.time()

    while queue:
        curr_game, path = queue.popleft()

        if len(path) >= max_depth:
            continue

        iterations += 1
        if iterations % 5000 == 0:
            elapsed = time.time() - t0
            print(f"  iter={iterations}, depth={len(path)}, queue={len(queue)}, "
                  f"visited={len(visited)}, {iterations/elapsed:.0f} it/s")

        for action_id in [1, 2, 3, 4]:
            game_copy = copy.deepcopy(curr_game)
            old_key = state_key(game_copy)

            game_copy.perform_action(ACTIONS[action_id])
            new_key = state_key(game_copy)

            if new_key == old_key:
                continue
            if new_key in visited:
                continue
            visited.add(new_key)

            new_path = path + [ACTION_NAMES[action_id]]

            if is_won(game_copy):
                elapsed = time.time() - t0
                print(f"\n*** SOLUTION FOUND! ***")
                print(f"Actions ({len(new_path)}): {''.join(new_path)}")
                print(f"Iterations: {iterations}, Time: {elapsed:.1f}s")
                print(f"Game actions: {['ACTION'+{'U':'1','D':'2','L':'3','R':'4'}[a] for a in new_path]}")
                return new_path

            if game_copy.qiercdohl > 0:
                queue.append((game_copy, new_path))

    elapsed = time.time() - t0
    print(f"\nNo solution found within depth {max_depth}")
    print(f"Iterations: {iterations}, Time: {elapsed:.1f}s, States: {len(visited)}")
    return None


if __name__ == "__main__":
    solve()
