"""Complete solution for SU15 (su15-4c352900) — all 9 levels.

Vacuum puzzle: click near fruits to pull them toward goal. Fruits merge
when overlapping. Win = required kinds inside goal area.

Actions: CLICK only (ACTION6 with x,y coordinates).
Total: 104 clicks. Baselines: 566.
"""
import arc_agi
from arcengine import GameAction

CLICK = GameAction.ACTION6
BASELINES = [18, 28, 50, 151, 18, 31, 50, 179, 41]

SOLUTIONS = {
    1: [(10, 53), (16, 47), (22, 41), (28, 35), (34, 29), (40, 23), (45, 16)],
    2: [(47, 53), (41, 40), (43, 46), (19, 41), (19, 50), (25, 44), (34, 45), (34, 38), (35, 30)],
    3: [(55, 20), (34, 19), (9, 26), (16, 24), (28, 25), (22, 31), (53, 23), (15, 38), (12, 46), (8, 46), (53, 16), (56, 19), (62, 19), (11, 51), (13, 54), (57, 24), (57, 29), (57, 34), (60, 37), (9, 49), (5, 46), (63, 43), (57, 48), (8, 46), (54, 51), (12, 52), (49, 46), (43, 46), (36, 46), (30, 46), (25, 41), (19, 41), (5, 53), (13, 46)],
    4: [(29, 32), (26, 45), (26, 38), (12, 40), (11, 26), (10, 33), (18, 35), (11, 42), (4, 49), (5, 56)],
    5: [(47, 23), (14, 23), (21, 23), (28, 23), (40, 19), (32, 15)],
    6: [(29, 28), (22, 21), (15, 14), (8, 10), (3, 20), (0, 13), (0, 10), (0, 10)],
    7: [(10, 33), (28, 32), (19, 32), (21, 25), (23, 17), (47, 32), (45, 25)],
    8: [(8, 44), (30, 33), (8, 51), (23, 26), (16, 23), (9, 16), (23, 52), (4, 23), (11, 23)],
    9: [(17, 54), (11, 54), (0, 30), (0, 30), (0, 30), (23, 51), (18, 47), (13, 43), (1, 44), (15, 41), (14, 43), (12, 43), (12, 33), (11, 41)],
}


def verify():
    arcade = arc_agi.Arcade()
    env = arcade.make("su15-4c352900", render_mode=None)
    env.reset()
    total = 0

    for level in range(1, 10):
        clicks = SOLUTIONS[level]
        for x, y in clicks:
            result = env.step(CLICK, data={"x": x, "y": y})
        total += len(clicks)
        print(f"  L{level}: {len(clicks):3d} clicks (baseline {BASELINES[level-1]}), levels_completed={result.levels_completed}")

    print(f"\nTotal: {total} clicks (baselines: {sum(BASELINES)})")
    print(f"Final state: {result.state}")
    assert str(result.state) == "GameState.WIN", f"Expected WIN, got {result.state}"
    print("ALL VERIFIED!")


if __name__ == "__main__":
    verify()
