"""A* on L10 with heuristic = distance between the two regs (for consumption)."""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
import time, heapq
from l7_sim import load_init
from l7_search import moves


def heuristic(s):
    if len(s.piece_pos) < 12:
        return 0
    # Find reg positions
    regs = [p for pid, p in s.piece_pos if 'reg' in pid]
    if len(regs) < 2:
        return 0
    # Distance between regs, divided by 2 (chain moves 2 cells)
    r1, r2 = regs
    return (max(abs(r1[0]-r2[0]), abs(r1[1]-r2[1])) + 1) // 2


def astar(cap=20_000_000):
    s0 = load_init('/tmp/l10_init.json')
    pq = [(heuristic(s0), 0, 0, s0)]
    counter = 1
    best_g = {s0.sig(): 0}
    parent = {s0.sig(): (None, None)}
    best_h = heuristic(s0)
    t = time.time()
    while pq:
        f, g, _, s = heapq.heappop(pq)
        if len(best_g) > cap:
            break
        if len(s.piece_pos) < 12:
            # win — reconstruct path
            path = []
            sig = s.sig()
            while parent[sig][0] is not None:
                prev, mv = parent[sig]
                path.append(mv)
                sig = prev
            return s, list(reversed(path))
        h = heuristic(s)
        if h < best_h:
            best_h = h
            regs = [p for pid, p in s.piece_pos if 'reg' in pid]
            print(f'h={h} g={g} regs={regs} t={time.time()-t:.0f}s seen={len(best_g):,}')
        for mv, ns in moves(s):
            ng = g + 1
            nsig = ns.sig()
            if nsig not in best_g or ng < best_g[nsig]:
                best_g[nsig] = ng
                parent[nsig] = (s.sig(), mv)
                heapq.heappush(pq, (ng + heuristic(ns), ng, counter, ns))
                counter += 1
    return None, None


if __name__ == '__main__':
    got, path = astar()
    if got:
        print(f'WIN in {len(path)} moves')
    else:
        print('no win')
