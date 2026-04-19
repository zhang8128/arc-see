"""R11L solver — deepcopy BFS with pixel hash. Click leg + click destination."""
import importlib.util, copy, hashlib
import arc_agi
from collections import deque
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('r11l', 'environment_files/r11l/aa269680/r11l.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

CLICK = GameAction.ACTION6


def act(g, x, y):
    return g.perform_action(ActionInput(id=CLICK, data={'x': x, 'y': y}))


def pixel_hash(g):
    frame = g.get_pixels(0, 0, 64, 64)
    return hashlib.md5(frame[2:].tobytes()).hexdigest()


def get_leg_centers(g):
    return [(l.x + l.width // 2, l.y + l.height // 2) for l in g.ftmaz]


def get_target_positions(g):
    targets = set()
    for name, data in g.brdck.items():
        t = data.get("xwdrv")
        if t:
            targets.add((t.x, t.y))
    return targets


def get_destinations(g):
    """Smart destinations: near targets + grid positions near legs."""
    dests = set()
    targets = get_target_positions(g)
    legs = get_leg_centers(g)

    # Near all targets
    for tx, ty in targets:
        for dx in range(-20, 24, 4):
            for dy in range(-20, 24, 4):
                nx, ny = tx + dx, ty + dy
                if 0 <= nx < 64 and 0 <= ny < 64:
                    dests.add((nx, ny))

    # Near all current legs
    for lx, ly in legs:
        for dx in range(-16, 20, 4):
            for dy in range(-16, 20, 4):
                nx, ny = lx + dx, ly + dy
                if 0 <= nx < 64 and 0 <= ny < 64:
                    dests.add((nx, ny))

    return sorted(dests)


def bfs_solve(level_idx, max_moves=None):
    g0 = mod.R11l()
    g0.set_level(level_idx)
    baseline = [7, 28, 30, 20, 37, 45][level_idx]
    move_limit = max_moves or (baseline // 2 + 5)  # each "move" = select + place = 2 clicks

    legs = get_leg_centers(g0)
    dests = get_destinations(g0)
    start = pixel_hash(g0)

    print(f"Level {level_idx+1}: baseline={baseline}, move_limit={move_limit}, "
          f"legs={len(legs)}, dests={len(dests)}", flush=True)

    queue = deque()
    queue.append((g0, []))
    visited = {start}
    iters = 0

    while queue:
        g, moves = queue.popleft()
        iters += 1
        if iters % 1000 == 0:
            print(f"  iter={iters} q={len(queue)} d={len(moves)} v={len(visited)}", flush=True)

        if len(moves) >= move_limit:
            continue

        # For each leg, try each destination
        leg_centers = get_leg_centers(g)
        for li, (lx, ly) in enumerate(leg_centers):
            for (dx, dy) in dests:
                g2 = copy.deepcopy(g)
                # Select leg
                act(g2, lx, ly)
                # Move to destination
                act(g2, dx, dy)

                if g2._current_level_index > level_idx or g2._state.name == "WIN":
                    result = moves + [(lx, ly, dx, dy)]
                    print(f"  FOUND! {len(result)} moves = {len(result)*2} clicks ({iters} iters)", flush=True)
                    return result

                if g2._state.name == "GAME_OVER":
                    continue

                h = pixel_hash(g2)
                if h not in visited:
                    visited.add(h)
                    queue.append((g2, moves + [(lx, ly, dx, dy)]))

    print(f"  No solution ({iters} iters, {len(visited)} states)", flush=True)
    return None


if __name__ == "__main__":
    all_solutions = {}
    for level in range(6):
        moves = bfs_solve(level)
        if moves:
            clicks = []
            for (lx, ly, dx, dy) in moves:
                clicks.extend([(lx, ly), (dx, dy)])
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
