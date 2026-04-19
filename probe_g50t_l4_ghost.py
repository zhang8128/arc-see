"""G50T L4: ghost-aware BFS + inspection.

Test 1: with ghost A holding switch[0], what's reachable?
Test 2: with ghost A holding switch[1], what's reachable?
Test 3: what happens when the live player reaches ulhh[2] or ulhh[3]?
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


def doors(g):
    return tuple((d.x, d.y) for d in g.vgwycxsxjz.uwxkstolmf)


def is_win(g):
    return g._state.name == "WIN" or g._current_level_index > 3


def bfs_from_prefix(prefix, max_depth=30):
    """BFS live-player moves after prefix. State key = (player_pos, doors)."""
    g0 = fresh()
    apply(g0, prefix)
    start = pos(g0)
    start_key = (start, doors(g0))
    seen = {start_key: []}
    tile_paths = {start: []}
    q = deque([(start_key, [])])
    found_win = None
    while q:
        (p, d), path = q.popleft()
        if len(path) >= max_depth:
            continue
        for name in 'UDLR':
            g = fresh()
            apply(g, prefix + path + [name])
            if is_win(g):
                if found_win is None:
                    found_win = prefix + path + [name]
                    print(f"  !!! WIN at {len(found_win)} actions")
                continue
            new_p = pos(g)
            new_d = doors(g)
            new_key = (new_p, new_d)
            if new_key in seen:
                continue
            seen[new_key] = path + [name]
            q.append((new_key, path + [name]))
            if new_p not in tile_paths or len(path + [name]) < len(tile_paths[new_p]):
                tile_paths[new_p] = path + [name]
    return tile_paths, found_win


def test(label, prefix, max_depth=20):
    print(f"\n=== {label} ({len(prefix)} prefix actions) ===")
    g = fresh()
    apply(g, prefix)
    print(f"  post-prefix player: {pos(g)}")
    print(f"  doors: {doors(g)}")
    print(f"  ghosts: {[(k.x, k.y) for k in g.vgwycxsxjz.rloltuowth]}")
    tiles, win = bfs_from_prefix(prefix, max_depth=max_depth)
    print(f"  reachable tiles: {len(tiles)}")
    # Print tiles sorted
    for t in sorted(tiles, key=lambda p: (p[1], p[0])):
        marker = ""
        if t == (7, 49): marker = "  <-- WIN"
        elif t == (25, 37): marker = "  <-- ulhh[2]"
        elif t == (25, 49): marker = "  <-- ulhh[3]"
        elif t == (31, 25): marker = "  <-- switch[1]"
        elif t == (49, 25): marker = "  <-- switch[0]"
        print(f"    {t}{marker}")
    if win:
        print(f"  WIN SEQ: {len(win)} actions")


def main():
    # Ghost A holds switch[0]. Path: DDRRUURRDDD (11 moves).
    prefix_sw0_ghost = list('DDRRUURRDDD') + ['ACTION5']
    test("Ghost A holds switch[0]", prefix_sw0_ghost)

    # Ghost A holds switch[1]. Path: DDRD (4 moves).
    prefix_sw1_ghost = list('DDRD') + ['ACTION5']
    test("Ghost A holds switch[1]", prefix_sw1_ghost)


if __name__ == "__main__":
    main()
