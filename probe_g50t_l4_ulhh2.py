"""G50T L4: after reaching ulhh[2], BFS the full reach to see if it changes.

Also test: what can we reach from (25, 37)?
Also test: does the ulhh[2] state persist after a successful step-off (L)?
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
    g.set_level(3)
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


def ulhh_sets(g):
    return tuple((len(h.rqxibulywa), len(h.vbqvjbxkfm))
                 for h in g.vgwycxsxjz.hamayflsib
                 if type(h).__name__ == 'ulhhdeoyok')


def ulhh_visible(g):
    return tuple(h.is_visible for h in g.vgwycxsxjz.hamayflsib
                 if type(h).__name__ == 'ulhhdeoyok')


def doors(g):
    return tuple((d.x, d.y) for d in g.vgwycxsxjz.uwxkstolmf)


def state_label(g):
    return f"player={pos(g)} doors={doors(g)} ulhh_sets={ulhh_sets(g)} ulhh_vis={ulhh_visible(g)}"


def is_win(g):
    return g._state.name == "WIN" or g._current_level_index > 3


# Prefix: walk to switch[1] via DDRD, ACTION5, then 4 moves for ghost to freeze,
# then walk to ulhh[2] via DDDDRRR = 7 more moves
PREFIX = list('DDRD') + ['ACTION5'] + list('LLLD') + list('DDDD') + list('RRR')


def main():
    g = fresh()
    apply(g, PREFIX)
    print(f"After prefix ({len(PREFIX)} actions): {state_label(g)}")

    # Test: try all 4 directions from ulhh[2]
    print("\nDirections from (25, 37):")
    for d in 'UDLR':
        g2 = fresh()
        apply(g2, PREFIX + [d])
        print(f"  {d}: {state_label(g2)}")

    # Now, from the post-prefix state, BFS: what tiles are reachable?
    # State key = (player_pos, doors, ulhh_sets_lens)
    print("\nBFS from post-ulhh[2] state...")
    start_key = (pos(g), doors(g), ulhh_sets(g))
    seen = {start_key: []}
    q = deque([(start_key, [])])
    tiles = {pos(g): []}
    win_seq = None
    while q:
        (p, d, u), path = q.popleft()
        if len(path) >= 25:
            continue
        for name in 'UDLR':
            g2 = fresh()
            apply(g2, PREFIX + path + [name])
            if is_win(g2):
                win_seq = PREFIX + path + [name]
                print(f"  WIN at {len(win_seq)} actions: {''.join(c if c != 'ACTION5' else '!' for c in path + [name])}")
                break
            new_p = pos(g2)
            new_d = doors(g2)
            new_u = ulhh_sets(g2)
            new_key = (new_p, new_d, new_u)
            if new_key in seen:
                continue
            seen[new_key] = path + [name]
            q.append((new_key, path + [name]))
            if new_p not in tiles:
                tiles[new_p] = path + [name]
        if win_seq:
            break

    print(f"\nReachable tiles: {len(tiles)}")
    for t in sorted(tiles, key=lambda p: (p[1], p[0])):
        marker = ""
        if t == (7, 49): marker = "  <-- WIN tile"
        elif t == (25, 49): marker = "  <-- ulhh[3]"
        elif t == (25, 37): marker = "  <-- ulhh[2]"
        print(f"  {t}{marker}")

    # Check: is switch[1] still held (ghost A frozen)?
    print(f"\nFinal switch[1] state: {g.vgwycxsxjz.hamayflsib[1].dijhfchobv}")
    print(f"Final ghost positions: {[(k.x, k.y) for k in g.vgwycxsxjz.rloltuowth]}")


if __name__ == "__main__":
    main()
