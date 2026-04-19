"""R11L L2: visit each of the 4 hip centers with the HEAD in all orders.

L1 win was 'head visits 3 diamonds in order A → hip → B'. L2 has 4 hips;
maybe the win is head visits all 4 in a specific order.
"""
import copy
import itertools
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

    # Head = click + (1, 1). To place head at each hip center, click = hip - (1, 1).
    hip_centers = [(49, 9), (8, 21), (45, 35), (54, 48)]
    head_clicks = [(x - 1, y - 1) for x, y in hip_centers]
    print(f"head-clicks: {head_clicks}")

    # All 24 perms of 4 head-clicks
    wins = []
    for perm in itertools.permutations(head_clicks):
        env._game = copy.deepcopy(snap)
        lc = 0
        for cx, cy in perm:
            obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            lc = max(lc, obs.levels_completed)
        if lc >= 2:
            wins.append(perm)
            print(f"  WIN: {perm}")
            if len(wins) >= 5:
                return
    print(f"\n4-perm wins: {len(wins)}")

    # Also try 5-click: insert one "extra" click in each position
    extras = head_clicks + [(26, 54), (45, 35), (54, 48), (49, 9), (8, 21)]
    print("\n-- 5-click sequences (4 head visits + 1 extra) --")
    for perm in itertools.permutations(head_clicks):
        for extra in extras:
            for pos in range(5):
                seq = list(perm[:pos]) + [extra] + list(perm[pos:])
                env._game = copy.deepcopy(snap)
                lc = 0
                for cx, cy in seq:
                    obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
                    lc = max(lc, obs.levels_completed)
                if lc >= 2:
                    print(f"  WIN: {seq}")
                    return

    print("no 5-click wins")


if __name__ == "__main__":
    main()
