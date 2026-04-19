"""M0R0 solution — mirror movement puzzle. 181 total moves, baseline 970.
Run: uv run python solutions/solution_m0r0.py"""
import importlib.util
import arc_agi
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('m0r0', 'environment_files/m0r0/dadda488/m0r0.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

CLICK = GameAction.ACTION6
DIRS = [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4]
DIR_MAP = {"U": 0, "D": 1, "L": 2, "R": 3}
GRID_MAP = {(11, 11): (4, 4, 5), (13, 13): (6, 6, 4), (15, 15): (2, 2, 4)}

SOLUTIONS = [
    # L1: 15 moves
    "U U L U L U U U U U R U R R R".split(),
    # L2: 23 moves
    "D L L L D D D R R U R R D D D D D D R R R U L".split(),
    # L3: 55 moves (24 cvcer + 31 pieces)
    ['C(1,3)', 'U', 'R', 'U', 'X', 'C(6,2)', 'R', 'U', 'R', 'R', 'R', 'R', 'D', 'D', 'D', 'L', 'L', 'U', 'X', 'C(8,6)', 'R', 'R', 'R', 'X', 'U', 'L', 'L', 'U', 'U', 'U', 'R', 'R', 'R', 'U', 'U', 'L', 'L', 'L', 'L', 'U', 'U', 'U', 'U', 'U', 'R', 'R', 'R', 'R', 'D', 'R', 'R', 'D', 'D', 'D', 'R'],
    # L4: 11 moves (5 cvcer + 6 pieces)
    ['C(5,5)', 'L', 'L', 'D', 'X', 'U', 'R', 'D', 'D', 'R', 'R'],
    # L5: 39 moves
    ['L', 'L', 'U', 'U', 'U', 'U', 'L', 'U', 'R', 'R', 'U', 'R', 'R', 'U', 'L', 'L', 'L', 'L', 'U', 'U', 'U', 'L', 'L', 'U', 'U', 'U', 'U', 'U', 'R', 'R', 'U', 'U', 'U', 'U', 'U', 'L', 'L', 'L', 'L'],
    # L6: 38 moves (interleaved)
    "U U S L U U L U U U U L X D D D S D D X D L D D D R R R R R R D R D U U U U".split(),
]


def grid_to_display(gx, gy, grid_size):
    bx, by, cs = GRID_MAP[grid_size]
    return bx + gx * cs, by + gy * cs


if __name__ == "__main__":
    # Verify with game engine first
    print("Verifying with game engine...", flush=True)
    for level_idx in range(6):
        g = mod.M0r0()
        g.set_level(level_idx)
        gs = g.current_level.grid_size
        path = SOLUTIONS[level_idx]

        for name in path:
            if name in ("U", "D", "L", "R"):
                g.perform_action(ActionInput(id=DIRS[DIR_MAP[name]]))
            elif name.startswith("C("):
                coords = name[2:-1].split(",")
                gx, gy = int(coords[0]), int(coords[1])
                dx, dy = grid_to_display(gx, gy, gs)
                g.perform_action(ActionInput(id=CLICK, data={"x": dx, "y": dy}))
            elif name == "S":
                cvcers = g.current_level.get_sprites_by_name("cvcer")
                if cvcers:
                    dx, dy = grid_to_display(cvcers[0].x, cvcers[0].y, gs)
                    g.perform_action(ActionInput(id=CLICK, data={"x": dx, "y": dy}))
            elif name == "X":
                dx, dy = grid_to_display(0, 0, gs)
                g.perform_action(ActionInput(id=CLICK, data={"x": dx, "y": dy}))

        ok = g._current_level_index > level_idx or g._state.name == "WIN"
        print(f"  L{level_idx+1}: {len(path)} moves {'✓' if ok else '✗'}")
        if not ok:
            print("VERIFICATION FAILED")
            exit(1)

    # Submit to API
    print("\nSubmitting to API...", flush=True)
    arcade = arc_agi.Arcade()
    env = arcade.make("m0r0-dadda488", render_mode=None)
    result = env.reset()

    for level_idx in range(6):
        g = mod.M0r0()
        g.set_level(level_idx)
        gs = g.current_level.grid_size
        path = SOLUTIONS[level_idx]

        for name in path:
            if name in ("U", "D", "L", "R"):
                result = env.step(DIRS[DIR_MAP[name]])
                g.perform_action(ActionInput(id=DIRS[DIR_MAP[name]]))
            elif name.startswith("C("):
                coords = name[2:-1].split(",")
                gx, gy = int(coords[0]), int(coords[1])
                dx, dy = grid_to_display(gx, gy, gs)
                result = env.step(CLICK, data={"x": dx, "y": dy})
                g.perform_action(ActionInput(id=CLICK, data={"x": dx, "y": dy}))
            elif name == "S":
                cvcers = g.current_level.get_sprites_by_name("cvcer")
                if cvcers:
                    dx, dy = grid_to_display(cvcers[0].x, cvcers[0].y, gs)
                    result = env.step(CLICK, data={"x": dx, "y": dy})
                    g.perform_action(ActionInput(id=CLICK, data={"x": dx, "y": dy}))
            elif name == "X":
                dx, dy = grid_to_display(0, 0, gs)
                result = env.step(CLICK, data={"x": dx, "y": dy})
                g.perform_action(ActionInput(id=CLICK, data={"x": dx, "y": dy}))

        print(f"  L{level_idx+1}: {len(path)} moves, completed={result.levels_completed}")

    total = sum(len(s) for s in SOLUTIONS)
    print(f"\nTotal: {total} moves (baseline: 970), State: {result.state}")
