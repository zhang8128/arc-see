"""Does a higher-kind enemy downgrade F5?

Setup: merge left pair → E2, let E2 chase F5, observe F5 kind over ticks.
If E2 doesn't downgrade F5, try to let E3 form near F5 and observe again.
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


def fmt(g):
    lvl = g.current_level
    fs = []
    for s in lvl.get_sprites_by_tag('fruit'):
        fs.append(f"F{s.name}@({s.x},{s.y})")
    es = []
    for tag, k in (('enemy', 1), ('enemy2', 2), ('enemy3', 3)):
        if tag in lvl.get_all_tags():
            for s in lvl.get_sprites_by_tag(tag):
                es.append(f"E{k}@({s.x},{s.y})")
    return f"[{' '.join(sorted(fs))}] [{' '.join(sorted(es))}]"


print("=" * 60)
print("Test 1: E2 collides with F5 — does F5 downgrade?")
print("=" * 60)
g = at_l9()
print(f"start:                 {fmt(g)}")
# Click 1: merge left pair → E2 at (14, 12)
g.perform_action(ActionInput(id=GameAction.ACTION6, data={'x': 16, 'y': 14}))
print(f"after (16,14):         {fmt(g)}")
# Now E2 will chase nearest fruit. Nearest to (14, 12) c(16, 14):
# F1 (18,46) c(19, 47) = dist 1098. F1 (23,52) c(24, 53) = 1585. F5 (35,48) c(38, 51) = 1853.
# E2 chases F1 closest. But F1 is not our target — we want E2 to chase F5.
# Strategy: vacuum F1 fruits away so F5 becomes closest to E2.
# Or: leave F1's alone and see if E2 eats F1 then moves to F5.

# Actually, simpler: merge F1 fruits to F2 via (17, 54) — then two fruits: F2 and F5.
# E2 will chase closer of those.
g.perform_action(ActionInput(id=GameAction.ACTION6, data={'x': 17, 'y': 54}))
print(f"after (17,54):         {fmt(g)}")
# Now: F2 at (16, 53), F5 at (35, 48). E2 at wherever chase took it.
# E2 was at (14, 12). Its chase direction after (16, 14) click: toward nearest fruit.
# Hmm — so E2 may have moved to (18, 16) or similar.

# Let E2 chase toward F5 by vacuuming F2 into a corner and letting F5 be the attractor.
# But F2 is a goal target, don't lose it.

# Instead: bypass the complication — do repeated productive clicks at F5's center so
# F5 stays put and E2 is forced to chase F5 (or F2 if closer).
for step in range(15):
    # Click at F5 center to keep F5 still and advance time
    fruits = list(g.current_level.get_sprites_by_tag('fruit'))
    f5 = next((s for s in fruits if s.name == '5'), None)
    if f5 is None:
        print(f"  F5 gone at step {step}")
        break
    cx, cy = f5.x + f5.width // 2, f5.y + f5.height // 2
    cx = max(0, min(63, cx))
    cy = max(10, min(62, cy))
    # Alternate 1px to avoid stasis penalty
    cx += (1 if step % 2 == 0 else -1)
    cx = max(0, min(63, cx))
    g.perform_action(ActionInput(id=GameAction.ACTION6, data={'x': cx, 'y': cy}))
    print(f"  step {step+1:2d} ({cx},{cy}): {fmt(g)}")
    if g._state.name == 'GAME_OVER':
        print("  GAME OVER")
        break
    if g._current_level_index > 8:
        print("  WIN!")
        break
