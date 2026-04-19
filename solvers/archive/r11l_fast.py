"""R11L fast solver — BFS with deepcopy (no replay from scratch)."""
import importlib.util
import copy
import arc_agi
from collections import deque
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('r11l', 'environment_files/r11l/aa269680/r11l.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

CLICK = GameAction.ACTION6


def act(g, x, y):
    return g.perform_action(ActionInput(id=CLICK, data={'x': x, 'y': y}))


def get_state(g):
    return tuple((s.x, s.y) for s in g.ftmaz)


def try_move(g, leg_idx, dest_x, dest_y):
    """Try a move on a COPY. Returns (new_game, success)."""
    g2 = copy.deepcopy(g)
    legs = list(g2.ftmaz)
    if leg_idx >= len(legs):
        return None, False
    leg = legs[leg_idx]
    old_pos = (leg.x, leg.y)

    # Select leg
    act(g2, leg.x + leg.width // 2, leg.y + leg.height // 2)
    # Move
    act(g2, dest_x, dest_y)

    new_pos = (leg.x, leg.y)
    if new_pos == old_pos:
        return None, False  # Move blocked/reversed

    return g2, True


def compute_dests(g):
    """Smart destination set per leg."""
    legs = list(g.ftmaz)
    dests_per_leg = {}

    for creature_name, data in g.brdck.items():
        target = data.get("xwdrv")
        creature_legs = data.get("mdpcc", [])
        if not target or not creature_legs:
            continue

        n = len(creature_legs)
        tx, ty = target.x, target.y

        for i, leg in enumerate(creature_legs):
            leg_idx = legs.index(leg)
            other_sum_x = sum(ol.x for j, ol in enumerate(creature_legs) if j != i)
            other_sum_y = sum(ol.y for j, ol in enumerate(creature_legs) if j != i)
            ideal_x = n * tx - other_sum_x
            ideal_y = n * ty - other_sum_y

            local_dests = set()
            for dx in range(-28, 32, 4):
                for dy in range(-28, 32, 4):
                    nx, ny = ideal_x + dx, ideal_y + dy
                    if 0 <= nx < 60 and 0 <= ny < 60:
                        local_dests.add((nx, ny))

            if leg_idx not in dests_per_leg:
                dests_per_leg[leg_idx] = set()
            dests_per_leg[leg_idx] |= local_dests

    return dests_per_leg


def bfs_solve(level_idx, max_moves=None):
    g0 = mod.R11l()
    g0.set_level(level_idx)
    baseline = [7, 28, 30, 20, 37, 45][level_idx]
    move_limit = max_moves or (baseline // 2 + 3)

    legs = list(g0.ftmaz)
    num_legs = len(legs)
    start_state = get_state(g0)
    dests = compute_dests(g0)
    total_dests = sum(len(d) for d in dests.values())

    print(f"Level {level_idx+1}: baseline={baseline}, move_limit={move_limit}, "
          f"legs={num_legs}, total_dests={total_dests}", flush=True)

    queue = deque()
    queue.append((g0, [], start_state))
    visited = {start_state}
    iters = 0

    while queue:
        g, moves, state = queue.popleft()
        iters += 1
        if iters % 1000 == 0:
            print(f"  iter={iters} q={len(queue)} d={len(moves)} v={len(visited)}", flush=True)

        if len(moves) >= move_limit:
            continue

        for leg_idx in range(num_legs):
            for (dx, dy) in dests.get(leg_idx, []):
                g2, ok = try_move(g, leg_idx, dx, dy)
                if not ok:
                    continue

                if g2._current_level_index > level_idx or g2._state.name == "WIN":
                    all_moves = moves + [(leg_idx, dx, dy)]
                    print(f"  FOUND! {len(all_moves)} moves = {len(all_moves)*2} clicks ({iters} iters)",
                          flush=True)
                    return all_moves, g0

                if g2._state.name == "GAME_OVER":
                    continue

                new_state = get_state(g2)
                if new_state not in visited:
                    visited.add(new_state)
                    queue.append((g2, moves + [(leg_idx, dx, dy)], new_state))

    print(f"  No solution ({iters} iters, {len(visited)} states)", flush=True)
    return None, g0


def moves_to_clicks(level_idx, moves):
    g = mod.R11l()
    g.set_level(level_idx)
    clicks = []
    for (li, dx, dy) in moves:
        legs = list(g.ftmaz)
        leg = legs[li]
        cx, cy = leg.x + leg.width // 2, leg.y + leg.height // 2
        clicks.append((cx, cy))
        act(g, cx, cy)
        clicks.append((dx, dy))
        act(g, dx, dy)
    return clicks


if __name__ == "__main__":
    all_solutions = {}
    for level in range(6):
        result = bfs_solve(level)
        moves, g0 = result
        if moves:
            clicks = moves_to_clicks(level, moves)
            all_solutions[level] = clicks
        else:
            print(f"  FAILED", flush=True)
            break
        print(flush=True)

    print("=" * 60, flush=True)
    total = sum(len(p) for p in all_solutions.values())
    baseline = sum([7, 28, 30, 20, 37, 45])
    print(f"Solved {len(all_solutions)}/6, Total: {total} clicks, Baseline: {baseline}", flush=True)

    if len(all_solutions) == 6:
        print("\nVerifying with API...", flush=True)
        arcade = arc_agi.Arcade()
        env = arcade.make("r11l-aa269680", render_mode=None)
        result = env.reset()
        for level_idx in range(6):
            for (x, y) in all_solutions[level_idx]:
                result = env.step(CLICK, data={"x": x, "y": y})
            print(f"  Level {level_idx+1}: {len(all_solutions[level_idx])} clicks, "
                  f"levels={result.levels_completed}")
        print(f"\nTotal: {total}, State: {result.state}")
