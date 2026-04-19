#!/usr/bin/env python3
"""SK48 L6 — Guided search using game engine with phase-based strategy.

Strategy:
Phase 1: Push 8-targets from x=29 to x=35 using H-rack on rows 32,38,44
Phase 2: Push 9-target at (35,26) down using V-rack at x=35
Phase 3: V-rack at x=35, extend to 8 segs → V-rack wins
Phase 4: H-rack at correct row with 9-targets → H-rack wins

Key insight: the SWITCH action (ACTION6 click) costs 1 game action.
"""
import sys, copy, itertools
sys.path.insert(0, 'environment_files/sk48/41055498')
from sk48 import Sk48
from arcengine import GameAction
from arcengine.enums import ActionInput

def make():
    g = Sk48()
    g._current_level_index = 5
    g.on_set_level(g._levels[5])
    return g

def act(g, aid, data=None):
    ai = ActionInput(id=aid, data=data or {})
    g.perform_action(ai)
    for _ in range(200):
        if g.is_action_complete: break
        g.step()

def switch_rack(g):
    """Switch to the other rack."""
    for rack in g.xpmcmtbcv.keys():
        if rack != g.vzvypfsnt:
            act(g, GameAction.ACTION6, {'x': rack.x + 2, 'y': rack.y + 2})
            return

def get_active_name(g):
    return 'H' if g.vzvypfsnt.rotation == 0 else 'V'

AM = {'U': GameAction.ACTION1, 'D': GameAction.ACTION2, 'L': GameAction.ACTION3, 'R': GameAction.ACTION4}

def do_seq(g, seq, log=None):
    """Execute a sequence of actions. Returns list of game actions used."""
    actions = []
    for s in seq:
        if s == 'S':
            switch_rack(g)
            actions.append('S')
        else:
            act(g, AM[s])
            actions.append(get_active_name(g) + s)
    if log:
        log.extend(actions)
    return actions

def is_won(g):
    return g.gvtmoopqgy()

def get_targets(g):
    return {(t.x, t.y): int(t.pixels[1,1]) for t in g.vbelzuaian}

def get_state(g):
    racks = {}
    for r, segs in g.mwfajkguqx.items():
        racks[(r.x, r.y, r.rotation)] = len(segs)
    return racks, get_targets(g)

def try_sequence(seq):
    """Try a sequence and return (won, action_count, state_info)."""
    g = make()
    path = []
    do_seq(g, seq, path)
    won = is_won(g)
    return won, len(path), get_state(g), path

# Try various strategies
def strategy_1():
    """
    Phase 1: H-rack pushes 8-targets right from x=29 to x=35 on rows 32,38,44
    Phase 2: V-rack moves to x=35, extends to cover the 8-targets
    Phase 3: Fix 9-targets for H-rack
    """
    # H-rack starts active at y=26, 2 segs
    # First: move H down to y=32, extend 3× (push 8-target), shrink 3×
    phase1_row32 = list('DRRRLLLDRRRLLL')  # D to 32, RRR extend (push), LLL shrink, RRR extend again for next...

    # Actually let me be more precise
    # D: y=26→32
    # R: 3 segs, x=5,11,17
    # R: 4 segs, x=5,...,23
    # R: 5 segs, x=5,...,29, pushes (29,32)→(35,32)
    # L: 4 segs
    # L: 3 segs
    # L: 2 segs
    # D: y=32→38
    # RRR: 5 segs, pushes (29,38)→(35,38)
    # LLL: 2 segs
    # D: y=38→44
    # RRR: 5 segs, pushes (29,44)→(35,44)
    # LLL: 2 segs

    phase1 = list('DRRRLLLDRRRLLLDRRRLLLL')  # Extra L at end? No.
    # D + RRR + LLL + D + RRR + LLL + D + RRR + LLL = 1+3+3+1+3+3+1+3+3 = 21
    phase1 = list('DRRRLLL' * 3)  # Wait, first D is from y=26→32, then 32→38, then 38→44
    # Actually: DRRRLLLDRRRLLLDRRRLL
    # But the first D goes from 26→32. Then we do RRR to extend (pushes at row 32).
    # Then LLL to shrink. Then D from 32→38. RRR push at 38. LLL. D from 38→44. RRR push at 44. LLL.
    phase1 = list('DRRRLLLDRRRLLLDRRRLL')

    # Hmm let me just be explicit
    phase1 = ['D', 'R','R','R', 'L','L','L',
              'D', 'R','R','R', 'L','L','L',
              'D', 'R','R','R', 'L','L']  # 20 actions, rack ends at y=44, 1 seg (need LLL to get to 2?)

    # Wait, initial is 2 segs. Extend 3× → 5 segs. Shrink 3× → 2 segs.
    # Then D, extend 3×, shrink 3× → 2 segs.
    # Then D, extend 3×, shrink 2× → 3 segs? No, shrink 3× → 2 segs.
    phase1 = ['D'] + ['R']*3 + ['L']*3 + ['D'] + ['R']*3 + ['L']*3 + ['D'] + ['R']*3 + ['L']*3  # 21

    # Now switch to V-rack
    phase2 = ['S']  # Switch to V-rack

    # V-rack at x=29. Move RIGHT to x=35.
    phase2 += ['R']

    # Extend V-rack DOWN to 8 segs. Start with 2, need 6 more D's.
    phase2 += ['D'] * 6  # 8 segs at y=2,...,44

    # Total so far: 21 + 1 + 1 + 6 = 29

    # Now check: V-rack at x=35 with 8 segs.
    # Targets at (35,32)=8, (35,38)=8, (35,44)=8 on segs at y=32,38,44.
    # But there might be a 9-target at (35,26) that got pushed down during V-rack extension!

    # During extension at x=35, when seg at y=20→26: target at (35,26)=9 gets pushed.
    # Chain: (35,26) → (35,32). But (35,32) has 8-target! Chain: (35,32)→(35,38)→(35,44)→(35,50) OOB.
    # Parallel extension: push fails, targets stay. 9-target overlaps with segment.

    # This means vjfbwggsd for V-rack will have 9-target before 8-targets: [9,8,8,8]
    # That's wrong! Need [8,8,8].

    # Solution: push 9-target at (35,26) away BEFORE phase2.
    # Use H-rack to push it... but H-rack can't reach x=35 on y=26.

    # Alternative: push (35,26) DOWN using V-rack FIRST (before pushing 8-targets to x=35).
    # Then the 9-target at (35,32) gets pushed further when 8-targets arrive.

    # Actually let's just try and see what happens
    full = phase1 + phase2
    won, count, state, path = try_sequence(full)
    print(f"Strategy 1: won={won}, actions={count}")
    print(f"State: {state}")
    tgts = state[1]
    print(f"Targets: {tgts}")
    return won, path

