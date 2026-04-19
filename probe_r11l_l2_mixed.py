"""R11L L2: test game-over hypothesis with mixed click sequences.

Hypothesis: game-over fires when counter hits 5 AND arm 1 foot is at
saturation (31, 14). If foot is elsewhere, no game-over.
"""
import copy
import numpy as np
import arc_agi
from arcengine import GameAction


def foot_of_arm1(g):
    sixes = np.argwhere(g == 6)
    for y, x in sixes:
        if (int(x), int(y)) != (49, 41):
            return (int(x), int(y))
    return None


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    L1 = [(36, 13), (26, 61), (42, 30)]
    env.reset()
    for cx, cy in L1:
        env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
    snap = copy.deepcopy(env._game)

    # Test 1: 4x (10, 10), then 1x (30, 30). Counter = 5, foot jumps to (31, 14).
    print("-- 4x (10,10), 1x (30,30) --")
    env._game = copy.deepcopy(snap)
    for i in range(4):
        obs = env.step(GameAction.ACTION6, data={"x": 10, "y": 10})
    obs = env.step(GameAction.ACTION6, data={"x": 30, "y": 30})
    g = np.array(obs.frame[-1], dtype=np.int64)
    print(f"  after 5 clicks: foot={foot_of_arm1(g)}  state={obs.state.name}  lc={obs.levels_completed}")

    # Test 2: 3x (30, 30), 2x (10, 10). Counter at 5, foot at?
    print("\n-- 3x (30,30), 2x (10,10) --")
    env._game = copy.deepcopy(snap)
    for i in range(3):
        env.step(GameAction.ACTION6, data={"x": 30, "y": 30})
    for i in range(2):
        obs = env.step(GameAction.ACTION6, data={"x": 10, "y": 10})
    g = np.array(obs.frame[-1], dtype=np.int64)
    print(f"  after 5 clicks: foot={foot_of_arm1(g)}  state={obs.state.name}")

    # Test 3: 4x (10, 10), 1x (0, 0). Counter = 5, foot stays (22, 13)?
    print("\n-- 4x (10,10), 1x (0,0) --")
    env._game = copy.deepcopy(snap)
    for i in range(4):
        env.step(GameAction.ACTION6, data={"x": 10, "y": 10})
    obs = env.step(GameAction.ACTION6, data={"x": 0, "y": 0})
    g = np.array(obs.frame[-1], dtype=np.int64)
    print(f"  after 5 clicks: foot={foot_of_arm1(g)}  state={obs.state.name}")

    # Test 4: what IS the game-over condition? Click 30,30 once, then try various things
    print("\n-- arm 1 at saturated (31, 14), then single (10, 10) --")
    env._game = copy.deepcopy(snap)
    env.step(GameAction.ACTION6, data={"x": 30, "y": 30})  # foot → (31, 14), counter=1
    obs = env.step(GameAction.ACTION6, data={"x": 10, "y": 10})  # foot → (22, 13)
    g = np.array(obs.frame[-1], dtype=np.int64)
    print(f"  foot={foot_of_arm1(g)}  state={obs.state.name}")

    # Test 5: trace what happens at exact game-over boundary for (30, 30)
    print("\n-- (30, 30) x 5, track foot --")
    env._game = copy.deepcopy(snap)
    for i in range(5):
        obs = env.step(GameAction.ACTION6, data={"x": 30, "y": 30})
        g = np.array(obs.frame[-1], dtype=np.int64)
        print(f"  click{i}: foot={foot_of_arm1(g)}  state={obs.state.name}")
        if obs.state.name == "GAME_OVER":
            break


if __name__ == "__main__":
    main()
