"""Scroll viewport with A3/A4 to map out the full L4 world."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from lf52_tool import LF52, render_png
import numpy as np


def main():
    g = LF52(up_to_level=4, verbose=False)
    base_pix = g.pixels()
    render_png(base_pix, label='init').save('/tmp/lf52_frames/world_00_init.png')

    # Camera inspection
    renderer = g.env._game.ikhhdzfmarl
    camera = renderer.camera
    print('Camera attrs:')
    for attr in dir(camera):
        if attr.startswith('__'): continue
        try:
            v = getattr(camera, attr)
            if callable(v): continue
            t = type(v).__name__
            val = repr(v)[:80]
            print(f'  {attr}: {t} = {val}')
        except Exception as e:
            pass

    # Scroll A3 multiple times to see what's revealed
    for i in range(1, 10):
        g.action(3)
        renderer = g.env._game.ikhhdzfmarl
        cam = renderer.camera
        pix = g.pixels()
        render_png(pix, label=f'A3x{i}').save(f'/tmp/lf52_frames/world_A3x{i}.png')
        print(f'A3x{i}: 7-count={int((pix==7).sum())} e-count={int((pix==14).sum())}')

    # Reset and try A4 several times
    g2 = LF52(up_to_level=4, verbose=False)
    for i in range(1, 10):
        g2.action(4)
        pix = g2.pixels()
        render_png(pix, label=f'A4x{i}').save(f'/tmp/lf52_frames/world_A4x{i}.png')
        e_count = int((pix == 14).sum())
        f_count = int((pix == 15).sum())
        seven_count = int((pix == 7).sum())
        print(f'A4x{i}: e={e_count} f={f_count} 7={seven_count}')

    # Also test A1, A2
    print()
    print('=== A1 then A2 tests ===')
    for seq_name, seq in [('A1', [1]), ('A2', [2]), ('A1x3', [1, 1, 1]), ('A2x3', [2, 2, 2])]:
        g3 = LF52(up_to_level=4, verbose=False)
        for a in seq:
            g3.action(a)
        pix = g3.pixels()
        diff = int((base_pix != pix).sum())
        print(f'  {seq_name}: diff={diff}')

    # Also try all combos A3/A4 to find edges of accessible world
    print()
    print('=== A3+A4 combinations ===')
    g4 = LF52(up_to_level=4, verbose=False)
    for i in range(5):
        g4.action(4)
    # Now viewport is scrolled right. Try A2 (maybe now it works?) or A1
    pix0 = g4.pixels()
    for a in [1, 2]:
        import copy
        snap = copy.deepcopy(g4.env._game)
        obs_snap = copy.deepcopy(g4.obs)
        g4.action(a)
        diff = int((pix0 != g4.pixels()).sum())
        print(f'After A4x5 + A{a}: diff={diff}')
        g4.env._game = snap
        g4.obs = obs_snap
        g4._cached_frame = None


if __name__ == '__main__':
    main()
