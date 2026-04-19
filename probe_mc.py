"""Monte Carlo random search for L4. From the opener state, try random sequences.
Hope to stumble on the win condition."""
import copy, sys, time, random
from pathlib import Path
from collections import defaultdict, deque
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
from lf52_tool import LF52


def sm(g):
    d = defaultdict(list)
    for item in g.env._game.ikhhdzfmarl._sorted_cache:
        _, sp, _ = item
        d[getattr(sp, 'name', '')].append((sp.x, sp.y))
    return dict(d)


def piece_count(g):
    return sum(1 for item in g.env._game.ikhhdzfmarl._sorted_cache
               if getattr(item[1], 'name', '') == 'fozwvlovdui')


def g_snap(g):
    return (copy.deepcopy(g.env._game), copy.deepcopy(g.obs))


def g_restore(g, snap):
    g.env._game = copy.deepcopy(snap[0])
    g.obs = copy.deepcopy(snap[1])
    g._cached_frame = None


def all_pos(pix, c):
    ys, xs = np.where(pix == c)
    return set(zip(xs.tolist(), ys.tolist()))


def find_e_clusters(pix):
    unassigned = all_pos(pix, 14)
    clusters = []
    while unassigned:
        seed = next(iter(unassigned))
        c = {seed}
        unassigned.discard(seed)
        q = deque([seed])
        while q:
            a, b = q.popleft()
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nb = (a+dx, b+dy)
                if nb in unassigned:
                    unassigned.discard(nb)
                    c.add(nb)
                    q.append(nb)
        clusters.append(c)
    return clusters


def cluster_center(c):
    xs = [x for x,y in c]; ys = [y for x,y in c]
    return (sum(xs)//len(xs), sum(ys)//len(ys))


def find_red_clusters(pix):
    unassigned = all_pos(pix, 2)
    clusters = []
    while unassigned:
        seed = next(iter(unassigned))
        c = {seed}
        unassigned.discard(seed)
        q = deque([seed])
        while q:
            a, b = q.popleft()
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    if dx == 0 and dy == 0: continue
                    nb = (a+dx, b+dy)
                    if nb in unassigned:
                        unassigned.discard(nb)
                        c.add(nb)
                        q.append(nb)
        clusters.append(c)
    return clusters


def find_moves(g):
    """Return list of valid moves."""
    base = g_snap(g)
    pix0 = g.pixels()
    moves = []
    for a in [1, 2, 3, 4]:
        g_restore(g, base)
        try:
            pix_before = g.pixels()
            g.action(a)
            if int((pix_before != g.pixels()).sum()) > 5:
                moves.append(('A', a))
        except:
            pass
    e_clusters = find_e_clusters(pix0)
    for c in e_clusters:
        cx, cy = cluster_center(c)
        g_restore(g, base)
        try:
            g.click(cx, cy)
        except:
            continue
        red = find_red_clusters(g.pixels())
        for rc in red:
            rx, ry = cluster_center(rc)
            moves.append(('C', (cx, cy), (rx, ry)))
    g_restore(g, base)
    return moves


def apply_move(g, move):
    if move[0] == 'A':
        g.action(move[1])
    else:
        _, src, dst = move
        g.click(*src)
        red = find_red_clusters(g.pixels())
        if red:
            best = min(red, key=lambda r: abs(cluster_center(r)[0] - dst[0]) + abs(cluster_center(r)[1] - dst[1]))
            g.click(*cluster_center(best))
        else:
            g.click(*dst)


def main():
    t0 = time.time()
    best_pc = 100
    best_path = None
    max_trials = 1000
    g = LF52(up_to_level=4, verbose=False)
    init_snap = g_snap(g)

    for trial in range(max_trials):
        if time.time() - t0 > 300:  # 5 min
            break
        g_restore(g, init_snap)
        path = []
        for step_i in range(50):
            try:
                moves = find_moves(g)
                if not moves:
                    break
                move = random.choice(moves)
                apply_move(g, move)
                path.append(move)
                if g.level() > 3:
                    print(f'*** WIN trial {trial}! path-len={len(path)}', flush=True)
                    print(f'  path: {path}', flush=True)
                    return
                pc = piece_count(g)
                if pc < best_pc:
                    best_pc = pc
                    best_path = list(path)
                    print(f'trial {trial} step {step_i}: new best pc={pc}, path-len={len(path)}', flush=True)
            except Exception:
                break
        if trial % 20 == 0:
            print(f'trial {trial}: best_pc={best_pc} elapsed={time.time()-t0:.1f}s', flush=True)

    print(f'Done. best_pc={best_pc}')
    if best_path:
        print(f'Best path ({len(best_path)} actions):')
        for m in best_path:
            print(f'  {m}')


if __name__ == '__main__':
    main()
