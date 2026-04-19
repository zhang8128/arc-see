"""RE86 solver — keyboard game with 5 actions. TU93-style BFS with replay."""
import sys
import importlib.util
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


def get_state(g):
    """Hash game state using pixel rendering."""
    import hashlib
    frame = g.get_pixels(0, 0, 64, 64)
    return hashlib.md5(frame[2:].tobytes()).hexdigest()


def replay(level_idx, actions):
    g = mod.Re86()
    g.set_level(level_idx)
    for d in actions:
        act(g, d)
    return g


def bfs_solve(level_idx, max_depth=None):
    g0 = mod.Re86()
    g0.set_level(level_idx)
    baseline = [28, 38, 198, 57, 84, 117, 328, 221][level_idx]
    limit = max_depth or min(baseline + 5, 120)

    start = get_state(g0)
    print(f"Level {level_idx+1}: baseline={baseline}, limit={limit}", flush=True)

    queue = deque()
    queue.append([])
    visited = {start}
    iters = 0

    while queue:
        path = queue.popleft()
        iters += 1
        if iters % 5000 == 0:
            print(f"  iter={iters} q={len(queue)} d={len(path)} v={len(visited)}", flush=True)

        if len(path) >= limit:
            continue

        for d in DIRS:
            new_path = path + [d]
            g = replay(level_idx, new_path)

            if g._current_level_index > level_idx or g._state.name == "WIN":
                names = "".join(NAMES[DIRS.index(a)] for a in new_path)
                print(f"  FOUND! {len(new_path)} moves ({iters} iters): {names}", flush=True)
                return new_path

            if g._state.name == "GAME_OVER":
                continue

            state = get_state(g)
            if state not in visited:
                visited.add(state)
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
    baseline = sum([28, 38, 198, 57, 84, 117, 328, 221])
    print(f"Solved {len(all_solutions)}/8, Total: {total}, Baseline: {baseline}", flush=True)

    if len(all_solutions) == 8:
        print("\nVerifying with API...", flush=True)
        arcade = arc_agi.Arcade()
        env = arcade.make("re86-4e57566e", render_mode=None)
        result = env.reset()
        api_total = 0
        for level_idx in range(8):
            for a in all_solutions[level_idx]:
                result = env.step(a)
                api_total += 1
            print(f"  Level {level_idx+1}: {len(all_solutions[level_idx])} moves, "
                  f"levels={result.levels_completed}")
        print(f"\nTotal: {api_total}, State: {result.state}")
        assert str(result.state) == "GameState.WIN"
        print("ALL VERIFIED!")
