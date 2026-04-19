"""R11L L2: deeper GAME_OVER analysis.

- Does repeating ANY c-dot click game-over at click 5?
- Does repeating a non-c-dot click game-over?
- What distinguishes game-over triggers?
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

    # Test 1: repeat each c-dot 10 times
    print("-- repeat each c-dot 10 times --")
    c_dots = [(39, 48), (41, 48), (38, 49), (42, 49),
              (37, 50), (43, 50), (37, 52), (43, 52),
              (38, 53), (42, 53), (39, 54), (41, 54)]
    for dot in c_dots:
        env._game = copy.deepcopy(snap)
        for i in range(10):
            obs = env.step(GameAction.ACTION6, data={"x": dot[0], "y": dot[1]})
            if obs.state.name == "GAME_OVER":
                print(f"  {dot}: GAME_OVER at click {i}")
                break
        else:
            print(f"  {dot}: no GAME_OVER in 10 clicks")

    # Test 2: repeat non-c-dot clicks
    print("\n-- repeat non-c-dot clicks --")
    tests = [(30, 30), (10, 10), (50, 50), (20, 40), (40, 20), (0, 0)]
    for click in tests:
        env._game = copy.deepcopy(snap)
        for i in range(20):
            obs = env.step(GameAction.ACTION6, data={"x": click[0], "y": click[1]})
            if obs.state.name == "GAME_OVER":
                print(f"  {click}: GAME_OVER at click {i}")
                break
        else:
            print(f"  {click}: no GAME_OVER in 20 clicks")

    # Test 3: does counter matter? Track counter cells over a long sequence
    import numpy as np
    print("\n-- click (30, 30) 10 times, track counter --")
    env._game = copy.deepcopy(snap)
    for i in range(10):
        obs = env.step(GameAction.ACTION6, data={"x": 30, "y": 30})
        g = np.array(obs.frame[-1], dtype=np.int64)
        counter = sum(1 for r in range(64) if int(g[r, 0]) == 5)
        print(f"  click{i}: counter={counter}  state={obs.state.name}  lc={obs.levels_completed}")
        if obs.state.name == "GAME_OVER":
            break


if __name__ == "__main__":
    main()
