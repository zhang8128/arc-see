"""G50T L5: test sw[0], then test ghost-held sw[1] with latches applied."""
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
    return tuple((d.x, d.y, bool(d.dpdubazedr), bool(d.dijhfchobv))
                 for d in g.vgwycxsxjz.uwxkstolmf)


def sw_state(g):
    return tuple(getattr(h, 'dijhfchobv', None) for h in g.vgwycxsxjz.hamayflsib)


ANNOT = {
    (55, 25): 'sw[0]', (19, 37): 'sw[1]', (19, 25): 'sw[2]', (1, 7): 'sw[3]',
    (43, 37): 'ulhh[4]', (43, 49): 'ulhh[5]', (7, 43): 'WIN',
}


def bfs_from(prefix, max_depth=45):
    g0 = fresh()
    apply(g0, prefix)
    start = pos(g0)
    tiles = {start: []}
    q = deque([(start, [])])
    while q:
        p, path = q.popleft()
        if len(path) >= max_depth:
            continue
        for name in 'UDLR':
            g = fresh()
            apply(g, prefix + path + [name])
            np_ = pos(g)
            if np_ != p and np_ not in tiles:
                tiles[np_] = path + [name]
                q.append((np_, path + [name]))
    return tiles


def main():
    # Walk sequence that latches sw[3] and sw[2] along the way:
    #   from (1,13): U → sw[3] (latch)  then D → (1,13)
    #   D R R R D → sw[2] (latch) then U → (19,19)
    # After this, BFS all tiles.
    latch_prefix = ['U', 'D', 'D', 'R', 'R', 'R', 'D', 'U']

    # Find path to sw[0] from post-latch state
    tiles = bfs_from(latch_prefix)
    path_to_sw0 = tiles.get((55, 25))
    if path_to_sw0 is None:
        print("sw[0] unreachable after latches!")
        return
    print(f"Path to sw[0] after latches: {''.join(path_to_sw0)} ({len(path_to_sw0)} moves)")

    # Walk onto sw[0] and observe
    g = fresh()
    apply(g, latch_prefix + path_to_sw0)
    print(f"\non sw[0]:")
    print(f"  player: {pos(g)}")
    print(f"  doors: {doors(g)}")
    print(f"  sw states: {sw_state(g)}")

    # Step off sw[0]
    g2 = fresh()
    apply(g2, latch_prefix + path_to_sw0 + ['U'])
    print(f"\nafter stepping off sw[0] (U):")
    print(f"  player: {pos(g2)}")
    print(f"  doors: {doors(g2)}")
    print(f"  sw states: {sw_state(g2)}")

    # Does sw[0] latch anything new or open a path?
    print("\n=== BFS after walking onto sw[0] then off ===")
    tiles_after_sw0 = bfs_from(latch_prefix + path_to_sw0 + ['U'])
    new_tiles = set(tiles_after_sw0) - set(tiles)
    print(f"New tiles after sw[0]-touch: {new_tiles}")

    # Also: try holding sw[0] via a live player being stationary (can't move without action)
    # Instead: test ghost on sw[0], see what opens
    # But first: let's see if ANY switch directly affects ulhh reachability.
    # Try: ghost A holds sw[1] (shortest ghost, only DDDRRRD = 7 moves path? actually it's after latches)
    # Path to sw[1] from sw[3]+sw[2] latched state:
    path_to_sw1 = tiles.get((19, 37))
    if path_to_sw1 is None:
        print("\nsw[1] unreachable after latches!")
        return
    print(f"\nPath to sw[1] after latches: {''.join(path_to_sw1)} ({len(path_to_sw1)} moves)")

    # Probe: with sw[1] held (by live player, door[0] shifted), what's new?
    g3 = fresh()
    apply(g3, latch_prefix + path_to_sw1)
    print(f"\non sw[1]:")
    print(f"  doors: {doors(g3)}")


if __name__ == "__main__":
    main()
