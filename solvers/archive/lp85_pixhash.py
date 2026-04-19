"""LP85 solver — game-engine BFS with pixel hash for fast state dedup."""
import importlib.util
import hashlib
import arc_agi
from collections import deque
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('lp85', 'environment_files/lp85/305b61c3/lp85.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

CLICK = GameAction.ACTION6


def get_buttons(g):
    s, ox, oy = g.camera._calculate_scale_and_offset()
    clicks = []
    for cs in g.current_level.get_sprites_by_tag("sys_click"):
        dx = cs.x * s + ox + cs.width * s // 2
        dy = cs.y * s + oy + cs.height * s // 2
        clicks.append((dx, dy))
    return clicks


def pixel_hash(g, grid_w, grid_h):
    """Fast hash of the game pixel state (excluding counter area)."""
    frame = g.get_pixels(0, 0, grid_w, grid_h)
    # Hash only the game area, excluding row 0 (counter)
    return hashlib.md5(frame[1:].tobytes()).hexdigest()


def replay(level_idx, path, btns):
    g = mod.Lp85()
    g.set_level(level_idx)
    for i in path:
        g.perform_action(ActionInput(id=CLICK, data={"x": btns[i][0], "y": btns[i][1]}))
    return g


baselines = [33, 22, 31, 23, 33, 34, 73, 173]


def bfs_solve(level_idx, max_depth=None):
    g0 = mod.Lp85()
    g0.set_level(level_idx)
    btns = get_buttons(g0)
    grid_w, grid_h = g0.current_level.grid_size or (16, 16)
    baseline = baselines[level_idx]
    limit = max_depth or min(baseline + 5, 200)

    start_hash = pixel_hash(g0, grid_w, grid_h)
    print(f"Level {level_idx+1}: baseline={baseline}, limit={limit}, buttons={len(btns)}", flush=True)

    queue = deque()
    queue.append([])
    visited = {start_hash}
    iters = 0

    while queue:
        path = queue.popleft()
        iters += 1
        if iters % 10000 == 0:
            print(f"  iter={iters} q={len(queue)} d={len(path)} v={len(visited)}", flush=True)
        if len(path) >= limit:
            continue

        for i in range(len(btns)):
            new_path = path + [i]
            g = replay(level_idx, new_path, btns)

            if g._current_level_index > level_idx or g._state.name == "WIN":
                clicks = [(btns[j][0], btns[j][1]) for j in new_path]
                print(f"  FOUND! {len(new_path)} clicks ({iters} iters)", flush=True)
                return clicks

            if g._state.name == "GAME_OVER":
                continue

            h = pixel_hash(g, grid_w, grid_h)
            if h not in visited:
                visited.add(h)
                queue.append(new_path)

    print(f"  No solution ({iters} iters, {len(visited)} states)", flush=True)
    return None


if __name__ == "__main__":
    all_solutions = {}
    for level in range(8):
        path = bfs_solve(level)
        if path:
            all_solutions[level] = path
        else:
            print(f"  FAILED", flush=True)
            break
        print(flush=True)

    print("=" * 60, flush=True)
    total = sum(len(p) for p in all_solutions.values())
    baseline = sum(baselines)
    print(f"Solved {len(all_solutions)}/8, Total: {total}, Baseline: {baseline}", flush=True)

    if len(all_solutions) == 8:
        print("\nVerifying with API...", flush=True)
        arcade = arc_agi.Arcade()
        env = arcade.make("lp85-305b61c3", render_mode=None)
        result = env.reset()
        api_total = 0
        for level_idx in range(8):
            for (dx, dy) in all_solutions[level_idx]:
                result = env.step(CLICK, data={"x": dx, "y": dy})
                api_total += 1
            print(f"  Level {level_idx+1}: {len(all_solutions[level_idx])} clicks, levels={result.levels_completed}")
        print(f"\nTotal: {api_total}, State: {result.state}")
        assert str(result.state) == "GameState.WIN"
        print("ALL VERIFIED!")
