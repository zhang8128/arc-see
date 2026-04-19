"""R11L: brute BFS L1 with coarse click grid."""
import importlib.util
from collections import deque
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


def state_key(g):
    return ((g.ftmaz[0].x, g.ftmaz[0].y),
            (g.ftmaz[1].x, g.ftmaz[1].y),
            (g.mjdkn.x, g.mjdkn.y),
            g.winning, g._current_level_index)


def is_win(g):
    return g.winning or g._state.name == "WIN" or g._current_level_index > 0


def main():
    # Coarse click grid
    CANDIDATES = [(x, y) for x in range(0, 68, 4) for y in range(0, 72, 4)]
    print(f"Click candidates: {len(CANDIDATES)}")

    max_depth = 7
    g0 = fresh()
    start = state_key(g0)
    seen = {start: []}
    q = deque([(start, [])])
    found = None

    while q:
        key, path = q.popleft()
        if len(path) >= max_depth:
            continue
        for cx, cy in CANDIDATES:
            g = fresh()
            for (px, py) in path:
                click(g, px, py)
            click(g, cx, cy)
            if is_win(g):
                found = path + [(cx, cy)]
                print(f"WIN at {len(found)} clicks: {found}")
                break
            nk = state_key(g)
            if nk in seen:
                continue
            seen[nk] = path + [(cx, cy)]
            q.append((nk, path + [(cx, cy)]))
        if found:
            break
        if len(seen) > 3000:
            print(f"  states explored: {len(seen)}")
            break

    if not found:
        print(f"No WIN found in {max_depth} clicks, explored {len(seen)} states")
        # Show reachable legs positions
        positions = set()
        for k in seen:
            positions.add(k[0])
            positions.add(k[1])
        print(f"Distinct leg positions seen: {len(positions)}")


if __name__ == "__main__":
    main()
