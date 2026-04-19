"""Dump raw L9 ground truth: full sprite list, all tags, raw goal spec."""
import importlib.util, json
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('su15', 'environment_files/su15/4c352900/su15.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

with open('solutions/su15_solutions.json') as f:
    sols = json.load(f)


def new_engine_at_l9():
    g = mod.Su15()
    for prev in range(8):
        for (cx, cy) in sols[str(prev)]:
            g.perform_action(ActionInput(id=GameAction.ACTION6, data={'x': cx, 'y': cy}))
    assert g._current_level_index == 8
    return g


g = new_engine_at_l9()
lvl = g.current_level

print("=" * 70)
print("L9 RAW GROUND TRUTH")
print("=" * 70)

# Raw goal spec
print(f"\ng.reqbygadvzmjired = {g.reqbygadvzmjired}")

# All sprites with tags
print(f"\nAll sprites in L9 ({len(lvl.sprites)} total):")
all_tags = set()
for s in lvl.sprites:
    tags = tuple(sorted(s.tags))
    all_tags.update(tags)
    name = getattr(s, 'name', '?')
    print(f"  {name!r:10} pos=({s.x:2d},{s.y:2d}) size={s.width}x{s.height} tags={tags}")

print(f"\nUnique tags seen in L9: {sorted(all_tags)}")

# What tags exist in ALL levels, collected by sprite count?
print("\n=== Tag summary across all levels ===")
for idx in range(9):
    g = mod.Su15()
    g.set_level(idx)
    tag_counts = {}
    for s in g.current_level.sprites:
        for t in s.tags:
            tag_counts[t] = tag_counts.get(t, 0) + 1
    tag_str = ", ".join(f"{t}={c}" for t, c in sorted(tag_counts.items()))
    print(f"  L{idx+1}: {tag_str}")

# Play a few clicks and watch all sprites
print("\n=== L9: all sprites after a few clicks ===")
g = new_engine_at_l9()
for i, (cx, cy) in enumerate([(17, 54), (50, 26), (10, 55)]):
    g.perform_action(ActionInput(id=GameAction.ACTION6, data={'x': cx, 'y': cy}))
    print(f"\n-- After click {i+1} ({cx},{cy}) --")
    for s in g.current_level.sprites:
        if any(t in s.tags for t in ('fruit', 'enemy', 'enemy2', 'enemy3', 'goal')):
            name = getattr(s, 'name', '?')
            print(f"  {name!r:10} ({s.x:2d},{s.y:2d}) {sorted(s.tags)}")
