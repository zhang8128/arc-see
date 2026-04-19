#!/usr/bin/env python3
"""SK48 L7 — Inspect game internals for lightweight state management."""

import numpy as np
import time
import copy
import sys
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

env, obs = create_env()
g = env._game
level = g._levels[g._current_level_index]

# Inspect level structure
print(f"Level type: {type(level).__name__}")
attrs = [a for a in dir(level) if not a.startswith('__')]
print(f"Level attributes: {attrs}")

# Look for sprite list
for attr_name in attrs:
    val = getattr(level, attr_name)
    if isinstance(val, (list, tuple)) and len(val) if hasattr(val, '__len__') else False:
        if len(val) > 0 and hasattr(val[0] if isinstance(val, list) else val, 'x'):
            print(f"\n  {attr_name}: {len(val)} items with x attr")

# Check for get_pixels or render
print(f"\nHas get_pixels: {hasattr(level, 'get_pixels')}")
print(f"Has render: {hasattr(level, 'render')}")
print(f"Has step: {hasattr(level, 'step')}")

# Time a single deepcopy
t0 = time.time()
g2 = copy.deepcopy(g)
t1 = time.time()
print(f"\nSingle deepcopy: {(t1-t0)*1000:.0f}ms")

# Time a single step
t0 = time.time()
obs2 = env.step(GameAction.ACTION1, data={})
t1 = time.time()
print(f"Single step: {(t1-t0)*1000:.0f}ms")

# Check size of game state
print(f"\nGame object size estimate:")
print(f"  sys.getsizeof(g): {sys.getsizeof(g)}")
print(f"  sys.getsizeof(level): {sys.getsizeof(level)}")

# Try to find a lightweight state representation
# The game has no internal engine, so the state IS the pixel grid
# Can we reconstruct the game from the pixel grid?

# Actually, let's check if we can save/restore game state
# by just saving sprite positions
if hasattr(level, '_sprites'):
    sprites = level._sprites
elif hasattr(level, 'sprites'):
    sprites = level.sprites
else:
    sprites = None
    # Try to find sprites in other attributes
    for attr in attrs:
        val = getattr(level, attr)
        if isinstance(val, list) and len(val) > 5:
            first = val[0] if val else None
            if first and hasattr(first, 'x') and hasattr(first, 'y'):
                sprites = val
                print(f"\nFound sprites in '{attr}': {len(val)} sprites")
                break

if sprites:
    print(f"\nSprite count: {len(sprites)}")
    # Categorize sprites
    movable = []
    for s in sprites:
        x = getattr(s, 'x', None)
        y = getattr(s, 'y', None)
        w = getattr(s, 'w', 0)
        h = getattr(s, 'h', 0)
        name = getattr(s, 'name', '')
        tags = getattr(s, 'tags', [])
        pixels = getattr(s, 'pixels', None)
        # Get unique colors in pixels
        if pixels is not None and hasattr(pixels, '__iter__'):
            flat = []
            for row in pixels:
                if hasattr(row, '__iter__'):
                    for px in row:
                        if px != -1:
                            flat.append(px)
            unique_colors = set(flat[:20])
        else:
            unique_colors = set()

        if x is not None:
            movable.append((x, y, w, h, name, tags, unique_colors))

    # Print sprites sorted by position
    movable.sort(key=lambda s: (s[1], s[0]))
    for x, y, w, h, name, tags, colors in movable[:40]:
        print(f"  ({x:3d},{y:3d}) {w}x{h} name='{name}' tags={tags[:3]} colors={colors}")

    # Count total sprites for deepcopy estimate
    print(f"\n  Total sprites: {len(sprites)}")

    # Test: how fast is copying just the sprite positions?
    t0 = time.time()
    for _ in range(1000):
        state = tuple((s.x, s.y) for s in sprites if hasattr(s, 'x'))
    t1 = time.time()
    print(f"  Extract positions: {(t1-t0)/1000*1000:.2f}ms ({len(state)} sprites)")
