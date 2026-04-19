"""G50T L3: full 2-ghost solve.

Strategy:
  Phase A: walk to switch[1], ACTION5 → ghost A saved (11 moves)
           path: UURRRRDDDDR
  Phase B: walk to switch[0], ACTION5 → ghost B saved (21 moves)
           path: UURRRRRRRDDDDDDDLLLLL
  Phase C: live player walks 21+ moves (ghost B's path length) while
           ghost A replays (11 moves) and freezes on sw1, then ghost B
           replays (21 moves) and freezes on sw0. On move 21+, door[1]
           shifts and the goal becomes reachable.

We BFS phase C using the engine as ground truth. State key = full engine
fingerprint (player position + door positions). Ghost positions are
implicit in live move count + ghost paths.
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


PREFIX = (
    list('UURRRRDDDDR') + ['ACTION5']  # 12 actions: walk sw1 + save ghost A
    + list('UURRRRRRRDDDDDDDLLLLL') + ['ACTION5']  # 22 actions: walk sw0 + save ghost B
)


def main():
    g = fresh()
    apply(g, PREFIX)
    print(f"After prefix ({len(PREFIX)} actions):")
    print(f"  player: {pos(g)}")
    print(f"  doors: {doors(g)}")
    print(f"  ghost count: {len(g.vgwycxsxjz.rloltuowth)}")

    # BFS phase C. State key = (player_pos, doors, live_move_count_clamp).
    # After move 21, both ghosts frozen so move count no longer matters.
    print("\nBFS phase C...")
    start_key = (pos(g), doors(g), 0)
    seen = {start_key: []}
    q = deque([(start_key, [])])
    best = None
    max_depth = 45
    while q:
        (p, d, mc), path = q.popleft()
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
                    print(f"WIN at phase-C move {len(path)+1}, total {len(full)}")
                break
            new_p = pos(g2)
            new_d = doors(g2)
            new_mc = min(len(path) + 1, 21)
            new_key = (new_p, new_d, new_mc)
            if new_key in seen:
                continue
            seen[new_key] = path + [name]
            q.append((new_key, path + [name]))

    if best:
        print(f"\n=== L3 SOLUTION ===")
        print(f"Actions: {len(best)} (baseline 86, {100*len(best)/86:.1f}%)")
        # Readable form - note: single-char action names ('U','D','L','R') are
        # used in PREFIX/phase-C lists, while ACTION5 is the full string
        to_letter = {'U': 'U', 'D': 'D', 'L': 'L', 'R': 'R', 'ACTION5': '!'}
        print(''.join(to_letter.get(a, '?') for a in best))
        print(f"\nFull action list:")
        print(best)
    else:
        print(f"\nNo win found in {max_depth} moves of phase C. States: {len(seen)}")
        tiles = set(k[0] for k in seen)
        print(f"Distinct tiles reached: {len(tiles)}")


if __name__ == "__main__":
    main()
