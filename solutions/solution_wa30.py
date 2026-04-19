"""WA30 solution — partial, L1-L6 solved.

WA30 is a pick-and-place puzzle on a 4px grid (16x16 positions).
Player grabs pieces (A5), carries them to target zones, drops.
Helpers auto-carry pieces toward targets. Enemies steal pieces.
"""
import sys
sys.path.insert(0, "environment_files/wa30/ee6fef47")
from wa30 import Wa30
from wa30_solve import (
    engine_step, extract_level, solve_simple, solve_with_engine,
    plan_delivery, bfs_carry, verify_local, DIRS, STEP
)

BASELINES = [71, 119, 183, 98, 368, 68, 79, 442, 415]


def solve_l5_targeted():
    """L5: player handles 2 specific pieces, helper handles 4."""
    g = Wa30()
    g.set_level(4)
    cfg = extract_level(g)
    walls = set(cfg["walls"])
    pieces = list(cfg["pieces"])

    blocked1 = set(walls)
    for i, pp in enumerate(pieces):
        if i != 0:
            blocked1.add(pp)
    r1 = plan_delivery(cfg["player"], pieces[0], (8, 36), blocked1)

    blocked2 = set(walls)
    for i, pp in enumerate(pieces):
        if i != 1:
            blocked2.add(pp)
    blocked2.add((8, 36))
    r2 = plan_delivery(r1[1], pieces[1], (8, 24), blocked2)

    total = r1[2] + r2[2]
    idle = [3] * 3 + [1, 2] * ((125 - total - 3) // 2 + 1)
    return r1[0] + r2[0] + idle[:125 - total]


def solve_all():
    g = Wa30()
    solutions = {}

    # L1: decomposition
    g.set_level(0)
    solutions[1] = solve_simple(extract_level(g))

    # L2-L4: greedy engine solver
    for lvl_idx in [1, 2, 3]:
        g.set_level(lvl_idx)
        cfg = extract_level(g)
        solutions[lvl_idx + 1] = solve_with_engine(lvl_idx, cfg["step_limit"])

    # L5: targeted
    solutions[5] = solve_l5_targeted()

    # L6: greedy
    solutions[6] = solve_with_engine(5, 75)

    # L7: manual (kill enemy then deliver)
    solutions[7] = [3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,4,4,4,4,4,4,4,1,4,5,1,4,5,3,3,3,3,3,2,5,2,4,4,4,4,4,4,4,4,4,4,5,3,3,3,3,3,3,3,3,3,5]

    # L8: kill both enemies then deliver one piece, let helpers finish
    # Kill upper enemy (7 acts): [1,1,4,4,4,1,5]
    # Kill lower enemy (13 acts): [2,2,4,4,4,4,4,2,2,2,3,3,5]
    # Deliver (8,12) to target (32 acts)
    # Idle for helpers (84 acts = to level completion)
    solutions[8] = [1,1,4,4,4,1,5,2,2,4,4,4,4,4,2,2,2,3,3,5,1,4,4,1,1,1,3,3,3,3,1,1,3,3,1,3,1,5,4,1,1,4,4,4,4,2,2,4,4,4,4,5,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3]

    # L9: 9/9 pieces in 70 steps (wins at step 69, 1 spare)
    # Prefix-40 from prior solution + randomized tail for helper coordination
    solutions[9] = [4,4,4,4,4,5,1,1,5,3,2,5,1,4,5,3,5,2,2,2,3,3,3,3,1,1,1,5,2,3,3,3,3,3,3,3,3,2,4,5,4,5,5,4,3,4,2,1,4,1,4,4,4,4,2,4,3,4,5,2,2,1,4,1,2,1,1,2,1,3]

    for lvl, sol in sorted(solutions.items()):
        if sol:
            print(f"  L{lvl}: {len(sol)} actions (baseline {BASELINES[lvl-1]})")
        else:
            print(f"  L{lvl}: FAILED")

    # Build sequential
    all_actions = []
    for lvl in range(1, 10):
        sol = solutions.get(lvl)
        if sol:
            all_actions.extend(sol)
        else:
            break

    print(f"\nTotal: {len(all_actions)} actions across {len(solutions)} levels")
    print("\nVerifying...")
    verify_local(all_actions)
    return all_actions


if __name__ == "__main__":
    solve_all()
