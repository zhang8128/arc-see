"""R11L: sweep first click, fix clicks 2 and 3 at the known winning values.

Find which first clicks enable the (26, 61), (42, 30) combo to win.
This tells us what initial state is required before the hip sequence.
"""
import arc_agi
from arcengine import GameAction


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    wins = []
    for cx1 in range(64):
        for cy1 in range(64):
            env.reset()
            env.step(GameAction.ACTION6, data={"x": cx1, "y": cy1})
            env.step(GameAction.ACTION6, data={"x": 26, "y": 61})
            obs = env.step(GameAction.ACTION6, data={"x": 42, "y": 30})
            if obs.levels_completed > 0:
                wins.append((cx1, cy1))

    print(f"first-click positions that enable the (26,61),(42,30) win: {len(wins)}")
    if wins:
        xs = [p[0] for p in wins]
        ys = [p[1] for p in wins]
        print(f"  x range: {min(xs)}..{max(xs)}")
        print(f"  y range: {min(ys)}..{max(ys)}")
        # Print a grid showing which cells trigger win
        print("  sample (first 20):", wins[:20])

        # Check if the "winning" first clicks are clustered
        win_set = set(wins)
        print("\n  first-click map (W = winning first click):")
        for cy in range(0, 64, 2):
            row = "".join("W" if (cx, cy) in win_set else "." for cx in range(0, 64, 2))
            print(f"    y={cy:2d}: {row}")


if __name__ == "__main__":
    main()
