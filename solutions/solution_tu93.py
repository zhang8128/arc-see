"""Complete solution for TU93 (tu93-2b534c15) — all 9 levels.

TU93 is a grid puzzle with projectiles and enemies. Navigate to exit(s)
while managing moving entities. Found via BFS with state deduplication.

Verified with arc_agi API: 185 total actions vs 378 baseline (51% improvement).
"""
import arc_agi
from arcengine import GameAction

UP, DOWN, LEFT, RIGHT = GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4
D = {"U": UP, "D": DOWN, "L": LEFT, "R": RIGHT}

SOLUTIONS = {
    1: "RDDRURDDLLDRRDRURD",
    2: "URRDRRURRU",
    3: "UURULLULLDRDLLLDRDR",
    4: "RLRLRRRRUULUULLDL",
    5: "LLLRLLLLLDUDUDUDUDDDRDDRRRUUL",
    6: "LLDUDUDDLLRRRDDLDLUDLUULUUUL",
    7: "RRRDDRURUUURDD",
    8: "RRUURRLLLDDRUURRUUULL",
    9: "LLUURDDLUURUURRRDDRDLDLDDLLUR",
}


def verify():
    arcade = arc_agi.Arcade()
    env = arcade.make("tu93-2b534c15", render_mode=None)
    result = env.reset()

    total = 0
    for level_num in range(1, 10):
        moves = SOLUTIONS[level_num]
        for ch in moves:
            result = env.step(D[ch])
            total += 1
        print(f"Level {level_num}: {len(moves):3d} moves, "
              f"levels_completed={result.levels_completed}, state={result.state}")

    print(f"\nTotal: {total} actions")
    print(f"Baseline: {sum([19, 15, 34, 42, 76, 91, 47, 23, 31])}")
    print(f"Final state: {result.state}")
    assert str(result.state) == "GameState.WIN", f"Expected WIN, got {result.state}"
    print("ALL VERIFIED!")


if __name__ == "__main__":
    verify()
