"""From chain-9, press A5, then explore clicks in zvcnglshzcx mode."""
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
    vp = tuple(ik.hncnfaqaddg.cdpcbbnfdp)
    lvl = ik.whtqurkphir
    return foz, veh, dgx, vp, lvl


if __name__ == '__main__':
    h = L7Harness(verbose=False)
    go_to_chain9(h)
    # Press A5
    h._base.env.step(GameAction.ACTION5)
    print('After A5:')
    ik = h._base.env._game.ikhhdzfmarl
    print(f'  zvcnglshzcx: {ik.zvcnglshzcx}')
    print(f'  foz count: {len(ik.hncnfaqaddg.ndtvadsrqf("fozwvlovdui"))}')
    print(f'  iajuzrgttrv: {ik.iajuzrgttrv}')
    print(f'  evxflhofing: {ik.evxflhofing}')
    # Now save snapshot and try clicks in bottom-left (zvcnglshzcx trigger: x<16, y>48)
    snap = copy.deepcopy(h._base.env._game)
    base = snap_state(ik)
    found = []
    for sy in range(64):
        for sx in range(64):
            h._base.env._game = copy.deepcopy(snap)
            h._base.obs = None
            h._base._cached_frame = None
            h._base.env.step(GameAction.ACTION6, data={'x': sx, 'y': sy})
            got = snap_state(h._base.env._game.ikhhdzfmarl)
            if got[0] != base[0] or got[1] != base[1]:  # foz or vehicles change
                found.append((sx, sy, got))
            # Also check for win
            if h._base.env._game.ikhhdzfmarl.iajuzrgttrv or h._base.env._game.ikhhdzfmarl.evxflhofing:
                print(f'SPECIAL at ({sx},{sy}): win={h._base.env._game.ikhhdzfmarl.iajuzrgttrv}, lose={h._base.env._game.ikhhdzfmarl.evxflhofing}')
    for sx, sy, got in found:
        print(f'  ({sx}, {sy}): foz={got[0]}')
    print(f'total {len(found)} state-changing clicks')
