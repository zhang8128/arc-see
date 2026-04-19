#!/usr/bin/env python3
"""S5I5 L7 solver — iterative click discovery BFS.

The trick: click positions change as bars move. Scan for new clicks
at frontier states when BFS stalls. Repeat until target found.
"""
import importlib.util, copy, hashlib, numpy as np, time
from collections import deque
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('s5i5', 'environment_files/s5i5/a48e4b1d/s5i5.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

CLICK = GameAction.ACTION6


def discover_clicks(g):
    """Full pixel scan to find all unique click actions from a state."""
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


def marker_key(g):
    return tuple((s.x, s.y) for s in g.current_level.get_sprites() if 'zylvdxoiuq' in s.tags)


def manhattan_to_target(mk, target):
    return sum(abs(a - b) for pair_m, pair_t in zip(mk, target)
               for a, b in zip(pair_m, pair_t))


g0 = mod.S5i5()
g0.set_level(6)
target = marker_key(g0)  # will compute after scanning targets
targets_sprites = [(s.x, s.y) for s in g0.current_level.get_sprites() if 'cpdhnkdobh' in s.tags]
markers_sprites = [(s.x, s.y) for s in g0.current_level.get_sprites() if 'zylvdxoiuq' in s.tags]
print(f"Markers: {markers_sprites}", flush=True)
print(f"Targets: {targets_sprites}", flush=True)

# Iterative click discovery + BFS
all_clicks = set()
visited = {}  # marker_key -> (game_state, path)
limit = 96
round_num = 0

# Seed: discover from initial state
new_clicks = discover_clicks(g0)
all_clicks |= new_clicks
print(f"Round 0: {len(new_clicks)} clicks from initial state. Total: {len(all_clicks)}", flush=True)

start_key = marker_key(g0)
visited[start_key] = (g0, [])

while True:
    round_num += 1
    t0 = time.time()

    # BFS with current click set
    queue = deque()
    for mk, (g, path) in visited.items():
        queue.append((g, path))

    new_states = 0
    best_dist = min((manhattan_to_target(mk, tuple(targets_sprites))
                     for mk in visited), default=999)
    best_mk = None

    while queue:
        g, path = queue.popleft()
        if len(path) >= limit:
            continue
        for (cx, cy) in sorted(all_clicks):
            g2 = copy.deepcopy(g)
            g2.perform_action(ActionInput(id=CLICK, data={'x': cx, 'y': cy}))
            if g2._current_level_index > 6 or g2._state.name == "WIN":
                result = path + [(cx, cy)]
                print(f"\nFOUND! {len(result)} clicks (round {round_num})", flush=True)
                print(f"Solution: {result}", flush=True)
                # Verify
                import arc_agi
                arcade = arc_agi.Arcade()
                env = arcade.make("s5i5-a48e4b1d", render_mode=None)
                obs = env.reset()
                # Play L1-L6 first
                from solution_s5i5_clicks import L1_L6
                for lx, ly in L1_L6:
                    obs = env.step(CLICK, data={"x": lx, "y": ly})
                for rx, ry in result:
                    obs = env.step(CLICK, data={"x": rx, "y": ry})
                print(f"Verify: levels_completed={obs.levels_completed}", flush=True)
                exit(0)
            if g2._state.name == "GAME_OVER":
                continue
            mk = marker_key(g2)
            if mk not in visited:
                visited[mk] = (g2, path + [(cx, cy)])
                queue.append((g2, path + [(cx, cy)]))
                new_states += 1
                dist = manhattan_to_target(mk, tuple(targets_sprites))
                if dist < best_dist:
                    best_dist = dist
                    best_mk = mk

    elapsed = time.time() - t0
    print(f"Round {round_num}: BFS found {new_states} new states ({len(visited)} total), "
          f"best_dist={best_dist}, t={elapsed:.0f}s", flush=True)

    if new_states == 0 and round_num > 1:
        # BFS stalled AND we already tried discovering new clicks
        print("BFS stalled with no new states. Giving up.", flush=True)
        break

    # Discover new clicks from frontier states (closest to target)
    # Pick up to 5 states closest to target that we haven't scanned yet
    scanned = set()
    candidates = sorted(visited.keys(),
                       key=lambda mk: manhattan_to_target(mk, tuple(targets_sprites)))

    new_click_count = 0
    for mk in candidates[:5]:
        if mk in scanned:
            continue
        scanned.add(mk)
        g_state, _ = visited[mk]
        found = discover_clicks(g_state)
        added = found - all_clicks
        if added:
            all_clicks |= added
            new_click_count += len(added)
            print(f"  Scanned {mk}: +{len(added)} new clicks (total {len(all_clicks)})", flush=True)

    if new_click_count == 0:
        # No new clicks found from closest states, try more diverse states
        for mk in candidates[5:20]:
            if mk in scanned:
                continue
            scanned.add(mk)
            g_state, _ = visited[mk]
            found = discover_clicks(g_state)
            added = found - all_clicks
            if added:
                all_clicks |= added
                new_click_count += len(added)
                print(f"  Scanned {mk}: +{len(added)} new clicks (total {len(all_clicks)})", flush=True)
                break  # found new clicks, go back to BFS

    if new_click_count == 0:
        print(f"No new clicks found from {len(scanned)} scanned states. Stuck.", flush=True)
        break

    print(f"  Discovered {new_click_count} new clicks. Re-running BFS...", flush=True)

# Print reachable state summary
print(f"\nTotal reachable marker states: {len(visited)}", flush=True)
print(f"Total click positions: {len(all_clicks)}", flush=True)
closest = min(visited.keys(), key=lambda mk: manhattan_to_target(mk, tuple(targets_sprites)))
print(f"Closest to target: {closest} (dist={manhattan_to_target(closest, tuple(targets_sprites))})", flush=True)
