"""R11L smart solver — compute ideal leg positions analytically.

Body = centroid of legs (approximately). For each leg, compute where it
should go to center the body on the target, then BFS over a small set
of nearby destinations.
"""
import importlib.util
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


def replay(level_idx, moves):
    """Replay moves. Each move = (leg_index, dest_x, dest_y)."""
    g = mod.R11l()
    g.set_level(level_idx)
    for (li, dx, dy) in moves:
        legs = list(g.ftmaz)
        if li < len(legs):
            leg = legs[li]
            act(g, leg.x + leg.width // 2, leg.y + leg.height // 2)
            act(g, dx, dy)
    return g


def compute_smart_dests(g):
    """Compute a small set of destinations for each leg based on target positions."""
    dests_per_leg = {}
    legs = list(g.ftmaz)

    for creature_name, data in g.brdck.items():
        target = data.get("xwdrv")
        creature_legs = data.get("mdpcc", [])
        if not target or not creature_legs:
            continue

        n = len(creature_legs)
        tx, ty = target.x, target.y

        # Body should be at target. Body ≈ centroid of legs (with width/2 offset).
        # For each leg, if we fix all others, this leg should be at:
        # ideal_x = n * tx - sum(other_legs.x) (approximately)
        for i, leg in enumerate(creature_legs):
            leg_idx = legs.index(leg)
            other_sum_x = sum(ol.x for j, ol in enumerate(creature_legs) if j != i)
            other_sum_y = sum(ol.y for j, ol in enumerate(creature_legs) if j != i)

            # Rough ideal position
            ideal_x = n * tx - other_sum_x
            ideal_y = n * ty - other_sum_y

            # Generate destinations around ideal position
            local_dests = set()
            for dx in range(-24, 28, 4):
                for dy in range(-24, 28, 4):
                    nx = ideal_x + dx
                    ny = ideal_y + dy
                    if 0 <= nx < 64 and 0 <= ny < 64:
                        local_dests.add((nx, ny))

            # Also add target-adjacent positions
            for dx in range(-12, 16, 4):
                for dy in range(-12, 16, 4):
                    nx = tx + dx
                    ny = ty + dy
                    if 0 <= nx < 64 and 0 <= ny < 64:
                        local_dests.add((nx, ny))

            if leg_idx not in dests_per_leg:
                dests_per_leg[leg_idx] = set()
            dests_per_leg[leg_idx] |= local_dests

    # For any leg not assigned, use all grid positions
    for i in range(len(legs)):
        if i not in dests_per_leg:
            dests_per_leg[i] = set((x, y) for x in range(0, 64, 4) for y in range(0, 64, 4))

    return dests_per_leg


def bfs_solve(level_idx, max_depth=None):
    g0 = mod.R11l()
    g0.set_level(level_idx)
    baseline = [7, 28, 30, 20, 37, 45][level_idx]
    move_limit = max_depth or (baseline // 2 + 3)

    legs = list(g0.ftmaz)
    num_legs = len(legs)
    start_state = get_state(g0)
    dests_per_leg = compute_smart_dests(g0)

    total_dests = sum(len(d) for d in dests_per_leg.values())
    print(f"Level {level_idx+1}: baseline={baseline}, move_limit={move_limit}, "
          f"legs={num_legs}, total_dests={total_dests}", flush=True)

    queue = deque()
    queue.append(([], start_state))
    visited = {start_state}
    iters = 0

    while queue:
        moves, state = queue.popleft()
        iters += 1
        if iters % 2000 == 0:
            print(f"  iter={iters} q={len(queue)} d={len(moves)} v={len(visited)}", flush=True)

        if len(moves) >= move_limit:
            continue

        for leg_idx in range(num_legs):
            for (dx, dy) in dests_per_leg.get(leg_idx, []):
                g = replay(level_idx, moves + [(leg_idx, dx, dy)])

                if g._current_level_index > level_idx or g._state.name == "WIN":
                    all_moves = moves + [(leg_idx, dx, dy)]
                    print(f"  FOUND! {len(all_moves)} moves = {len(all_moves)*2} clicks ({iters} iters)",
                          flush=True)
                    return all_moves

                if g._state.name == "GAME_OVER":
                    continue

                new_state = get_state(g)
                if new_state != state and new_state not in visited:
                    visited.add(new_state)
                    queue.append((moves + [(leg_idx, dx, dy)], new_state))

    print(f"  No solution ({iters} iters, {len(visited)} states)", flush=True)
    return None


def moves_to_clicks(level_idx, moves):
    """Convert moves to API click coordinates."""
    clicks = []
    g = mod.R11l()
    g.set_level(level_idx)
    for (li, dx, dy) in moves:
        legs = list(g.ftmaz)
        leg = legs[li]
        clicks.append((leg.x + leg.width // 2, leg.y + leg.height // 2))
        act(g, leg.x + leg.width // 2, leg.y + leg.height // 2)
        clicks.append((dx, dy))
        act(g, dx, dy)
    return clicks


if __name__ == "__main__":
    all_solutions = {}
    for level in range(6):
        moves = bfs_solve(level)
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
