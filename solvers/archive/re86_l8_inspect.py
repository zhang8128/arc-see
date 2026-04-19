"""Inspect the morphed frame patterns — does 16x10 actually cover 4 corners?"""
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
        print('  ' + ''.join('.' if c == -1 else f'{int(c):2d}'[-1] for c in row))


# Start L8 and trigger a morph
g = new_game_at_l8()
s = active_sprite(g)
show(s, 'L8 start')

# Morph trigger at (34, 55). Frame A at (45, 42). Move frame to overlap trigger.
# Trigger 5x5 at (34..38, 55..59). Frame bbox (45..57, 42..54). No overlap initially.
# Move LEFT to get x=34, DOWN to y=51.
# Move DOWN first: y=42 → y=51 (3 DOWN moves) → frame (45..57, 51..63). Overlap trigger rows 55..59 ✓. Cols 45..57 vs trigger 34..38 — NO col overlap.
# Move LEFT: x=45 → x=36 (3 LEFT) → frame (36..48, ?, ?).
# Then check if morph happens.

print('\n--- Move toward trigger 1 (34, 55) ---')
for _ in range(3): g.perform_action(ActionInput(id=GameAction.ACTION2))  # DOWN
for _ in range(3): g.perform_action(ActionInput(id=GameAction.ACTION3))  # LEFT
s = active_sprite(g)
show(s, 'moved 3D 3L')

print('\n--- Continue LEFT to enter trigger pixel overlap ---')
for i in range(6):
    prev = (s._x, s._y, s.width, s.height)
    g.perform_action(ActionInput(id=GameAction.ACTION3))
    s = active_sprite(g)
    cur = (s._x, s._y, s.width, s.height)
    print(f'L{i+1}: {prev} → {cur}')
    if cur[2:] != prev[2:]:  # dimension change
        show(s, f'morphed L{i+1}')
