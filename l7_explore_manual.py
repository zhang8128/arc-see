"""Systematic click exploration from chain-9 state.
Click every cell and see what changes. Might reveal hidden mechanics.
"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
import numpy as np
import copy
from lf52_tool import LF52, render_png
from l7_harness import L7Harness
from arcengine import GameAction


def go_to_chain9():
    h = L7Harness(verbose=False)
    h.restore_to('chain8')
    # execute chain 9: reg1 R (9,8)→(11,8) via red pivot
    # vp=(-39, 5). Screen (9*6+3-39, 8*6+3+5) = (18, 56). Target (30, 56).
    h.click(18, 56)
    h.click(30, 56)
    return h


def scan_all_clicks(h, label):
    """Try every click position. Save state before each. Compare after."""
    base_state = copy.deepcopy(h._base.env._game)
    base_pix = h.pixels().copy()
    hits = []
    ik = base_state.ikhhdzfmarl
    print(f'[{label}] vp={tuple(ik.hncnfaqaddg.cdpcbbnfdp)}')
    print(f'  foz: {[(s.name, tuple(s.chahdtpdoz)) for s in ik.hncnfaqaddg.xpnsbxlatu if "fozwvlovdui" in s.name]}')
    # Scan ALL 64x64 pixels. Check for piece position changes.
    base_foz = {(s.name, tuple(s.chahdtpdoz)) for s in ik.hncnfaqaddg.xpnsbxlatu if 'fozwvlovdui' in s.name}
    base_veh = {tuple(s.chahdtpdoz) for s in ik.hncnfaqaddg.xpnsbxlatu if s.name == 'hupkpseyuim2'}
    for sy in range(64):
        for sx in range(64):
            h._base.env._game = copy.deepcopy(base_state)
            h._base.obs = None
            h._base._cached_frame = None
            obs = h._base.env.step(GameAction.ACTION6, data={'x': sx, 'y': sy})
            new_pix = np.array(obs.frame[-1], dtype=np.int64)
            diff = (base_pix != new_pix).sum()
            after = h._base.env._game.ikhhdzfmarl
            new_foz = {(s.name, tuple(s.chahdtpdoz)) for s in after.hncnfaqaddg.xpnsbxlatu if 'fozwvlovdui' in s.name}
            new_veh = {tuple(s.chahdtpdoz) for s in after.hncnfaqaddg.xpnsbxlatu if s.name == 'hupkpseyuim2'}
            # Only care about state changes
            if new_foz != base_foz or new_veh != base_veh:
                hits.append((sx, sy, diff, new_foz, new_veh))
    # Restore
    h._base.env._game = copy.deepcopy(base_state)
    h._base.obs = None
    h._base._cached_frame = None
    print(f'State-change click hits: {len(hits)}')
    for sx, sy, d, foz, veh in hits[:20]:
        print(f'  ({sx},{sy}) diff={d}, foz={sorted(foz)}, veh={sorted(veh)}')


if __name__ == '__main__':
    h = go_to_chain9()
    h.render('/tmp/l7_ch9_frame.png')
    scan_all_clicks(h, 'chain9')
