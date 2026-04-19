"""Deep BFS from L7 init — find ALL selections and directions."""
import sys, copy
import numpy as np
from collections import deque
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
from lf52_tool import LF52
from arcengine import GameAction

g = LF52(up_to_level=7, verbose=False)
snap0 = copy.deepcopy(g.env._game)

def veh_key(game):
    return tuple(sorted((s.x, s.y) for z, s, e in game.ikhhdzfmarl._sorted_cache
                        if 'hupkpseyuim' in s.name and s.visible))

def check_selections(env, game_snap):
    results = []
    foz = [(s.x, s.y, s.name) for z, s, e in game_snap.ikhhdzfmarl._sorted_cache
           if 'fozwvlovdui' in s.name and s.visible]
    vp = tuple(game_snap.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
    for fx, fy, fn in foz:
        sx, sy = fx+vp[0]+3, fy+vp[1]+3
        if not (0 <= sx < 64 and 0 <= sy < 64): continue
        env._game = copy.deepcopy(game_snap)
        obs = env.step(GameAction.ACTION6, data={'x': sx, 'y': sy})
        frame = np.array(obs.frame[-1], dtype=np.int16)
        c3 = int((frame == 3).sum())
        if c3 > 0:
            hints = [(int(x), int(y)) for y, x in zip(*np.where(frame == 2))]
            hw = sorted(set(((h[0]-vp[0])//6*6, (h[1]-vp[1])//6*6) for h in hints))
            results.append((fx, fy, fn, hw))
    return results

visited = set()
visited.add(veh_key(snap0))
queue = deque([([], copy.deepcopy(snap0))])
all_selections = set()
states = 0

print("Deep BFS from L7 init...")
sys.stdout.flush()

while queue and states < 500:
    actions, snap = queue.popleft()
    if len(actions) > 15:
        continue
    sels = check_selections(g.env, snap)
    for fx, fy, fn, hw in sels:
        key = (fx, fy, fn[:15], tuple(hw))
        if key not in all_selections:
            all_selections.add(key)
            dirs = []
            for hx, hy in hw:
                if hx > fx: dirs.append('R')
                elif hx < fx: dirs.append('L')
                elif hy > fy: dirs.append('D')
                elif hy < fy: dirs.append('U')
            print(f"  [{len(actions):2d}A] ({fx},{fy})[{fn[:10]}] → {hw} {dirs} seq={actions[:6]}")
            sys.stdout.flush()
    states += 1
    if states % 100 == 0:
        print(f"  ... {states} states, {len(visited)} unique, {len(all_selections)} sels")
        sys.stdout.flush()
    if len(actions) < 15:
        for a in [1, 2, 3, 4]:
            g.env._game = copy.deepcopy(snap)
            g.env.step(getattr(GameAction, f'ACTION{a}'))
            new_g = copy.deepcopy(g.env._game)
            key = veh_key(new_g)
            if key not in visited:
                visited.add(key)
                queue.append((actions + [a], new_g))

print(f"\nTotal: {states} states, {len(visited)} unique, {len(all_selections)} sels")
for s in sorted(all_selections):
    print(f"  ({s[0]},{s[1]})[{s[2]}] → {s[3]}")
