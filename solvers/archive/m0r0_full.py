"""M0R0 solver — mirror movement puzzle with cvcer (movable walls) support.
BFS with state = (piece_positions, cvcer_positions, cancelled, mode)."""
import importlib.util, copy
import arc_agi
from collections import deque
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('m0r0', 'environment_files/m0r0/dadda488/m0r0.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

UP, DOWN, LEFT, RIGHT = GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4
CLICK = GameAction.ACTION6
DIRS = [UP, DOWN, LEFT, RIGHT]
DIR_NAMES = "UDLR"
PIECE_NAMES = ["qzfkx-ubwff-idtiq", "qzfkx-ubwff-crkfz", "qzfkx-kncqr-idtiq", "qzfkx-kncqr-crkfz"]
BASELINES = [30, 209, 83, 86, 436, 126]

# Grid-to-display coordinate mapping per grid size
GRID_MAP = {
    (11, 11): (4, 4, 5),   # base_x, base_y, cell_size
    (13, 13): (6, 6, 4),
    (15, 15): (2, 2, 4),
}


def grid_to_display(gx, gy, grid_size):
    bx, by, cs = GRID_MAP[grid_size]
    return bx + gx * cs, by + gy * cs


def get_state(g):
    """Get hashable state: piece positions + cvcer positions + cancelled + mode."""
    positions = []
    for pn in PIECE_NAMES:
        sps = g.current_level.get_sprites_by_name(pn)
        if sps:
            positions.append((sps[0].x, sps[0].y))
        else:
            positions.append(None)

    cvcers = g.current_level.get_sprites_by_name("cvcer")
    cvcer_pos = tuple(sorted((c.x, c.y) for c in cvcers))

    # Mode: which cvcer is selected (by position), or None for player mode
    mode = None
    if g.cfwgj and not g.vmcbq:
        mode = (g.cfwgj.x, g.cfwgj.y)

    return (tuple(positions), cvcer_pos, frozenset(g.fqunj), mode)


def make_click(gx, gy, grid_size):
    dx, dy = grid_to_display(gx, gy, grid_size)
    return ActionInput(id=CLICK, data={"x": dx, "y": dy})


def bfs_solve(level_idx, max_states=2_000_000):
    g0 = mod.M0r0()
    g0.set_level(level_idx)
    baseline = BASELINES[level_idx]
    limit = min(baseline + 10, 150)
    grid_size = g0.current_level.grid_size

    # Check if cvcers exist
    cvcers = g0.current_level.get_sprites_by_name("cvcer")
    has_cvcers = len(cvcers) > 0

    start = get_state(g0)
    print(f"Level {level_idx+1}: baseline={baseline}, limit={limit}, grid={grid_size}, cvcers={len(cvcers)}", flush=True)

    queue = deque([(g0, [])])  # game state, action list
    visited = {start}
    iters = 0

    while queue:
        g, path = queue.popleft()
        iters += 1
        if iters % 10000 == 0:
            print(f"  iter={iters} q={len(queue)} d={len(path)} v={len(visited)}", flush=True)
        if len(path) >= limit:
            continue
        if len(visited) >= max_states:
            print(f"  State limit reached ({max_states})", flush=True)
            break

        # Generate actions based on mode
        actions = []
        is_player_mode = g.vmcbq

        # UDLR always available
        for i, d in enumerate(DIRS):
            actions.append((ActionInput(id=d), DIR_NAMES[i]))

        if has_cvcers:
            if is_player_mode:
                # Can click on cvcers to select them
                current_cvcers = g.current_level.get_sprites_by_name("cvcer")
                for ci, c in enumerate(current_cvcers):
                    click_action = make_click(c.x, c.y, grid_size)
                    actions.append((click_action, f"C({c.x},{c.y})"))
            else:
                # Can click to deselect (click on wall position (0,0))
                click_action = make_click(0, 0, grid_size)
                actions.append((click_action, "X"))

        for action, name in actions:
            g2 = copy.deepcopy(g)
            g2.perform_action(action)

            if g2._current_level_index > level_idx or g2._state.name == "WIN":
                result_path = path + [name]
                result_str = " ".join(result_path)
                print(f"  FOUND! {len(result_path)} moves ({iters} iters): {result_str}", flush=True)
                return result_path
            if g2._state.name == "GAME_OVER":
                continue

            st = get_state(g2)
            if st not in visited:
                visited.add(st)
                queue.append((g2, path + [name]))

    print(f"  No solution ({iters} iters, {len(visited)} states)", flush=True)
    return None


def path_to_actions(path, grid_size):
    """Convert path names to ActionInput objects for verification."""
    actions = []
    for name in path:
        if name in "UDLR":
            idx = DIR_NAMES.index(name)
            actions.append(ActionInput(id=DIRS[idx]))
        elif name.startswith("C("):
            # Parse click coords
            coords = name[2:-1].split(",")
            gx, gy = int(coords[0]), int(coords[1])
            actions.append(make_click(gx, gy, grid_size))
        elif name == "X":
            actions.append(make_click(0, 0, grid_size))
    return actions


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
    baseline = sum(BASELINES)
    print(f"Solved {len(all_solutions)}/6, Total: {total}, Baseline: {baseline}", flush=True)

    if len(all_solutions) == 6:
        print("\nVerifying with API...", flush=True)
        arcade = arc_agi.Arcade()
        env = arcade.make("m0r0-dadda488", render_mode=None)
        result = env.reset()

        for level_idx in range(6):
            g_tmp = mod.M0r0()
            g_tmp.set_level(level_idx)
            gs = g_tmp.current_level.grid_size
            acts = path_to_actions(all_solutions[level_idx], gs)
            for act in acts:
                if act.id == CLICK:
                    result = env.step(act.id, data=act.data)
                else:
                    result = env.step(act.id)
            print(f"  Level {level_idx+1}: {len(all_solutions[level_idx])} moves, levels={result.levels_completed}")

        print(f"\nTotal: {total}, State: {result.state}")
        assert str(result.state) == "GameState.WIN"
        print("ALL VERIFIED!")
