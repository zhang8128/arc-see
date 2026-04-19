"""Advance to L7 using verified solutions, then dump sprite/swatch/target state.

Uses the game engine as a black-box simulator: load module, perform actions,
read live state. Does NOT parse level data from source code.
"""
import importlib.util, sys, json
sys.path.insert(0, '.')
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('re86', 'environment_files/re86/4e57566e/re86.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# Load verified solutions
solutions_mod = importlib.util.spec_from_file_location('sol_re86', 'solutions/solution_re86.py')
sol = importlib.util.module_from_spec(solutions_mod)
solutions_mod.loader.exec_module(sol)

g = mod.Re86()
g.set_level(0)

# Advance to L7
for lvl in range(1, 7):
    for a in sol.SOLUTIONS[lvl]:
        g.perform_action(ActionInput(id=getattr(GameAction, a)))

print(f'State: {g._state.name}, level_idx: {g._current_level_index}')

import numpy as np
level = g._levels[6]

# Full dump of player sprites and background target positions
print('\n=== PLAYER SPRITES (vfaeucgcyr) ===')
for i, s in enumerate(level._sprites):
    if 'vfaeucgcyr' not in s._tags: continue
    px = s.pixels
    tags = s._tags
    colors = sorted(set(int(c) for c in px.flatten() if c != -1))
    print(f'\nSprite {i} ({s._name}) tags={tags} pos=({s._x},{s._y}) size={s.width}x{s.height} colors={colors}')
    # Print full pattern
    for row in px:
        print('  ' + ''.join('.' if c == -1 else f'{int(c):2d}'[-1] for c in row))

print('\n=== BACKGROUND TARGETS ===')
bg = None
for s in level._sprites:
    if 'vzuwsebntu' in s._tags:
        bg = s.pixels
        break
# Find all non-transparent, non-4 positions
targets = {}
for y in range(bg.shape[0]):
    for x in range(bg.shape[1]):
        c = int(bg[y, x])
        if c == -1 or c == 4: continue
        targets.setdefault(c, []).append((x, y))
for c, pts in sorted(targets.items()):
    print(f'  color {c}: {len(pts)} pts: {pts}')

print('\n=== SWATCHES ===')
for i, s in enumerate(level._sprites):
    if 'ozhohpbjxz' in s._tags:
        px = s.pixels
        colors = sorted(set(int(c) for c in px.flatten() if c != 2 and c != -1))
        print(f'  Swatch {i} at ({s._x},{s._y}) size={s.width}x{s.height} fill_color={colors}')

print('\n=== MORPH TRIGGER ===')
for i, s in enumerate(level._sprites):
    if 'miqpqafylc' in s._tags:
        px = s.pixels
        print(f'  Trigger {i} at ({s._x},{s._y}) size={s.width}x{s.height}')
        for row in px:
            print('  ' + ''.join('.' if c == -1 else f'{int(c):2d}'[-1] for c in row))
