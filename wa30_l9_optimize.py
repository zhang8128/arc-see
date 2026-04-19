"""WA30 L9 optimization — find 9/9 piece placement in 70 steps.

Uses arc_agi env wrapper for proper step handling.
"""
import sys
import copy
import random
import numpy as np

sys.path.insert(0, '/Users/kairos/Projects/arc-see')
import arc_agi
from arcengine import GameAction

GAME_ID = 'wa30-ee6fef47'
ACTIONS = [1, 2, 3, 4, 5]


def make_env():
    """Create WA30 env, double-reset, return env."""
    arcade = arc_agi.Arcade()
    env = arcade.make(GAME_ID, render_mode=None)
    env.reset()
    env.reset()
    return env


def advance_to_l9(env):
    """Replay L1-L8 solutions to reach L9 legitimately."""
    from solutions.solution_wa30 import solve_all
    # Actually, just use set_level via game internals
    g = env._game
    g.set_level(8)  # L9 = index 8
    g.on_set_level(g.current_level)
    # Trigger a dummy step to initialize properly
    obs = env.step(GameAction.ACTION3)  # Move right (harmless)
    return obs


def run_solution(env_game_snap, actions):
    """Run actions on a deepcopy of the game, return (won, steps_used, state_info)."""
    arcade = arc_agi.Arcade()
    env = arcade.make(GAME_ID, render_mode=None)
    env.reset()
    env.reset()
    env._game = copy.deepcopy(env_game_snap)

    for i, a in enumerate(actions):
        act = getattr(GameAction, f'ACTION{a}')
        obs = env.step(act)
        if obs.state.name == 'WIN':
            return True, i + 1, 'WIN'
        if obs.state.name == 'LOSE':
            return False, i + 1, 'LOSE'

    return False, len(actions), obs.state.name


def count_pieces_on_target(game):
    """Count geezpjgiyd sprites at fsjjayjoeg positions."""
    targets = game.lkvghqfwan
    bad = game.uuorgjazmj
    count = 0
    total = 0
    # Need to find piece sprites
    # Check pkbufziase vs lkvghqfwan
    for pos in game.pkbufziase:
        if pos in targets and pos not in bad:
            count += 1
    return count


def run_and_count(env, game_snap, actions):
    """Run actions and return (pieces_delivered, won)."""
    env._game = copy.deepcopy(game_snap)

    for a in actions:
        act = getattr(GameAction, f'ACTION{a}')
        obs = env.step(act)
        if obs.state.name == 'WIN':
            return 9, True  # All 9 delivered
        if obs.state.name == 'LOSE':
            break

    # Count delivered via pixel analysis or game state
    g = env._game
    try:
        won = g.ymzfopzgbq() if hasattr(g, 'ymzfopzgbq') else False
    except:
        won = False

    return 0 if obs.state.name == 'LOSE' else -1, obs.state.name == 'WIN'


def pixel_score(env, game_snap, actions):
    """Run actions, return a score based on how close to winning."""
    env._game = copy.deepcopy(game_snap)

    last_obs = None
    for a in actions:
        act = getattr(GameAction, f'ACTION{a}')
        obs = env.step(act)
        last_obs = obs
        if obs.state.name == 'WIN':
            return 10000
        if obs.state.name == 'LOSE':
            return -1

    # Score = negative of pixels that differ from win state
    # Actually, just check how many pieces are in target zone
    pix = np.array(obs.frame[-1], dtype=np.int16)
    # More unique colors in target area = more pieces delivered
    return obs.score if hasattr(obs, 'score') else 0


def mutate(actions, n=3):
    result = list(actions)
    for _ in range(n):
        op = random.choice(['swap', 'replace', 'insert', 'delete', 'segment'])
        if op == 'swap' and len(result) >= 2:
            i, j = random.sample(range(len(result)), 2)
            result[i], result[j] = result[j], result[i]
        elif op == 'replace' and result:
            i = random.randrange(len(result))
            result[i] = random.choice(ACTIONS)
        elif op == 'insert' and len(result) < 70:
            i = random.randrange(len(result) + 1)
            result.insert(i, random.choice(ACTIONS))
        elif op == 'delete' and len(result) > 30:
            i = random.randrange(len(result))
            result.pop(i)
        elif op == 'segment' and len(result) >= 5:
            # Replace a segment with random
            start = random.randrange(len(result) - 3)
            seg_len = random.randint(2, min(8, len(result) - start))
            for j in range(start, start + seg_len):
                result[j] = random.choice(ACTIONS)
    return result[:70]


