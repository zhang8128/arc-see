"""G50T L6: full reach BFS with door-state in key, and switch mapping."""
import importlib.util
from collections import deque
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'g50t', 'environment_files/g50t/5849a774/g50t.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

ACTIONS = {'U': 'ACTION1', 'D': 'ACTION2', 'L': 'ACTION3', 'R': 'ACTION4'}


def fresh():
    g = mod.G50t()
    g.set_level(5)
    return g


def do(g, name):
    full = name if name.startswith('ACTION') else ACTIONS[name]
    g.perform_action(ActionInput(id=getattr(GameAction, full)))


def apply(g, seq):
    for a in seq:
        do(g, a)


def pos(g):
    p = g.vgwycxsxjz.dzxunlkwxt
    return (p.x, p.y)


def doors(g):
    return tuple((d.x, d.y, bool(d.dijhfchobv)) for d in g.vgwycxsxjz.uwxkstolmf)


def is_win(g):
    return g._state.name == "WIN" or g._current_level_index > 5


ANNOT = {
    (43, 25): 'sw[0]', (31, 25): 'sw[1]', (19, 7): 'sw[2]',
    (1, 7): 'sw[3]', (13, 49): 'sw[4]',
    (43, 49): 'WIN',
}


def main():
    # BFS with (pos, doors) state key
    g0 = fresh()
    start = (pos(g0), doors(g0))
    seen = {start: []}
    q = deque([(start, [])])
    tiles = {pos(g0): []}
    win_path = None
    print(f"Initial doors: {doors(g0)}")

    while q:
        (p, d), path = q.popleft()
        if len(path) > 35:
            continue
        for name in 'UDLR':
            g = fresh()
            apply(g, path + [name])
            if is_win(g):
                if win_path is None or len(path) + 1 < len(win_path):
                    win_path = path + [name]
                    print(f"!!! WIN via walking: {len(win_path)} moves")
                continue
            np_ = pos(g)
            nd = doors(g)
            nk = (np_, nd)
            if nk in seen:
                continue
            seen[nk] = path + [name]
            q.append((nk, path + [name]))
            if np_ not in tiles or len(path + [name]) < len(tiles[np_]):
                tiles[np_] = path + [name]

    print(f"\nReached {len(tiles)} tiles, {len(seen)} unique states")
    for p in sorted(tiles, key=lambda t: (t[1], t[0])):
        ann = f"  <-- {ANNOT[p]}" if p in ANNOT else ""
        print(f"  {p}  via {''.join(tiles[p])}{ann}")
    missing = [t for t in ANNOT if t not in tiles]
    print(f"\nUnreachable: {missing}")
    if win_path:
        print(f"\nWIN path: {''.join(win_path)} ({len(win_path)} moves)")


if __name__ == "__main__":
    main()
