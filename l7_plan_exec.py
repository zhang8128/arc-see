"""Manually execute the full plan in sim:
1. Start from chain-9 state.
2. Chain reg1 R (9,8)→(11,8) via red pivot.
3. Chain red L (10,8)→(8,8) via reg1 pivot. [red off V-M]
4. Drive V-M (empty now at 10,8) to (11, 6) via M-component paths.
5. Chain reg1 UP (11,8)→(11,6) via DGX(11,7). reg1 loaded on V-M.
6. Drive V-M with reg1 to (14, 2) via M-component.
7. Chain red to (14, 3) via some bridge.
8. Execute the col-14 leapfrog bridge.

Each A-action moves ALL 6 vehicles. We need careful ordering.
This is a search, not a straight-line plan. Use greedy sim execution
with backtracking via sim state snapshots.
"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
from dataclasses import replace
import copy

from l7_sim import load_init, Sim
from l7_search_deep import at_chain9

U, D, L, R = (0, -1), (0, 1), (-1, 0), (1, 0)
A_DIR = {1: U, 2: D, 3: L, 4: R}
DN = {U: 'U', D: 'D', L: 'L', R: 'R'}


def show(s, label):
    print(f'{label}:')
    print(f'  pieces: {s.pieces}')
    print(f'  vehicles: {s.vehicle_pos}')
    print(f'  foz={s.foz_count()}')


def try_chain(s, pid, d, label):
    if pid not in s.pieces:
        print(f'  SKIP {label}: {pid} missing')
        return s, False
    opts = s.chain_options(pid)
    if d not in opts:
        print(f'  FAIL {label}: chain {pid} {DN[d]} INVALID. options={[DN[x] for x in opts]}, piece@{s.pieces[pid]}')
        return s, False
    s2 = s.do_chain(pid, d)
    print(f'  OK {label}: chain {pid} {DN[d]} → {s2.pieces[pid] if pid in s2.pieces else "consumed"}')
    return s2, True


def try_act(s, a, label):
    d = A_DIR[a]
    s2 = s.do_action(d)
    # Compare
    changed = s2.sig() != s.sig()
    print(f'  {label}: A{a} changed={changed}, vehicles={s2.vehicle_pos}')
    return s2


if __name__ == '__main__':
    s = at_chain9()
    show(s, 'Start')

    # Phase 1: chain reg1 R to (11, 8)
    s, ok = try_chain(s, 'reg1', R, 'chain reg1 R')
    show(s, 'after reg1 R')

    # Phase 2: chain red L from (10, 8) to (8, 8) via reg1(9, 8) pivot?
    # Wait reg1 is at (11, 8) now, not (9, 8). red at (10, 8) chain L: pivot (9, 8) is hup (reg1 moved). Invalid.
    # Alternative: keep red's chain for later. Actually we can't chain red L — need reg1 or another pivot at (9, 8).
    # Let's try another sequence.
    # Option: before moving reg1, chain red L first. But initially red chain options at (10, 8):
    # L: pivot (9, 8) = reg1 → valid. Target (8, 8) hup → valid. YES!

    s = at_chain9()  # restart
    show(s, 'Restart from chain-9')
    s, ok = try_chain(s, 'red', L, 'chain red L (10,8)→(8,8)')
    show(s, 'after red L')

    # Now red at (8, 8). V-M still at (10, 8) (empty of red since red chained out).
    # Actually wait — when red chains out, it leaves V-M. V-M stays at (10, 8). Let me verify.
    # Verify: a chain moves a piece from source to target. Vehicle at source cell doesn't move.
    # So V at (10, 8) stays. Red goes to (8, 8). Good.
    print()
    print(f'V-M at {"yes" if (10, 8) in s.vehicle_pos else "no"}')
    print(f'piece at (10, 8)? {[pid for pid, p in s.piece_pos if p == (10, 8)]}')

    # Phase 3: chain reg1 R (9, 8) → (11, 8) via pivot? (10, 8) has V-M only now, no foz/dgx.
    # Unless DGX at (10, 8). No DGX currently. Invalid.
    opts = s.chain_options('reg1')
    print(f'reg1 options after red L: {[DN[x] for x in opts]}')
    # Hmm, pivot at (10, 8) no foz/dgx → chain R fails. reg1 at (9, 8) stuck.

    # Plan B: chain reg1 R FIRST (to (11, 8)), then drive V-M (with red) to (11, 6).
    # After V-M reaches (11, 6), red is at (11, 6). Chain red D via DGX(11, 7) to (11, 8)? No, reg1 at (11, 8).
    # Alternative: chain reg1 UP (11, 8) via DGX(11, 7) to (11, 6). Target (11, 6) has V-M + red → len 3 invalid.
    # Hmm, need red NOT at (11, 6) when reg1 chains UP.
    #
    # Plan C: chain reg1 R (9,8)→(11,8). Drive V-M (with red) to (11, 5). Chain red D (11,5)→(11,7)? target (11,7) DGX+hup len=2 no hup2 invalid.
    # chain red D from (11, 5) via pivot (11, 6) track+vehicle if V there. Target (11, 7) invalid.
    # chain red D from (11, 5) via pivot (11, 6)=track+V if V there — but if V still there, V just dragged red there. Circular.
    print()
    print('=== Plan B: drive V-M with red further, leave red off somewhere useful ===')
    s = at_chain9()
    s, _ = try_chain(s, 'reg1', R, 'reg1 R')
    # Drive V-M from (10, 8) upward. A1.
    for a in [1, 3, 3, 1, 1, 4, 4, 4, 2]:  # ~(10,8)→(10,7)→(9,7)→(8,7)→(8,6)→(8,5)→(9,5)→(10,5)→(11,5)→(11,6)
        s = try_act(s, a, f'A{a}')
    show(s, 'after drive')
    # Check positions
    print(f'red at {s.pieces["red"]}, reg1 at {s.pieces["reg1"]}')
    # Chain red to somewhere off V-M to free V-M for picking up reg1
    if s.pieces['red'] == (11, 6):
        opts = s.chain_options('red')
        print(f'red options: {[DN[x] for x in opts]}')
    # DGX state after drive
    veh_dgx = set(s.vehicle_pos) & set(s.dgx_pos)
    print(f'DGX+vehicle cells: {sorted(veh_dgx)}')
    print(f'mobile DGX cells: {sorted(set(s.dgx_pos) - {(0,2),(6,2),(13,3),(15,5),(17,5),(15,6),(17,6),(1,7),(6,7),(11,7),(2,8),(4,8)})}')
    # Try chain reg1 UP (11,8) via DGX(11,7) to (11, 6). Target (11, 6) has V + red.
    opts = s.chain_options('reg1')
    print(f'reg1 options at (11,8): {[DN[x] for x in opts]}')
    # U target (11, 6) = V + red + track-up → len 3 → invalid.
    # Need red off V.
    # Also: first move V-M out of (11, 6). Drive V-M somewhere (red follows).
    # Then reg1 can chain UP to (11, 6) with just track (invalid — need vehicle).
    # Plan: red off V at a different cell.
    print()
    print('Explore: chain red somewhere off V')
    # from (11, 6) options = []. Try driving V further so red has options later.
    # e.g., drive V to (11, 5). Then red at (11, 5) chain options:
    # D: pivot (11, 6) V only no foz/dgx (if no DGX there). Actually if we move V further, DGX may follow.
    # Let's just try: drive V from (11, 6) to (10, 5) via A3 then A1. Carrying red.
    for a, lbl in [(1, 'A1: V to (11,5)')]:
        s = try_act(s, a, lbl)
    # After A1: V at (11, 5)? But (11, 5) track-> valid. Let's see
    print(f'After A1: red at {s.pieces["red"]}')
    print(f'vehicles: {s.vehicle_pos}')
    opts = s.chain_options('red')
    print(f'red options: {[DN[x] for x in opts]}')