def strategy_2():
    """
    Phase 0: Push 9-target at (35,26) away from x=35
    Phase 1: Push 8-targets from x=29 to x=35
    Phase 2: V-rack to x=35, extend down
    Phase 3: H-rack collects 9-targets

    For Phase 0: switch to V-rack, move to x=35, extend to push (35,26) down, shrink back.
    """
    # Phase 0: V-rack pushes (35,26) down
    # Switch to V-rack, move right to x=35, extend 3× to push through y=26
    phase0 = ['S', 'R']  # Switch + move V to x=35
    phase0 += ['D'] * 3   # Extend to 5 segs, pushing (35,26) to (35,32)
    phase0 += ['U'] * 3   # Shrink back to 2 segs
    phase0 += ['L']        # Move back to x=29
    # 9 actions, V-rack back at x=29, 2 segs

    # Phase 1: Switch to H-rack, push 8-targets
    phase1 = ['S']  # Switch to H-rack (now at y=26, 2 segs... wait, did it move?)
    # H-rack hasn't moved, still at y=26, 2 segs
    # But 9-target at (35,26) was pushed to (35,32)!
    phase1 += ['D'] + ['R']*3 + ['L']*3  # y=32, push (29,32) right. But (35,32) has 9-target!
    # When extending: (29,32) pushes to (35,32)=9. Chain: (35,32)→(41,32). Empty? (41,26)=9 is at y=26, not 32. Yes, (41,32) is empty. Push succeeds!
    # After: (35,32)=8, (41,32)=9

    phase1 += ['D'] + ['R']*3 + ['L']*3  # y=38, push (29,38) right. (35,38) empty → (35,38)=8
    phase1 += ['D'] + ['R']*3 + ['L']*3  # y=44, push (29,44) right. (35,44) empty → (35,44)=8
    # 1 + 21 = 22 actions

    # Phase 2: V-rack to x=35, extend to 8 segs
    phase2 = ['S', 'R']  # Switch to V, move right to x=35
    phase2 += ['D'] * 6   # Extend to 8 segs
    # During extension, seg y=20→26: no target at (35,26) (pushed in phase 0). Good!
    # Seg y=26→32: target at (35,32)=8. Push? Chain (35,32)→(35,38)→(35,44)→(35,50) OOB.
    # Parallel extension: push fails. Target stays. Segment overlaps. Target ON segment!
    # Same for y=38 and y=44 targets.
    # vjfbwggsd: targets at y=32,38,44 = [8,8,8]. No 9-target in between!
    # 8 actions

    # But wait, the 9-target at (41,32) — is it at x=35? No, it's at x=41. V-rack is at x=35. Not a problem.

    # Total: 9 + 22 + 8 = 39 actions
    # Still need H-rack to win with [9,9,9]!

    # Phase 3: H-rack collects 9-targets
    # 9-targets now at: (41,26), (47,26), (41,32)
    # Wait, where did (35,26) go? It was pushed to (35,32) in phase 0.
    # Then in phase 1, extending H-rack at y=32 pushed (29,32) to (35,32), but (35,32) already had the 9-target!
    # The 9-target at (35,32) gets pushed to (41,32) by the chain.
    # And (29,32)=8 takes its place at (35,32).
    # So 9-targets: (41,26), (47,26), (41,32)

    # H-rack at y=44 with 2 segs after phase 1. Need to get to a row with 9-targets.
    # 9-targets at y=26: (41,26), (47,26)
    # 9-target at y=32: (41,32)

    # If H-rack goes to y=32 (or y=26), with segments at x=41,47: needs 7+ segs (x=5,...,47)
    # But on y=26, can't have segment at x=29 (obstacle).

    # H-rack at y=32 with 8 segs (x=5,...,47): covers (41,32) → 1 nine-target. Need 3.

    # The other 9-targets at y=26 need to be pushed to y=32. Use V-rack at x=41 and x=47.
    # But V-rack is currently at x=35 with 8 segs...

    # This is getting complex. Let me just try the first 39 actions and see.
    full = phase0 + phase1 + phase2
    won, count, state, path = try_sequence(full)
    print(f"Strategy 2 partial: won={won}, actions={count}")
    racks, tgts = state
    print(f"Racks: {racks}")
    print(f"Targets: {tgts}")
    return won, path


