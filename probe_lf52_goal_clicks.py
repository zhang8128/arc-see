"""Click directly on goal marker positions and test various state transitions.
Also test A7 (undo) for special behaviors."""
import copy, sys
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


def find_red_clusters(pix):
    ys, xs = np.where(pix == 2)
    unassigned = set(zip(xs.tolist(), ys.tolist()))
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


def apply_seq(g, seq):
    for step in seq:
        if step[0] == 'C':
            g.click(*step[1]); g.click(*step[2])
        else:
            g.action(step[1])


def main():
    # State: load+A3x4+A2x2. h2 at (24, 66), (42, 18), (48, 54)
    g = LF52(up_to_level=4, verbose=False)
    seq = [('C',(13,25),(25,25)),('C',(25,25),(37,25)),('A',3),('C',(37,25),(49,25))]
    seq += [('A',3)]*4 + [('A',2)]*2
    apply_seq(g, seq)
    pc0 = piece_count(g)
    print(f'State: pc={pc0}, foz={sorted(sm(g)["fozwvlovdui"])}')
    print(f'       h2={sorted(sm(g)["hupkpseyuim2"])}')
    print(f'       kraubslpehi: main={sm(g).get("kraubslpehi")} <={sm(g).get("kraubslpehi-<")} up={sm(g).get("kraubslpehi-up")}')

    base = g_snap(g)

    # Goal markers in world: (24, 18), (48, 42), (48, 48)
    # In viewport, where would these render? If 1:1 world→viewport mapping, those coords
    print()
    print('=== Click all 64x64 positions and report hits ===')
    hits_by_pos = {}
    for cy in range(0, 64):
        for cx in range(0, 64):
            g_restore(g, base)
            try:
                g.click(cx, cy)
            except Exception:
                continue
            pc_new = piece_count(g)
            pix = g.pixels()
            red = find_red_clusters(pix)
            lvl = g.level()
            if pc_new != pc0 or lvl > 3 or (red and (cx > 20 or cy > 30)):
                hits_by_pos[(cx, cy)] = {'pc': pc_new, 'lvl': lvl, 'red': len(red)}
    print(f'Interesting hits: {len(hits_by_pos)}')
    for pos, info in hits_by_pos.items():
        print(f'  click{pos}: {info}')

    # A7 (undo) testing
    print()
    print('=== A7 from post-load state ===')
    g_restore(g, base)
    pix_before = g.pixels()
    try:
        g.action(7)
        pix_after = g.pixels()
        diff = int((pix_before != pix_after).sum())
        pc_new = piece_count(g)
        print(f'A7: diff={diff} pc={pc_new} foz={sorted(sm(g)["fozwvlovdui"])}')
    except Exception as e:
        print(f'A7: ERROR {e}')


if __name__ == '__main__':
    main()
