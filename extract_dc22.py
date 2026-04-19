#!/usr/bin/env python3
"""Extract DC22 solutions by running BFS + API replay, then dumping the working sequences."""
import importlib.util, copy, hashlib, json
import arc_agi
from collections import deque
from arcengine import GameAction, ActionInput, InteractionMode

spec = importlib.util.spec_from_file_location('dc22', 'environment_files/dc22/4c9bff3e/dc22.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

UP, DOWN, LEFT, RIGHT = GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4
CLICK = GameAction.ACTION6
BASELINES = [64, 117, 59, 78, 324, 550]
ACTION_NAMES = {GameAction.ACTION1: 'U', GameAction.ACTION2: 'D',
                GameAction.ACTION3: 'L', GameAction.ACTION4: 'R'}

L5_PATH = "L Cb L U U L Cb Cf Cf Cf Cf Ce Ce Ce Ce Nu Nu Nu Nr Nr Nr Cp Nl Nl Nl Nd Nd Nd Nr Nr Nr L U U U U R U Nl Nl Nl Nu Nu Nu Nr Nr Nr L U U U U U U U Cc R Nl Nl Nl Nd Nd Nd U U U U U U U U D D D D D D D D D D D D D R R R R R R R Cd D D D D D L L Cd U U L L L L L L"
L5_BUTTON_MAP = {
    'Cb': {'x': 52, 'y': 41}, 'Cc': {'x': 52, 'y': 48},
    'Cd': {'x': 52, 'y': 14}, 'Ce': {'x': 57, 'y': 23},
    'Cf': {'x': 47, 'y': 22}, 'Cp': {'x': 52, 'y': 35},
    'Nr': {'x': 55, 'y': 30}, 'Nd': {'x': 60, 'y': 30},
    'Nl': {'x': 45, 'y': 30}, 'Nu': {'x': 50, 'y': 30},
}
L5_DIR_MAP = {'U': UP, 'D': DOWN, 'L': LEFT, 'R': RIGHT}


def pixel_hash(g):
    frame = g.get_pixels(0, 0, 64, 64)
    return hashlib.md5(frame[2:63].tobytes()).hexdigest()

def get_static_actions(g):
    actions = []
    for i in g._available_actions:
        if i <= 5:
            actions.append((getattr(GameAction, f"ACTION{i}"), None))
    try:
        s, ox, oy = g.camera._calculate_scale_and_offset()
        for cs in g.current_level.get_sprites_by_tag("sys_click"):
            cx = cs.x * s + ox + cs.width * s // 2
            cy = cs.y * s + oy + cs.height * s // 2
            actions.append((CLICK, {"x": cx, "y": cy}))
    except:
        pass
    return actions

def bfs_solve(level_idx):
    g0 = mod.Dc22()
    g0.set_level(level_idx)
    baseline = BASELINES[level_idx]
    limit = min(baseline + 15, 400)
    actions = get_static_actions(g0)
    start = pixel_hash(g0)
    queue = deque([(g0, [])])
    visited = {start}
    while queue:
        g, path = queue.popleft()
        if len(path) >= limit:
            continue
        for a_id, a_data in actions:
            g2 = copy.deepcopy(g)
            g2.perform_action(ActionInput(id=a_id, data=a_data or {}))
            if g2._current_level_index > level_idx or g2._state.name == "WIN":
                return path + [(a_id, a_data)]
            if g2._state.name == "GAME_OVER":
                continue
            h = pixel_hash(g2)
            if h not in visited:
                visited.add(h)
                queue.append((g2, path + [(a_id, a_data)]))
    return None

def solve_level5():
    actions = []
    for token in L5_PATH.split():
        if token in L5_DIR_MAP:
            actions.append((L5_DIR_MAP[token], None))
        elif token in L5_BUTTON_MAP:
            actions.append((CLICK, L5_BUTTON_MAP[token]))
    return actions

def solve_level6():
    g = mod.Dc22(); g.set_level(5)
    actions = []
    def do(action):
        g.perform_action(action)
        actions.append((action.id, action.data if action.data else None))
    def moves(s):
        for c in s:
            do(ActionInput(id={'U':UP,'D':DOWN,'L':LEFT,'R':RIGHT}[c]))
    def click(x, y):
        do(ActionInput(id=CLICK, data={'x': x, 'y': y}))
    moves('LLLLL'); moves('UU'); click(51, 25); moves('UUR'); moves('LDD'); click(51, 25)
    moves('DD'); click(51, 25)
    for _ in range(4): click(56, 8)
    moves('DDLLL'); moves('DL'); click(56, 8); moves('UL'); click(56, 8)
    for _ in range(19): moves('U')
    moves('L'); moves('DDR')
    for _ in range(16): moves('D')
    moves('R')
    click(56, 8); moves('R'); click(56, 8); moves('R'); click(56, 8); moves('R'); click(56, 8); moves('R')
    moves('UUU')
    for _ in range(3): click(51, 48)
    click(51, 25); moves('L')
    for _ in range(4): click(47, 37)
    click(51, 18); moves('RR')
    for _ in range(5): click(55, 37)
    moves('LU')
    for _ in range(3): click(51, 33)
    moves('LD')
    for _ in range(2): click(47, 37)
    moves('RU')
    for _ in range(3): click(51, 33)
    moves('RD'); moves('L'); click(51, 25)
    for _ in range(3): click(51, 48)
    click(51, 25); moves('DDD')
    for _ in range(21): moves('R')
    moves('UU')
    return actions

def encode(actions):
    parts = []
    for a_id, a_data in actions:
        if a_id in ACTION_NAMES:
            parts.append(ACTION_NAMES[a_id])
        elif a_data:
            parts.append(f"C{a_data['x']},{a_data['y']}")
    return ' '.join(parts)

# Solve all levels
all_solutions = {}
for level in range(4):
    print(f"BFS L{level+1}...", flush=True)
    all_solutions[level] = bfs_solve(level)
print("L5 replay...", flush=True)
all_solutions[4] = solve_level5()
print("L6 manual...", flush=True)
all_solutions[5] = solve_level6()

# API verification
print("\nAPI verification...", flush=True)
arcade = arc_agi.Arcade()
env = arcade.make("dc22-4c9bff3e", render_mode=None)
result = env.reset()

for level_idx in range(6):
    for (a_id, a_data) in all_solutions[level_idx]:
        if a_data:
            result = env.step(a_id, data=a_data)
        else:
            result = env.step(a_id)
    expected = level_idx + 1
    if result.levels_completed >= expected:
        encoded = encode(all_solutions[level_idx])
        print(f'    {level_idx+1}: "{encoded}",  # {len(all_solutions[level_idx])} actions')
    else:
        print(f"    L{level_idx+1}: FAILED (levels_completed={result.levels_completed})")
        break

print(f"\nTotal: {sum(len(v) for v in all_solutions.values())}, State: {result.state}")
