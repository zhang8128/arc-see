"""Probe morph trigger — cross actually aligned to pass through."""
import importlib.util, sys
sys.path.insert(0, '.')
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('re86', 'environment_files/re86/4e57566e/re86.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
sol_spec = importlib.util.spec_from_file_location('sol_re86', 'solutions/solution_re86.py')
sol = importlib.util.module_from_spec(sol_spec)
sol_spec.loader.exec_module(sol)


def new_game_at_l7():
    g = mod.Re86()
    g.set_level(0)
    for lvl in range(1, 7):
        for a in sol.SOLUTIONS[lvl]:
            g.perform_action(ActionInput(id=getattr(GameAction, a)))
    return g


def act(g, a):
    g.perform_action(ActionInput(id=getattr(GameAction, a)))


def players(g):
    lvl = g._levels[g._current_level_index]
    return [s for s in lvl._sprites if 'vfaeucgcyr' in s._tags]


def active_sprite(g):
    for s in players(g):
        if 0 in s.pixels:
            return s
    return None


def show(s, label=''):
    print(f'[{label}] {s._name} pos=({s._x},{s._y}) size={s.width}x{s.height}')
    for row in s.pixels:
        print('  ' + ''.join('.' if c == -1 else f'{int(c):2d}'[-1] for c in row))


def step_track(g, a, label):
    prev = active_sprite(g)
    prev_px = prev.pixels.copy()
    prev_pos = (prev._x, prev._y); prev_dim = (prev.width, prev.height)
    act(g, a)
    s = active_sprite(g)
    pos = (s._x, s._y); dim = (s.width, s.height)
    note = []
    if pos == prev_pos and a != 'ACTION5': note.append('BLOCKED')
    if dim != prev_dim: note.append(f'DIM {prev_dim}→{dim}')
    if s.pixels.shape == prev_px.shape:
        if not (s.pixels == prev_px).all():
            note.append('pixels-changed')
    else:
        note.append('shape-changed')
    print(f'{label}: {a} pos={pos} size={dim} {" ".join(note)}')
    if any('changed' in n or 'DIM' in n for n in note):
        show(s, label)
    return s


# Start: P1 cross at (3,39), need cross vertical arm (col 9 in pattern) at world col 30 → x=21
# So move RIGHT 6 times (3 → 21).
g = new_game_at_l7()
print('=== START: move RIGHT to align vertical arm with trigger col ===')
for i in range(6):
    step_track(g, 'ACTION4', f'R{i+1}')

# Now move UP. Cross center_y = y+9. Start y=39 → center_y=48. Trigger y 28..35.
# At y=24: pattern row 9 (horiz arm) at world row 33, in trigger range.
print('\n=== Now UP, watching for trigger interaction ===')
for i in range(10):
    s = step_track(g, 'ACTION1', f'U{i+1}')
    if s is None: break
