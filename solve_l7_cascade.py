"""LF52 L7 cascade solver — execute known chain path + find continuation.

Known path:
  Chain 1: (0,6)→(0,18) via DGX(0,12) [DOWN]
  Drive: [4,4,4,2,2,3,3,2] → piece at (6,36)
  Chain 2: (6,36)→(6,48) via DGX(6,42) [DOWN]
  Drive: [1,4] → selection enabled
  Chain 3: (6,48)→(18,48) via DGX(12,48) [RIGHT]
  Drive: [3] → selection enabled
  Chain 4: (18,48)→(30,48) via DGX(24,48) [RIGHT]
"""
import sys
import copy
import random
import numpy as np
from collections import deque

sys.path.insert(0, '/Users/kairos/Projects/arc-see')
from lf52_tool import LF52, render_png
from arcengine import GameAction
from pathlib import Path

OUT = Path('/tmp/lf52_l7_solver')
OUT.mkdir(exist_ok=True)


def get_foz(game):
    return [(s.x, s.y, s.name) for z, s, e in game.ikhhdzfmarl._sorted_cache
            if 'fozwvlovdui' in s.name and s.visible]


def get_vp(game):
    return tuple(game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)


def do_a(env, a):
    return env.step(getattr(GameAction, f'ACTION{a}'))


def do_click(env, x, y):
    return env.step(GameAction.ACTION6, data={'x': x, 'y': y})


def select_and_chain(env, game_snap, piece_wx, piece_wy, direction='any'):
    """Select piece at world (wx,wy) and execute chain. direction filters hints."""
    vp = get_vp(game_snap)
    sx, sy = piece_wx + vp[0] + 3, piece_wy + vp[1] + 3
    if not (0 <= sx < 64 and 0 <= sy < 64):
        return None

    env._game = copy.deepcopy(game_snap)
    obs = do_click(env, sx, sy)
    frame = np.array(obs.frame[-1], dtype=np.int16)
    if int((frame == 3).sum()) == 0:
        return None

    hints = [(int(x), int(y)) for y, x in zip(*np.where(frame == 2))]
    if not hints:
        return None

    if direction == 'right':
        hints = [(x, y) for x, y in hints if x > sx]
    elif direction == 'down':
        hints = [(x, y) for x, y in hints if y > sy]
    elif direction == 'up':
        hints = [(x, y) for x, y in hints if y < sy]
    elif direction == 'left':
        hints = [(x, y) for x, y in hints if x < sx]

    if not hints:
        return None

    hx = int(np.mean([h[0] for h in hints]))
    hy = int(np.mean([h[1] for h in hints]))

    env._game = copy.deepcopy(game_snap)
    do_click(env, sx, sy)
    do_click(env, hx, hy)

    return copy.deepcopy(env._game)


def show_state(label, game):
    foz = get_foz(game)
    vp = get_vp(game)
    print(f'{label}: foz={len(foz)} vp={vp}')
    for f in foz:
        print(f'  {f[2][:25]:25s} ({f[0]:3d},{f[1]:3d})')
    return foz


def find_chain_bfs(env, start_snap, visited_pos, max_depth=15):
    """BFS over A-actions to find chain to a NEW position."""

    def sk(g):
        foz = tuple(sorted((s.x, s.y) for z, s, e in g.ikhhdzfmarl._sorted_cache
                            if 'fozwvlovdui' in s.name and s.visible))
        veh = tuple(sorted((s.x, s.y) for z, s, e in g.ikhhdzfmarl._sorted_cache
                            if 'hupkpseyuim' in s.name and s.visible))
        return (foz, veh)

    visited = {sk(start_snap)}
    queue = deque([([], copy.deepcopy(start_snap))])
    foz_start = set((f[0], f[1]) for f in get_foz(start_snap))

    while queue:
        actions, snap = queue.popleft()
        if len(actions) > max_depth:
            continue

        foz = get_foz(snap)
        vp = get_vp(snap)

        for fx, fy, fn in foz:
            sx, sy = fx + vp[0] + 3, fy + vp[1] + 3
            if not (0 <= sx < 64 and 0 <= sy < 64):
                continue

            env._game = copy.deepcopy(snap)
            obs = do_click(env, sx, sy)
            frame = np.array(obs.frame[-1], dtype=np.int16)
            if int((frame == 3).sum()) == 0:
                continue

            hints = [(int(x), int(y)) for y, x in zip(*np.where(frame == 2))]
            if not hints:
                continue

            hx = int(np.mean([h[0] for h in hints]))
            hy = int(np.mean([h[1] for h in hints]))

            env._game = copy.deepcopy(snap)
            do_click(env, sx, sy)
            do_click(env, hx, hy)

            new_foz = get_foz(env._game)
            new_pos = set((f[0], f[1]) for f in new_foz)

            if len(new_foz) < len(foz):
                return actions, copy.deepcopy(env._game), f'chain({fx},{fy})->foz_reduced!', new_foz

            new_reached = new_pos - foz_start
            if new_reached and not all(p in visited_pos for p in new_reached):
                return actions, copy.deepcopy(env._game), f'chain({fx},{fy})->new_pos', new_foz

        if len(actions) < max_depth:
            for a in [1, 2, 3, 4]:
                env._game = copy.deepcopy(snap)
                do_a(env, a)
                new_g = copy.deepcopy(env._game)
                key = sk(new_g)
                if key not in visited:
                    visited.add(key)
                    queue.append((actions + [a], new_g))

    return None


