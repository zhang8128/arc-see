"""G50T L2: ghost-aware BFS.

Strategy:
  Phase A: record a ghost that ends standing on switch[1]=(37,25).
           Path is LL (2 moves). After ACTION5, ghost replays L,L; after its
           2 moves are exhausted it stays on (37,25) holding door[1] open.
  Phase B: from the ACTION5 state, BFS (via engine replay) to find all tiles
           reachable by the live player while the ghost holds switch[1].

We look for:
  - Is switch[0]=(13,37) now reachable?
  - Is the goal (25,19) reachable?
  - What new tiles opened up?
"""
import importlib.util
from collections import deque
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'g50t', 'environment_files/g50t/5849a774/g50t.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

ACTIONS = {
    'U': 'ACTION1',
    'D': 'ACTION2',
    'L': 'ACTION3',
    'R': 'ACTION4',
}
A5 = 'ACTION5'


def fresh():
    g = mod.G50t()
    g.set_level(1)
    return g


def do(g, name):
    g.perform_action(ActionInput(id=getattr(GameAction, name if name.startswith('ACTION') else ACTIONS[name])))


def pos(g):
    p = g.vgwycxsxjz.dzxunlkwxt
    return (p.x, p.y)


def ghost_positions(g):
    eng = g.vgwycxsxjz
    gs = getattr(eng, 'rloltuowth', {})
    if isinstance(gs, dict):
        return [(gk.x, gk.y) for gk in gs]
    return []


def door_states(g):
    return tuple((d.x, d.y) for d in g.vgwycxsxjz.uwxkstolmf)


def setup_phase_a():
    """Build the 'ghost holds switch[1]' start state. Returns the sequence used."""
    return ['L', 'L', 'ACTION5']


def apply(g, seq):
    for a in seq:
        do(g, a)


def bfs_with_ghost(prefix, max_depth=40):
    """BFS live-player movements from the end of `prefix`.
    State key = (player_pos, door_positions, ghost_positions_tuple).
    """
    # Validate the prefix produces a ghost on the switch
    g = fresh()
    apply(g, prefix)
    print(f"Phase A setup: player at {pos(g)}, ghosts at {ghost_positions(g)}, doors at {door_states(g)}")

    reach = {}  # (player_pos, doors, ghosts) -> move sequence
    start_key = (pos(g), door_states(g), tuple(ghost_positions(g)))
    reach[start_key] = []
    q = deque([(start_key, [])])
    tile_to_best = {pos(g): []}

    while q:
        key, path = q.popleft()
        if len(path) >= max_depth:
            continue
        for name in 'UDLR':
            g = fresh()
            apply(g, prefix + path + [name])
            new_player = pos(g)
            new_doors = door_states(g)
            new_ghosts = tuple(ghost_positions(g))
            new_key = (new_player, new_doors, new_ghosts)
            if new_key in reach:
                continue
            reach[new_key] = path + [name]
            q.append((new_key, path + [name]))
            if new_player not in tile_to_best or len(path + [name]) < len(tile_to_best[new_player]):
                tile_to_best[new_player] = path + [name]

    return reach, tile_to_best


def main():
    prefix = setup_phase_a()
    reach, tiles = bfs_with_ghost(prefix, max_depth=30)

    print(f"\nReached {len(reach)} distinct states, {len(tiles)} distinct tiles.")
    print("\nAll tiles reachable with ghost holding switch[1]:")
    for p in sorted(tiles, key=lambda t: (t[1], t[0])):
        marker = ""
        if p == (25, 19):
            marker = "  <-- WIN"
        elif p == (13, 37):
            marker = "  <-- switch[0]"
        elif p == (37, 25):
            marker = "  <-- switch[1]"
        print(f"  {p}  via {''.join(tiles[p])}{marker}")

    # Compare to no-ghost reach
    from_start_tiles = {
        (7, 7), (13, 7), (19, 7), (25, 7), (31, 7), (37, 7), (43, 7), (49, 7),
        (7, 13), (37, 13), (49, 13),
        (7, 19), (37, 19), (49, 19),
        (37, 25), (43, 25), (49, 25),
        (49, 31), (49, 37), (49, 43),
        (43, 49), (49, 49),
    }
    new_tiles = set(tiles) - from_start_tiles
    print(f"\nNewly opened tiles (not reachable without ghost): {len(new_tiles)}")
    for p in sorted(new_tiles, key=lambda t: (t[1], t[0])):
        print(f"  {p}  via {''.join(tiles[p])}")


if __name__ == "__main__":
    main()
