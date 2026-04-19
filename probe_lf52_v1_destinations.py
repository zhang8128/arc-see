"""After loading v1, what happens with different A-action combos?
Goal: find sequence that moves loaded v1 to reach pieces at (30, 54) or (30, 78)."""
import copy, sys
from pathlib import Path
from collections import defaultdict, deque
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
from lf52_tool import LF52, render_png


def sprite_map(g):
    d = defaultdict(list)
    for item in g.env._game.ikhhdzfmarl._sorted_cache:
        _, sp, _ = item
        d[getattr(sp, 'name', '')].append((sp.x, sp.y))
    return d


def g_snap(g):
    return (copy.deepcopy(g.env._game), copy.deepcopy(g.obs))


def g_restore(g, snap):
    g.env._game = copy.deepcopy(snap[0])
    g.obs = copy.deepcopy(snap[1])
    g._cached_frame = None


def piece_count(g):
    return sum(1 for item in g.env._game.ikhhdzfmarl._sorted_cache
               if getattr(item[1], 'name', '') == 'fozwvlovdui')


def find_red_clusters(pix):
    from collections import deque
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


def cluster_center(cluster):
    xs = [x for x, y in cluster]
    ys = [y for x, y in cluster]
    return (sum(xs)//len(xs), sum(ys)//len(ys))


def main():
    # Load v1 with A3 positioning
    g = LF52(up_to_level=4, verbose=False)
    for step in [('C',(13,25),(25,25)),('C',(25,25),(37,25)),('A',3),('C',(37,25),(49,25))]:
        if step[0] == 'C': g.click(*step[1]); g.click(*step[2])
        else: g.action(step[1])

    print('Just loaded:')
    sm = sprite_map(g)
    print(f'  foz: {sorted(sm["fozwvlovdui"])}')
    print(f'  h2: {sorted(sm["hupkpseyuim2"])}')
    loaded = g_snap(g)

    # Test many A-action sequences to drive v1 and observe unload options
    print('\n=== Drive v1 via various A-sequences, find unload destinations ===')
    sequences = []
    # single A4 and A3 series
    for n in range(0, 16):
        sequences.append((f'A4x{n}' if n else '', [4]*n))
        sequences.append((f'A3x{n}' if n else '', [3]*n))
    # mixes
    for n3 in range(0, 4):
        for n4 in range(0, 4):
            if n3 == 0 and n4 == 0: continue
            name = f'A3x{n3}+A4x{n4}'
            sequences.append((name, [3]*n3 + [4]*n4))
            sequences.append((f'A4x{n4}+A3x{n3}', [4]*n4 + [3]*n3))

    seen_outcomes = {}
    from collections import deque
    print(f'sequences: {len(sequences)}', flush=True)
    for idx, (seq_name, aseq) in enumerate(sequences):
        print(f'  [{idx}/{len(sequences)}] trying {seq_name}', flush=True)
        g_restore(g, loaded)
        try:
            for act in aseq:
                g.action(act)
        except Exception as e:
            print(f'{seq_name}: exception in actions: {e}', flush=True)
            continue
        sm = sprite_map(g)
        foz_pos = tuple(sorted(sm['fozwvlovdui']))
        init_foz = {(6, 18), (30, 54), (30, 78), (36, 18), (72, 18), (96, 18)}
        loaded_foz = set(foz_pos) - init_foz
        pix = g.pixels()
        ys, xs = np.where(pix == 14)
        unassigned = set(zip(xs.tolist(), ys.tolist()))
        e_clusters = []
        while unassigned:
            seed = next(iter(unassigned))
            cc = {seed}
            unassigned.discard(seed)
            q = deque([seed])
            while q:
                a, b = q.popleft()
                for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nb = (a+dx, b+dy)
                    if nb in unassigned:
                        unassigned.discard(nb)
                        cc.add(nb)
                        q.append(nb)
            e_clusters.append(cc)
        snap2 = g_snap(g)
        all_unload_dests = set()
        for cluster in e_clusters:
            cx, cy = cluster_center(cluster)
            g_restore(g, snap2)
            g.click(cx, cy)
            red_clusters = find_red_clusters(g.pixels())
            for rc in red_clusters:
                rx, ry = cluster_center(rc)
                all_unload_dests.add((cx, cy, rx, ry))
        key = (tuple(sorted(loaded_foz)), tuple(sorted(all_unload_dests)))
        if key not in seen_outcomes:
            seen_outcomes[key] = seq_name
            print(f'{seq_name:20s}: loaded@{sorted(loaded_foz)}, unload-options={len(all_unload_dests)}: {sorted(all_unload_dests)[:5]}', flush=True)


if __name__ == '__main__':
    main()
