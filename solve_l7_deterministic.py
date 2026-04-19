"""LF52 L7 deterministic solver — uses exact sequences from verified run."""
import sys, copy, random
import numpy as np
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
from lf52_tool import LF52
from arcengine import GameAction

g = LF52(up_to_level=7, verbose=False)
env = g.env

def get_foz():
    return [(s.x, s.y, s.name) for z, s, e in env._game.ikhhdzfmarl._sorted_cache
            if 'fozwvlovdui' in s.name and s.visible]
def get_vp():
    return tuple(env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
def do_a(a):
    return env.step(getattr(GameAction, f'ACTION{a}'))

def select_and_chain(wx, wy, direction=None):
    vp = get_vp()
    sx, sy = wx + vp[0] + 3, wy + vp[1] + 3
    if not (0 <= sx < 64 and 0 <= sy < 64): return False
    obs = env.step(GameAction.ACTION6, data={'x': sx, 'y': sy})
    frame = np.array(obs.frame[-1], dtype=np.int16)
    if int((frame == 3).sum()) == 0: return False
    hints = [(int(x), int(y)) for y, x in zip(*np.where(frame == 2))]
    if not hints: return False
    if direction == 'right': hints = [h for h in hints if h[0] > sx]
    elif direction == 'down': hints = [h for h in hints if h[1] > sy]
    elif direction == 'left': hints = [h for h in hints if h[0] < sx]
    elif direction == 'up': hints = [h for h in hints if h[1] < sy]
    if not hints: return False
    hx, hy = int(np.mean([h[0] for h in hints])), int(np.mean([h[1] for h in hints]))
    env.step(GameAction.ACTION6, data={'x': hx, 'y': hy})
    return True

def search_and_chain(wx, wy, direction, max_trials=1000):
    """Systematically try all A-sequences of length 0-8 to enable chain."""
    from itertools import product
    snap = copy.deepcopy(env._game)
    # Try length 0 first (no A-actions needed)
    env._game = copy.deepcopy(snap)
    snap_t = copy.deepcopy(env._game)
    if select_and_chain(wx, wy, direction):
        return True
    env._game = copy.deepcopy(snap_t)
    # Systematic for short (1-5), then random for longer
    for length in range(1, 6):
        for seq in product([1,2,3,4], repeat=length):
            env._game = copy.deepcopy(snap)
            for a in seq: do_a(a)
            snap_t = copy.deepcopy(env._game)
            if select_and_chain(wx, wy, direction):
                print(f"    Found: A-seq={list(seq)}", flush=True)
                return True
            env._game = copy.deepcopy(snap_t)
    # Random for longer sequences
    for trial in range(max_trials):
        env._game = copy.deepcopy(snap)
        seq = [random.choice([1,2,3,4]) for _ in range(random.randint(5, 20))]
        for a in seq: do_a(a)
        snap_t = copy.deepcopy(env._game)
        if select_and_chain(wx, wy, direction):
            print(f"    Found: random trial {trial} seq={seq[:12]}", flush=True)
            return True
        env._game = copy.deepcopy(snap_t)
    return False

# Monkey-patch for logging
scene = env._game.ikhhdzfmarl
orig = scene.cfilhtifcb.__func__
def patched(self, p):
    u = self.wpwvsglgmb.qoifrofmiu
    if u:
        r = u.chahdtpdoz; c = p.cdpcbbnfdp
        f = (r[0]+c[0]//6, r[1]+c[1]//6)
        print(f'  CHAIN: {r}→{f} vp={tuple(self.hncnfaqaddg.cdpcbbnfdp)}', flush=True)
    orig(self, p)
scene.cfilhtifcb = patched.__get__(scene)

# === PHASE 1: Red to row 8 ===
print("Phase 1: Red to row 8", flush=True)
for a in [3,1,2,3,4,3,1,1,1,4,2,4,4]: do_a(a)
assert select_and_chain(36, 6), "Red chain 1 failed"
for a in [1,1,3,1,3,2,3,2,4,2,2,4,4,4,2,1,2]: do_a(a)
assert select_and_chain(36, 36, 'down'), "Red chain 2 failed"
red = [(s.x, s.y) for z, s, e in env._game.ikhhdzfmarl._sorted_cache if 'red' in s.name and s.visible]
print(f"  Red at {red}", flush=True)

# === PHASE 2: Regular to row 8 ===
print("\nPhase 2: Regular to row 8", flush=True)
random.seed(42)  # Fresh seed for this phase
assert search_and_chain(0, 6, None, 5000), "Reg unlock failed"
reg = [(s.x,s.y) for z,s,e in env._game.ikhhdzfmarl._sorted_cache if s.name=='fozwvlovdui' and s.visible and s.x<100]
print(f"  Reg chain 1: {reg}", flush=True)

# Drive to (6,36) and cascade
snap = copy.deepcopy(env._game)
for trial in range(5000):
    env._game = copy.deepcopy(snap)
    seq = [random.choice([1,2,3,4]) for _ in range(random.randint(1,20))]
    for a in seq: do_a(a)
    r = [(s.x,s.y) for z,s,e in env._game.ikhhdzfmarl._sorted_cache if s.name=='fozwvlovdui' and s.visible and s.x<100]
    if r and r[0]==(6,36): break

assert select_and_chain(6, 36, 'down'), "Reg chain 2 failed"
assert search_and_chain(6, 48, 'right', 3000), "Reg chain 3 failed"
assert search_and_chain(18, 48, 'right', 3000), "Reg chain 4 failed"
foz = get_foz()
print(f"  Cascade done: {[(f[0],f[1]) for f in foz]}", flush=True)

# === PHASE 3: Leapfrog ===
print("\nPhase 3: Leapfrog", flush=True)

# Explicit leapfrog: reg through red, then red through reg
# Current: reg at (30,48), red at (36,48)
foz = get_foz()
print(f"Leapfrog start: {[(f[0],f[1],f[2][:10]) for f in foz]}", flush=True)

# Step 1: Reg at (30,48) chains RIGHT through red at (36,48) → reg at (42,48)
print("Step 1: reg RIGHT through red...", flush=True)
ok1 = search_and_chain(30, 48, 'right', 3000)
foz = get_foz()
print(f"  Result: ok={ok1} foz={[(f[0],f[1]) for f in foz]} vp={get_vp()}", flush=True)

if ok1:
    # Step 2: Red at (36,48) chains RIGHT through reg at (42,48) → red at (48,48) SCROLL!
    print("Step 2: red RIGHT through reg...", flush=True)
    ok2 = search_and_chain(36, 48, 'right', 3000)
    foz = get_foz()
    vp = get_vp()
    print(f"  Result: ok={ok2} foz={[(f[0],f[1]) for f in foz]} vp={vp}", flush=True)
    if vp != (5, 5):
        print(f"  *** FIRST SCROLL! vp={vp} ***", flush=True)

    # Continue alternating
    for step in range(3, 30):
        foz = get_foz()
        vp = get_vp()
        lc = env._game._current_level_index
        reg_pos = [(f[0],f[1]) for f in foz if f[2]=='fozwvlovdui' and f[0]<200]
        red_pos = [(f[0],f[1]) for f in foz if 'red' in f[2]]
        if not reg_pos or not red_pos: break

        if step % 2 == 1:  # odd: reg through red
            ok = search_and_chain(reg_pos[0][0], reg_pos[0][1], 'right', 3000)
            who = "reg"
        else:  # even: red through reg
            ok = search_and_chain(red_pos[0][0], red_pos[0][1], 'right', 3000)
            who = "red"

        foz = get_foz()
        vp_new = get_vp()
        lc = env._game._current_level_index
        print(f"  Step {step}: {who} ok={ok} foz={[(f[0],f[1]) for f in foz]} vp={vp_new} lc={lc}", flush=True)
        if not ok: break
        if vp_new != vp: print(f"  *** SCROLL! ***", flush=True)
        if len(foz) < 3: print(f"  *** FOZ REDUCED! ***", flush=True)
        if lc > 6: print(f"  *** L7 SOLVED! ***", flush=True); break

print(f"\nFinal: vp={get_vp()} foz={[(f[0],f[1],f[2][:10]) for f in get_foz()]}", flush=True)
print(f"State: {env._game._state}", flush=True)
