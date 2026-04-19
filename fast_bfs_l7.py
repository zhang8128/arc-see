"""Fast BFS — track vehicle configs only, find selection-enabling positions."""
import sys, copy
from collections import deque
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
from lf52_tool import LF52
from arcengine import GameAction

g = LF52(up_to_level=7, verbose=False)
snap0 = copy.deepcopy(g.env._game)

def veh_key(game):
    return tuple(sorted((s.x, s.y) for z, s, e in game.ikhhdzfmarl._sorted_cache
                        if 'hupkpseyuim' in s.name and s.visible))

def veh_positions(game):
    return set((s.x, s.y) for z, s, e in game.ikhhdzfmarl._sorted_cache
               if 'hupkpseyuim' in s.name and s.visible)

visited = set()
visited.add(veh_key(snap0))
queue = deque([([], copy.deepcopy(snap0))])
states = 0
candidates = []

targets = [(0, 18), (36, 18), (0, 0), (6, 6), (30, 6), (42, 6)]

print("Fast BFS - vehicle configs...", flush=True)

while queue:
    actions, snap = queue.popleft()
    if len(actions) > 15:
        continue

    vps = veh_positions(snap)
    for t in targets:
        if t in vps:
            candidates.append((len(actions), t, list(actions)))

    states += 1
    if states % 5000 == 0:
        print(f"  {states} states, {len(visited)} unique, {len(candidates)} hits, depth~{len(actions)}", flush=True)

    if len(actions) < 15:
        for a in [1, 2, 3, 4]:
            g.env._game = copy.deepcopy(snap)
            g.env.step(getattr(GameAction, f'ACTION{a}'))
            new_g = copy.deepcopy(g.env._game)
            nk = veh_key(new_g)
            if nk not in visited:
                visited.add(nk)
                queue.append((actions + [a], new_g))

print(f"\nTotal: {states} states, {len(visited)} unique", flush=True)
print(f"Candidates with target vehicles: {len(candidates)}", flush=True)

# Show first candidates per target
from collections import defaultdict
by_target = defaultdict(list)
for d, t, seq in candidates:
    by_target[t].append((d, seq))

for t in sorted(by_target.keys()):
    entries = by_target[t]
    entries.sort()
    print(f"\n  Target {t}: {len(entries)} configs")
    for d, seq in entries[:3]:
        print(f"    depth={d}: {seq[:10]}")
