"""Targeted L7 search: DFS to find vehicle configs that enable selection.
Memory-efficient: DFS + only store visited set (not full game states).
"""
import sys, copy
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

targets = {(0, 18): 'reg_unlock', (36, 18): 'red_chain_dest', (0, 0): 'reg_up',
           (6, 6): 'reg_right', (30, 6): 'near_red', (42, 6): 'past_red'}

visited = set()
visited.add(veh_key(snap0))
results = {}

def dfs(game_snap, actions, depth):
    if depth > 12:
        return

    vps = veh_positions(game_snap)
    for t, name in targets.items():
        if t in vps and t not in results:
            results[t] = (len(actions), list(actions), name)
            print(f"  HIT: {name} vehicle at {t}, depth={len(actions)}, seq={actions[:10]}", flush=True)

    if len(results) == len(targets):
        return  # All found

    for a in [1, 2, 3, 4]:
        g.env._game = copy.deepcopy(game_snap)
        g.env.step(getattr(GameAction, f'ACTION{a}'))
        new_g = copy.deepcopy(g.env._game)
        key = veh_key(new_g)
        if key not in visited:
            visited.add(key)
            dfs(new_g, actions + [a], depth + 1)
            if len(results) == len(targets):
                return

print("Targeted DFS from L7 init (depth 12)...", flush=True)
dfs(snap0, [], 0)

print(f"\nResults ({len(results)}/{len(targets)} targets found):", flush=True)
for t in sorted(results.keys()):
    d, seq, name = results[t]
    print(f"  {name:15s} at {t}: depth={d}, seq={seq[:10]}")

print(f"\nVisited: {len(visited)} unique configs", flush=True)

if not results:
    print("No target vehicle positions found! The targets may be wrong.")
