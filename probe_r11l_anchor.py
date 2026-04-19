"""R11L: test the 'diamond-is-hip, click pivots the extremity' hypothesis.

Also test win hypotheses:
  H1: win when foot lands on (27, 59) — requires finding a reachable click
  H2: win when the two extremities (7,36) and (17,47)/(27,60) meet
  H3: win when foot lands on any 3-cell
  H4: win triggered after a sequence (score increments on each correct click)
"""
import numpy as np
import arc_agi
from arcengine import GameAction


def frame(obs):
    return np.array(obs.frame[-1], dtype=np.int64)


def foot_pos(grid):
    sixes = np.argwhere(grid == 6)
    if len(sixes) != 1:
        return None
    y, x = sixes[0]
    return (int(x), int(y))


def head_pos(grid):
    """The f center surrounded by 0s (the smaller extremity)."""
    ys, xs = np.where(grid == 15)
    for y, x in zip(ys, xs):
        if y < 1 or y > 62 or x < 1 or x > 62:
            continue
        nb = [int(grid[y - 1, x]), int(grid[y + 1, x]),
              int(grid[y, x - 1]), int(grid[y, x + 1])]
        if nb.count(0) >= 3:
            return (int(x), int(y))
    return None


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    obs = env.reset()
    g0 = frame(obs)
    print(f"initial foot: {foot_pos(g0)}  head: {head_pos(g0)}")

    # Claim: the 3-diamond is the hip (anchor). The 3-cells are at:
    threes = [tuple(p.tolist()) for p in np.argwhere(g0 == 3)]  # (y, x)
    print(f"3-cells: {threes}")

    # Under the formula: anchor = (26, 58). Reachable foot positions from
    # click (cx, cy) are ((26+cx)//2, (58+cy)//2) (approximately).
    # To land foot at (27, 59): need cx in {28}, cy in {60}. Try it.
    print("\n-- targeted: foot → (27, 59) --")
    for cx, cy in [(28, 60), (27, 60), (29, 60), (28, 59), (28, 61)]:
        env.reset()
        obs2 = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        g = frame(obs2)
        fp = foot_pos(g)
        hp = head_pos(g)
        print(f"  click({cx},{cy}): foot={fp}  head={hp}  state={obs2.state.name}")

    # H2 test: try to click so that foot lands ON the other extremity.
    # Head is at (7, 36). To put foot at (7, 36):
    #   cx = 2*7 - 26 = -12  (out of bounds — impossible)
    # So H2 ruled out by the formula alone.

    # H4 test: watch for score/indicator change. Monitor if row 0 col 0 (turn
    # counter) increments by more than 5 on a "successful" click, or if some
    # other cell changes beyond the player+counter.
    print("\n-- cell (0,0) and other deltas over 3 clicks --")
    env.reset()
    g_prev = frame(env.reset())
    for i, (cx, cy) in enumerate([(28, 60), (20, 40), (10, 30)]):
        obs2 = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        g = frame(obs2)
        print(f"  click{i} ({cx},{cy}): (0,0)={int(g[0,0])}  state={obs2.state.name}  foot={foot_pos(g)}")
        g_prev = g

    # Try multi-click to the goal neighborhood: 7 clicks at (28, 60)
    print("\n-- 7 repeated clicks at (28, 60) --")
    env.reset()
    for i in range(7):
        obs2 = env.step(GameAction.ACTION6, data={"x": 28, "y": 60})
        g = frame(obs2)
        print(f"  click{i}: foot={foot_pos(g)}  state={obs2.state.name}  (0,0)={int(g[0,0])}")
        if obs2.state.name == "WIN":
            print("  *** WIN ***")
            break


if __name__ == "__main__":
    main()
