"""G50T L5: careful reach BFS with awareness of switch toggling.

BFS state = (player_pos, door_states_tuple). This correctly handles toggles
because door state changes on each switch press.

Goal: find the largest reach envelope possible.
"""
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
    g.set_level(4)
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
    return g._state.name == "WIN" or g._current_level_index > 4


ANNOT = {
    (55, 25): 'sw[0]', (19, 37): 'sw[1]', (19, 25): 'sw[2]', (1, 7): 'sw[3]',
    (43, 37): 'ulhh[4]', (43, 49): 'ulhh[5]', (7, 43): 'WIN',
}


def main():
    # BFS with state = (player_pos, door_states)
    g0 = fresh()
    start = (pos(g0), doors(g0))
    seen = {start: []}
    q = deque([(start, [])])
    tile_best = {pos(g0): []}
    door_configs = set()
    door_configs.add(start[1])
    win_path = None

    while q:
        (p, d), path = q.popleft()
        if len(path) >= 30:
            continue
        for name in 'UDLR':
            g = fresh()
            apply(g, path + [name])
            if is_win(g):
                win_path = path + [name]
                print(f"!!! WIN at {len(win_path)} actions (walking only)")
                break
            new_p = pos(g)
            new_d = doors(g)
            new_key = (new_p, new_d)
            if new_key in seen:
                continue
            seen[new_key] = path + [name]
            q.append((new_key, path + [name]))
            if new_p not in tile_best or len(path + [name]) < len(tile_best[new_p]):
                tile_best[new_p] = path + [name]
            door_configs.add(new_d)
        if win_path:
            break

    print(f"\nReached {len(tile_best)} unique tiles, {len(door_configs)} unique door configs.")
    print("\nTiles:")
    for p in sorted(tile_best, key=lambda t: (t[1], t[0])):
        ann = f"  <-- {ANNOT[p]}" if p in ANNOT else ""
        print(f"  {p}  via {''.join(tile_best[p])}{ann}")

    missing = [t for t in ANNOT if t not in tile_best]
    print(f"\nUnreachable annotated tiles: {missing}")

    if win_path:
        print(f"\nWin path: {''.join(win_path)}")


if __name__ == "__main__":
    main()
