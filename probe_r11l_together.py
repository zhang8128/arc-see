"""R11L: test win conditions — both legs together? Specific target?"""
import importlib.util
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'r11l', 'environment_files/r11l/aa269680/r11l.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def fresh(level=0):
    g = mod.R11l()
    g.set_level(level)
    return g


def click(g, x, y):
    g.perform_action(ActionInput(id=GameAction.ACTION6, data={'x': x, 'y': y}))


def show(g, label):
    print(f"{label}: ft0=({g.ftmaz[0].x},{g.ftmaz[0].y}) ft1=({g.ftmaz[1].x},{g.ftmaz[1].y}) "
          f"winning={g.winning} state={g._state.name} lvl={g._current_level_index} zmxct={g.zmxct.get('kpaac')}")


def main():
    # Test: bring legs together
    g = fresh()
    show(g, "start")
    # Leg 0 at (5,34), leg 1 at (25,57). Try to bring leg 0 to leg 1's spot.
    click(g, 5, 34)  # select leg 0
    show(g, "clicked leg0")
    click(g, 25, 57)  # move leg 0 to leg 1's pos
    show(g, "move leg0 → leg1 pos")

    # Try: both to a random spot (say 40, 40)
    g = fresh()
    click(g, 5, 34)
    click(g, 40, 40)
    show(g, "leg0 → (40,40)")
    click(g, 25, 57)
    click(g, 40, 40)
    show(g, "leg1 → (40,40) (both should overlap)")

    # Try various specific targets — maybe the goal is a tile in the level bg
    # L1 sprite is bvzgd-Level1 at (-5,-6) size 73x78 so world spans x ∈ [-5, 68], y ∈ [-6, 72]
    # Maybe there's a specific target tile. Let me scan positions and see if any trigger winning
    print("\n--- Scan: leg 0 to various positions, see if any trigger winning ---")
    for tx in range(0, 70, 5):
        for ty in range(0, 75, 5):
            g = fresh()
            click(g, g.ftmaz[0].x, g.ftmaz[0].y)  # select leg 0
            click(g, tx, ty)  # move to target
            if g.winning or g._state.name == "WIN":
                print(f"  winning at leg0 → ({tx},{ty}): actual pos ({g.ftmaz[0].x},{g.ftmaz[0].y})")
            if g._current_level_index > 0:
                print(f"  LEVEL UP! leg0 → ({tx},{ty})")
    print("scan done")


if __name__ == "__main__":
    main()
