"""Advance to L8, dump sprites/targets."""
import importlib.util, sys
sys.path.insert(0, '.')
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('re86', 'environment_files/re86/4e57566e/re86.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
sol_spec = importlib.util.spec_from_file_location('sol_re86', 'solutions/solution_re86.py')
sol = importlib.util.module_from_spec(sol_spec)
sol_spec.loader.exec_module(sol)

g = mod.Re86()
g.set_level(0)
for lvl in range(1, 8):
    for a in sol.SOLUTIONS[lvl]:
        g.perform_action(ActionInput(id=getattr(GameAction, a)))

print(f'State: {g._state.name}, level_idx: {g._current_level_index}')
level = g._levels[g._current_level_index]

print('\n=== L8 PLAYER SPRITES (vfaeucgcyr) ===')
for i, s in enumerate(level._sprites):
    if 'vfaeucgcyr' not in s._tags: continue
    px = s.pixels
    tags = s._tags
    colors = sorted(set(int(c) for c in px.flatten() if c != -1 and c != 0))
    active = 0 in px
    print(f'\nSprite {i} ({s._name}) {"[ACTIVE]" if active else ""} tags={tags} pos=({s._x},{s._y}) size={s.width}x{s.height} colors={colors}')
    for row in px:
        print('  ' + ''.join('.' if c == -1 else f'{int(c):2d}'[-1] for c in row))

print('\n=== SWATCHES (ozhohpbjxz) ===')
for i, s in enumerate(level._sprites):
    if 'ozhohpbjxz' in s._tags:
        colors = sorted(set(int(c) for c in s.pixels.flatten() if c != 2 and c != -1))
        print(f'  Swatch {i} at ({s._x},{s._y}) size={s.width}x{s.height} color={colors}')

print('\n=== MORPH TRIGGERS (miqpqafylc) ===')
for i, s in enumerate(level._sprites):
    if 'miqpqafylc' in s._tags:
        print(f'  Trigger {i} at ({s._x},{s._y}) size={s.width}x{s.height}')

print('\n=== BACKGROUND TARGETS ===')
bg = None
for s in level._sprites:
    if 'vzuwsebntu' in s._tags:
        bg = s.pixels
        break
targets = {}
for y in range(bg.shape[0]):
    for x in range(bg.shape[1]):
        c = int(bg[y, x])
        if c == -1 or c == 4: continue
        targets.setdefault(c, []).append((x, y))
for c, pts in sorted(targets.items()):
    print(f'  color {c}: {len(pts)} targets: {pts}')
