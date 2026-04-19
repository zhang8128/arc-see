"""Smart click scan: snapshot once, revert via deepcopy, try each cell-center click."""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
import copy
from lf52_tool import LF52
from l7_harness import L7Harness
from arcengine import GameAction


def go_to_chain9(h):
    h.restore_to('chain8')
    h.click(18, 56)
    h.click(30, 56)


def snap_state(ik):
    foz = tuple(sorted((s.name, tuple(s.chahdtpdoz)) for s in ik.hncnfaqaddg.xpnsbxlatu if 'fozwvlovdui' in s.name))
    veh = tuple(sorted(tuple(s.chahdtpdoz) for s in ik.hncnfaqaddg.xpnsbxlatu if s.name == 'hupkpseyuim2'))
    dgx = tuple(sorted(tuple(s.chahdtpdoz) for s in ik.hncnfaqaddg.xpnsbxlatu if s.name == 'dgxfozncuiz'))
    return foz, veh, dgx


def test_click(h, snap, sx, sy):
    h._base.env._game = copy.deepcopy(snap)
    h._base.obs = None
    h._base._cached_frame = None
    h._base.env.step(GameAction.ACTION6, data={'x': sx, 'y': sy})
    return snap_state(h._base.env._game.ikhhdzfmarl)


if __name__ == '__main__':
    h = L7Harness(verbose=False)
    go_to_chain9(h)
    snap = copy.deepcopy(h._base.env._game)
    base = snap_state(h._base.env._game.ikhhdzfmarl)
    print(f'base foz: {base[0]}')

    found = []
    for world_y in range(9):
        for world_x in range(23):
            sx = world_x*6 + 3 + (-39)
            sy = world_y*6 + 3 + 5
            if not (0 <= sx < 64 and 0 <= sy < 64):
                continue
            got = test_click(h, snap, sx, sy)
            if got != base:
                found.append((world_x, world_y, sx, sy, got))
                print(f'CHANGE at world ({world_x}, {world_y}) screen ({sx}, {sy})')
                print(f'  new foz: {got[0]}')
    print(f'\nTotal state-changing clicks: {len(found)}')
