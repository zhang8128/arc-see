"""Probe all arm shift mechanics: UP/DOWN/LEFT/RIGHT when blocked."""
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
    print(f'[{label}] pos=({s._x},{s._y}) size={s.width}x{s.height}')
    for row in s.pixels:
        print('  ' + ''.join('.' if c == -1 else f'{int(c):2d}'[-1] for c in row))


def arm_positions(s):
    """Find horiz arm row and vert arm col in pattern."""
    import numpy as np
    px = s.pixels
    # Row with most non-(-1) pixels = horizontal arm row
    row_counts = [sum(1 for c in row if c != -1) for row in px]
    h_row = row_counts.index(max(row_counts))
    col_counts = [sum(1 for row in px if row[c] != -1) for c in range(s.width)]
    v_col = col_counts.index(max(col_counts))
    return h_row, v_col


# TEST A: cross against trigger, try ALL 4 push directions
# Start by getting cross stuck against trigger from the SOUTH (pressing UP)
# Cross at (3,39) → move to (21, 36): 6R, 1U, then blocked.
# Actually we also need to arrive NOT touching trigger then touch.
def setup_south_of_trigger():
    g = new_game_at_l7()
    for _ in range(6): act(g, 'ACTION4')  # R to x=21
    act(g, 'ACTION1')  # U once, lands at (21, 36), touches trigger
    return g


print('=== TEST 1: stuck south of trigger, push UP ===')
g = setup_south_of_trigger()
s = active_sprite(g); show(s, 'after 1U'); print('arms:', arm_positions(s))
for i in range(6):
    act(g, 'ACTION1')
    s = active_sprite(g)
    print(f'U{i+2}: pos=({s._x},{s._y}) arms={arm_positions(s)}')
show(s, 'final')

print('\n=== TEST 2: stuck south, push LEFT and RIGHT ===')
g = setup_south_of_trigger()
for i in range(6):
    act(g, 'ACTION3')  # LEFT
    s = active_sprite(g)
    print(f'L{i+1}: pos=({s._x},{s._y}) arms={arm_positions(s)}')
show(s, 'after L-pushes')

print('\n=== TEST 3: stuck south, push DOWN ===')
g = setup_south_of_trigger()
for i in range(6):
    act(g, 'ACTION2')  # DOWN
    s = active_sprite(g)
    print(f'D{i+1}: pos=({s._x},{s._y}) arms={arm_positions(s)}')

print('\n=== TEST 4: after UP-pushes, move AWAY from trigger — do shifts persist? ===')
g = setup_south_of_trigger()
for i in range(3): act(g, 'ACTION1')  # 3 UP pushes
s = active_sprite(g)
print(f'after 3U: arms={arm_positions(s)}')
# Move DOWN to escape
for i in range(3):
    act(g, 'ACTION2')
    s = active_sprite(g)
    print(f'D{i+1}: pos=({s._x},{s._y}) arms={arm_positions(s)}')
show(s, 'escaped')
