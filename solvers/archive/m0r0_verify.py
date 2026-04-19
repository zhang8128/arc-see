"""Verify M0R0 solutions with game engine and API."""
import importlib.util
import arc_agi
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('m0r0', 'environment_files/m0r0/dadda488/m0r0.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

DIR_NAMES = ["U", "D", "L", "R"]
GAME_DIRS = [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4]
CLICK = GameAction.ACTION6

GRID_MAP = {(11, 11): (4, 4, 5), (13, 13): (6, 6, 4), (15, 15): (2, 2, 4)}

LEVEL_CVCERS = [[], [], [(1,3),(6,2),(8,6)], [(5,5)], [], [(6,9)]]

# Solutions from the solver
SOLUTIONS = {
    0: "U U L U L U U U U U R U R R R".split(),
    1: "D L L L D D D R R U R R D D D D D D R R R U L".split(),
    2: None,  # Will be filled from decompose solver
    3: None,
    4: None,
    5: "U U S L U U L U U U U L X D D D S D D X D L D D D R R R R R R D R D U U U U".split(),
}

# Get L3-L5 solutions
import sys; sys.path.insert(0, 'solvers')
from m0r0_decompose import solve_level3, solve_level4, solve_level5
SOLUTIONS[2] = solve_level3()
SOLUTIONS[3] = solve_level4()
SOLUTIONS[4] = solve_level5()


def grid_to_display(gx, gy, grid_size):
    bx, by, cs = GRID_MAP[grid_size]
    return bx + gx * cs, by + gy * cs


def replay_with_engine(level_idx, path):
    """Replay a solution path using the game engine."""
    g = mod.M0r0()
    g.set_level(level_idx)
    gs = g.current_level.grid_size

    cvcers = list(sorted(LEVEL_CVCERS[level_idx]))
    mode = -1  # player mode

    for i, name in enumerate(path):
        if name in ("U", "D", "L", "R"):
            idx = DIR_NAMES.index(name)
            g.perform_action(ActionInput(id=GAME_DIRS[idx]))
        elif name.startswith("C("):
            # Position-based click: C(x,y)
            coords = name[2:-1].split(",")
            gx, gy = int(coords[0]), int(coords[1])
            dx, dy = grid_to_display(gx, gy, gs)
            g.perform_action(ActionInput(id=CLICK, data={"x": dx, "y": dy}))
        elif name.startswith("C"):
            # Index-based click (legacy): C0, C1, etc.
            ci = int(name[1:])
            current = g.current_level.get_sprites_by_name("cvcer")
            cvcers_sorted = sorted([(c.x, c.y) for c in current])
            cx, cy = cvcers_sorted[ci]
            dx, dy = grid_to_display(cx, cy, gs)
            g.perform_action(ActionInput(id=CLICK, data={"x": dx, "y": dy}))
        elif name == "S":
            # Select the only cvcer
            current = g.current_level.get_sprites_by_name("cvcer")
            if current:
                cx, cy = current[0].x, current[0].y
                dx, dy = grid_to_display(cx, cy, gs)
                g.perform_action(ActionInput(id=CLICK, data={"x": dx, "y": dy}))
        elif name == "X":
            dx, dy = grid_to_display(0, 0, gs)
            g.perform_action(ActionInput(id=CLICK, data={"x": dx, "y": dy}))

    return g._current_level_index, g._state.name


def replay_with_api(all_solutions):
    """Replay all solutions using the official API."""
    arcade = arc_agi.Arcade()
    env = arcade.make("m0r0-dadda488", render_mode=None)
    result = env.reset()

    for level_idx in range(6):
        g_tmp = mod.M0r0()
        g_tmp.set_level(level_idx)
        gs = g_tmp.current_level.grid_size
        path = all_solutions[level_idx]
        cvcers = list(sorted(LEVEL_CVCERS[level_idx]))
        mode = -1

        for name in path:
            if name in ("U", "D", "L", "R"):
                idx = DIR_NAMES.index(name)
                result = env.step(GAME_DIRS[idx])
            elif name.startswith("C("):
                coords = name[2:-1].split(",")
                gx, gy = int(coords[0]), int(coords[1])
                dx, dy = grid_to_display(gx, gy, gs)
                result = env.step(CLICK, data={"x": dx, "y": dy})
            elif name.startswith("C"):
                ci = int(name[1:])
                # For legacy index-based: use game engine to find positions
                g_track = mod.M0r0()
                g_track.set_level(level_idx)
                # Can't easily track here; just pass the sorted cvcers
                curr = sorted(LEVEL_CVCERS[level_idx])  # Use initial as fallback
                cx, cy = curr[ci] if ci < len(curr) else (0, 0)
                dx, dy = grid_to_display(cx, cy, gs)
                result = env.step(CLICK, data={"x": dx, "y": dy})
            elif name == "S":
                curr = LEVEL_CVCERS[level_idx]
                if curr:
                    cx, cy = curr[0]
                    dx, dy = grid_to_display(cx, cy, gs)
                    result = env.step(CLICK, data={"x": dx, "y": dy})
            elif name == "X":
                dx, dy = grid_to_display(0, 0, gs)
                result = env.step(CLICK, data={"x": dx, "y": dy})

        print(f"  Level {level_idx+1}: {len(path)} moves, levels={result.levels_completed}")

    total = sum(len(all_solutions[i]) for i in range(6))
    print(f"\nTotal: {total} moves, State: {result.state}")
    return result


if __name__ == "__main__":
    print("Verifying with game engine...", flush=True)
    for level_idx in range(6):
        path = SOLUTIONS[level_idx]
        if path is None:
            print(f"  Level {level_idx+1}: NO SOLUTION")
            break
        level_after, state = replay_with_engine(level_idx, path)
        ok = level_after > level_idx or state == "WIN"
        print(f"  Level {level_idx+1}: {len(path)} moves → level={level_after} state={state} {'✓' if ok else '✗'}")
        if not ok:
            break

    print("\nVerifying with API...", flush=True)
    result = replay_with_api(SOLUTIONS)
