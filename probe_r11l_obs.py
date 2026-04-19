"""R11L: inspect the full obs object. What fields does it have beyond
frame and state? Maybe there's a score, level index, or other signal.
"""
import arc_agi
from arcengine import GameAction


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    obs = env.reset()
    print(f"type(obs) = {type(obs).__name__}")
    print(f"obs dir (non-underscore):")
    for a in sorted(dir(obs)):
        if a.startswith("_"):
            continue
        try:
            v = getattr(obs, a)
            if callable(v):
                continue
            # Truncate long reprs
            repr_v = repr(v)
            if len(repr_v) > 200:
                repr_v = repr_v[:200] + "..."
            print(f"  {a}: {repr_v}")
        except Exception as e:
            print(f"  {a}: <err {e}>")

    # After a click, do any new fields appear?
    print("\n-- after click(40, 40) --")
    obs2 = env.step(GameAction.ACTION6, data={"x": 40, "y": 40})
    for a in sorted(dir(obs2)):
        if a.startswith("_"):
            continue
        try:
            v = getattr(obs2, a)
            if callable(v):
                continue
            repr_v = repr(v)
            if len(repr_v) > 200:
                repr_v = repr_v[:200] + "..."
            print(f"  {a}: {repr_v}")
        except Exception:
            pass

    # Compare two different click sequences, same ending foot position
    print("\n-- same foot endpoint, different paths --")
    # Path A: 1 click directly
    env.reset()
    obs_a = env.step(GameAction.ACTION6, data={"x": 30, "y": 30})
    # Path B: 3 clicks ending at the same target
    env.reset()
    env.step(GameAction.ACTION6, data={"x": 20, "y": 25})
    env.step(GameAction.ACTION6, data={"x": 25, "y": 28})
    obs_b = env.step(GameAction.ACTION6, data={"x": 30, "y": 30})
    print("Path A (1 click to 30,30):")
    for a in ("score", "state", "info", "action_input"):
        try:
            v = getattr(obs_a, a, None)
            print(f"  {a}: {repr(v)[:200]}")
        except Exception:
            pass
    print("Path B (3 clicks to 30,30):")
    for a in ("score", "state", "info", "action_input"):
        try:
            v = getattr(obs_b, a, None)
            print(f"  {a}: {repr(v)[:200]}")
        except Exception:
            pass


if __name__ == "__main__":
    main()
