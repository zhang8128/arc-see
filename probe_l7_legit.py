"""LF52 L7 comprehensive probe from LEGIT state (L1-L6 played through).

Uses _sorted_cache for sprite access (correct API for this engine version).
"""
import sys
import copy
import hashlib
import numpy as np
from collections import deque

sys.path.insert(0, '/Users/kairos/Projects/arc-see')
from lf52_tool import LF52
from arcengine import GameAction


def get_sprites(game):
    """Get all visible sprites from _sorted_cache."""
    scene = game.env._game.ikhhdzfmarl
    sprites = []
    for entry in scene._sorted_cache:
        z, s = entry[0], entry[1]
        if s.visible:
            sprites.append({
                'z': z, 'name': s.name, 'x': s.x, 'y': s.y,
                'w': getattr(s, 'width', 0), 'h': getattr(s, 'height', 0),
            })
    return sprites


def get_viewport(game):
    """Get viewport offset."""
    try:
        return tuple(game.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
    except:
        return (0, 0)


def world_to_screen(wx, wy, vp):
    """Convert world coords to screen/viewport coords."""
    return wx + vp[0], wy + vp[1]


def pixel_hash(game):
    pix = np.array(game.env._game.get_pixels(0, 0, 64, 64), dtype=np.int16)
    return hashlib.md5(pix.tobytes()).hexdigest()


def get_pixels(game):
    return np.array(game.env._game.get_pixels(0, 0, 64, 64), dtype=np.int16)


def click_diff(game, x, y):
    """Click at screen (x,y), return (pixel_diff_count, color3_delta)."""
    pre = get_pixels(game)
    c3_pre = int((pre == 3).sum())
    game.env.step(GameAction.ACTION6, data={'x': x, 'y': y})
    post = get_pixels(game)
    c3_post = int((post == 3).sum())
    diff = int(np.sum(pre != post))
    return diff, c3_post - c3_pre


def get_foz_info(game):
    """Get foz pieces with positions."""
    sprites = get_sprites(game)
    foz = [(s['x'], s['y'], s['name']) for s in sprites if 'fozwvlovdui' in s['name']]
    return foz


def get_vehicles(game):
    sprites = get_sprites(game)
    return [(s['x'], s['y'], s['name']) for s in sprites if 'hupkpseyuim' in s['name']]


def get_dgx(game):
    sprites = get_sprites(game)
    return [(s['x'], s['y'], s['name']) for s in sprites if 'dgx' in s['name']]


def apply_action(game, a):
    game.env.step(getattr(GameAction, f'ACTION{a}'))


def main():
    print("=" * 60)
    print("LF52 L7 LEGIT STATE PROBE v2")
    print("=" * 60)

    print("\n[1] Building legit L7 state via L1-L6 pipeline...")
    game = LF52(up_to_level=7, verbose=False)
    level = game.env._game._current_level_index
    print(f"  Level index: {level}")

    vp = get_viewport(game)
    print(f"  Viewport: {vp}")

    # State dump
    print("\n[2] L7 INIT STATE DUMP")
    print("-" * 40)

    foz = get_foz_info(game)
    print(f"  Foz pieces ({len(foz)}):")
    for fx, fy, fn in foz:
        sx, sy = world_to_screen(fx, fy, vp)
        print(f"    world=({fx},{fy}) screen=({sx},{sy}) name={fn}")

    vehicles = get_vehicles(game)
    print(f"  Vehicles ({len(vehicles)}):")
    for vx, vy, vn in vehicles:
        sx, sy = world_to_screen(vx, vy, vp)
        co_foz = any(fx == vx and fy == vy for fx, fy, _ in foz)
        tag = " *** CO-LOCATED WITH FOZ" if co_foz else ""
        print(f"    world=({vx},{vy}) screen=({sx},{sy}) name={vn}{tag}")

    dgx = get_dgx(game)
    print(f"  DGX pivots ({len(dgx)}):")
    for dx, dy, dn in dgx:
        sx, sy = world_to_screen(dx, dy, vp)
        print(f"    world=({dx},{dy}) screen=({sx},{sy})")

    # Game internals
    print("\n[3] GAME INTERNALS")
    g = game.env._game
    try:
        print(f"  ddaguepwkt: {g.ddaguepwkt}")
    except:
        print("  ddaguepwkt: N/A")
    try:
        print(f"  btiyglcumku: {g.btiyglcumku}")
    except:
        print("  btiyglcumku: N/A")
    try:
        print(f"  apiwkxksucg: {g.apiwkxksucg}")
    except:
        pass
    try:
        print(f"  State: {g._state}")
    except:
        pass

    # Color distribution
    pix = get_pixels(game)
    unique, counts = np.unique(pix, return_counts=True)
    print(f"  Colors: {dict(zip(unique.tolist(), counts.tolist()))}")

    # Save init snapshot
    init_snap = copy.deepcopy(game.env._game)

    # Try clicking pieces at screen coords
    print("\n[4] CLICK PROBE AT INIT - PIECES")
    print("-" * 40)
    for fx, fy, fn in foz:
        game.env._game = copy.deepcopy(init_snap)
        sx, sy = world_to_screen(fx, fy, vp)
        if 0 <= sx < 64 and 0 <= sy < 64:
            diff, c3d = click_diff(game, sx, sy)
            print(f"  Click foz screen=({sx},{sy}): diff={diff}, c3_delta={c3d}")
            # Also try center of sprite (offset by 3 for 6x6 tiles)
            for ox, oy in [(3, 3), (0, 0), (5, 5), (1, 1)]:
                game.env._game = copy.deepcopy(init_snap)
                tx, ty = sx + ox, sy + oy
                if 0 <= tx < 64 and 0 <= ty < 64:
                    diff2, c3d2 = click_diff(game, tx, ty)
                    if diff2 != diff:
                        print(f"    Offset ({ox},{oy}) -> ({tx},{ty}): diff={diff2}, c3_delta={c3d2}")

    # Try clicking vehicles
    print("\n[5] CLICK PROBE AT INIT - VEHICLES")
    print("-" * 40)
    for vx, vy, vn in vehicles:
        game.env._game = copy.deepcopy(init_snap)
        sx, sy = world_to_screen(vx, vy, vp)
        if 0 <= sx < 64 and 0 <= sy < 64:
            diff, c3d = click_diff(game, sx, sy)
            print(f"  Click vehicle screen=({sx},{sy}) [{vn[:25]}]: diff={diff}, c3_delta={c3d}")
            for ox, oy in [(3, 3), (1, 1)]:
                game.env._game = copy.deepcopy(init_snap)
                tx, ty = sx + ox, sy + oy
                if 0 <= tx < 64 and 0 <= ty < 64:
                    diff2, c3d2 = click_diff(game, tx, ty)
                    if diff2 != diff:
                        print(f"    Offset ({ox},{oy}) -> ({tx},{ty}): diff={diff2}, c3_delta={c3d2}")

    # Try clicking DGX
    print("\n[6] CLICK PROBE AT INIT - DGX")
    print("-" * 40)
    for dx, dy, dn in dgx:
        game.env._game = copy.deepcopy(init_snap)
        sx, sy = world_to_screen(dx, dy, vp)
        if 0 <= sx < 64 and 0 <= sy < 64:
            diff, c3d = click_diff(game, sx, sy)
            if diff > 1:
                print(f"  Click DGX screen=({sx},{sy}): diff={diff}, c3_delta={c3d}")

    # Try clicking tracks
    print("\n[7] CLICK PROBE AT INIT - TRACKS")
    print("-" * 40)
    sprites = get_sprites(game)
    tracks = [(s['x'], s['y'], s['name']) for s in sprites if 'kraubslpehi' in s['name']]
    best_track_diff = 0
    for tx, ty, tn in tracks:
        game.env._game = copy.deepcopy(init_snap)
        sx, sy = world_to_screen(tx, ty, vp)
        if 0 <= sx < 64 and 0 <= sy < 64:
            diff, c3d = click_diff(game, sx, sy)
            if diff > best_track_diff:
                best_track_diff = diff
                print(f"  Click track screen=({sx},{sy}) [{tn}]: diff={diff}, c3_delta={c3d}")

    # BFS over A-actions: find states where ANY click produces more than 1 pixel change
    print("\n[8] BFS: A-SEQUENCES + FOCUSED CLICK PROBE")
    print("-" * 40)

    best_diff = 0
    best_seq = None
    best_click = None
    selection_found = False

    visited = set()
    init_hash = pixel_hash(game)
    game.env._game = copy.deepcopy(init_snap)
    visited.add(init_hash)

    queue = deque()
    queue.append(([], copy.deepcopy(init_snap)))

    states_explored = 0
    max_depth = 8

    while queue and states_explored < 8000 and not selection_found:
        actions, snap = queue.popleft()

        if len(actions) > max_depth:
            continue

        game.env._game = copy.deepcopy(snap)
        vp_now = get_viewport(game)
        foz_now = get_foz_info(game)
        veh_now = get_vehicles(game)

        # Click targets: all foz pieces + all vehicles (at sprite coord + offsets)
        click_targets = []
        for fx, fy, fn in foz_now:
            sx, sy = world_to_screen(fx, fy, vp_now)
            click_targets.append((sx + 3, sy + 3, fn))
        for vx, vy, vn in veh_now:
            sx, sy = world_to_screen(vx, vy, vp_now)
            click_targets.append((sx + 3, sy + 3, vn))

        for cx, cy, name in click_targets:
            if not (0 <= cx < 64 and 0 <= cy < 64):
                continue

            game.env._game = copy.deepcopy(snap)
            diff, c3d = click_diff(game, cx, cy)

            if diff > best_diff:
                best_diff = diff
                best_seq = list(actions)
                best_click = (cx, cy, name)
                print(f"  NEW BEST: seq={actions} click=({cx},{cy}) diff={diff} c3d={c3d} [{name[:20]}]")

            if c3d > 0:
                print(f"  *** SELECTION! seq={actions} click=({cx},{cy}) c3_delta={c3d} [{name[:20]}]")
                selection_found = True
                break

            # Check if level changed
            game.env._game = copy.deepcopy(snap)
            game.env.step(GameAction.ACTION6, data={'x': cx, 'y': cy})
            new_level = game.env._game._current_level_index
            if new_level != level:
                print(f"  *** LEVEL CHANGE! seq={actions} click=({cx},{cy}) {level}->{new_level}")
                selection_found = True
                break

            # Check foz count change
            foz_after = get_foz_info(game)
            if len(foz_after) != len(foz_now):
                print(f"  *** FOZ COUNT CHANGED! seq={actions} click=({cx},{cy}) {len(foz_now)}->{len(foz_after)}")
                selection_found = True
                break

        states_explored += 1
        if states_explored % 1000 == 0:
            print(f"  ... {states_explored} states, depth {len(actions)}, {len(visited)} unique, best_diff={best_diff}")

        # Expand A-actions
        if len(actions) < max_depth and not selection_found:
            for a in [1, 2, 3, 4]:
                game.env._game = copy.deepcopy(snap)
                apply_action(game, a)
                h = pixel_hash(game)
                if h not in visited:
                    visited.add(h)
                    queue.append((actions + [a], copy.deepcopy(game.env._game)))

    print(f"\n  TOTAL: {states_explored} states, {len(visited)} unique")
    print(f"  Best: diff={best_diff} seq={best_seq} click={best_click}")

    # Expanded pixel scan: try every non-zero pixel at several A-states
    print("\n[9] FULL PIXEL SCAN AT INIT + KEY A-STATES")
    print("-" * 40)

    test_seqs = [
        [],
        [3, 3, 3, 3],
        [4, 4, 4, 4],
        [1, 1, 1, 1],
        [2, 2, 2, 2],
        [3, 1, 3, 1],
        [4, 2, 4, 2],
        [1, 3, 2, 4],
    ]

    for seq in test_seqs:
        game.env._game = copy.deepcopy(init_snap)
        for a in seq:
            apply_action(game, a)

        pix = get_pixels(game)
        nonzero_yx = list(zip(*np.where(pix != 0)))

        max_diff = 0
        max_pos = None
        tested = 0
        snap_after_seq = copy.deepcopy(game.env._game)

        for y, x in nonzero_yx:
            game.env._game = copy.deepcopy(snap_after_seq)
            diff, c3d = click_diff(game, int(x), int(y))
            if diff > max_diff:
                max_diff = diff
                max_pos = (int(x), int(y))
            if c3d > 0:
                print(f"  *** SELECTION at seq={seq} pixel=({x},{y}) color={pix[y,x]} c3d={c3d} diff={diff}")
            tested += 1

        print(f"  seq={seq}: {tested} pixels tested, max_diff={max_diff} at {max_pos}")

    # Try ACTION5 and ACTION7
    print("\n[10] UNUSUAL ACTIONS (A5, A7)")
    print("-" * 40)
    for a in [5, 7]:
        game.env._game = copy.deepcopy(init_snap)
        pre = get_pixels(game)
        try:
            game.env.step(getattr(GameAction, f'ACTION{a}'))
            post = get_pixels(game)
            diff = int(np.sum(pre != post))
            print(f"  ACTION{a}: {diff} pixels changed")
            if diff > 1:
                # Check foz
                foz_after = get_foz_info(game)
                print(f"    foz after: {len(foz_after)} (was {len(foz)})")
        except Exception as e:
            print(f"  ACTION{a}: error — {e}")

    # Try double-click patterns
    print("\n[11] DOUBLE-CLICK PATTERNS")
    print("-" * 40)
    for fx, fy, fn in foz:
        sx, sy = world_to_screen(fx, fy, vp)
        sx, sy = sx + 3, sy + 3
        if not (0 <= sx < 64 and 0 <= sy < 64):
            continue
        # Click piece, then click same piece again
        game.env._game = copy.deepcopy(init_snap)
        pre = get_pixels(game)
        game.env.step(GameAction.ACTION6, data={'x': sx, 'y': sy})
        mid = get_pixels(game)
        game.env.step(GameAction.ACTION6, data={'x': sx, 'y': sy})
        post = get_pixels(game)
        d1 = int(np.sum(pre != mid))
        d2 = int(np.sum(mid != post))
        if d2 > 1:
            print(f"  Double-click ({sx},{sy}): d1={d1}, d2={d2}")

        # Click piece, A-action, click piece
        for a in [1, 2, 3, 4]:
            game.env._game = copy.deepcopy(init_snap)
            game.env.step(GameAction.ACTION6, data={'x': sx, 'y': sy})
            apply_action(game, a)
            post2 = get_pixels(game)
            game.env.step(GameAction.ACTION6, data={'x': sx, 'y': sy})
            post3 = get_pixels(game)
            d = int(np.sum(post2 != post3))
            if d > 1:
                print(f"  Click-A{a}-Click ({sx},{sy}): diff={d}")

    # Try clicking DGX cells that are adjacent to pieces
    print("\n[12] ADJACENT DGX CLICK (piece neighbor cells)")
    print("-" * 40)
    for fx, fy, fn in foz:
        for ddx, ddy in [(-6, 0), (6, 0), (0, -6), (0, 6)]:
            neighbor = (fx + ddx, fy + ddy)
            # Check if any DGX is at this neighbor
            for dx, dy, dn in dgx:
                if dx == neighbor[0] and dy == neighbor[1]:
                    game.env._game = copy.deepcopy(init_snap)
                    sx, sy = world_to_screen(dx, dy, vp)
                    sx, sy = sx + 3, sy + 3
                    if 0 <= sx < 64 and 0 <= sy < 64:
                        diff, c3d = click_diff(game, sx, sy)
                        print(f"  DGX({dx},{dy}) adj to foz({fx},{fy}): diff={diff} c3d={c3d}")

    print("\n" + "=" * 60)
    print("PROBE COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    main()
