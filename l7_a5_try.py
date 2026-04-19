"""What happens after A5 + clicking the cwyrzsciwms (exit) sprite in L7?
Does the level end in ANY state, or only reject? Also try A5+chain combos."""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
import copy
from lf52_tool import LF52
from l7_harness import L7Harness
from arcengine import GameAction


def go(h):
    h.restore_to('chain8')
    h.click(18, 56)
    h.click(30, 56)


if __name__ == '__main__':
    h = L7Harness(verbose=False)
    go(h)
    # Press A5
    h._base.env.step(GameAction.ACTION5)
    ik = h._base.env._game.ikhhdzfmarl
    print(f'After A5: zvcnglshzcx={ik.zvcnglshzcx}, cwyrzsciwms in grid?')
    # Find cwyrzsciwms sprite
    for s in ik.xpnsbxlatu if hasattr(ik, 'xpnsbxlatu') else []:
        pass
    # Check overall sprites
    print('Sprites with cwyrzs* or similar:')
    for s in ik.hncnfaqaddg.xpnsbxlatu:
        if 'cwyr' in s.name or s.name.startswith('c'):
            print(f'  {s.name} at {s.chahdtpdoz}')
    # Children of ik
    print('ik children (rxmjztculbk):')
    for child in ik.rxmjztculbk:
        print(f'  type={type(child).__name__}, name={getattr(child, "name", "?")}, pos=({getattr(child, "eocrokcvgsq", None)}, {getattr(child, "htoojidbdud", None)})')
    print()

    # Now click bottom-left quadrant (x<16, y>48)
    obs = h._base.env.step(GameAction.ACTION6, data={'x': 5, 'y': 55})
    print(f'After click (5,55): state={obs.state.name}, levels={obs.levels_completed}')
    print(f'  zvcnglshzcx={ik.zvcnglshzcx}, iajuzrgttrv={ik.iajuzrgttrv}')

    # From pre-A5 state, try a chain that was valid
    h2 = L7Harness(verbose=False)
    go(h2)
    h2._base.env.step(GameAction.ACTION5)
    # Also try click + chain
    # Click reg1 at (9, 8) = screen (18, 56)
    obs = h2._base.env.step(GameAction.ACTION6, data={'x': 18, 'y': 56})
    print()
    print(f'After click reg1: state={obs.state.name}, zvcnglshzcx={h2._base.env._game.ikhhdzfmarl.zvcnglshzcx}')
    # Chain indicator should appear? let me click indicator position for direction R (reg1 R)
    # Screen for target (11, 8): (30, 56). Indicator at approx same.
    obs = h2._base.env.step(GameAction.ACTION6, data={'x': 30, 'y': 56})
    ik2 = h2._base.env._game.ikhhdzfmarl
    print(f'After click indicator: state={obs.state.name}, zvcnglshzcx={ik2.zvcnglshzcx}')
    print(f'  pieces: {[(s.name, tuple(s.chahdtpdoz)) for s in ik2.hncnfaqaddg.xpnsbxlatu if "fozwvlovdui" in s.name]}')
