"""Query engine for valid clicks at L7 init and after each A-action."""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
sys.path.insert(0, '/Users/kairos/Projects/arc-see/solutions')

import copy, hashlib
import numpy as np
from lf52_tool import LF52
from arcengine import GameAction
import solution_lf52_l5 as L5
import solution_lf52_l6 as L6


def setup_l7(g):
    g.env._game.set_level(4)
    g.env._game.on_set_level(g.env._game.current_level)
    obs = g.env.step(GameAction.ACTION6, data={'x': 0, 'y': 0})
    for step in L5.SOLUTION:
        if isinstance(step, str):
            obs = g.env.step(getattr(GameAction, f'ACTION{int(step[1:])}'))
        else:
            kind, src, direction = step
            ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
            sx, sy = src; dx, dy = direction
            obs = g.env.step(GameAction.ACTION6, data={'x': sx*6+3+ox, 'y': sy*6+3+oy})
            ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
            obs = g.env.step(GameAction.ACTION6, data={'x': (sx+2*dx)*6+3+ox, 'y': (sy+2*dy)*6+3+oy})
    for step in L6.parse_solution():
        if step[0] == 'A':
            obs = g.env.step(getattr(GameAction, f'ACTION{step[1]}'))
        else:
            _, (sx, sy), (dx, dy) = step
            ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
            obs = g.env.step(GameAction.ACTION6, data={'x': sx*6+3+ox, 'y': sy*6+3+oy})
            ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
            obs = g.env.step(GameAction.ACTION6, data={'x': (sx+2*dx)*6+3+ox, 'y': (sy+2*dy)*6+3+oy})
    return obs


def frame_hash(pix):
    return hashlib.md5(np.array(pix, dtype=np.int16).tobytes()).hexdigest()[:10]


def try_brute_clicks(g, obs_init):
    """Scan ALL world pixel coords and find ones that change the frame."""
    pix_init = np.array(obs_init.frame[-1], dtype=np.int16)
    h_init = frame_hash(pix_init)
    snap = copy.deepcopy(g.env._game)
    changed = []
    # World pixels are 0..~180 x 0..~90, since viewport shows 64×64
    # but world can extend up to ~24 tiles = 144 pixels
    for py in range(0, 90, 3):
        for px in range(0, 180, 3):
            g.env._game = copy.deepcopy(snap)
            try:
                obs = g.env.step(GameAction.ACTION6, data={'x': px, 'y': py})
            except Exception:
                continue
            pix = np.array(obs.frame[-1], dtype=np.int16)
            h = frame_hash(pix)
            if h != h_init:
                changed.append((px, py, h))
    return changed


def main():
    print("Setting up L7...")
    g = LF52(up_to_level=1, verbose=False)
    obs = setup_l7(g)
    print(f"L7 init: idx={g.env._game._current_level_index}")
    print(f"init frame hash: {frame_hash(obs.frame[-1])}")

    # Also scan state after each A-action
    snap = copy.deepcopy(g.env._game)
    for action_seq_name, acts in [
        ('init', []),
        ('A1', [1]),
        ('A2', [2]),
        ('A3', [3]),
        ('A4', [4]),
        ('A1A1', [1, 1]),
        ('A3A1', [3, 1]),
        ('A4A4', [4, 4]),
    ]:
        g.env._game = copy.deepcopy(snap)
        cur_obs = obs
        for a in acts:
            cur_obs = g.env.step(getattr(GameAction, f'ACTION{a}'))
        print(f"\n--- State: {action_seq_name} (frame_hash={frame_hash(cur_obs.frame[-1])}) ---")
        changed = try_brute_clicks(g, cur_obs)
        from collections import defaultdict
        by_hash = defaultdict(list)
        h_base = frame_hash(cur_obs.frame[-1])
        for px, py, h in changed:
            by_hash[h].append((px, py))
        print(f"  Clicks changing frame: {len(changed)}, unique post-states: {len(by_hash)}")
        for h, coords in list(by_hash.items())[:5]:
            # Reduce to tile clusters
            tiles = sorted(set((px // 6, py // 6) for px, py in coords))
            print(f"    hash={h}: {len(coords)} clicks, tiles={tiles[:10]}{'...' if len(tiles)>10 else ''}")


if __name__ == '__main__':
    main()
