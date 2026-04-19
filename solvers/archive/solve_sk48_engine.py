#!/usr/bin/env python3
"""
SK48 Solver — Uses actual game engine with deepcopy BFS.
State hash: sprite positions only (excludes step counter).
"""

import sys
import os
import copy
from collections import deque

# Add the game directory to path
GAME_DIR = os.path.join(os.path.dirname(__file__), '..', 'environment_files', 'sk48', '41055498')
sys.path.insert(0, GAME_DIR)

from sk48 import Sk48
from arcengine.enums import ActionInput


def make_game():
    """Create a fresh game instance."""
    game = Sk48()
    return game


def advance_to_level(game, target_level):
    """Play through levels to reach target_level (0-indexed)."""
    # For now we start from level 0 and skip to level target_level
    # We need to set the internal level index
    pass


def get_state_key(game):
    """Extract a hashable state key from the game.

    We care about:
    - Rack position (y)
    - Segments: list of (x, y) positions
    - Targets: list of (x, y, color) tuples
    - Currently selected rack
    """
    g = game
    # Get segments for all racks
    seg_data = []
    for rack, segs in g.mwfajkguqx.items():
        rack_key = (rack.x, rack.y, rack.rotation)
        seg_positions = tuple((s.x, s.y, s.pixels[1, 1]) for s in segs)
        seg_data.append((rack_key, seg_positions))
    seg_data.sort()

    # Get target positions
    target_data = tuple(sorted((t.x, t.y, t.pixels[1, 1]) for t in g.vbelzuaian))

    # Selected rack
    sel = (g.vzvypfsnt.x, g.vzvypfsnt.y) if g.vzvypfsnt else None

    return (tuple(seg_data), target_data, sel)


def is_won(game):
    """Check if current state is a win."""
    return game.gvtmoopqgy()


ACTION_INPUTS = None

def get_action_inputs():
    """Cache ActionInput objects."""
    global ACTION_INPUTS
    if ACTION_INPUTS is None:
        from arcengine import GameAction
        from arcengine.enums import ActionInput
        ACTION_INPUTS = {
            1: ActionInput(id=GameAction.ACTION1),
            2: ActionInput(id=GameAction.ACTION2),
            3: ActionInput(id=GameAction.ACTION3),
            4: ActionInput(id=GameAction.ACTION4),
        }
    return ACTION_INPUTS


def apply_action(game, action_id):
    """Apply an action using perform_action."""
    inputs = get_action_inputs()
    game.perform_action(inputs[action_id])
    return True


def solve_bfs(game, max_depth=35):
    """BFS using deepcopy of game state."""
    actions = [1, 2, 3, 4]  # UP, DOWN, LEFT, RIGHT
    action_names = {1: 'U', 2: 'D', 3: 'L', 4: 'R'}

    initial_key = get_state_key(game)
    queue = deque()
    queue.append((game, [], initial_key))
    visited = {initial_key}

    iterations = 0

    while queue:
        curr_game, path, _ = queue.popleft()

        if len(path) >= max_depth:
            continue

        iterations += 1
        if iterations % 10000 == 0:
            print(f"  iter={iterations}, depth={len(path)}, queue={len(queue)}, visited={len(visited)}")

        for action_id in actions:
            game_copy = copy.deepcopy(curr_game)
            old_key = get_state_key(game_copy)

            # Save state to check if action had effect
            apply_action(game_copy, action_id)

            new_key = get_state_key(game_copy)

            # Skip if action had no effect
            if new_key == old_key:
                continue

            if new_key in visited:
                continue
            visited.add(new_key)

            new_path = path + [action_names[action_id]]

            # Check win
            if is_won(game_copy):
                print(f"\n*** SOLUTION FOUND! ***")
                print(f"Actions ({len(new_path)}): {''.join(new_path)}")
                print(f"Iterations: {iterations}")
                print(f"States visited: {len(visited)}")
                return new_path

            # Check if game is still playable
            if game_copy.qiercdohl > 0:
                queue.append((game_copy, new_path, new_key))

    print(f"\nNo solution found within depth {max_depth}")
    print(f"Iterations: {iterations}")
    print(f"States visited: {len(visited)}")
    return None


if __name__ == "__main__":
    print("SK48 Engine-based BFS Solver")
    print("Creating game...")

    game = make_game()

    # Need to advance to level 2 (index 1)
    # First, let's see what level we start on
    print(f"Current level index: {game._current_level_index}")
    print(f"Number of levels: {len(game._levels)}")

    # Skip to level 2 by setting the level directly
    game._current_level_index = 1
    game.on_set_level(game._levels[1])

    print(f"Now on level: {game._current_level_index + 1}")
    print(f"Turn limit: {game.qiercdohl}")

    # Print initial state
    print(f"\nRacks:")
    for rack, segs in game.mwfajkguqx.items():
        print(f"  Rack at ({rack.x}, {rack.y}), rot={rack.rotation}, name={rack.name}")
        print(f"    Segments ({len(segs)}):")
        for s in segs:
            print(f"      ({s.x}, {s.y}) rot={s.rotation} color={s.pixels[1,1]}")

    print(f"\nTargets:")
    for t in game.vbelzuaian:
        print(f"  ({t.x}, {t.y}) color={t.pixels[1,1]}")

    print(f"\nPaired racks:")
    for upper, lower in game.xpmcmtbcv.items():
        print(f"  Upper: ({upper.x}, {upper.y}) -> Lower: ({lower.x}, {lower.y})")

    print(f"\nWin check: {is_won(game)}")

    print(f"\nStarting BFS...")
    result = solve_bfs(game, max_depth=35)

    if result:
        print(f"\nSolution: {''.join(result)} ({len(result)} actions)")
