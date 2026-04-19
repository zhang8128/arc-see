"""R11L L2: find which click in the c-dot sequence caused lc to drop to 0.

The sequence of 13 raw c-dot clicks ended with lc=0, meaning SOMETHING
reset L1's completion. Trace the sequence click-by-click.
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

    c_dots = [
        (39, 48), (41, 48), (38, 49), (42, 49),
        (37, 50), (43, 50), (37, 52), (43, 52),
        (38, 53), (42, 53), (39, 54), (41, 54),
        (40, 51),
    ]

    env._game = copy.deepcopy(snap)
    for i, dot in enumerate(c_dots):
        obs = env.step(GameAction.ACTION6, data={"x": dot[0], "y": dot[1]})
        print(f"  click{i:2d} {dot}: lc={obs.levels_completed}  state={obs.state.name}  avail={list(obs.available_actions)}  full_reset={obs.full_reset}")

    print(f"\nfinal lc={obs.levels_completed}")

    # Also check: what about a shorter sequence?
    print("\n-- only first click --")
    env._game = copy.deepcopy(snap)
    obs = env.step(GameAction.ACTION6, data={"x": 39, "y": 48})
    print(f"  click(39, 48): lc={obs.levels_completed}  state={obs.state.name}")


if __name__ == "__main__":
    main()
