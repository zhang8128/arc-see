"""R11L L2 search engine — correct double-reset, reusable, configurable.

Usage:
    python probe_r11l_engine.py [strategy] [options]

Strategies:
    3click-grid N       3-click (A, hip, B) at N-px grid, all 4 hips
    2click-grid N       2-click at N-px grid
    4click-grid N       4-click (A, hip1, hip2, B) at N-px grid
    arm1-map N          Map all arm1 foot positions at N-px
    arm2-reject N HIP   Map arm2 B rejection for given hip at N-px
                        HIP format: "45,35" or "54,48"
    targeted FILE       Read click sequences from FILE, test each

All strategies use double-reset for correctness.
"""
import arc_agi
import sys
import time
import json
import numpy as np
from arcengine import GameAction
from collections import Counter, deque
from itertools import product

L1 = [(36, 13), (26, 61), (42, 30)]
ALL_HIPS = [(49, 9), (8, 21), (45, 35), (54, 48)]
ARM1_HIPS = [(49, 9), (8, 21)]
ARM2_HIPS = [(45, 35), (54, 48)]


class R11LEngine:
    """Correct R11L L2 search engine with double-reset."""

    def __init__(self):
        import copy
        self.arcade = arc_agi.Arcade()
        self.env = self.arcade.make("r11l-aa269680", render_mode=None)
        # Create verified-correct L2 snapshot via double-reset
        self.env.reset()
        self.env.reset()
        for px, py in L1:
            self.env.step(GameAction.ACTION6, data={"x": px, "y": py})
        self._snap = copy.deepcopy(self.env._game)
        self.trials = 0
        self.wins = []
        self.t0 = time.time()

    def play(self, l2_clicks):
        """Play L2 clicks from verified snapshot. Fast (no L1 replay)."""
        import copy
        self.env._game = copy.deepcopy(self._snap)
        obs = None
        for cx, cy in l2_clicks:
            obs = self.env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        self.trials += 1
        return obs

    def check_win(self, obs, seq_desc=""):
        if obs.levels_completed >= 2:
            self.wins.append(seq_desc)
            print(f"  WIN! {seq_desc}", flush=True)
            return True
        return False

    def sixes(self, obs):
        g = np.array(obs.frame[-1], dtype=np.int64)
        return sorted([(int(x), int(y)) for y, x in np.argwhere(g == 6)])

    def progress(self, total=None, every=5000):
        if self.trials % every == 0:
            elapsed = time.time() - self.t0
            rate = self.trials / elapsed if elapsed > 0 else 0
            if total:
                eta = (total - self.trials) / rate if rate > 0 else 0
                print(f"  [{self.trials}/{total}] {elapsed:.0f}s, "
                      f"~{eta:.0f}s remaining, {len(self.wins)} wins",
                      flush=True)
            else:
                print(f"  [{self.trials}] {elapsed:.0f}s, "
                      f"{len(self.wins)} wins", flush=True)

    def summary(self):
        elapsed = time.time() - self.t0
        print(f"\n=== DONE: {len(self.wins)} wins in {self.trials} trials "
              f"({elapsed:.0f}s) ===", flush=True)
        for w in self.wins[:20]:
            print(f"  {w}", flush=True)


def make_grid(n):
    """Return list of coordinates at n-pixel spacing."""
    return list(range(0, 64, n))


def parse_hip(s):
    """Parse hip from string like '45,35'."""
    parts = s.split(",")
    return (int(parts[0]), int(parts[1]))


def search_3click(eng, px):
    """3-click (A, hip, B) at given pixel grid."""
    g = make_grid(px)
    total = 4 * len(g)**2 * len(g)**2
    print(f"3-click search: 4 hips × {len(g)}² A × {len(g)}² B = "
          f"{total} trials at {px}px", flush=True)

    for hip in ALL_HIPS:
        for ax, ay in product(g, repeat=2):
            for bx, by in product(g, repeat=2):
                obs = eng.play([(ax, ay), hip, (bx, by)])
                eng.check_win(obs, f"({ax},{ay})->{hip}->({bx},{by})")
                eng.progress(total)
                if len(eng.wins) >= 10:
                    return
        print(f"  hip {hip}: {eng.trials} done, {len(eng.wins)} wins "
              f"({time.time()-eng.t0:.0f}s)", flush=True)


def search_2click(eng, px):
    """2-click search at given pixel grid."""
    g = make_grid(px)
    total = len(g)**4
    print(f"2-click search: {len(g)}⁴ = {total} trials at {px}px",
          flush=True)

    for x1, y1 in product(g, repeat=2):
        for x2, y2 in product(g, repeat=2):
            obs = eng.play([(x1, y1), (x2, y2)])
            eng.check_win(obs, f"({x1},{y1})->({x2},{y2})")
            eng.progress(total)
            if len(eng.wins) >= 10:
                return


