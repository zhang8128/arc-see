"""LF52 L7 probe v3 — uses obs.frame (camera pipeline) not get_pixels.

The critical bug in v1/v2: get_pixels() bypasses the camera rendering pipeline
(reveal masks, viewport transforms). obs.frame[-1] is the TRUE rendered frame.
"""
import sys
import copy
import hashlib
import numpy as np
from collections import deque

sys.path.insert(0, '/Users/kairos/Projects/arc-see')
from lf52_tool import LF52, render_png, ascii_grid
from arcengine import GameAction
from pathlib import Path

OUT_DIR = Path('/tmp/lf52_l7_probe')


def frame_hash(frame):
    return hashlib.md5(np.array(frame, dtype=np.int16).tobytes()).hexdigest()


def frame_diff(f1, f2):
    a1 = np.array(f1, dtype=np.int16)
    a2 = np.array(f2, dtype=np.int16)
    return int(np.sum(a1 != a2))


def color_count(frame, color):
    return int((np.array(frame, dtype=np.int16) == color).sum())


def color_dist(frame):
    arr = np.array(frame, dtype=np.int16)
    unique, counts = np.unique(arr, return_counts=True)
    return dict(zip(unique.tolist(), counts.tolist()))


def step_action(env, a):
    """Step with A-action, return obs."""
    return env.step(getattr(GameAction, f'ACTION{a}'))


def step_click(env, x, y):
    """Step with click, return obs."""
    return env.step(GameAction.ACTION6, data={'x': x, 'y': y})


