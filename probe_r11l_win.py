"""R11L: find the win condition. What position triggers winning=True?"""
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
    print(f"{label}: mjdkn=({g.mjdkn.x},{g.mjdkn.y}) "
          f"ft0=({g.ftmaz[0].x},{g.ftmaz[0].y}) ft1=({g.ftmaz[1].x},{g.ftmaz[1].y}) "
          f"winning={g.winning} state={g._state.name} lvl={g._current_level_index}")


def main():
    # Print level sprite details
    g = fresh()
    print(f"Level sprite (yhfnp[0]): name={g.yhfnp[0].name} pos=({g.yhfnp[0].x},{g.yhfnp[0].y}) size=({g.yhfnp[0].width}x{g.yhfnp[0].height})")

    # Check kdabh (length 256 = 16x16 grid?)
    print(f"\nkdabh first 20 entries:")
    for i, item in enumerate(g.kdabh[:20]):
        print(f"  [{i}] type={type(item).__name__}")
        if hasattr(item, 'x'):
            print(f"      at ({item.x},{item.y})")
            for a in sorted(dir(item)):
                if a.startswith('_') or callable(getattr(item, a, None)):
                    continue
                try:
                    v = getattr(item, a)
                    if isinstance(v, (int, bool, str)) and not isinstance(v, type):
                        print(f"        {a}: {v!r}")
                except:
                    pass

    # Try to walk: click leg 0 at its current spot (to "select"), then click the goal
    # Then click leg 1, then the goal.
    print("\n=== Walk attempt ===")
    g = fresh()
    show(g, "start")
    click(g, 5, 34)  # click on leg 0 ("select it")
    show(g, "after click leg 0")
    click(g, 15, 15)  # move to (13, 13)?
    show(g, "after click (15,15)")
    click(g, 25, 57)  # click on leg 1
    show(g, "after click leg 1")
    click(g, 40, 40)  # move
    show(g, "after click (40,40)")


if __name__ == "__main__":
    main()
