"""R11L L2 solver: move feet to get body centroids at hand positions.

Mechanic: click on foot to select, click elsewhere to move.
Body = centroid of all feet for that body.
Win = all bodies' kignw collides with xwdrv (hand).
Budget = 60 actions.
"""
import copy
import arc_agi
from arcengine import GameAction

arcade = arc_agi.Arcade()
env = arcade.make("r11l-aa269680", render_mode=None)
L1 = [(36, 13), (26, 61), (42, 30)]
env.reset()
env.reset()
for px, py in L1:
    env.step(GameAction.ACTION6, data={"x": px, "y": py})
snap = copy.deepcopy(env._game)

g = env._game

# Target: both bodies' centroids at their hands
# qniqj: 3 feet, hand at (37, 48) size 7x7. Center = (40.5, 51.5)
# kpaac: 2 feet, hand at (54, 15) size 7x7. Center = (57.5, 18.5)

# Body = centroid of feet centers - body_half
# Feet center = (foot.x + foot.width//2, foot.y + foot.height//2) = (foot.x+2, foot.y+2)

# For collision: body center must be within (hand_center ± (body_half + hand_half))
# body_half = 2.5, hand_half = 3.5. Range = 6.

# qniqj target centroid: (40.5, 51.5) ± 6 → (34.5-46.5, 45.5-57.5)
# kpaac target centroid: (57.5, 18.5) ± 6 → (51.5-63.5, 12.5-24.5)

# qniqj has feet at (15,4), (6,19), (47,7)
# Centers: (17, 6), (8, 21), (49, 9). Sum = (74, 36). Target sum = 3*(40.5,51.5) = (121.5, 154.5)
# Need to increase sum by (47.5, 118.5). Need feet at higher y values.

# kpaac has feet at (43,33), (52,46)
# Centers: (45, 35), (54, 48). Sum = (99, 83). Target sum = 2*(57.5, 18.5) = (115, 37)
# Need to increase sum by (16, -46). Need one foot at higher x and much lower y.

# Strategy: move each foot to the optimal position, one at a time.
# For qniqj: move all 3 feet to positions near hand center.
# For kpaac: move both feet to positions near hand center.

# qniqj foot targets (each near (40.5, 51.5)):
# foot[0]: move to ~(38, 49) — center at (40, 51) ≈ hand center
# foot[1]: move to ~(38, 49) — same target
# foot[2]: move to ~(38, 49) — same target

# kpaac foot targets (each near (57.5, 18.5)):
# foot[3]: move to ~(55, 16) — center at (57, 18) ≈ hand center
# foot[4]: move to ~(55, 16) — same target

# But we need to check terrain and obstacle constraints!
# Let's just try it and see what happens.

def select_foot(foot_idx):
    """Click on a foot to select it. Returns click coordinates."""
    f = g.ftmaz[foot_idx]
    return (f.x + f.width // 2, f.y + f.height // 2)


# Build the click sequence
clicks = []

# 1. Move foot[0] (already active) to near qniqj hand
clicks.append((40, 53))  # move to near hand, center at (40, 53)

# 2. Select foot[1] at (6, 19)
clicks.append(select_foot(1))  # click on foot[1]

# 3. Move foot[1] to near qniqj hand
clicks.append((40, 53))

# 4. Select foot[2] at (47, 7)
clicks.append(select_foot(2))

# 5. Move foot[2] to near qniqj hand
clicks.append((40, 53))

# 6. Select foot[3] (kpaac) at (43, 33)
clicks.append(select_foot(3))

# 7. Move foot[3] to near kpaac hand
clicks.append((57, 18))

# 8. Select foot[4] (kpaac) at (52, 46)
clicks.append(select_foot(4))

# 9. Move foot[4] to near kpaac hand
clicks.append((57, 18))

print("Click sequence:")
env._game = copy.deepcopy(snap)
for i, (cx, cy) in enumerate(clicks):
    obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
    active = env._game.mjdkn
    act_name = f"({active.x},{active.y})" if active else "None"
    print(f"  {i+1}. click ({cx},{cy}): active={act_name} "
          f"act_count={env._game._action_count} state={obs.state.name}")
    # Check bodies
    for body in env._game.brdck:
        b = env._game.brdck[body]["kignw"]
        h = env._game.dfugm[body]["xwdrv"]
        feet = [(f.x, f.y) for f in env._game.brdck[body]["mdpcc"]]
        col = b.collides_with(h) if b and h else False
        if col:
            print(f"       >>> {body}: COLLISION! body=({b.x},{b.y}) hand=({h.x},{h.y})")
        else:
            print(f"       {body}: body=({b.x},{b.y}) feet={feet}")
    if obs.levels_completed >= 2:
        print(f"\n  >>> WIN! levels_completed={obs.levels_completed} <<<")
        break
    if obs.state.name != "NOT_FINISHED":
        print(f"\n  >>> {obs.state.name} <<<")
        break

print(f"\nFinal: lc={obs.levels_completed} state={obs.state.name} winning={env._game.winning}")
