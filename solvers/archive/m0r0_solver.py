"""M0R0 solver — mirror movement puzzle. Pieces move in mirrored directions.
BFS with state = (piece_positions, cancelled_set)."""
import importlib.util, copy
import arc_agi
from collections import deque
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('m0r0', 'environment_files/m0r0/dadda488/m0r0.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

UP, DOWN, LEFT, RIGHT = GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4
DIRS = [UP, DOWN, LEFT, RIGHT]
NAMES = "UDLR"
PIECE_NAMES = ["qzfkx-ubwff-idtiq", "qzfkx-ubwff-crkfz", "qzfkx-kncqr-idtiq", "qzfkx-kncqr-crkfz"]
BASELINES = [30, 209, 83, 86, 436, 126]


def get_state(g):
    positions = []
    for pn in PIECE_NAMES:
        sps = g.current_level.get_sprites_by_name(pn)
        if sps:
            positions.append((sps[0].x, sps[0].y))
        else:
            positions.append(None)
    return (tuple(positions), frozenset(g.fqunj))


def bfs_solve(level_idx, max_depth=None):
    g0 = mod.M0r0()
    g0.set_level(level_idx)
    baseline = BASELINES[level_idx]
    limit = max_depth or min(baseline + 10, 250)

    start = get_state(g0)
    print(f"Level {level_idx+1}: baseline={baseline}, limit={limit}", flush=True)

    queue = deque([(g0, "")])
    visited = {start}
    iters = 0

    while queue:
        g, path = queue.popleft()
        iters += 1
        if iters % 10000 == 0:
            print(f"  iter={iters} q={len(queue)} d={len(path)} v={len(visited)}", flush=True)
        if len(path) >= limit:
            continue

        for i, d in enumerate(DIRS):
            g2 = copy.deepcopy(g)
            g2.perform_action(ActionInput(id=d))
            if g2._current_level_index > level_idx or g2._state.name == "WIN":
                result = path + NAMES[i]
                print(f"  FOUND! {len(result)} moves ({iters} iters): {result}", flush=True)
                return result
            if g2._state.name == "GAME_OVER":
                continue
            st = get_state(g2)
            if st not in visited:
                visited.add(st)
                queue.append((g2, path + NAMES[i]))

    print(f"  No solution ({iters} iters, {len(visited)} states)", flush=True)
    return None


if __name__ == "__main__":
    DIR_MAP = {"U": UP, "D": DOWN, "L": LEFT, "R": RIGHT}
    all_solutions = {}

    for level in range(6):
        result = bfs_solve(level)
        if result:
            all_solutions[level] = result
        else:
            print(f"  FAILED", flush=True)
            break
        print(flush=True)

    print("=" * 60, flush=True)
    total = sum(len(p) for p in all_solutions.values())
    baseline = sum(BASELINES)
    print(f"Solved {len(all_solutions)}/6, Total: {total}, Baseline: {baseline}", flush=True)

    if len(all_solutions) == 6:
        print("\nVerifying with API...", flush=True)
        arcade = arc_agi.Arcade()
        env = arcade.make("m0r0-dadda488", render_mode=None)
        result = env.reset()
        for level_idx in range(6):
            for ch in all_solutions[level_idx]:
                result = env.step(DIR_MAP[ch])
            print(f"  Level {level_idx+1}: {len(all_solutions[level_idx])} moves, levels={result.levels_completed}")
        print(f"\nTotal: {total}, State: {result.state}")
        assert str(result.state) == "GameState.WIN"
        print("ALL VERIFIED!")
