"""Test BP35 with full grid visibility."""
import sys
import arc_agi
from arcengine import GameAction


def grid_str(eng, rows_range=None):
    lookup = eng.hdnrlfmyrj.jhzcxkveiw
    p = eng.twdpowducb
    w, h = eng.hdnrlfmyrj.grid_size
    if rows_range is None:
        rows_range = range(h)
    rows = []
    for y in rows_range:
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


def click_tile(env, gx, gy):
    eng = env._game.oztjzzyqoek
    cam_y = eng.camera.rczgvgfsfb[1]
    screen_x = gx * 6 + 3
    screen_y = gy * 6 - cam_y + 3
    return env.step(GameAction.ACTION6, data={'x': screen_x, 'y': screen_y})


def do(env, tok):
    t = tok.upper().strip()
    if t == 'L':
        return env.step(GameAction.ACTION3)
    elif t == 'R':
        return env.step(GameAction.ACTION4)
    elif t == 'U':
        return env.step(GameAction.ACTION7)
    elif t.startswith('C'):
        x, y = t[1:].split(',')
        return click_tile(env, int(x), int(y))
    raise ValueError(tok)


def show(env, obs, tag=''):
    eng = env._game.oztjzzyqoek
    p = eng.twdpowducb
    print(f"=== {tag} === P=({p.grid_x},{p.grid_y}) gravity_up={eng.vivnprldht} levels={obs.levels_completed} state={obs.state.name}")
    print(grid_str(eng))
    print()


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make('bp35-0a0ad940', render_mode=None)
    env.reset()
    obs = env.reset()
    show(env, obs, 'START')

    for tok in sys.argv[1:]:
        obs = do(env, tok)
        show(env, obs, tok)
        if obs.state.name == 'WIN':
            print(f"★ FULL WIN!")
            break


if __name__ == '__main__':
    main()
