"""CN04 solver — keyboard+click game. Deepcopy BFS + pixel hash."""
import importlib.util, copy, hashlib
import arc_agi
from collections import deque
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('cn04', 'environment_files/cn04/65d47d14/cn04.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def pixel_hash(g):
    frame = g.get_pixels(0, 0, 64, 64)
    return hashlib.md5(frame[3:].tobytes()).hexdigest()


def get_actions(g):
    """Get all available actions including button clicks."""
    s, ox, oy = g.camera._calculate_scale_and_offset()
    actions = [
        (GameAction.ACTION1, None, 'U'),
        (GameAction.ACTION2, None, 'D'),
        (GameAction.ACTION3, None, 'L'),
        (GameAction.ACTION4, None, 'R'),
        (GameAction.ACTION5, None, '5'),
    ]
    for cs in g.current_level.get_sprites_by_tag('sys_click'):
        dx = cs.x * s + ox + cs.width * s // 2
        dy = cs.y * s + oy + cs.height * s // 2
        actions.append((GameAction.ACTION6, {'x': dx, 'y': dy}, f'C{len(actions)-5}'))
    return actions


def bfs_solve(level_idx, max_depth=None):
    g0 = mod.Cn04()
    g0.set_level(level_idx)
    baseline = [16, 54, 69, 318, 208, 114][level_idx]
    limit = max_depth or min(baseline + 10, 250)

    actions = get_actions(g0)
    start = pixel_hash(g0)
    print(f"Level {level_idx+1}: baseline={baseline}, limit={limit}, actions={len(actions)}", flush=True)

    queue = deque([(g0, [])])
    visited = {start}
    iters = 0

    while queue:
        g, path = queue.popleft()
        iters += 1
        if iters % 5000 == 0:
            print(f"  iter={iters} q={len(queue)} d={len(path)} v={len(visited)}", flush=True)
        if len(path) >= limit:
            continue

        for a_id, a_data, a_name in actions:
            g2 = copy.deepcopy(g)
            g2.perform_action(ActionInput(id=a_id, data=a_data or {}))

            if g2._current_level_index > level_idx or g2._state.name == "WIN":
                result = path + [(a_id, a_data, a_name)]
                names = ".".join(r[2] for r in result)
                print(f"  FOUND! {len(result)} actions ({iters} iters): {names}", flush=True)
                return result

            if g2._state.name == "GAME_OVER":
                continue

            h = pixel_hash(g2)
            if h not in visited:
                visited.add(h)
                queue.append((g2, path + [(a_id, a_data, a_name)]))

    print(f"  No solution ({iters} iters, {len(visited)} states)", flush=True)
    return None


if __name__ == "__main__":
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
    baseline = sum([16, 54, 69, 318, 208, 114])
    print(f"Solved {len(all_solutions)}/6, Total: {total}, Baseline: {baseline}", flush=True)

    if len(all_solutions) == 6:
        print("\nVerifying with API...", flush=True)
        arcade = arc_agi.Arcade()
        env = arcade.make("cn04-65d47d14", render_mode=None)
        result = env.reset()
        for level_idx in range(6):
            for (a_id, a_data, _) in all_solutions[level_idx]:
                if a_data:
                    result = env.step(a_id, data=a_data)
                else:
                    result = env.step(a_id)
            print(f"  Level {level_idx+1}: {len(all_solutions[level_idx])} actions, "
                  f"levels={result.levels_completed}")
        print(f"\nTotal: {total}, State: {result.state}")
        assert str(result.state) == "GameState.WIN"
        print("ALL VERIFIED!")
