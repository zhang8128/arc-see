"""L7: probe every tile position with a click; record which clicks produce state changes."""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')

import copy
import hashlib
from lf52_tool import LF52
from arcengine import GameAction


def skip_to_level(g, target_level_idx):
    while g.env._game._current_level_index < target_level_idx:
        g.env._game.set_level(g.env._game._current_level_index + 1)
    g.env._game.on_set_level(g.env._game.current_level)
    g.obs = g.env.step(GameAction.ACTION6, data={'x': 0, 'y': 0})


def snapshot(g):
    return copy.deepcopy(g.env._game)


def restore(g, snap):
    g.env._game = copy.deepcopy(snap)


def get_frame(g):
    """Return 64x64 pixels as bytes for quick hash."""
    import numpy as np
    pix = g.env._game.get_pixels(0, 0, 64, 64)
    return np.array(pix, dtype=np.int16).tobytes()


def state_hash(g):
    return hashlib.md5(get_frame(g)).hexdigest()[:8]


def describe_named_sprites(g):
    """List named sprites for quick comparison."""
    cache = g.env._game.ikhhdzfmarl._sorted_cache
    out = []
    for item in cache:
        s = item[1]
        nm = getattr(s, 'name', '')
        if not nm:
            continue
        x = getattr(s, 'x', -999)
        y = getattr(s, 'y', -999)
        out.append((nm, x // 6, y // 6))
    return sorted(out)


def main():
    print("Init LF52 at L7...")
    g = LF52(up_to_level=1, verbose=False)
    skip_to_level(g, 6)
    init_snap = snapshot(g)
    init_hash = state_hash(g)
    init_sprites = describe_named_sprites(g)
    print(f"L7 init hash: {init_hash}, {len(init_sprites)} named sprites")

    # First test: does ANY action produce a state change?
    print("\n=== ACTIONS 1-4 ===")
    for a in [1, 2, 3, 4]:
        restore(g, init_snap)
        try:
            obs = g.env.step(getattr(GameAction, f'ACTION{a}'))
            h = state_hash(g)
            if h != init_hash:
                new_sprites = describe_named_sprites(g)
                added = sorted(set(new_sprites) - set(init_sprites))
                removed = sorted(set(init_sprites) - set(new_sprites))
                print(f"ACTION{a}: hash={h}, added={added[:5]}, removed={removed[:5]}")
            else:
                print(f"ACTION{a}: NO CHANGE")
        except Exception as e:
            print(f"ACTION{a}: ERROR {e}")

    # Read viewport origin
    ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
    print(f"viewport origin: ({ox}, {oy})")

    # Probe every tile in 0..23 × 0..10 with origin offset
    print("\n=== CLICKS (with origin offset) ===")
    clickable_tiles = []
    for ty in range(11):
        for tx in range(24):
            restore(g, init_snap)
            px = tx * 6 + 3 + ox
            py = ty * 6 + 3 + oy
            try:
                obs = g.env.step(GameAction.ACTION6, data={'x': px, 'y': py})
            except Exception as e:
                continue
            new_hash = state_hash(g)
            if new_hash != init_hash:
                new_sprites = describe_named_sprites(g)
                added = sorted(set(new_sprites) - set(init_sprites))
                removed = sorted(set(init_sprites) - set(new_sprites))
                clickable_tiles.append((tx, ty, new_hash, added, removed))

    print(f"Tiles producing state change: {len(clickable_tiles)}")
    for tx, ty, h, added, removed in clickable_tiles:
        print(f"\nClick ({tx}, {ty}) → hash={h}")
        if added:
            print(f"  ADDED: {added}")
        if removed:
            print(f"  REMOVED: {removed}")


if __name__ == '__main__':
    main()
