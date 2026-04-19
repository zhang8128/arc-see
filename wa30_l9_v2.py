"""WA30 L9 optimization v2 — uses deepcopy + direct action, no env wrapper.

The game's step() uses self.action (an ActionInput). We set that directly.
"""
import sys
import copy
import random

sys.path.insert(0, '/Users/kairos/Projects/arc-see')
sys.path.insert(0, 'environment_files/wa30/ee6fef47')
from wa30 import Wa30
from arcengine import GameAction
from arcengine.enums import ActionInput

ACTIONS = [1, 2, 3, 4, 5]


def do_action(g, a):
    """Execute action on game object directly."""
    ai = ActionInput(id=getattr(GameAction, f'ACTION{a}'))
    g.yygfcvqoyx(ai)
    if g.ymzfopzgbq():
        g.next_level()
    elif g.kuncbnslnm.current_steps <= 0:
        g.lose()


def is_won(g):
    return g._state.name == 'WIN'


def is_lost(g):
    return g._state.name == 'LOSE' or g.kuncbnslnm.current_steps <= 0


def run_solution(g_init, actions):
    """Run actions on deepcopy, return (won, final_state_name)."""
    g = copy.deepcopy(g_init)
    for a in actions:
        do_action(g, a)
        if is_won(g):
            return True, 'WIN'
        if is_lost(g):
            return False, 'LOSE'
    return is_won(g), g._state.name


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
            start = random.randrange(len(result) - 3)
            seg_len = random.randint(2, min(8, len(result) - start))
            for j in range(start, start + seg_len):
                if j < len(result):
                    result[j] = random.choice(ACTIONS)
    return result[:70]


def main():
    print("=" * 60)
    print("WA30 L9 OPTIMIZATION v2")
    print("=" * 60)

    g = Wa30()
    g.set_level(8)
    g.on_set_level(g.current_level)
    print(f"  Steps: {g.kuncbnslnm.dbdarsgrbj}")

    l9_init = copy.deepcopy(g)

    # Test current best
    current_best = [4,4,4,4,4,5,1,1,5,3,2,5,1,4,5,3,5,2,2,2,3,3,3,3,1,1,1,5,2,3,3,3,3,3,3,3,3,2,4,5,1,2,2,4,4,1,5,2,3,3,3,2,5,2,4,4,1,1,4,1,1,1,2,5,3,2,3,3,4,3]
    won, state = run_solution(l9_init, current_best)
    print(f"  Current best: {len(current_best)} actions, won={won}, state={state}")

    best_actions = list(current_best)
    best_won = won

    # Hill climbing
    print("\n[1] Hill-climbing (500K trials)...")
    for trial in range(500000):
        n_mut = random.randint(1, 6)
        candidate = mutate(best_actions, n_mut)
        won_c, _ = run_solution(l9_init, candidate)

        if won_c:
            print(f"  *** WIN at trial {trial}!")
            print(f"  Actions: {candidate}")
            best_actions = candidate
            best_won = True
            break

        if trial % 50000 == 0 and trial > 0:
            print(f"  ... {trial} trials")

    if not best_won:
        print(f"  No win in 500K mutations")

    # Random search
    if not best_won:
        print("\n[2] Random (200K trials)...")
        for trial in range(200000):
            candidate = [random.choice(ACTIONS) for _ in range(70)]
            won_c, _ = run_solution(l9_init, candidate)
            if won_c:
                print(f"  *** RANDOM WIN at trial {trial}!")
                print(f"  Actions: {candidate}")
                best_actions = candidate
                best_won = True
                break
            if trial % 50000 == 0 and trial > 0:
                print(f"  ... {trial} trials")

    # Prefix-preserve
    if not best_won:
        print("\n[3] Prefix-preserve...")
        for prefix_len in [60, 55, 50, 45, 40, 35, 30, 25, 20, 15, 10, 5]:
            base = best_actions[:prefix_len]
            for trial in range(30000):
                tail = [random.choice(ACTIONS) for _ in range(70 - prefix_len)]
                candidate = base + tail
                won_c, _ = run_solution(l9_init, candidate)
                if won_c:
                    print(f"  *** PREFIX({prefix_len}) WIN at trial {trial}!")
                    print(f"  Actions: {candidate}")
                    best_actions = candidate
                    best_won = True
                    break
            if best_won:
                break
            print(f"  Prefix {prefix_len}: no win in 30K")

    print("\n" + "=" * 60)
    if best_won:
        print(f"SOLVED! Actions: {best_actions}")
    else:
        print("NOT SOLVED")
    print("=" * 60)


if __name__ == '__main__':
    main()
