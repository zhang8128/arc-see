"""Critical test: does L7 init (via legit L5+L6 wins) differ from L7 init (via set_level skip)?
If yes, the click-enabling mechanism lies in the legit win path."""
import sys, copy
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
sys.path.insert(0, '/Users/kairos/Projects/arc-see/solutions')
from lf52_tool import LF52
from arcengine import GameAction
import solution_lf52_l5 as L5
import solution_lf52_l6 as L6

print("start", flush=True)


def legit_path():
    g = LF52(up_to_level=1, verbose=False)
    g.env._game.set_level(4)
    g.env._game.on_set_level(g.env._game.current_level)
    g.env.step(GameAction.ACTION6, data={'x': 0, 'y': 0})
    for step in L5.SOLUTION:
        if isinstance(step, str):
            g.env.step(getattr(GameAction, f'ACTION{int(step[1:])}'))
        else:
            kind, src, direction = step
            ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
            sx, sy = src; dx, dy = direction
            g.env.step(GameAction.ACTION6, data={'x': sx*6+3+ox, 'y': sy*6+3+oy})
            ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
            g.env.step(GameAction.ACTION6, data={'x': (sx+2*dx)*6+3+ox, 'y': (sy+2*dy)*6+3+oy})
    for step in L6.parse_solution():
        if step[0] == 'A':
            g.env.step(getattr(GameAction, f'ACTION{step[1]}'))
        else:
            _, (sx, sy), (dx, dy) = step
            ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
            g.env.step(GameAction.ACTION6, data={'x': sx*6+3+ox, 'y': sy*6+3+oy})
            ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
            g.env.step(GameAction.ACTION6, data={'x': (sx+2*dx)*6+3+ox, 'y': (sy+2*dy)*6+3+oy})
    return g


def skip_path():
    g = LF52(up_to_level=1, verbose=False)
    g.env._game.set_level(6)
    g.env._game.on_set_level(g.env._game.current_level)
    g.env.step(GameAction.ACTION6, data={'x': 0, 'y': 0})
    return g


def cache_detail(g):
    """Full cache details: z, name, x, y, type(name) for all entries."""
    out = []
    for item in g.env._game.ikhhdzfmarl._sorted_cache:
        s = item[1]
        nm = getattr(s, 'name', '')
        x, y = getattr(s, 'x', -1), getattr(s, 'y', -1)
        # Also check visibility, etc
        vis = getattr(s, 'visible', None)
        ttag = getattr(s, '_tags', None)  # tags (might be set by engine)
        out.append((item[0], nm, x, y, vis))
    return sorted(out)


def try_click(g, tile_x, tile_y, label=""):
    """Click a tile; return (cache-size before, cache-size after, whether any named sprites added)."""
    import hashlib
    def cache_hash(g):
        details = cache_detail(g)
        return len(details), hashlib.md5(repr(details).encode()).hexdigest()[:8]
    n_before, h_before = cache_hash(g)
    ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
    snap = copy.deepcopy(g.env._game)
    g.env.step(GameAction.ACTION6, data={'x': tile_x*6+3+ox, 'y': tile_y*6+3+oy})
    n_after, h_after = cache_hash(g)
    print(f"  {label} click ({tile_x},{tile_y}): {n_before}→{n_after} sprites, hash {h_before}→{h_after}{' CHANGED' if h_before != h_after else ''}", flush=True)
    g.env._game = copy.deepcopy(snap)


def main():
    print("\n=== LEGIT PATH (play L5+L6) ===", flush=True)
    g1 = legit_path()
    detail1 = cache_detail(g1)
    print(f"L7 cache (legit): {len(detail1)} sprites", flush=True)
    # Pieces?
    pieces1 = [d for d in detail1 if d[1].startswith('fozwvlovdui')]
    print(f"pieces: {pieces1}", flush=True)
    # Try clicks
    try_click(g1, 0, 1, "legit")
    try_click(g1, 6, 1, "legit")
    try_click(g1, 22, 6, "legit")
    try_click(g1, 5, 5, "legit")

    print("\n=== SKIP PATH (set_level) ===", flush=True)
    g2 = skip_path()
    detail2 = cache_detail(g2)
    print(f"L7 cache (skip): {len(detail2)} sprites", flush=True)
    pieces2 = [d for d in detail2 if d[1].startswith('fozwvlovdui')]
    print(f"pieces: {pieces2}", flush=True)
    try_click(g2, 0, 1, "skip")
    try_click(g2, 6, 1, "skip")
    try_click(g2, 22, 6, "skip")

    # DIFF: are caches identical?
    set1 = {(d[1], d[2], d[3]) for d in detail1}  # ignore z/vis
    set2 = {(d[1], d[2], d[3]) for d in detail2}
    diff1 = set1 - set2
    diff2 = set2 - set1
    print(f"\nLegit has {len(diff1)} sprites skip doesn't:", flush=True)
    for d in sorted(diff1)[:10]:
        print(f"  {d}", flush=True)
    print(f"\nSkip has {len(diff2)} sprites legit doesn't:", flush=True)
    for d in sorted(diff2)[:10]:
        print(f"  {d}", flush=True)


if __name__ == '__main__':
    main()
