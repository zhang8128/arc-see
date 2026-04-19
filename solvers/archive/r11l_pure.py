"""R11L pure-Python BFS solver.

Body = floor(avg(leg_centers)) - 2. Win = body overlaps target.
State = tuple of leg positions. Pure math, no game engine in BFS loop.
"""
import importlib.util
import arc_agi
from collections import deque
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('r11l', 'environment_files/r11l/aa269680/r11l.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

CLICK = GameAction.ACTION6
LEG_SIZE = 5
BODY_SIZE = 5
HALF_LEG = LEG_SIZE // 2  # 2


def act(g, x, y):
    return g.perform_action(ActionInput(id=CLICK, data={'x': x, 'y': y}))


def extract_level(level_idx):
    """Extract level data for pure-Python simulation."""
    g = mod.R11l()
    g.set_level(level_idx)

    creatures = {}
    for name, data in g.brdck.items():
        legs = data.get("mdpcc", [])
        target = data.get("xwdrv")
        if legs and target:
            leg_indices = [list(g.ftmaz).index(l) for l in legs]
            creatures[name] = {
                "leg_indices": leg_indices,
                "target": (target.x, target.y, target.width, target.height),
            }

    initial_legs = [(l.x, l.y) for l in g.ftmaz]
    num_legs = len(initial_legs)

    # Pre-compute valid positions using game engine
    valid_positions = set()
    for x in range(0, 60, 2):
        for y in range(0, 60, 2):
            g2 = mod.R11l()
            g2.set_level(level_idx)
            # Quick collision test: try moving first leg there
            # Actually just check bounds - obstacles are border walls
            # Valid if 0 <= x <= 58 and 0 <= y <= 58
            if 0 <= x <= 58 and 0 <= y <= 58:
                valid_positions.add((x, y))

    return {
        "creatures": creatures,
        "initial_legs": initial_legs,
        "num_legs": num_legs,
        "valid_positions": valid_positions,
    }


def body_position(leg_positions, leg_indices):
    """Compute body position from leg positions."""
    n = len(leg_indices)
    sum_cx = sum(leg_positions[i][0] + HALF_LEG for i in leg_indices)
    sum_cy = sum(leg_positions[i][1] + HALF_LEG for i in leg_indices)
    bx = int(sum_cx / n) - HALF_LEG
    by = int(sum_cy / n) - HALF_LEG
    return bx, by


def check_win(leg_positions, creatures):
    """Check if all bodies overlap their targets."""
    for name, cdata in creatures.items():
        bx, by = body_position(leg_positions, cdata["leg_indices"])
        tx, ty, tw, th = cdata["target"]
        # Body (bx, by, bx+5, by+5) overlaps target (tx, ty, tx+tw, ty+th)?
        if not (bx < tx + tw and bx + BODY_SIZE > tx and by < ty + th and by + BODY_SIZE > ty):
            return False
    return True


def bfs_solve(level_idx, max_moves=None):
    data = extract_level(level_idx)
    creatures = data["creatures"]
    initial = tuple(data["initial_legs"])
    num_legs = data["num_legs"]
    baseline = [7, 28, 30, 20, 37, 45][level_idx]
    move_limit = max_moves or (baseline // 2 + 3)

    # Compute smart destinations per leg
    dests_per_leg = {}
    for name, cdata in creatures.items():
        tx, ty, tw, th = cdata["target"]
        for li in cdata["leg_indices"]:
            other_indices = [j for j in cdata["leg_indices"] if j != li]
            n = len(cdata["leg_indices"])
            # Current sum of other legs
            other_sx = sum(initial[j][0] + HALF_LEG for j in other_indices)
            other_sy = sum(initial[j][1] + HALF_LEG for j in other_indices)
            # For body to overlap target: tx-4 <= bx <= tx+tw-1
            # bx = int((other_sx + this_cx) / n) - 2
            # So: tx-2 <= int((other_sx + this_cx) / n) <= tx+tw+1
            # this_cx range: n*(tx-2) - other_sx to n*(tx+tw+1) - other_sx
            # this_x = this_cx - 2
            min_cx = n * (tx - 2) - other_sx
            max_cx = n * (tx + tw + 1) - other_sx
            min_cy = n * (ty - 2) - other_sy
            max_cy = n * (ty + tw + 1) - other_sy

            local_dests = set()
            for x in range(max(0, int(min_cx) - 20), min(60, int(max_cx) + 20), 2):
                for y in range(max(0, int(min_cy) - 20), min(60, int(max_cy) + 20), 2):
                    local_dests.add((x, y))

            if li not in dests_per_leg:
                dests_per_leg[li] = set()
            dests_per_leg[li] |= local_dests

    total_dests = sum(len(d) for d in dests_per_leg.values())
    print(f"Level {level_idx+1}: baseline={baseline}, move_limit={move_limit}, "
          f"legs={num_legs}, total_dests={total_dests}", flush=True)

    if check_win(list(initial), creatures):
        print("  Already won!", flush=True)
        return []

    queue = deque()
    queue.append((initial, []))
    visited = {initial}
    iters = 0

    while queue:
        state, moves = queue.popleft()
        iters += 1
        if iters % 100000 == 0:
            print(f"  iter={iters} q={len(queue)} d={len(moves)} v={len(visited)}", flush=True)

        if len(moves) >= move_limit:
            continue

        legs = list(state)
        for li in range(num_legs):
            for (nx, ny) in dests_per_leg.get(li, []):
                if (nx, ny) == legs[li]:
                    continue  # same position
                new_legs = list(legs)
                new_legs[li] = (nx, ny)
                new_state = tuple(new_legs)

                if new_state in visited:
                    continue
                visited.add(new_state)

                if check_win(new_legs, creatures):
                    all_moves = moves + [(li, nx, ny)]
                    print(f"  FOUND! {len(all_moves)} moves ({iters} iters)", flush=True)
                    return all_moves

                queue.append((new_state, moves + [(li, nx, ny)]))

    print(f"  No solution ({iters} iters, {len(visited)} states)", flush=True)
    return None


def moves_to_clicks(level_idx, moves):
    """Convert pure-Python moves to API clicks. Verify with game engine."""
    g = mod.R11l()
    g.set_level(level_idx)
    clicks = []
    for (li, nx, ny) in moves:
        legs = list(g.ftmaz)
        leg = legs[li]
        cx, cy = leg.x + leg.width // 2, leg.y + leg.height // 2
        clicks.append((cx, cy))
        act(g, cx, cy)
        # Destination: click at center of target position
        clicks.append((nx + HALF_LEG, ny + HALF_LEG))
        act(g, nx + HALF_LEG, ny + HALF_LEG)
    won = g._current_level_index > level_idx or g._state.name == "WIN"
    return clicks, won


if __name__ == "__main__":
    all_solutions = {}
    for level in range(6):
        moves = bfs_solve(level)
        if moves is not None:
            clicks, won = moves_to_clicks(level, moves)
            if won:
                all_solutions[level] = clicks
                print(f"  Verified! {len(clicks)} clicks", flush=True)
            else:
                print(f"  Pure-Python solution didn't work in game engine!", flush=True)
                break
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
