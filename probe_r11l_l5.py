"""Probe R11L L5: inspect body/obstacle sprites and test absorption orders."""
import copy
import numpy as np
import arc_agi
from arcengine import GameAction

arcade = arc_agi.Arcade()
env = arcade.make("r11l-aa269680", render_mode=None)

# L1 solution
L1 = [(36, 13), (26, 61), (42, 30)]

def replay_to_l5():
    """Replay L1-L4 to reach L5."""
    env.reset()
    env.reset()
    # L1
    for px, py in L1:
        obs = env.step(GameAction.ACTION6, data={"x": px, "y": py})
    print(f"After L1: lc={obs.levels_completed}")

    # L2-L4: use the solver
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
            print(f"After L{level}: lc={obs.levels_completed}")
        else:
            print(f"STUCK at L{level}")
            return False
    return True


def dump_l5_info():
    """Dump all sprite info for L5."""
    g = env._game

    print("\n=== L5 Bodies (brdck) ===")
    for name, data in g.brdck.items():
        kignw = data.get("kignw")
        mdpcc = data.get("mdpcc", [])
        hand = g.dfugm.get(name, {}).get("xwdrv") if name in g.dfugm else None
        print(f"\n  Body: {name}")
        if kignw:
            print(f"    kignw: name={kignw.name} pos=({kignw.x},{kignw.y}) "
                  f"size={kignw.width}x{kignw.height}")
            px = kignw.pixels
            colors = {int(c) for c in np.unique(px) if c >= 0}
            nonzero = {int(c) for c in np.unique(px) if c > 0}
            nontrans = np.sum(px != -1)
            print(f"    pixels shape={px.shape} colors={colors} nonzero={nonzero} "
                  f"non-transparent={nontrans}/{px.size}")
        else:
            print(f"    kignw: None")
        if hand:
            print(f"    hand: name={hand.name} pos=({hand.x},{hand.y}) "
                  f"size={hand.width}x{hand.height}")
            hpx = hand.pixels
            hcolors = {int(c) for c in np.unique(hpx) if c > 0}
            print(f"    hand colors={hcolors}")
        print(f"    feet ({len(mdpcc)}):")
        for i, f in enumerate(mdpcc):
            print(f"      foot {i}: pos=({f.x},{f.y}) size={f.width}x{f.height}")

    print("\n=== L5 fwqwj (absorption bodies) ===")
    for name, absorbed in g.fwqwj.items():
        print(f"  {name}: absorbed={absorbed}")

    print("\n=== L5 nxahg (obstacles) ===")
    for obs in g.nxahg:
        px = obs.pixels
        colors = {int(c) for c in np.unique(px) if c > 0}
        nontrans = np.sum(px != -1)
        print(f"  {obs.name}: pos=({obs.x},{obs.y}) size={obs.width}x{obs.height} "
              f"colors={colors} non-transparent={nontrans}/{px.size}")

    print("\n=== L5 Feet (ftmaz) ===")
    for i, f in enumerate(g.ftmaz):
        print(f"  foot[{i}]: name={f.name} pos=({f.x},{f.y}) size={f.width}x{f.height}")

    print("\n=== Foot-to-body mapping ===")
    for i, f in enumerate(g.ftmaz):
        body = g.mfrvmbaujm(f)
        print(f"  foot[{i}] -> body={body}")


def test_absorption(snap, body_kignw_name, obstacle_name, desc=""):
    """Test if a body can absorb an obstacle at various positions."""
    g = snap
    # Find the body sprite
    body_sprites = g.current_level.get_sprites_by_name(body_kignw_name)
    if not body_sprites:
        print(f"  Body sprite {body_kignw_name} not found!")
        return
    body = body_sprites[0]

    # Find the obstacle
    obs = None
    for o in g.nxahg:
        if o.name == obstacle_name:
            obs = o
            break
    if not obs:
        print(f"  Obstacle {obstacle_name} not found!")
        return

    print(f"\n=== Testing: {desc} ===")
    print(f"  Body: {body.name} at ({body.x},{body.y}) size={body.width}x{body.height}")
    print(f"  Obstacle: {obs.name} at ({obs.x},{obs.y}) size={obs.width}x{obs.height}")

    # Check if they can collide at various offsets
    collisions = []
    for dx in range(-body.width - obs.width, body.width + obs.width + 1):
        for dy in range(-body.height - obs.height, body.height + obs.height + 1):
            bx = obs.x + dx
            by = obs.y + dy
            body.set_position(bx, by)
            if body.collides_with(obs):
                collisions.append((bx, by))

    print(f"  Collision positions: {len(collisions)}")
    if collisions:
        print(f"  Sample positions: {collisions[:10]}")
    else:
        print(f"  *** NO POSSIBLE COLLISION - pixel shapes don't overlap ***")
        # Show the pixel patterns
        print(f"  Body pixels (non-transparent):")
        bpx = body.pixels
        for y in range(bpx.shape[0]):
            row = ""
            for x in range(bpx.shape[1]):
                v = bpx[y, x]
                if v == -1:
                    row += "."
                elif v == 0:
                    row += "0"
                else:
                    row += hex(int(v))[2:]
            print(f"    {row}")
        print(f"  Obstacle pixels (non-transparent):")
        opx = obs.pixels
        for y in range(opx.shape[0]):
            row = ""
            for x in range(opx.shape[1]):
                v = opx[y, x]
                if v == -1:
                    row += "."
                elif v == 0:
                    row += "0"
                else:
                    row += hex(int(v))[2:]
            print(f"    {row}")


def try_absorption_order(snap, order_desc, foot_clicks):
    """Try a specific sequence of foot movements and check absorption."""
    g = copy.deepcopy(snap)
    env._game = g

    print(f"\n=== Trying: {order_desc} ===")
    for i, (fx, fy, tx, ty) in enumerate(foot_clicks):
        # Select foot
        obs_result = env.step(GameAction.ACTION6, data={"x": fx, "y": fy})
        # Move foot
        obs_result = env.step(GameAction.ACTION6, data={"x": tx, "y": ty})

        # Check what was absorbed
        for name, absorbed in g.fwqwj.items():
            if absorbed:
                print(f"  After click {i+1}: {name} absorbed {absorbed}")

        # Check body pixels
        for name in g.fwqwj:
            sprites = g.current_level.get_sprites_by_name(name)
            if sprites:
                px = sprites[0].pixels
                colors = {int(c) for c in np.unique(px) if c > 0}
                if colors:
                    print(f"  {name} now has colors: {colors}")

    print(f"  State: {obs_result.state.name}, lc={obs_result.levels_completed}")
    return g


if __name__ == "__main__":
    if not replay_to_l5():
        print("Failed to reach L5")
        exit(1)

    print("\n" + "="*60)
    print("=== L5 INITIAL STATE ===")
    print("="*60)

    dump_l5_info()

    # Save L5 initial state
    l5_snap = copy.deepcopy(env._game)

    # Test collisions before any absorption
    g = env._game
    for bname, absorbed in g.fwqwj.items():
        for obs in g.nxahg:
            test_absorption(copy.deepcopy(g), bname, obs.name,
                          f"{bname} vs {obs.name} (fresh)")
