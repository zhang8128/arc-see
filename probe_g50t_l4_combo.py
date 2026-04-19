"""G50T L4: test various simultaneous states.

Tests:
  1. Ghost A on sw[0], ghost B on sw[1] — what's reachable?
  2. Ghost A on sw[1], ghost B on ulhh[2] — what's reachable?
  3. Ghost A on sw[1], live player on ulhh[2] + more ghost — ulhh[3] reachable?
  4. Does ghost A on switch[0] do ANYTHING (change any entity state)?

Also: brute-force try reaching ulhh[3] from the ghost-sw[1] state by trying
much longer BFS depths with more actions.
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


def ulhh(g):
    return tuple((len(h.rqxibulywa), len(h.vbqvjbxkfm), h.is_visible, h.x, h.y)
                 for h in g.vgwycxsxjz.hamayflsib
                 if type(h).__name__ == 'ulhhdeoyok')


def is_win(g):
    return g._state.name == "WIN" or g._current_level_index > 3


def bfs(prefix, max_depth=25):
    """BFS from post-prefix state. Returns (tiles_reached, win_seq)."""
    g0 = fresh()
    apply(g0, prefix)
    start_key = (pos(g0), doors(g0), ulhh(g0))
    seen = {start_key: []}
    q = deque([(start_key, [])])
    tiles = {pos(g0): []}
    win = None
    while q:
        (p, d, u), path = q.popleft()
        if win or len(path) >= max_depth:
            continue
        for name in 'UDLR':
            g = fresh()
            apply(g, prefix + path + [name])
            if is_win(g):
                win = prefix + path + [name]
                break
            new_p = pos(g)
            new_d = doors(g)
            new_u = ulhh(g)
            new_key = (new_p, new_d, new_u)
            if new_key in seen:
                continue
            seen[new_key] = path + [name]
            q.append((new_key, path + [name]))
            if new_p not in tiles:
                tiles[new_p] = path + [name]
        if win:
            break
    return tiles, win


def test(label, prefix):
    print(f"\n=== {label} ===")
    g = fresh()
    apply(g, prefix)
    print(f"  prefix len: {len(prefix)}")
    print(f"  post-prefix: player={pos(g)} doors={doors(g)} ulhh={ulhh(g)}")
    print(f"  ghosts: {[(k.x, k.y) for k in g.vgwycxsxjz.rloltuowth]}")
    tiles, win = bfs(prefix, max_depth=25)
    print(f"  reach: {len(tiles)} tiles")
    if win:
        print(f"  WIN in {len(win)} actions!")
        to_letter = {'U': 'U', 'D': 'D', 'L': 'L', 'R': 'R', 'ACTION5': '!'}
        print(f"  seq: {''.join(to_letter.get(a, '?') for a in win)}")
        print(f"  list: {win}")
        # Tile list in sorted order
        print(f"  tiles in reach: {sorted(tiles.keys(), key=lambda p: (p[1], p[0]))}")
    else:
        key = {(7,49):"WIN",(25,49):"ulhh[3]",(25,37):"ulhh[2]"}
        reached = [t for t in key if t in tiles]
        print(f"  key tiles reached: {reached}")


def main():
    # Plan A: 2 ghosts. Walk to sw[0] (11 moves) + ACTION5 + walk to sw[1] (?) + ACTION5
    # We need to walk from (25,7) to sw[1]=(31,25) after first ACTION5.
    # But during the first ACTION5 walk to sw[0], ghost A's path is 11 moves.
    # After ACTION5, ghost A replays from spawn. Second walk to sw[1] uses paths.
    # From (25,7) initial, path to sw[1] = DDRD (4 moves).
    # Ghost A replays 4 moves of its 11-move path (first 4 = DDRR → (37, 19)).
    # So ghost A at (37,19) not on sw[0]. Second ACTION5: ghost B saved (4 moves).
    # Third walk: 11 live moves so ghost A finishes. Ghost B finishes at move 4.
    # At move 11: ghost A on sw[0], ghost B on sw[1].
    # Neither switch position matters if switch[0] is a decoy...
    #
    # But let's test.
    prefix_a = (
        list('DDRRUURRDDD') + ['ACTION5']   # 12: walk to sw[0], save ghost A
        + list('DDRD') + ['ACTION5']         # 5: walk to sw[1], save ghost B
    )
    test("Ghost A → sw[0], Ghost B → sw[1] (after both finish replaying)", prefix_a)

    # Plan B: skip sw[0] entirely. Just hold sw[1] and try to reach (7,49).
    prefix_b = list('DDRD') + ['ACTION5']
    test("Ghost A → sw[1] only", prefix_b)

    # Plan C: ghost A holds sw[1]. Live player goes to ulhh[2]. Then deeper BFS.
    # Already explored. Try deeper.
    prefix_c = list('DDRD') + ['ACTION5'] + list('LLLD') + list('DDDD') + list('RRR')
    test("Post-ulhh[2] state", prefix_c)


if __name__ == "__main__":
    main()
