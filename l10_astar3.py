"""A* v3: heuristic incorporates blue-pivot positioning for col-4 ladder."""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
import time, heapq
from l7_sim import load_init
from l7_search import moves


PIVOTS_NEEDED = {(4, 1), (4, 3), (4, 5), (4, 7)}


def heuristic(s):
    if len(s.piece_pos) < 12:
        return 0
    # Count pivots set up for col-4 ladder (ONLY blues, not regs)
    blue_cells = set(p for pid, p in s.piece_pos if 'blue' in pid)
    missing_pivots = PIVOTS_NEEDED - blue_cells
    score = len(missing_pivots) * 2
    r1 = s.pieces.get('reg1')
    if r1 is None:
        return score
    # Reward reg1 at even-row cells in col 4 (progressing down ladder)
    # reg1 at (4, 0) = start, (4, 8) = nearly done
    if r1[0] == 4 and r1[1] % 2 == 0:
        score += max(0, 8 - r1[1])
    else:
        # Penalize if off the ladder
        score += 10 + max(abs(r1[0] - 4), abs(r1[1] - 8))
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
            foz_cells = set(p for pid, p in s.piece_pos)
            pivots_have = foz_cells & PIVOTS_NEEDED
            print(f'h={h} g={g} r1={pieces.get("reg1")} r2={pieces.get("reg2")} pivots={sorted(pivots_have)} t={time.time()-t:.0f}s seen={len(best_g):,}')
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
        with open('/tmp/l10_path.py', 'w') as f:
            f.write(f'PATH = {path!r}\n')
    else:
        print('no win')
