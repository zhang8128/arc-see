"""R11L: reproduce the winning path and minimize it.

Known winning sequence (from probe_r11l_random rollout 169):
  (36, 14), (13, 63), (25, 25), (33, 25), (45, 52), (37, 20), (5, 63), (26, 61), (42, 30)

Tasks:
  1. Verify the path wins.
  2. Per-click trace: print (head, foot, counter, levels_completed) after each.
  3. Delta-minimization: try removing each click and see if the shorter path
     still wins. Repeat until minimal.
"""
import numpy as np
import arc_agi
from arcengine import GameAction


def frame(obs):
    return np.array(obs.frame[-1], dtype=np.int64)


def foot_pos(grid):
    sixes = np.argwhere(grid == 6)
    if len(sixes) != 1:
        return None
    y, x = sixes[0]
    return (int(x), int(y))


def head_pos(grid):
    ys, xs = np.where(grid == 15)
    for y, x in zip(ys, xs):
        if y < 1 or y > 62 or x < 1 or x > 62:
            continue
        nb = [int(grid[y - 1, x]), int(grid[y + 1, x]),
              int(grid[y, x - 1]), int(grid[y, x + 1])]
        if nb.count(0) >= 3:
            return (int(x), int(y))
    return None


def col0_marks(g):
    return sum(1 for r in range(g.shape[0]) if int(g[r, 0]) == 5)


def play(env, path):
    env.reset()
    last = None
    trace = []
    for cx, cy in path:
        last = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        g = frame(last)
        trace.append({
            "click": (cx, cy),
            "head": head_pos(g),
            "foot": foot_pos(g),
            "counter": col0_marks(g),
            "state": last.state.name,
            "levels_completed": last.levels_completed,
        })
    return last, trace


def wins(env, path):
    last, _ = play(env, path)
    return last.levels_completed > 0 or last.state.name == "WIN"


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    WINNING = [
        (36, 14), (13, 63), (25, 25), (33, 25),
        (45, 52), (37, 20), (5, 63), (26, 61), (42, 30),
    ]
    print(f"verifying full path ({len(WINNING)} clicks)...")
    last, trace = play(env, WINNING)
    for i, t in enumerate(trace):
        print(f"  click {i}: {t}")
    print(f"final: state={last.state.name}  levels_completed={last.levels_completed}")
    if last.levels_completed == 0 and last.state.name != "WIN":
        print("ERROR: path does not win!")
        return

    # Minimize: try removing each click one at a time
    path = list(WINNING)
    while True:
        removed = False
        for i in range(len(path)):
            trial = path[:i] + path[i + 1:]
            if wins(env, trial):
                path = trial
                print(f"  removed click index {i}, now {len(path)} clicks")
                removed = True
                break
        if not removed:
            break
    print(f"\nminimized path ({len(path)} clicks): {path}")
    last, trace = play(env, path)
    print(f"final: levels_completed={last.levels_completed}  state={last.state.name}")
    for i, t in enumerate(trace):
        print(f"  click {i}: head={t['head']} foot={t['foot']} lc={t['levels_completed']}")


if __name__ == "__main__":
    main()
