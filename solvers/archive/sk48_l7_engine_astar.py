#!/usr/bin/env python3
"""SK48 L7 — A* directly on the game engine.
3ms deepcopy + 0ms step = can explore ~300 states/sec.
With good heuristic, should find solution in reasonable time.

Target block positions (sprite coords):
  H-rack: 9@(11,26), 14@(17,26), 9@(23,26)
  V-rack: 8@(29,8), 14@(29,14), 8@(29,20)
"""

import numpy as np
import copy
import time
import heapq
import arc_agi
from arcengine import GameAction, GameState

SOLUTIONS = {
    1: "UUURRRRLDDRLUR",
    2: "RRRRUUULLURRDDRURLLURRLLURR",
    3: "RRUUUURDDLDRRRRLLLLUUUURDDDLUUUUR",
    4: "RRUUUULLLLDRURDRURRDLLU",
    5: "LULLRRRRRURRDLLLLDDLDRRRRLURDRLUR",
}

L6_SEQ = [
    ('A', 'ACTION2'), ('A', 'ACTION4'), ('A', 'ACTION4'), ('A', 'ACTION4'),
    ('C', 31, 4),
    ('A', 'ACTION2'), ('A', 'ACTION2'), ('A', 'ACTION4'), ('A', 'ACTION2'),
    ('A', 'ACTION1'), ('A', 'ACTION4'), ('A', 'ACTION2'), ('A', 'ACTION1'),
    ('A', 'ACTION4'), ('A', 'ACTION2'),
    ('C', 7, 34),
    ('A', 'ACTION4'), ('A', 'ACTION4'), ('A', 'ACTION4'), ('A', 'ACTION3'),
    ('A', 'ACTION3'), ('A', 'ACTION3'), ('A', 'ACTION3'), ('A', 'ACTION2'),
    ('A', 'ACTION2'), ('A', 'ACTION4'), ('A', 'ACTION1'), ('A', 'ACTION3'),
    ('A', 'ACTION1'), ('A', 'ACTION4'),
    ('C', 49, 4),
    ('A', 'ACTION3'), ('A', 'ACTION3'), ('A', 'ACTION2'), ('A', 'ACTION2'),
    ('A', 'ACTION2'),
]

GA = {'U': GameAction.ACTION1, 'D': GameAction.ACTION2, 'L': GameAction.ACTION3, 'R': GameAction.ACTION4}
AM = {'ACTION1': GameAction.ACTION1, 'ACTION2': GameAction.ACTION2,
      'ACTION3': GameAction.ACTION3, 'ACTION4': GameAction.ACTION4,
      'ACTION6': GameAction.ACTION6}

def create_env():
    arcade = arc_agi.Arcade()
    env = arcade.make("sk48-41055498", render_mode=None)
    obs = env.reset()
    for lvl in range(1, 6):
        for c in SOLUTIONS[lvl]:
            obs = env.step(GA[c], data={})
    for item in L6_SEQ:
        if item[0] == 'C':
            obs = env.step(GameAction.ACTION6, data={'x': item[1], 'y': item[2]})
        else:
            obs = env.step(AM[item[1]], data={})
    return env, obs

CELL = 6
# Target positions (sprite coords) — e at (17,14) shared by both racks
# H-rack at hry=14: 9@(11,14), 14@(17,14), 9@(23,14)
# V-rack at vrx=17: 8@(17,8), 14@(17,14), 8@(17,20)
H_TARGETS = {9: [(11, 14), (23, 14)], 14: [(17, 14)]}
V_TARGETS = {8: [(17, 8), (17, 20)], 14: [(17, 14)]}  # e counted once

def get_block_positions(game):
    """Extract movable block sprite positions from game."""
    level = game._levels[game._current_level_index]
    blocks = []
    for s in level._sprites:
        if hasattr(s, 'name') and s.name == 'elmjchdqcn' and s.y < 54:
            colors = set()
            for row in s.pixels:
                for px in row:
                    if px != -1 and px != -2:
                        colors.add(int(px))
            color = max(colors) if colors else 0
            blocks.append((s.x, s.y, color))
    return tuple(sorted(blocks))

