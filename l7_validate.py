"""Validate l7_sim.py against the engine on the verified chain 1-9 sequence.

For each step: run both sim and engine, compare piece & vehicle positions.
Mismatch = sim bug.
"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
import copy
from lf52_tool import LF52
from arcengine import GameAction

from l7_sim import load_init, Sim

U, D, L, R = (0, -1), (0, 1), (-1, 0), (1, 0)
A_DIR = {1: U, 2: D, 3: L, 4: R}
DIR_LETTER = {U: 'U', D: 'D', L: 'L', R: 'R'}


# Each step:
#   ('A', [a1,a2,...]) for actions, or
#   ('C', piece_id, direction) for a chain we initiate in the sim.
#
# For the engine, we separately supply a pair of (click_x, click_y) screen coords
# that we know initiate that chain. The engine's viewport may shift — we pass
# the same clicks that the verified session used.

VERIFIED = [
    # step, sim_op, engine_click_pair (or None for actions)
    ('A', [3, 3, 1, 1, 3, 3, 3], None),
    ('C', 'reg1', D, [(6, 12), (6, 24)]),      # chain 1: (0,1)→(0,3)
    ('A', [4, 4, 4, 2, 2, 3, 3, 2], None),
    ('C', 'reg1', D, [(13, 44), (13, 55)]),    # chain 2: (1,6)→(1,8)
    ('A', [1, 4, 4, 1, 1, 4, 4, 4], None),
    ('C', 'red', D, [(42, 12), (42, 24)]),     # load red: (6,1)→(6,3)
    ('A', [3, 3, 3, 2, 2, 4, 4, 4, 2], None),
    ('C', 'red', D, [(43, 44), (43, 55)]),     # chain: red delivered to slot 6 = (6,8)
    ('A', [1, 3, 3, 3, 1, 1, 3, 3, 3, 4, 4, 4, 2, 2, 3, 3, 3, 2], None),
    ('C', 'reg1', R, [(13, 55), (25, 55)]),    # tan 1→3 via teal(dgx) pivot at slot 2 = (3,8)
    ('C', 'reg1', R, [(25, 55), (37, 55)]),    # tan 3→5 via dgx(4,8)? ending at (5,8)
    ('C', 'reg1', R, [(37, 55), (47, 55)]),    # tan 5→7 via lb(6,8) pivot = red... wait
    ('C', 'red', R, [(43, 55), (55, 55)]),     # red 6→8 — TRIGGERS SCROLL
    ('C', 'reg1', R, [(5, 55), (17, 55)]),     # post-scroll: tan (5,8)→(7,8) via red(6,8)? hmm
    ('A', [2, 3, 2, 2, 4, 4, 2], None),        # drive
    ('C', 'red', R, [(11, 55), (23, 55)]),     # chain 8
]


def run_engine(sequence):
    """Run on live engine, yielding (piece_pos, vehicle_pos) after each step."""
    g = LF52(up_to_level=7, verbose=False)
    yield snap(g)
    for step in sequence:
        kind = step[0]
        if kind == 'A':
            for a in step[1]:
                g.action(a)
        elif kind == 'C':
            clicks = step[3]
            for x, y in clicks:
                g.click(x, y)
        yield snap(g)


def snap(g):
    """Extract (piece_pos_dict, vehicle_tuple, dgx_tuple) from engine."""
    ik = g.env._game.ikhhdzfmarl
    grid = ik.hncnfaqaddg
    pieces = {}
    vehicles = []
    dgxs = []
    for s in grid.xpnsbxlatu:
        n = s.name
        pos = tuple(s.chahdtpdoz)
        if n == 'fozwvlovdui':
            pieces.setdefault('_regs', []).append(pos)
        elif n == 'fozwvlovdui_red':
            pieces['red'] = pos
        elif n == 'fozwvlovdui_blue':
            pieces['blue'] = pos
        elif n == 'hupkpseyuim2':
            vehicles.append(pos)
        elif n == 'dgxfozncuiz':
            dgxs.append(pos)
    regs = sorted(pieces.pop('_regs', []))
    for i, p in enumerate(regs, 1):
        pieces[f'reg{i}'] = p
    return pieces, tuple(sorted(vehicles)), tuple(sorted(dgxs))


def run_sim(sequence):
    s = load_init()
    yield s.pieces, s.vehicle_pos, s.dgx_pos
    for step in sequence:
        kind = step[0]
        if kind == 'A':
            for a in step[1]:
                s = s.do_action(A_DIR[a])
        elif kind == 'C':
            pid, d = step[1], step[2]
            if pid not in s.pieces:
                raise RuntimeError(f'sim: {pid} missing')
            opts = s.chain_options(pid)
            if d not in opts:
                raise RuntimeError(f'sim: chain {pid} {DIR_LETTER[d]} invalid. valid={[DIR_LETTER[x] for x in opts]}; piece@{s.pieces[pid]}')
            s = s.do_chain(pid, d)
        yield s.pieces, s.vehicle_pos, s.dgx_pos


def main():
    print('Running engine and sim in parallel...')
    mismatch = False
    eng_gen = run_engine(VERIFIED)
    sim_gen = run_sim(VERIFIED)
    for i, ((ep, ev, edg), (sp, sv, sdg)) in enumerate(zip(eng_gen, sim_gen)):
        eng_piece_set = (frozenset(ep.values()), sorted(ep.keys()))
        sim_piece_set = (frozenset(sp.values()), sorted(sp.keys()))
        if eng_piece_set != sim_piece_set or ev != sv or edg != sdg:
            print(f'\nMISMATCH at step {i}: {VERIFIED[i-1] if i>0 else "init"}')
            print(f'  engine pieces: {sorted(ep.items())}')
            print(f'  sim    pieces: {sorted(sp.items())}')
            print(f'  engine vehicles: {ev}')
            print(f'  sim    vehicles: {sv}')
            print(f'  engine dgx: {edg}')
            print(f'  sim    dgx: {sdg}')
            mismatch = True
            break
        print(f'step {i}: OK  pieces={sorted(ep.items())} vehicles={ev} dgx_diff={len(set(edg)^set(self_init_dgx(i)))}' if False else f'step {i}: OK  (pieces={sorted(ep.items())}; {len(edg)} DGX)')
    if not mismatch:
        print('\nALL STEPS MATCHED')


if __name__ == '__main__':
    main()
