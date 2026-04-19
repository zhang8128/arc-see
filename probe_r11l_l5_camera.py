"""Quick probe: check camera transform and wall layout for L5."""
import copy
import arc_agi
from arcengine import GameAction

arcade = arc_agi.Arcade()
env = arcade.make("r11l-aa269680", render_mode=None)

L1 = [(36, 13), (26, 61), (42, 30)]

def replay_to_l5():
    env.reset()
    env.reset()
    for px, py in L1:
        obs = env.step(GameAction.ACTION6, data={"x": px, "y": py})
    from solve_r11l_v2 import solve_level
    for level in range(2, 5):
        snap = copy.deepcopy(env._game)
        clicks = solve_level(snap, level, level)
        if clicks:
            env._game = copy.deepcopy(snap)
            for cx, cy in clicks:
                obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
                if obs.levels_completed >= level:
                    break
    return obs.levels_completed >= 4

replay_to_l5()
g = env._game

# Check camera transform
cam = g.camera
print("Camera info:")
print(f"  type: {type(cam)}")
for attr in ['x', 'y', 'width', 'height', 'zoom', 'scale', 'offset_x', 'offset_y']:
    if hasattr(cam, attr):
        print(f"  {attr}: {getattr(cam, attr)}")

# Test display_to_grid for various coords
print("\nCamera display_to_grid tests:")
for x, y in [(0,0), (2,50), (32,32), (63,63), (10,25), (59,35)]:
    result = cam.display_to_grid(x, y)
    print(f"  ({x},{y}) -> {result}")

# Check walls
print(f"\nWalls (yhfnp): {len(g.yhfnp)} sprites")
for w in g.yhfnp[:10]:
    print(f"  {w.name}: ({w.x},{w.y}) {w.width}x{w.height}")

# Check if foot[2] can move to (0,48)
foot2 = g.ftmaz[2]
orig = (foot2.x, foot2.y)
foot2.set_position(0, 48)
blocked = any(foot2.collides_with(w) for w in g.yhfnp)
print(f"\nfoot[2] at (0,48): blocked by wall = {blocked}")
if blocked:
    for w in g.yhfnp:
        foot2.set_position(0, 48)
        if foot2.collides_with(w):
            print(f"  Collides with: {w.name} at ({w.x},{w.y}) {w.width}x{w.height}")
foot2.set_position(*orig)

# Check what positions are blocked for foot[2]
print("\nBlocked foot[2] positions in x=[0,5], y=[45,55]:")
for fx in range(0, 6):
    for fy in range(45, 56):
        foot2.set_position(fx, fy)
        blocked = any(foot2.collides_with(w) for w in g.yhfnp)
        if blocked:
            print(f"  ({fx},{fy}): BLOCKED")
foot2.set_position(*orig)

# Test actual game step with click at (2,50)
snap = copy.deepcopy(g)
env._game = snap
# First select foot[2]
f2 = snap.ftmaz[2]
obs = env.step(GameAction.ACTION6, data={"x": f2.x+2, "y": f2.y+2})
print(f"\nSelected foot[2] at ({f2.x+2},{f2.y+2})")
print(f"  mjdkn: {snap.mjdkn}")
print(f"  tfhng: {snap.tfhng}")

# Now try to move to (2,50)
f2_before = (snap.ftmaz[2].x, snap.ftmaz[2].y)
obs = env.step(GameAction.ACTION6, data={"x": 2, "y": 50})
f2_after = (snap.ftmaz[2].x, snap.ftmaz[2].y)
print(f"  Click at (2,50): foot moved {f2_before} -> {f2_after}")

# display_to_grid for (2,50)
result = snap.camera.display_to_grid(2, 50)
print(f"  display_to_grid(2,50) = {result}")
