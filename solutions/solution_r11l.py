"""Complete solution for R11L (r11l-aa269680) — all 6 levels.

Walker puzzle: click to move feet. L1-L4 are foot-placement to match
hand targets. L5-L6 are paint absorption puzzles with forbidden zones.

Actions: CLICK only (ACTION6 with x,y coordinates).
Total: ~69 clicks. Baselines: 167.

IMPORTANT: env.reset() leaks state — call twice before replaying.
L2-L4 solutions are from meet-in-the-middle solver (specific to foot
layout). L6 includes foot-selection clicks interleaved with move clicks.
"""
import arc_agi
from arcengine import GameAction

CLICK = GameAction.ACTION6
BASELINES = [7, 25, 31, 35, 37, 45]

SOLUTIONS = {
    1: [(36, 13), (26, 61), (42, 30)],
    2: [(45, 35), (50, 26), (54, 48), (62, 10), (17, 6), (42, 58), (8, 21), (54, 52), (49, 9), (24, 44)],
    3: [(37, 34), (52, 62), (52, 40), (16, 46), (14, 16), (34, 48), (23, 21), (62, 54), (34, 9), (62, 42), (39, 16), (62, 48)],
    4: [(46, 52), (0, 50), (46, 36), (34, 58), (17, 36), (30, 0), (27, 52), (44, 0), (10, 47), (62, 40), (23, 20), (10, 42), (39, 6), (62, 56)],
    5: [(43, 34), (9, 39), (50, 7), (11, 18), (41, 47), (48, 36), (34, 55), (58, 44), (10, 54), (52, 55), (10, 58), (50, 6), (10, 54), (48, 2)],
    6: [(11, 11), (28, 58), (22, 19), (24, 58), (10, 26), (50, 6), (28, 58), (52, 34), (4, 19), (56, 6), (49, 43), (18, 34), (46, 10), (2, 56), (50, 57), (28, 54)],
}


def verify():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)
    env.reset()
    env.reset()  # double-reset: env.reset() leaks state
    total = 0

    for level in range(1, 7):
        clicks = SOLUTIONS[level]
        for x, y in clicks:
            result = env.step(CLICK, data={"x": x, "y": y})
        total += len(clicks)
        print(f"  L{level}: {len(clicks):3d} clicks (baseline {BASELINES[level-1]}), levels_completed={result.levels_completed}")

    print(f"\nTotal: {total} clicks (baselines: {sum(BASELINES)})")
    print(f"Final state: {result.state}")
    assert result.levels_completed == 6, f"Expected 6 levels, got {result.levels_completed}"
    print("ALL VERIFIED!")


if __name__ == "__main__":
    verify()
