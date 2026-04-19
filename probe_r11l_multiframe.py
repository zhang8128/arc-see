"""R11L: diff the 3 frames in obs.frame after a click. Look for transient
state only visible in mid-animation frames.

Also: click many times (up to 20) and see if state EVER changes to WIN or GAME_OVER.
"""
import numpy as np
import arc_agi
from arcengine import GameAction


def allf(obs):
    return [np.array(f, dtype=np.int64) for f in obs.frame]


def dump_grid(g, tag):
    print(f"--- {tag} ---")
    chars = "0123456789abcdef"
    h, w = g.shape
    for y in range(h):
        row = []
        for x in range(w):
            v = int(g[y, x])
            row.append("." if v < 0 else (chars[v] if 0 <= v < 16 else "?"))
        print("".join(row))
    print()


def diff_cells(a, b):
    ys, xs = np.where(a != b)
    return [(int(y), int(x), int(a[y, x]), int(b[y, x])) for y, x in zip(ys, xs)]


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    # Reset baseline
    obs = env.reset()
    initial = allf(obs)[-1]
    print(f"reset frame count: {len(obs.frame)}")

    # Click and get all frames
    obs2 = env.step(GameAction.ACTION6, data={"x": 40, "y": 40})
    frames = allf(obs2)
    print(f"click frame count: {len(frames)}\n")

    # Diff frame[i] vs frame[i+1]
    for i in range(len(frames) - 1):
        d = diff_cells(frames[i], frames[i + 1])
        print(f"frame[{i}] vs frame[{i+1}]: {len(d)} cells differ")
        if 0 < len(d) < 40:
            for y, x, o, n in d[:40]:
                print(f"  ({x:2d},{y:2d}) {o}->{n}")

    # Diff initial (reset) vs frame[i]
    for i in range(len(frames)):
        n = len(diff_cells(initial, frames[i]))
        print(f"initial vs frame[{i}]: {n} cells differ")

    # Dump frame[0] to see what it looks like
    if len(frames) >= 1:
        dump_grid(frames[0], "frame[0] after click(40, 40)")

    # Does frame[0] contain anything that frame[-1] doesn't? If so, transient
    # overlay (e.g. goal marker animated away).
    if len(frames) >= 2:
        f_first, f_last = frames[0], frames[-1]
        only_first = set()
        only_last = set()
        h, w = f_first.shape
        for y in range(h):
            for x in range(w):
                v0 = int(f_first[y, x])
                vL = int(f_last[y, x])
                if v0 != vL:
                    only_first.add((y, x, v0))
                    only_last.add((y, x, vL))
        print(f"\ncells differing between frame[0] and frame[-1]: {len(only_first)}")
        unique_vals_first = sorted(set(v for _, _, v in only_first))
        unique_vals_last = sorted(set(v for _, _, v in only_last))
        print(f"  values only in frame[0]: {unique_vals_first}")
        print(f"  values only in frame[-1]: {unique_vals_last}")

    # Click many times, checking for state changes
    print("\n-- 20 clicks at varying positions --")
    env.reset()
    states_seen = set()
    counters_seen = set()
    for i in range(20):
        # Sweep clicks around
        cx = 15 + (i * 3) % 40
        cy = 20 + (i * 5) % 35
        obs2 = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        g = allf(obs2)[-1]
        states_seen.add(obs2.state.name)
        # Count col-0 markers
        h_rows = g.shape[0]
        counter = sum(1 for r in range(h_rows) if int(g[r, 0]) == 5)
        counters_seen.add(counter)
        if i < 10 or i > 15:
            print(f"  click{i:2d} ({cx},{cy}): state={obs2.state.name}  counter_marks={counter}")
    print(f"  all states seen: {states_seen}")
    print(f"  all counter values seen: {sorted(counters_seen)}")


if __name__ == "__main__":
    main()
