"""LF52 L7 solver — red-to-row8 leapfrog strategy.

Phase 1: Red piece → row 8 (tile 6,8) as stepping-stone pivot
Phase 2: Regular piece → row 8 (tile 5,8) via cascade
Phase 3: Leapfrog both pieces rightward past DGX gap
Phase 4: Viewport scrolls → reach piece at (132,36) → consume → win
"""
import sys, copy
import numpy as np
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
from lf52_tool import LF52
from arcengine import GameAction


def get_foz(game):
    return [(s.x, s.y, s.name) for z, s, e in game.ikhhdzfmarl._sorted_cache
            if 'fozwvlovdui' in s.name and s.visible]

def get_vp(game):
    return tuple(game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)

def do_a(env, a):
    return env.step(getattr(GameAction, f'ACTION{a}'))

def select_and_chain(env, wx, wy, direction=None):
    """Select piece at world (wx,wy) and chain via hint. Returns True if chain executed."""
    vp = get_vp(env._game)
    sx, sy = wx + vp[0] + 3, wy + vp[1] + 3
    if not (0 <= sx < 64 and 0 <= sy < 64):
        return False
    obs = env.step(GameAction.ACTION6, data={'x': sx, 'y': sy})
    frame = np.array(obs.frame[-1], dtype=np.int16)
    if int((frame == 3).sum()) == 0:
        return False
    hints = [(int(x), int(y)) for y, x in zip(*np.where(frame == 2))]
    if not hints:
        return False
    if direction == 'right':
        hints = [h for h in hints if h[0] > sx]
    elif direction == 'down':
        hints = [h for h in hints if h[1] > sy]
    elif direction == 'up':
        hints = [h for h in hints if h[1] < sy]
    elif direction == 'left':
        hints = [h for h in hints if h[0] < sx]
    if not hints:
        return False
    hx = int(np.mean([h[0] for h in hints]))
    hy = int(np.mean([h[1] for h in hints]))
    env.step(GameAction.ACTION6, data={'x': hx, 'y': hy})
    return True


