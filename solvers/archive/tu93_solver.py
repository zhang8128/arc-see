"""TU93 solver — grid puzzle with moving projectiles/enemies.
BFS with replay from scratch. State = player pos + all tagged sprite positions.
"""
import sys
import importlib.util
from collections import deque
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('tu93', 'environment_files/tu93/2b534c15/tu93.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

UP, DOWN, LEFT, RIGHT = GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4
DIRS = [UP, DOWN, LEFT, RIGHT]
DIR_NAMES = ["U", "D", "L", "R"]


def act(g, d):
    return g.perform_action(ActionInput(id=d))


def get_state(g):
    """Hash the game state for deduplication."""
    player = g.current_level.get_sprites_by_tag("albwnmiahg")
    # Include all moving entity positions
    movers = (g.current_level.get_sprites_by_tag("vllvfeggte") +
              g.current_level.get_sprites_by_tag("zzuxulcort") +
              g.current_level.get_sprites_by_tag("natiyqayts"))
    p = tuple((s.x, s.y) for s in player) if player else ()
    m = tuple(sorted((s.x, s.y, s.rotation) for s in movers))
    return (p, m)


def replay(level_idx, actions):
    g = mod.Tu93()
    g.set_level(level_idx)
    for d in actions:
        act(g, d)
    return g


def bfs_solve(level_idx, max_depth=None):
    g0 = mod.Tu93()
    g0.set_level(level_idx)
    baseline = [19, 15, 34, 42, 76, 91, 47, 23, 31][level_idx]
    limit = max_depth or min(baseline + 5, 100)

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


def actions_to_string(actions):
    return " ".join(f"ACTION{DIRS.index(a)+1}" for a in actions)


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
    baseline = sum([19, 15, 34, 42, 76, 91, 47, 23, 31])
    print(f"Solved {len(all_solutions)}/9, Total: {total}, Baseline: {baseline}", flush=True)