def strategy_3():
    """
    Fully integrated strategy:
    1. Push 9-targets DOWN from y=26 using V-rack at each x (35,41,47)
    2. Push 8-targets RIGHT from x=29 to x=35 using H-rack
    3. V-rack at x=35 extend to win
    4. H-rack at appropriate y to cover 9-targets at (35,32),(41,32),(47,32)

    Step 1: V-rack → push 9-targets to y=32
    1a. V-rack at x=47: extend to push (47,26)→(47,32). Shrink back.
    1b. V-rack to x=41: extend to push (41,26)→(41,32). Shrink.
    1c. V-rack to x=35: extend to push (35,26)→(35,32). Shrink.

    Step 2: H-rack push 8-targets to x=35
    2a. H-rack at y=32: extend pushes (29,32)→(35,32)→(41,32)→(47,32)→(53,32) OOB!
        Chain fails because 9-targets are also at y=32!

    Problem: 9 and 8 targets collide at y=32.
    Solution: push 9-targets to y=38 or y=20 instead.
    """
    # Push 9-targets to y=32, then 8-targets to y=38? No, 8-targets start at y=32,38,44.

    # Different idea: push 9-targets to y=20 (UP from 26), then they're above the obstacle.
    # V-rack can push DOWN (extend), not UP. Can't push targets UP using V-rack extension.

    # V-rack SHRINK pushes remaining segs UP. But that removes segs, doesn't help.

    # Use H-rack to push 9-targets? H-rack at y=26 with seg at x=35: can't reach.

    # What if we just try running the engine with different strategies and see scores?
    pass

def brute_phase():
    """Try all orderings of basic strategies."""
    import random
    random.seed(123)

    best_score = 0
    best_path = None

    for trial in range(100000):
        g = make()
        path = []
        score = 0

        # Random strategy
        for step in range(50):
            # Decide: H-rack or V-rack action
            if random.random() < 0.3:
                # Switch
                switch_rack(g)
                path.append('S')
            else:
                # Weighted random action
                rk = get_active_name(g)
                if rk == 'H':
                    # Bias toward R (extend) and D (move down)
                    weights = [1, 3, 1, 4]  # U D L R
                else:
                    # V-rack: bias toward D (extend) and R (move right)
                    weights = [1, 4, 1, 3]  # U D L R
                actions = [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4]
                import random as r2
                idx = r2.choices(range(4), weights=weights, k=1)[0]
                act(g, actions[idx])
                path.append(rk + ['U','D','L','R'][idx])

            if g.qiercdohl <= 0:
                break

            g.gvtmoopqgy()
            if g.lgdrixfno >= 0:
                print(f"\n*** WIN trial {trial}, {len(path)} actions: {' '.join(path)} ***")
                return path

        g.gvtmoopqgy()
        sc = sum(1 for r,ref in g.xpmcmtbcv.items()
                 for i in range(min(len(g.vjfbwggsd[r]), len(g.vjfbwggsd[ref])))
                 if g.vjfbwggsd[r][i].pixels[1,1] == g.vjfbwggsd[ref][i].pixels[1,1])

        if sc > best_score:
            best_score = sc
            best_path = path[:]
            print(f"Trial {trial}: NEW BEST score={sc} path={' '.join(path[:20])}...")

        if trial % 10000 == 0 and trial > 0:
            print(f"Trial {trial}: best={best_score}")

    return best_path


if __name__ == "__main__":
    print("SK48 L6 Guided Search")

    print("\n=== Strategy 2 (phased) ===")
    won, path = strategy_2()
    if won:
        print("SOLVED!")
    else:
        print("\n=== Brute force with bias ===")
        brute_phase()
