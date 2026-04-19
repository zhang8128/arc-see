"""Manual play interface: replay to chain-9, then take actions one at a time
and RENDER each state. I want to LOOK at the frames — maybe see something the
sim doesn't capture.
"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
from lf52_tool import LF52, render_png
from l7_harness import L7Harness
import copy


def dump(h, tag):
    ik = h._base.env._game.ikhhdzfmarl
    grid = ik.hncnfaqaddg
    vp = tuple(grid.cdpcbbnfdp)
    foz = [(s.name, tuple(s.chahdtpdoz)) for s in grid.xpnsbxlatu if 'fozwvlovdui' in s.name]
    veh = sorted([tuple(s.chahdtpdoz) for s in grid.xpnsbxlatu if s.name == 'hupkpseyuim2'])
    dgx = sorted([tuple(s.chahdtpdoz) for s in grid.xpnsbxlatu if s.name == 'dgxfozncuiz'])
    foz_count = len(ik.hncnfaqaddg.ndtvadsrqf('fozwvlovdui'))
    print(f'[{tag}] vp={vp}, foz_count={foz_count}')
    print(f'  foz: {foz}')
    print(f'  vehicles: {veh}')
    mobile_dgx = sorted(set(dgx) & set(veh))
    print(f'  mobile DGX cells: {mobile_dgx}')
    h.render(f'/tmp/l7_{tag}.png', label=tag)


if __name__ == '__main__':
    h = L7Harness(verbose=False)
    h.restore_to('chain8')
    dump(h, 'chain8_start')

    # Now try chain 9: reg1 R (9,8)→(11,8)
    # vp at chain-8 is (-39, 5). Screen for world (9, 8) = (9*6+3-39, 8*6+3+5) = (18, 56). Screen for (11, 8) = (30, 56).
    h.click(18, 56)
    h.click(30, 56)
    dump(h, 'chain9')
    print()
    # From chain-9, let's try forward chains I haven't considered.
    # reg1 at (11, 8). Options?
    # Also red at (10, 8) loaded.
    # Let me try: click red to select, then click indicator direction
    # Can we SELECT red even though it's on vehicle?
    print('Try selecting red at (10, 8)...')
    # Screen for (10, 8) = (10*6+3-39, 8*6+3+5) = (24, 56)
    obs = h.click(24, 56)
    dump(h, 'after_select_red')
