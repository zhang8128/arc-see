"""L7: click on piece, compare cache before/after at sprite attribute level."""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
sys.path.insert(0, '/Users/kairos/Projects/arc-see/solutions')

import copy, hashlib
import numpy as np
from lf52_tool import LF52
from arcengine import GameAction
import solution_lf52_l5 as L5
import solution_lf52_l6 as L6


def setup_l7(g):
    g.env._game.set_level(4)
    g.env._game.on_set_level(g.env._game.current_level)
    g.env.step(GameAction.ACTION6, data={'x': 0, 'y': 0})
    # Run L5
    for step in L5.SOLUTION:
        if isinstance(step, str):
            a = int(step[1:])
            g.env.step(getattr(GameAction, f'ACTION{a}'))
        else:
            kind, src, direction = step
            ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
            sx, sy = src
            dx, dy = direction
            g.env.step(GameAction.ACTION6, data={'x': sx*6+3+ox, 'y': sy*6+3+oy})
            ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
            g.env.step(GameAction.ACTION6, data={'x': (sx+2*dx)*6+3+ox, 'y': (sy+2*dy)*6+3+oy})
    # Run L6
    steps = L6.parse_solution()
    for step in steps:
        if step[0] == 'A':
            a = step[1]
            g.env.step(getattr(GameAction, f'ACTION{a}'))
        else:
            _, (sx, sy), (dx, dy) = step
            ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
            g.env.step(GameAction.ACTION6, data={'x': sx*6+3+ox, 'y': sy*6+3+oy})
            ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
            g.env.step(GameAction.ACTION6, data={'x': (sx+2*dx)*6+3+ox, 'y': (sy+2*dy)*6+3+oy})


def dump_all_sprite_attrs(g):
    """Return a dict: (name, x, y) -> full attr dict."""
    out = {}
    for item in g.env._game.ikhhdzfmarl._sorted_cache:
        s = item[1]
        nm = getattr(s, 'name', '')
        if not nm:
            continue
        x, y = getattr(s, 'x', -999), getattr(s, 'y', -999)
        # Snapshot all non-private attrs
        attrs = {}
        for a in dir(s):
            if a.startswith('_'):
                continue
            try:
                v = getattr(s, a)
                if callable(v):
                    continue
                attrs[a] = v
            except Exception:
                pass
        out[(nm, x, y)] = attrs
    return out


def frame_hash(obs):
    return hashlib.md5(np.array(obs.frame[-1], dtype=np.int16).tobytes()).hexdigest()[:10]


def main():
    g = LF52(up_to_level=1, verbose=False)
    setup_l7(g)
    print(f"L7 init: level_idx={g.env._game._current_level_index}")

    snap = copy.deepcopy(g.env._game)
    attrs_before = dump_all_sprite_attrs(g)
    print(f"Sprites with attrs: {len(attrs_before)}")

    # Perform clicks at origin offset
    ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
    print(f"origin: ({ox}, {oy})")

    test_tiles = [(0, 1), (6, 1), (22, 6)]
    for tx, ty in test_tiles:
        g.env._game = copy.deepcopy(snap)
        px, py = tx * 6 + 3 + ox, ty * 6 + 3 + oy
        obs = g.env.step(GameAction.ACTION6, data={'x': px, 'y': py})
        attrs_after = dump_all_sprite_attrs(g)
        print(f"\nClick ({tx}, {ty}) @ pix ({px}, {py}):")
        print(f"  frame_hash: {frame_hash(obs)}")
        # Diff
        all_keys = set(attrs_before) | set(attrs_after)
        diffs = []
        for k in sorted(all_keys):
            a = attrs_before.get(k, {})
            b = attrs_after.get(k, {})
            for attr in set(a) | set(b):
                va = a.get(attr, '<missing>')
                vb = b.get(attr, '<missing>')
                try:
                    if isinstance(va, np.ndarray) or isinstance(vb, np.ndarray):
                        if not np.array_equal(np.asarray(va), np.asarray(vb)):
                            diffs.append((k, attr, f"arr{getattr(va,'shape','')}", f"arr{getattr(vb,'shape','')}"))
                    elif va != vb:
                        diffs.append((k, attr, va, vb))
                except Exception:
                    pass
        print(f"  {len(diffs)} attribute changes")
        for d in diffs[:15]:
            print(f"    {d}")
        if len(diffs) > 15:
            print(f"    ... +{len(diffs)-15} more")

        # Check game-level attributes that might hold selection/tally
        game = g.env._game
        for attr in ['foztuzaztfm', 'ikhhdzfmarl', 'selection', 'selected', '_tally', 'tally', '_score', 'score']:
            v = getattr(game, attr, None)
            if v is not None:
                print(f"  game.{attr} = {type(v).__name__}")


if __name__ == '__main__':
    main()
