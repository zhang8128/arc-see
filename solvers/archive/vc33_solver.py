"""VC33 solver — conveyor belt sliding puzzle. BFS with replay."""
import sys
import importlib.util
from collections import deque
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('vc33', 'environment_files/vc33/9851e02b/vc33.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

CLICK = GameAction.ACTION6


def act(g, dx, dy):
    return g.perform_action(ActionInput(id=CLICK, data={'x': dx, 'y': dy}))


def grid_to_display(g, gx, gy):
    s, ox, oy = g.camera._calculate_scale_and_offset()
    return gx * s + ox, gy * s + oy


def get_clickables(g):
    clicks = []
    for s in g.current_level.get_sprites_by_tag('ZGd'):
        dx, dy = grid_to_display(g, s.x + s.width // 2, s.y + s.height // 2)
        clicks.append((dx, dy))
    for s in g.current_level.get_sprites_by_tag('zHk'):
        if g.krt(s):
            dx, dy = grid_to_display(g, s.x + s.width // 2, s.y + s.height // 2)
            clicks.append((dx, dy))
    return clicks


def get_state(g):
    hqb = g.current_level.get_sprites_by_tag('HQB')
    rdn = g.current_level.get_sprites_by_tag('rDn')
    pieces = tuple(sorted((s.x, s.y) for s in hqb))
    tracks = tuple(sorted((s.x, s.y, s.width, s.height) for s in rdn))
    return (pieces, tracks)


def replay(level_idx, path):
    g = mod.Vc33()
    g.set_level(level_idx)
    for (dx, dy) in path:
        act(g, dx, dy)
    return g


def bfs_solve(level_idx, max_depth=None):
    g0 = mod.Vc33()
    g0.set_level(level_idx)
    baseline = [6, 13, 31, 59, 92, 24, 82][level_idx]
    limit = max_depth or min(baseline + 5, 100)

    start_state = get_state(g0)
    start_clicks = get_clickables(g0)
    print(f"Level {level_idx+1}: limit={limit}, baseline={baseline}, clickables={len(start_clicks)}", flush=True)

    queue = deque()
    queue.append([])
    visited = {start_state}
    iters = 0

    while queue:
        path = queue.popleft()
        iters += 1
        if iters % 2000 == 0:
            print(f"  iter={iters} q={len(queue)} d={len(path)} v={len(visited)}", flush=True)

        if len(path) >= limit:
            continue

        g = replay(level_idx, path)

        if g._current_level_index > level_idx or g._state.name == "WIN":
            print(f"  FOUND! {len(path)} clicks ({iters} iters)", flush=True)
            return path

        clicks = get_clickables(g)

        for (dx, dy) in clicks:
            new_path = path + [(dx, dy)]
            g2 = replay(level_idx, new_path)

            if g2._current_level_index > level_idx or g2._state.name == "WIN":
                print(f"  FOUND! {len(new_path)} clicks ({iters} iters)", flush=True)
                return new_path

            state = get_state(g2)
            if state not in visited:
                visited.add(state)
                queue.append(new_path)

    print(f"  No solution ({iters} iters, {len(visited)} states)", flush=True)
    return None


if __name__ == "__main__":
    all_solutions = {}
    for level in range(7):
        path = bfs_solve(level)
        if path:
            all_solutions[level] = path
            print(f"  Solution: {path}", flush=True)
        else:
            print(f"  FAILED", flush=True)
            break
        print(flush=True)

    print("=" * 60, flush=True)
    total = sum(len(p) for p in all_solutions.values())
    baseline = sum([6, 13, 31, 59, 92, 24, 82])
    print(f"Total: {total} clicks, Baseline: {baseline}", flush=True)
