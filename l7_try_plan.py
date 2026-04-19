"""Try a specific plan to get reg1 loaded on V-M:
  1. From chain-9, chain reg1 L back to (9, 8). (reg1 at 9,8, red+V at 10,8)
  2. chain red L to (8, 8). (red at 8,8, V-M at 10,8 empty)
  3. Drive V-M (empty) to (11, 6) via M-component.
  4. chain reg1 UP from (11, 8)? Wait reg1 is at (9, 8) now.
     We need reg1 at (11, 8). Re-chain?
  Actually we need to re-chain reg1 R from (9, 8) to (11, 8) first — but that needs red at (10, 8) pivot. Red moved.
  So the trick: move V-M AFTER reg1 is at (11, 8) but red is gone.

  Alt plan:
  1. chain-9 state already has reg1 at (11, 8), red at (10, 8) V.
  2. chain red L (10, 8) → (8, 8) — uses reg1(9, 8) pivot. But reg1 at (11, 8) not (9, 8). INVALID.

  Hmm. At chain-9, reg1 is at (11, 8). Red chain L (10, 8) L: pivot = (9, 8). (9, 8) hup only
  (reg1 moved to (11, 8) after chain 9). Invalid pivot.

  So we need reg1 at (9, 8) for red L.
"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
from l7_sim import load_init
from l7_search_deep import at_chain9

U, D, L, R = (0, -1), (0, 1), (-1, 0), (1, 0)
A_DIR = {1: U, 2: D, 3: L, 4: R}
DN = {U:'U',D:'D',L:'L',R:'R'}


def show(s, lbl):
    print(f'[{lbl}] pieces={s.pieces}, vehicles={s.vehicle_pos[:]}')


def apply(s, ops, lbl_prefix=''):
    for i, op in enumerate(ops):
        lbl = f'{lbl_prefix}{i}'
        if op[0] == 'A':
            d = A_DIR[op[1]]
            ns = s.do_action(d)
            if ns.sig() == s.sig():
                print(f'  {lbl}: A{op[1]} NO CHANGE')
            s = ns
        else:
            pid, d = op[1], op[2]
            opts = s.chain_options(pid)
            if d not in opts:
                print(f'  {lbl}: FAIL chain {pid} {DN[d]}. opts={[DN[x] for x in opts]}')
                return s, False
            s = s.do_chain(pid, d)
            print(f'  {lbl}: chain {pid} {DN[d]} → {s.pieces[pid] if pid in s.pieces else "consumed"}')
    return s, True


if __name__ == '__main__':
    s = at_chain9()
    show(s, 'chain-9')

    # Step 1: reg1 L back to (9, 8) via red pivot
    s, ok = apply(s, [('C', 'reg1', L)], 'rev_')
    show(s, 'after reg1 L')

    # Step 2: red L (10, 8) → (8, 8) via reg1(9, 8) pivot
    s, ok = apply(s, [('C', 'red', L)], 'redL_')
    show(s, 'after red L')
    # State: reg1 (9, 8), red (8, 8), V-M (10, 8) empty

    # Step 3: Drive V-M from (10, 8) to (11, 6)
    drive = [1, 3, 3, 1, 1, 4, 4, 4, 2]  # up left left up up right right right down
    # (10,8)→(10,7)→(9,7)→(8,7)→(8,6)→(8,5)→(9,5)→(10,5)→(11,5)→(11,6)
    s, _ = apply(s, [('A', a) for a in drive], 'drv_')
    show(s, 'after drive')

    # Check: is V-M at (11, 6)?
    print(f'V-M at (11, 6)? {(11, 6) in s.vehicle_pos}')
    print(f'pieces at (11, 6): {[pid for pid, p in s.piece_pos if p == (11, 6)]}')

    # Step 4: re-chain reg1 R (9, 8) → (11, 8). But pivot (10, 8) is empty (V-M gone, red gone).
    opts = s.chain_options('reg1')
    print(f'reg1 options: {[DN[x] for x in opts]}')
    # L via red(8, 8) would go to (7, 8). Not useful.

    # Problem: reg1 can't get to (11, 8) without pivot at (10, 8).
    # V-M is at (11, 6) so we can't use it as pivot at (10, 8).
    # Can we bring RED back to (10, 8) as pivot?
    # red at (8, 8). Chain red R: pivot (9, 8) = reg1. Target (10, 8) = track-3 only, no hup2 (V-M gone). len=1 "kraubslpehi-3" no hup → invalid.
    # So target (10, 8) invalid.
    # Unless we drive V-M BACK to (10, 8) first. Let me try.
    drive_back = [1, 3, 3, 3, 1, 1, 4, 2, 2, 4]
    # (11,6)→(11,5)→(10,5)→(9,5)→(8,5)→(8,6)→(8,7)→(9,7)→(9,8)? no track at (9,8)
    # Oh wait (9, 8) has no track. V-M can't be there.
    # Let me recompute: V-M can drive to (10, 7) (track) but not (10, 8) directly from (10, 7)... actually (10, 7) to (10, 8) is A2 (down) and (10, 8) is track-3. Valid.
    # So V-M drive back: (11, 6)→(11, 5)→(10, 5)→(10, ... wait (10, 6) empty. So (10, 5) to (10, 7) needs gap. Via (9, 5)→(9, 4)? No (10, 7) not adjacent to (10, 5).
    # Actually path: (11, 6) → (11, 5) → (10, 5) → (9, 5) → (8, 5) → (8, 6) → (8, 7) → (9, 7) → (10, 7) → (10, 8). 9 moves.
    drive_back = [1, 3, 3, 3, 1, 1, 4, 4, 2]
    s, _ = apply(s, [('A', a) for a in drive_back], 'bak_')
    show(s, 'after drive back')
    print(f'V-M at (10, 8)? {(10, 8) in s.vehicle_pos}')
