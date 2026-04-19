"""Run L5 + L6 solutions properly, then probe L7 state."""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')

import copy, hashlib
import numpy as np
from lf52_tool import LF52
from arcengine import GameAction

# Import the solutions as modules
sys.path.insert(0, '/Users/kairos/Projects/arc-see/solutions')
import solution_lf52_l5 as L5
import solution_lf52_l6 as L6


def state_hash(g):
    """Hash game state by sprite list + viewport origin + level. No obs required."""
    sprites = []
    cache = g.env._game.ikhhdzfmarl._sorted_cache
    for item in cache:
        s = item[1]
        nm = getattr(s, 'name', '')
        if not nm:
            continue
        x, y = getattr(s, 'x', -999), getattr(s, 'y', -999)
        sprites.append((nm, x, y))
    sprites.sort()
    ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
    idx = g.env._game._current_level_index
    rep = repr((sprites, ox, oy, idx))
    return hashlib.md5(rep.encode()).hexdigest()[:10]


def foz_count(g):
    cache = g.env._game.ikhhdzfmarl._sorted_cache
    total = 0
    for item in cache:
        for part in item:
            if hasattr(part, 'name') and isinstance(part.name, str) and part.name.startswith('fozwvlovdui'):
                total += 1
                break
    return total


def named_sprites(g):
    cache = g.env._game.ikhhdzfmarl._sorted_cache
    out = []
    for item in cache:
        s = item[1]
        nm = getattr(s, 'name', '')
        if not nm:
            continue
        x, y = getattr(s, 'x', -999), getattr(s, 'y', -999)
        out.append((nm, x // 6, y // 6))
    return sorted(out)


def run_l5_steps(g):
    for step in L5.SOLUTION:
        if isinstance(step, str):
            a = int(step[1:])
            g.env.step(getattr(GameAction, f'ACTION{a}'))
        else:
            kind, src, direction = step
            ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
            sx, sy = src
            dx, dy = direction
            g.env.step(GameAction.ACTION6, data={'x': sx*6+3+ox, 'y': sy*6+3+oy})
            ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
            g.env.step(GameAction.ACTION6, data={'x': (sx+2*dx)*6+3+ox, 'y': (sy+2*dy)*6+3+oy})


def run_l6_steps(g):
    steps = L6.parse_solution()
    for step in steps:
        if step[0] == 'A':
            a = step[1]
            g.env.step(getattr(GameAction, f'ACTION{a}'))
        else:
            _, (sx, sy), (dx, dy) = step
            ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
            g.env.step(GameAction.ACTION6, data={'x': sx*6+3+ox, 'y': sy*6+3+oy})
            ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
            g.env.step(GameAction.ACTION6, data={'x': (sx+2*dx)*6+3+ox, 'y': (sy+2*dy)*6+3+oy})


def main():
    print("Init LF52...")
    g = LF52(up_to_level=1, verbose=False)
    # Skip to L5
    g.env._game.set_level(4)
    g.env._game.on_set_level(g.env._game.current_level)
    g.env.step(GameAction.ACTION6, data={'x': 0, 'y': 0})
    print(f"L5 init: idx={g.env._game._current_level_index}, foz={foz_count(g)}, hash={state_hash(g)}")

    print("\nRunning L5 solution...")
    run_l5_steps(g)
    print(f"After L5: idx={g.env._game._current_level_index}, foz={foz_count(g)}, hash={state_hash(g)}")

    print("\nRunning L6 solution...")
    run_l6_steps(g)
    print(f"After L6: idx={g.env._game._current_level_index}, foz={foz_count(g)}, hash={state_hash(g)}")

    # Probe L7
    print("\n=== L7 INIT (after legit wins) ===")
    ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
    print(f"viewport origin: ({ox}, {oy})")
    sprites = named_sprites(g)
    pieces = [s for s in sprites if s[0].startswith('fozwvlovdui')]
    vehicles = [s for s in sprites if s[0].startswith('hupkpseyuim2')]
    panels = [s for s in sprites if s[0] == 'hupkpseyuim']
    dgx = [s for s in sprites if s[0].startswith('dgxfozncuiz')]
    tracks = [s for s in sprites if s[0].startswith('kraubslpehi')]
    print(f"pieces={len(pieces)}: {pieces}")
    print(f"vehicles={len(vehicles)}: {vehicles}")
    print(f"panels={len(panels)}")
    for p in panels:
        print(f"  {p}")
    print(f"dgx={len(dgx)}: {dgx}")
    print(f"tracks={len(tracks)}")

    # Test actions
    init_snap = copy.deepcopy(g.env._game)
    init_hash = state_hash(g)
    print("\n=== Actions 1-4 at L7 init ===")
    for a in [1, 2, 3, 4]:
        g.env._game = copy.deepcopy(init_snap)
        try:
            g.env.step(getattr(GameAction, f'ACTION{a}'))
        except Exception as e:
            print(f"ACTION{a}: ERROR {e}")
            continue
        h = state_hash(g)
        if h != init_hash:
            new_sprites = named_sprites(g)
            new_vs = [s for s in new_sprites if s[0].startswith('hupkpseyuim2')]
            print(f"ACTION{a}: hash={h}, vehicles={new_vs}")
        else:
            print(f"ACTION{a}: NO CHANGE")

    # Click directly on piece positions with origin offset (5, 5)
    print("\n=== Clicks on pieces, WITH origin offset (5, 5) ===")
    ox, oy = 5, 5
    for tx, ty in [(0, 1), (6, 1), (22, 6), (5, 5), (14, 2)]:
        g.env._game = copy.deepcopy(init_snap)
        px, py = tx * 6 + 3 + ox, ty * 6 + 3 + oy
        try:
            obs = g.env.step(GameAction.ACTION6, data={'x': px, 'y': py})
        except Exception as e:
            print(f"click tile({tx},{ty}) @ pix({px},{py}): ERROR {e}")
            continue
        h = state_hash(g)
        # Also hash frame
        frame_h = hashlib.md5(np.array(obs.frame[-1], dtype=np.int16).tobytes()).hexdigest()[:10]
        print(f"click tile({tx},{ty}) @ pix({px},{py}): sprite_hash={h} frame_hash={frame_h}")


if __name__ == '__main__':
    main()
