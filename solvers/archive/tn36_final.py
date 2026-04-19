"""TN36 solver — manually planned paths accounting for walls.

Instruction opcodes: 0=noop, 1=left4, 2=right4, 3=down4, 5=rot90,
8=scale+1, 9=scale-1, 33=up4, 34=left4, 63=color15
"""
import importlib.util
import arc_agi
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('tn36', 'environment_files/tn36/ab4f63cc/tn36.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

CLICK = GameAction.ACTION6

SLOT_XY = {}  # populated per level


def act(g, data=None):
    return g.perform_action(ActionInput(id=CLICK, data=data or {}))


def compute_clicks(g, level_idx, target_program):
    """Compute clicks to set right panel registers + execute."""
    g2 = mod.Tn36()
    g2.set_level(level_idx)
    right = g2.tsflfunycx.xsseeglmfh
    prog = right.fcrcpemsnv
    clicks = []

    for i, reg in enumerate(prog.thofkgziyd):
        if i >= len(target_program):
            break
        current_val = reg.kbswvermjk
        target_val = target_program[i]
        diff = current_val ^ target_val
        for j, bit in enumerate(reg.puakvdstpr):
            if diff & (1 << j):
                cx = bit.qmbzztjrjk.x + bit.qmbzztjrjk.width // 2
                cy = bit.qmbzztjrjk.y + bit.qmbzztjrjk.height // 2
                clicks.append((cx, cy))

    # Execute button
    exec_btn = right.owdgwmdfzu
    if exec_btn:
        clicks.append((exec_btn.x + exec_btn.width // 2,
                        exec_btn.y + exec_btn.height // 2))

    return clicks


def verify_local(level_idx, target_program):
    """Verify a solution using local game engine."""
    g = mod.Tn36()
    g.set_level(level_idx)
    right = g.tsflfunycx.xsseeglmfh
    prog = right.fcrcpemsnv

    # Set registers directly
    for i, reg in enumerate(prog.thofkgziyd):
        if i < len(target_program):
            reg.zpzcmabenn(target_program[i])

    # Execute via button click
    exec_btn = right.owdgwmdfzu
    if exec_btn:
        act(g, {"x": exec_btn.x + exec_btn.width // 2,
                "y": exec_btn.y + exec_btn.height // 2})

    return g._current_level_index > level_idx or g._state.name == "WIN"


# Solutions: target programs for each level
# Level 1: (30,13) -> (30,33), no walls, 5 regs (2-bit)
# dy=+20 = 5*down4. Program: [3,3,3,3,3]
L1 = [3, 3, 3, 3, 3]

# Level 2: (45,24) -> (45,8), no walls, 4 regs (6-bit)
# dy=-16 = 4*up4. Program: [33,33,33,33]
L2 = [33, 33, 33, 33]

# Level 3: (37,20) -> (53,12), walls at (45,20,4x12) and (45,4,4x12)
# Gap at y=16-19. Path: up4 to y=16, right4x4 through gap, up4 to y=12
# [33, 2, 2, 2, 2, 33]
L3 = [33, 2, 2, 2, 2, 33]

# Level 4: (45,8) s=2 -> (41,24) s=1, walls at (33,20,8x4) and (45,20,16x4)
# Block starts at scale 2 (8x8), needs scale 1 (4x4)
# At scale 2 at (45,8): block covers (45-52, 8-15)
# Need: scale-1, move left 4, move down 16
# Wall at (45,20) with 16x4 means x=45-60, y=20-23 blocked
# Wall at (33,20) with 8x4 means x=33-40, y=20-23 blocked
# At scale 1, block is 4x4. From (45,8) after scale-1: (45,8) 4x4
# left4: (41,8). down4x4: (41,24). But wall at (33,20) is x=33-40, block at x=41 doesn't overlap. OK!
# Wait, wall at (45,20) is x=45-60. After left to (41,8), going down to (41,20): block at (41-44,20-23).
# Wall at (45,20) is (45-60,20-23). No overlap at x=41-44 vs 45-60. OK!
# Program: [9, 1, 3, 3, 3, 3] = scale-1, left4, down4x4
L4 = [9, 1, 3, 3, 3, 3]

# Level 5: (49,8) r=270 s=1 c=11 -> (49,20) r=0 s=2 c=15
# walls at (53,16,8x4) and (33,16,16x4)
# Need: rot90, scale+1, color15, move down 12
# At scale 1 at (49,8): block 4x4. After scale+1: block 8x8 at (49,8) covers (49-56,8-15)
# After down4: (49,12) covers (49-56,12-19). Wall at (53,16) is (53-60,16-19). Overlap! Blocked.
# So scale up AFTER moving down to avoid wall.
# Path: rot90, down4x3 = (49,20), scale+1 = covers (49-56,20-27). No wall overlap. color15.
# But at scale 1 moving down from (49,8): no wall issues since walls at y=16 and block at y=8.
# down4: (49,12), block (49-52,12-15). Wall at (53,16): no overlap. OK
# down4: (49,16), block (49-52,16-19). Wall at (53,16): wall is (53-60,16-19). No overlap at x=49-52 vs 53-60. OK!
# down4: (49,20), block (49-52,20-23). No wall. OK.
# Now scale+1: (49,20) scale 2 = (49-56,20-27). No wall overlap. OK.
# Now rot90 and color15.
# Wait, rotation needs to go from 270 to 0, which is rot90 (+90). And color to 15 = opcode 63.
# Program: [5, 63, 3, 3, 3, 8] = rot90, color15, down4x3, scale+1
L5 = [5, 63, 3, 3, 3, 8]

# Level 6: (33,28) r=90 -> (37,8) r=90, walls at (33,24,16x4),(53,8,4x20),(45,8,4x12),(37,12,4x12)
# gridPos: (53,28,1), (49,20,1), (53,4,1)
# dx=+4, dy=-20. Need right4, up4x5
# Walls analysis:
# (33,24,16x4): x=33-48, y=24-27. Block at (33,28) 4x4 is at y=28-31, just below this wall.
# (53,8,4x20): x=53-56, y=8-27
# (45,8,4x12): x=45-48, y=8-19
# (37,12,4x12): x=37-40, y=12-23
#
# Block at (33,28), need to reach (37,8).
# right4: (37,28). Block covers (37-40,28-31). Wall (37,12) covers (37-40,12-23). No overlap. OK
# up4: (37,24). Block (37-40,24-27). Wall (33,24) covers (33-48,24-27). Overlap! Blocked.
#
# Hmm, wall at (33,24) blocks y=24. Let me think...
# From (33,28) up4: (33,24). Block (33-36,24-27). Wall (33,24,16x4) = (33-48,24-27). Overlap! Blocked.
# So we can't go up from y=28 either.
#
# Grid positions: (53,28), (49,20), (53,4). These seem to be checkpoint positions.
# Maybe this level requires multi-step: move to gridPos, then continue from there?
#
# Wait - the grid positions update the block's saved position. When the block lands on a grid position
# during execution, nklxbrmrww saves it. Then if the program ends unsuccessfully, the block stays at
# the grid position for the next attempt. But reset=True means the block DOES reset.
#
# Actually, looking at zhxlrqdrcn more carefully, when execution ends and NOT won:
# if self.fcrcpemsnv.dtkijoiuip:  # reset flag
#     self.aasnichwxq()  # reset block to saved position
# But nklxbrmrww was called earlier if block is on a grid position!
# So the block gets saved at grid position and then "reset" to the grid position.
# This means grid positions are CHECKPOINTS - the block stays there between attempts!
#
# So level 6 is multi-step:
# Step 1: Move from (33,28) to grid position (53,28). dx=+20 = right4x5
#          Wall check: (33,24) at y=24-27 won't block horizontal movement at y=28.
#          Wall (53,8) at (53-56,8-27). Block at (53,28) covers (53-56,28-31). No overlap (wall ends at y=27). OK
#          Program: [2,2,2,2,2,0] = right4x5 + noop
#          This gets block to (53,28) which IS a grid position. Block saved there.
#
# Step 2: From (53,28), move to (49,20). dy=-8, dx=-4
#          up4: (53,24). Block (53-56,24-27). Wall (53,8) covers (53-56,8-27). Overlap! Blocked.
#          Hmm. left4: (49,28). Then up to y=20?
#          left4: (49,28). up4: (49,24). Block (49-52,24-27). Wall (33,24) covers (33-48,24-27). No overlap at x=49-52 vs 33-48. OK!
#          up4: (49,20). Block (49-52,20-23). Wall (45,8) covers (45-48,8-19). No overlap. OK!
#          Program: [1,33,33,0,0,0] = left4, up4, up4, noop, noop, noop
#          Block at (49,20) IS a grid position. Saved.
#
# Step 3: From (49,20), move to (53,4).
#          right4: (53,20). Block (53-56,20-23). Wall (53,8) covers (53-56,8-27). Overlap! Blocked.
#          Hmm. Up first to y=4? But wall (45,8) at (45-48,8-19) and (53,8) at (53-56,8-27).
#          From (49,20): up4: (49,16). Block (49-52,16-19). Wall (45,8) at (45-48,8-19). No overlap at x=49-52 vs 45-48. OK
#          up4: (49,12). OK. up4: (49,8). OK. up4: (49,4). OK.
#          right4: (53,4). Block (53-56,4-7). Wall (53,8) at (53-56,8-27). No overlap at y=4-7 vs 8-27. OK!
#          Program: [33,33,33,33,2,0] = up4x4, right4, noop
#          Block at (53,4) IS a grid position. Saved.
#
# Step 4: From (53,4), move to (37,8). dx=-16, dy=+4
#          left4: (49,4). Block (49-52,4-7). OK.
#          left4: (45,4). Wall (45,8) at (45-48,8-19). Block at (45-48,4-7). No overlap. OK!
#          down4: (45,8). Block (45-48,8-11). Wall (45,8) at (45-48,8-19). OVERLAP! Blocked.
#          Hmm. So can't go down at x=45 because of wall.
#
#          Alternative: left all the way first.
#          From (53,4): left4x4: (53→49→45→41→37). All at y=4, no wall overlap.
#          Then down4: (37,8). Block (37-40,8-11). Wall (37,12) at (37-40,12-23). No overlap at y=8-11 vs 12-23. OK!
#          Program: [1,1,1,1,3,0] = left4x4, down4, noop
#          Block at (37,8) = GOAL!

# So level 6 needs 4 separate clicks of execute button (4 programs).
# But each program execution costs 1 click (execute button). Plus the register setting clicks.

# Actually wait — I need to re-examine. Looking at the execution flow:
# After a program runs and the block lands on a grid position, the block position is saved.
# Then if NOT won, the block resets (aasnichwxq) to the saved position.
# So the block stays at the grid position for the next attempt.
# But the program registers are still whatever they were set to.
# For the next attempt, I need to:
# 1. Click register bits to change the program
# 2. Click execute again

# For Level 6, I need 4 phases:
# Phase 1: set program [2,2,2,2,2,0], execute → block saves at (53,28)
# Phase 2: set program [1,33,33,0,0,0], execute → block saves at (49,20)
# Phase 3: set program [33,33,33,33,2,0], execute → block saves at (53,4)
# Phase 4: set program [1,1,1,1,3,0], execute → block at (37,8) = WIN

# Level 7 is even more complex with toggle walls...
# Let me figure it out step by step.

# Level 7: (41,28) -> (41,8), walls at many places, toggleWalls at (37-50,16,4x4) and (37-50,16,4x4)
# Wait the toggle walls are at (47,16,14x4) and (37,16,14x4). Both at y=16-19, covering x=37-50 and x=47-60.
# Actually: (47,16,14x4) = x=47-60,y=16-19 and (37,16,14x4) = x=37-50,y=16-19
# Together they cover x=37-60, y=16-19 when visible.
# They start invisible and toggle every 3 instructions.
# Static walls: (37,8,4x4)=(37-40,8-11), (45,8,4x4)=(45-48,8-11), (33,16,4x4)=(33-36,16-19),
#               (49,24,4x8)=(49-52,24-31), (37,4,12x4)=(37-48,4-7)
# gridPos: (41,28,1), (53,24,1), (53,8,1), (33,12,1)

# This is complex. Let me work on it later and focus on what I have.

SOLUTIONS = {
    0: {"programs": [[3, 3, 3, 3, 3]]},
    1: {"programs": [[33, 33, 33, 33]]},
    2: {"programs": [[33, 2, 2, 2, 2, 33]]},
    3: {"programs": [[9, 1, 3, 3, 3, 3]]},
    4: {"programs": [[5, 63, 3, 3, 3, 8]]},
    5: {"programs": [
        [2, 2, 2, 2, 2, 0],   # -> (53,28)
        [1, 33, 33, 0, 0, 0], # -> (49,20)
        [33, 33, 33, 33, 2, 0], # -> (53,4)
        [1, 1, 1, 1, 3, 0],   # -> (37,8)
    ]},
    6: None,  # TODO: figure out level 7
}


def solve_and_verify():
    """Test all solutions locally."""
    for level_idx in range(7):
        sol = SOLUTIONS.get(level_idx)
        if sol is None:
            print(f"Level {level_idx+1}: TODO")
            continue

        programs = sol["programs"]
        g = mod.Tn36()
        g.set_level(level_idx)

        for prog_idx, target_prog in enumerate(programs):
            right = g.tsflfunycx.xsseeglmfh
            prog = right.fcrcpemsnv

            # Set registers
            for i, reg in enumerate(prog.thofkgziyd):
                if i < len(target_prog):
                    reg.zpzcmabenn(target_prog[i])

            # Execute
            exec_btn = right.owdgwmdfzu
            if exec_btn:
                act(g, {"x": exec_btn.x + exec_btn.width // 2,
                        "y": exec_btn.y + exec_btn.height // 2})

            rb = right.ravxreuqho
            status = "WIN" if (g._current_level_index > level_idx or g._state.name == "WIN") else f"block=({rb.x},{rb.y})"
            print(f"Level {level_idx+1} phase {prog_idx+1}: {target_prog} -> {status}")

            if g._current_level_index > level_idx or g._state.name == "WIN":
                break

        won = g._current_level_index > level_idx or g._state.name == "WIN"
        print(f"  Level {level_idx+1}: {'✓' if won else '✗'}")
        print()


if __name__ == "__main__":
    solve_and_verify()
