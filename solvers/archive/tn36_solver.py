"""TN36 solver — register programming puzzle.

Game: Click register bits on the right panel to program instructions,
then execute. Block must match goal (position, rotation, scale, color).

Instructions:
  0=toggle, 1=left4, 2=right4, 3=down4, 5=rot90, 6=rot-90, 7=rot180,
  8=scale+1, 9=scale-1, 10/11=right8, 12/13=left8, 14=color9, 15=color8,
  16=rot270, 33=up4, 34=left4, 63=color15
"""
import importlib.util
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('tn36', 'environment_files/tn36/ab4f63cc/tn36.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

CLICK = GameAction.ACTION6

# oocxrjijjq = 4 (movement step size)
OPCODES = {
    0: "toggle", 1: "left4", 2: "right4", 3: "down4",
    5: "rot90", 6: "rot-90", 7: "rot180", 8: "scale+1", 9: "scale-1",
    10: "right8", 11: "right8", 12: "left8", 13: "left8",
    14: "color9", 15: "color8", 16: "rot270",
    33: "up4", 34: "left4", 63: "color15",
}


def act(g, data=None):
    return g.perform_action(ActionInput(id=CLICK, data=data or {}))


def analyze_level(level_idx):
    """Analyze a level and find the solution."""
    g = mod.Tn36()
    g.set_level(level_idx)

    sm = g.tsflfunycx
    right = sm.xsseeglmfh
    left = sm.kmhfvaisxu
    prog = right.fcrcpemsnv

    rb = right.ravxreuqho
    rg = right.ddzsdagbti

    print(f"\n=== Level {level_idx + 1} ===")
    print(f"Block: ({rb.x},{rb.y}) rot={rb.rotation} scale={rb.scale} color={rb.dtxpbtpcbh}")
    if rg:
        print(f"Goal:  ({rg.x},{rg.y}) rot={rg.rotation} scale={rg.scale} color={rg.dtxpbtpcbh}")
    print(f"Current program: {right.nensmzujat}")
    print(f"ReadOnly: {prog.scpsempaey}")
    print(f"Num registers: {len(prog.thofkgziyd)}")

    # Figure out needed program
    if rg:
        dx = rg.x - rb.x
        dy = rg.y - rb.y
        drot = (rg.rotation - rb.rotation) % 360
        dscale = rg.scale - rb.scale
        dcolor = rg.dtxpbtpcbh != rb.dtxpbtpcbh

        print(f"Delta: dx={dx} dy={dy} drot={drot} dscale={dscale} dcolor={dcolor}")

    # Show buttons
    if sm.mcxkhvobyv:
        print(f"Buttons: {len(sm.mcxkhvobyv)}")
        for i, btn in enumerate(sm.mcxkhvobyv):
            print(f"  Button {i}: ({btn.x},{btn.y})")

    if sm.yobglothsl:
        print(f"Programs: {sm.yobglothsl}")

    # Register details
    for i, reg in enumerate(prog.thofkgziyd):
        val = reg.kbswvermjk
        num_bits = len(reg.puakvdstpr)
        print(f"  Reg {i}: val={val} ({num_bits} bits)")

    return g


def find_program(start, goal, num_regs):
    """Find instruction sequence to transform start to goal.
    start/goal: (x, y, rotation, scale, color)
    """
    sx, sy, srot, sscale, scolor = start
    gx, gy, grot, gscale, gcolor = goal

    instructions = []

    # Handle color first (if needed)
    if scolor != gcolor:
        if gcolor == 9:
            instructions.append(14)
        elif gcolor == 8:
            instructions.append(15)
        elif gcolor == 15:
            instructions.append(63)

    # Handle scale
    while sscale < gscale:
        instructions.append(8)  # scale+1
        sscale += 1
    while sscale > gscale:
        instructions.append(9)  # scale-1
        sscale -= 1

    # Handle rotation
    drot = (grot - srot) % 360
    if drot == 90:
        instructions.append(5)
    elif drot == 180:
        instructions.append(7)
    elif drot == 270:
        instructions.append(16)

    # Handle movement
    dx = gx - sx
    dy = gy - sy

    # Use double moves where possible
    while dx >= 8:
        instructions.append(10)  # right8
        dx -= 8
    while dx <= -8:
        instructions.append(12)  # left8
        dx += 8
    while dx >= 4:
        instructions.append(2)  # right4
        dx -= 4
    while dx <= -4:
        instructions.append(1)  # left4
        dx += 4
    while dy >= 4:
        instructions.append(3)  # down4
        dy -= 4
    while dy <= -4:
        instructions.append(33)  # up4
        dy += 4

    # Pad with 0 (toggle, will cancel out) if even number needed
    while len(instructions) < num_regs:
        instructions.append(0)

    if len(instructions) > num_regs:
        print(f"WARNING: need {len(instructions)} instructions but only {num_regs} registers!")
        # Try to use double-moves to compress
        return None

    return instructions


def compute_clicks(g, target_program):
    """Compute the clicks needed to set the right panel's registers to target_program.
    Returns list of (x, y) click coordinates.
    """
    right = g.tsflfunycx.xsseeglmfh
    prog = right.fcrcpemsnv
    clicks = []

    for i, reg in enumerate(prog.thofkgziyd):
        if i >= len(target_program):
            break
        current_val = reg.kbswvermjk
        target_val = target_program[i]

        if current_val == target_val:
            continue

        # XOR to find which bits need toggling
        diff = current_val ^ target_val
        for j, bit in enumerate(reg.puakvdstpr):
            if diff & (1 << j):
                # Need to toggle this bit — click at its center
                cx = bit.qmbzztjrjk.x + bit.qmbzztjrjk.width // 2
                cy = bit.qmbzztjrjk.y + bit.qmbzztjrjk.height // 2
                clicks.append((cx, cy))

    return clicks


def find_execute_click(g):
    """Find the coordinate to click to execute the right panel."""
    right = g.tsflfunycx.xsseeglmfh
    # Click somewhere on the right panel that's NOT a register
    # The execute button is owdgwmdfzu (if it exists)
    if right.owdgwmdfzu:
        btn = right.owdgwmdfzu
        cx = btn.x + btn.width // 2
        cy = btn.y + btn.height // 2
        return (cx, cy)
    # Otherwise click the panel area
    return (right.x + right.width // 2, right.y + 2)


def solve_level(level_idx):
    """Solve a single level. Returns list of (x,y) clicks."""
    g = mod.Tn36()
    g.set_level(level_idx)

    sm = g.tsflfunycx
    right = sm.xsseeglmfh
    rb = right.ravxreuqho
    rg = right.ddzsdagbti

    if not rg:
        print(f"Level {level_idx+1}: No goal on right panel!")
        return None

    start = (rb.x, rb.y, rb.rotation, rb.scale, int(rb.dtxpbtpcbh))
    goal = (rg.x, rg.y, rg.rotation, rg.scale, int(rg.dtxpbtpcbh))
    num_regs = len(right.fcrcpemsnv.thofkgziyd)

    print(f"\nLevel {level_idx+1}: {start} -> {goal} ({num_regs} regs)")

    target = find_program(start, goal, num_regs)
    if target is None:
        print(f"  No program found!")
        return None

    print(f"  Target program: {target} ({[OPCODES.get(t, f'?{t}') for t in target]})")

    # Compute register clicks
    reg_clicks = compute_clicks(g, target)
    print(f"  Register clicks: {len(reg_clicks)}")

    # Execute click
    exec_click = find_execute_click(g)
    print(f"  Execute click: {exec_click}")

    all_clicks = reg_clicks + [exec_click]

    # Verify by replaying
    g2 = mod.Tn36()
    g2.set_level(level_idx)
    for (x, y) in all_clicks:
        act(g2, {"x": x, "y": y})

    won = g2.tsflfunycx.xsseeglmfh.yxabhsirzl
    print(f"  Result: win={won}, level_idx={g2._current_level_index}")

    if not won:
        # Check state
        rb2 = g2.tsflfunycx.xsseeglmfh.ravxreuqho
        print(f"  Block after: ({rb2.x},{rb2.y}) rot={rb2.rotation} scale={rb2.scale} color={rb2.dtxpbtpcbh}")
        prog2 = g2.tsflfunycx.xsseeglmfh.fcrcpemsnv
        print(f"  Program set: {[r.kbswvermjk for r in prog2.thofkgziyd]}")

    return all_clicks


if __name__ == "__main__":
    for i in range(7):
        analyze_level(i)

    print("\n" + "="*60)
    print("SOLVING")
    print("="*60)

    for i in range(7):
        clicks = solve_level(i)
