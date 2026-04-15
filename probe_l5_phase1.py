"""L5 Phase I: move v2 to (4,3), chain pieces, load v1 at (7,3), consume (6,3).

Sequence:
1. A3 A3 A2 A2 A2 → v2 to (4, 3) [Track #0 col 4]
2. Chain piece (1, 3) R → (3, 3) [using f-pivot (2, 3)]
3. Move v1 to (7, 3). Path: col 4 down past v2 is blocked; try col 4/row 6/col 7 route.
   First move v1 right & down via A4 A4 A2 but careful of v2 blocks.
4. Chain (3, 3) R → (5, 3) [using v2's dgx at (4, 3) as pivot]
5. Chain (5, 3) R → (7, 3) [using piece (6, 3) as pivot — CONSUMES it, loads v1]
"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')

from lf52_tool import LF52, render_png
from arcengine import GameAction
import numpy as np
import copy

def setup_l5():
    g = LF52(up_to_level=1, verbose=False)
    g.env._game.set_level(4)
    g.env._game.on_set_level(g.env._game.current_level)
    g.env.step(GameAction.ACTION6, data={'x': 0, 'y': 0})
    return g

def panel_offset(g):
    return tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)

def click_grid(g, gx, gy):
    ox, oy = panel_offset(g)
    return g.env.step(GameAction.ACTION6, data={'x': gx * 6 + 3 + ox, 'y': gy * 6 + 3 + oy})

def do_chain(g, src, direction):
    sx, sy = src
    dx, dy = direction
    click_grid(g, sx, sy)
    return click_grid(g, sx + 2*dx, sy + 2*dy)

def foz_count(g):
    return sum(1 for item in g.env._game.ikhhdzfmarl._sorted_cache if getattr(item[1], 'name', '') == 'fozwvlovdui')

def piece_positions(g):
    return sorted([(s.grid_x, s.grid_y) for item in g.env._game.ikhhdzfmarl._sorted_cache for _,s,_ in [item] if getattr(s, 'name', '') == 'fozwvlovdui'])

def vehicle_positions(g):
    return sorted([(s.grid_x, s.grid_y) for item in g.env._game.ikhhdzfmarl._sorted_cache for _,s,_ in [item] if getattr(s, 'name', '') == 'hupkpseyuim2'])

def pivot_positions(g):
    return sorted([(s.grid_x, s.grid_y) for item in g.env._game.ikhhdzfmarl._sorted_cache for _,s,_ in [item] if getattr(s, 'name', '') == 'dgxfozncuiz'])

def state_snap(g):
    return f'foz={foz_count(g)}, pieces={piece_positions(g)}, vehicles={vehicle_positions(g)}, pivots={pivot_positions(g)}, panel_offset={panel_offset(g)}'

g = setup_l5()
print('INIT:', state_snap(g))

# Phase I step 1: Get v2 to (4, 3) — route v1 to (7, 3) first via col 4 → row 6 → col 7
# Actually v1 needs to descend col 4 BEFORE v2 does, otherwise v2 blocks.
# Plan: A4×2 (v1 to (4,0) T), then A2×6 (v1 descends col 4 to (4,6) t), then A4×3 (v1 along row 6 to (7,6)), then A1×3 (v1 up col 7 to (7,3))
print('\n--- Moving v1 to (7, 3) ---')
for a in [4, 4]:
    g.env.step(getattr(GameAction, f'ACTION{a}'))
print(f'After A4×2: {state_snap(g)}')

for a in [2, 2, 2, 2, 2, 2]:
    g.env.step(getattr(GameAction, f'ACTION{a}'))
print(f'After A2×6: {state_snap(g)}')

for a in [4, 4, 4]:
    g.env.step(getattr(GameAction, f'ACTION{a}'))
print(f'After A4×3: {state_snap(g)}')

for a in [1, 1, 1]:
    g.env.step(getattr(GameAction, f'ACTION{a}'))
print(f'After A1×3: {state_snap(g)}')

# Now v1 should be at (7, 3). Next, move v2 to (4, 3)
# v2 should be at (7, 0) currently. Drive v2 left via A3, but that blocks if v1 at (6, 0 or 7, 3).
# v1 at (7, 3) — A3 target (6, 3) panel blocked. So A3 doesn't move v1.
# v2 at (7, 0) — A3 target (6, 0) track. Moves.
# v3 at (20, 2)? — A3 target (19, 2) empty blocked.
for a in [3, 3, 3]:
    g.env.step(getattr(GameAction, f'ACTION{a}'))
print(f'After A3×3: {state_snap(g)}')

# Now v2 at (4, 0). Descend col 4 to (4, 3) via A2×3.
# But A2 will move v1 too (from (7, 3) to (7, 4)).
# HMMMM problem. Let me see if v1 can be blocked vertically.
# Actually if v1 at (7, 3), (7, 4) is track. A2 moves v1 to (7, 4).
# So v1 leaves (7, 3).

# Alternative plan:
# Maybe we can do the chain before moving v2 via A2.
# But we need v2 at (4, 3) for the chain to work. And v1 at (7, 3).

# Let me check current state
print()
print('Testing chain (1, 3) R:')
snap = copy.deepcopy(g.env._game)
do_chain(g, (1, 3), (1, 0))
print(f'After chain: {state_snap(g)}')
g.env._game = copy.deepcopy(snap)

# Alternative: move v2 first, then v1 goes around.
# Need v2 at (4, 3) and v1 at (7, 3). Both need vertical moves.
# Hmm. Let me trace more carefully.
