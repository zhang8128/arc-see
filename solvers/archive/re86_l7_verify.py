"""Compose L7 solution from per-sprite BFS paths and verify."""
import importlib.util, sys
sys.path.insert(0, '.')
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('re86', 'environment_files/re86/4e57566e/re86.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
sol_spec = importlib.util.spec_from_file_location('sol_re86', 'solutions/solution_re86.py')
sol = importlib.util.module_from_spec(sol_spec)
sol_spec.loader.exec_module(sol)


A_SEQ = ['ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION3', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION2', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2']
B_SEQ = ['ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION4', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION1', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4']
C_SEQ = ['ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION4', 'ACTION2', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION4', 'ACTION1', 'ACTION4', 'ACTION2', 'ACTION2', 'ACTION2']

L7_SEQ = A_SEQ + ['ACTION5'] + B_SEQ + ['ACTION5'] + C_SEQ
print(f'L7 total: {len(L7_SEQ)} actions')


def new_game_at_l7():
    g = mod.Re86()
    g.set_level(0)
    for lvl in range(1, 7):
        for a in sol.SOLUTIONS[lvl]:
            g.perform_action(ActionInput(id=getattr(GameAction, a)))
    return g


def players(g):
    lvl = g._levels[g._current_level_index]
    return [s for s in lvl._sprites if 'vfaeucgcyr' in s._tags]


g = new_game_at_l7()
print(f'Start L7. State={g._state.name} level={g._current_level_index}')

for i, a in enumerate(L7_SEQ):
    g.perform_action(ActionInput(id=getattr(GameAction, a)))
    if g._state.name == 'WIN' or g._current_level_index > 6:
        print(f'  WIN at step {i+1}!')
        break

print(f'Final: state={g._state.name} level={g._current_level_index}')

# Dump final sprite positions
print('\nFinal sprite states:')
for s in players(g):
    print(f'  {s._name} pos=({s._x},{s._y}) size={s.width}x{s.height}')
    nonblank_pos = set()
    for y in range(s.height):
        for x in range(s.width):
            c = int(s.pixels[y, x])
            if c not in (-1, 4):
                nonblank_pos.add((s._x+x, s._y+y, c))
    # Show coverage on target list
    targets = [
        (9, 9, 8), (3, 15, 8), (36, 15, 8), (9, 27, 8),
        (57, 18, 9), (39, 24, 9),
        (45, 30, 11), (39, 48, 11), (51, 48, 11),
    ]
    hit = 0
    for (tx, ty, tc) in targets:
        if (tx, ty, tc) in nonblank_pos:
            hit += 1
    print(f'    targets hit: {hit}')
