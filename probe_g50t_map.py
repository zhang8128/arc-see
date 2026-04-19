"""G50T: map L1's reachable positions and find hidden state that BFS is missing."""
import copy
import importlib.util
from collections import deque
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'g50t', 'environment_files/g50t/5849a774/g50t.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

ACTIONS = ['ACTION1', 'ACTION2', 'ACTION3', 'ACTION4', 'ACTION5']


def player(g):
    return g.vgwycxsxjz.dzxunlkwxt


def bool_tuple(g):
    """Collect all booleans in the internal engine."""
    eng = g.vgwycxsxjz
    return tuple(
        getattr(eng, n) for n in
        ('dofntsemri', 'jqpwhiraaj', 'jvtgoshrhq', 'pohkooyzds', 'safkknjslo', 'zvuxrhnlcb')
    )


def entity_list_lens(g):
    """Lengths of the three entity lists (not contents, just sizes for now)."""
    eng = g.vgwycxsxjz
    return tuple(
        len(getattr(eng, n, []))
        for n in ('drofvwhbxb', 'hamayflsib', 'uwxkstolmf')
    )


def entity_ref_pos(g, name):
    """(x, y) of a named entity ref if it has them."""
    eng = g.vgwycxsxjz
    ent = getattr(eng, name, None)
    if ent is None:
        return None
    x = getattr(ent, 'x', None)
    y = getattr(ent, 'y', None)
    return (x, y)


def rich_state_key(g):
    p = player(g)
    return (
        (p.x, p.y),
        bool_tuple(g),
        entity_list_lens(g),
        entity_ref_pos(g, 'whftgckbcu'),
        entity_ref_pos(g, 'afbbgvkpip'),
        entity_ref_pos(g, 'zmqoxwsfgh'),
        # yugzlzepkr looks like a mutable counter; include it
        getattr(g.vgwycxsxjz, 'yugzlzepkr', 0),
        getattr(g.vgwycxsxjz, 'rlazdofsxb', 0),
    )


def is_won(g, level_idx):
    return g._state.name == "WIN" or g._current_level_index > level_idx


def explore_l1():
    g = mod.G50t()
    g.set_level(0)
    print(f"start pos: ({player(g).x}, {player(g).y})")
    print(f"start rich key: {rich_state_key(g)}")
    # Other single-refs
    eng = g.vgwycxsxjz
    for name in ('whftgckbcu', 'afbbgvkpip', 'dzxunlkwxt', 'zmqoxwsfgh'):
        ent = getattr(eng, name, None)
        if ent is None:
            continue
        print(f"  entity {name}: x={getattr(ent, 'x', '?')} y={getattr(ent, 'y', '?')} "
              f"type={type(ent).__name__}")
    print(f"  list drofvwhbxb: len={len(getattr(eng, 'drofvwhbxb', []))}")
    print(f"  list hamayflsib: len={len(getattr(eng, 'hamayflsib', []))}")
    print(f"  list uwxkstolmf: len={len(getattr(eng, 'uwxkstolmf', []))}")

    # BFS with rich key, track all reachable positions
    seen = {rich_state_key(g): ([], copy.deepcopy(g))}
    positions = set()
    positions.add((player(g).x, player(g).y))
    queue = deque([(g, [])])
    wins = []
    expanded = 0

    while queue and expanded < 50000:
        g, path = queue.popleft()
        expanded += 1
        for a in ACTIONS:
            g2 = copy.deepcopy(g)
            try:
                g2.perform_action(ActionInput(id=getattr(GameAction, a)))
            except Exception:
                continue
            k = rich_state_key(g2)
            if k in seen:
                continue
            seen[k] = (path + [a], g2)
            positions.add((player(g2).x, player(g2).y))
            if is_won(g2, 0):
                wins.append((path + [a], g2))
                print(f"  WIN @ depth {len(path)+1} via {path[-3:] + [a]}")
                return path + [a]
            queue.append((g2, path + [a]))

    print(f"\nBFS exhausted: expanded={expanded} seen={len(seen)} distinct_positions={len(positions)}")
    print(f"\nReachable player positions ({len(positions)}):")
    for pos in sorted(positions):
        print(f"  {pos}")

    # Look at one of the "deepest" states to see what changed
    print("\nSample states from BFS:")
    for k, (path, g2) in list(seen.items())[:3]:
        print(f"  path={path} key={k}")
    return None


if __name__ == "__main__":
    explore_l1()
