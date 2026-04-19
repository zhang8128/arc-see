"""Test BP35 L9 by replaying L1-L8 then stepping on L9.

Usage: uv run python test_bp35_l9.py [tok1 tok2 ...]
  tokens: L, R, CB, U, Cx,y

Prints the 11×45 tile grid before each action so you can see state evolve.
"""
import sys
import arc_agi
from arcengine import GameAction
from solutions.solution_bp35 import SOLUTIONS


def click_tile(env, gx, gy):
    eng = env._game.oztjzzyqoek
    cam_y = eng.camera.rczgvgfsfb[1]
    return env.step(GameAction.ACTION6, data={'x': gx * 6 + 3, 'y': gy * 6 - cam_y + 3})


def do(env, tok):
    t = tok.upper().strip()
    eng = env._game.oztjzzyqoek
    cam_y = eng.camera.rczgvgfsfb[1]
    if t == 'L':
        return env.step(GameAction.ACTION3)
    if t == 'R':
        return env.step(GameAction.ACTION4)
    if t == 'U':
        return env.step(GameAction.ACTION7)
    if t == 'CB':
        p = eng.twdpowducb.qumspquyus
        gu = eng.vivnprldht
        dy = -1 if gu else 1
        return env.step(GameAction.ACTION6, data={'x': p[0] * 6, 'y': (p[1] + dy) * 6 - cam_y})
    if t.startswith('C'):
        x, y = t[1:].split(',')
        return click_tile(env, int(x), int(y))
    raise ValueError(tok)


def replay(env, upto):
    for lvl in sorted(SOLUTIONS.keys()):
        if lvl > upto:
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
                obs = env.step(GameAction.ACTION6, data={"x": pp[0] * 6, "y": (pp[1] + dy) * 6 - cam_y})
            elif desc.startswith('C'):
                cx, cy = map(int, desc[1:].split(','))
                obs = env.step(GameAction.ACTION6, data={"x": cx * 6, "y": cy * 6 - cam_y})
    return obs


def grid_str(eng):
    lookup = eng.hdnrlfmyrj.jhzcxkveiw
    p = eng.twdpowducb
    w, h = eng.hdnrlfmyrj.grid_size
    rows = [f'    ' + ''.join(str(c % 10) for c in range(w))]
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


def entity_summary(eng):
    lookup = eng.hdnrlfmyrj.jhzcxkveiw
    w, h = eng.hdnrlfmyrj.grid_size
    by_letter = {}
    for y in range(h):
        for x in range(w):
            t = lookup(x, y)
            if t:
                for obj in t:
                    if hasattr(obj, 'name') and obj.name:
                        ch = obj.name[0]
                        by_letter.setdefault(ch, []).append((x, y))
    return by_letter


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make('bp35-0a0ad940', render_mode=None)
    env.reset()
    obs = env.reset()
    obs = replay(env, 8)
    eng = env._game.oztjzzyqoek
    p = eng.twdpowducb
    print(f"After L1-L8: levels_completed={obs.levels_completed} state={obs.state.name}")
    print(f"Player: ({p.grid_x},{p.grid_y}) grav_up={eng.vivnprldht}")
    print(f"Grid size: {eng.hdnrlfmyrj.grid_size}")

    ents = entity_summary(eng)
    print("Entity counts:")
    for ch in sorted(ents):
        print(f"  {ch}: {len(ents[ch])}")

    if not sys.argv[1:]:
        print("\n=== L9 GRID ===")
        print(grid_str(eng))
        print("\nEntity positions:")
        for ch in sorted(ents):
            if ch in ('.', 'x'):
                continue
            print(f"  {ch}: {ents[ch]}")
        return

    for i, tok in enumerate(sys.argv[1:], 1):
        obs = do(env, tok)
        p = eng.twdpowducb
        msg = f"--- #{i} {tok} --- P=({p.grid_x},{p.grid_y}) grav_up={eng.vivnprldht} state={obs.state.name}"
        print(msg)
        if obs.state.name == 'GAME_OVER':
            print("GAME OVER")
            print(grid_str(eng))
            break
        if obs.state.name == 'WIN':
            print("★ WIN!")
            break
    else:
        print("\n=== GRID after sequence ===")
        print(grid_str(eng))


if __name__ == '__main__':
    main()
