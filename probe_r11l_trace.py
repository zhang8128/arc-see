"""Trace L2 game state step-by-step through click sequences."""
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


def play_trace(seq):
    env._game = copy.deepcopy(snap)
    for i, (cx, cy) in enumerate(seq):
        obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        g = env._game
        print(f"\n  Click {i+1} ({cx},{cy}): lc={obs.levels_completed} winning={g.winning}")
        for body in ["kpaac", "qniqj"]:
            d = g.dfugm[body]
            hand = d["xwdrv"]
            mi = d["miwyy"]
            wu = d["wugiv"]
            qn = d["qnpnk"]
            rf = d["rftjv"]
            print(f"    {body}: hand=({hand.x},{hand.y}) miwyy={mi} wugiv={wu} qnpnk={qn} rftjv={rf}")
        feet = [(f.x, f.y) for f in g.ftmaz]
        print(f"    feet={feet}")


sequences = [
    [(49, 9), (56, 18), (45, 35), (20, 48)],
    [(54, 15), (45, 35), (37, 48)],
    [(37, 48), (45, 35), (54, 15)],
    [(37, 48), (8, 21), (54, 15)],
    [(10, 10), (45, 35), (26, 54)],
    [(49, 9), (54, 15)],
    [(8, 21), (37, 48)],
]

for seq in sequences:
    label = " -> ".join(f"({cx},{cy})" for cx, cy in seq)
    print(f"\n=== {label} ===")
    play_trace(seq)
