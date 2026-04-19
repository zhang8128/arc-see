"""Attempt a full win plan from chain-9.

Strategy (from analysis):
  A. Move reg1 east to (14, 2) or (14, 3), with red at the complementary cell.
     Bridge plan: swap reg1 and red through col 14's hup ladder to reach col 16+.
  B. Get reg1 loaded on a non-DGX vehicle that reaches (22, 3).
  C. Drive a DGX-carrying vehicle to (22, 4).
  D. Chain reg1 (22, 3) DOWN via DGX pivot (22, 4) to (22, 5). reg1 now at (22, 5).
  E. Re-arrange vehicles so (22, 4) has a vehicle but NO DGX.
  F. Chain reg2 (22, 6) UP via reg1 pivot (22, 5) to (22, 4). Reg1 consumed. WIN.

The challenge is step E - decoupling DGX from vehicle at (22, 4). Approach:
drag the DGX-vehicle AWAY from (22, 4), then park a different (non-DGX)
vehicle there.

Because all vehicles move simultaneously per A-action, we need careful
ordering. Let's try to express the plan and see where it breaks.
"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
from dataclasses import replace

from l7_sim import load_init, Sim
from l7_search_deep import at_chain9

U, D, L, R = (0, -1), (0, 1), (-1, 0), (1, 0)
A_DIR = {1: U, 2: D, 3: L, 4: R}
DN = {U: 'U', D: 'D', L: 'L', R: 'R'}


def describe(s):
    print(f'  pieces: {s.pieces}')
    print(f'  vehicles: {s.vehicle_pos}')
    mobile_dgx = set(s.dgx_pos) & set(s.vehicle_pos)
    print(f'  mobile DGX (co-loc vehicle): {sorted(mobile_dgx)}')
    print(f'  foz count: {s.foz_count()}')


def apply(s, op):
    kind = op[0]
    if kind == 'A':
        for a in op[1]:
            s = s.do_action(A_DIR[a])
    elif kind == 'C':
        pid, d = op[1], op[2]
        if pid not in s.pieces:
            print(f'  FAIL: piece {pid} missing')
            return s, False
        opts = s.chain_options(pid)
        if d not in opts:
            print(f'  FAIL: chain {pid} {DN[d]} invalid. opts={[DN[x] for x in opts]}, piece@{s.pieces[pid]}')
            return s, False
        s = s.do_chain(pid, d)
    return s, True


if __name__ == '__main__':
    s = at_chain9()
    print('=== Starting at chain-9 ===')
    describe(s)

    # Try some simple chains to see what's reachable from (9, 8)
    # reg1 (9, 8) R → (11, 8) via red (10, 8) pivot
    print()
    print('Chain reg1 R from (9,8)')
    s, ok = apply(s, ('C', 'reg1', R))
    if not ok:
        sys.exit()
    describe(s)

    # reg1 at (11, 8). Now try chains from here.
    print()
    print('reg1 options from (11, 8):')
    opts = [DN[x] for x in s.chain_options('reg1')]
    print(f'  {opts}')
    # Likely UP via DGX(11, 7) if target (11, 6) has vehicle.

    # Let's check each direction's pivot and target
    for d in [U, D, L, R]:
        src = s.pieces['reg1']
        piv = (src[0]+d[0], src[1]+d[1])
        tgt = (src[0]+2*d[0], src[1]+2*d[1])
        print(f'  {DN[d]}: pivot {piv}={s.cell_sprites(piv)}, target {tgt}={s.cell_sprites(tgt)}')
