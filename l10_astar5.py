"""A* v5: simpler heuristic — reward reg1 near (6, 8), blue at (5, 8) for final bridge."""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
import time, heapq
from l7_sim import load_init
from l7_search import moves


def heuristic(s):
    if len(s.piece_pos) < 12:
        return 0
    pieces = dict(s.piece_pos)
    if pieces.get('reg2') != (6, 9):
        return 100  # reg2 moved, bad
    r1 = pieces.get('reg1')
    if r1 is None:
        return 0
    blue_cells = set(p for pid, p in s.piece_pos if 'blue' in pid)
    # Final goal: reg1 at (6, 8)
    dist_to_68 = max(abs(r1[0] - 6), abs(r1[1] - 8))
    # Bonus if blue at (5, 8) (bridge pivot)
    bridge_ready = 0 if (5, 8) in blue_cells else 3
    # reg1 progression through col 4 or near (6, 8)
    return dist_to_68 + bridge_ready + 1


def astar(cap=20_000_000):
    s0 = load_init('/tmp/l10_init.json')
    pq = [(heuristic(s0), 0, 0, s0)]
    counter = 1
    best_g = {s0.sig(): 0}
    parent = {s0.sig(): (None, None)}
    best_h = heuristic(s0)
    t = time.time()
    last_log = 0
    while pq:
        f, g, _, s = heapq.heappop(pq)
        if len(best_g) > cap:
            break
        if len(s.piece_pos) < 12:
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
            pieces = dict(s.piece_pos)
            print(f'h={h} g={g} r1={pieces.get("reg1")} r2={pieces.get("reg2")} t={time.time()-t:.0f}s seen={len(best_g):,}')
        if len(best_g) - last_log > 1_000_000:
            last_log = len(best_g)
            print(f'  seen={len(best_g):,} best_h={best_h} t={time.time()-t:.0f}s')
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
        with open('/tmp/l10_path5.py', 'w') as f:
            f.write(f'PATH = {path!r}\n')
    else:
        print('no win')