def main():
    print("=" * 60)
    print("LF52 L7 PROBE v3 (using obs.frame)")
    print("=" * 60)

    OUT_DIR.mkdir(exist_ok=True)

    print("\n[1] Building legit L7 state...")
    game = LF52(up_to_level=7, verbose=False)
    level = game.env._game._current_level_index
    print(f"  Level index: {level}, levels_completed: {game.obs.levels_completed}")

    # Get the REAL L7 init frame
    init_frame = np.array(game.obs.frame[-1], dtype=np.int16)
    print(f"  Init frame colors: {color_dist(init_frame)}")
    print(f"  Color 14 (pieces): {color_count(init_frame, 14)} pixels")
    print(f"  Color 3 (selection): {color_count(init_frame, 3)} pixels")

    # Render and save init frame
    render_png(init_frame, label='L7 init (legit)').save(OUT_DIR / 'l7_init.png')
    print(f"  Saved to {OUT_DIR / 'l7_init.png'}")

    # ASCII grid
    print("\n  L7 INIT ASCII GRID:")
    print(ascii_grid(init_frame))

    # Save init snapshot
    init_snap = copy.deepcopy(game.env._game)
    init_hash = frame_hash(init_frame)

    # Try clicking each pixel that has a non-background color
    print("\n[2] SYSTEMATIC CLICK SCAN")
    print("-" * 40)

    # Find all interesting pixel positions (non-black, non-color-10)
    interesting_colors = set()
    for y in range(64):
        for x in range(64):
            c = int(init_frame[y, x])
            if c not in (0, 10):  # skip black and dark-blue background
                interesting_colors.add(c)

    print(f"  Interesting colors: {interesting_colors}")

    # Test clicks at EVERY non-background pixel
    best_diff = 0
    best_pos = None
    selection_found = False

    for y in range(64):
        for x in range(64):
            c = int(init_frame[y, x])
            if c in (0, 10):  # skip background
                continue

            game.env._game = copy.deepcopy(init_snap)
            obs = step_click(game.env, x, y)
            post_frame = np.array(obs.frame[-1], dtype=np.int16)
            diff = frame_diff(init_frame, post_frame)

            c3_delta = color_count(post_frame, 3) - color_count(init_frame, 3)

            if diff > best_diff:
                best_diff = diff
                best_pos = (x, y, c)
                print(f"  NEW BEST click ({x},{y}) color={c}: diff={diff}, c3_delta={c3_delta}")

            if c3_delta > 0:
                print(f"  *** SELECTION at ({x},{y}) color={c}: diff={diff} c3={c3_delta}")
                render_png(post_frame, label=f'sel ({x},{y})').save(OUT_DIR / f'l7_sel_{x}_{y}.png')
                selection_found = True

            if diff > 100:
                print(f"  *** BIG CHANGE at ({x},{y}) color={c}: diff={diff}")
                render_png(post_frame, label=f'big ({x},{y})').save(OUT_DIR / f'l7_big_{x}_{y}.png')

    print(f"\n  Init scan: best_diff={best_diff} at {best_pos}")

    # Try A-actions and see their effects on the frame
    print("\n[3] A-ACTION EFFECTS")
    print("-" * 40)

    for a in [1, 2, 3, 4, 5, 7]:
        game.env._game = copy.deepcopy(init_snap)
        obs = step_action(game.env, a)
        post_frame = np.array(obs.frame[-1], dtype=np.int16)
        diff = frame_diff(init_frame, post_frame)
        print(f"  ACTION{a}: diff={diff} colors={color_dist(post_frame)}")
        if diff > 0:
            render_png(post_frame, label=f'A{a}').save(OUT_DIR / f'l7_A{a}.png')

    # BFS: A-action sequences → click every non-bg pixel
    print("\n[4] BFS: A-SEQUENCES + CLICK PROBE")
    print("-" * 40)

    visited = {init_hash}
    queue = deque()
    queue.append(([], copy.deepcopy(init_snap), init_frame.copy()))

    states_explored = 0
    max_depth = 8
    global_best_diff = best_diff

    while queue and states_explored < 3000 and not selection_found:
        actions, snap, base_frame = queue.popleft()

        if len(actions) > max_depth:
            continue

        # Try clicking all non-background pixels at this state
        base_arr = np.array(base_frame, dtype=np.int16)
        c3_base = int((base_arr == 3).sum())

        # Targeted click: only try pixels with piece/vehicle/dgx colors
        # Colors: 14=pieces, 15=f-containers, 11=trans-border, 12=trans-interior,
        #         8=light-blue(red-piece), 7=orange(goals), 1=blue, 5=gray(walls)
        target_colors = {14, 15, 11, 12, 8, 7, 1}

        for y in range(64):
            for x in range(64):
                c = int(base_arr[y, x])
                if c not in target_colors:
                    continue

                game.env._game = copy.deepcopy(snap)
                obs = step_click(game.env, x, y)
                post_frame = np.array(obs.frame[-1], dtype=np.int16)
                diff = frame_diff(base_frame, post_frame)
                c3_post = int((np.array(post_frame, dtype=np.int16) == 3).sum())
                c3_delta = c3_post - c3_base

                if diff > global_best_diff:
                    global_best_diff = diff
                    print(f"  BEST: seq={actions} click({x},{y}) c={c}: diff={diff} c3d={c3_delta}")
                    render_png(post_frame, label=f'{actions}+click({x},{y})').save(
                        OUT_DIR / f'l7_best_{"_".join(map(str,actions))}_{x}_{y}.png')

                if c3_delta > 0:
                    print(f"  *** SELECTION! seq={actions} click({x},{y}) c={c}: c3d={c3_delta}")
                    render_png(post_frame, label=f'sel').save(
                        OUT_DIR / f'l7_selection_{"_".join(map(str,actions))}_{x}_{y}.png')
                    selection_found = True
                    break

                if diff > 100:
                    print(f"  *** BIG: seq={actions} click({x},{y}) c={c}: diff={diff}")
                    render_png(post_frame, label=f'big').save(
                        OUT_DIR / f'l7_big_{"_".join(map(str,actions))}_{x}_{y}.png')

            if selection_found:
                break

        states_explored += 1
        if states_explored % 200 == 0:
            print(f"  ... {states_explored} states, {len(visited)} unique, best_diff={global_best_diff}")

        # Expand A-actions
        if len(actions) < max_depth and not selection_found:
            for a in [1, 2, 3, 4]:
                game.env._game = copy.deepcopy(snap)
                obs = step_action(game.env, a)
                new_frame = np.array(obs.frame[-1], dtype=np.int16)
                h = frame_hash(new_frame)
                if h not in visited:
                    visited.add(h)
                    queue.append((actions + [a], copy.deepcopy(game.env._game), new_frame))

    print(f"\n  TOTAL: {states_explored} states, {len(visited)} unique")
    print(f"  Global best diff: {global_best_diff}")

    # If no selection found, try a broader random search
    if not selection_found:
        print("\n[5] RANDOM A-SEQUENCE + FULL-PIXEL CLICK (1000 trials)")
        print("-" * 40)
        import random
        for trial in range(1000):
            game.env._game = copy.deepcopy(init_snap)
            seq_len = random.randint(1, 12)
            seq = [random.choice([1, 2, 3, 4]) for _ in range(seq_len)]
            for a in seq:
                step_action(game.env, a)

            state_snap = copy.deepcopy(game.env._game)
            base_frame = np.array(game.obs.frame[-1] if game.obs else init_frame, dtype=np.int16)

            # Need to get frame after A-actions via a noop click
            obs = step_click(game.env, 0, 0)
            base_frame = np.array(obs.frame[-1], dtype=np.int16)
            game.env._game = copy.deepcopy(state_snap)

            c3_base = int((base_frame == 3).sum())

            # Try 20 random non-bg pixels
            nonbg = list(zip(*np.where((base_frame != 0) & (base_frame != 10))))
            if not nonbg:
                continue
            sample = random.sample(nonbg, min(20, len(nonbg)))

            for y, x in sample:
                game.env._game = copy.deepcopy(state_snap)
                obs = step_click(game.env, int(x), int(y))
                post = np.array(obs.frame[-1], dtype=np.int16)
                c3_post = int((post == 3).sum())
                diff = frame_diff(base_frame, post)

                if c3_post > c3_base:
                    print(f"  *** SELECTION! trial={trial} seq={seq} click({x},{y}): c3={c3_post}")
                    selection_found = True
                    break
                if diff > 50:
                    print(f"  Big diff: trial={trial} seq={seq} click({x},{y}): diff={diff}")

            if selection_found:
                break
            if trial % 200 == 0:
                print(f"  ... {trial} trials")

    print("\n" + "=" * 60)
    if selection_found:
        print("SELECTION FOUND! Check /tmp/lf52_l7_probe/ for images.")
    else:
        print("NO SELECTION FOUND in any configuration tested.")
    print("=" * 60)


if __name__ == '__main__':
    main()
