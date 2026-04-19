"""G50T L7: ghost A holds sw[3]. What does the reach open up?"""
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
    g.set_level(6)
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
    return g._state.name == "WIN" or g._current_level_index > 6


ANNOT = {
    (1, 25): 'sw[0]', (49, 1): 'sw[1]', (19, 37): 'sw[2]', (13, 1): 'sw[3]',
    (13, 13): 'ulhh[4]', (13, 25): 'ulhh[5]', (49, 37): 'ulhh[6]', (49, 49): 'ulhh[7]',
    (31, 49): 'WIN',
}

# Ghost path to sw[3]: DDLRUULLUU (10 moves, ends at (13,1) via teleport)
SW3_PATH = list('DDLRUULLUU')
PREFIX = SW3_PATH + ['ACTION5']


def main():
    g = fresh()
    apply(g, PREFIX)
    print(f"After prefix ({len(PREFIX)} actions):")
    print(f"  player: {pos(g)}")
    print(f"  doors: {doors(g)}")
    print(f"  ghosts: {len(g.vgwycxsxjz.rloltuowth)}")

    # BFS for goal
    max_depth = 70
    start = (pos(g), doors(g), 0)
    seen = {start: []}
    q = deque([(start, [])])
    best = None
    tile_best = {pos(g): []}
    while q:
        (p, d, _), path = q.popleft()
        if best and len(path) >= len(best):
            continue
        if len(path) > max_depth:
            continue
        for name in 'UDLR':
            g2 = fresh()
            apply(g2, PREFIX + path + [name])
            if is_win(g2):
                full = PREFIX + path + [name]
                if not best or len(full) < len(best):
                    best = full
                    print(f"  WIN at {len(full)} actions!")
                break
            new_p = pos(g2)
            new_d = doors(g2)
            new_mc = min(len(path) + 1, len(SW3_PATH))
            new_key = (new_p, new_d, new_mc)
            if new_key in seen:
                continue
            seen[new_key] = path + [name]
            q.append((new_key, path + [name]))
            if new_p not in tile_best:
                tile_best[new_p] = path + [name]

    if best:
        to_letter = {'U': 'U', 'D': 'D', 'L': 'L', 'R': 'R', 'ACTION5': '!'}
        print(f"\nSOLUTION: {len(best)} vs baseline 67 ({100*len(best)/67:.1f}%)")
        print(''.join(to_letter.get(a, '?') for a in best))
    else:
        print(f"\nNo win. Tiles reached: {len(tile_best)}")
        for p in sorted(tile_best, key=lambda t: (t[1], t[0])):
            ann = f"  <-- {ANNOT[p]}" if p in ANNOT else ""
            print(f"  {p}{ann}")


if __name__ == "__main__":
    main()
