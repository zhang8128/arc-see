"""G50T L7: walking-only reach BFS with door state key."""
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
    g.set_level(6)
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
    return g._state.name == "WIN" or g._current_level_index > 6


ANNOT = {
    (1, 25): 'sw[0]', (49, 1): 'sw[1]', (19, 37): 'sw[2]', (13, 1): 'sw[3]',
    (13, 13): 'ulhh[4]', (13, 25): 'ulhh[5]', (49, 37): 'ulhh[6]', (49, 49): 'ulhh[7]',
    (31, 49): 'WIN',
}


def main():
    g0 = fresh()
    print(f"L7 start: {pos(g0)}, goal: (30,48) → win (31,49)")
    print(f"Initial doors: {doors(g0)}")
    start = (pos(g0), doors(g0))
    seen = {start: []}
    q = deque([(start, [])])
    tiles = {pos(g0): []}
    win_path = None

    while q:
        (p, d), path = q.popleft()
        if len(path) > 30:
            continue
        for name in 'UDLR':
            g = fresh()
            apply(g, path + [name])
            if is_win(g):
                if win_path is None or len(path) + 1 < len(win_path):
                    win_path = path + [name]
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

    print(f"\nReached {len(tiles)} tiles")
    for p in sorted(tiles, key=lambda t: (t[1], t[0])):
        ann = f"  <-- {ANNOT[p]}" if p in ANNOT else ""
        print(f"  {p}  via {''.join(tiles[p])}{ann}")

    missing = [t for t in ANNOT if t not in tiles]
    print(f"\nUnreachable: {missing}")
    if win_path:
        print(f"WIN via walking: {''.join(win_path)} ({len(win_path)} moves)")


if __name__ == "__main__":
    main()
