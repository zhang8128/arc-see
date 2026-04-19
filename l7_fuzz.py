"""Fuzz test: random actions + chains on both engine and sim, compare states.
If sim diverges from engine, we find the exact step and diagnose.
"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
import random

from lf52_tool import LF52
from l7_sim import load_init, Sim, DIRS
from l7_validate import snap, A_DIR, U, D, L, R

random.seed(42)
DIR_NAME = {U: 'U', D: 'D', L: 'L', R: 'R'}


def screen_xy_for_chain(piece_pos, d, vp=(5, 5)):
    """Return (src_click, dir_click) screen coords for chaining piece at piece_pos in dir d."""
    sx, sy = piece_pos
    tsx, tsy = sx + 2*d[0], sy + 2*d[1]
    return (sx * 6 + 3 + vp[0], sy * 6 + 3 + vp[1]), (tsx * 6 + 3 + vp[0], tsy * 6 + 3 + vp[1])


def fuzz(n_steps=50):
    g = LF52(up_to_level=7, verbose=False)
    s = load_init()
    for step in range(n_steps):
        # Pick random move from sim's move set
        moves_s = []
        for d in DIRS:
            ns = s.do_action(d)
            if ns.sig() != s.sig():
                moves_s.append(('A', d, None))
        for pid in s.pieces:
            for d in s.chain_options(pid):
                moves_s.append(('C', pid, d))
        if not moves_s:
            print(f'step {step}: no moves available')
            return
        mv = random.choice(moves_s)
        # Apply to both
        if mv[0] == 'A':
            d = mv[1]
            a = {U: 1, D: 2, L: 3, R: 4}[d]
            g.action(a)
            s = s.do_action(d)
        else:
            _, pid, d = mv
            pos = s.pieces[pid]
            vp = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
            (sx, sy), (tx, ty) = screen_xy_for_chain(pos, d, vp)
            g.click(sx, sy); g.click(tx, ty)
            s = s.do_chain(pid, d)
        # Compare states
        ep, ev, edg = snap(g)
        sim_p = s.pieces
        sim_v = s.vehicle_pos
        sim_d = s.dgx_pos
        eng_pset = frozenset(ep.values())
        sim_pset = frozenset(sim_p.values())
        if eng_pset != sim_pset or ev != sim_v or edg != sim_d:
            print(f'MISMATCH at step {step}: move={mv}')
            print(f'  engine pieces: {sorted(ep.items())}')
            print(f'  sim    pieces: {sorted(sim_p.items())}')
            print(f'  engine vehicles: {ev}')
            print(f'  sim    vehicles: {sim_v}')
            print(f'  engine dgx: {edg}')
            print(f'  sim    dgx: {sim_d}')
            return
    print(f'Fuzz {n_steps} steps: all match')


if __name__ == '__main__':
    for seed in range(10):
        random.seed(seed)
        print(f'=== seed {seed} ===')
        fuzz(n_steps=500)
