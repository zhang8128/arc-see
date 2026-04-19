"""LF52 L7 solver — BFS over (A-action, chain) sequences.

State: game snapshot.
Actions: A1-A4 (move vehicles), or click-chain (if selection + hint available).
Goal: reduce foz count below 3.
"""
import sys
import copy
import hashlib
import numpy as np
from collections import deque

sys.path.insert(0, '/Users/kairos/Projects/arc-see')
from lf52_tool import LF52, render_png
from arcengine import GameAction
from pathlib import Path

OUT = Path('/tmp/lf52_l7_solver')
OUT.mkdir(exist_ok=True)


def get_foz(game_obj):
    scene = game_obj.ikhhdzfmarl
    return [(s.x, s.y, s.name) for z, s, e in scene._sorted_cache
            if 'fozwvlovdui' in s.name and s.visible]


def get_vehicles(game_obj):
    scene = game_obj.ikhhdzfmarl
    return [(s.x, s.y, s.name) for z, s, e in scene._sorted_cache
            if 'hupkpseyuim' in s.name and s.visible]


def state_key(game_obj):
    """Compact state key: foz positions + vehicle positions."""
    foz = tuple(sorted((s.x, s.y) for z, s, e in game_obj.ikhhdzfmarl._sorted_cache
                        if 'fozwvlovdui' in s.name and s.visible))
    veh = tuple(sorted((s.x, s.y) for z, s, e in game_obj.ikhhdzfmarl._sorted_cache
                        if 'hupkpseyuim' in s.name and s.visible))
    return (foz, veh)


def try_select_and_chain(env, game_obj):
    """Try every selectable piece and every chain. Return list of (new_game_obj, description)."""
    results = []
    foz = get_foz(game_obj)
    vp = tuple(game_obj.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)

    for fx, fy, fn in foz:
        sx, sy = fx + vp[0] + 3, fy + vp[1] + 3
        if not (0 <= sx < 64 and 0 <= sy < 64):
            continue

        env._game = copy.deepcopy(game_obj)
        obs = env.step(GameAction.ACTION6, data={'x': sx, 'y': sy})
        frame = np.array(obs.frame[-1], dtype=np.int16)
        c3 = int((frame == 3).sum())

        if c3 == 0:
            continue

        hint_yx = list(zip(*np.where(frame == 2)))
        if not hint_yx:
            continue

        hint_center_y = int(np.mean([y for y, x in hint_yx]))
        hint_center_x = int(np.mean([x for y, x in hint_yx]))

        env._game = copy.deepcopy(game_obj)
        env.step(GameAction.ACTION6, data={'x': sx, 'y': sy})
        obs2 = env.step(GameAction.ACTION6, data={'x': hint_center_x, 'y': hint_center_y})

        new_foz = get_foz(env._game)
        desc = f'chain({fx},{fy})->hint({hint_center_x},{hint_center_y})'

        foz_positions_before = set((f[0], f[1]) for f in foz)
        foz_positions_after = set((f[0], f[1]) for f in new_foz)

        if foz_positions_before != foz_positions_after:
            results.append((copy.deepcopy(env._game), desc, new_foz))

    return results


def main():
    print("=" * 60)
    print("LF52 L7 SOLVER")
    print("=" * 60)

    g = LF52(up_to_level=7, verbose=False)

    # Phase 1: Apply known unlock + first chain
    print("\n[1] Applying unlock [3,3,1,1,3,3,3] + first chain...")
    for a in [3, 3, 1, 1, 3, 3, 3]:
        g.env.step(getattr(GameAction, f'ACTION{a}'))
    g.env.step(GameAction.ACTION6, data={'x': 7, 'y': 13})
    g.env.step(GameAction.ACTION6, data={'x': 7, 'y': 25})

    init_foz = get_foz(g.env._game)
    print(f"  Foz count: {len(init_foz)}")
    for f in init_foz:
        print(f"    {f}")

    init_state = copy.deepcopy(g.env._game)

    # Phase 2: BFS over (A-actions + chains)
    print("\n[2] BFS: A-actions + chain execution")
    print("-" * 40)

    visited = set()
    visited.add(state_key(init_state))

    queue = deque()
    queue.append((init_state, [], 0))  # (game_state, action_log, chain_count)

    states_explored = 0
    max_a_depth = 15
    solved = False

    while queue and not solved and states_explored < 50000:
        game_state, action_log, chain_count = queue.popleft()

        # Check win condition
        foz = get_foz(game_state)
        if len(foz) < 3:
            print(f"\n  *** FOZ REDUCED! foz={len(foz)} via {action_log}")
            solved = True
            break

        # Try chains first (they're more valuable than A-actions)
        chains = try_select_and_chain(g.env, game_state)
        for new_state, desc, new_foz in chains:
            key = state_key(new_state)
            if key not in visited:
                visited.add(key)
                new_log = action_log + [desc]
                if len(new_foz) < len(foz):
                    print(f"\n  *** FOZ REDUCED by chain! foz={len(new_foz)} via {new_log}")
                    solved = True
                    # Show final foz
                    for f in new_foz:
                        print(f"    {f}")
                    break
                queue.append((new_state, new_log, chain_count + 1))

        if solved:
            break

        # Try A-actions (only if total A-actions in log is < max_a_depth)
        a_count = sum(1 for x in action_log if x.startswith('A'))
        if a_count < max_a_depth:
            for a in [1, 2, 3, 4]:
                g.env._game = copy.deepcopy(game_state)
                g.env.step(getattr(GameAction, f'ACTION{a}'))
                new_state = copy.deepcopy(g.env._game)
                key = state_key(new_state)
                if key not in visited:
                    visited.add(key)
                    queue.append((new_state, action_log + [f'A{a}'], chain_count))

        states_explored += 1
        if states_explored % 1000 == 0:
            print(f"  ... {states_explored} states, {len(visited)} unique, queue={len(queue)}")

    if not solved:
        print(f"\n  Not solved in {states_explored} states")

    print(f"\n  Total: {states_explored} states, {len(visited)} unique")
    print("=" * 60)


if __name__ == '__main__':
    main()
