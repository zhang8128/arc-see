"""LF52 L7 solver v2 — iterative chain-drive-chain with BFS between chains.

Strategy: after each chain, BFS over A-actions to find next selectable state,
execute chain, repeat until foz < 3.
"""
import sys
import copy
import hashlib
import random
import numpy as np
from collections import deque

sys.path.insert(0, '/Users/kairos/Projects/arc-see')
from lf52_tool import LF52, render_png
from arcengine import GameAction
from pathlib import Path

OUT = Path('/tmp/lf52_l7_solver')
OUT.mkdir(exist_ok=True)


def get_foz(g):
    return [(s.x, s.y, s.name) for z, s, e in g.ikhhdzfmarl._sorted_cache
            if 'fozwvlovdui' in s.name and s.visible]


def get_vp(g):
    return tuple(g.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)


def try_selection_and_chain(env, game_snap):
    """From game_snap, try selecting each foz piece and executing any available chain.
    Returns list of (new_game_snap, chain_desc, new_foz_positions)."""
    foz = get_foz(game_snap)
    vp = get_vp(game_snap)
    results = []

    for fx, fy, fn in foz:
        sx, sy = fx + vp[0] + 3, fy + vp[1] + 3
        if not (0 <= sx < 64 and 0 <= sy < 64):
            continue

        env._game = copy.deepcopy(game_snap)
        obs = env.step(GameAction.ACTION6, data={'x': sx, 'y': sy})
        frame = np.array(obs.frame[-1], dtype=np.int16)

        if int((frame == 3).sum()) == 0:
            continue

        hint_yx = list(zip(*np.where(frame == 2)))
        if not hint_yx:
            continue

        hx = int(np.mean([x for y, x in hint_yx]))
        hy = int(np.mean([y for y, x in hint_yx]))

        env._game = copy.deepcopy(game_snap)
        env.step(GameAction.ACTION6, data={'x': sx, 'y': sy})
        env.step(GameAction.ACTION6, data={'x': hx, 'y': hy})

        new_foz = get_foz(env._game)
        new_pos = set((f[0], f[1]) for f in new_foz)
        old_pos = set((f[0], f[1]) for f in foz)

        if new_pos != old_pos:
            desc = f'chain({fx},{fy})->({hx},{hy})'
            results.append((copy.deepcopy(env._game), desc, new_foz))

    return results


def find_chain_after_a_actions(env, start_snap, max_depth=12, visited_positions=None):
    """BFS over A-actions to find ANY state where a chain moves piece to NEW position.
    Returns (a_sequence, chain_game_snap, chain_desc, new_foz) or None."""
    visited = set()

    def sk(g):
        foz = tuple(sorted((s.x, s.y) for z, s, e in g.ikhhdzfmarl._sorted_cache
                            if 'fozwvlovdui' in s.name and s.visible))
        veh = tuple(sorted((s.x, s.y) for z, s, e in g.ikhhdzfmarl._sorted_cache
                            if 'hupkpseyuim' in s.name and s.visible))
        return (foz, veh)

    visited.add(sk(start_snap))
    queue = deque()
    queue.append(([], copy.deepcopy(start_snap)))

    while queue:
        actions, snap = queue.popleft()
        if len(actions) > max_depth:
            continue

        chains = try_selection_and_chain(env, snap)
        foz_before = set((f[0], f[1]) for f in get_foz(snap))

        for new_snap, desc, new_foz in chains:
            new_pos = set((f[0], f[1]) for f in new_foz)
            if new_pos == foz_before:
                continue

            # Check if any NEW position was reached (not just any change)
            if visited_positions:
                new_reached = new_pos - foz_before
                if new_reached and all(p in visited_positions for p in new_reached):
                    continue  # All new positions already visited — skip

            # Also check: did foz count decrease?
            if len(new_foz) < len(get_foz(snap)):
                return (actions, new_snap, desc, new_foz)  # FOZ REDUCED — always take it

            return (actions, new_snap, desc, new_foz)

        # Expand
        if len(actions) < max_depth:
            for a in [1, 2, 3, 4]:
                env._game = copy.deepcopy(snap)
                env.step(getattr(GameAction, f'ACTION{a}'))
                new_g = copy.deepcopy(env._game)
                key = sk(new_g)
                if key not in visited:
                    visited.add(key)
                    queue.append((actions + [a], new_g))

    return None


def main():
    print("=" * 60)
    print("LF52 L7 SOLVER v2")
    print("=" * 60)

    g = LF52(up_to_level=7, verbose=False)

    # Phase 1: Known unlock + first chain
    print("\n[Phase 1] Unlock + first chain")
    unlock = [3, 3, 1, 1, 3, 3, 3]
    for a in unlock:
        g.env.step(getattr(GameAction, f'ACTION{a}'))
    g.env.step(GameAction.ACTION6, data={'x': 7, 'y': 13})
    g.env.step(GameAction.ACTION6, data={'x': 7, 'y': 25})

    current_state = copy.deepcopy(g.env._game)
    foz = get_foz(current_state)
    print(f"  Foz: {len(foz)} pieces")
    for f in foz:
        print(f"    {f}")

    full_sequence = list(unlock) + ['click(7,13)', 'click(7,25)']

    # Phase 2: Iterative chain-drive-chain
    print("\n[Phase 2] Iterative chain cascade")
    chain_num = 1
    max_chains = 20

    visited_piece_positions = set()
    for f in get_foz(current_state):
        visited_piece_positions.add((f[0], f[1]))

    while chain_num < max_chains:
        foz = get_foz(current_state)
        if len(foz) < 3:
            print(f"\n  *** FOZ REDUCED TO {len(foz)}! ***")
            break

        print(f"\n  Chain {chain_num + 1}: searching (visited positions: {visited_piece_positions})...")
        result = find_chain_after_a_actions(g.env, current_state, max_depth=12,
                                            visited_positions=visited_piece_positions)

        if result is None:
            print(f"  No NEW chains found at depth 12")
            break

        a_seq, new_state, desc, new_foz = result
        print(f"  A-sequence: {a_seq}")
        print(f"  Chain: {desc}")
        print(f"  New foz positions:")
        for f in new_foz:
            print(f"    {f}")
            visited_piece_positions.add((f[0], f[1]))

        full_sequence += [f'A{a}' for a in a_seq] + [desc]
        current_state = new_state
        chain_num += 1

    # Final result
    print("\n" + "=" * 60)
    foz = get_foz(current_state)
    if len(foz) < 3:
        print(f"SOLVED! Foz reduced to {len(foz)}")
    else:
        print(f"NOT SOLVED. Foz still {len(foz)}")
        print(f"Final positions:")
        for f in foz:
            print(f"  {f}")

    print(f"\nFull sequence ({len(full_sequence)} steps):")
    print(f"  {full_sequence}")
    print("=" * 60)


if __name__ == '__main__':
    main()
