#!/usr/bin/env python3
"""SK48 L7 — BFS with deepcopy (3ms per state).
Target: find solution within 63 actions (baseline)."""

import numpy as np
import time
import hashlib
import copy
from collections import deque
import arc_agi
from arcengine import GameAction, GameState

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

GA = {
    'U': GameAction.ACTION1, 'D': GameAction.ACTION2,
    'L': GameAction.ACTION3, 'R': GameAction.ACTION4,
}
AM = {
    'ACTION1': GameAction.ACTION1, 'ACTION2': GameAction.ACTION2,
    'ACTION3': GameAction.ACTION3, 'ACTION4': GameAction.ACTION4,
    'ACTION6': GameAction.ACTION6,
}

def create_env():
    arcade = arc_agi.Arcade()
    env = arcade.make("sk48-41055498", render_mode=None)
    obs = env.reset()
    for lvl in range(1, 6):
        for c in SOLUTIONS[lvl]:
            obs = env.step(GA[c], data={})
    for item in L6_SEQ:
        if item[0] == 'C':
            obs = env.step(GameAction.ACTION6, data={'x': item[1], 'y': item[2]})
        else:
            obs = env.step(AM[item[1]], data={})
    return env, obs

def pixel_hash(obs):
    """Fast hash of game-relevant pixels only."""
    grid = np.array(obs.frame[-1], dtype=np.int64)
    # Exclude step counter (row 53+) and static border
    return hashlib.md5(grid[:53].tobytes()).digest()

def sprite_hash(game):
    """Hash based on sprite positions — much smaller than pixel hash."""
    level = game._levels[game._current_level_index]
    positions = []
    for s in level._sprites:
        if hasattr(s, 'x') and hasattr(s, 'y'):
            positions.append((s.x, s.y))
    return hash(tuple(positions))

# Actions: UDLR + click cage15
# From the L6 solution, clicks were at specific coords:
# (31,4)=cage15, (7,34)=scan column click, (49,4)=cage15 moved position
# For L7, the cage15 starts at (29,2) and can move.
# The click on cage15 toggles between racks.
# We need: click to switch to cage15, and click to switch back to cage6.
# cage6 click target: the ejlpqgojjt sprite at (5,20) with sys_click tag
# Wait, (5,20) is the cage6 position!

ACTIONS = [
    ('U', GameAction.ACTION1, {}),
    ('D', GameAction.ACTION2, {}),
    ('L', GameAction.ACTION3, {}),
    ('R', GameAction.ACTION4, {}),
    ('C1', GameAction.ACTION6, {'x': 31, 'y': 4}),   # cage15 at initial pos
    ('C6', GameAction.ACTION6, {'x': 7, 'y': 22}),    # cage6 (sprite at 5,20 + offset)
]

print("Setting up L7...")
env, obs = create_env()
g = env._game

# Verify initial state
grid = np.array(obs.frame[-1], dtype=np.int64)
print(f"Level: {g._current_level_index}")
print(f"Sprites: {len(g._levels[g._current_level_index]._sprites)}")

# Run BFS
print(f"\nStarting BFS with {len(ACTIONS)} actions...")
t_start = time.time()

init_hash = sprite_hash(g)
visited = {init_hash}
# Queue: (game_copy, path_list)
queue = deque()
queue.append((copy.deepcopy(g), []))

max_depth = 40  # try up to 40 first
solution = None
prev_depth = -1
states_at_depth = {}

while queue and not solution:
    game_copy, path = queue.popleft()
    depth = len(path)

    if depth != prev_depth:
        elapsed = time.time() - t_start
        print(f"  d={depth}: visited={len(visited)} q={len(queue)} t={elapsed:.1f}s", flush=True)
        prev_depth = depth
        if elapsed > 300:  # 5 min timeout
            print("  TIMEOUT")
            break

    if depth >= max_depth:
        continue

    for aname, action, data in ACTIONS:
        g2 = copy.deepcopy(game_copy)
        # Create a minimal env wrapper to call step
        # Actually we need the env for step(). Let me create a fresh env each time.
        # NO - that's too expensive. Let me reuse the env by swapping the game.
        env._game = g2
        try:
            obs2 = env.step(action, data=data)
        except Exception:
            continue

        h = sprite_hash(g2)
        if h in visited:
            continue
        visited.add(h)

        new_path = path + [aname]

        # Check win
        if obs2.state == GameState.WIN or g2._current_level_index > 6:
            solution = new_path
            elapsed = time.time() - t_start
            print(f"\n*** SOLUTION at depth {len(new_path)} in {elapsed:.1f}s ***")
            print(f"  Path: {' '.join(new_path)}")
            break

        queue.append((copy.deepcopy(g2), new_path))

if not solution:
    elapsed = time.time() - t_start
    print(f"\nNo solution found. Visited {len(visited)} states in {elapsed:.1f}s")
    print(f"Depth distribution: max depth reached = {prev_depth}")
else:
    # Verify by replaying
    print("\nVerifying solution...")
    env2, obs2 = create_env()
    g2 = env2._game
    for aname in solution:
        for an, action, data in ACTIONS:
            if an == aname:
                obs2 = env2.step(action, data=data)
                break
    print(f"  Final state: {obs2.state}")
    print(f"  Level: {g2._current_level_index}")

    # Convert to submission format
    print("\n  Solution for submission:")
    action_map = {'U': 'ACTION1', 'D': 'ACTION2', 'L': 'ACTION3', 'R': 'ACTION4'}
    for a in solution:
        if a in action_map:
            print(f"    ('A', '{action_map[a]}'),")
        elif a.startswith('C'):
            for an, action, data in ACTIONS:
                if an == a:
                    print(f"    ('C', {data['x']}, {data['y']}),")
                    break
