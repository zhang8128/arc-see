"""G50T: print the actual rendered pixels to see walls."""
import importlib.util
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'g50t', 'environment_files/g50t/5849a774/g50t.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def show_pixels(g, tag=""):
    px = g.get_pixels(x=0, y=0, width=64, height=64)
    # px is ndarray shape (64, 64), dtype int
    print(f"\n=== {tag} pixels ===")
    # Use hex for each cell
    for row in px:
        line = ''
        for v in row:
            v = int(v)
            if v < 0:
                line += '-'
            elif v < 16:
                line += f'{v:x}'
            else:
                line += '?'
        print(f"  {line}")
    # Count distinct colors
    colors = {}
    for row in px:
        for v in row:
            colors[int(v)] = colors.get(int(v), 0) + 1
    print(f"  distinct colors: {sorted(colors.items())}")


def main():
    g = mod.G50t()
    g.set_level(0)
    show_pixels(g, "L1 initial")

    # After walking
    for _ in range(4):
        g.perform_action(ActionInput(id=GameAction.ACTION4))
    show_pixels(g, "L1 after 4R (at 37,7)")


if __name__ == "__main__":
    main()
