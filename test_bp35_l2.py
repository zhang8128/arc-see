"""Test BP35 L2 starting from L2 directly."""
import sys
import arc_agi
from arcengine import GameAction

# Import L1 solution
from solutions.solution_bp35 import SOLUTIONS


def click_tile(env, gx, gy):
    eng = env._game.oztjzzyqoek
    cam_y = eng.camera.rczgvgfsfb[1]
    return env.step(GameAction.ACTION6, data={'x': gx*6+3, 'y': gy*6-cam_y+3})


def do(env, tok):
    t = tok.upper().strip()
    eng = env._game.oztjzzyqoek
    cam_y = eng.camera.rczgvgfsfb[1]
    if t == 'L': return env.step(GameAction.ACTION3)
    elif t == 'R': return env.step(GameAction.ACTION4)
    elif t == 'U': return env.step(GameAction.ACTION7)
    elif t == 'CB':
        p = eng.twdpowducb.qumspquyus
        gu = eng.vivnprldht
        dy = -1 if gu else 1
        return env.step(GameAction.ACTION6, data={'x': p[0]*6, 'y': (p[1]+dy)*6 - cam_y})
    elif t.startswith('C'):
        x, y = t[1:].split(',')
        return click_tile(env, int(x), int(y))
    raise ValueError(tok)


def grid_str(eng, y_start=0, y_end=None):
    lookup = eng.hdnrlfmyrj.jhzcxkveiw
    p = eng.twdpowducb
    w, h = eng.hdnrlfmyrj.grid_size
    if y_end is None: y_end = h
    rows = []
    for y in range(y_start, y_end):
        row = ''
        for x in range(w):
            t = lookup(x, y)
            if (x, y) == (p.grid_x, p.grid_y):
                row += 'P'
            elif t and hasattr(t[0], 'name') and t[0].name:
                row += t[0].name[0]
            else:
                row += '.'
        rows.append(f'{y:2d}: {row}')
    return '\n'.join(rows)


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make('bp35-0a0ad940', render_mode=None)
    env.reset(); obs = env.reset()

    # Run L1 to get to L2
    for desc in SOLUTIONS[1]:
        obs = do(env, desc)
    print(f"After L1: levels={obs.levels_completed}")

    # Now on L2
    eng = env._game.oztjzzyqoek
    p = eng.twdpowducb
    print(f"Player at ({p.grid_x},{p.grid_y})")
    print("=== L2 GRID ===")
    print(grid_str(eng))
    print()

    # Run any test sequence from argv
    for tok in sys.argv[1:]:
        obs = do(env, tok)
        p = eng.twdpowducb
        print(f"--- {tok} --- P=({p.grid_x},{p.grid_y}) levels={obs.levels_completed} state={obs.state.name}")
        print(grid_str(eng, 0, 40))
        if obs.state.name == 'GAME_OVER':
            print(f"GAME OVER!")
            break
        if obs.state.name == 'WIN':
            print(f"★ FULL WIN!")
            break


if __name__ == '__main__':
    main()
