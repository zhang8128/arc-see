"""Dynamic plan for L9: track F5 actual position each click, vacuum toward target.

Strategy:
  1. Merge fruits and deliver F2 to goal 3 (2 clicks)
  2. Chain-vacuum F5 toward goal 1 (upper-left) — DYNAMIC: recompute click
     based on current F5 center each step
  3. Once F5 is close to goal 1, no-op for decay + enemy convergence
  4. Deliver F5 (now F4 via decay) into goal 1
"""
import importlib.util, json
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('su15', 'environment_files/su15/4c352900/su15.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
with open('solutions/su15_solutions.json') as f:
    sols = json.load(f)


def at_l9():
    g = mod.Su15()
    for prev in range(8):
        for (cx, cy) in sols[str(prev)]:
            g.perform_action(ActionInput(id=GameAction.ACTION6, data={'x': cx, 'y': cy}))
    return g


def snap(g):
    lvl = g.current_level
    fruits = list(lvl.get_sprites_by_tag('fruit'))
    enemies = []
    for tag, k in (('enemy', 1), ('enemy2', 2), ('enemy3', 3)):
        if tag in lvl.get_all_tags():
            for s in lvl.get_sprites_by_tag(tag):
                enemies.append((k, s))
    return fruits, enemies


def goals(g):
    return [(s.x, s.y, s.width, s.height) for s in g.current_level.get_sprites_by_tag('goal')]


def status_str(g):
    gs = goals(g)
    fs, es = snap(g)
    fstr = []
    for f in fs:
        cx, cy = f.x + f.width//2, f.y + f.height//2
        ig = any(gx<=cx<gx+gw and gy<=cy<gy+gh for gx,gy,gw,gh in gs)
        fstr.append(f'{f.name}sz{f.width}@({f.x},{f.y}){{g={int(ig)}}}')
    estr = []
    for k, s in es:
        cx, cy = s.x + s.width//2, s.y + s.height//2
        ig = any(gx<=cx<gx+gw and gy<=cy<gy+gh for gx,gy,gw,gh in gs)
        estr.append(f'E{k}@({s.x},{s.y}){{g={int(ig)}}}')
    return f'F={fstr} E={estr}'


def find_big_fruit(g):
    """Find the originally-F5 fruit — track by being the biggest one on field."""
    fs, _ = snap(g)
    if not fs:
        return None
    return max(fs, key=lambda f: f.width)


click_count = [0]
def do(g, cx, cy, note=''):
    click_count[0] += 1
    cx = max(0, min(63, cx))
    cy = max(10, min(62, cy))
    g.perform_action(ActionInput(id=GameAction.ACTION6, data={'x': cx, 'y': cy}))
    print(f'  {click_count[0]:2d}. ({cx:2d},{cy:2d}) {note}: {status_str(g)}  score={g._score}')
    if g._current_level_index > 8:
        print('      🏆 WIN!')
        return 'win'
    if g._state.name == 'GAME_OVER':
        print('      GAME OVER')
        return 'over'
    return 'ok'


# Run
g = at_l9()
print(f'start: {status_str(g)}')

# Plan XX: Plan LL flow + active enemy herding
# Phase 1: deliver F2
if do(g, 17, 54, 'merge') != 'ok': raise SystemExit
if do(g, 11, 54, 'F2 → goal 3') != 'ok': raise SystemExit

# Phase 2: 3 no-ops to let enemies reach F5 (triggers size decay via collision)
for i in range(3):
    if do(g, 0, 30, f'stage decay {i+1}') != 'ok': raise SystemExit

# Phase 3: dynamically vacuum F5 toward goal 1
target_x, target_y = 11, 41
for step in range(8):
    f5 = find_big_fruit(g)
    if f5 is None:
        print('  F5 gone')
        break
    cx = f5.x + f5.width // 2
    cy = f5.y + f5.height // 2
    if abs(cx - target_x) <= 2 and abs(cy - target_y) <= 2:
        print(f'  F5 reached goal 1 as F4! center=({cx},{cy}) size={f5.width}')
        break
    dx = target_x - cx
    dy = target_y - cy
    step_mag = 5
    mag = max(abs(dx), abs(dy), 1)
    scale = min(step_mag, mag) / mag
    click_x = cx + int(round(dx * scale))
    click_y = cy + int(round(dy * scale))
    result = do(g, click_x, click_y, f'vac F5 toward g1 (f5@{cx},{cy} sz{f5.width})')
    if result != 'ok':
        raise SystemExit

# Phase 4: herd left-side E1 away from F2 using a click far from F4
# F4 at ~(11, 41). Click must be far from F4 (>10 dist) but in E1 range.
# Click (1, 44) is 12 px from F4, in range of E1@(1, 48).
if do(g, 1, 44, 'herd left E1 up (safe from F4)') != 'ok': raise SystemExit

# Phase 5: big directed click — vacuum right E1 toward F4
# Click (15, 41) — F4 moves to (13, 39), E1@(21,41) vacuumed to ~(9, 37)
if do(g, 15, 41, 'vac right E1 toward F4') != 'ok': raise SystemExit

# Phase 6: tiny oscillation to let the close enemies converge
offsets = [(1, 0), (-1, 0), (0, 1), (0, -1)]
for step in range(10):
    f4 = find_big_fruit(g)
    if f4 is None:
        print('  Big fruit gone')
        break
    cx = f4.x + f4.width // 2
    cy = f4.y + f4.height // 2
    ox, oy = offsets[step % len(offsets)]
    click_x = max(0, min(63, cx + ox))
    raw_y = cy + oy
    click_y = max(38, min(44, raw_y))
    result = do(g, click_x, click_y, f'tiny oscillate F4 (f4@{cx},{cy})')
    if result != 'ok':
        raise SystemExit
