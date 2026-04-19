"""KA59 BFS solver v2 — proper state hash with flushing."""
import sys, copy, importlib.util
from collections import deque
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('ka59', 'environment_files/ka59/9f096b4a/ka59.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

U = ActionInput(id=GameAction.ACTION1, data={})
D = ActionInput(id=GameAction.ACTION2, data={})
L = ActionInput(id=GameAction.ACTION3, data={})
R = ActionInput(id=GameAction.ACTION4, data={})
DIRS = [U, D, L, R]
DN = 'UDLR'

sys.stdout.reconfigure(line_buffering=True)


def clk_actions(g):
    ps = g.current_level.get_sprites_by_tag('xlfuqjygey')
    sel = g.ascpmvdpwj
    r = []
    for s in ps:
        if s is not sel:
            gx, gy = s.x + s.width // 2, s.y + s.height // 2
            sc, ox, oy = g.camera._calculate_scale_and_offset()
            r.append(ActionInput(id=GameAction.ACTION6, data={'x': int(gx*sc+ox), 'y': int(gy*sc+oy)}))
    return r


def get_state(g):
    ps = sorted(g.current_level.get_sprites_by_tag('xlfuqjygey'), key=lambda s: s.name)
    es = sorted(g.current_level.get_sprites_by_tag('nnckfubbhi'), key=lambda s: s.name)
    sel = g.ascpmvdpwj
    s = tuple((p.x, p.y, 1 if p is sel else 0) for p in ps)
    s += tuple((e.x, e.y) for e in es)
    z = tuple(sorted((k.name, v) for k, v in g.zhcrzgpwcp.items())) if g.zhcrzgpwcp else ()
    return s + (z, g.msbtawvatm)


def bfs(level, max_depth=50, max_iters=500000, use_clicks=True):
    g0 = mod.Ka59()
    g0.set_level(level)
    start = get_state(g0)
    print(f'L{level+1}: start={start}')

    queue = deque([(g0, [])])
    visited = {start}
    iters = 0

    while queue and iters < max_iters:
        g, path = queue.popleft()
        iters += 1
        if iters % 5000 == 0:
            print(f'  iter={iters} q={len(queue)} d={len(path)} v={len(visited)}')

        if len(path) >= max_depth:
            continue

        if g._current_level_index > level:
            names = []
            for a in path:
                if a.id == GameAction.ACTION6:
                    names.append(f'C({a.data["x"]},{a.data["y"]})')
                else:
                    names.append(DN[DIRS.index(a)])
            print(f'SOLVED! {len(path)} acts ({iters} iters, {len(visited)} states)')
            print(f'Path: {" ".join(names)}')
            return path

        actions = list(DIRS)
        if use_clicks:
            actions += clk_actions(g)

        for a in actions:
            g2 = copy.deepcopy(g)
            g2.perform_action(a)
            s = get_state(g2)
            if s not in visited:
                visited.add(s)
                queue.append((g2, path + [a]))

    print(f'No solution. v={len(visited)} iters={iters}')
    return None


if __name__ == '__main__':
    level = int(sys.argv[1])
    max_d = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    max_i = int(sys.argv[3]) if len(sys.argv) > 3 else 500000
    clicks = '--no-clicks' not in sys.argv
    bfs(level, max_d, max_i, clicks)
