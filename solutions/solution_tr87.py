"""Complete solution for TR87 (tr87-cd924810) — all 6 levels.

Verified with arc_agi API: GameState.WIN, 124 total actions.
Baseline: 317 actions. Our solution: 61% improvement.

L1-L4: Solved via brute-force target finding + pure-Python BFS.
L5-L6: alter_rules mode — BFS with game engine.
"""

SOLUTIONS = {
    1: "ACTION2 ACTION2 ACTION3 ACTION2 ACTION2 ACTION3 ACTION2 ACTION3 ACTION1 ACTION1 ACTION1 ACTION3 ACTION2 ACTION2",  # 14 actions
    2: "ACTION2 ACTION2 ACTION2 ACTION3 ACTION2 ACTION2 ACTION2 ACTION3 ACTION1 ACTION1 ACTION1 ACTION3 ACTION1 ACTION1 ACTION1 ACTION3 ACTION1 ACTION1 ACTION3 ACTION1 ACTION1 ACTION1 ACTION3 ACTION2 ACTION2",  # 25 actions
    3: "ACTION2 ACTION3 ACTION2 ACTION2 ACTION3 ACTION2 ACTION2 ACTION3 ACTION1 ACTION1 ACTION1 ACTION3 ACTION2 ACTION2 ACTION3 ACTION2 ACTION2 ACTION2 ACTION3 ACTION2 ACTION2",  # 21 actions
    4: "ACTION1 ACTION1 ACTION1 ACTION3 ACTION2 ACTION3 ACTION1 ACTION1 ACTION1 ACTION3 ACTION2 ACTION2 ACTION3 ACTION3 ACTION1 ACTION1 ACTION1 ACTION3 ACTION1 ACTION1 ACTION1",  # 21 actions
    5: "ACTION2 ACTION2 ACTION2 ACTION4 ACTION2 ACTION2 ACTION4 ACTION1 ACTION4 ACTION1 ACTION4 ACTION2 ACTION4 ACTION1 ACTION1 ACTION4 ACTION1 ACTION1 ACTION1",  # 19 actions
    6: "ACTION1 ACTION1 ACTION4 ACTION1 ACTION1 ACTION4 ACTION4 ACTION1 ACTION4 ACTION4 ACTION2 ACTION4 ACTION1 ACTION1 ACTION4 ACTION4 ACTION2 ACTION4 ACTION4 ACTION1 ACTION4 ACTION1 ACTION1 ACTION1",  # 24 actions
}

def verify():
    """Verify all solutions with the arc_agi API."""
    import arc_agi
    from arcengine import GameAction

    arcade = arc_agi.Arcade()
    env = arcade.make("tr87-cd924810", render_mode=None)
    env.reset()

    total = 0
    for level_num in range(1, 7):
        actions = SOLUTIONS[level_num].split()
        for a in actions:
            result = env.step(getattr(GameAction, a))
        total += len(actions)
        print(f"Level {level_num}: {len(actions):3d} actions, levels_completed={result.levels_completed}")

    print(f"\nTotal: {total} actions")
    print(f"Final state: {result.state}")
    assert result.levels_completed == 6, f"Expected 6 levels, got {result.levels_completed}"
    assert str(result.state) == "GameState.WIN", f"Expected WIN, got {result.state}"
    print("ALL VERIFIED!")

if __name__ == "__main__":
    verify()
