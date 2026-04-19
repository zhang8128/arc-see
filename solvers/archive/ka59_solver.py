"""KA59 solver — tile arrangement puzzle. BFS with replay."""
import sys
import importlib.util
from collections import deque
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('ka59', 'environment_files/ka59/9f096b4a/ka59.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def get_state(g):
    """Hash: positions of movable pieces + which is selected."""
    pieces = g.current_level.get_sprites_by_tag('xlfuqjygey')
    selected = g.ascpmvdpwj
    state = []
    for s in sorted(pieces, key=lambda s: (s.x, s.y)):
        is_sel = 1 if s is selected else 0
        state.append((s.x, s.y, is_sel))
    return tuple(state)


def get_actions(g):
    """Get all possible actions: UDLR + click on non-selected pieces."""
    actions = [
        ActionInput(id=GameAction.ACTION1, data={}),
        ActionInput(id=GameAction.ACTION2, data={}),
        ActionInput(id=GameAction.ACTION3, data={}),
        ActionInput(id=GameAction.ACTION4, data={}),
    ]
    # Click on non-selected pieces to swap
    pieces = g.current_level.get_sprites_by_tag('xlfuqjygey')
    selected = g.ascpmvdpwj
    for s in pieces:
        if s is not selected:
            gx = s.x + s.width // 2
            gy = s.y + s.height // 2
            sc, ox, oy = g.camera._calculate_scale_and_offset()
            dx = int(gx * sc + ox)
            dy = int(gy * sc + oy)
            actions.append(ActionInput(id=GameAction.ACTION6, data={'x': dx, 'y': dy}))
    return actions


def replay(level_idx, actions):
    g = mod.Ka59()
    g.set_level(level_idx)
    for a in actions:
        g.perform_action(a)
    return g


def is_won(g, level_idx):
    try:
        return g._current_level_index > level_idx
    except:
        return False


def bfs_solve(level_idx, max_depth=None):
    g0 = mod.Ka59()
    g0.set_level(level_idx)
    baselines = [39, 175, 86, 47, 21, 132, 326]
    baseline = baselines[level_idx]
    limit = max_depth or min(baseline + 10, 200)

    start_state = get_state(g0)
    pieces = g0.current_level.get_sprites_by_tag('xlfuqjygey')
    frames = g0.current_level.get_sprites_by_tag('rktpmjcpkt')
    print(f"Level {level_idx+1}: limit={limit}, baseline={baseline}")
    print(f"  Pieces: {[(s.x, s.y, s.width, s.height) for s in pieces]}")
    print(f"  Frames: {[(s.x, s.y, s.width, s.height) for s in frames]}")
    print(f"  Target positions: {[(f.x+1, f.y+1) for f in frames]}")
    print(f"  Start state: {start_state}", flush=True)

    queue = deque()
    queue.append([])
    visited = {start_state}
    iters = 0

    while queue:
        path = queue.popleft()
        iters += 1
        if iters % 5000 == 0:
            print(f"  iter={iters} q={len(queue)} d={len(path)} v={len(visited)}", flush=True)

        if len(path) >= limit:
            continue

        g = replay(level_idx, path)

        if is_won(g, level_idx):
            action_names = []
            for a in path:
                if a.id == GameAction.ACTION6:
                    action_names.append(f"CLICK({a.data.get('x')},{a.data.get('y')})")
                else:
                    action_names.append(a.id.name)
            print(f"  FOUND! {len(path)} actions ({iters} iters)")
            print(f"  Path: {action_names}")
            return path

        for action in get_actions(g):
            g2 = replay(level_idx, path + [action])
            state = get_state(g2)
            if state not in visited:
                visited.add(state)
                queue.append(path + [action])

    print(f"  No solution found (visited {len(visited)} states, {iters} iters)")
    return None


if __name__ == '__main__':
    level = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    max_d = int(sys.argv[2]) if len(sys.argv) > 2 else None
    result = bfs_solve(level, max_d)
    if result:
        print(f"\nSolution found with {len(result)} actions!")
