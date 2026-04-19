"""G50T L3: try ghost holding switch[1] + latched door[2].

Prefix: UURRRRDDDDR + ACTION5
  - Walks (7,19)→(31,19) [latches door[2]] →...→ (37,31)=switch[1]
  - ACTION5 saves ghost A with 11-move path, new player spawns at (7,19)
  - On live move 1, ghost A replays move[0]
  - After live move 11, ghost A is frozen on (37,31) holding switch[1]

Then BFS from new player position until goal. During live moves 1-10, switch[1]
is NOT held (ghost A still walking). So BFS should plan a path that spends the
first ~11 moves in limbo (reachable area with just door[2] latched) and on
move 12+, take advantage of switch[1]'s door[0] shift.
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
    g.set_level(2)
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
    return tuple((d.x, d.y) for d in g.vgwycxsxjz.uwxkstolmf)


def is_win(g):
    return g._state.name == "WIN" or g._current_level_index > 2


PREFIX = list('UURRRRDDDDR') + ['ACTION5']


def main():
    g = fresh()
    apply(g, PREFIX)
    print(f"After prefix ({len(PREFIX)} actions):")
    print(f"  player: {pos(g)}")
    print(f"  doors: {doors(g)}")
    print(f"  switches: {tuple(h.dijhfchobv for h in g.vgwycxsxjz.hamayflsib)}")
    print(f"  ghost count: {len(g.vgwycxsxjz.rloltuowth)}")

    # BFS from here
    print("\nBFS for win...")
    start_key = (pos(g), doors(g))
    seen = {start_key: []}
    q = deque([(start_key, [])])
    best = None
    while q:
        (p, _), path = q.popleft()
        if best and len(path) >= len(best):
            continue
        if len(path) > 40:
            continue
        for name in 'UDLR':
            g2 = fresh()
            apply(g2, PREFIX + path + [name])
            if is_win(g2):
                full = PREFIX + path + [name]
                print(f"WIN at phase-2 move {len(path)+1}, total {len(full)} actions")
                if not best or len(full) < len(best):
                    best = full
                break
            new_p = pos(g2)
            new_d = doors(g2)
            new_key = (new_p, new_d)
            if new_key in seen:
                continue
            seen[new_key] = path + [name]
            q.append((new_key, path + [name]))

    if best:
        print(f"\n=== SOLUTION ({len(best)} actions vs baseline 86) ===")
        print(f"Ratio: {100*len(best)/86:.1f}%")
        print(''.join(a if len(a)==1 else f'[{a}]' for a in best))
    else:
        print(f"\nNo win. {len(seen)} states explored.")
        # Show reachable tiles
        tiles = set(k[0] for k in seen.keys())
        print(f"Distinct player positions: {len(tiles)}")
        for t in sorted(tiles, key=lambda p: (p[1], p[0])):
            print(f"  {t}")


if __name__ == "__main__":
    main()
