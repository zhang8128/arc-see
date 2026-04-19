"""Interactive probe: see how sprites interact with the morph trigger on L7."""
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


def player_sprites(g):
    lvl = g._levels[g._current_level_index]
    return [s for s in lvl._sprites if 'vfaeucgcyr' in s._tags]


def show_players(g, label=''):
    ps = player_sprites(g)
    print(f'[{label}] active? checking each')
    for i, s in enumerate(ps):
        colors = sorted(set(int(c) for c in s.pixels.flatten() if c != -1))
        print(f'  P{i} {s._name} pos=({s._x},{s._y}) size={s.width}x{s.height} colors={colors}')


def act(g, a):
    g.perform_action(ActionInput(id=getattr(GameAction, a)))


# Establish which sprite moves by default
g = new_game_at_l7()
print('=== INITIAL L7 ===')
show_players(g, 'init')

print('\n=== TRY ACTION1 (UP) ===')
act(g, 'ACTION1')
show_players(g, 'after UP')

print('\n=== TRY ACTION5 (SWITCH) ===')
act(g, 'ACTION5')
print('now which moves?')
g2 = new_game_at_l7()
act(g2, 'ACTION5')
act(g2, 'ACTION1')
show_players(g2, 'switch+UP')

print('\n=== SWITCH TWICE + UP ===')
g3 = new_game_at_l7()
act(g3, 'ACTION5'); act(g3, 'ACTION5'); act(g3, 'ACTION1')
show_players(g3, 'switch x2 + UP')
