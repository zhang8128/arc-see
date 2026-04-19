"""Probe vertical arm shifts and DOWN direction."""
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


def active(g):
    for s in players(g):
        if 0 in s.pixels:
            return s


def arms(s):
    px = s.pixels
    row_counts = [sum(1 for c in row if c != -1) for row in px]
    h_row = row_counts.index(max(row_counts))
    col_counts = [sum(1 for row in px if row[c] != -1) for c in range(s.width)]
    v_col = col_counts.index(max(col_counts))
    return h_row, v_col


def show(s, label=''):
    print(f'[{label}] pos=({s._x},{s._y}) {s.width}x{s.height}')
    for row in s.pixels:
        print('  ' + ''.join('.' if c == -1 else f'{int(c):2d}'[-1] for c in row))


# === Vertical arm shift test ===
# Need to approach trigger from the EAST pushing LEFT against it, or from the WEST pushing RIGHT.
# Trigger at (28,28) 8x8. Cross pattern 19x19, arms at (9,9).
# Approach from east: cross at x such that horizontal arm enters trigger cols but vert arm clear.
# At x=30: sprite (30..48, y..y+18). Vert arm col 39 (clear east). Horiz arm row y+9 cols 30..48. If y+9 in [28,35], overlap.
# y such that horiz arm row in trigger rows: y in [19, 26]. Pick y=21, horiz row 30.
# But reach (30, 21) from start (3, 39): too far up-right. Let's route: 9R (to x=30), 6U (to y=21).

g = new_game_at_l7()
# First, ensure no trigger contact during moves. At y=39 moving R freely.
for _ in range(9): act(g, 'ACTION4')
s = active(g)
print(f'after 9R: pos=({s._x},{s._y}) arms={arms(s)}')

# Now UP toward y=21. Each step: y -= 3.
# At y=36: horiz row 45, vert col 39. No overlap.
# At y=33: horiz row 42, no overlap.
# ...at y=24: horiz row 33, in trigger rows. Vert col 39. Does any sprite pixel enter trigger?
#   Horiz arm at row 33 cols 30..48. Trigger cols 28..35. Overlap cols 30..35 ≠ ∅. YES trigger collision.
# So the move y=27→y=24 could be blocked at UP.
for i in range(8):
    prev = (s._x, s._y, arms(s))
    act(g, 'ACTION1')
    s = active(g)
    cur = (s._x, s._y, arms(s))
    print(f'U{i+1}: {prev} → {cur}')

show(s, 'after UP attempts')

# Now push LEFT — should try to decrease x (move west, toward trigger).
print('\n--- Push LEFT ---')
for i in range(8):
    prev = (s._x, s._y, arms(s))
    act(g, 'ACTION3')
    s = active(g)
    print(f'L{i+1}: {prev} → pos=({s._x},{s._y}) arms={arms(s)}')

show(s, 'after LEFT pushes')
