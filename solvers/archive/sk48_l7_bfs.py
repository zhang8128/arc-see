#!/usr/bin/env python3
"""SK48 L7 — BFS solver using pure-Python pixel state."""

import numpy as np
import copy
import time
from collections import deque
import arc_agi
from arcengine import GameAction, GameState

GA = {
    'U': GameAction.ACTION1, 'D': GameAction.ACTION2,
    'L': GameAction.ACTION3, 'R': GameAction.ACTION4,
}
AM = {
    'ACTION1': GameAction.ACTION1, 'ACTION2': GameAction.ACTION2,
    'ACTION3': GameAction.ACTION3, 'ACTION4': GameAction.ACTION4,
    'ACTION6': GameAction.ACTION6, 'ACTION7': GameAction.ACTION7,
}

SOLUTIONS = {
    1: "UUURRRRLDDRLUR",
    2: "RRRRUUULLURRDDRURLLURRLLURR",
    3: "RRUUUURDDLDRRRRLLLLUUUURDDDLUUUUR",
    4: "RRUUUULLLLDRURDRURRDLLU",
    5: "LULLRRRRRURRDLLLLDDLDRRRRLURDRLUR",
}

L6_SEQ = [
    ('A', 'ACTION2'), ('A', 'ACTION4'), ('A', 'ACTION4'), ('A', 'ACTION4'),
    ('C', 31, 4),
    ('A', 'ACTION2'), ('A', 'ACTION2'), ('A', 'ACTION4'), ('A', 'ACTION2'),
    ('A', 'ACTION1'), ('A', 'ACTION4'), ('A', 'ACTION2'), ('A', 'ACTION1'),
    ('A', 'ACTION4'), ('A', 'ACTION2'),
    ('C', 7, 34),
    ('A', 'ACTION4'), ('A', 'ACTION4'), ('A', 'ACTION4'), ('A', 'ACTION3'),
    ('A', 'ACTION3'), ('A', 'ACTION3'), ('A', 'ACTION3'), ('A', 'ACTION2'),
    ('A', 'ACTION2'), ('A', 'ACTION4'), ('A', 'ACTION1'), ('A', 'ACTION3'),
    ('A', 'ACTION1'), ('A', 'ACTION4'),
    ('C', 49, 4),
    ('A', 'ACTION3'), ('A', 'ACTION3'), ('A', 'ACTION2'), ('A', 'ACTION2'),
    ('A', 'ACTION2'),
]

def replay_to_l7():
    arcade = arc_agi.Arcade()
    env = arcade.make("sk48-41055498", render_mode=None)
    g = env._game
    obs = env.reset()
    for lvl in range(1, 6):
        for c in SOLUTIONS[lvl]:
            obs = env.step(GA[c], data={})
    for item in L6_SEQ:
        if item[0] == 'C':
            obs = env.step(GameAction.ACTION6, data={'x': item[1], 'y': item[2]})
        else:
            obs = env.step(AM[item[1]], data={})
    return env, g, obs

def get_grid(obs):
    return np.array(obs.frame[-1], dtype=np.int64)

def state_hash(grid):
    """Hash grid excluding step counter area (y >= 53)."""
    return grid[:53].tobytes()

# Define actions to try
# Directional actions + clicks on cage positions
# From L6, click targets were at (x=31,y=4), (x=7,y=34), (x=49,y=4)
# For L7, let's try clicking the two cage interiors
ACTIONS = [
    ('U', GameAction.ACTION1, {}),
    ('D', GameAction.ACTION2, {}),
    ('L', GameAction.ACTION3, {}),
    ('R', GameAction.ACTION4, {}),
    ('C1', GameAction.ACTION6, {'x': 31, 'y': 4}),  # cage15 interior
    ('C2', GameAction.ACTION6, {'x': 7, 'y': 28}),   # cage6 interior
    ('A7', GameAction.ACTION7, {}),
]

print("Replaying to L7...")
env, g, obs = replay_to_l7()
init_grid = get_grid(obs)
init_hash = state_hash(init_grid)
print(f"Initial state hash: {hash(init_hash)}")
print(f"Level index: {g._current_level_index}")

# BFS
print("\nStarting BFS...")
start_time = time.time()

# State: (game_deepcopy, path)
# To save memory, store: visited set + queue of (game, env, path)
# Actually, let's use the approach from L6: deepcopy game object

visited = {init_hash}
queue = deque()
queue.append((copy.deepcopy(g), copy.deepcopy(env), []))

max_depth = 63  # baseline
states_per_depth = {}
solution = None

while queue and not solution:
    game_copy, env_copy, path = queue.popleft()
    depth = len(path)

    if depth not in states_per_depth:
        states_per_depth[depth] = 0
        elapsed = time.time() - start_time
        print(f"  Depth {depth}: {len(visited)} visited, {len(queue)} queued, {elapsed:.1f}s")
    states_per_depth[depth] = states_per_depth.get(depth, 0) + 1

    if depth >= max_depth:
        continue

    for action_name, action, data in ACTIONS:
        # Deepcopy for branching
        g2 = copy.deepcopy(game_copy)
        e2 = copy.deepcopy(env_copy)
        e2._game = g2

        try:
            obs2 = e2.step(action, data=data)
        except Exception:
            continue

        grid2 = get_grid(obs2)
        h = state_hash(grid2)

        if h in visited:
            continue
        visited.add(h)

        new_path = path + [action_name]

        # Check win
        if obs2.state == GameState.WIN:
            solution = new_path
            print(f"\n*** SOLUTION FOUND at depth {len(new_path)}! ***")
            print(f"  Path: {' '.join(new_path)}")
            break

        if g2._current_level_index > 6:
            solution = new_path
            print(f"\n*** LEVEL ADVANCED at depth {len(new_path)}! ***")
            print(f"  Path: {' '.join(new_path)}")
            break

        queue.append((g2, e2, new_path))

elapsed = time.time() - start_time
print(f"\nBFS complete: {len(visited)} states, {elapsed:.1f}s")
if solution:
    print(f"Solution ({len(solution)} steps): {' '.join(solution)}")
else:
    print("No solution found within depth limit")

# Print stats
print("\nStates per depth:")
for d in sorted(states_per_depth.keys()):
    print(f"  Depth {d}: {states_per_depth[d]}")
