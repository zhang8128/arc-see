"""KA59 L7 solver — BFS with checkpoint replay for deep search.

Uses FIFO BFS (not A*) to avoid heuristic misdirection.
Checkpoints every 10 depths to reduce deepcopy overhead.
"""
import sys, copy, time, importlib.util
from collections import deque
from arcengine import GameAction, ActionInput

sys.stdout.reconfigure(line_buffering=True)

spec = importlib.util.spec_from_file_location('ka59', 'environment_files/ka59/9f096b4a/ka59.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

U = ActionInput(id=GameAction.ACTION1, data={})
D = ActionInput(id=GameAction.ACTION2, data={})
L = ActionInput(id=GameAction.ACTION3, data={})
R = ActionInput(id=GameAction.ACTION4, data={})
DIRS = [U, D, L, R]
DN = 'UDLR'
CKPT = 10  # checkpoint interval
MAX_DEPTH = 326
MAX_ITERS = 10_000_000


def get_state(g):
    ps = sorted(g.current_level.get_sprites_by_tag('xlfuqjygey'), key=lambda s: s.name)
    es = sorted(g.current_level.get_sprites_by_tag('nnckfubbhi'), key=lambda s: s.name)
    sel = g.ascpmvdpwj
    s = tuple((p.x, p.y, 1 if p is sel else 0) for p in ps)
    s += tuple((e.x, e.y) for e in es)
    z = tuple(sorted((k.name, v) for k, v in g.zhcrzgpwcp.items())) if g.zhcrzgpwcp else ()
    return s + (z, g.msbtawvatm)


def get_clicks(g):
    ps = g.current_level.get_sprites_by_tag('xlfuqjygey')
    sel = g.ascpmvdpwj
    r = []
    for s in ps:
        if s is not sel:
            gx, gy = s.x + s.width // 2, s.y + s.height // 2
            sc, ox, oy = g.camera._calculate_scale_and_offset()
            r.append(ActionInput(id=GameAction.ACTION6, data={'x': int(gx*sc+ox), 'y': int(gy*sc+oy)}))
    return r


def replay(g_base, actions):
    """Replay actions from a checkpoint."""
    g = copy.deepcopy(g_base)
    for a in actions:
        g.perform_action(a)
    return g


def solve():
    g0 = mod.Ka59()
    g0.set_level(6)
    start = get_state(g0)
    t0 = time.time()

    # Queue entries: (checkpoint_game, actions_since_checkpoint, full_action_list)
    # To save memory: store actions as tuples of indices
    checkpoints = {0: copy.deepcopy(g0)}
    queue = deque()
    queue.append((0, ()))  # (checkpoint_depth, actions_since_ckpt as tuple of action indices)
    visited = {start}
    iters = 0
    best_ey = 9
    full_paths = {start: ()}  # state -> full action tuple

    print(f'L7 BFS starting. Max depth: {MAX_DEPTH}', flush=True)

    while queue and iters < MAX_ITERS:
        ckpt_depth, actions_since = queue.popleft()
        depth = ckpt_depth + len(actions_since)
        iters += 1

        if iters % 10000 == 0:
            t = time.time() - t0
            rate = iters / t if t > 0 else 0
            print(f'iter={iters:,} q={len(queue):,} d={depth} v={len(visited):,} ckpts={len(checkpoints)} ey={best_ey} rate={rate:.0f}/s t={t:.0f}s', flush=True)

        if depth >= MAX_DEPTH:
            continue

        # Reconstruct game state
        nearest_ckpt = (depth // CKPT) * CKPT
        if nearest_ckpt > ckpt_depth:
            nearest_ckpt = ckpt_depth
        base = checkpoints.get(ckpt_depth)
        if base is None:
            continue  # checkpoint was pruned
        g = replay(base, [resolve_idx(i) for i in actions_since])

        # Check win
        if g._current_level_index > 6:
            # Reconstruct full path
            state = get_state(g)
            full = full_paths.get(state, actions_since)
            names = [action_name(resolve_idx(i)) for i in full]
            print(f'SOLVED! {len(full)} actions ({iters} iters)', flush=True)
            print(f'Path: {" ".join(names)}', flush=True)
            return

        # Track enemy
        es = g.current_level.get_sprites_by_tag('nnckfubbhi')
        if es and es[0].y > best_ey:
            best_ey = es[0].y
            t = time.time() - t0
            print(f'  ** enemy y={best_ey} at depth={depth} iter={iters} t={t:.0f}s', flush=True)

        # Maybe create checkpoint
        new_ckpt_depth = depth
        if depth % CKPT == 0 and depth not in checkpoints:
            checkpoints[depth] = copy.deepcopy(g)

        # Expand
        all_actions = list(range(4)) + list(range(4, 4 + len(get_clicks(g))))
        for ai in all_actions:
            a = resolve_idx(ai) if ai < 4 else get_clicks(g)[ai - 4]
            g2 = copy.deepcopy(g)
            g2.perform_action(a)
            s = get_state(g2)
            if s not in visited:
                visited.add(s)
                new_actions = actions_since + (ai,)
                # Determine checkpoint for new entry
                new_depth = depth + 1
                new_ckpt = (new_depth // CKPT) * CKPT
                if new_ckpt <= ckpt_depth:
                    queue.append((ckpt_depth, new_actions))
                elif new_ckpt in checkpoints:
                    # Actions from the new checkpoint
                    actions_from_new = new_actions[new_ckpt - ckpt_depth:]
                    queue.append((new_ckpt, actions_from_new))
                else:
                    queue.append((ckpt_depth, new_actions))
                full_paths[s] = new_actions  # approximate

    print(f'No solution found. iters={iters}, visited={len(visited)}', flush=True)


def resolve_idx(i):
    if i < 4:
        return DIRS[i]
    return None  # clicks need game context


def action_name(a):
    if a is None:
        return 'C'
    if a in DIRS:
        return DN[DIRS.index(a)]
    return f'C({a.data.get("x")},{a.data.get("y")})'


if __name__ == '__main__':
    solve()