def main():
    print("=" * 60)
    print("LF52 L7 FINAL SOLVER")
    print("=" * 60)

    g = LF52(up_to_level=7, verbose=False)
    env = g.env

    # Monkey-patch to log fldpqdkmge
    scene = env._game.ikhhdzfmarl
    original = scene.cfilhtifcb.__func__
    def patched(self, lgbyiaitpdi):
        u = self.wpwvsglgmb.qoifrofmiu
        if u:
            r = u.chahdtpdoz
            c = lgbyiaitpdi.cdpcbbnfdp
            f = (r[0] + c[0] // 6, r[1] + c[1] // 6)
            vp = tuple(self.hncnfaqaddg.cdpcbbnfdp)
            print(f'  CHAIN: src_tile={r} dest_tile={f} vp={vp}', flush=True)
        original(self, lgbyiaitpdi)
    scene.cfilhtifcb = patched.__get__(scene)

    # === PHASE 1: Red to row 8 ===
    print("\n--- Phase 1: Red to row 8 ---", flush=True)

    # Red unlock
    for a in [3, 1, 2, 3, 4, 3, 1, 1, 1, 4, 2, 4, 4]:
        do_a(env, a)

    # Red chain 1: (36,6) → (36,18)
    ok = select_and_chain(env, 36, 6)
    foz = get_foz(env._game)
    red = [(f[0], f[1]) for f in foz if 'red' in f[2]]
    print(f"Red chain 1: {red} ok={ok}", flush=True)

    # Drive red to (36, 36)
    for a in [1, 1, 3, 1, 3, 2, 3, 2, 4, 2, 2, 4, 4, 4, 2, 1, 2]:
        do_a(env, a)
    red = [(s.x, s.y) for z, s, e in env._game.ikhhdzfmarl._sorted_cache if 'red' in s.name and s.visible]
    print(f"Red driven to: {red}", flush=True)

    # Red chain 2: (36,36) → (36,48)
    ok = select_and_chain(env, 36, 36, 'down')
    red = [(s.x, s.y) for z, s, e in env._game.ikhhdzfmarl._sorted_cache if 'red' in s.name and s.visible]
    print(f"Red chain 2: {red} ok={ok}", flush=True)

    # === PHASE 2: Regular to row 8 ===
    print("\n--- Phase 2: Regular to row 8 ---", flush=True)

    # Search for reg unlock from post-red state
    import random
    random.seed(42)
    snap_reg = copy.deepcopy(env._game)
    reg_ok = False
    for trial in range(5000):
        env._game = copy.deepcopy(snap_reg)
        seq = [random.choice([1,2,3,4]) for _ in range(random.randint(1, 20))]
        for a in seq: do_a(env, a)
        snap_try = copy.deepcopy(env._game)
        if select_and_chain(env, 0, 6):
            print(f"Reg unlock found! trial={trial} seq={seq[:12]}", flush=True)
            foz = get_foz(env._game)
            reg = [(f[0], f[1]) for f in foz if f[2] == 'fozwvlovdui' and f[0] < 100]
            print(f"Reg chain 1: {reg}", flush=True)
            reg_ok = True
            break
        env._game = copy.deepcopy(snap_try)
        if trial % 1000 == 0 and trial > 0:
            print(f"  ... reg unlock trial {trial}", flush=True)
    if not reg_ok:
        print("FAILED to find reg unlock!", flush=True)
        return

    # Drive reg to (6, 36) = tile (1, 6), then cascade to row 8
    # Need to find drive sequence from THIS state
    import random
    random.seed(42)
    snap = copy.deepcopy(env._game)
    for trial in range(5000):
        env._game = copy.deepcopy(snap)
        seq = [random.choice([1,2,3,4]) for _ in range(random.randint(1, 20))]
        for a in seq: do_a(env, a)
        reg = [(s.x, s.y) for z, s, e in env._game.ikhhdzfmarl._sorted_cache
               if s.name == 'fozwvlovdui' and s.visible and s.x < 100]
        if reg and reg[0] == (6, 36):
            print(f"Drive reg to (6,36): {seq[:10]}", flush=True)
            break

    # Reg chain 2: (6,36) → (6,48) via DGX (6,42)
    ok = select_and_chain(env, 6, 36, 'down')
    reg = [(s.x, s.y) for z, s, e in env._game.ikhhdzfmarl._sorted_cache
           if s.name == 'fozwvlovdui' and s.visible and s.x < 100]
    print(f"Reg chain 2 (to row 8): {reg} ok={ok}", flush=True)

    # Reg chain 3: (6,48) → (18,48) RIGHT via DGX (12,48)
    # Need A-actions for selection
    snap2 = copy.deepcopy(env._game)
    for trial in range(1000):
        env._game = copy.deepcopy(snap2)
        seq = [random.choice([1,2,3,4]) for _ in range(random.randint(1, 10))]
        for a in seq: do_a(env, a)
        if select_and_chain(env, 6, 48, 'right'):
            reg = [(s.x, s.y) for z, s, e in env._game.ikhhdzfmarl._sorted_cache
                   if s.name == 'fozwvlovdui' and s.visible and s.x < 100]
            print(f"Reg chain 3 RIGHT: {reg} seq={seq[:6]}", flush=True)
            break

    # Reg chain 4: (18,48) → (30,48) RIGHT via DGX (24,48)
    snap3 = copy.deepcopy(env._game)
    for trial in range(1000):
        env._game = copy.deepcopy(snap3)
        seq = [random.choice([1,2,3,4]) for _ in range(random.randint(1, 10))]
        for a in seq: do_a(env, a)
        if select_and_chain(env, 18, 48, 'right'):
            reg = [(s.x, s.y) for z, s, e in env._game.ikhhdzfmarl._sorted_cache
                   if s.name == 'fozwvlovdui' and s.visible and s.x < 100]
            print(f"Reg chain 4 RIGHT: {reg} seq={seq[:6]}", flush=True)
            break

    # === PHASE 3: Leapfrog ===
    print("\n--- Phase 3: Leapfrog ---", flush=True)
    foz = get_foz(env._game)
    print(f"Before leapfrog: {[(f[0],f[1],f[2][:15]) for f in foz]}", flush=True)

    # Reg at (30,48)=tile(5,8), Red at (36,48)=tile(6,8)
    # Step 1: Reg RIGHT through Red → Reg at (42,48)=tile(7,8)
    snap4 = copy.deepcopy(env._game)
    for trial in range(500):
        env._game = copy.deepcopy(snap4)
        seq = [random.choice([1,2,3,4]) for _ in range(random.randint(1, 10))]
        for a in seq: do_a(env, a)
        if select_and_chain(env, 30, 48, 'right'):
            foz = get_foz(env._game)
            print(f"Leapfrog 1 (reg through red): {[(f[0],f[1]) for f in foz]} seq={seq[:6]}", flush=True)
            break

    # Step 2: Red RIGHT through Reg → Red at (48,48)=tile(8,8) → SCROLL!
    snap5 = copy.deepcopy(env._game)
    for trial in range(500):
        env._game = copy.deepcopy(snap5)
        seq = [random.choice([1,2,3,4]) for _ in range(random.randint(1, 10))]
        for a in seq: do_a(env, a)
        if select_and_chain(env, 36, 48, 'right'):
            foz = get_foz(env._game)
            vp = get_vp(env._game)
            print(f"Leapfrog 2 (red through reg): {[(f[0],f[1]) for f in foz]} vp={vp}", flush=True)
            if vp != (5, 5):
                print(f"*** VIEWPORT SCROLL TRIGGERED! vp changed to {vp} ***", flush=True)
            break

    print(f"\nFinal state: vp={get_vp(env._game)}", flush=True)
    print(f"Final foz: {[(f[0],f[1],f[2][:15]) for f in get_foz(env._game)]}", flush=True)
    print("=" * 60, flush=True)


if __name__ == '__main__':
    main()
