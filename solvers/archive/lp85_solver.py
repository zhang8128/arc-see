"""LP85 solver — cyclic permutation puzzle.

Each button group (A, B, C...) is an independent cycle.
Clicking R shifts tiles forward in the cycle, L shifts backward.
Goal: align colored tiles with goal positions.
Optimal: for each group, min(R_clicks, L_clicks) to align.
"""
import importlib.util
import arc_agi
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('lp85', 'environment_files/lp85/305b61c3/lp85.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

CLICK = GameAction.ACTION6
crxpafuiwp = 3  # grid cell size


def solve_level(level_idx):
    """Solve a level by computing optimal cycle shifts."""
    g = mod.Lp85()
    g.set_level(level_idx)

    s, ox, oy = g.camera._calculate_scale_and_offset()

    # Get button info
    click_sprites = g.current_level.get_sprites_by_tag("sys_click")
    buttons = {}  # group -> {L: (dx,dy), R: (dx,dy)}
    for cs in click_sprites:
        tag = cs.tags[0]  # e.g. "button_A_R"
        parts = tag.split("_")
        if len(parts) == 3:
            group = parts[1]
            direction = parts[2]
            dx = cs.x * s + ox + cs.width * s // 2
            dy = cs.y * s + oy + cs.height * s // 2
            if group not in buttons:
                buttons[group] = {}
            buttons[group][direction] = (dx, dy)

    # Get tiles and goals
    tiles = g.current_level.get_sprites_by_tag("tile") + g.current_level.get_sprites_by_tag("bghvgbtwcb")
    goals = []
    for gs in g.current_level.get_sprites_by_tag("goal"):
        goals.append((gs.x, gs.y, int(gs.pixels[1, 1]) if gs.pixels.shape[0] > 1 else int(gs.pixels[0, 0])))

    # Get the permutation data for each button group
    level_name = g.current_level.get_data("level_name")
    perm_data = g.uopmnplcnv

    if level_name not in perm_data:
        print(f"  No perm data for level '{level_name}'")
        return None

    level_perms = perm_data[level_name]

    # For each group, figure out cycle length and current offset from goal
    all_clicks = []

    for group, btn_dirs in sorted(buttons.items()):
        if group not in level_perms:
            continue

        perm_info = level_perms[group]
        cycle_len = perm_info["oxbwsencfv"]
        pos_map = perm_info["qcmzcjocmj"]

        if cycle_len <= 1:
            continue

        # Try each possible shift (0 to cycle_len-1) and check if it aligns with goals
        # A "right" click shifts by +1, a "left" click shifts by -1

        best_clicks = None
        best_count = float('inf')

        for shift in range(cycle_len):
            # Check if this shift aligns all tiles to goals
            g_test = mod.Lp85()
            g_test.set_level(level_idx)

            # Apply 'shift' right clicks
            if "R" in btn_dirs:
                dx, dy = btn_dirs["R"]
                for _ in range(shift):
                    g_test.perform_action(ActionInput(id=CLICK, data={"x": dx, "y": dy}))

            # Check win
            if g_test.khartslnwa():
                r_count = shift
                l_count = cycle_len - shift if shift > 0 else 0
                if r_count <= l_count:
                    count = r_count
                    clicks = [(btn_dirs["R"], "R")] * count if "R" in btn_dirs else []
                else:
                    count = l_count
                    clicks = [(btn_dirs["L"], "L")] * count if "L" in btn_dirs else []

                if count < best_count:
                    best_count = count
                    best_clicks = clicks
                break  # First match found

        if best_clicks is None:
            # Group doesn't have independent win — try all shifts
            # This means groups interact. Need different approach.
            pass
        else:
            all_clicks.extend(best_clicks)

    return all_clicks


def solve_level_bfs(level_idx, max_depth=50):
    """BFS fallback for levels where groups interact."""
    g0 = mod.Lp85()
    g0.set_level(level_idx)

    s, ox, oy = g0.camera._calculate_scale_and_offset()

    # Get all button click coords
    click_sprites = g0.current_level.get_sprites_by_tag("sys_click")
    btn_coords = []
    for cs in click_sprites:
        dx = cs.x * s + ox + cs.width * s // 2
        dy = cs.y * s + oy + cs.height * s // 2
        btn_coords.append((dx, dy))

    from collections import deque

    def get_state(g):
        all_moving = (g.current_level.get_sprites_by_tag("tile") +
                      g.current_level.get_sprites_by_tag("bghvgbtwcb") +
                      g.current_level.get_sprites_by_tag("fdgmtkfrxl"))
        return tuple(sorted((t.x, t.y, t.name) for t in all_moving))

    def replay(path):
        g = mod.Lp85()
        g.set_level(level_idx)
        for (dx, dy) in path:
            g.perform_action(ActionInput(id=CLICK, data={"x": dx, "y": dy}))
        return g

    start = get_state(g0)
    queue = deque()
    queue.append([])
    visited = {start}
    iters = 0

    while queue:
        path = queue.popleft()
        iters += 1
        if iters % 5000 == 0:
            print(f"  BFS iter={iters} q={len(queue)} d={len(path)} v={len(visited)}", flush=True)
        if len(path) >= max_depth:
            continue

        for (dx, dy) in btn_coords:
            new_path = path + [(dx, dy)]
            g = replay(new_path)
            if g._current_level_index > level_idx or g._state.name == "WIN":
                print(f"  BFS found! {len(new_path)} clicks ({iters} iters)", flush=True)
                return new_path
            if g._state.name == "GAME_OVER":
                continue
            state = get_state(g)
            if state not in visited:
                visited.add(state)
                queue.append(new_path)

    print(f"  BFS failed ({iters} iters, {len(visited)} states)", flush=True)
    return None


def solve_all():
    """Solve all levels, verify with API."""
    baselines = [33, 22, 31, 23, 33, 34, 73, 173]
    all_solutions = {}

    for level_idx in range(8):
        print(f"Level {level_idx+1} (baseline={baselines[level_idx]}):", flush=True)

        # Try analytical approach first
        clicks = solve_level(level_idx)
        if clicks:
            # Verify
            g = mod.Lp85()
            g.set_level(level_idx)
            s, ox, oy = g.camera._calculate_scale_and_offset()
            api_clicks = []
            for (dx, dy), direction in clicks:
                g.perform_action(ActionInput(id=CLICK, data={"x": dx, "y": dy}))
                api_clicks.append((dx, dy))

            if g._current_level_index > level_idx or g._state.name == "WIN" or g.khartslnwa():
                print(f"  Analytical: {len(api_clicks)} clicks", flush=True)
                all_solutions[level_idx] = api_clicks
                continue

        # Fall back to BFS
        print(f"  Trying BFS...", flush=True)
        path = solve_level_bfs(level_idx, max_depth=min(baselines[level_idx] + 5, 100))
        if path:
            all_solutions[level_idx] = path
        else:
            print(f"  FAILED", flush=True)
            break

    return all_solutions


if __name__ == "__main__":
    solutions = solve_all()

    print("\n" + "=" * 60, flush=True)
    total = sum(len(p) for p in solutions.values())
    baseline = sum([33, 22, 31, 23, 33, 34, 73, 173])
    print(f"Solved {len(solutions)}/8, Total: {total}, Baseline: {baseline}", flush=True)

    if len(solutions) == 8:
        print("\nVerifying with API...", flush=True)
        arcade = arc_agi.Arcade()
        env = arcade.make("lp85-305b61c3", render_mode=None)
        result = env.reset()
        api_total = 0
        for level_idx in range(8):
            for (dx, dy) in solutions[level_idx]:
                result = env.step(CLICK, data={"x": dx, "y": dy})
                api_total += 1
            print(f"  Level {level_idx+1}: {len(solutions[level_idx])} clicks, levels={result.levels_completed}")
        print(f"\nTotal: {api_total}, State: {result.state}")
