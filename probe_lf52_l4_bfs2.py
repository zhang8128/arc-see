"""BFS from L4 init with proper hint deduplication and deeper search."""
import copy
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
from lf52_tool import LF52


def all_pos(pix, c):
    ys, xs = np.where(pix == c)
    return set(zip(xs.tolist(), ys.tolist()))


def group_pos(positions, max_dist=1):
    """Group with orthogonal adjacency by default. Use max_dist=2 for Chebyshev."""
    unassigned = set(positions)
    clusters = []
    while unassigned:
        seed = next(iter(unassigned))
        cluster = [seed]
        unassigned.remove(seed)
        frontier = [seed]
        while frontier:
            cx, cy = frontier.pop()
            # Check all cells within max_dist
            for dx in range(-max_dist, max_dist + 1):
                for dy in range(-max_dist, max_dist + 1):
                    if dx == 0 and dy == 0:
                        continue
                    nb = (cx + dx, cy + dy)
                    if nb in unassigned:
                        unassigned.remove(nb)
                        cluster.append(nb)
                        frontier.append(nb)
        clusters.append(cluster)
    return clusters


def centers(positions, max_dist=1):
    return sorted((sum(p[0] for p in c)//len(c), sum(p[1] for p in c)//len(c), len(c))
                  for c in group_pos(positions, max_dist))


def g_snap(g):
    return (copy.deepcopy(g.env._game), copy.deepcopy(g.obs))


def g_restore(g, snap):
    g.env._game = copy.deepcopy(snap[0])
    g.obs = copy.deepcopy(snap[1])
    g._cached_frame = None


def state_key(g):
    return hash(tuple(g.pixels().ravel().tolist()))


def find_moves(g):
    """Unique moves. Red hints clustered with Chebyshev distance 2 to treat cross-pattern as 1."""
    base = g_snap(g)
    pix0 = g.pixels()
    moves = []

    for a in [1, 2, 3, 4]:
        g_restore(g, base)
        try:
            g.action(a)
            if int((g.pixels() != pix0).sum()) > 5:
                moves.append(('A', a))
        except Exception:
            pass

    e_clusters = centers(all_pos(pix0, 14), max_dist=1)
    for cx, cy, sz in e_clusters:
        g_restore(g, base)
        try:
            g.click(cx, cy)
        except Exception:
            continue
        pix_after_sel = g.pixels()
        red = all_pos(pix_after_sel, 2)
        # Cluster with distance-2 (cross patterns)
        red_clusters = centers(red, max_dist=2)
        for rx, ry, rsz in red_clusters:
            moves.append(('C', (cx, cy), (rx, ry)))

    g_restore(g, base)
    return moves


def apply_move(g, move):
    if move[0] == 'A':
        g.action(move[1])
    else:
        g.click(*move[1])
        g.click(*move[2])


def best_effort_click_coord(g, cx, cy):
    """Try to find a red cell near (cx, cy) since hint is cross-pattern center."""
    pix = g.pixels()
    red = all_pos(pix, 2)
    if (cx, cy) in red:
        return (cx, cy)
    # Find nearest red cell
    best = None
    best_d = 1e9
    for rx, ry in red:
        d = abs(rx - cx) + abs(ry - cy)
        if d < best_d:
            best_d = d
            best = (rx, ry)
    return best if best else (cx, cy)


def apply_move_safe(g, move):
    if move[0] == 'A':
        g.action(move[1])
    else:
        _, src, dst = move
        g.click(*src)
        actual_dst = best_effort_click_coord(g, *dst)
        g.click(*actual_dst)


def main():
    t0 = time.time()
    g = LF52(up_to_level=4, verbose=False)
    init_snap = g_snap(g)

    frontier = [(init_snap, [])]
    seen = {state_key(g)}

    MAX_DEPTH = 12
    depth = 0
    win_path = None

    while frontier and depth < MAX_DEPTH:
        depth += 1
        new_frontier = []
        for snap, path in frontier:
            g_restore(g, snap)
            moves = find_moves(g)
            for move in moves:
                g_restore(g, snap)
                try:
                    apply_move_safe(g, move)
                except Exception:
                    continue
                lvl = g.level()
                if lvl > 3:
                    print(f'*** WIN at depth {depth}! path={path + [move]}')
                    return path + [move]
                key = state_key(g)
                if key not in seen:
                    seen.add(key)
                    new_frontier.append((g_snap(g), path + [move]))
        elapsed = time.time() - t0
        print(f'Depth {depth}: frontier size={len(new_frontier)}, total seen={len(seen)}, elapsed={elapsed:.1f}s')
        frontier = new_frontier

    print(f'\nNo win in {MAX_DEPTH} depth levels.')
    # Report deepest unique states sampled
    for i, (snap, path) in enumerate(frontier[:10]):
        g_restore(g, snap)
        pix = g.pixels()
        e = int((pix == 14).sum())
        sev = int((pix == 7).sum())
        print(f'  sample {i}: e={e} 7={sev} lvl={g.level()} path-len={len(path)}: {path[-3:] if len(path) > 3 else path}')


if __name__ == '__main__':
    main()
