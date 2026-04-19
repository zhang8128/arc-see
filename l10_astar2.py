"""A* with multi-stage heuristic for L10.

Key insight: for reg+reg consumption, the consumption chain is either:
  (A) reg-A at (4, 9) chain R via reg-B(6, 9) to (8, 9). Target (8, 9)=[hup2+track] (no blue).
  (B) reg-A at (8, 9) chain L via reg-B(6, 9) to (4, 9). Target (4, 9) hup valid.

Both require:
  - One reg reaches (4, 9) or (8, 9).
  - (8, 9) must be len=2 (blue6 moved off V-8,9).
  - reg2 stays at (6, 9).

Heuristic: prefer states where reg1 near (4, 9) AND blue6 far from (8, 9).
"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
import time, heapq
from l7_sim import load_init
from l7_search import moves


def heuristic(s):
    pieces = dict(s.piece_pos)
    # Check win
    if len(s.piece_pos) < 12:
        return 0
    if 'reg1' not in pieces or 'reg2' not in pieces:
        return 0  # one consumed
    r1 = pieces['reg1']
    r2 = pieces['reg2']
    # If reg2 still at (6, 9):
    if r2 != (6, 9):
        return 20  # reg2 moved — bad unless we're close to consumption
    # reg1 should reach (4, 9) or (8, 9)
    # Count (8, 9) blue presence
    blue_at_89 = 0
    for pid, p in s.piece_pos:
        if p == (8, 9) and 'blue' in pid:
            blue_at_89 = 1
            break
    # Distance from reg1 to (4, 9)
    d1 = max(abs(r1[0] - 4), abs(r1[1] - 9))
    # Distance from reg1 to (8, 9)
    d2 = max(abs(r1[0] - 8), abs(r1[1] - 9))
    # Prefer path A (easier): d1 + 0 (target (8,9) needs clear); path B: d2 + blue_at_89 cost
    # Path A cost: move reg1 to (4, 9). Target (8, 9) NEEDS len=2, so blue6 off.
    # But wait target check for chain: source (4, 9) R to (8, 9) with reg2 pivot.
    # Target (8, 9) = currently blue6+V+track = len=3. Need len=2. So blue6 off V.
    # Path A total: d1 + blue_at_89 * 3
    # Path B total: d2 + 3 (since piece on V at (8,9) means reg1 needs to reach there; different)
    hA = (d1 + 1) // 2 + blue_at_89 * 2
    hB = (d2 + 1) // 2 + 3  # harder
    return min(hA, hB) + 1


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
            print(f'h={h} g={g} reg1={pieces.get("reg1")} reg2={pieces.get("reg2")} t={time.time()-t:.0f}s seen={len(best_g):,}')
        if len(best_g) - last_log > 500_000:
            last_log = len(best_g)
            print(f'  seen={len(best_g):,} g={g} best_h={best_h} t={time.time()-t:.0f}s')
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
        with open('/tmp/l10_path.py', 'w') as f:
            f.write(f'PATH = {path!r}\n')
    else:
        print('no win')