def heuristic(blocks):
    """Manhattan distance — e counted once (shared at (17,14))."""
    h = 0
    # 9-blocks: need at (11,14) and (23,14)
    for tx, ty in [(11, 14), (23, 14)]:
        best = 999
        for bx, by, bc in blocks:
            if bc == 9:
                best = min(best, abs(bx - tx) // CELL + abs(by - ty) // CELL)
        h += best
    # 8-blocks: need at (17,8) and (17,20)
    for tx, ty in [(17, 8), (17, 20)]:
        best = 999
        for bx, by, bc in blocks:
            if bc == 8:
                best = min(best, abs(bx - tx) // CELL + abs(by - ty) // CELL)
        h += best
    # e-block: need at (17,14) — counted ONCE
    best = 999
    for bx, by, bc in blocks:
        if bc == 14:
            best = min(best, abs(bx - 17) // CELL + abs(by - 14) // CELL)
    h += best
    return h

def state_key(game):
    """Hash based on ALL sprite positions (blocks + rack state)."""
    level = game._levels[game._current_level_index]
    positions = tuple((s.x, s.y) for s in level._sprites if hasattr(s, 'x'))
    return hash(positions)

# Actions: UDLR + 2 clicks (cage6 and cage15)
# Click positions found dynamically
def get_actions(game):
    """Get available actions with click targets."""
    actions = [
        ('U', GameAction.ACTION1, {}),
        ('D', GameAction.ACTION2, {}),
        ('L', GameAction.ACTION3, {}),
        ('R', GameAction.ACTION4, {}),
    ]
    level = game._levels[game._current_level_index]
    for s in level._sprites:
        if hasattr(s, 'tags') and 'sys_click' in s.tags and s.y < 54:
            colors = {int(px) for row in s.pixels for px in row if px != -1}
            if 15 in colors:
                actions.append(('Cv', GameAction.ACTION6, {'x': s.x+2, 'y': s.y+2}))
            elif 6 in colors:
                actions.append(('Ch', GameAction.ACTION6, {'x': s.x+2, 'y': s.y+2}))
    return actions

print("Setting up...")
env, obs = create_env()
g = env._game

init_blocks = get_block_positions(g)
init_h = heuristic(init_blocks)
print(f"Initial blocks: {init_blocks}")
print(f"Initial heuristic: {init_h}")

# A* search
print(f"\nStarting A*...")
t_start = time.time()

pq = [(init_h, 0, id(g), copy.deepcopy(g), [])]
visited = {state_key(g): 0}
best = 50  # tight limit since solution ~35 abstract + clicks
found = None
iterations = 0
prev_depth = -1

while pq:
    f, cost, _, game, path = heapq.heappop(pq)
    if cost >= best:
        continue

    sk = state_key(game)
    if sk in visited and visited[sk] < cost:
        continue

    iterations += 1
    if cost != prev_depth:
        elapsed = time.time() - t_start
        print(f"  d={cost}: vis={len(visited)} pq={len(pq)} it={iterations} t={elapsed:.1f}s h={f-cost}", flush=True)
        prev_depth = cost
        if elapsed > 2400:  # 40 min timeout
            break

    # Get actions for this state
    actions = get_actions(game)

    for aname, action, data in actions:
        g2 = copy.deepcopy(game)
        env._game = g2
        try:
            obs2 = env.step(action, data=data)
        except Exception:
            continue

        # Check win
        if obs2.state == GameState.WIN or g2._current_level_index > 6:
            new_path = path + [aname]
            print(f"\n*** SOLUTION FOUND at depth {cost+1}! ***")
            print(f"  Path: {' '.join(new_path)}")
            print(f"  Iterations: {iterations}, Time: {time.time()-t_start:.1f}s")
            found = new_path
            best = cost + 1
            break

        sk2 = state_key(g2)
        new_cost = cost + 1
        if sk2 in visited and visited[sk2] <= new_cost:
            continue
        visited[sk2] = new_cost

        blocks2 = get_block_positions(g2)
        h2 = heuristic(blocks2)

        if new_cost + h2 < best:
            heapq.heappush(pq, (new_cost + h2, new_cost, id(g2), g2, path + [aname]))

    if found:
        break

elapsed = time.time() - t_start
print(f"\nA* complete: {iterations} iterations, {len(visited)} visited, {elapsed:.1f}s")
if found:
    print(f"Solution ({len(found)} steps): {' '.join(found)}")
else:
    print("No solution found")
