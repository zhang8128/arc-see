"""Improved cache diff probe — runs fully in-project, flushes output."""
import sys, copy
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
sys.path.insert(0, '/Users/kairos/Projects/arc-see/solutions')
from lf52_tool import LF52
from arcengine import GameAction
import solution_lf52_l5 as L5
import solution_lf52_l6 as L6

print("start", flush=True)


def setup_l7(g):
    g.env._game.set_level(6)
    g.env._game.on_set_level(g.env._game.current_level)
    g.env.step(GameAction.ACTION6, data={'x': 0, 'y': 0})
    print(f"  at L7 via set_level directly, idx={g.env._game._current_level_index}", flush=True)


def cache_snapshot(g):
    out = set()
    for item in g.env._game.ikhhdzfmarl._sorted_cache:
        s = item[1]
        nm = getattr(s, 'name', '')
        x = getattr(s, 'x', -999)
        y = getattr(s, 'y', -999)
        z = item[0]
        out.add((z, nm, x, y))
    return out


def test_click_pair(g, src, dst):
    """Click src and dst in sequence; report cache changes."""
    snap = copy.deepcopy(g.env._game)
    init_sprites = cache_snapshot(g)
    ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
    sx, sy = src
    g.env.step(GameAction.ACTION6, data={'x': sx*6+3+ox, 'y': sy*6+3+oy})
    post_src = cache_snapshot(g)
    added = post_src - init_sprites
    removed = init_sprites - post_src
    print(f"\n=== Click src ({sx},{sy}) @pix ({sx*6+3+ox},{sy*6+3+oy}) ===", flush=True)
    print(f"  cache {len(init_sprites)} → {len(post_src)} sprites", flush=True)
    if added:
        print(f"  ADDED ({len(added)}):", flush=True)
        for a in sorted(added)[:20]:
            print(f"    {a}", flush=True)
    if removed:
        print(f"  REMOVED ({len(removed)}):", flush=True)
        for r in sorted(removed)[:20]:
            print(f"    {r}", flush=True)
    if not added and not removed:
        print("  (no cache changes)", flush=True)
    if dst:
        dxx, dyy = dst
        ox2, oy2 = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
        g.env.step(GameAction.ACTION6, data={'x': dxx*6+3+ox2, 'y': dyy*6+3+oy2})
        post_dst = cache_snapshot(g)
        added2 = post_dst - post_src
        removed2 = post_src - post_dst
        print(f"=== Click dst ({dxx},{dyy}) ===", flush=True)
        print(f"  cache {len(post_src)} → {len(post_dst)}", flush=True)
        if added2:
            print(f"  ADDED ({len(added2)}):", flush=True)
            for a in sorted(added2)[:20]:
                print(f"    {a}", flush=True)
        if removed2:
            print(f"  REMOVED ({len(removed2)}):", flush=True)
            for r in sorted(removed2)[:20]:
                print(f"    {r}", flush=True)
    g.env._game = copy.deepcopy(snap)


def main():
    g = LF52(up_to_level=1, verbose=False)
    print("init done", flush=True)
    setup_l7(g)
    print(f"L7 cache: {len(cache_snapshot(g))} sprites", flush=True)

    test_click_pair(g, (0, 1), (0, 3))
    test_click_pair(g, (0, 1), (2, 1))
    test_click_pair(g, (6, 1), (6, 3))
    test_click_pair(g, (22, 6), (22, 4))
    # Also try click on DGX cells
    test_click_pair(g, (0, 2), None)
    test_click_pair(g, (13, 3), None)
    # And on vehicles
    test_click_pair(g, (5, 5), None)
    test_click_pair(g, (19, 2), None)
    print("done", flush=True)


if __name__ == '__main__':
    main()
