"""Render L7 initial state + post-click states as PNG for visual inspection."""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
sys.path.insert(0, '/Users/kairos/Projects/arc-see/solutions')

import copy
from pathlib import Path
from lf52_tool import LF52, render_png
from arcengine import GameAction
import solution_lf52_l5 as L5
import solution_lf52_l6 as L6
import numpy as np


def setup_l7(g):
    g.env._game.set_level(4)
    g.env._game.on_set_level(g.env._game.current_level)
    obs = g.env.step(GameAction.ACTION6, data={'x': 0, 'y': 0})
    for step in L5.SOLUTION:
        if isinstance(step, str):
            a = int(step[1:])
            obs = g.env.step(getattr(GameAction, f'ACTION{a}'))
        else:
            kind, src, direction = step
            ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
            sx, sy = src
            dx, dy = direction
            obs = g.env.step(GameAction.ACTION6, data={'x': sx*6+3+ox, 'y': sy*6+3+oy})
            ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
            obs = g.env.step(GameAction.ACTION6, data={'x': (sx+2*dx)*6+3+ox, 'y': (sy+2*dy)*6+3+oy})
    steps = L6.parse_solution()
    for step in steps:
        if step[0] == 'A':
            obs = g.env.step(getattr(GameAction, f'ACTION{step[1]}'))
        else:
            _, (sx, sy), (dx, dy) = step
            ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
            obs = g.env.step(GameAction.ACTION6, data={'x': sx*6+3+ox, 'y': sy*6+3+oy})
            ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
            obs = g.env.step(GameAction.ACTION6, data={'x': (sx+2*dx)*6+3+ox, 'y': (sy+2*dy)*6+3+oy})
    return obs


def main():
    out_dir = Path('/tmp/lf52_frames')
    out_dir.mkdir(exist_ok=True)

    g = LF52(up_to_level=1, verbose=False)
    obs = setup_l7(g)
    print(f"L7 init: level_idx={g.env._game._current_level_index}, state={obs.state.name}")

    pix_init = np.array(obs.frame[-1], dtype=np.int16)
    render_png(pix_init, label='L7 init').save(out_dir / 'L7_init.png')
    print(f"Saved L7_init.png; pix shape={pix_init.shape}")

    # Snapshot
    snap = copy.deepcopy(g.env._game)
    ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)

    # Try ACTION1 + render
    g.env._game = copy.deepcopy(snap)
    obs = g.env.step(GameAction.ACTION1)
    pix = np.array(obs.frame[-1], dtype=np.int16)
    render_png(pix, label='L7 +A1').save(out_dir / 'L7_A1.png')
    print(f"Saved L7_A1.png")

    # Click on piece (0, 1)
    g.env._game = copy.deepcopy(snap)
    obs = g.env.step(GameAction.ACTION6, data={'x': 0*6+3+ox, 'y': 1*6+3+oy})
    pix = np.array(obs.frame[-1], dtype=np.int16)
    render_png(pix, label='L7 click(0,1)').save(out_dir / 'L7_click_0_1.png')
    print(f"Saved L7_click_0_1.png")

    # Click on piece (6, 1) red
    g.env._game = copy.deepcopy(snap)
    obs = g.env.step(GameAction.ACTION6, data={'x': 6*6+3+ox, 'y': 1*6+3+oy})
    pix = np.array(obs.frame[-1], dtype=np.int16)
    render_png(pix, label='L7 click(6,1) red').save(out_dir / 'L7_click_6_1.png')
    print(f"Saved L7_click_6_1.png")

    # Click on piece (22, 6)
    g.env._game = copy.deepcopy(snap)
    obs = g.env.step(GameAction.ACTION6, data={'x': 22*6+3+ox, 'y': 6*6+3+oy})
    pix = np.array(obs.frame[-1], dtype=np.int16)
    render_png(pix, label='L7 click(22,6)').save(out_dir / 'L7_click_22_6.png')
    print(f"Saved L7_click_22_6.png")


if __name__ == '__main__':
    main()
