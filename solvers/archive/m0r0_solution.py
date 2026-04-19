"""M0R0 complete solution — solve all 6 levels and submit via API."""
import importlib.util
import arc_agi
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('m0r0', 'environment_files/m0r0/dadda488/m0r0.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

CLICK = GameAction.ACTION6
GAME_DIRS = [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4]
DIR_MAP = {"U": 0, "D": 1, "L": 2, "R": 3}
GRID_MAP = {(11, 11): (4, 4, 5), (13, 13): (6, 6, 4), (15, 15): (2, 2, 4)}


def grid_to_display(gx, gy, grid_size):
    bx, by, cs = GRID_MAP[grid_size]
    return bx + gx * cs, by + gy * cs


def replay_path(env_or_game, path, grid_size, is_api=False):
    """Replay a solution path. Returns list of (action_id, data) tuples."""
    for name in path:
        if name in ("U", "D", "L", "R"):
            d = DIR_MAP[name]
            if is_api:
                env_or_game.step(GAME_DIRS[d])
            else:
                env_or_game.perform_action(ActionInput(id=GAME_DIRS[d]))
        elif name.startswith("C("):
            coords = name[2:-1].split(",")
            gx, gy = int(coords[0]), int(coords[1])
            dx, dy = grid_to_display(gx, gy, grid_size)
            if is_api:
                env_or_game.step(CLICK, data={"x": dx, "y": dy})
            else:
                env_or_game.perform_action(ActionInput(id=CLICK, data={"x": dx, "y": dy}))
        elif name == "S":
            # Select the only cvcer (find its position from game state)
            if not is_api:
                cvcers = env_or_game.current_level.get_sprites_by_name("cvcer")
                if cvcers:
                    dx, dy = grid_to_display(cvcers[0].x, cvcers[0].y, grid_size)
                    env_or_game.perform_action(ActionInput(id=CLICK, data={"x": dx, "y": dy}))
            else:
                # For API, we need to know position — handled separately
                pass
        elif name == "X":
            dx, dy = grid_to_display(0, 0, grid_size)
            if is_api:
                env_or_game.step(CLICK, data={"x": dx, "y": dy})
            else:
                env_or_game.perform_action(ActionInput(id=CLICK, data={"x": dx, "y": dy}))


def verify_with_engine(solutions):
    """Verify each level's solution with the game engine."""
    all_ok = True
    for level_idx in range(6):
        g = mod.M0r0()
        g.set_level(level_idx)
        gs = g.current_level.grid_size
        path = solutions[level_idx]

        replay_path(g, path, gs)

        ok = g._current_level_index > level_idx or g._state.name == "WIN"
        symbol = "✓" if ok else "✗"
        print(f"  L{level_idx+1}: {len(path)} moves → idx={g._current_level_index} state={g._state.name} {symbol}")
        if not ok:
            all_ok = False
    return all_ok


def submit_with_api(solutions):
    """Submit all solutions via the official API."""
    arcade = arc_agi.Arcade()
    env = arcade.make("m0r0-dadda488", render_mode=None)
    result = env.reset()

    for level_idx in range(6):
        # Use game engine to track cvcer positions for S commands
        g = mod.M0r0()
        g.set_level(level_idx)
        gs = g.current_level.grid_size
        path = solutions[level_idx]

        for name in path:
            if name in ("U", "D", "L", "R"):
                d = DIR_MAP[name]
                result = env.step(GAME_DIRS[d])
                g.perform_action(ActionInput(id=GAME_DIRS[d]))
            elif name.startswith("C("):
                coords = name[2:-1].split(",")
                gx, gy = int(coords[0]), int(coords[1])
                dx, dy = grid_to_display(gx, gy, gs)
                result = env.step(CLICK, data={"x": dx, "y": dy})
                g.perform_action(ActionInput(id=CLICK, data={"x": dx, "y": dy}))
            elif name == "S":
                cvcers = g.current_level.get_sprites_by_name("cvcer")
                if cvcers:
                    gx, gy = cvcers[0].x, cvcers[0].y
                    dx, dy = grid_to_display(gx, gy, gs)
                    result = env.step(CLICK, data={"x": dx, "y": dy})
                    g.perform_action(ActionInput(id=CLICK, data={"x": dx, "y": dy}))
            elif name == "X":
                dx, dy = grid_to_display(0, 0, gs)
                result = env.step(CLICK, data={"x": dx, "y": dy})
                g.perform_action(ActionInput(id=CLICK, data={"x": dx, "y": dy}))

        print(f"  L{level_idx+1}: {len(path)} moves, completed={result.levels_completed}")

    total = sum(len(solutions[i]) for i in range(6))
    print(f"\nTotal: {total}, State: {result.state}")
    return result


if __name__ == "__main__":
    import sys
    sys.path.insert(0, 'solvers')

    # Compute solutions
    print("Computing solutions...", flush=True)
    from m0r0_decompose import solve_level_no_cvcers, solve_level3, solve_level4, solve_level5
    from m0r0_l6 import bfs_solve as l6_solve

    solutions = {}
    solvers = [
        ("L1", lambda: solve_level_no_cvcers(0)),
        ("L2", lambda: solve_level_no_cvcers(1)),
        ("L3", solve_level3),
        ("L4", solve_level4),
        ("L5", solve_level5),
        ("L6", l6_solve),
    ]

    for name, solver in solvers:
        print(f"\n{name}:", flush=True)
        r = solver()
        if r:
            solutions[len(solutions)] = r
            print(f"  → {len(r)} moves")
        else:
            print(f"  → FAILED")
            break

    if len(solutions) < 6:
        print("Not all levels solved!")
        exit(1)

    # Verify with game engine
    print("\n" + "=" * 50)
    print("Verifying with game engine...", flush=True)
    ok = verify_with_engine(solutions)

    if ok:
        print("\nSubmitting to API...", flush=True)
        result = submit_with_api(solutions)
    else:
        print("\nVerification FAILED — not submitting")
