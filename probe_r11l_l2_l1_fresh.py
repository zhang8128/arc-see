"""R11L L2: apply L1 winning sequence (36, 13), (26, 61), (42, 30) on L2
using fresh reset.
"""
import numpy as np
import arc_agi
from arcengine import GameAction


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

    # Test L1 sequence in L2
    for seq_name, seq in [
        ("L1 in L2", L1),
        ("reversed", list(reversed(L1))),
        ("2x L1", L1 + L1),
        ("L1+L1 interleaved", [(36, 13), (42, 30), (26, 61)]),
    ]:
        obs = play(seq)
        print(f"  {seq_name}: lc={obs.levels_completed}  state={obs.state.name}")

    # Test: single click that might TRIGGER L2 setup
    print("\n-- single clicks that might trigger L2 --")
    for c in [(36, 13), (26, 58), (27, 59), (42, 30), (16, 6), (49, 41), (40, 51)]:
        obs = play([c])
        print(f"  {c}: lc={obs.levels_completed}  state={obs.state.name}")


if __name__ == "__main__":
    main()
