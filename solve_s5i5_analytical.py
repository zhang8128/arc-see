#!/usr/bin/env python3
"""S5I5 analytical solver — vector displacement puzzle.

Each click applies a displacement to markers. Find minimum clicks to move
markers from start to target positions. This is integer linear programming.
"""
import importlib.util, copy, itertools
import arc_agi
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('s5i5', 'environment_files/s5i5/a48e4b1d/s5i5.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

CLICK = GameAction.ACTION6
BASELINES = [19, 57, 85, 203, 82, 30, 76, 56]


def get_marker_positions(g):
    """Get all marker (zylvdxoiuq) positions."""
    return {id(s): (s.x, s.y) for s in g.current_level.get_sprites() if 'zylvdxoiuq' in s.tags}


def get_target_positions(g):
    """Get all target (cpdhnkdobh) positions."""
    return [(s.x, s.y) for s in g.current_level.get_sprites() if 'cpdhnkdobh' in s.tags]


def discover_click_vectors(g):
    """For each unique click, determine the displacement vector on each marker."""
    import numpy as np, hashlib
    f0 = g.get_pixels(0, 0, 64, 64)
    markers_before = [(s.x, s.y) for s in g.current_level.get_sprites() if 'zylvdxoiuq' in s.tags]

    seen_hashes = {}
    click_vectors = []

    for x in range(64):
        for y in range(64):
            g2 = copy.deepcopy(g)
            g2.perform_action(ActionInput(id=CLICK, data={'x': x, 'y': y}))
            f1 = g2.get_pixels(0, 0, 64, 64)
            if np.array_equal(f0, f1):
                continue
            h = hashlib.md5(f1.tobytes()).hexdigest()
            if h in seen_hashes:
                continue
            seen_hashes[h] = True

            markers_after = [(s.x, s.y) for s in g2.current_level.get_sprites() if 'zylvdxoiuq' in s.tags]
            # Compute displacement for each marker
            displacements = []
            for (bx, by), (ax, ay) in zip(markers_before, markers_after):
                displacements.append((ax - bx, ay - by))

            click_vectors.append({
                'pos': (x, y),
                'displacements': tuple(displacements),  # per-marker (dx, dy)
            })

    return click_vectors


def solve_level(level_idx):
    """Solve a level analytically."""
    g = mod.S5i5()
    g.set_level(level_idx)

    markers = [(s.x, s.y) for s in g.current_level.get_sprites() if 'zylvdxoiuq' in s.tags]
    targets = [(s.x, s.y) for s in g.current_level.get_sprites() if 'cpdhnkdobh' in s.tags]

    print(f"\nL{level_idx+1} (baseline {BASELINES[level_idx]}):", flush=True)
    print(f"  Markers: {markers}", flush=True)
    print(f"  Targets: {targets}", flush=True)

    if len(markers) != len(targets):
        print(f"  WARNING: {len(markers)} markers but {len(targets)} targets", flush=True)

    # Sort targets to match markers (by proximity)
    target_displacements = []
    for mx, my in markers:
        best = min(targets, key=lambda t: abs(t[0]-mx) + abs(t[1]-my))
        target_displacements.append((best[0] - mx, best[1] - my))
    print(f"  Target displacements: {target_displacements}", flush=True)

    # Discover click vectors
    print(f"  Discovering click vectors...", flush=True)
    clicks = discover_click_vectors(g)
    print(f"  Found {len(clicks)} unique clicks:", flush=True)
    for c in clicks:
        print(f"    click{c['pos']}: displacements={c['displacements']}", flush=True)

    # Flatten: each marker has (dx, dy), so total dimensions = 2 * num_markers
    # Need: sum of (count_i * vector_i) = target_vector for all dimensions
    n_markers = len(markers)
    n_dims = 2 * n_markers
    n_clicks = len(clicks)

    # Build target vector
    target_vec = []
    for dx, dy in target_displacements:
        target_vec.extend([dx, dy])

    # Build click matrix: each click is a column vector
    click_matrix = []
    for c in clicks:
        vec = []
        for dx, dy in c['displacements']:
            vec.extend([dx, dy])
        click_matrix.append(vec)

    print(f"  Target vector: {target_vec}", flush=True)
    print(f"  Dimensions: {n_dims}, Click vectors: {n_clicks}", flush=True)

    # For small problems, use BFS on the abstract state (marker positions)
    # State = tuple of marker positions, Actions = click vectors
    from collections import deque

    start_state = tuple(p for mx, my in markers for p in (mx, my))
    goal_state = tuple(p for (mx, my), (dx, dy) in zip(markers, target_displacements) for p in (mx+dx, my+dy))

    print(f"  Start: {start_state}", flush=True)
    print(f"  Goal:  {goal_state}", flush=True)

    # Abstract BFS — pure Python, no deepcopy needed!
    queue = deque([(start_state, [])])
    visited = {start_state}
    limit = BASELINES[level_idx] + 2
    iters = 0

    while queue:
        state, path = queue.popleft()
        iters += 1
        if iters % 100000 == 0:
            print(f"    iter={iters} q={len(queue)} d={len(path)} v={len(visited)}", flush=True)
        if len(path) >= limit:
            continue

        for i, c in enumerate(clicks):
            # Apply click vector to state
            new_state = list(state)
            valid = True
            for j, (dx, dy) in enumerate(c['displacements']):
                new_state[2*j] += dx
                new_state[2*j+1] += dy
                # Bounds check (markers must stay in 0-63 range)
                if not (0 <= new_state[2*j] <= 63 and 0 <= new_state[2*j+1] <= 63):
                    valid = False
                    break
            if not valid:
                continue
            new_state = tuple(new_state)

            if new_state == goal_state:
                result = path + [i]
                print(f"  FOUND! {len(result)} clicks ({iters} iters)", flush=True)
                return [clicks[idx]['pos'] for idx in result]

            if new_state not in visited:
                visited.add(new_state)
                queue.append((new_state, path + [i]))

    print(f"  No solution ({iters} iters, {len(visited)} states)", flush=True)
    return None


# Solve all levels
all_solutions = {}
for level in range(8):
    result = solve_level(level)
    if result:
        all_solutions[level] = result
    else:
        print(f"  FAILED", flush=True)
        break

# API verification
if all_solutions:
    print("\n=== API Verification ===", flush=True)
    arcade = arc_agi.Arcade()
    env = arcade.make("s5i5-a48e4b1d", render_mode=None)
    obs = env.reset()
    total = 0
    for level in range(len(all_solutions)):
        for x, y in all_solutions[level]:
            obs = env.step(CLICK, data={"x": x, "y": y})
        total += len(all_solutions[level])
        print(f"  L{level+1}: {len(all_solutions[level]):3d} clicks (baseline {BASELINES[level]}), levels_completed={obs.levels_completed}", flush=True)

    print(f"\nTotal: {total} clicks (baselines: {sum(BASELINES[:len(all_solutions)])})", flush=True)
    print(f"State: {obs.state}", flush=True)

    print("\nSOLUTIONS = {", flush=True)
    for level in sorted(all_solutions.keys()):
        print(f"    {level+1}: {all_solutions[level]},", flush=True)
    print("}", flush=True)
