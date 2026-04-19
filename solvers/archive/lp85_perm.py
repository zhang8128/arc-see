"""LP85 pure-Python permutation BFS solver.

Each button applies a cyclic permutation to grid positions.
Goals (tagged sprites) move with the cycles.
Win when every goal lands on a bgh target and every goalo lands on a fdg target.

State = frozenset of (grid_pos, sprite_id) for all moving sprites.
BFS over button clicks. No game engine needed except for initial extraction and final verification.
"""
import importlib.util
import arc_agi
from collections import deque
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('lp85', 'environment_files/lp85/305b61c3/lp85.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

CLICK = GameAction.ACTION6
CELL = 3  # crxpafuiwp


def extract_level(level_idx):
    """Extract everything needed for pure-Python BFS."""
    g = mod.Lp85()
    g.set_level(level_idx)
    s, ox, oy = g.camera._calculate_scale_and_offset()
    level_name = g.current_level.get_data("level_name")
    perm_data = mod.qfvvosdkqr(mod.izutyjcpih).get(level_name, {})

    # Group all button sprites by position (multiple groups fire per click!)
    from collections import defaultdict
    pos_groups = defaultdict(list)
    for sp in g.current_level.get_sprites():
        if sp.tags and "button" in sp.tags[0]:
            parts = sp.tags[0].split("_")
            if len(parts) == 3:
                pos_groups[(sp.x, sp.y)].append((parts[1], parts[2] == "R"))

    # Build combined permutation for each unique click position
    buttons = []
    seen_pos = set()
    for cs in g.current_level.get_sprites_by_tag("sys_click"):
        if (cs.x, cs.y) in seen_pos:
            continue
        seen_pos.add((cs.x, cs.y))
        dx = cs.x * s + ox + cs.width * s // 2
        dy = cs.y * s + oy + cs.height * s // 2

        combined_perm = {}
        for group, is_right in pos_groups.get((cs.x, cs.y), []):
            if group not in perm_data:
                continue
            info = perm_data[group]
            cycle_len = info["oxbwsencfv"]
            pos_map = info["qcmzcjocmj"]
            if cycle_len <= 1:
                continue
            for num, pos in pos_map.items():
                dest_num = (1 if num == cycle_len else num + 1) if is_right else (cycle_len if num == 1 else num - 1)
                src_px = (pos.x * CELL, pos.y * CELL)
                dst_px = (pos_map[dest_num].x * CELL, pos_map[dest_num].y * CELL)
                combined_perm[src_px] = dst_px

        if combined_perm:
            buttons.append((dx, dy, combined_perm))

    # Extract all sprites at grid positions
    # Map grid_pos -> list of (sprite_id, tag_type)
    initial_tiles = {}  # grid_pos -> [(sprite_unique_id, is_goal, is_goalo)]
    sprite_id = 0
    all_sprites = g.current_level.get_sprites()

    goal_ids = set()
    goalo_ids = set()

    for sp in all_sprites:
        if sp.x % CELL != 0 or sp.y % CELL != 0:
            continue
        px = (sp.x, sp.y)  # pixel position = (sprite.x, sprite.y)
        is_goal = "goal" in sp.tags
        is_goalo = "goal-o" in sp.tags
        if is_goal or is_goalo or "tile" in sp.tags:
            sid = sprite_id
            sprite_id += 1
            if px not in initial_tiles:
                initial_tiles[px] = []
            initial_tiles[px].append(sid)
            if is_goal:
                goal_ids.add(sid)
            if is_goalo:
                goalo_ids.add(sid)

    # Target pixel positions: bgh at (bx, by) → check at (bx+1, by+1)
    # Round to nearest grid position
    bgh_targets = set()
    for sp in g.current_level.get_sprites_by_tag("bghvgbtwcb"):
        # Win checks get_sprite_at(sp.x+1, sp.y+1, "goal")
        # Goal sprites are at grid positions. Find the grid pos containing (sp.x+1, sp.y+1)
        px = ((sp.x + 1) // CELL * CELL, (sp.y + 1) // CELL * CELL)
        bgh_targets.add(px)

    fdg_targets = set()
    for sp in g.current_level.get_sprites_by_tag("fdgmtkfrxl"):
        px = ((sp.x + 1) // CELL * CELL, (sp.y + 1) // CELL * CELL)
        fdg_targets.add(px)

    return {
        "buttons": buttons,
        "initial_tiles": initial_tiles,
        "goal_ids": goal_ids,
        "goalo_ids": goalo_ids,
        "bgh_targets": bgh_targets,
        "fdg_targets": fdg_targets,
    }


def make_state(tiles, goal_ids, goalo_ids):
    """Hashable state: only positions of goal and goalo sprites (the win-relevant ones)."""
    items = []
    for gp, sids in tiles.items():
        for sid in sids:
            if sid in goal_ids or sid in goalo_ids:
                items.append((gp, sid))
    return frozenset(items)


def apply_perm(tiles, perm):
    """Apply permutation to tiles dict. Returns new tiles dict."""
    new_tiles = {}
    for gp, sids in tiles.items():
        if gp in perm:
            dst = perm[gp]
            if dst not in new_tiles:
                new_tiles[dst] = []
            new_tiles[dst].extend(sids)
        else:
            if gp not in new_tiles:
                new_tiles[gp] = []
            new_tiles[gp].extend(sids)
    return new_tiles


def check_win(tiles, goal_ids, goalo_ids, bgh_targets, fdg_targets):
    """Check if all goals are at bgh targets and all goalos at fdg targets."""
    # Find positions of goal sprites
    for gp, sids in tiles.items():
        for sid in sids:
            if sid in goal_ids:
                if gp not in bgh_targets:
                    return False
            if sid in goalo_ids:
                if gp not in fdg_targets:
                    return False
    return True


def bfs_solve(level_idx):
    """Pure-Python BFS."""
    data = extract_level(level_idx)
    buttons = data["buttons"]
    initial = data["initial_tiles"]
    goal_ids = data["goal_ids"]
    goalo_ids = data["goalo_ids"]
    bgh_targets = data["bgh_targets"]
    fdg_targets = data["fdg_targets"]

    baseline = [33, 22, 31, 23, 33, 34, 73, 173][level_idx]
    limit = min(baseline + 5, 200)

    print(f"Level {level_idx+1}: baseline={baseline}, limit={limit}, buttons={len(buttons)}, "
          f"goals={len(goal_ids)}, goalos={len(goalo_ids)}, "
          f"bgh_targets={bgh_targets}, fdg_targets={fdg_targets}", flush=True)

    if not goal_ids and not goalo_ids:
        print("  No goals to match!", flush=True)
        return None

    start = make_state(initial, goal_ids, goalo_ids)
    if check_win(initial, goal_ids, goalo_ids, bgh_targets, fdg_targets):
        print("  Already won!", flush=True)
        return []

    queue = deque()
    queue.append(([], initial))
    visited = {start}
    iters = 0

    while queue:
        path, tiles = queue.popleft()
        iters += 1
        if iters % 100000 == 0:
            print(f"  iter={iters} q={len(queue)} d={len(path)} v={len(visited)}", flush=True)

        if len(path) >= limit:
            continue

        for i, (dx, dy, perm) in enumerate(buttons):
            new_tiles = apply_perm(tiles, perm)
            new_path = path + [i]

            if check_win(new_tiles, goal_ids, goalo_ids, bgh_targets, fdg_targets):
                clicks = [(buttons[j][0], buttons[j][1]) for j in new_path]
                print(f"  FOUND! {len(new_path)} clicks ({iters} iters)", flush=True)
                return clicks

            key = make_state(new_tiles, goal_ids, goalo_ids)
            if key not in visited:
                visited.add(key)
                queue.append((new_path, new_tiles))

    print(f"  No solution ({iters} iters, {len(visited)} states)", flush=True)
    return None


def verify_with_api(solutions):
    """Verify all solutions with the arc_agi API."""
    arcade = arc_agi.Arcade()
    env = arcade.make("lp85-305b61c3", render_mode=None)
    result = env.reset()
    total = 0
    for level_idx in range(len(solutions)):
        for (dx, dy) in solutions[level_idx]:
            result = env.step(CLICK, data={"x": dx, "y": dy})
            total += 1
        print(f"  Level {level_idx+1}: {len(solutions[level_idx])} clicks, "
              f"levels={result.levels_completed}, state={result.state}")
    print(f"\nTotal: {total}, State: {result.state}")
    return str(result.state) == "GameState.WIN"


if __name__ == "__main__":
    all_solutions = {}
    for level in range(8):
        path = bfs_solve(level)
        if path is not None:
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
        if verify_with_api(all_solutions):
            print("ALL VERIFIED!")
