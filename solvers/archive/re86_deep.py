"""RE86 solver — keyboard game with 5 actions. Deepcopy BFS + pixel hash."""
import importlib.util, copy, hashlib
import arc_agi
from collections import deque
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('re86', 'environment_files/re86/4e57566e/re86.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

DIRS = [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4, GameAction.ACTION5]
NAMES = ["U", "D", "L", "R", "5"]


def act(g, d):
    return g.perform_action(ActionInput(id=d))


def pixel_hash(g):
    frame = g.get_pixels(0, 0, 64, 64)
    return hashlib.md5(frame[2:].tobytes()).hexdigest()


def bfs_solve(level_idx, max_depth=None):
    g0 = mod.Re86()
    g0.set_level(level_idx)
    baseline = [28, 38, 198, 57, 84, 117, 328, 221][level_idx]
    limit = max_depth or min(baseline + 10, 250)

    start = pixel_hash(g0)
    print(f"Level {level_idx+1}: baseline={baseline}, limit={limit}", flush=True)

    queue = deque()
    queue.append((g0, []))
    visited = {start}
    iters = 0

    while queue:
        g, path = queue.popleft()
        iters += 1
        if iters % 5000 == 0:
            print(f"  iter={iters} q={len(queue)} d={len(path)} v={len(visited)}", flush=True)

        if len(path) >= limit:
            continue

        for i, d in enumerate(DIRS):
            g2 = copy.deepcopy(g)
            act(g2, d)

            if g2._current_level_index > level_idx or g2._state.name == "WIN":
                result = path + [i]
                names = "".join(NAMES[j] for j in result)
                print(f"  FOUND! {len(result)} moves ({iters} iters): {names}", flush=True)
                return result

            if g2._state.name == "GAME_OVER":
                continue

            h = pixel_hash(g2)
            if h not in visited:
                visited.add(h)
                queue.append((g2, path + [i]))

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
    baseline = sum([28, 38, 198, 57, 84, 117, 328, 221])
    print(f"Solved {len(all_solutions)}/8, Total: {total}, Baseline: {baseline}", flush=True)

    if len(all_solutions) == 8:
        print("\nVerifying with API...", flush=True)
        arcade = arc_agi.Arcade()
        env = arcade.make("re86-4e57566e", render_mode=None)
        result = env.reset()
        for level_idx in range(8):
            for i in all_solutions[level_idx]:
                result = env.step(DIRS[i])
            print(f"  Level {level_idx+1}: {len(all_solutions[level_idx])} moves, "
                  f"levels={result.levels_completed}")
        print(f"\nTotal: {total}, State: {result.state}")
        assert str(result.state) == "GameState.WIN"
        print("ALL VERIFIED!")