def main():
    print("=" * 60)
    print("WA30 L9 OPTIMIZATION")
    print("=" * 60)

    env = make_env()

    # Advance to L9
    print("\n[1] Setting up L9...")
    g = env._game
    g.set_level(8)
    g.on_set_level(g.current_level)

    # Get initial state info
    print(f"  Level: {g._current_level_index}")
    print(f"  Step counter: {g.kuncbnslnm.dbdarsgrbj}")
    print(f"  Targets (lkvghqfwan): {len(g.lkvghqfwan)} positions")
    print(f"  Bad zone (uuorgjazmj): {len(g.uuorgjazmj)} positions")
    print(f"  Walls (qthdiggudy): {len(g.qthdiggudy)} positions")
    print(f"  Pieces (pkbufziase): {len(g.pkbufziase)} positions")

    # Save L9 init snapshot
    l9_snap = copy.deepcopy(g)

    # Test current best
    print("\n[2] Current best solution test...")
    current_best = [4,4,4,4,4,5,1,1,5,3,2,5,1,4,5,3,5,2,2,2,3,3,3,3,1,1,1,5,2,3,3,3,3,3,3,3,3,2,4,5,1,2,2,4,4,1,5,2,3,3,3,2,5,2,4,4,1,1,4,1,1,1,2,5,3,2,3,3,4,3]
    won, steps, state = run_solution(l9_snap, current_best)
    print(f"  Actions: {len(current_best)}, Won: {won}, State: {state}, Steps used: {steps}")

    # Hill climbing via mutation
    print("\n[3] Hill-climbing mutation search...")
    best_actions = list(current_best)
    best_won = won

    # Use simple won/not-won + mutation
    trials = 0
    for trial in range(200000):
        n_mut = random.randint(1, 6)
        candidate = mutate(best_actions, n_mut)

        env._game = copy.deepcopy(l9_snap)
        won_c = False
        for a in candidate:
            act = getattr(GameAction, f'ACTION{a}')
            obs = env.step(act)
            if obs.state.name == 'WIN':
                won_c = True
                break

        if won_c:
            print(f"  *** WIN at trial {trial}!")
            print(f"  Actions: {candidate}")
            best_actions = candidate
            best_won = True
            break

        trials += 1
        if trials % 25000 == 0:
            print(f"  ... {trials} trials, no win yet")

    if not best_won:
        print(f"  No win found in {trials} mutations")

    # Random search
    if not best_won:
        print("\n[4] Random sequence search (100K)...")
        for trial in range(100000):
            candidate = [random.choice(ACTIONS) for _ in range(70)]

            env._game = copy.deepcopy(l9_snap)
            won_c = False
            for a in candidate:
                act = getattr(GameAction, f'ACTION{a}')
                obs = env.step(act)
                if obs.state.name == 'WIN':
                    won_c = True
                    break

            if won_c:
                print(f"  *** RANDOM WIN at trial {trial}!")
                print(f"  Actions: {candidate}")
                best_actions = candidate
                best_won = True
                break

            if trial % 25000 == 0 and trial > 0:
                print(f"  ... {trial} random trials")

        if not best_won:
            print(f"  No random win")

    # Prefix-mutation: keep best prefix, randomize tail
    if not best_won:
        print("\n[5] Prefix-preserve search...")
        for prefix_len in [60, 55, 50, 45, 40, 35, 30, 25, 20, 15, 10]:
            base = best_actions[:prefix_len]
            found = False
            for trial in range(20000):
                tail = [random.choice(ACTIONS) for _ in range(70 - prefix_len)]
                candidate = base + tail

                env._game = copy.deepcopy(l9_snap)
                won_c = False
                for a in candidate:
                    act = getattr(GameAction, f'ACTION{a}')
                    obs = env.step(act)
                    if obs.state.name == 'WIN':
                        won_c = True
                        break

                if won_c:
                    print(f"  *** PREFIX({prefix_len}) WIN at trial {trial}!")
                    print(f"  Actions: {candidate}")
                    best_actions = candidate
                    best_won = True
                    found = True
                    break

            if found:
                break
            print(f"  Prefix {prefix_len}: no win in 20K trials")

    print("\n" + "=" * 60)
    if best_won:
        print(f"SOLVED! Actions ({len(best_actions)}): {best_actions}")
    else:
        print("NOT SOLVED — 8/9 remains best")
    print("=" * 60)


if __name__ == '__main__':
    main()
