#!/usr/bin/env python3
"""SK48 L8 — Game-engine A* (correct physics)."""

import numpy as np, copy, time, heapq
import arc_agi
from arcengine import GameAction, GameState

SOLUTIONS = {1:"UUURRRRLDDRLUR",2:"RRRRUUULLURRDDRURLLURRLLURR",
    3:"RRUUUURDDLDRRRRLLLLUUUURDDDLUUUUR",4:"RRUUUULLLLDRURDRURRDLLU",
    5:"LULLRRRRRURRDLLLLDDLDRRRRLURDRLUR"}
L6_SEQ = [('A','ACTION2'),('A','ACTION4'),('A','ACTION4'),('A','ACTION4'),
    ('C',31,4),('A','ACTION2'),('A','ACTION2'),('A','ACTION4'),('A','ACTION2'),
    ('A','ACTION1'),('A','ACTION4'),('A','ACTION2'),('A','ACTION1'),
    ('A','ACTION4'),('A','ACTION2'),('C',7,34),('A','ACTION4'),('A','ACTION4'),
    ('A','ACTION4'),('A','ACTION3'),('A','ACTION3'),('A','ACTION3'),('A','ACTION3'),
    ('A','ACTION2'),('A','ACTION2'),('A','ACTION4'),('A','ACTION1'),('A','ACTION3'),
    ('A','ACTION1'),('A','ACTION4'),('C',49,4),('A','ACTION3'),('A','ACTION3'),
    ('A','ACTION2'),('A','ACTION2'),('A','ACTION2')]
L7_ABS = "VD HR HR VR VD VD HR VD VD VD VU VU VU VU VL VU VL VL VD HL HL HL VD HU HR HR HR HR HR HR HL HL HL HL".split()
GA = {'U':GameAction.ACTION1,'D':GameAction.ACTION2,'L':GameAction.ACTION3,'R':GameAction.ACTION4}
AM = {'ACTION1':GameAction.ACTION1,'ACTION2':GameAction.ACTION2,'ACTION3':GameAction.ACTION3,
      'ACTION4':GameAction.ACTION4,'ACTION6':GameAction.ACTION6}
AH = {'HR':'ACTION4','HL':'ACTION3','HU':'ACTION1','HD':'ACTION2'}
AV = {'VD':'ACTION2','VU':'ACTION1','VL':'ACTION3','VR':'ACTION4'}
CELL = 6

def create_env():
    a = arc_agi.Arcade(); e = a.make("sk48-41055498", render_mode=None)
    g = e._game; o = e.reset()
    for l in range(1,6):
        for c in SOLUTIONS[l]: o = e.step(GA[c], data={})
    for i in L6_SEQ:
        if i[0]=='C': o = e.step(GameAction.ACTION6, data={'x':i[1],'y':i[2]})
        else: o = e.step(AM[i[1]], data={})
    # L7
    cur = 'H'
    def cc(cn):
        lv = g._levels[g._current_level_index]
        for s in lv._sprites:
            if hasattr(s,'tags') and 'sys_click' in s.tags and s.y < 54:
                cs = {int(px) for r in s.pixels for px in r if px != -1}
                if cn=='cage15' and 15 in cs: return e.step(GameAction.ACTION6,data={'x':s.x+2,'y':s.y+2})
                elif cn=='cage6' and 6 in cs: return e.step(GameAction.ACTION6,data={'x':s.x+2,'y':s.y+2})
        return None
    for a2 in L7_ABS:
        r = a2[0]
        if r != cur:
            cc('cage15' if r=='V' else 'cage6'); cur = r
        o = e.step(AM[(AH if r=='H' else AV)[a2]], data={})
    return e, g, o

def get_blocks(game):
    lv = game._levels[game._current_level_index]
    bl = []
    for s in lv._sprites:
        if hasattr(s,'name') and s.name == 'elmjchdqcn' and s.y < 54:
            cs = set()
            for r in s.pixels:
                for px in r:
                    if px != -1 and px != -2: cs.add(int(px))
            bl.append((s.x, s.y, max(cs) if cs else 0))
    return tuple(sorted(bl))

def heuristic(blocks):
    h = 0
    for tx,ty,tc in [(11,26,9),(17,26,14),(29,14,8),(29,20,12)]:
        best = 99
        for bx,by,bc in blocks:
            if bc == tc:
                best = min(best, abs(bx-tx)//CELL + abs(by-ty)//CELL)
        h += best
    return h

def state_key(game):
    lv = game._levels[game._current_level_index]
    return hash(tuple((s.x,s.y) for s in lv._sprites if hasattr(s,'x')))

def get_actions(game):
    acts = [('U',GameAction.ACTION1,{}),('D',GameAction.ACTION2,{}),
            ('L',GameAction.ACTION3,{}),('R',GameAction.ACTION4,{})]
    lv = game._levels[game._current_level_index]
    for s in lv._sprites:
        if hasattr(s,'tags') and 'sys_click' in s.tags and s.y < 54:
            cs = {int(px) for r in s.pixels for px in r if px != -1}
            if 15 in cs: acts.append(('Cv',GameAction.ACTION6,{'x':s.x+2,'y':s.y+2}))
            elif 6 in cs: acts.append(('Ch',GameAction.ACTION6,{'x':s.x+2,'y':s.y+2}))
    return acts

print("Setting up L8...")
env, g, obs = create_env()
ib = get_blocks(g); ih = heuristic(ib)
print(f"L8 blocks: {ib}, h={ih}")

pq = [(ih, 0, id(g), copy.deepcopy(g), [])]
visited = {state_key(g): 0}; best = 60; found = None; it = 0; t0 = time.time()

while pq:
    f, cost, _, game, path = heapq.heappop(pq)
    if cost >= best: continue
    sk = state_key(game)
    if sk in visited and visited[sk] < cost: continue
    it += 1
    if cost > 0 and it % 100 == 0:
        el = time.time() - t0
        if el > 3600: break  # 1hr timeout
    if it % 2000 == 0:
        el = time.time() - t0
        bl = get_blocks(game)
        print(f"  it={it} f={f} d={cost} vis={len(visited)} t={el:.0f}s h={f-cost} bl={bl}", flush=True)

    for an, act, data in get_actions(game):
        g2 = copy.deepcopy(game); env._game = g2
        try: obs2 = env.step(act, data=data)
        except: continue
        if obs2.state == GameState.WIN or g2._current_level_index > 7:
            found = path + [an]
            print(f"\n*** L8 SOLVED at depth {cost+1}! ***")
            print(f"  Path: {' '.join(found)}")
            print(f"  Time: {time.time()-t0:.1f}s, States: {len(visited)}")
            best = cost + 1; break
        sk2 = state_key(g2); nc = cost + 1
        if sk2 in visited and visited[sk2] <= nc: continue
        visited[sk2] = nc
        h2 = heuristic(get_blocks(g2))
        if nc + h2 < best:
            heapq.heappush(pq, (nc+h2, nc, id(g2), g2, path+[an]))
    if found: break

el = time.time()-t0
if found: print(f"\nSolution ({len(found)} steps): {' '.join(found)}")
else: print(f"\nNo solution found ({it} it, {len(visited)} vis, {el:.0f}s)")
