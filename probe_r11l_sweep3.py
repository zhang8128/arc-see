"""R11L: sweep third click with fixed clicks 1, 2 = (36, 13), (26, 61).

Check which third clicks trigger the win. If 'any' third click works, win is
triggered on click 2 but only reported at step 3 (some kind of commit).
If only specific third clicks work, the sequence is more constrained.
"""
import arc_agi
from arcengine import GameAction


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    # Verify the 3-click solution with click 1 = center of winning region
    env.reset()
    env.step(GameAction.ACTION6, data={"x": 36, "y": 13})
    env.step(GameAction.ACTION6, data={"x": 26, "y": 61})
    obs = env.step(GameAction.ACTION6, data={"x": 42, "y": 30})
    print(f"(36,13)/(26,61)/(42,30): levels_completed={obs.levels_completed}")

    # Now sweep click 3
    wins = []
    for cx in range(64):
        for cy in range(64):
            env.reset()
            env.step(GameAction.ACTION6, data={"x": 36, "y": 13})
            env.step(GameAction.ACTION6, data={"x": 26, "y": 61})
            obs3 = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            if obs3.levels_completed > 0:
                wins.append((cx, cy))
    print(f"\nthird-click positions that trigger win (after (36,13),(26,61)): {len(wins)}")
    if wins:
        xs = [p[0] for p in wins]
        ys = [p[1] for p in wins]
        print(f"  x range: {min(xs)}..{max(xs)}  y range: {min(ys)}..{max(ys)}")
        win_set = set(wins)
        # Print a 2-pixel-stride map
        print("  winning third-click map (W = win):")
        for cy in range(0, 64, 2):
            row = "".join("W" if (cx, cy) in win_set else "." for cx in range(0, 64, 2))
            print(f"    y={cy:2d}: {row}")


if __name__ == "__main__":
    main()
