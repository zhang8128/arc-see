"""Test A1/A2 systematically across many states.
Maybe they're active when a piece is pre-selected or vehicle is at certain position."""
import copy, sys
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
from lf52_tool import LF52


def sprite_map(g):
    d = defaultdict(list)
    for item in g.env._game.ikhhdzfmarl._sorted_cache:
        _, sp, _ = item
        d[getattr(sp, 'name', '')].append((sp.x, sp.y))
    return d


def g_snap(g):
    return (copy.deepcopy(g.env._game), copy.deepcopy(g.obs))


def g_restore(g, snap):
    g.env._game = copy.deepcopy(snap[0])
    g.obs = copy.deepcopy(snap[1])
    g._cached_frame = None


def apply_seq(g, seq):
    for step in seq:
        if step[0] == 'C':
            g.click(*step[1]); g.click(*step[2])
        else:
            g.action(step[1])


def test_a1a2(g, label):
    """For current state, test each A1/A2 and report sprite changes."""
    base = g_snap(g)
    base_sm = sprite_map(g)
    base_foz = sorted(base_sm['fozwvlovdui'])
    base_h2 = sorted(base_sm['hupkpseyuim2'])
    base_h1 = sorted(base_sm['hupkpseyuim'])

    for a in [1, 2]:
        g_restore(g, base)
        try:
            g.action(a)
            sm2 = sprite_map(g)
            foz2 = sorted(sm2['fozwvlovdui'])
            h22 = sorted(sm2['hupkpseyuim2'])
            h12 = sorted(sm2['hupkpseyuim'])
            changes = []
            if foz2 != base_foz:
                changes.append(f'foz:{base_foz}->{foz2}')
            if h22 != base_h2:
                changes.append(f'h2:{base_h2}->{h22}')
            if h12 != base_h1:
                changes.append(f'h1:{base_h1}->{h12}')
            pix_diff = int((g.pixels() != g_snap(g)[0].ikhhdzfmarl.xfyfphklhzp).sum()) if False else 0
            # Compare pixels before after
            g_before_pix = None
            if changes:
                print(f'  [{label}] A{a}: {", ".join(changes)}')
        except Exception as e:
            print(f'  [{label}] A{a}: ERROR {e}')
    g_restore(g, base)


def main():
    # Test various states
    states = []

    # 1. INIT
    g = LF52(up_to_level=4, verbose=False)
    states.append(('init', g_snap(g)))

    # 2. After A3
    g2 = LF52(up_to_level=4, verbose=False)
    g2.action(3)
    states.append(('A3', g_snap(g2)))

    # 3. After piece1 click (selected)
    g3 = LF52(up_to_level=4, verbose=False)
    g3.click(13, 25)
    states.append(('piece1-selected', g_snap(g3)))

    # 4. After first merge
    g4 = LF52(up_to_level=4, verbose=False)
    g4.click(13, 25); g4.click(25, 25)
    states.append(('merge1', g_snap(g4)))

    # 5. After full opener
    g5 = LF52(up_to_level=4, verbose=False)
    apply_seq(g5, [
        ('C',(13,25),(25,25)),('C',(25,25),(37,25)),('A',3),('C',(37,25),(49,25)),
        ('A',4),('A',4),('A',4),('A',4),('C',(19,25),(31,25)),
    ])
    states.append(('opener', g_snap(g5)))

    # 6. Post-15
    g6 = LF52(up_to_level=4, verbose=False)
    apply_seq(g6, [
        ('C',(13,25),(25,25)),('C',(25,25),(37,25)),('A',3),('C',(37,25),(49,25)),
        ('A',4),('A',4),('A',4),('A',4),
        ('C',(19,25),(31,25)),('C',(31,25),(31,37)),('C',(31,37),(31,49)),
        ('C',(49,25),(49,37)),('C',(49,37),(49,49)),
        ('C',(49,49),(37,49)),('C',(37,49),(25,49)),
    ])
    states.append(('post-15', g_snap(g6)))

    # 7. After A3x3 from init (h2 aligned with col 30)
    g7 = LF52(up_to_level=4, verbose=False)
    for _ in range(3): g7.action(3)
    states.append(('A3x3', g_snap(g7)))

    # 8. After A3x4 from init (h2 stuck at 24, 66)
    g8 = LF52(up_to_level=4, verbose=False)
    for _ in range(4): g8.action(3)
    states.append(('A3x4', g_snap(g8)))

    # 9. Click piece1 then try A1/A2 (select + action)
    # 10. After loading: piece selected in vehicle
    g10 = LF52(up_to_level=4, verbose=False)
    apply_seq(g10, [
        ('C',(13,25),(25,25)),('C',(25,25),(37,25)),('A',3),('C',(37,25),(49,25)),
    ])
    states.append(('loaded', g_snap(g10)))
    g10.click(19, 25)  # select loaded piece
    states.append(('loaded+sel', g_snap(g10)))

    # Test A1/A2 at each state
    g_test = LF52(up_to_level=4, verbose=False)
    for label, snap in states:
        g_restore(g_test, snap)
        test_a1a2(g_test, label)


if __name__ == '__main__':
    main()
