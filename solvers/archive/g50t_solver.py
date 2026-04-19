"""G50T solver — keyboard game with 5 actions. BFS with replay."""
import sys
import importlib.util
from collections import deque
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('g50t', 'environment_files/g50t/5849a774/g50t.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

UP, DOWN, LEFT, RIGHT, ACT5 = (GameAction.ACTION1, GameAction.ACTION2,
                                 GameAction.ACTION3, GameAction.ACTION4, GameAction.ACTION5)
DIRS = [UP, DOWN, LEFT, RIGHT, ACT5]
DIR_NAMES = ["U", "D", "L", "R", "5"]


def act(g, d):
    return g.perform_action(ActionInput(id=d))


def get_state(g):
    """Hash game state for dedup — exclude counter sprite."""
    counter_tag = "ppfvilwwnk"
    all_sprites = g.current_level.get_sprites()
    return tuple(sorted((s.name, s.x, s.y, s.rotation) for s in all_sprites
                        if s.is_visible and counter_tag not in s.tags))


def replay(level_idx, actions):
    g = mod.G50t()
    g.set_level(level_idx)
    for d in actions:
        act(g, d)
    return g


def bfs_solve(level_idx, max_depth=None):
    g0 = mod.G50t()
    g0.set_level(level_idx)
    baseline = [51, 175, 86, 52, 96, 48, 67][level_idx]
    limit = max_depth or min(baseline + 5, 200)

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
                names = "".join(DIR_NAMES[DIRS.index(a)] for a in new_path)
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
    for level in range(7):
        path = bfs_solve(level)
        if path:
            all_solutions[level] = path
        else:
            print(f"  FAILED", flush=True)
            break
        print(flush=True)

    print("=" * 60, flush=True)
    total = sum(len(p) for p in all_solutions.values())
    baseline = sum([51, 175, 86, 52, 96, 48, 67])
    print(f"Solved {len(all_solutions)}/7, Total: {total}, Baseline: {baseline}", flush=True)
