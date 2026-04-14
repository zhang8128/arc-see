"""Test BP35 L7 by replaying L1-L6 then starting at L7."""
import sys
import arc_agi
from arcengine import GameAction
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


def replay_existing(env, upto_level):
    for lvl in sorted(SOLUTIONS.keys()):
        if lvl > upto_level:
            break
        for desc in SOLUTIONS[lvl]:
            eng = env._game.oztjzzyqoek
            cam_y = eng.camera.rczgvgfsfb[1]
            if desc == 'L':
                obs = env.step(GameAction.ACTION3)
            elif desc == 'R':
                obs = env.step(GameAction.ACTION4)
            elif desc == 'CB':
                pp = eng.twdpowducb.qumspquyus
                gu = eng.vivnprldht
                dy = -1 if gu else 1
                obs = env.step(GameAction.ACTION6, data={"x": pp[0]*6, "y": (pp[1]+dy)*6 - cam_y})
            elif desc.startswith('C'):
                cx, cy = map(int, desc[1:].split(','))
                obs = env.step(GameAction.ACTION6, data={"x": cx*6, "y": cy*6 - cam_y})
    return obs


def grid_str(eng):
    lookup = eng.hdnrlfmyrj.jhzcxkveiw
    p = eng.twdpowducb
    w, h = eng.hdnrlfmyrj.grid_size
    rows = []
    for y in range(h):
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
    obs = replay_existing(env, 6)
    print(f"After L1-L6: levels={obs.levels_completed}")
    eng = env._game.oztjzzyqoek
    p = eng.twdpowducb
    print(f"Player: ({p.grid_x},{p.grid_y})")

    # Identify entity types
    lookup = eng.hdnrlfmyrj.jhzcxkveiw
    w, h = eng.hdnrlfmyrj.grid_size
    names = {}
    for y in range(h):
        for x in range(w):
            t = lookup(x, y)
            if t:
                for obj in t:
                    if hasattr(obj, 'name') and obj.name:
                        names.setdefault(obj.name, 0)
                        names[obj.name] += 1
    print("Entity types:")
    for n, c in names.items():
        print(f"  {n[0]}: {n} ({c})")
    print()
    print("=== L7 GRID ===")
    print(grid_str(eng))

    # Run test sequence
    for tok in sys.argv[1:]:
        obs = do(env, tok)
        p = eng.twdpowducb
        print(f"--- {tok} --- P=({p.grid_x},{p.grid_y}) levels={obs.levels_completed} state={obs.state.name}")
        if obs.state.name == 'GAME_OVER':
            print("GAME OVER")
            break
        if obs.state.name == 'WIN':
            print("★ WIN!")
            break


if __name__ == '__main__':
    main()