def search_4click(eng, px):
    """4-click (A, hip1, hip2, B) visiting both arm hip pairs."""
    g = make_grid(px)
    hip_combos = [(h1, h2) for h1 in ARM1_HIPS for h2 in ARM2_HIPS]
    total = len(hip_combos) * 2 * len(g)**4
    print(f"4-click search: {len(hip_combos)} hip combos × 2 orders "
          f"× {len(g)}⁴ = {total} at {px}px", flush=True)

    for h1, h2 in hip_combos:
        for ax, ay in product(g, repeat=2):
            for bx, by in product(g, repeat=2):
                obs = eng.play([(ax, ay), h1, h2, (bx, by)])
                eng.check_win(obs, f"({ax},{ay})->{h1}->{h2}->({bx},{by})")
                eng.progress(total)
                if len(eng.wins) >= 10:
                    return
        for ax, ay in product(g, repeat=2):
            for bx, by in product(g, repeat=2):
                obs = eng.play([(ax, ay), h2, h1, (bx, by)])
                eng.check_win(obs, f"({ax},{ay})->{h2}->{h1}->({bx},{by})")
                eng.progress(total)
                if len(eng.wins) >= 10:
                    return
        print(f"  {h1}+{h2}: {eng.trials} done ({time.time()-eng.t0:.0f}s)",
              flush=True)


def map_arm1(eng, px):
    """Map all arm1 foot positions."""
    g = make_grid(px)
    positions = Counter()
    click_map = {}
    for x, y in product(g, repeat=2):
        obs = eng.play([(x, y)])
        s = eng.sixes(obs)
        pos = s[0]  # arm1 is first when arm2 at initial (49,41)
        positions[pos] += 1
        if pos not in click_map:
            click_map[pos] = (x, y)

    print(f"\n{len(positions)} distinct arm1 positions at {px}px:",
          flush=True)
    for pos, cnt in positions.most_common():
        print(f"  {pos}: {cnt}x (click {click_map[pos]})", flush=True)

    out = {"px": px, "positions": {str(k): v for k, v in click_map.items()}}
    with open(f"/tmp/r11l_arm1_map_{px}px.json", "w") as f:
        json.dump(out, f)
    print(f"Saved to /tmp/r11l_arm1_map_{px}px.json", flush=True)


def map_arm2_reject(eng, px, hip):
    """Map arm2 B acceptance/rejection for given hip."""
    hip = tuple(hip)
    g = make_grid(px)
    accepted = []
    rejected = []
    for bx, by in product(g, repeat=2):
        obs = eng.play([(10, 10), hip, (bx, by)])
        s = eng.sixes(obs)
        if (49, 41) in s:
            rejected.append((bx, by))
        else:
            foot = s[1] if s[0] == (22, 13) else s[0]
            accepted.append((bx, by, foot[0], foot[1]))

    print(f"\nArm2 B map (hip={hip}, {px}px): "
          f"{len(accepted)} accepted, {len(rejected)} rejected", flush=True)

    lookup = {}
    for bx, by, fx, fy in accepted:
        lookup[(bx, by)] = "."
    for bx, by in rejected:
        lookup[(bx, by)] = "#"

    print("Rejection map (. = accepted, # = rejected):", flush=True)
    for by in g:
        row = ""
        for bx in g:
            row += lookup.get((bx, by), " ")
        print(f"  y={by:2d}: {row}", flush=True)

    # Find isolated regions via BFS
    acc_set = {(bx, by) for bx, by, _, _ in accepted}
    if not acc_set:
        return

    start = max(acc_set, key=lambda p: p[0] + p[1])
    visited = set()
    queue = deque([start])
    visited.add(start)
    while queue:
        cx, cy = queue.popleft()
        for dx, dy in [(-px, 0), (px, 0), (0, -px), (0, px)]:
            nx, ny = cx + dx, cy + dy
            if (nx, ny) in acc_set and (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append((nx, ny))

    isolated = acc_set - visited
    if isolated:
        print(f"\nISOLATED accepted cells ({len(isolated)}):", flush=True)
        for bx, by in sorted(isolated):
            foot = [(fx, fy) for bx2, by2, fx, fy in accepted
                    if bx2 == bx and by2 == by][0]
            print(f"  B=({bx},{by}) → arm2 foot at {foot}", flush=True)
    else:
        print("\nNo isolated regions found.", flush=True)


def search_targeted(eng, filepath):
    """Test click sequences from a JSON file."""
    with open(filepath) as f:
        sequences = json.load(f)
    print(f"Testing {len(sequences)} sequences from {filepath}", flush=True)
    for seq in sequences:
        clicks = [tuple(c) for c in seq]
        obs = eng.play(clicks)
        eng.check_win(obs, str(clicks))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    eng = R11LEngine()
    strategy = sys.argv[1]

    if strategy == "3click-grid":
        px = int(sys.argv[2]) if len(sys.argv) > 2 else 4
        search_3click(eng, px)
    elif strategy == "2click-grid":
        px = int(sys.argv[2]) if len(sys.argv) > 2 else 4
        search_2click(eng, px)
    elif strategy == "4click-grid":
        px = int(sys.argv[2]) if len(sys.argv) > 2 else 8
        search_4click(eng, px)
    elif strategy == "arm1-map":
        px = int(sys.argv[2]) if len(sys.argv) > 2 else 2
        map_arm1(eng, px)
    elif strategy == "arm2-reject":
        px = int(sys.argv[2]) if len(sys.argv) > 2 else 2
        hip_str = sys.argv[3] if len(sys.argv) > 3 else "45,35"
        hip = parse_hip(hip_str)
        map_arm2_reject(eng, px, hip)
    elif strategy == "targeted":
        search_targeted(eng, sys.argv[2])
    else:
        print(f"Unknown strategy: {strategy}")
        print(__doc__)
        return

    eng.summary()


if __name__ == "__main__":
    main()
