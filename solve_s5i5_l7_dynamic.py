#!/usr/bin/env python3
"""S5I5 L7 solver — BFS with dynamic click re-discovery.

Every 50K states, re-scan for clicks from the state closest to target
that hasn't been scanned yet. New clicks are added to the global set
and BFS continues from ALL existing states.
"""
import importlib.util, copy, hashlib, numpy as np, time, sys
from collections import deque
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('s5i5', 'environment_files/s5i5/a48e4b1d/s5i5.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
CLICK = GameAction.ACTION6

def pixel_hash(g):
    return hashlib.md5(g.get_pixels(0, 0, 64, 64).tobytes()).hexdigest()

def marker_pos(g):
    return tuple((s.x, s.y) for s in g.current_level.get_sprites() if 'zylvdxoiuq' in s.tags)

def discover_clicks(g):
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
    return set(seen.values())

def target_dist(mk, target):
    return sum(abs(a-b) for pair_m, pair_t in zip(mk, target)
               for a, b in zip(pair_m, pair_t))

g0 = mod.S5i5()
g0.set_level(6)
target = ((24, 15), (21, 6))

# Global click set + scanned state hashes
all_clicks = discover_clicks(g0)
scanned_hashes = {pixel_hash(g0)}
print(f"Initial: {len(all_clicks)} clicks", flush=True)

# BFS state: pixel_hash -> (game_obj, path)
visited = {}
start_h = pixel_hash(g0)
visited[start_h] = (g0, [])
queue = deque([(g0, [], start_h)])

t0 = time.time()
iters = 0
best_dist = target_dist(marker_pos(g0), target)
rescan_interval = 20000  # re-scan every N new states
states_since_scan = 0

while queue:
    g, path, g_hash = queue.popleft()
    iters += 1

    if iters % 10000 == 0:
        mk = marker_pos(g)
        print(f"  iter={iters} q={len(queue)} d={len(path)} v={len(visited)} "
              f"clicks={len(all_clicks)} best_dist={best_dist} t={time.time()-t0:.0f}s", flush=True)

    if len(path) >= 200:
        continue

    for cx, cy in sorted(all_clicks):
        g2 = copy.deepcopy(g)
        g2.perform_action(ActionInput(id=CLICK, data={'x': cx, 'y': cy}))

        if g2._current_level_index > 6 or g2._state.name == "WIN":
            result = path + [(cx, cy)]
            print(f"\nFOUND! {len(result)} clicks ({iters} iters, {time.time()-t0:.0f}s)", flush=True)
            print(f"Solution: {result}", flush=True)
            sys.exit(0)

        if g2._state.name == "GAME_OVER":
            continue

        h = pixel_hash(g2)
        if h not in visited:
            visited[h] = (g2, path + [(cx, cy)])
            queue.append((g2, path + [(cx, cy)], h))
            states_since_scan += 1

            mk = marker_pos(g2)
            d = target_dist(mk, target)
            if d < best_dist:
                best_dist = d
                print(f"    New best: {mk} dist={d} at depth {len(path)+1}", flush=True)

    # Periodically re-scan for new clicks
    if states_since_scan >= rescan_interval:
        states_since_scan = 0
        # Find unscanned state closest to target
        best_scan_h = None
        best_scan_dist = 999
        for h, (g_s, p_s) in visited.items():
            if h in scanned_hashes:
                continue
            mk = marker_pos(g_s)
            d = target_dist(mk, target)
            if d < best_scan_dist:
                best_scan_dist = d
                best_scan_h = h

        if best_scan_h:
            g_scan, _ = visited[best_scan_h]
            mk = marker_pos(g_scan)
            print(f"  Re-scanning from {mk} (dist={best_scan_dist})...", flush=True)
            new_clicks = discover_clicks(g_scan)
            added = new_clicks - all_clicks
            scanned_hashes.add(best_scan_h)
            if added:
                all_clicks |= added
                print(f"    +{len(added)} new clicks! Total={len(all_clicks)}", flush=True)
                # Re-queue ALL visited states to try new clicks
                for h_old, (g_old, p_old) in visited.items():
                    if len(p_old) < 200:
                        queue.append((g_old, p_old, h_old))
                print(f"    Re-queued {len(visited)} states", flush=True)
            else:
                print(f"    No new clicks from {mk}", flush=True)

print(f"\nNo solution ({iters} iters, {len(visited)} states, {time.time()-t0:.0f}s)", flush=True)
print(f"Best distance to target: {best_dist}", flush=True)
