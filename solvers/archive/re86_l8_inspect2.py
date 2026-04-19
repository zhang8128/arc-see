"""Force a UD morph to get 16x10 shape and inspect it."""
import importlib.util, sys, copy
sys.path.insert(0, '.')
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('re86', 'environment_files/re86/4e57566e/re86.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
sol_spec = importlib.util.spec_from_file_location('sol_re86', 'solutions/solution_re86.py')
sol = importlib.util.module_from_spec(sol_spec)
sol_spec.loader.exec_module(sol)


def new_game_at_l8():
    g = mod.Re86()
    g.set_level(0)
    for lvl in range(1, 8):
        for a in sol.SOLUTIONS[lvl]:
            g.perform_action(ActionInput(id=getattr(GameAction, a)))
    return g


def players(g):
    lvl = g._levels[g._current_level_index]
    return [s for s in lvl._sprites if 'vfaeucgcyr' in s._tags]


def active_sprite(g):
    for s in players(g):
        if 0 in s.pixels: return s


def show(s, label=''):
    print(f'[{label}] {s._name} pos=({s._x},{s._y}) {s.width}x{s.height}')
    for row in s.pixels:
        # Print with 2-digit codes
        print('  ' + ''.join('..' if c == -1 else f'{int(c):2d}' for c in row))


# Get the frame near trigger 1 at (34, 55) and approach with UD motion
g = new_game_at_l8()
# Move to (34, 42) — at y=42 with x=34: sprite cols 34..46 overlap trigger cols 34..38 ✓.
# Then UP or DOWN to create UD morph. Frame (34, 42)..(46, 54). Trigger (34..38, 55..59).
# No y overlap yet. Move DOWN.
for _ in range(4): g.perform_action(ActionInput(id=GameAction.ACTION3))  # 4L: 45->33 (wait, start 45 → 45-12=33)
s = active_sprite(g)
print(f'after 4L: pos=({s._x},{s._y}) size={s.width}x{s.height}')

# Now DOWN
for i in range(8):
    prev = (s._x, s._y, s.width, s.height)
    g.perform_action(ActionInput(id=GameAction.ACTION2))
    s = active_sprite(g)
    cur = (s._x, s._y, s.width, s.height)
    print(f'D{i+1}: {prev} → {cur}')
    if cur[2:] != prev[2:]:
        show(s, f'morphed D{i+1}')
        break

# Once 16x10, inspect pattern
s = active_sprite(g)
if s.width == 16 and s.height == 10:
    show(s, '16x10 current')
    print('\nCorner cells:')
    print(f'  TL (0,0) = {int(s.pixels[0, 0])}')
    print(f'  TR (0, w-1) = {int(s.pixels[0, s.width-1])}')
    print(f'  BL (h-1, 0) = {int(s.pixels[s.height-1, 0])}')
    print(f'  BR (h-1, w-1) = {int(s.pixels[s.height-1, s.width-1])}')
