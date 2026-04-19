"""KA59 solver — deepcopy BFS for all levels."""
import sys
import copy
import importlib.util
from collections import deque
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('ka59', 'environment_files/ka59/9f096b4a/ka59.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

R = ActionInput(id=GameAction.ACTION4, data={})
L = ActionInput(id=GameAction.ACTION3, data={})
U = ActionInput(id=GameAction.ACTION1, data={})
D = ActionInput(id=GameAction.ACTION2, data={})
DIR_ACTIONS = [U, D, L, R]
DIR_NAMES = ['U', 'D', 'L', 'R']


def get_state(g):
    pieces = g.current_level.get_sprites_by_tag('xlfuqjygey')
    sel = g.ascpmvdpwj
    state = []
    for s in sorted(pieces, key=lambda s: (s.x, s.y)):
        is_sel = 1 if s is sel else 0
        state.append((s.x, s.y, is_sel))
    return tuple(state)


def get_click_actions(g):
    pieces = g.current_level.get_sprites_by_tag('xlfuqjygey')
    sel = g.ascpmvdpwj
    clicks = []
    for s in pieces:
        if s is not sel:
            gx = s.x + s.width // 2
            gy = s.y + s.height // 2
            sc, ox, oy = g.camera._calculate_scale_and_offset()
            dx = int(gx * sc + ox)
            dy = int(gy * sc + oy)
            clicks.append(ActionInput(id=GameAction.ACTION6, data={'x': dx, 'y': dy}))
    return clicks


def bfs_solve(level_idx, max_depth=None):
    g0 = mod.Ka59()
    g0.set_level(level_idx)
    baselines = [39, 175, 86, 47, 21, 132, 326]
    baseline = baselines[level_idx]
    limit = max_depth or min(baseline + 10, 200)

    start_state = get_state(g0)
    print(f"Level {level_idx+1}: limit={limit}, baseline={baseline}")
    print(f"  Start: {start_state}", flush=True)

    queue = deque()
    queue.append((g0, []))
    visited = {start_state}
    iters = 0

    while queue:
        g, path = queue.popleft()
        iters += 1
        if iters % 2000 == 0:
            print(f"  iter={iters} q={len(queue)} d={len(path)} v={len(visited)}", flush=True)

        if len(path) >= limit:
            continue

        if g._current_level_index > level_idx:
            names = []
            for a in path:
                if a.id == GameAction.ACTION6:
                    names.append(f"C({a.data.get('x')},{a.data.get('y')})")
                else:
                    names.append(['U','D','L','R'][[GameAction.ACTION1,GameAction.ACTION2,GameAction.ACTION3,GameAction.ACTION4].index(a.id)])
            print(f"  FOUND! {len(path)} actions ({iters} iters)")
            print(f"  Path: {' '.join(names)}")
            return path

        all_actions = list(DIR_ACTIONS) + get_click_actions(g)

        for action in all_actions:
            g2 = copy.deepcopy(g)
            g2.perform_action(action)
            state = get_state(g2)
            if state not in visited:
                visited.add(state)
                queue.append((g2, path + [action]))

    print(f"  No solution (visited {len(visited)}, {iters} iters)")
    return None


if __name__ == '__main__':
    level = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    max_d = int(sys.argv[2]) if len(sys.argv) > 2 else None
    bfs_solve(level, max_d)
