"""Multi-game deepcopy BFS solver for AR25, CN04, DC22, SK48."""
import importlib.util, copy, hashlib, sys, os
import arc_agi
from collections import deque
from arcengine import GameAction, ActionInput

GAME = sys.argv[1]
GAME_DIR = f'environment_files/{GAME}'
SUB = os.listdir(GAME_DIR)[0]
GAME_ID = f'{GAME}-{SUB}'
GAME_FILE = f'{GAME_DIR}/{SUB}/{GAME}.py'

BASELINES = {
    "ar25": [17, 22, 103, 29, 29, 159, 152, 66],
    "cn04": [16, 54, 69, 318, 208, 114],
    "dc22": [64, 117, 59, 78, 324, 550],
    "sk48": [15, 32, 35, 113, 304, 42, 63, 92],
}

spec = importlib.util.spec_from_file_location(GAME, GAME_FILE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
CLS = getattr(mod, GAME.capitalize())


def pixel_hash(g):
    frame = g.get_pixels(0, 0, 64, 64)
    return hashlib.md5(frame[2:].tobytes()).hexdigest()


def get_actions(g):
    actions = []
    for i in g._available_actions:
        if i <= 5:
            actions.append((getattr(GameAction, f"ACTION{i}"), None, f"A{i}"))
    try:
        s, ox, oy = g.camera._calculate_scale_and_offset()
        for cs in g.current_level.get_sprites_by_tag("sys_click"):
            dx = cs.x * s + ox + cs.width * s // 2
            dy = cs.y * s + oy + cs.height * s // 2
            actions.append((GameAction.ACTION6, {"x": dx, "y": dy}, f"B({dx},{dy})"))
    except:
        pass
    return actions


def bfs_solve(level_idx, max_depth=None):
    g0 = CLS()
    g0.set_level(level_idx)
    bl = BASELINES[GAME]
    baseline = bl[level_idx] if level_idx < len(bl) else 100
    limit = max_depth or min(baseline + 15, 300)

    actions = get_actions(g0)
    start = pixel_hash(g0)
    print(f"Level {level_idx+1}: baseline={baseline}, limit={limit}, actions={len(actions)}", flush=True)

    queue = deque([(g0, [])])
    visited = {start}
    iters = 0

    while queue:
        g, path = queue.popleft()
        iters += 1
        if iters % 3000 == 0:
            print(f"  iter={iters} q={len(queue)} d={len(path)} v={len(visited)}", flush=True)
        if len(path) >= limit:
            continue

        for a_id, a_data, name in actions:
            g2 = copy.deepcopy(g)
            g2.perform_action(ActionInput(id=a_id, data=a_data or {}))
            if g2._current_level_index > level_idx or g2._state.name == "WIN":
                result = path + [(a_id, a_data, name)]
                print(f"  FOUND! {len(result)} actions ({iters} iters): {'.'.join(r[2] for r in result)}", flush=True)
                return result
            if g2._state.name == "GAME_OVER":
                continue
            h = pixel_hash(g2)
            if h not in visited:
                visited.add(h)
                queue.append((g2, path + [(a_id, a_data, name)]))

    print(f"  No solution ({iters} iters, {len(visited)} states)", flush=True)
    return None


if __name__ == "__main__":
    bl = BASELINES[GAME]
    all_solutions = {}
    for level in range(len(bl)):
        result = bfs_solve(level)
        if result:
            all_solutions[level] = result
        else:
            print(f"  FAILED", flush=True)
            break
        print(flush=True)

    print("=" * 60, flush=True)
    total = sum(len(p) for p in all_solutions.values())
    baseline = sum(bl)
    print(f"Solved {len(all_solutions)}/{len(bl)}, Total: {total}, Baseline: {baseline}", flush=True)

    if len(all_solutions) == len(bl):
        print("\nVerifying with API...", flush=True)
        arcade = arc_agi.Arcade()
        env = arcade.make(GAME_ID, render_mode=None)
        result = env.reset()
        for level_idx in range(len(bl)):
            for (a_id, a_data, _) in all_solutions[level_idx]:
                if a_data:
                    result = env.step(a_id, data=a_data)
                else:
                    result = env.step(a_id)
            print(f"  Level {level_idx+1}: {len(all_solutions[level_idx])} actions, levels={result.levels_completed}")
        print(f"\nTotal: {total}, State: {result.state}")
