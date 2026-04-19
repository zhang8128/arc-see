"""Plan v2:
1. Chain reg1 R (9,8) → (11,8). reg1 at (11,8).
2. Drive V-M (with red) from (10,8) to (6,6). Long M-drive.
3. Chain red D (6,6) → (6,8) via DGX(6,7). red at (6,8), V-M at (6,6) empty.
4. Drive V-M empty from (6,6) to (11,6). M-drive back.
5. Chain reg1 UP (11,8) → (11,6) via DGX(11,7). Target valid (V-M there, no red).
6. reg1 loaded on V-M at (11,6).
7. Drive V-M with reg1 to (14, 2). reg1 at (14, 2).
8. Chain red to (14, 3) — need to position red.
"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
from l7_sim import load_init
from l7_search_deep import at_chain9

U, D, L, R = (0, -1), (0, 1), (-1, 0), (1, 0)
A_DIR = {1: U, 2: D, 3: L, 4: R}
DN = {U:'U',D:'D',L:'L',R:'R'}


def show(s, lbl):
    print(f'[{lbl}] pieces={s.pieces}')
    veh_dgx = sorted(set(s.vehicle_pos) & set(s.dgx_pos))
    print(f'  vehicles={s.vehicle_pos}')
    print(f'  veh+DGX: {veh_dgx}')


def apply_chain(s, pid, d, lbl):
    opts = s.chain_options(pid)
    if d not in opts:
        print(f'  {lbl}: FAIL chain {pid} {DN[d]}. opts={[DN[x] for x in opts]}')
        return s, False
    s2 = s.do_chain(pid, d)
    print(f'  {lbl}: {pid} {DN[d]} → {s2.pieces[pid] if pid in s2.pieces else "consumed"}')
    return s2, True


def apply_a(s, action_list, lbl):
    for a in action_list:
        d = A_DIR[a]
        s = s.do_action(d)
    return s


if __name__ == '__main__':
    s = at_chain9()
    show(s, 'Start at_chain9')

    # Step 1: reg1 R to (11, 8)
    s, ok = apply_chain(s, 'reg1', R, 'ch9')
    show(s, 'after ch9')

    # Step 2: drive V-M (with red) to (6, 6)
    # Path: (10,8)→(10,7)→(9,7)→(8,7)→(8,6)→(8,5)→(9,5)→(9,4)→(9,3)→(10,3)→(11,3)→(11,2)→(11,1)
    # Actually we want (6, 6). Let me trace.
    # (10,8)→(10,7) A1
    # (10,7)→(9,7) A3
    # (9,7)→(8,7) A3
    # (8,7)→(8,6) A1
    # (8,6)→(6,6)? Not adjacent. (8,6)→(8,5) A1; (8,5)→(8,6)? already there. Hmm.
    # Actually (6, 6) connects to (6, 5), (6, 3) in L-component! Not to M.
    # M has (8, 6) but not (6, 6) or (7, 6). Let me verify.
    # (6, 6) is track-up — part of which component? Let me ask.
    # Component 2 (M): includes (8, 5), (8, 6), (8, 7), (9, 3-5/7), (10, 3/5/7/8), (11, 1-3/5/6), (12, 1), (13, 1), (14, 1/2).
    # (6, 6) NOT in M! It's in L-component.
    # Oh no — V-M can't reach (6, 6). That's L-component.
    # So Plan v2 step 2 is impossible.
    print()
    print('CORRECTION: (6, 6) is in L-component, not M!')
    print('V-M in M-component can only reach M-cells.')
    print('M DGX pivots that allow red offload:')
    print('  (11, 7) DGX adj (11, 6) V, (11, 8) hup')
    # row 8 DGXs (2, 8), (4, 8) adj (1, 8), (3, 8), (5, 8) hup but no tracks at y=8 except (10, 8). DGX not reachable by V-M.
