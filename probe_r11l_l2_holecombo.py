"""R11L L2: try sequences involving the single reachable 'hole' cell (36, 20)
and the isolated cluster (33-36, 29-31). Plus arm 2 c-diamond (40, 51).
"""
import copy
import arc_agi
from arcengine import GameAction


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    L1 = [(36, 13), (26, 61), (42, 30)]
    env.reset()
    for cx, cy in L1:
        env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
    snap = copy.deepcopy(env._game)

    HOLE_CLICK = (51, 30)        # arm 1 foot → (36, 20)
    ISO_CLICK = (45, 60)         # arm 1 foot → (34, 30)
    ISO2_CLICK = (42, 57)        # arm 1 foot → (33, 29)
    CDIAM_SEQ = [(45, 35), (26, 54)]  # arm 2 foot → (40, 51)

    seqs = [
        # hole only
        [HOLE_CLICK],
        [HOLE_CLICK, ISO_CLICK],
        [HOLE_CLICK, ISO_CLICK, (26, 54)],
        [HOLE_CLICK, (45, 35), (26, 54)],
        # iso then hole
        [ISO_CLICK, HOLE_CLICK],
        [ISO_CLICK, HOLE_CLICK, (45, 35), (26, 54)],
        # hole + cdiamond
        [HOLE_CLICK, (45, 35), (26, 54)],
        # hole + two iso + cdiamond
        [HOLE_CLICK, ISO_CLICK, ISO2_CLICK, (45, 35), (26, 54)],
        [ISO_CLICK, HOLE_CLICK, ISO2_CLICK, (45, 35), (26, 54)],
        # "A → hip → B" with hole and iso as A/B
        [HOLE_CLICK, (49, 9), ISO_CLICK],
        [HOLE_CLICK, (8, 21), ISO_CLICK],
        [ISO_CLICK, (49, 9), HOLE_CLICK],
        # Same with arm 2 hip as middle
        [HOLE_CLICK, (45, 35), ISO_CLICK],
        [HOLE_CLICK, (54, 48), ISO_CLICK],
        # Full combo: A → hip_arm1 → B for arm1, then arm2 placement
        [HOLE_CLICK, (49, 9), ISO_CLICK, (45, 35), (26, 54)],
        [HOLE_CLICK, (8, 21), ISO_CLICK, (45, 35), (26, 54)],
        [ISO_CLICK, (49, 9), HOLE_CLICK, (45, 35), (26, 54)],
        [ISO_CLICK, (8, 21), HOLE_CLICK, (45, 35), (26, 54)],
    ]

    for seq in seqs:
        env._game = copy.deepcopy(snap)
        lc = 0
        for cx, cy in seq:
            obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            lc = max(lc, obs.levels_completed)
        marker = " *** WIN ***" if lc >= 2 else ""
        print(f"{seq}: lc={lc}{marker}")


if __name__ == "__main__":
    main()
