"""Dynamic runner: let click sequence depend on observed state.

Strategy (Plan O):
  1. Merge F1 fruits at (17,54) → F2
  2. Move F2 into goal 3 at (11,54)
  3. Thereafter, click at F5's current center to advance time productively
     (F5 is always in range of its own center → productive click, no penalty)
  4. Observe enemy merge chain and goal status
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


def snapshot(g):
    lvl = g.current_level
    fruits = [(int(s.name) if s.name.isdigit() else -1, s.x, s.y, s.width) for s in lvl.get_sprites_by_tag('fruit')]
    enemies = []
    all_tags = lvl.get_all_tags()
    for tag, ek in (('enemy', 1), ('enemy2', 2), ('enemy3', 3)):
        if tag in all_tags:
            for s in lvl.get_sprites_by_tag(tag):
                enemies.append((ek, s.x, s.y))
    return fruits, enemies


def goal_status(g):
    lvl = g.current_level
    goals = [(s.x, s.y, s.width, s.height) for s in lvl.get_sprites_by_tag('goal')]
    fruits, enemies = snapshot(g)
    f_counts = {}
    for k, x, y, w in fruits:
        cx, cy = x + w // 2, y + w // 2
        for gx, gy, gw, gh in goals:
            if gx <= cx < gx + gw and gy <= cy < gy + gh:
                f_counts[k] = f_counts.get(k, 0) + 1
                break
    e_counts = {}
    for k, x, y in enemies:
        cx, cy = x + 5 // 2, y + 4 // 2
        for gx, gy, gw, gh in goals:
            if gx <= cx < gx + gw and gy <= cy < gy + gh:
                e_counts[k] = e_counts.get(k, 0) + 1
                break
    need_f4 = 1 - f_counts.get(4, 0)
    need_f2 = 1 - f_counts.get(2, 0)
    need_e3 = 1 - e_counts.get(3, 0)
    parts = []
    if need_f4 > 0: parts.append(f"need F4:{need_f4}")
    if need_f2 > 0: parts.append(f"need F2:{need_f2}")
    if need_e3 > 0: parts.append(f"need E3:{need_e3}")
    if not parts:
        return "ALL MET"
    return " ".join(parts)


def fmt(g):
    fruits, enemies = snapshot(g)
    fs = " ".join(f"F{k}@({x},{y})" for k, x, y, _ in sorted(fruits))
    es = " ".join(f"E{k}@({x},{y})" for k, x, y in sorted(enemies))
    return f"[{fs}] [{es}]"


def do_click(g, cx, cy, label):
    g.perform_action(ActionInput(id=GameAction.ACTION6, data={'x': cx, 'y': cy}))
    level_now = g._current_level_index
    state_name = g._state.name
    return level_now, state_name


# =============================================================================
g = at_l9()
print(f"start: {fmt(g)}  {goal_status(g)}")

click_num = 0
def do(cx, cy, note=""):
    global click_num
    click_num += 1
    level_now, state_name = do_click(g, cx, cy, "")
    print(f"  {click_num:2d}. ({cx:2d},{cy:2d}) → {fmt(g)}  {goal_status(g)}  {note}")
    if level_now > 8:
        print("      🏆 WIN!")
        return True
    if state_name == 'GAME_OVER':
        print("      ❌ GAME OVER")
        return True
    return False


# Plan P: chain-vacuum F5 into goal 3, with F2 alongside, check F4 status
if do(17, 54, "merge fruits → F2@(16,53)"): raise SystemExit
if do(11, 54, "F2 → (10,53) goal 3"): raise SystemExit
if do(32, 51, "F5 pull left → (29,48)"): raise SystemExit
if do(26, 51, "F5 pull left → (23,48)"): raise SystemExit
if do(20, 51, "F5 pull left → (17,48)"): raise SystemExit
if do(14, 51, "F5 pull left → (11,48)"): raise SystemExit
if do(11, 55, "F5 into goal 3 → center (11,55)?"): raise SystemExit

# After 7 clicks, check goal status. If F4 is met (F5-counts-as-F4), we're 2/3 done.
# Then advance chase productively via F5-center alternating clicks
for step in range(20):
    fruits, enemies = snapshot(g)
    f5 = [f for f in fruits if f[0] == 5]
    if not f5:
        print("  F5 GONE — abort")
        break
    fk, fx, fy, fw = f5[0]
    cx, cy = fx + fw // 2, fy + fw // 2
    # Alternate 1 pixel left/right to avoid stasis penalty
    cx = max(0, min(63, cx + (1 if step % 2 == 0 else -1)))
    cy = max(10, min(62, cy))
    if do(cx, cy, f"anchor near F5"):
        raise SystemExit

print()
print(f"final state: {fmt(g)}  {goal_status(g)}")
