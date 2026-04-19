"""G50T L6: 2-ghost BFS. Ghost A holds sw[0], Ghost B holds sw[1].

Paths:
  sw[0] = (43,25) via LLU (3 moves)
  sw[1] = (31,25) via LLULL (5 moves)

Prefix: LLU + ACTION5 + LLULL + ACTION5
"""
import importlib.util
from collections import deque
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'g50t', 'environment_files/g50t/5849a774/g50t.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

ACTION_NAMES = {'U': 'ACTION1', 'D': 'ACTION2', 'L': 'ACTION3', 'R': 'ACTION4'}


def fresh():
    g = mod.G50t()
    g.set_level(5)
    return g


def do(g, name):
    full = name if name.startswith('ACTION') else ACTION_NAMES[name]
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


PREFIX = list('LLU') + ['ACTION5'] + list('LLULL') + ['ACTION5']
MAX_GHOST = max(3, 5)  # ghost path lengths


def main():
    g = fresh()
    apply(g, PREFIX)
    print(f"After prefix ({len(PREFIX)} actions):")
    print(f"  player: {pos(g)}")
    print(f"  doors: {doors(g)}")
    print(f"  ghost count: {len(g.vgwycxsxjz.rloltuowth)}")

    # BFS for win
    start_key = (pos(g), doors(g), 0)
    seen = {start_key: []}
    q = deque([(start_key, [])])
    best = None
    tiles = {pos(g): []}
    while q:
        (p, d, _), path = q.popleft()
        if best and len(path) >= len(best):
            continue
        if len(path) > 40:
            continue
        for name in 'UDLR':
            g2 = fresh()
            apply(g2, PREFIX + path + [name])
            if is_win(g2):
                full = PREFIX + path + [name]
                if not best or len(full) < len(best):
                    best = full
                    print(f"  WIN at total {len(full)} actions")
                break
            new_p = pos(g2)
            new_d = doors(g2)
            new_mc = min(len(path) + 1, MAX_GHOST)
            new_key = (new_p, new_d, new_mc)
            if new_key in seen:
                continue
            seen[new_key] = path + [name]
            q.append((new_key, path + [name]))
            if new_p not in tiles:
                tiles[new_p] = path + [name]

    if best:
        to_letter = {'U': 'U', 'D': 'D', 'L': 'L', 'R': 'R', 'ACTION5': '!'}
        print(f"\n=== L6 SOLUTION ({len(best)} vs baseline 48) ===")
        print(f"Ratio: {100*len(best)/48:.1f}%")
        print(f"Seq: {''.join(to_letter.get(a, '?') for a in best)}")
    else:
        print(f"\nNo win. Reached {len(tiles)} tiles, {len(seen)} states")
        for p in sorted(tiles, key=lambda t: (t[1], t[0]))[:50]:
            print(f"  {p}")


if __name__ == "__main__":
    main()
