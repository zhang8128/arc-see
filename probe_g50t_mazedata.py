"""G50T: dump the actual maze pixel data from afbbgvkpip.xmdjbwrpmv."""
import importlib.util
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'g50t', 'environment_files/g50t/5849a774/g50t.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def print_grid(grid, title=""):
    print(f"\n{title} (shape={grid.shape}, dtype={grid.dtype})")
    # Print with col ruler
    W = grid.shape[1]
    print("     " + ''.join(str((c // 10) % 10) if c % 5 == 0 else ' ' for c in range(W)))
    print("     " + ''.join(str(c % 10) if c % 5 == 0 else ' ' for c in range(W)))
    for r, row in enumerate(grid):
        s = ''
        for v in row:
            v = int(v)
            if v < 0:
                s += '-'
            elif v == 0:
                s += '.'  # wall / transparent
            elif v < 16:
                s += f'{v:x}'
            else:
                s += '?'
        print(f"  r{r:2d} {s}")


def main():
    g = mod.G50t()
    g.set_level(0)

    # Maze layer
    maze = g.vgwycxsxjz.afbbgvkpip.xmdjbwrpmv.pixels
    print_grid(maze, "=== MAZE LAYER (afbbgvkpip) ===")

    # Player sprite
    p = g.vgwycxsxjz.dzxunlkwxt.xmdjbwrpmv.pixels
    print_grid(p, "\n=== PLAYER SPRITE ===")

    # Goal sprite
    goal = g.vgwycxsxjz.whftgckbcu.xmdjbwrpmv
    if hasattr(goal, 'pixels'):
        print_grid(goal.pixels, "\n=== GOAL SPRITE ===")

    # Hamay and uwx sprites (the triggers)
    for name in ('hamayflsib', 'uwxkstolmf', 'drofvwhbxb'):
        lst = getattr(g.vgwycxsxjz, name, [])
        for i, e in enumerate(lst):
            inner = getattr(e, 'xmdjbwrpmv', None)
            if inner is not None and hasattr(inner, 'pixels'):
                print_grid(inner.pixels, f"\n=== {name}[{i}] (pos {e.x},{e.y}) ===")


if __name__ == "__main__":
    main()
