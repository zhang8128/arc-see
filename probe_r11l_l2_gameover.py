"""R11L L2: trace GAME_OVER triggers.

Does click (37, 50) always game-over, or only after specific prior clicks?
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

    # Test 1: single click (37, 50) from fresh L2
    print("-- single click (37, 50) from L2 init --")
    env._game = copy.deepcopy(snap)
    obs = env.step(GameAction.ACTION6, data={"x": 37, "y": 50})
    print(f"  lc={obs.levels_completed}  state={obs.state.name}")

    # Test 2: all single clicks, find which game-over
    print("\n-- all 4096 single clicks, find GAME_OVER triggers --")
    game_over_clicks = []
    for cy in range(64):
        for cx in range(64):
            env._game = copy.deepcopy(snap)
            obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            if obs.state.name == "GAME_OVER":
                game_over_clicks.append((cx, cy))
    print(f"  total single-click GAME_OVERs: {len(game_over_clicks)}")
    if game_over_clicks:
        # Print the set
        xs = [p[0] for p in game_over_clicks]
        ys = [p[1] for p in game_over_clicks]
        print(f"  x range: {min(xs)}..{max(xs)}  y range: {min(ys)}..{max(ys)}")

        # Visualize
        go_set = set(game_over_clicks)
        print("  GAME_OVER click map (# = game-over):")
        for cy in range(0, 64, 2):
            row = "".join("#" if (cx, cy) in go_set else "." for cx in range(0, 64, 2))
            print(f"    y={cy:2d}: {row}")

    # Test 3: single click (37, 50) 5 times — does cumulative hit?
    print("\n-- repeat click (37, 50) 10 times --")
    env._game = copy.deepcopy(snap)
    for i in range(10):
        obs = env.step(GameAction.ACTION6, data={"x": 37, "y": 50})
        print(f"  click{i}: lc={obs.levels_completed}  state={obs.state.name}")
        if obs.state.name in ("GAME_OVER", "WIN"):
            break


if __name__ == "__main__":
    main()
