"""SU15 solver — vacuum puzzle. Click near fruits to pull them toward goal.
Deepcopy BFS with dynamic click positions near current fruit locations."""
import importlib.util, copy, hashlib
import arc_agi
from collections import deque
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('su15', 'environment_files/su15/4c352900/su15.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

CLICK = GameAction.ACTION6
BASELINES = [18, 28, 50, 151, 18, 31, 50, 179, 41]


def pixel_hash(g):
    frame = g.get_pixels(0, 0, 64, 64)
    return hashlib.md5(frame[3:].tobytes()).hexdigest()


def get_clicks(g, radius=12, step=3):
    """Click positions near fruits, goals, and keys."""
    clicks = set()
    for tag in ["fruit", "goal", "key"]:
        for sp in g.current_level.get_sprites_by_tag(tag):
            cx, cy = sp.x + sp.width // 2, sp.y + sp.height // 2
            for dx in range(-radius, radius + 1, step):
                for dy in range(-radius, radius + 1, step):
                    nx, ny = cx + dx, cy + dy
                    if 10 <= ny < 63 and 0 <= nx < 64:
                        clicks.add((nx, ny))
    return sorted(clicks)


def bfs_solve(level_idx, max_depth=None):
    g0 = mod.Su15()
    g0.set_level(level_idx)
    baseline = BASELINES[level_idx]
    limit = max_depth or min(baseline + 10, 200)

    start = pixel_hash(g0)
    print(f"Level {level_idx+1}: baseline={baseline}, limit={limit}", flush=True)

    queue = deque([(g0, [])])
    visited = {start}
    iters = 0

    while queue:
        g, path = queue.popleft()
        iters += 1
        if iters % 2000 == 0:
            fruits = g.current_level.get_sprites_by_tag('fruit')
            fp = f"({fruits[0].x},{fruits[0].y})" if fruits else "none"
            print(f"  iter={iters} q={len(queue)} d={len(path)} v={len(visited)} fruit={fp}", flush=True)
        if len(path) >= limit:
            continue

        clicks = get_clicks(g)
        for (cx, cy) in clicks:
            g2 = copy.deepcopy(g)
            g2.perform_action(ActionInput(id=CLICK, data={'x': cx, 'y': cy}))
            if g2._current_level_index > level_idx or g2._state.name == "WIN":
                result = path + [(cx, cy)]
                print(f"  FOUND! {len(result)} clicks ({iters} iters)", flush=True)
                return result
            if g2._state.name == "GAME_OVER":
                continue
            h = pixel_hash(g2)
            if h not in visited:
                visited.add(h)
                queue.append((g2, path + [(cx, cy)]))

    print(f"  No solution ({iters} iters, {len(visited)} states)", flush=True)
    return None


if __name__ == "__main__":
    all_solutions = {}
    for level in range(9):
        path = bfs_solve(level)
        if path:
            all_solutions[level] = path
        else:
            print(f"  FAILED", flush=True)
            break
        print(flush=True)

    print("=" * 60, flush=True)
    total = sum(len(p) for p in all_solutions.values())
    baseline = sum(BASELINES)
    print(f"Solved {len(all_solutions)}/9, Total: {total}, Baseline: {baseline}", flush=True)

    if len(all_solutions) == 9:
        print("\nVerifying with API...", flush=True)
        arcade = arc_agi.Arcade()
        env = arcade.make("su15-4c352900", render_mode=None)
        result = env.reset()
        for level_idx in range(9):
            for (x, y) in all_solutions[level_idx]:
                result = env.step(CLICK, data={"x": x, "y": y})
            print(f"  Level {level_idx+1}: {len(all_solutions[level_idx])} clicks, levels={result.levels_completed}")
        print(f"\nTotal: {total}, State: {result.state}")
        assert str(result.state) == "GameState.WIN"
        print("ALL VERIFIED!")
