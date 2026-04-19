"""FULL L7 WIN SEQUENCE.

Execution order:
1. Verified chain 1-8 (via lf52_tool setup through chain-8 state).
2. Chain 9: reg1 R (9,8) → (11,8).
3. Bridge setup: drive + chains to get reg1 (18, 6), red (18, 5).
4. R-vehicle maneuvering to get reg1 to (22, 5), V at (22, 4) no DGX.
5. Chain reg2 U: consumes reg1, wins L7.
"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
from l7_sim import load_init
from l7_search_deep import at_chain9

U, D, L, R = (0, -1), (0, 1), (-1, 0), (1, 0)
A_DIR = {1: U, 2: D, 3: L, 4: R}
DN = {U:'U',D:'D',L:'L',R:'R'}


def apply(s, op, lbl):
    if op[0] == 'A':
        d = A_DIR[op[1]]
        ns = s.do_action(d)
        return ns, True
    else:
        pid, d = op[1], op[2]
        if pid not in s.pieces:
            print(f'  FAIL {lbl}: {pid} missing')
            return s, False
        opts = s.chain_options(pid)
        if d not in opts:
            print(f'  FAIL {lbl}: chain {pid} {DN[d]} invalid. opts={[DN[x] for x in opts]}, at {s.pieces.get(pid)}')
            return s, False
        return s.do_chain(pid, d), True


def run():
    s = at_chain9()
    # sim has pieces reg1 (9,8), red (10,8), reg2 (22,6). vp treated as (5,5) for chain-8 sim.
    plan = []

    # Step 1: chain 9 (reg1 R to (11, 8))
    plan.append(('C', 'reg1', R))

    # Step 2: drive V-M with red to (12, 3)
    for a in [1, 3, 3, 1, 1, 4, 1, 1, 4, 4, 4]:
        plan.append(('A', a))

    # Step 3: chain red R to (14, 3)
    plan.append(('C', 'red', R))

    # Step 4: drive V-M empty to (11, 6)
    for a in [3, 3, 3, 2, 2, 4, 4, 2]:
        plan.append(('A', a))

    # Step 5: chain reg1 U to (11, 6)
    plan.append(('C', 'reg1', U))

    # Step 6: drive V-M with reg1 to (14, 2)
    for a in [1, 3, 3, 1, 1, 4, 4, 1, 1, 4, 4, 4, 2]:
        plan.append(('A', a))

    # Step 7-10: col 14 ladder
    plan.append(('C', 'reg1', D))  # (14, 2) → (14, 4)
    plan.append(('C', 'red', D))   # (14, 3) → (14, 5)
    plan.append(('C', 'reg1', D))  # (14, 4) → (14, 6)

    # Step 11-13: east bridge
    plan.append(('C', 'reg1', R))  # (14, 6) → (16, 6)
    plan.append(('C', 'reg1', R))  # (16, 6) → (18, 6)
    plan.append(('C', 'red', R))   # (14, 5) → (16, 5)
    plan.append(('C', 'red', R))   # (16, 5) → (18, 5)

    # Now reg1 (18, 6), red (18, 5). Need to get reg1 to (22, 5) loaded.
    # From A* we know path exists. Let me add the needed steps.
    # Actually this was my h=3 state. I need to figure out the moves from
    # post-bridge to h=3 state. Let me just try running and see if sim continues.

    # For now, try to reach h=3 state via: chain reg1 UP to (18, 4) (needs V at (18, 4) no DGX)
    # Drive R-vehicles to set up (18, 4) non-DGX V.
    # From reach BFS: drive_r [3, 2, 2, 4, 2, 2] got V at (18, 4) but WITH DGX.
    # Need different drives to have V at (18, 4) no DGX.

    # Let me first just run what I have
    for i, op in enumerate(plan):
        s, ok = apply(s, op, f'step{i}')
        if not ok:
            print(f'Plan aborted at step {i}')
            return s
    print(f'After bridge: pieces={s.pieces}')
    print(f'  vehicles={s.vehicle_pos}')
    print(f'  DGX-on-V={sorted(set(s.dgx_pos)&set(s.vehicle_pos))}')
    print(f'  foz_count={s.foz_count()}')
    return s


if __name__ == '__main__':
    run()
