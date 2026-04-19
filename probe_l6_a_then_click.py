"""Test: does A2 A2 at L6 init unlock clicks? (The first 2 actions of L6 solution)"""
import sys, copy
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
sys.path.insert(0, '/Users/kairos/Projects/arc-see/solutions')
from lf52_tool import LF52
from arcengine import GameAction


def foz(g):
    return sum(1 for i in g.env._game.ikhhdzfmarl._sorted_cache
               if getattr(i[1],'name','').startswith('fozwvlovdui'))


def try_click(g, tx, ty, label=""):
    import hashlib
    def ch(g):
        d = []
        for item in g.env._game.ikhhdzfmarl._sorted_cache:
            s = item[1]
            nm = getattr(s, 'name', '')
            x, y = getattr(s, 'x', -1), getattr(s, 'y', -1)
            d.append((item[0], nm, x, y))
        return hashlib.md5(repr(sorted(d)).encode()).hexdigest()[:8]
    snap = copy.deepcopy(g.env._game)
    h_before = ch(g)
    fz_before = foz(g)
    ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
    g.env.step(GameAction.ACTION6, data={'x': tx*6+3+ox, 'y': ty*6+3+oy})
    h_after = ch(g)
    fz_after = foz(g)
    worked = h_before != h_after
    print(f"  {label} click ({tx},{ty}): {h_before}→{h_after} foz {fz_before}→{fz_after} {'✓' if worked else '✗'}", flush=True)
    g.env._game = copy.deepcopy(snap)
    return worked


def main():
    # L6 init: piece at (2, 2) etc
    g = LF52(up_to_level=1, verbose=False)
    g.env._game.set_level(5)  # L6
    g.env._game.on_set_level(g.env._game.current_level)
    g.env.step(GameAction.ACTION6, data={'x': 0, 'y': 0})

    print(f"L6 init: foz={foz(g)}", flush=True)

    # Test clicks BEFORE A-actions
    print("\n=== L6 init, no A-actions ===", flush=True)
    try_click(g, 2, 2, "fresh")
    try_click(g, 2, 3, "fresh")

    # After A2
    print("\n=== L6 + A2 ===", flush=True)
    snap = copy.deepcopy(g.env._game)
    g.env.step(GameAction.ACTION2)
    try_click(g, 2, 2, "A2")
    try_click(g, 2, 3, "A2")
    g.env._game = copy.deepcopy(snap)

    # After A2 A2
    print("\n=== L6 + A2 A2 ===", flush=True)
    g.env.step(GameAction.ACTION2)
    g.env.step(GameAction.ACTION2)
    try_click(g, 2, 2, "A2 A2")
    try_click(g, 2, 3, "A2 A2")
    # Then test THE full L6 first chain
    print("\n=== L6 + A2 A2 + chain click (2, 2)→(2, 4) ===", flush=True)
    snap2 = copy.deepcopy(g.env._game)
    # Click source (2, 2)
    ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
    g.env.step(GameAction.ACTION6, data={'x': 2*6+3+ox, 'y': 2*6+3+oy})
    # Click dest (2, 4)
    ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
    g.env.step(GameAction.ACTION6, data={'x': 2*6+3+ox, 'y': 4*6+3+oy})
    print(f"  After chain (2,2)→(2,4): foz={foz(g)}", flush=True)
    g.env._game = copy.deepcopy(snap2)


if __name__ == '__main__':
    main()
