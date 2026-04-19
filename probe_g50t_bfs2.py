"""G50T L1 BFS v2 — rich key that includes all mutable entity positions/flags.

Key findings from probe_g50t_interact.py:
- ACTION5 = reset (player -> start, rlazdofsxb++). SKIP in BFS.
- Stepping on (37,7) triggers uwxkstolmf[0] to slide and hamayflsib[0].dijhfchobv to flip.
- Base-layer pixels don't update; must use engine attrs as state key.
"""
import copy
import importlib.util
from collections import deque
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'g50t', 'environment_files/g50t/5849a774/g50t.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

ACTIONS = ['ACTION1', 'ACTION2', 'ACTION3', 'ACTION4', 'ACTION5']  # all actions


def state_key(g):
    eng = g.vgwycxsxjz
    p = eng.dzxunlkwxt
    # Player position + orientation + any transient flags
    player_key = (p.x, p.y, p.amjlzzsesf, p.pddqxjztas, p.qxtpxrcvcd)
    ham = tuple((e.x, e.y, e.dijhfchobv) for e in eng.hamayflsib)
    uwx = tuple((e.x, e.y, e.dijhfchobv) for e in eng.uwxkstolmf)
    zmq = (eng.zmqoxwsfgh.x, eng.zmqoxwsfgh.y)
    # rlazdofsxb cycles through drofvwhbxb length
    rlaz = eng.rlazdofsxb
    # Include move history LENGTH (not content) as a proxy for undo state
    hist_len = len(eng.areahjypvy)
    return (player_key, ham, uwx, zmq, rlaz, hist_len)


def is_won(g, level_idx):
    return g._state.name == "WIN" or g._current_level_index > level_idx


def player_pos(g):
    p = g.vgwycxsxjz.dzxunlkwxt
    return (p.x, p.y)


def bfs(level_idx=0, max_expanded=50000):
    g = mod.G50t()
    g.set_level(level_idx)
    start = state_key(g)
    print(f"L{level_idx+1} start player: {player_pos(g)}")

    seen = {start: []}
    queue = deque([(g, [])])
    expanded = 0
    positions = {player_pos(g)}

    while queue and expanded < max_expanded:
        g, path = queue.popleft()
        expanded += 1
        for a in ACTIONS:
            g2 = copy.deepcopy(g)
            try:
                g2.perform_action(ActionInput(id=getattr(GameAction, a)))
            except Exception as e:
                print(f"  action err {a}: {e}")
                continue
            k = state_key(g2)
            if k in seen:
                continue
            seen[k] = path + [a]
            positions.add(player_pos(g2))

            if is_won(g2, level_idx):
                print(f"  WIN @ depth {len(path)+1}")
                print(f"  path: {path + [a]}")
                print(f"  compressed: {compress(path + [a])}")
                return path + [a]
            queue.append((g2, path + [a]))

        if expanded % 500 == 0:
            print(f"  exp={expanded} frontier={len(queue)} seen={len(seen)} positions={len(positions)}")

    print(f"\nBFS done: expanded={expanded} seen={len(seen)}")
    print(f"Distinct player positions: {len(positions)}")
    print(f"  positions: {sorted(positions)}")
    return None


def compress(path):
    """Run-length encode a path."""
    if not path:
        return ""
    out = []
    run = [path[0], 1]
    for a in path[1:]:
        if a == run[0]:
            run[1] += 1
        else:
            out.append(run)
            run = [a, 1]
    out.append(run)
    names = {'ACTION1': 'U', 'ACTION2': 'D', 'ACTION3': 'L', 'ACTION4': 'R', 'ACTION5': '5'}
    return ' '.join(f"{n}×{names.get(a, a)}" for a, n in out)


if __name__ == "__main__":
    bfs(level_idx=0, max_expanded=200000)
