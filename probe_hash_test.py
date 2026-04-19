"""Diagnose: why does the game hash look identical across levels?"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
sys.path.insert(0, '/Users/kairos/Projects/arc-see/solutions')

import numpy as np, hashlib
from lf52_tool import LF52
from arcengine import GameAction
import solution_lf52_l5 as L5


def state_hash(g):
    pix = g.env._game.get_pixels(0, 0, 64, 64)
    arr = np.array(pix, dtype=np.int16)
    return hashlib.md5(arr.tobytes()).hexdigest()[:8], arr


def frame_hash_from_obs(g):
    if g.obs is None:
        return None
    return hashlib.md5(np.array(g.obs.frame[-1], dtype=np.int16).tobytes()).hexdigest()[:8]


def main():
    g = LF52(up_to_level=1, verbose=False)
    print(f"After reset: level_idx={g.env._game._current_level_index}")
    h1, arr1 = state_hash(g)
    print(f"get_pixels hash: {h1}")
    print(f"first row: {arr1[0, :10]}")
    print(f"piece cells sum: {int(arr1.sum())}")
    print(f"obs frame hash: {frame_hash_from_obs(g)}")

    # Try a click and see if anything changes via obs
    obs1 = g.env.step(GameAction.ACTION6, data={'x': 18, 'y': 19})
    print(f"\nAfter click(18,19) L1: level_idx={g.env._game._current_level_index}")
    h2, arr2 = state_hash(g)
    print(f"get_pixels hash: {h2}")
    print(f"obs frame hash: {hashlib.md5(np.array(obs1.frame[-1], dtype=np.int16).tobytes()).hexdigest()[:8]}")
    print(f"arr1 == arr2? {np.array_equal(arr1, arr2)}")
    # Compare obs vs get_pixels
    obs_arr = np.array(obs1.frame[-1], dtype=np.int16)
    print(f"obs == get_pixels? {np.array_equal(obs_arr, arr2)}")
    if not np.array_equal(obs_arr, arr2):
        # Where do they differ?
        diff = (obs_arr != arr2).sum()
        print(f"{diff} pixels differ; obs sum={obs_arr.sum()}, get_pix sum={arr2.sum()}")


if __name__ == '__main__':
    main()
