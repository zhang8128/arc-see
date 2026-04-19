"""LP85 fast solver — pure-Python BFS over cyclic permutations.

Each button shifts tiles in a cycle. Cycles can share positions (overlap).
State = tuple of tile positions. Much faster than game engine replay.
"""
import importlib.util
import arc_agi
from collections import deque
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('lp85', 'environment_files/lp85/305b61c3/lp85.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

CLICK = GameAction.ACTION6
crxpafuiwp = 3  # grid cell size


def extract_level(level_idx):
    """Extract level data for pure-Python simulation."""
    g = mod.Lp85()
    g.set_level(level_idx)

    s, ox, oy = g.camera._calculate_scale_and_offset()
    level_name = g.current_level.get_data("level_name")
    perm_data = g.uopmnplcnv[level_name]

    # Get button display coords
    click_sprites = g.current_level.get_sprites_by_tag("sys_click")
    buttons = []  # (display_x, display_y, group_name, is_right)
    for cs in click_sprites:
        tag = cs.tags[0]
        parts = tag.split("_")
        if len(parts) == 3:
            group = parts[1]
            is_right = parts[2] == "R"
            dx = cs.x * s + ox + cs.width * s // 2
            dy = cs.y * s + oy + cs.height * s // 2
            buttons.append((dx, dy, group, is_right))

    # Build permutation for each button
    # A permutation maps position → position
    button_perms = []
    for dx, dy, group, is_right in buttons:
        if group not in perm_data:
            button_perms.append((dx, dy, {}))
            continue

        info = perm_data[group]
        cycle_len = info["oxbwsencfv"]
        pos_map = info["qcmzcjocmj"]

        if cycle_len <= 1:
            button_perms.append((dx, dy, {}))
            continue

        # Build source→dest mapping
        perm = {}
        for num, pos in pos_map.items():
            if is_right:
                dest_num = 1 if num == cycle_len else num + 1
            else:
                dest_num = cycle_len if num == 1 else num - 1
            dest_pos = pos_map[dest_num]
            # Convert to grid pixel coords
            src = (pos.y * crxpafuiwp, pos.x * crxpafuiwp)
            dst = (dest_pos.y * crxpafuiwp, dest_pos.x * crxpafuiwp)
            perm[src] = dst

        button_perms.append((dx, dy, perm))

    # Get initial tile positions (all sprites at grid positions)
    all_moving = {}
    for tag_name in ["tile", "bghvgbtwcb", "fdgmtkfrxl"]:
        for sp in g.current_level.get_sprites_by_tag(tag_name):
            all_moving[(sp.x, sp.y)] = (sp.name, tag_name)

    # Get goal positions
    bgh_sprites = g.current_level.get_sprites_by_tag("bghvgbtwcb")
    bgh_positions = [(sp.x, sp.y) for sp in bgh_sprites]

    goal_sprites = g.current_level.get_sprites_by_tag("goal")
    goal_positions = [(sp.x + 1, sp.y + 1) for sp in goal_sprites]  # win checks x+1,y+1

    fdg_sprites = g.current_level.get_sprites_by_tag("fdgmtkfrxl")
    fdg_positions = [(sp.x, sp.y) for sp in fdg_sprites]

    goalo_sprites = g.current_level.get_sprites_by_tag("goal-o")
    goalo_positions = [(sp.x + 1, sp.y + 1) for sp in goalo_sprites]

    return {
        "buttons": button_perms,
        "all_moving": all_moving,
        "bgh_positions": bgh_positions,
        "goal_positions": set(goal_positions),
        "fdg_positions": fdg_positions,
        "goalo_positions": set(goalo_positions),
    }


def apply_perm(state, perm):
    """Apply a permutation to the state. State = dict mapping (x,y) -> value."""
    if not perm:
        return state

    new_state = dict(state)
    # Collect all tiles that are at permutation source positions
    moves = {}
    for src, dst in perm.items():
        if src in new_state:
            moves[src] = (dst, new_state[src])

    # Remove from old positions
    for src in moves:
        del new_state[src]

    # Place at new positions
    for src, (dst, val) in moves.items():
        new_state[dst] = val

    return new_state


def check_win(state, level_data):
    """Check if bgh sprites are at goal positions and fdg at goalo."""
    bgh_pos = level_data["bgh_positions"]
    goal_pos = level_data["goal_positions"]
    fdg_pos = level_data["fdg_positions"]
    goalo_pos = level_data["goalo_positions"]

    # Find current positions of bgh sprites
    for orig_pos in bgh_pos:
        # Find where this sprite moved to
        # Actually, we need to track individual sprites, not just positions
        pass

    # Simpler: check if ALL goal positions have a bgh-tagged sprite
    # and ALL goalo positions have a fdg-tagged sprite
    for gp in goal_pos:
        if gp not in state or state[gp][1] != "bghvgbtwcb":
            return False
    for gp in goalo_pos:
        if gp not in state or state[gp][1] != "fdgmtkfrxl":
            return False
    return True


def state_key(state):
    """Convert state to hashable key."""
    return tuple(sorted(state.items()))


def bfs_solve(level_idx):
    """Fast BFS using pure-Python simulation."""
    data = extract_level(level_idx)
    buttons = data["buttons"]
    initial_state = data["all_moving"]
    baseline = [33, 22, 31, 23, 33, 34, 73, 173][level_idx]
    limit = min(baseline + 5, 200)

    print(f"Level {level_idx+1}: baseline={baseline}, limit={limit}, buttons={len(buttons)}", flush=True)

    start_key = state_key(initial_state)
    queue = deque()
    queue.append(([], initial_state))
    visited = {start_key}
    iters = 0

    while queue:
        path, state = queue.popleft()
        iters += 1
        if iters % 50000 == 0:
            print(f"  iter={iters} q={len(queue)} d={len(path)} v={len(visited)}", flush=True)

        if len(path) >= limit:
            continue

        for i, (dx, dy, perm) in enumerate(buttons):
            new_state = apply_perm(state, perm)
            new_path = path + [i]

            if check_win(new_state, data):
                clicks = [(buttons[j][0], buttons[j][1]) for j in new_path]
                print(f"  FOUND! {len(new_path)} clicks ({iters} iters)", flush=True)
                return clicks

            key = state_key(new_state)
            if key not in visited:
                visited.add(key)
                queue.append((new_path, new_state))

    print(f"  No solution ({iters} iters, {len(visited)} states)", flush=True)
    return None


if __name__ == "__main__":
    all_solutions = {}
    for level in range(8):
        path = bfs_solve(level)
        if path:
            all_solutions[level] = path
        else:
            print(f"  FAILED", flush=True)
            break
        print(flush=True)

    print("=" * 60, flush=True)
    total = sum(len(p) for p in all_solutions.values())
    baseline = sum([33, 22, 31, 23, 33, 34, 73, 173])
    print(f"Solved {len(all_solutions)}/8, Total: {total}, Baseline: {baseline}", flush=True)

    if len(all_solutions) == 8:
        print("\nVerifying with API...", flush=True)
        arcade = arc_agi.Arcade()
        env = arcade.make("lp85-305b61c3", render_mode=None)
        result = env.reset()
        api_total = 0
        for level_idx in range(8):
            for (dx, dy) in all_solutions[level_idx]:
                result = env.step(CLICK, data={"x": dx, "y": dy})
                api_total += 1
            print(f"  Level {level_idx+1}: {len(all_solutions[level_idx])} clicks, levels={result.levels_completed}")
        print(f"\nTotal: {api_total}, State: {result.state}")
        assert str(result.state) == "GameState.WIN"
        print("ALL VERIFIED!")
