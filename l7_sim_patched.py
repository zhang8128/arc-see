"""Patched L7 sim: add an artificial DGX in M-component to test whether
having one would make L7 solvable.

If BFS on the patched sim finds a win, that PROVES the original puzzle
is unsolvable without an M-DGX (i.e., structural blocker confirmed).
If even the patched version is unsolvable, something more fundamental
is wrong with my model.

Adds a static DGX at (10, 7) in M-component.
"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
from dataclasses import replace
from l7_sim import load_init


def load_init_patched():
    s = load_init()
    # Add DGX at (10, 7). In my model DGX positions are in s.dgx_pos.
    # (10, 7) is a track cell (kraubslpehi->). Adding DGX there.
    new_dgx = tuple(sorted(list(s.dgx_pos) + [(10, 7)]))
    return replace(s, dgx_pos=new_dgx)


if __name__ == '__main__':
    from l7_search import moves
    from collections import deque
    import time

    s0 = load_init_patched()
    print(f'Patched init: dgx count={len(s0.dgx_pos)}, includes (10,7): {(10,7) in s0.dgx_pos}')
    print(f'pieces: {s0.pieces}')

    # BFS for win
    frontier = deque([s0])
    seen = {s0.sig()}
    t0 = time.time()
    last_depth_report = 0
    depth_map = {s0.sig(): 0}
    cap = 5_000_000
    found = None
    while frontier and len(seen) < cap:
        s = frontier.popleft()
        d = depth_map[s.sig()]
        if s.foz_count() < 3:
            found = (s, d)
            break
        if d > last_depth_report:
            last_depth_report = d
            print(f'd={d} seen={len(seen):,} t={time.time()-t0:.0f}s')
        for mv, ns in moves(s):
            if ns.sig() not in seen:
                seen.add(ns.sig())
                depth_map[ns.sig()] = d + 1
                frontier.append(ns)
    if found:
        print(f'WIN at depth {found[1]}! pieces={found[0].pieces}')
    else:
        print(f'no win in {len(seen):,} states')
