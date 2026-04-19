"""Diff game state between L6 init (clickable) and L7 init (non-clickable)."""
import sys, copy
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
sys.path.insert(0, '/Users/kairos/Projects/arc-see/solutions')
from lf52_tool import LF52
from arcengine import GameAction


def dump_game_attrs(g):
    out = {}
    game = g.env._game
    for attr in dir(game):
        if attr.startswith('_'):
            continue
        try:
            v = getattr(game, attr)
            if callable(v):
                continue
            out[f"game.{attr}"] = (type(v).__name__, repr(v)[:80])
        except Exception:
            pass
    # Also ikhhdzfmarl attrs
    for attr in dir(game.ikhhdzfmarl):
        if attr.startswith('_'):
            continue
        try:
            v = getattr(game.ikhhdzfmarl, attr)
            if callable(v):
                continue
            out[f"ikh.{attr}"] = (type(v).__name__, repr(v)[:80])
        except Exception:
            pass
    return out


def cache_info(g):
    cache = g.env._game.ikhhdzfmarl._sorted_cache
    pieces = []
    for item in cache:
        s = item[1]
        nm = getattr(s, 'name', '')
        if nm.startswith('fozwvlovdui'):
            pieces.append((nm, getattr(s, 'x', -1)//6, getattr(s, 'y', -1)//6))
    return pieces


def setup_lvl(lvl_idx):
    g = LF52(up_to_level=1, verbose=False)
    g.env._game.set_level(lvl_idx)
    g.env._game.on_set_level(g.env._game.current_level)
    g.env.step(GameAction.ACTION6, data={'x': 0, 'y': 0})
    return g


def main():
    g6 = setup_lvl(5)  # L6
    g7 = setup_lvl(6)  # L7
    print(f"L6 pieces: {cache_info(g6)}", flush=True)
    print(f"L7 pieces: {cache_info(g7)}", flush=True)

    # First verify: does a piece click at L6 init change cache?
    import hashlib
    def snap(g):
        out = []
        for item in g.env._game.ikhhdzfmarl._sorted_cache:
            s = item[1]
            nm = getattr(s, 'name', '')
            x, y = getattr(s, 'x', -1), getattr(s, 'y', -1)
            out.append((item[0], nm, x, y))
        return sorted(out)

    # L6 click on piece: pieces are likely at diverse positions; click first piece
    pieces = cache_info(g6)
    if pieces:
        nm, tx, ty = pieces[0]
        ox, oy = tuple(g6.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
        s_before = snap(g6)
        print(f"L6 first-piece click on {nm} @ tile ({tx},{ty}) pix ({tx*6+3+ox},{ty*6+3+oy})", flush=True)
        g6.env.step(GameAction.ACTION6, data={'x': tx*6+3+ox, 'y': ty*6+3+oy})
        s_after = snap(g6)
        diff_added = set(s_after) - set(s_before)
        diff_removed = set(s_before) - set(s_after)
        print(f"  L6 click changed cache: {len(diff_added)} added, {len(diff_removed)} removed", flush=True)
        if diff_added or diff_removed:
            print("  ✓ L6 clicks work", flush=True)
        else:
            print("  ✗ L6 clicks ALSO do nothing", flush=True)

    # Diff game attrs between L6 and L7 init
    g6 = setup_lvl(5)  # fresh
    g7 = setup_lvl(6)
    d6 = dump_game_attrs(g6)
    d7 = dump_game_attrs(g7)

    all_keys = set(d6) | set(d7)
    print("\n=== Attrs that differ between L6 init and L7 init ===", flush=True)
    for k in sorted(all_keys):
        v6 = d6.get(k)
        v7 = d7.get(k)
        if v6 != v7:
            print(f"  {k}:\n    L6: {v6}\n    L7: {v7}", flush=True)


if __name__ == '__main__':
    main()
