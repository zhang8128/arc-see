"""R11L L2: test hypothesis - maybe there are 4 arms, one per 3-diamond.

Click at each hip center (with +1 offset to place head exactly on center).
Observe which arm moves. Also test multi-click sequences that visit all 4 hips
with the head.
"""
import numpy as np
import arc_agi
from arcengine import GameAction


def sixes(g):
    return sorted([(int(x), int(y)) for y, x in np.argwhere(g == 6)])


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)
    L1 = [(36, 13), (26, 61), (42, 30)]

    def play(seq):
        env.reset()
        obs = None
        for px, py in L1:
            obs = env.step(GameAction.ACTION6, data={"x": px, "y": py})
        for cx, cy in seq:
            obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        return obs

    # Hip centers (clusters from color-3 detection)
    hips = [(49, 9), (8, 21), (45, 35), (54, 48)]

    # Place head exactly on each hip center via click = hip - (1, 1)
    # (based on L1 where head = click + (1, 1))
    print("-- click to place head on each hip center --")
    for hip in hips:
        click = (hip[0] - 1, hip[1] - 1)
        obs = play([click])
        g = np.array(obs.frame[-1], dtype=np.int64)
        print(f"  click{click} → sixes={sixes(g)}  lc={obs.levels_completed}")

    # All 24 perms of 4 head-placing clicks
    print("\n-- all 24 perms of 4 head-on-hip clicks --")
    import itertools
    clicks = [(h[0] - 1, h[1] - 1) for h in hips]
    wins = []
    for perm in itertools.permutations(clicks):
        obs = play(list(perm))
        if obs.levels_completed >= 2:
            wins.append(perm)
            print(f"  WIN: {perm}")
    print(f"  total wins: {len(wins)}")

    # Also: 3-click perms (skip one hip)
    print("\n-- 3 head-on-hip clicks (skip one) --")
    for skip in range(4):
        sub = [c for i, c in enumerate(clicks) if i != skip]
        for perm in itertools.permutations(sub):
            obs = play(list(perm))
            if obs.levels_completed >= 2:
                print(f"  WIN (skipped hip {hips[skip]}): {perm}")
                return

    # Also: 2-click perms
    print("\n-- 2 head-on-hip clicks --")
    for c1 in clicks:
        for c2 in clicks:
            if c1 == c2:
                continue
            obs = play([c1, c2])
            if obs.levels_completed >= 2:
                print(f"  WIN: {c1} → {c2}")
                return

    print("\n  no wins")


if __name__ == "__main__":
    main()
