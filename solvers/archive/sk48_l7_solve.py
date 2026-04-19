#!/usr/bin/env python3
"""SK48 L7 — Efficient BFS using deepcopy + game state inspection."""

import numpy as np
import time
import hashlib
from collections import deque
import copy
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
    'ACTION6': GameAction.ACTION6, 'ACTION7': GameAction.ACTION7,
}

def create_env():
    """Create and replay to L7."""
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

def state_hash(obs):
    """Hash the grid excluding step counter area."""
    grid = np.array(obs.frame[-1], dtype=np.int64)
    return hashlib.md5(grid[:53].tobytes()).digest()

# Time the deepcopy approach
print("Setting up...")
env, obs = create_env()
g = env._game

print(f"\nTiming deepcopy...")
t0 = time.time()
for _ in range(100):
    g2 = copy.deepcopy(g)
t1 = time.time()
dc_ms = (t1-t0)/100*1000
print(f"deepcopy: {dc_ms:.1f}ms per copy")

# Inspect game internals
print(f"\nGame type: {type(g).__name__}")
print(f"Level index: {g._current_level_index}")

# Check what the game object contains
level = g._levels[g._current_level_index]
print(f"Level type: {type(level).__name__}")

# Find sprites
sprites = None
for attr in ['_sprites', 'sprites', '_sprite_list']:
    if hasattr(level, attr):
        sprites = getattr(level, attr)
        print(f"Sprites ({attr}): {len(sprites)} sprites")
        break

if sprites:
    # Find movable sprites by checking for x,y attributes
    movable = []
    for i, s in enumerate(sprites):
        if hasattr(s, 'x') and hasattr(s, 'y'):
            tags = getattr(s, 'tags', [])
            name = getattr(s, 'name', '')
            pixels = getattr(s, 'pixels', None)
            w = getattr(s, 'w', 0)
            h = getattr(s, 'h', 0)
            print(f"  Sprite {i}: ({s.x},{s.y}) {w}x{h} name='{name}' tags={tags}")
            if i < 30:  # show first 30
                movable.append(s)

# Now run BFS with deepcopy
# Actions: UDLR + click cage15 at initial position
# We'll use fewer click targets to reduce branching
ACTIONS = [
    ('U', GameAction.ACTION1, {}),
    ('D', GameAction.ACTION2, {}),
    ('L', GameAction.ACTION3, {}),
    ('R', GameAction.ACTION4, {}),
    ('C', GameAction.ACTION6, {'x': 31, 'y': 4}),  # cage15 initial
]

# For the return click, we need to know where cage6 is
# Let's add a few cage6 click options
ACTIONS.extend([
    ('c6', GameAction.ACTION6, {'x': 7, 'y': 28}),   # cage6 interior
])

print(f"\nBFS with {len(ACTIONS)} actions, deepcopy at {dc_ms:.0f}ms per state")
print(f"Estimated: depth 10 = ~{len(ACTIONS)**10/1e6:.0f}M states (with pruning much less)")

# Run BFS up to a limited depth to see the state space
init_hash = state_hash(obs)
visited = {init_hash}
# Store: (game_copy, path_str)
queue = deque([(copy.deepcopy(g), copy.deepcopy(env), "")])

t_start = time.time()
max_depth = 25  # start conservatively
depth_counts = {}
found = False

while queue and not found:
    game_copy, env_copy, path = queue.popleft()
    depth = len(path.split(',')) - 1 if path else 0

    if depth >= max_depth:
        continue

    if depth not in depth_counts:
        depth_counts[depth] = 0
        elapsed = time.time() - t_start
        rate = len(visited) / max(elapsed, 0.001)
        print(f"  d={depth}: visited={len(visited)} q={len(queue)} t={elapsed:.1f}s rate={rate:.0f}/s")
    depth_counts[depth] += 1

    for aname, action, data in ACTIONS:
        g2 = copy.deepcopy(game_copy)
        e2 = copy.deepcopy(env_copy)
        e2._game = g2

        try:
            obs2 = e2.step(action, data=data)
        except Exception:
            continue

        h = state_hash(obs2)
        if h in visited:
            continue
        visited.add(h)

        new_path = f"{path},{aname}" if path else aname

        # Check win
        if obs2.state == GameState.WIN or g2._current_level_index > 6:
            print(f"\n*** SOLUTION FOUND! ***")
            print(f"  Depth: {depth + 1}")
            print(f"  Path: {new_path}")
            found = True
            break

        queue.append((g2, e2, new_path))

    if found:
        break

elapsed = time.time() - t_start
print(f"\nBFS stats: {len(visited)} states, {elapsed:.1f}s")
print(f"Depth distribution: {dict(sorted(depth_counts.items()))}")
