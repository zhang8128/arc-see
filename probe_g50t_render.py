"""G50T: render the actual L1 frame and visualize walls vs reachable area."""
import importlib.util
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'g50t', 'environment_files/g50t/5849a774/g50t.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def try_render(g):
    """Try various ways to render the game."""
    # Method 1: get_pixels with frame bounds
    for wh in [(64, 64), (80, 80), (60, 60)]:
        try:
            px = g.get_pixels(x=0, y=0, width=wh[0], height=wh[1])
            print(f"  get_pixels(0,0,{wh[0]},{wh[1]}) -> {type(px).__name__} "
                  f"len={len(px) if hasattr(px, '__len__') else '?'}")
            if hasattr(px, '__len__') and len(px) > 0:
                print(f"    first row len: {len(px[0]) if hasattr(px[0], '__len__') else 'scalar'}")
                return px
        except Exception as e:
            print(f"  get_pixels({wh}) error: {type(e).__name__}: {e}")
    return None


def render_frame(g):
    """Manually render: player position + all visible entities' bounding boxes."""
    W, H = 64, 64
    grid = [['.'] * W for _ in range(H)]
    eng = g.vgwycxsxjz
    p = eng.dzxunlkwxt
    # Mark player
    if 0 <= p.x < W and 0 <= p.y < H:
        grid[p.y][p.x] = 'P'
    # Goal
    goal = eng.whftgckbcu
    for dy in range(goal.height):
        for dx in range(goal.width):
            y, x = goal.y + dy, goal.x + dx
            if 0 <= y < H and 0 <= x < W:
                grid[y][x] = 'G'
    # Hamay list (obstacles)
    for i, e in enumerate(eng.hamayflsib):
        for dy in range(e.height):
            for dx in range(e.width):
                y, x = e.y + dy, e.x + dx
                if 0 <= y < H and 0 <= x < W:
                    grid[y][x] = 'H'
    # Uwx list
    for i, e in enumerate(eng.uwxkstolmf):
        for dy in range(e.height):
            for dx in range(e.width):
                y, x = e.y + dy, e.x + dx
                if 0 <= y < H and 0 <= x < W:
                    grid[y][x] = 'U'
    # Dro list (top-left indicators)
    for i, e in enumerate(eng.drofvwhbxb):
        for dy in range(e.height):
            for dx in range(e.width):
                y, x = e.y + dy, e.x + dx
                if 0 <= y < H and 0 <= x < W:
                    grid[y][x] = 'd'
    # The maze/background? afbbgvkpip
    afb = eng.afbbgvkpip
    print(f"  afbbgvkpip: pos=({afb.x},{afb.y}) size={afb.width}x{afb.height} "
          f"type={type(afb).__name__}")
    # Don't overlay the maze since it'd cover everything
    return grid


def print_grid(grid, title=""):
    print(f"\n{title}")
    for row in grid:
        print('  ' + ''.join(row))


def main():
    g = mod.G50t()
    g.set_level(0)
    print("=== Render attempts ===")
    try_render(g)

    print("\n=== Entity overlay grid (initial) ===")
    grid = render_frame(g)
    print_grid(grid)

    # Now after triggering the shift
    print("\n=== After walking to (37, 7) ===")
    for _ in range(4):
        g.perform_action(ActionInput(id=GameAction.ACTION4))
    grid = render_frame(g)
    print_grid(grid)

    # Maze layer: does afbbgvkpip have a tiles/grid attr?
    afb = g.vgwycxsxjz.afbbgvkpip
    print("\n=== afbbgvkpip inspection ===")
    for name in sorted(dir(afb)):
        if name.startswith('_'):
            continue
        try:
            v = getattr(afb, name)
        except Exception:
            continue
        if callable(v):
            continue
        vstr = repr(v)[:120]
        print(f"  {name} = {vstr}")


if __name__ == "__main__":
    main()
