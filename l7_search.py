"""BFS from L7 init for foz_count == 2.

Moves per state:
  - 4 A-actions (one per direction), each moving all vehicles + co-loc pieces.
  - For each live reg/red/blue piece, for each valid chain direction.

Goal: any state where foz_count == 2 (one reg consumed).
Cap: max_depth moves.
"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')

import time
from collections import deque

from l7_sim import load_init, Sim, DIRS

U, D, L, R = (0, -1), (0, 1), (-1, 0), (1, 0)
DIR_NAME = {U: 'U', D: 'D', L: 'L', R: 'R'}


def moves(s: Sim):
    """Yield (label, next_state)."""
    # A-actions
    for d in DIRS:
        ns = s.do_action(d)
        if ns.sig() != s.sig():
            yield (('A', d), ns)
    # Chains
    for pid in s.pieces:
        for d in s.chain_options(pid):
            yield (('C', pid, d), s.do_chain(pid, d))


def bfs(max_states=2_000_000, verbose=True):
    s0 = load_init()
    frontier = deque([s0])
    seen = {s0.sig(): (None, None, 0)}  # sig → (prev_sig, last_move, depth)
    start = time.time()
    iterations = 0
    best_min_dist = 999
    while frontier:
        s = frontier.popleft()
        iterations += 1
        if s.foz_count() < 3:
            # WIN!
            return reconstruct(s, seen), seen
        if iterations % 10000 == 0 and verbose:
            elapsed = time.time() - start
            print(f'  {iterations} expanded, {len(seen)} seen, {len(frontier)} frontier, {elapsed:.1f}s')
        if len(seen) > max_states:
            print(f'Stopped: hit max_states={max_states}')
            break
        for mv, ns in moves(s):
            if ns.sig() not in seen:
                seen[ns.sig()] = (s.sig(), mv, seen[s.sig()][2] + 1)
                frontier.append(ns)
    return None, seen


def reconstruct(end_state: Sim, seen):
    moves_list = []
    sig = end_state.sig()
    while seen[sig][0] is not None:
        prev_sig, mv, _ = seen[sig]
        moves_list.append(mv)
        sig = prev_sig
    return list(reversed(moves_list))


def main():
    print('BFS from L7 init for foz_count < 3 ...')
    path, seen = bfs(max_states=3_000_000)
    if path:
        print(f'FOUND in {len(path)} moves')
        for i, m in enumerate(path):
            print(f'  {i}: {m}')
    else:
        print(f'No win found within {len(seen)} states')


if __name__ == '__main__':
    main()
