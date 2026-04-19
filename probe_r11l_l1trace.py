"""Trace L1 win mechanism to understand what triggers level completion."""
import copy
import arc_agi
from arcengine import GameAction

arcade = arc_agi.Arcade()
env = arcade.make("r11l-aa269680", render_mode=None)
env.reset()
env.reset()

g = env._game
print("=== L1 initial state ===")
print(f"  level_index={g.level_index}")
print(f"  bodies: {list(g.dfugm.keys())}")
for body in g.dfugm:
    d = g.dfugm[body]
    hand = d["xwdrv"]
    mi = d["miwyy"]
    wu = d["wugiv"]
    qn = d["qnpnk"]
    rf = d["rftjv"]
    me = d["meydp"]
    print(f"  {body}: hand=({hand.x},{hand.y}) miwyy={mi} wugiv={wu} qnpnk={qn} rftjv={rf} meydp={me}")
print(f"  feet: {[(f.x, f.y) for f in g.ftmaz]}")
print(f"  win_score={g.win_score}")

for i, (cx, cy) in enumerate([(36, 13), (26, 61), (42, 30)]):
    obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
    print(f"\n=== After L1 click {i+1} ({cx},{cy}) ===")
    print(f"  lc={obs.levels_completed} state={obs.state.name} winning={g.winning}")
    for body in g.dfugm:
        d = g.dfugm[body]
        hand = d["xwdrv"]
        mi = d["miwyy"]
        wu = d["wugiv"]
        qn = d["qnpnk"]
        rf = d["rftjv"]
        me = d["meydp"]
        print(f"  {body}: hand=({hand.x},{hand.y}) miwyy={mi} wugiv={wu} qnpnk={qn} rftjv={rf} meydp={me}")
    print(f"  feet: {[(f.x, f.y) for f in g.ftmaz]}")
    print(f"  level_index={g.level_index}")
    print(f"  zxankdpxcx={g.zxankdpxcx}")

# Now check L2 initial
print("\n=== L2 initial (after L1 win) ===")
print(f"  bodies: {list(g.dfugm.keys())}")
for body in g.dfugm:
    d = g.dfugm[body]
    hand = d["xwdrv"]
    mi = d["miwyy"]
    wu = d["wugiv"]
    qn = d["qnpnk"]
    rf = d["rftjv"]
    me = d["meydp"]
    print(f"  {body}: hand=({hand.x},{hand.y}) miwyy={mi} wugiv={wu} qnpnk={qn} rftjv={rf} meydp={me}")
