"""R11L: Replay L1-L5, inspect and solve L6."""
import copy
import numpy as np
import arc_agi
from arcengine import GameAction

arcade = arc_agi.Arcade()
env = arcade.make("r11l-aa269680", render_mode=None)
L1 = [(36, 13), (26, 61), (42, 30)]

# L5 solution clicks (select + move pairs)
L5_CLICKS = [
    (43,34), (9,39), (50,7), (11,18),           # yukft
    (41,47), (48,36),                             # y2: select foot[2], move
    (34,55), (58,44), (10,54),                    # y2: select foot[3], move, move
    (52,55), (10,58), (50,6),                     # y2: select foot[4], move, move
    (10,54), (48,2),                              # y2: select foot[3](now at 8,52), move
]

def replay_to_l6():
    env.reset(); env.reset()
    for px, py in L1:
        obs = env.step(GameAction.ACTION6, data={"x": px, "y": py})
    print(f"After L1: lc={obs.levels_completed}")

    from solve_r11l_v2 import solve_level
    for level in range(2, 5):
        snap = copy.deepcopy(env._game)
        clicks = solve_level(snap, level, level)
        if clicks:
            env._game = copy.deepcopy(snap)
            for cx, cy in clicks:
                obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
                if obs.levels_completed >= level: break
            print(f"After L{level}: lc={obs.levels_completed}")

    # L5
    for cx, cy in L5_CLICKS:
        obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        if obs.levels_completed >= 5:
            print(f"After L5: lc={obs.levels_completed}")
            break

    return obs.levels_completed >= 5

if not replay_to_l6():
    print("Failed to reach L6"); exit(1)

l6_snap = copy.deepcopy(env._game)
g = l6_snap

print("\n=== L6 STATE ===")
print(f"Bodies: {list(g.brdck.keys())}")
print(f"fwqwj: {list(g.fwqwj.keys())}")
print(f"nxahg: {len(g.nxahg)} obstacles")
print(f"ftmaz: {len(g.ftmaz)} feet")

for bname, data in g.brdck.items():
    kignw = data.get("kignw")
    mdpcc = data.get("mdpcc", [])
    hand = g.dfugm.get(bname, {}).get("xwdrv") if bname in g.dfugm else None
    print(f"\n  Body: {bname}")
    if kignw:
        colors = {int(c) for c in np.unique(kignw.pixels) if c > 0}
        print(f"    kignw: {kignw.name} ({kignw.x},{kignw.y}) {kignw.width}x{kignw.height} colors={colors}")
    else:
        print(f"    kignw: None")
    if hand:
        hc = {int(c) for c in np.unique(hand.pixels) if c > 0}
        print(f"    hand: {hand.name} ({hand.x},{hand.y}) {hand.width}x{hand.height} colors={hc}")
    print(f"    feet: {len(mdpcc)}")
    for i, m in enumerate(mdpcc):
        print(f"      {i}: ({m.x},{m.y})")

for i, f in enumerate(g.ftmaz):
    body = g.mfrvmbaujm(f)
    print(f"  foot[{i}]: ({f.x},{f.y}) center ({f.x+2},{f.y+2}) -> {body}")

for obs in g.nxahg:
    colors = {int(c) for c in np.unique(obs.pixels) if c > 0}
    print(f"  obstacle: {obs.name} ({obs.x},{obs.y}) colors={colors}")

print(f"\n  Walls: {len(g.yhfnp)}")

# Try the standard solver
print("\n=== Trying standard solver ===")
from solve_r11l_v2 import solve_level
snap = copy.deepcopy(l6_snap)
result = solve_level(snap, 6, 6)
if result:
    print(f"L6 solution: {len(result)} clicks")
    env._game = copy.deepcopy(l6_snap)
    for cx, cy in result:
        obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        if obs.levels_completed >= 6:
            print(f">>> L6 SOLVED in {len(result)} clicks! <<<")
            break
else:
    print("Standard solver failed for L6")
    # If L6 is also a paint puzzle, need the fast2 approach
    if g.fwqwj:
        print("L6 has fwqwj — it's also a paint puzzle!")
