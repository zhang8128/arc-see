"""Test Plan A: Get both reg1 and red loaded, drive to (22,3) and (22,4),
then chain reg1 DOWN through red pivot to (22,5).

Once reg1 at (22,5), then chain reg2 at (22,6) UP through reg1 pivot (consumes reg1) to (22,4).
Target (22,4): must be len==2 hup2 only. Red-loaded vehicle must be moved away.

Alternatively: chain reg1 from (22,3) through red → lands at (22,5). Then chain reg1 from (22,5)
UP through (22,4) pivot (red-carrying vehicle still there?) to (22,3). Etc.

Let's just get reg1 to (22,5) first and see what's next reachable.
"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
from l7_sim import load_init, Sim, DIRS
from l7_search import moves

U, D, L, R = (0, -1), (0, 1), (-1, 0), (1, 0)
A_DIR = {1: U, 2: D, 3: L, 4: R}
DIR_NAME = {U: 'U', D: 'D', L: 'L', R: 'R'}


def find_plan(init_state, goal_fn, max_depth=None, max_states=3_000_000):
    """BFS limited depth."""
    from collections import deque
    frontier = deque([(init_state, [])])
    seen = {init_state.sig(): 0}
    while frontier:
        s, path = frontier.popleft()
        if goal_fn(s):
            return s, path
        if max_depth is not None and len(path) >= max_depth:
            continue
        if len(seen) > max_states:
            return None, []
        for mv, ns in moves(s):
            if ns.sig() not in seen:
                seen[ns.sig()] = len(path) + 1
                frontier.append((ns, path + [mv]))
    return None, []


def describe(s):
    return f'pieces={sorted(s.pieces.items())}, vehicles={s.vehicle_pos}, foz={s.foz_count()}'


if __name__ == '__main__':
    s0 = load_init()
    print('init:', describe(s0))
    print()
    print('=== Goal: any piece at (22,3) via loading ===')
    def goal_22_3(s):
        # any piece co-located with a vehicle at (22,3)
        for pid, p in s.piece_pos:
            if p == (22, 3) and p in s.vehicle_pos:
                return True
        return False
    end, path = find_plan(s0, goal_22_3, max_states=1_500_000)
    if end:
        print(f'REACHED in {len(path)} moves')
        for i, m in enumerate(path):
            print(f'  {i}: {m}')
        print(describe(end))
    else:
        print('no plan found within cap')
