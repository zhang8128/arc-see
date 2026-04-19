"""Full verified L7 chain sequence as of 2026-04-18.

Run: uv run python l7_full.py
Gets to chain 8, then prints state for exploration.
"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')

from lf52_tool import LF52, render_png
import numpy as np

# Verified sequence (chains 1-8)
SEQUENCE = [
    # Chain 1: load tan
    ('actions', [3, 3, 1, 1, 3, 3, 3]),
    ('click', (6, 12)), ('click', (6, 24)),
    # Chain 2: deliver tan → slot 1 (world (6,48))
    ('actions', [4, 4, 4, 2, 2, 3, 3, 2]),
    ('click', (13, 44)), ('click', (13, 55)),
    # Load lightblue
    ('actions', [1, 4, 4, 1, 1, 4, 4, 4]),
    ('click', (42, 12)), ('click', (42, 24)),
    # Deliver lb → slot 6 (world (36,48))
    ('actions', [3, 3, 3, 2, 2, 4, 4, 4, 2]),
    ('click', (43, 44)), ('click', (43, 55)),
    # Return to (10, 41) for queue swaps
    ('actions', [1, 3, 3, 3, 1, 1, 3, 3, 3, 4, 4, 4, 2, 2, 3, 3, 3, 2]),
    # Chain 3: tan 1→3 via teal pivot at slot 2
    ('click', (13, 55)), ('click', (25, 55)),
    # Chain 4: tan 3→5 via teal pivot at slot 4
    ('click', (25, 55)), ('click', (37, 55)),
    # Chain 5: tan 5→7 via lb at slot 6
    ('click', (37, 55)), ('click', (47, 55)),
    # Chain 6: lb 6→8 via tan at slot 7 — TRIGGERS VIEWPORT SCROLL
    ('click', (43, 55)), ('click', (55, 55)),
    # Chain 7: tan fwd in post-scroll viewport
    ('click', (5, 55)), ('click', (17, 55)),
    # Chain 8: drive to (20,53), chain lb into vehicle
    ('actions', [2, 3, 2, 2, 4, 4, 2]),
    ('click', (11, 55)), ('click', (23, 55)),
]


def run():
    g = LF52(up_to_level=7, verbose=False)
    for kind, val in SEQUENCE:
        if kind == 'actions':
            for a in val:
                g.action(a)
        elif kind == 'click':
            g.click(*val)
    print(f'Level: {g.level()}, State: {g.state_name()}')
    print(f'Viewport: {tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)}')
    # Piece positions
    ik = g.env._game.ikhhdzfmarl
    for name, obj in ik.khosdevozr.items():
        pos = getattr(obj, 'cdpcbbnfdp', None)
        print(f'{name}: pos={list(pos)}')
    render_png(g.pixels(), label='chain8 final').save('/tmp/l7_chain8_final.png')
    return g


if __name__ == '__main__':
    run()
