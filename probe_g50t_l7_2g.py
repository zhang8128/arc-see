"""G50T L7: 2-ghost setup — ghost A on sw[3], ghost B on sw[1].

Phase A: walk DDLRUULLUU (10 moves, via teleport to sw[3]) + ACTION5
Phase B: walk to sw[1] (49,1). Need path with ghost A replaying the 10-move
         path concurrently. Find this path first by BFS.
Phase C: + ACTION5
Phase D: live player walks to goal.
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
    g.set_level(6)
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
    return tuple((d.x, d.y, bool(d.dijhfchobv)) for d in g.vgwycxsxjz.uwxkstolmf)


def is_win(g):
    return g._state.name == "WIN" or g._current_level_index > 6


SW3_GHOST = list('DDLRUULLUU')


def find_path(prefix, target, max_ghost_len, max_depth=30):
    """BFS for shortest live-player path to target tile after prefix."""
    g0 = fresh()
    apply(g0, prefix)
    start = (pos(g0), doors(g0), 0)
    seen = {start: []}
    q = deque([(start, [])])
    while q:
        (p, d, _), path = q.popleft()
        if p == target:
            return path
        if len(path) >= max_depth:
            continue
        for name in 'UDLR':
            g = fresh()
            apply(g, prefix + path + [name])
            new_p = pos(g)
            new_d = doors(g)
            new_mc = min(len(path) + 1, max_ghost_len)
            new_key = (new_p, new_d, new_mc)
            if new_key in seen:
                continue
            seen[new_key] = path + [name]
            q.append((new_key, path + [name]))
    return None


def main():
    # Phase A: walk to sw[3] + ACTION5
    prefix_a = SW3_GHOST + ['ACTION5']
    print(f"Phase A: {len(prefix_a)} actions")

    # Phase B: find path to sw[1] = (49, 1) post-phase-A
    path_b = find_path(prefix_a, (49, 1), max_ghost_len=len(SW3_GHOST))
    if path_b is None:
        print("sw[1] unreachable from phase A")
        return
    print(f"Phase B path: {''.join(path_b)} ({len(path_b)} moves)")

    # Phase C: ACTION5 to save ghost B
    prefix_ac = prefix_a + path_b + ['ACTION5']
    print(f"After phase A+B+ACTION5: {len(prefix_ac)} actions")

    g = fresh()
    apply(g, prefix_ac)
    print(f"  player: {pos(g)}")
    print(f"  doors: {doors(g)}")
    print(f"  ghost count: {len(g.vgwycxsxjz.rloltuowth)}")

    # Phase D: BFS for WIN
    max_ghost = max(len(SW3_GHOST), len(path_b))
    start = (pos(g), doors(g), 0)
    seen = {start: []}
    q = deque([(start, [])])
    best = None
    while q:
        (p, d, _), path = q.popleft()
        if best and len(path) >= len(best):
            continue
        if len(path) > 50:
            continue
        for name in 'UDLR':
            g2 = fresh()
            apply(g2, prefix_ac + path + [name])
            if is_win(g2):
                full = prefix_ac + path + [name]
                if not best or len(full) < len(best):
                    best = full
                    print(f"  WIN at {len(full)}")
                break
            new_p = pos(g2)
            new_d = doors(g2)
            new_mc = min(len(path) + 1, max_ghost)
            new_key = (new_p, new_d, new_mc)
            if new_key in seen:
                continue
            seen[new_key] = path + [name]
            q.append((new_key, path + [name]))

    if best:
        to_letter = {'U': 'U', 'D': 'D', 'L': 'L', 'R': 'R', 'ACTION5': '!'}
        print(f"\nSOLUTION: {len(best)} vs baseline 67 ({100*len(best)/67:.1f}%)")
        print(''.join(to_letter.get(a, '?') for a in best))
    else:
        print(f"\nNo win in phase D")


if __name__ == "__main__":
    main()
