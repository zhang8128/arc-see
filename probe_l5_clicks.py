"""Probe which clicks produce hints at L5 init — to find what's actually interactive."""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')

from lf52_tool import LF52, render_png
from arcengine import GameAction
import numpy as np
from collections import defaultdict
import copy

def get_foz_count(g):
    sm = defaultdict(int)
    for item in g.env._game.ikhhdzfmarl._sorted_cache:
        _, sp, _ = item
        sm[getattr(sp, 'name', '')] += 1
    return sm.get('fozwvlovdui', 0)

def get_all_sprites(g):
    """Dict mapping sprite-name → list of (x, y)."""
    sm = defaultdict(list)
    for item in g.env._game.ikhhdzfmarl._sorted_cache:
        _, sp, _ = item
        sm[getattr(sp, 'name', '')].append((sp.x, sp.y))
    return dict(sm)

def get_pixels(g):
    """Get current 64×64 viewport pixels."""
    obs = g.env.step(GameAction.ACTION6, data={'x': 0, 'y': 0})
    return np.array(obs.frame[-1], dtype=np.int16).copy()

def setup_l5():
    g = LF52(up_to_level=1, verbose=False)
    g.env._game.set_level(4)
    g.env._game.on_set_level(g.env._game.current_level)
    g.env.step(GameAction.ACTION6, data={'x': 0, 'y': 0})
    return g

def snapshot(g):
    return copy.deepcopy(g.env._game)

def restore(g, snap):
    g.env._game = copy.deepcopy(snap)

def main():
    g = setup_l5()
    init_snap = snapshot(g)
    init_pix = get_pixels(g)
    init_sprites = get_all_sprites(g)

    print('=== L5 initial state ===')
    print(f'Foz count (pieces): {get_foz_count(g)}')
    print(f'Piece positions: {init_sprites["fozwvlovdui"]}')
    print(f'F-pivot positions: {init_sprites["dgxfozncuiz"]}')
    print(f'Vehicle positions: {init_sprites["hupkpseyuim2"]}')

    # Probe each viewport position — which produces hints (color 2 pixels)?
    print('\n=== Probing clicks ===')
    results = []
    for y in range(0, 64, 1):
        for x in range(0, 64, 1):
            restore(g, init_snap)
            try:
                obs = g.env.step(GameAction.ACTION6, data={'x': x, 'y': y})
                pix = np.array(obs.frame[-1], dtype=np.int16)
                # Count pixel changes from init
                diff = int(np.sum(pix != init_pix))
                if diff > 0:
                    # Check for hint cells (color 2 = red hints)
                    hints = int(np.sum((pix == 2) & (init_pix != 2)))
                    results.append((diff, hints, x, y))
            except Exception as e:
                pass

    # Show top interesting clicks
    results.sort(key=lambda r: -r[1])  # sort by hint count desc
    print(f'Total clicks with any pixel change: {len(results)}')
    print(f'Top 20 clicks by hint-pixel count:')
    for diff, hints, x, y in results[:20]:
        print(f'  ({x:2d}, {y:2d}): diff={diff:4d} hints={hints:3d}')

    # Try A-actions
    print('\n=== Probing A-actions ===')
    for a in [1, 2, 3, 4, 5, 7]:
        restore(g, init_snap)
        try:
            obs = g.env.step(getattr(GameAction, f'ACTION{a}'))
            pix = np.array(obs.frame[-1], dtype=np.int16)
            diff = int(np.sum(pix != init_pix))
            foz = get_foz_count(g)
            print(f'  A{a}: diff={diff}, foz_count={foz}, state={obs.state.name}')
        except Exception as e:
            print(f'  A{a}: exception {e}')

if __name__ == '__main__':
    main()
