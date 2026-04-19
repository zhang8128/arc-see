"""R11L L2: find which clicks reach the isolated cluster and try them
combined with arm2 placement.
"""
import numpy as np
import arc_agi
from arcengine import GameAction


def arm1_foot(g):
    for y, x in np.argwhere(g == 6):
        if (int(x), int(y)) != (49, 41):
            return (int(x), int(y))
    return None


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

    # Find clicks that put arm1 foot in isolated cluster (rows 29-31, cols 33-36)
    isolated = {(x, y) for x in range(33, 37) for y in range(29, 32)}
    iso_clicks = []
    for cy in range(64):
        for cx in range(64):
            obs = play([(cx, cy)])
            g = np.array(obs.frame[-1], dtype=np.int64)
            f = arm1_foot(g)
            if f in isolated:
                iso_clicks.append((cx, cy))
    print(f"clicks reaching isolated cluster: {len(iso_clicks)}")
    print(f"sample: {iso_clicks[:10]}")

    # Now test: each iso click as A or B in (A, hip, B) pattern for both arms
    print("\n-- iso click → arm2 hip → arm2 goal click --")
    for iso in iso_clicks[:20]:
        for hip in [(45, 35), (54, 48)]:
            for final in [(26, 54), (40, 51), (40, 40), (30, 40)]:
                obs = play([iso, hip, final])
                if obs.levels_completed >= 2:
                    print(f"  WIN: {iso} → {hip} → {final}")
                    return

    # Also try: arm2 goal → arm1 iso
    print("\n-- arm2 goal seq → iso click --")
    for iso in iso_clicks[:20]:
        for hip in [(45, 35), (54, 48)]:
            for final in [(26, 54), (40, 51), (40, 40)]:
                obs = play([(10, 10), hip, final, iso])
                if obs.levels_completed >= 2:
                    print(f"  WIN: (10,10) → {hip} → {final} → {iso}")
                    return

    print("\nno wins")


if __name__ == "__main__":
    main()
