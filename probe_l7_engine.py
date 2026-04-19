"""Dump L7 real engine state — sprites, pieces, vehicles — to verify/fix l7_sim.py."""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')

from lf52_tool import LF52
from arcengine import GameAction
import copy


def skip_to_level(g, target_level_idx):
    """Advance engine to the given level index via set_level."""
    while g.env._game._current_level_index < target_level_idx:
        g.env._game.set_level(g.env._game._current_level_index + 1)
    g.env._game.on_set_level(g.env._game.current_level)
    # Kick observation to sync
    g.obs = g.env.step(GameAction.ACTION6, data={'x': 0, 'y': 0})


def dump_state(g, label=""):
    game = g.env._game
    cache = game.ikhhdzfmarl._sorted_cache
    origin = tuple(game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
    print(f"\n=== {label} ===")
    print(f"origin: {origin}")
    print(f"level_index: {game._current_level_index}")

    by_pos = {}
    for item in cache:
        sprite = item[1]
        name = getattr(sprite, 'name', '')
        if not name:
            continue
        x = getattr(sprite, 'x', None)
        y = getattr(sprite, 'y', None)
        if x is None or y is None:
            continue
        tx, ty = x // 6, y // 6
        by_pos.setdefault((tx, ty), []).append((name, (x, y)))

    # Categorize
    pieces = []
    vehicles = []
    tracks = []
    panels = []
    dgx_cells = []
    others = []
    for (tx, ty), items in sorted(by_pos.items()):
        for name, pos in items:
            if name.startswith('fozwvlovdui'):
                pieces.append((tx, ty, name))
            elif name.startswith('hupkpseyuim2'):
                vehicles.append((tx, ty, name))
            elif name.startswith('hupkpseyuim'):
                panels.append((tx, ty, name))
            elif name.startswith('kraubslpehi'):
                tracks.append((tx, ty, name))
            elif name.startswith('dgxfozncuiz'):
                dgx_cells.append((tx, ty, name))
            else:
                others.append((tx, ty, name))
    print(f"PIECES ({len(pieces)}):")
    for p in pieces:
        print(f"  {p}")
    print(f"VEHICLES ({len(vehicles)}):")
    for v in vehicles:
        print(f"  {v}")
    print(f"DGX PIVOTS ({len(dgx_cells)}):")
    for d in dgx_cells:
        print(f"  {d}")
    print(f"PANELS ({len(panels)}):")
    for p in panels:
        print(f"  {p}")
    print(f"TRACKS ({len(tracks)}):")
    for t in tracks:
        print(f"  {t}")
    if others:
        print(f"OTHER ({len(others)}):")
        for o in others[:10]:
            print(f"  {o}")
    return by_pos


def foz_count(g):
    game = g.env._game
    cache = game.ikhhdzfmarl._sorted_cache
    total = 0
    for item in cache:
        for part in item:
            if hasattr(part, 'name') and part.name.startswith('fozwvlovdui'):
                total += 1
                break
    return total


if __name__ == '__main__':
    print("Init LF52...")
    g = LF52(up_to_level=1, verbose=False)
    # Skip to L7 (index 6 since levels are 0-indexed)
    skip_to_level(g, 6)
    print(f"foz at L7 init: {foz_count(g)}")

    # Dump EVERY cached sprite (z, name, tile pos) at specific interesting positions
    cache = g.env._game.ikhhdzfmarl._sorted_cache
    print(f"cache len: {len(cache)}")

    # Tile positions we want to check (places where sim says there's a panel)
    suspects = [(0, 1), (6, 1), (22, 6), (14, 4), (14, 5), (14, 6), (16, 5), (16, 6),
                (18, 5), (18, 6), (22, 5), (22, 6), (15, 5), (15, 6), (17, 5), (17, 6),
                (1, 8), (3, 8), (5, 8), (6, 8), (7, 8), (8, 8), (9, 8), (11, 8),
                (1, 7), (6, 7), (11, 7), (2, 8), (4, 8)]
    print(f"\nALL sprites at suspect positions:")
    for (tx, ty) in sorted(set(suspects)):
        matches = []
        for item in cache:
            s = item[1]
            nm = getattr(s, 'name', '')
            if not nm:
                continue
            x = getattr(s, 'x', -999)
            y = getattr(s, 'y', -999)
            if x // 6 == tx and y // 6 == ty:
                matches.append((item[0], nm))
        if matches:
            print(f"  ({tx}, {ty}): {matches}")
        else:
            print(f"  ({tx}, {ty}): EMPTY")

    dump_state(g, "L7 INITIAL STATE")
