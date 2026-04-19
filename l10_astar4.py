"""A* v4: fixed heuristic for L10.
Win: chain reg2 U via reg1 pivot at (6, 8). So need:
  - reg1 at (6, 8)
  - reg2 at (6, 9)  (unchanged)

Path: reg1 descends col 4 via blue pivots at (4, 1), (4, 3), (4, 5), (4, 7),
then chains R via blue at (5, 8) to (6, 8).

Heuristic stages:
  - reg2 must stay at (6, 9). h += 20 if reg2 not there.
  - reg1 path: (4, 0) → (4, 2) → (4, 4) → (4, 6) → (4, 8) → (6, 8). 5 chain steps.
  - Pivots needed (blues): (4, 1), (4, 3), (4, 5), (4, 7), (5, 8).
"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
import time, heapq
from l7_sim import load_init
from l7_search import moves


PIVOTS_NEEDED = {(4, 1), (4, 3), (4, 5), (4, 7), (5, 8)}
REG1_PATH = [(4, 0), (4, 2), (4, 4), (4, 6), (4, 8), (6, 8)]


def heuristic(s):
    if len(s.piece_pos) < 12:
        return 0
    pieces = dict(s.piece_pos)
    if pieces.get('reg2') != (6, 9):
        return 30  # reg2 must stay
    # Blues at pivot cells
    blue_cells = set(p for pid, p in s.piece_pos if 'blue' in pid)
    missing = PIVOTS_NEEDED - blue_cells
    score = len(missing) * 3
    r1 = pieces.get('reg1')
    if r1 is None:
        return score  # consumed
    # Reg1 path progress: find how far along REG1_PATH
    try:
        idx = REG1_PATH.index(r1)
        score += (len(REG1_PATH) - 1 - idx) * 2
    except ValueError:
        # reg1 off path
        # Distance to (6, 8)
        score += 10 + max(abs(r1[0] - 6), abs(r1[1] - 8))
    return score + 1


def astar(cap=15_000_000):
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
            blue_cells = set(p for pid, p in s.piece_pos if 'blue' in pid)
            have = sorted(blue_cells & PIVOTS_NEEDED)
            print(f'h={h} g={g} r1={pieces.get("reg1")} pivots_have={have} t={time.time()-t:.0f}s seen={len(best_g):,}')
        if len(best_g) - last_log > 500_000:
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
        # Save path
        A_NUM = {(0,-1):1,(0,1):2,(-1,0):3,(1,0):4}
        with open('/tmp/l10_path.py', 'w') as f:
            f.write('# L10 win path\n')
            f.write(f'# {len(path)} moves\n')
            f.write(f'RAW = {path!r}\n')
    else:
        print('no win')
