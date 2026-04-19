#!/usr/bin/env python3
"""S5I5 deep probe — understand click mechanics."""
import importlib.util, copy, numpy as np, hashlib
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('s5i5', 'environment_files/s5i5/a48e4b1d/s5i5.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

CLICK = GameAction.ACTION6

def pixel_hash(g):
    return hashlib.md5(g.get_pixels(0, 0, 64, 64).tobytes()).hexdigest()

def frame(g):
    return g.get_pixels(0, 0, 64, 64)

# === L1 deep analysis ===
g = mod.S5i5()
g.set_level(0)
f0 = frame(g)

print("=== L1: Click at every pixel ===")
effective_clicks = []
for x in range(64):
    for y in range(64):
        g2 = copy.deepcopy(g)
        g2.perform_action(ActionInput(id=CLICK, data={'x': x, 'y': y}))
        f1 = frame(g2)
        diff = np.sum(f0 != f1)
        if diff > 0:
            effective_clicks.append((x, y, diff))

print(f"Effective click positions: {len(effective_clicks)}")
# Group by diff count
from collections import Counter
diff_counts = Counter(d for _, _, d in effective_clicks)
print(f"Diff counts: {dict(diff_counts)}")

# Show all effective positions
for x, y, d in effective_clicks:
    g2 = copy.deepcopy(g)
    g2.perform_action(ActionInput(id=CLICK, data={'x': x, 'y': y}))
    f1 = frame(g2)
    changed_positions = list(zip(*np.where(f0 != f1)))
    if len(changed_positions) <= 20:
        print(f"  click({x:2d},{y:2d}): {d} px changed at {changed_positions[:5]}...")

# Check if any click wins
print("\n=== L1: Brute-force 2-click search ===")
# Group effective clicks by unique resulting state
unique_states = {}
for x, y, d in effective_clicks:
    g2 = copy.deepcopy(g)
    g2.perform_action(ActionInput(id=CLICK, data={'x': x, 'y': y}))
    h = pixel_hash(g2)
    if h not in unique_states:
        unique_states[h] = (x, y)
print(f"Unique states after 1 click: {len(unique_states)}")

# Try 2 clicks from each unique state
for h1, (x1, y1) in unique_states.items():
    g2 = copy.deepcopy(g)
    g2.perform_action(ActionInput(id=CLICK, data={'x': x1, 'y': y1}))
    f1 = frame(g2)

    for x2 in range(64):
        for y2 in range(64):
            g3 = copy.deepcopy(g2)
            g3.perform_action(ActionInput(id=CLICK, data={'x': x2, 'y': y2}))
            if g3._current_level_index > 0 or g3._state.name == "WIN":
                print(f"  WIN! click({x1},{y1}) -> click({x2},{y2})")

print("\n=== L1: Check what sprites are clickable ===")
sprites = g.current_level.get_sprites()
for s in sprites:
    cx, cy = s.x + s.width // 2, s.y + s.height // 2
    g2 = copy.deepcopy(g)
    g2.perform_action(ActionInput(id=CLICK, data={'x': cx, 'y': cy}))
    f1 = frame(g2)
    diff = np.sum(f0 != f1)
    tags = list(s.tags) if hasattr(s, 'tags') else []
    print(f"  {s.name:20s} center=({cx:2d},{cy:2d}) size={s.width}x{s.height} tags={tags} -> {diff} px changed")

# Check attributes on the game object
print("\n=== Game object attributes ===")
for attr in sorted(dir(g)):
    if attr.startswith('_') or callable(getattr(g, attr)):
        continue
    val = getattr(g, attr)
    if isinstance(val, (int, float, str, bool, list, dict, type(None))):
        print(f"  {attr} = {repr(val)[:100]}")
