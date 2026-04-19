"""Verified L9 solution: 14 clicks.

Found by 2-click brute force from dyn2's click-12 state. The critical
discovery was that F4+F2+E3 can all be delivered to goal 1 (F4 and E3
overlapping at the same position) with click13=(12,33) click14=(11,41).
"""
import importlib.util, json
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('su15', 'environment_files/su15/4c352900/su15.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
with open('solutions/su15_solutions.json') as f:
    sols = json.load(f)


def act(g, x, y):
    g.perform_action(ActionInput(id=GameAction.ACTION6, data={'x': x, 'y': y}))


def snap_str(g):
    lvl = g.current_level
    fs = [(f.name, f.x, f.y, f.width) for f in lvl.get_sprites_by_tag('fruit')]
    es = []
    for tag, k in (('enemy', 1), ('enemy2', 2), ('enemy3', 3)):
        if tag in lvl.get_all_tags():
            for s in lvl.get_sprites_by_tag(tag):
                es.append((k, s.x, s.y))
    return f'F={fs} E={es}'


# Prefix: clear levels 0-7
g = mod.Su15()
for prev in range(8):
    for (cx, cy) in sols[str(prev)]:
        act(g, cx, cy)
print(f'At start of L9: state={g._state.name}, level={g._current_level_index}')
print(f'  {snap_str(g)}')

# The 14-click solution
solution = [
    (17, 54),  # 1 merge F1+F1 → F2
    (11, 54),  # 2 F2 → goal 3
    (0, 30),   # 3 decay stage 1
    (0, 30),   # 4 decay stage 2
    (0, 30),   # 5 decay stage 3
    (23, 51),  # 6 vac F5
    (18, 47),  # 7 vac F5
    (13, 43),  # 8 F5 → corner (11,41) of goal 1
    (1, 44),   # 9 herd left E1
    (15, 41),  # 10 herd right enemies
    (14, 43),  # 11 oscillate (stasis intentional)
    (12, 43),  # 12 oscillate → enemies converge, E2 in goal
    (12, 33),  # 13 pull enemies up, form E2→future-E3 staging
    (11, 41),  # 14 final merge → E3 in goal 1 ✓
]

for i, (x, y) in enumerate(solution, 1):
    act(g, x, y)
    print(f'  {i:2d}. ({x:2d},{y:2d}): state={g._state.name} score={g._score} {snap_str(g)}')
    if g._state.name == 'WIN':
        print(f'\n🏆 L9 WIN at click {i}! Final score={g._score}')
        break
    if g._state.name == 'GAME_OVER':
        print('GAME OVER')
        break
