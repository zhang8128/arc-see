"""R11L L2: test the hip-button hypothesis.

Click EACH of the 4 hip centers in isolation (from fresh L2 state).
Check whether each one inverts its diamond (0↔3 swap).
Then try sequences: click hip A, then click somewhere else, see if the arm
attaches to hip A.
"""
import numpy as np
import arc_agi
from arcengine import GameAction


def frame(obs):
    return np.array(obs.frame[-1], dtype=np.int64)


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    L1 = [(36, 13), (26, 61), (42, 30)]
    env.reset()
    for cx, cy in L1:
        obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
    g0 = frame(obs)

    hips = [(49, 9), (8, 21), (45, 35), (54, 48)]

    # Test each hip click in isolation
    print("-- each hip as single click --")
    for hip in hips:
        env.reset()
        for px, py in L1:
            env.step(GameAction.ACTION6, data={"x": px, "y": py})
        obs2 = env.step(GameAction.ACTION6, data={"x": hip[0], "y": hip[1]})
        g = frame(obs2)
        diffs = np.argwhere((g != g0) & (np.arange(g.shape[1])[None, :] != 0))
        from collections import Counter
        trans = Counter()
        for y, x in diffs:
            trans[(int(g0[y, x]), int(g[y, x]))] += 1
        print(f"  click({hip[0]},{hip[1]}): {len(diffs)} cells changed")
        print(f"    transitions: {dict(trans)}")

    # Test: click each hip, then click any other position, see if the click
    # now does something different (arm uses new hip)
    print("\n-- click hip then click elsewhere --")
    for hip in hips:
        env.reset()
        for px, py in L1:
            env.step(GameAction.ACTION6, data={"x": px, "y": py})
        env.step(GameAction.ACTION6, data={"x": hip[0], "y": hip[1]})
        obs2 = env.step(GameAction.ACTION6, data={"x": 30, "y": 30})
        g = frame(obs2)
        sixes = [(int(x), int(y)) for y, x in np.argwhere(g == 6)]
        print(f"  click({hip[0]},{hip[1]}) then (30,30): sixes={sixes}, lc={obs2.levels_completed}")

    # Also: try clicking the same hip twice (toggle?)
    print("\n-- click each hip TWICE --")
    for hip in hips:
        env.reset()
        for px, py in L1:
            env.step(GameAction.ACTION6, data={"x": px, "y": py})
        env.step(GameAction.ACTION6, data={"x": hip[0], "y": hip[1]})
        obs2 = env.step(GameAction.ACTION6, data={"x": hip[0], "y": hip[1]})
        g = frame(obs2)
        diffs = int(np.sum((g != g0) & (np.arange(g.shape[1])[None, :] != 0)))
        print(f"  click({hip[0]},{hip[1]}) x2: diff={diffs}, lc={obs2.levels_completed}")

    # Try clicking all 4 hips in sequence (maybe that wins)
    print("\n-- all 4 hips in order --")
    import itertools
    for perm in itertools.permutations(hips):
        env.reset()
        for px, py in L1:
            env.step(GameAction.ACTION6, data={"x": px, "y": py})
        last_lc = 0
        for h in perm:
            obs2 = env.step(GameAction.ACTION6, data={"x": h[0], "y": h[1]})
            last_lc = max(last_lc, obs2.levels_completed)
        if last_lc >= 2:
            print(f"  WIN: {perm}")
    print("  done")


if __name__ == "__main__":
    main()
