"""Verify composed L8 solution."""
import importlib.util, sys
sys.path.insert(0, '.')
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('re86', 'environment_files/re86/4e57566e/re86.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
sol_spec = importlib.util.spec_from_file_location('sol_re86', 'solutions/solution_re86.py')
sol = importlib.util.module_from_spec(sol_spec)
sol_spec.loader.exec_module(sol)

A_SEQ = ['ACTION3', 'ACTION3', 'ACTION3', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION1', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION2', 'ACTION4', 'ACTION4', 'ACTION2', 'ACTION4', 'ACTION4', 'ACTION2', 'ACTION2', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3']

B_SEQ = ['ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION2', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION2', 'ACTION2', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION2', 'ACTION4', 'ACTION4', 'ACTION2', 'ACTION4', 'ACTION4', 'ACTION2', 'ACTION2', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION2', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION2', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3']

L8_SEQ = A_SEQ + ['ACTION5'] + B_SEQ
print(f'L8 total: {len(L8_SEQ)} actions (baseline 221)')

g = mod.Re86()
g.set_level(0)
for lvl in range(1, 8):
    for a in sol.SOLUTIONS[lvl]:
        g.perform_action(ActionInput(id=getattr(GameAction, a)))
print(f'Start L8 (level_idx={g._current_level_index})')

for i, a in enumerate(L8_SEQ):
    g.perform_action(ActionInput(id=getattr(GameAction, a)))
    if g._state.name == 'WIN' or g._current_level_index > 7:
        print(f'WIN at step {i+1}!')
        break
print(f'Final: state={g._state.name} level={g._current_level_index}')
