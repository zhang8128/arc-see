"""R11L: diff-based analysis. Find the 1-cell HUD and what moves on click."""
import numpy as np
import arc_agi
from arcengine import GameAction


def frame(obs):
    return np.array(obs.frame[-1], dtype=np.int64)


def diff(a, b):
    """Return list of (y, x, old, new) for cells that changed."""
    ys, xs = np.where(a != b)
    return [(int(y), int(x), int(a[y, x]), int(b[y, x])) for y, x in zip(ys, xs)]


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    obs = env.reset()
    g0 = frame(obs)

    # First: find the "1-cell changed" cell for each no-op action. Is it
    # always the same cell? If yes, it's a shared HUD/counter.
    print("-- 1-cell actions --")
    for aid in [1, 2, 3, 4, 5, 7]:
        env.reset()
        obs = env.step(getattr(GameAction, f"ACTION{aid}"))
        d = diff(g0, frame(obs))
        print(f"ACTION{aid}: {d}")

    # Click on the apparent player (6, 36). Same 1 cell?
    env.reset()
    obs = env.step(GameAction.ACTION6, data={"x": 6, "y": 36})
    print(f"click(6,36): {diff(g0, frame(obs))}")

    # Now: click somewhere far away and see what moves.
    # Record the bounding box of the changed region.
    env.reset()
    obs = env.step(GameAction.ACTION6, data={"x": 30, "y": 30})
    g1 = frame(obs)
    d = diff(g0, g1)
    ys = [y for y, x, _, _ in d]
    xs = [x for y, x, _, _ in d]
    print(f"\nclick(30,30): {len(d)} cells changed")
    print(f"  y range: {min(ys)}..{max(ys)}  x range: {min(xs)}..{max(xs)}")

    # What got ERASED (old value non-background) — that's the old sprite.
    # What got DRAWN (new value non-background) — that's the new sprite.
    # "Background" at the player's location is probably 5.
    erased_non5 = [(y, x, o, n) for (y, x, o, n) in d if o != 5]
    drawn_non5 = [(y, x, o, n) for (y, x, o, n) in d if n != 5]
    print(f"  erased non-bg cells ({len(erased_non5)}):")
    for y, x, o, n in erased_non5[:30]:
        print(f"    ({x:2d},{y:2d}) {o}->{n}")
    print(f"  drawn non-bg cells ({len(drawn_non5)}):")
    for y, x, o, n in drawn_non5[:30]:
        print(f"    ({x:2d},{y:2d}) {o}->{n}")

    # Can we click twice? State persistent across clicks?
    print("\n-- 2 clicks in a row --")
    env.reset()
    env.step(GameAction.ACTION6, data={"x": 30, "y": 30})
    obs = env.step(GameAction.ACTION6, data={"x": 40, "y": 40})
    g2 = frame(obs)
    d2 = diff(g0, g2)
    print(f"after 2 clicks: {len(d2)} cells differ from start")
    ys = [y for y, x, _, _ in d2]
    xs = [x for y, x, _, _ in d2]
    if ys:
        print(f"  y range: {min(ys)}..{max(ys)}  x range: {min(xs)}..{max(xs)}")


if __name__ == "__main__":
    main()
