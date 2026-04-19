"""Complete solution for TN36 (tn36-ab4f63cc) — all 7 levels.

TN36 is a register programming puzzle. Right panel has a block and goal.
Click register bits to program instructions, click execute to run.
Multi-phase levels use grid positions as checkpoints.

Verified with arc_agi API.
"""
import importlib.util
import arc_agi
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('tn36', 'environment_files/tn36/ab4f63cc/tn36.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

CLICK = GameAction.ACTION6

# Solutions: list of programs per level (multi-phase for L6, L7)
SOLUTIONS = {
    1: [[3, 3, 3, 3, 3]],              # down4 x5
    2: [[33, 33, 33, 33]],             # up4 x4
    3: [[33, 2, 2, 2, 2, 33]],         # up, right x4, up (through wall gap)
    4: [[9, 1, 3, 3, 3, 3]],           # scale-1, left4, down4 x4
    5: [[5, 63, 3, 3, 3, 8]],          # rot90, color15, down4 x3, scale+1
    6: [                                 # 4-phase: checkpoints at grid positions
        [2, 2, 2, 2, 2, 0],            # -> (53,28)
        [1, 33, 33, 0, 0, 0],          # -> (49,20)
        [33, 33, 33, 33, 2, 0],        # -> (53,4)
        [1, 1, 1, 1, 3, 0],            # -> (37,8) = goal
    ],
    7: [                                 # 3-phase: avoid toggle walls at y=16-19
        [33, 33, 2, 2, 2, 3],          # -> (53,24) checkpoint
        [33, 33, 33, 33, 0, 0],        # -> (53,8) checkpoint
        [3, 1, 1, 1, 33, 0],           # -> (41,8) = goal
    ],
}


def play_level_local(level_idx, programs):
    """Play a level locally and return click sequence for API."""
    g = mod.Tn36()
    g.set_level(level_idx)
    right = g.tsflfunycx.xsseeglmfh
    prog_obj = right.fcrcpemsnv
    exec_btn = right.owdgwmdfzu
    all_clicks = []

    for target_prog in programs:
        # Compute bit toggle clicks
        for i, reg in enumerate(prog_obj.thofkgziyd):
            if i >= len(target_prog):
                break
            cv = reg.kbswvermjk
            tv = target_prog[i]
            diff = cv ^ tv
            for j, bit in enumerate(reg.puakvdstpr):
                if diff & (1 << j):
                    cx = bit.qmbzztjrjk.x + bit.qmbzztjrjk.width // 2
                    cy = bit.qmbzztjrjk.y + bit.qmbzztjrjk.height // 2
                    all_clicks.append((cx, cy))
                    g.perform_action(ActionInput(id=CLICK, data={"x": cx, "y": cy}))

        # Execute click
        ex = exec_btn.x + exec_btn.width // 2
        ey = exec_btn.y + exec_btn.height // 2
        all_clicks.append((ex, ey))
        g.perform_action(ActionInput(id=CLICK, data={"x": ex, "y": ey}))

        if g._current_level_index > level_idx or g._state.name == "WIN":
            break

    won = g._current_level_index > level_idx or g._state.name == "WIN"
    return all_clicks, won


def verify():
    """Verify all solutions with the arc_agi API."""
    arcade = arc_agi.Arcade()
    env = arcade.make("tn36-ab4f63cc", render_mode=None)
    result = env.reset()
    print(f"Game started: {result.state}")

    total = 0
    for level_num in range(1, 8):
        programs = SOLUTIONS[level_num]
        clicks, won_local = play_level_local(level_num - 1, programs)

        for cx, cy in clicks:
            result = env.step(CLICK, data={"x": cx, "y": cy})
            total += 1

        print(f"Level {level_num}: {len(clicks):3d} clicks, "
              f"levels_completed={result.levels_completed}, state={result.state}")

    print(f"\nTotal: {total} actions")
    print(f"Baseline: {sum([23, 22, 26, 37, 25, 56, 61])}")
    print(f"Final state: {result.state}")
    assert str(result.state) == "GameState.WIN", f"Expected WIN, got {result.state}"
    print("ALL VERIFIED!")


if __name__ == "__main__":
    verify()
