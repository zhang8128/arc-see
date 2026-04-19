"""Complete solution for FT09 (ft09-0d8bbf25) — all 6 levels.

Color-matching constraint puzzle. Click cells to cycle colors.
Total: 75 clicks. Baselines: 163.
"""
import arc_agi
from arcengine import GameAction

CLICK = GameAction.ACTION6
BASELINES = [8, 18, 34, 24, 42, 37]

SOLUTIONS = {
    1: [(40, 40), (40, 48), (56, 48), (40, 56)],
    2: [(24, 18), (24, 26), (40, 26), (24, 34), (40, 34), (32, 50), (24, 50)],
    3: [(24, 8), (24, 16), (32, 24), (40, 8), (32, 8), (16, 32), (16, 24), (32, 40), (48, 40), (48, 32), (24, 48), (32, 56), (24, 56), (40, 56)],
    4: [(24, 18), (24, 18), (32, 26), (32, 34), (48, 26), (32, 18), (24, 34), (24, 34), (40, 34), (48, 18), (24, 50), (24, 50), (32, 50), (32, 50), (40, 50), (40, 50)],
    5: [(26, 16), (42, 48), (26, 32), (18, 16), (18, 24), (18, 32), (18, 40), (18, 56), (26, 8), (34, 8), (34, 16), (34, 24), (34, 32), (34, 40), (34, 48), (34, 56), (42, 40), (42, 56), (50, 24), (50, 40), (50, 48)],
    6: [(24, 18), (40, 18), (16, 26), (24, 26), (40, 34), (16, 34), (48, 34), (32, 34), (48, 42), (24, 42), (56, 42), (8, 18), (8, 10)],
}


def verify():
    arcade = arc_agi.Arcade()
    env = arcade.make("ft09-0d8bbf25", render_mode=None)
    result = env.reset()
    total = 0

    for level in range(1, 7):
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
