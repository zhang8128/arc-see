"""G50T: enumerate every 6-px grid position and check walkability via the engine."""
import importlib.util
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'g50t', 'environment_files/g50t/5849a774/g50t.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def main():
    g = mod.G50t()
    g.set_level(0)
    eng = g.vgwycxsxjz
    afb = eng.afbbgvkpip
    p = eng.dzxunlkwxt
    uwx = eng.uwxkstolmf[0]

    # Enumerate all 6-grid positions (x from 13 up, y from 7 up, step 6)
    print("=== Walkable positions (player-center on maze, not colliding with uwx) ===")
    print("    13 19 25 31 37 43 49 55")
    reachable = set()
    for y in range(7, 60, 6):
        row = f"y={y:2d} "
        for x in range(13, 60, 6):
            cx, cy = x + 3, y + 3  # player center
            maze_val = afb.esidlbhbhw(cx, cy)
            on_maze = maze_val != -1
            in_uwx = uwx.esidlbhbhw(cx, cy) != -1 if uwx.is_visible else False
            if on_maze and not in_uwx:
                row += " # "
                reachable.add((x, y))
            elif on_maze and in_uwx:
                row += " U "
            elif not on_maze:
                row += " . "
        print(row)

    print(f"\nTotal walkable (single-point check): {len(reachable)}")
    print(f"Includes win pos (43, 49)? {(43, 49) in reachable}")

    # Now enumerate WITH uwx shifted to (19, 37)
    print("\n=== Walkable IF uwx were at (19, 37) ===")
    uwx_old_x = uwx.x
    # Directly check with synthetic uwx position via esidlbhbhw
    # Hack: we'd need to move the sprite. Let me just do it programmatically.
    # Simulate by checking if center would be inside uwx at shifted position.
    def fake_uwx_contains(cx, cy):
        lx = cx - 19
        ly = cy - 37
        if not (0 <= lx < 7 and 0 <= ly < 7):
            return False
        # uwx sprite is rotated 270, so pixels[lx, ly] per engine
        pixels = uwx.xmdjbwrpmv.pixels
        return int(pixels[lx, ly]) != -1

    reach2 = set()
    print("    13 19 25 31 37 43 49 55")
    for y in range(7, 60, 6):
        row = f"y={y:2d} "
        for x in range(13, 60, 6):
            cx, cy = x + 3, y + 3
            maze_val = afb.esidlbhbhw(cx, cy)
            on_maze = maze_val != -1
            in_uwx = fake_uwx_contains(cx, cy)
            if on_maze and not in_uwx:
                row += " # "
                reach2.add((x, y))
            elif on_maze:
                row += " U "
            else:
                row += " . "
        print(row)

    print(f"\nTotal walkable with uwx shifted: {len(reach2)}")
    new_positions = reach2 - reachable
    print(f"NEW positions unlocked: {sorted(new_positions)}")
    print(f"Includes (43, 49)? {(43, 49) in reach2}")


if __name__ == "__main__":
    main()
