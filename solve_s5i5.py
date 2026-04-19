#!/usr/bin/env python3
"""S5I5 solver — deepcopy BFS with pixel hash. Only 4 unique actions per state."""
import importlib.util, copy, hashlib, time
import arc_agi
from collections import deque
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('s5i5', 'environment_files/s5i5/a48e4b1d/s5i5.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

CLICK = GameAction.ACTION6
BASELINES = [19, 57, 85, 203, 82, 30, 76, 56]


def pixel_hash(g):
    return hashlib.md5(g.get_pixels(0, 0, 64, 64).tobytes()).hexdigest()


def get_effective_clicks(g):
    """Find representative click positions for each unique action.
    Each gdgcpukdrl piece has 2 halves -> 2 distinct actions per piece."""
    import numpy as np
    f0 = g.get_pixels(0, 0, 64, 64)
    seen_hashes = {}

    for x in range(64):
        for y in range(64):
            g2 = copy.deepcopy(g)
            g2.perform_action(ActionInput(id=CLICK, data={'x': x, 'y': y}))
            f1 = g2.get_pixels(0, 0, 64, 64)
            if np.array_equal(f0, f1):
                continue
            h = hashlib.md5(f1.tobytes()).hexdigest()
            if h not in seen_hashes:
                seen_hashes[h] = (x, y)

    return list(seen_hashes.values())


def bfs_solve(level_idx, max_depth=None):
    g0 = mod.S5i5()
    g0.set_level(level_idx)
    baseline = BASELINES[level_idx]
    limit = max_depth or baseline + 5

    # Find unique click actions for initial state
    clicks = get_effective_clicks(g0)
    print(f"L{level_idx+1}: baseline={baseline}, limit={limit}, unique_clicks={len(clicks)}: {clicks}")

    start = pixel_hash(g0)
    queue = deque([(g0, [])])
    visited = {start}
    t0 = time.time()
    iters = 0

    while queue:
        g, path = queue.popleft()
        iters += 1
        if iters % 5000 == 0:
            print(f"  iter={iters} q={len(queue)} d={len(path)} v={len(visited)} t={time.time()-t0:.1f}s")
        if len(path) >= limit:
            continue

        # Re-enumerate clicks from this state (they might change as bars move)
        cur_clicks = get_effective_clicks(g)
        for (cx, cy) in cur_clicks:
            g2 = copy.deepcopy(g)
            g2.perform_action(ActionInput(id=CLICK, data={'x': cx, 'y': cy}))
            if g2._current_level_index > level_idx or g2._state.name == "WIN":
                result = path + [(cx, cy)]
                print(f"  FOUND! {len(result)} clicks ({iters} iters, {time.time()-t0:.1f}s)")
                return result
            if g2._state.name == "GAME_OVER":
                continue
            h = pixel_hash(g2)
            if h not in visited:
                visited.add(h)
                queue.append((g2, path + [(cx, cy)]))

    print(f"  No solution ({iters} iters, {len(visited)} states, {time.time()-t0:.1f}s)")
    return None


# Solve all levels
all_solutions = {}
for level in range(8):
    result = bfs_solve(level)
    if result:
        all_solutions[level] = result
        print(f"  -> L{level+1}: {len(result)} clicks (baseline {BASELINES[level]})\n")
    else:
        print(f"  -> L{level+1}: FAILED\n")
        break

# API verification
if all_solutions:
    print("\n=== API Verification ===")
    arcade = arc_agi.Arcade()
    env = arcade.make("s5i5-a48e4b1d", render_mode=None)
    obs = env.reset()
    total = 0
    for level in range(len(all_solutions)):
        clicks = all_solutions[level]
        for x, y in clicks:
            obs = env.step(CLICK, data={"x": x, "y": y})
        total += len(clicks)
        print(f"  L{level+1}: {len(clicks):3d} clicks (baseline {BASELINES[level]}), levels_completed={obs.levels_completed}")

    print(f"\nTotal: {total} clicks (baselines: {sum(BASELINES[:len(all_solutions)])})")
    print(f"State: {obs.state}")

    # Print solution data for replay file
    print("\nSOLUTIONS = {")
    for level in sorted(all_solutions.keys()):
        print(f"    {level+1}: {all_solutions[level]},")
    print("}")
