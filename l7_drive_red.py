"""What if we drive V-M (carrying red) to (14, 2)?
Red ends up at (14, 2) loaded on V-M. reg1 stays at (9, 8).
Then can reg1 chain-bridge east using red's new pivot position?

Actually the key: with red at (14, 2), reg1 at (11, 8) could chain
UP via DGX(11,7) to (11,6) if (11,6) has a vehicle. But V-M is now at
(14, 2) with red, not (11, 6).

Alternative: chain red from (14, 2) to serve as pivot for reg1's moves.
But red at (14, 2) = track+vehicle+red. Only useful if reg1 has a chain
nearby using (14, 2) as pivot.

Reg1 chain via pivot (14, 2): source at (12, 2), (14, 0), (14, 4), (16, 2).
- (12, 2) empty (not track, not hup). Permanently no piece.
- (14, 0) empty.
- (14, 4) plain hup. Piece can be there... but reg1 needs to get to (14, 4).
- (16, 2) track-< only. Piece via vehicle — R-component vehicle. But R disconnected from M.

Dead.

Let's just run the drive and see state.
"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
from l7_sim import load_init, Sim
from l7_search_deep import at_chain9

U, D, L, R = (0, -1), (0, 1), (-1, 0), (1, 0)
A_DIR = {1: U, 2: D, 3: L, 4: R}
DN = {U:'U',D:'D',L:'L',R:'R'}


def run_plan(plan):
    s = at_chain9()
    for step in plan:
        if step[0] == 'A':
            s = s.do_action(A_DIR[step[1]])
        else:
            s = s.do_chain(step[1], step[2])
    return s


if __name__ == '__main__':
    # Start chain-9: reg1 (9,8), red (10,8) on V-M.
    # Drive V-M from (10,8) to (14,2) via M-component path.
    # Path: (10,8)→(10,7)→(9,7)→(8,7)→(8,6)→(8,5)→(9,5)→(9,4)→(9,3)→(10,3)→(11,3)→(11,2)→(11,1)→(12,1)→(13,1)→(14,1)→(14,2)
    # A sequence: A1 A3 A3 A1 A1 A4 A1 A1 A4 A4 A1 A1 A4 A4 A4 A2
    plan_actions = [1, 3, 3, 1, 1, 4, 1, 1, 4, 4, 1, 1, 4, 4, 4, 2]
    plan = [('A', a) for a in plan_actions]
    s = run_plan(plan)
    print(f'After drive: pieces={s.pieces}')
    print(f'vehicles: {s.vehicle_pos}')
    print(f'DGX (mobile): {[p for p in s.dgx_pos if p in set(s.vehicle_pos)]}')

    # Check what's at key cells
    for c in [(14, 2), (14, 3), (11, 8), (10, 8), (9, 8), (11, 6), (15, 5)]:
        sprites = s.cell_sprites(c)
        print(f'cell {c}: {sprites}')

    # Try chain options for reg1
    print(f'reg1 options at {s.pieces["reg1"]}: {[DN[x] for x in s.chain_options("reg1")]}')
    print(f'red options at {s.pieces["red"]}: {[DN[x] for x in s.chain_options("red")]}')