def main():
    print("=" * 60)
    print("LF52 L7 CASCADE SOLVER")
    print("=" * 60)

    g = LF52(up_to_level=7, verbose=False)
    env = g.env

    visited_pos = set()
    total_actions = []

    # Phase 1: Unlock
    print("\n--- Phase 1: Unlock ---")
    unlock = [3, 3, 1, 1, 3, 3, 3]
    for a in unlock:
        do_a(env, a)
    total_actions.extend([f'A{a}' for a in unlock])

    # Chain 1: (0,6) → (0,18) DOWN
    state = copy.deepcopy(env._game)
    state = select_and_chain(env, state, 0, 6, 'down')
    show_state('Chain 1', state)
    total_actions.extend(['C(0,6,down)'])
    visited_pos.update((f[0], f[1]) for f in get_foz(state))

    # Drive to (6,36)
    print("\n--- Drive to (6,36) ---")
    env._game = copy.deepcopy(state)
    drive1 = [4, 4, 4, 2, 2, 3, 3, 2]
    for a in drive1:
        do_a(env, a)
    state = copy.deepcopy(env._game)
    total_actions.extend([f'A{a}' for a in drive1])
    show_state('After drive', state)

    # Chain 2: (6,36) → (6,48) DOWN
    state = select_and_chain(env, state, 6, 36, 'down')
    if state:
        show_state('Chain 2', state)
        total_actions.append('C(6,36,down)')
        visited_pos.update((f[0], f[1]) for f in get_foz(state))
    else:
        print("  Chain 2 FAILED!")
        return

    # Drive for chain 3
    print("\n--- Drive for chain 3 ---")
    env._game = copy.deepcopy(state)
    drive2 = [1, 4]
    for a in drive2:
        do_a(env, a)
    state = copy.deepcopy(env._game)
    total_actions.extend([f'A{a}' for a in drive2])

    # Chain 3: (6,48) → RIGHT
    state = select_and_chain(env, state, 6, 48, 'right')
    if state:
        show_state('Chain 3', state)
        total_actions.append('C(6,48,right)')
        visited_pos.update((f[0], f[1]) for f in get_foz(state))
    else:
        print("  Chain 3 FAILED!")
        return

    # Drive for chain 4
    print("\n--- Drive for chain 4 ---")
    env._game = copy.deepcopy(state)
    drive3 = [3]
    for a in drive3:
        do_a(env, a)
    state = copy.deepcopy(env._game)
    total_actions.extend([f'A{a}' for a in drive3])

    # Chain 4: (18,48) → RIGHT
    state = select_and_chain(env, state, 18, 48, 'right')
    if state:
        foz4 = show_state('Chain 4', state)
        total_actions.append('C(18,48,right)')
        visited_pos.update((f[0], f[1]) for f in foz4)
    else:
        print("  Chain 4 FAILED! Trying BFS...")
        result = find_chain_bfs(env, state, visited_pos, max_depth=12)
        if result:
            a_seq, state, desc, foz4 = result
            total_actions.extend([f'A{a}' for a in a_seq] + [desc])
            show_state('Chain 4 (BFS)', state)
            visited_pos.update((f[0], f[1]) for f in foz4)
        else:
            print("  No chain 4 found!")
            return

    # Continue with BFS chain search
    print("\n--- Iterative BFS chains ---")
    chain_num = 5
    while chain_num <= 20:
        foz = get_foz(state)
        if len(foz) < 3:
            print(f"\n  *** FOZ REDUCED TO {len(foz)}! ***")
            break

        result = find_chain_bfs(env, state, visited_pos, max_depth=15)
        if result:
            a_seq, state, desc, new_foz = result
            total_actions.extend([f'A{a}' for a in a_seq] + [desc])
            show_state(f'Chain {chain_num}', state)
            visited_pos.update((f[0], f[1]) for f in new_foz)
            chain_num += 1
        else:
            print(f"  No more chains found (chain {chain_num})")
            break

    # Result
    print("\n" + "=" * 60)
    foz = get_foz(state)
    if len(foz) < 3:
        print(f"SOLVED! Foz = {len(foz)}")
        obs = do_click(env, 0, 0)
        frame = np.array(obs.frame[-1], dtype=np.int16)
        render_png(frame, label='L7 SOLVED!').save(OUT / 'l7_solved.png')
    else:
        print(f"NOT SOLVED. Foz = {len(foz)}")
        for f in foz:
            print(f"  {f}")

    print(f"\nTotal actions: {len(total_actions)}")
    print(f"Visited positions: {sorted(visited_pos)}")
    print(f"Sequence: {total_actions}")
    print("=" * 60)


if __name__ == '__main__':
    main()
