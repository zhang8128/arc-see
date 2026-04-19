"""Hand-craft L10 plan in sim."""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
from l7_sim import load_init
from l7_search import DIRS

U, D, L, R = (0, -1), (0, 1), (-1, 0), (1, 0)
A_DIR = {1: U, 2: D, 3: L, 4: R}
DN = {U:'U',D:'D',L:'L',R:'R'}


def show(s, lbl):
    print(f'[{lbl}]')
    for pid, p in s.piece_pos:
        print(f'  {pid}: {p}')
    print(f'  vehicles: {s.vehicle_pos}')
    print(f'  blues on vehicles: {[p for pid, p in s.piece_pos if "blue" in pid and p in s.vehicle_pos]}')


def chain(s, pid, d, label):
    if pid not in s.pieces:
        print(f'  FAIL {label}: {pid} missing')
        return s
    opts = s.chain_options(pid)
    if d not in opts:
        print(f'  FAIL {label}: chain {pid} {DN[d]}. valid={[DN[x] for x in opts]}. at {s.pieces[pid]}')
        return s
    return s.do_chain(pid, d)


def act(s, a_list):
    for a in a_list:
        s = s.do_action(A_DIR[a])
    return s


if __name__ == '__main__':
    s = load_init('/tmp/l10_init.json')
    show(s, 'init')
    print()

    # Phase 1: blue pivots chain setup on row 5
    s = chain(s, 'blue2', L, 'blue2 (6,5) L')  # blue2 (6,5) → (4,5)
    print(f'  blue2 now at: {s.pieces["blue2"]}')
    s = chain(s, 'blue1', L, 'blue1 (5,5) L')  # blue1 (5,5) → (3,5)
    print(f'  blue1 at: {s.pieces["blue1"]}')
    # Phase 2: extend blue ladder down col 3
    s = chain(s, 'blue1', D, 'blue1 (3,5) D')  # via blue3(3,6) → (3,7)
    print(f'  blue1 at: {s.pieces["blue1"]}')
    s = chain(s, 'blue3', D, 'blue3 (3,6) D')  # via blue1(3,7) → (3,8)
    print(f'  blue3 at: {s.pieces["blue3"]}')
    s = chain(s, 'blue1', D, 'blue1 (3,7) D')  # via blue3(3,8) → (3,9)
    print(f'  blue1 at: {s.pieces["blue1"]}')

    show(s, 'after blue cascade')
    print()

    # Now blue1 at (3, 9). reg2 at (6, 9).
    # For consumption: reg1 must reach (5, 9) or similar.
    # reg1 still at (4, 0). Need path down col 4.

    # Option: drive V-4,2 (no blue) up to (4, 1) as NON-pivot. Then stuck.
    # Alternative: chain reg1 down via blue pivots.
    # reg1 at (4, 0) D: pivot (4, 1) = track-T + V. Need foz/dgx. Not initially.
    # Can we move a blue to (4, 1)? (4, 1) is track. Vehicle could be there with blue.
    # But blues on col-8 Vs. Need to bring blue to (4, 1) via col-8 V → row 1 path.

    # Drive col-8 V up. A1 shifts train up. Each V+blue moves up one.
    # Initial V-8,9 has blue6. After A1: V-8,8 with blue6. etc.
    # Eventually get blue-V to (4, 1) via row 1.

    # Simple drive: A1 many times to lift train, then A3 (left) to shift left toward col 4.
    s = act(s, [1, 1, 1, 1, 1, 1, 1, 1])  # 8 A1s: V-8,13 might reach row 5-7 after 8 ups
    print(f'After 8 A1: vehicles={s.vehicle_pos}, pieces={s.pieces}')
    s = act(s, [3, 3, 3, 3])  # left 4
    print(f'After 4 A3: vehicles={s.vehicle_pos}')
    print(f'  pieces: {s.pieces}')
    # Try chain reg1 D now — pivot (4, 1) has V, need foz/dgx. Blue6 might be at (4, 1)?
    # Check cell (4, 1) content.
    print(f'  (4, 1): {s.cell_sprites((4, 1))}')
    print(f'  reg1 chain options: {[DN[x] for x in s.chain_options("reg1")]}')
