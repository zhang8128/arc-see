#!/usr/bin/env python3
"""S5I5 fast solver — use game state (marker positions) for BFS, not pixel hash."""
import importlib.util, copy, hashlib, time
import arc_agi
from collections import deque
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('s5i5', 'environment_files/s5i5/a48e4b1d/s5i5.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

CLICK = GameAction.ACTION6
BASELINES = [19, 57, 85, 203, 82, 30, 76, 56]


def state_key(g):
    """Hash game state from sprite positions + sizes."""
    parts = []
    for s in g.current_level.get_sprites():
        parts.append((s.name, s.x, s.y, s.width, s.height))
    return tuple(sorted(parts))


def get_piece_clicks(g):
    """Discover all unique click actions by scanning every pixel once.
    Returns list of (x, y) — one representative per unique outcome."""
    import numpy as np
    f0 = g.get_pixels(0, 0, 64, 64)
    seen = {}
    for x in range(64):
        for y in range(64):
            g2 = copy.deepcopy(g)
            g2.perform_action(ActionInput(id=CLICK, data={'x': x, 'y': y}))
            f1 = g2.get_pixels(0, 0, 64, 64)
            if not np.array_equal(f0, f1):
                h = hashlib.md5(f1.tobytes()).hexdigest()
                if h not in seen:
                    seen[h] = (x, y)
    return list(seen.values())


def bfs_solve(level_idx, max_depth=None):
    g0 = mod.S5i5()
    g0.set_level(level_idx)
    baseline = BASELINES[level_idx]
    limit = max_depth or baseline + 2

    clicks0 = get_piece_clicks(g0)
    print(f"L{level_idx+1}: baseline={baseline}, limit={limit}, clicks={clicks0}", flush=True)

    start = state_key(g0)
    queue = deque([(g0, [])])
    visited = {start}
    t0 = time.time()
    iters = 0

    while queue:
        g, path = queue.popleft()
        iters += 1
        if iters % 10000 == 0:
            print(f"  iter={iters} q={len(queue)} d={len(path)} v={len(visited)} t={time.time()-t0:.1f}s", flush=True)
        if len(path) >= limit:
            continue

        for (cx, cy) in clicks0:  # reuse initial clicks for all states
            g2 = copy.deepcopy(g)
            g2.perform_action(ActionInput(id=CLICK, data={'x': cx, 'y': cy}))
            if g2._current_level_index > level_idx or g2._state.name == "WIN":
                result = path + [(cx, cy)]
                print(f"  FOUND! {len(result)} clicks ({iters} iters, {time.time()-t0:.1f}s)", flush=True)
                return result
            if g2._state.name == "GAME_OVER":
                continue
            k = state_key(g2)
            if k not in visited:
                visited.add(k)
                queue.append((g2, path + [(cx, cy)]))

    print(f"  No solution ({iters} iters, {len(visited)} states, {time.time()-t0:.1f}s)", flush=True)
    return None


# Already solved L1-L5
all_solutions = {
    0: [(45, 21), (45, 21), (45, 21), (45, 21), (45, 21), (45, 21), (45, 21), (24, 44), (24, 44), (24, 44), (24, 44), (24, 44), (24, 44)],
    1: [(12, 57), (12, 57), (12, 57), (12, 57), (12, 57), (12, 57), (12, 57), (12, 57), (27, 57), (27, 57), (27, 57), (27, 57), (27, 57), (27, 57), (27, 57), (27, 57), (42, 57), (42, 57), (57, 57), (57, 57), (57, 57), (57, 57), (57, 57), (57, 57), (42, 57), (42, 57)],
    2: [(10, 48), (16, 57), (16, 57), (16, 57), (35, 57), (48, 48), (48, 48), (10, 48), (10, 48), (10, 48), (10, 48), (54, 57), (54, 57), (54, 57), (54, 57), (48, 48), (48, 48), (48, 48), (35, 57), (35, 57), (35, 57), (35, 57), (35, 57), (35, 57), (35, 57), (35, 48), (35, 48), (35, 48), (35, 48), (35, 48), (35, 48), (35, 48), (35, 48), (35, 48), (35, 48), (35, 48), (35, 48)],
    3: [(57, 57), (57, 57), (57, 57), (57, 57), (57, 57), (12, 48), (12, 48), (12, 48), (34, 54), (6, 57), (6, 57), (6, 57), (6, 57), (6, 57), (6, 57), (6, 57), (57, 48), (57, 48), (57, 48), (57, 48), (34, 54), (34, 54), (34, 54), (34, 54), (34, 54), (34, 54), (34, 54), (34, 54), (34, 54), (34, 54)],
    4: [(51, 57), (51, 57), (42, 57), (6, 57), (27, 57), (27, 57), (27, 57), (42, 57), (42, 57), (42, 57), (6, 57), (57, 57), (6, 57), (57, 57), (36, 57), (36, 57), (36, 57), (6, 57), (6, 57), (27, 57), (27, 57), (27, 57), (42, 57), (42, 57), (42, 57), (27, 57), (27, 57), (27, 57)],
}

# Solve remaining levels
for level in range(5, 8):
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
