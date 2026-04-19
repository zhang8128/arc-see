"""Interactive engine-play runner for L9. Pass a click sequence, get full per-click state.

Usage: edit PLAN at the bottom, run. Each click shows full sprite state.
"""
import importlib.util, json, sys
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('su15', 'environment_files/su15/4c352900/su15.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

with open('solutions/su15_solutions.json') as f:
    sols = json.load(f)


def at_l9():
    g = mod.Su15()
    for prev in range(8):
        for (cx, cy) in sols[str(prev)]:
            g.perform_action(ActionInput(id=GameAction.ACTION6, data={'x': cx, 'y': cy}))
    assert g._current_level_index == 8
    return g


def snapshot(g):
    lvl = g.current_level
    fruits = []
    for s in lvl.get_sprites_by_tag('fruit'):
        try:
            k = int(s.name)
        except ValueError:
            k = -1
        fruits.append((k, s.x, s.y, s.width))
    enemies = []
    all_tags = lvl.get_all_tags()
    for tag, ek in (('enemy', 1), ('enemy2', 2), ('enemy3', 3)):
        if tag not in all_tags:
            continue
        for s in lvl.get_sprites_by_tag(tag):
            enemies.append((ek, s.x, s.y))
    return fruits, enemies


def fmt_state(g):
    fruits, enemies = snapshot(g)
    fs = " ".join(f"F{k}@({x},{y})" for k, x, y, _ in sorted(fruits))
    es = " ".join(f"E{k}@({x},{y})" for k, x, y in sorted(enemies))
    return f"[{fs}] [{es}]"


def goal_status(g):
    """Check which spec targets are in-goal."""
    lvl = g.current_level
    goals = [(s.x, s.y, s.width, s.height) for s in lvl.get_sprites_by_tag('goal')]
    fruits, enemies = snapshot(g)
    f_counts = {}
    for k, x, y, w in fruits:
        cx, cy = x + w // 2, y + w // 2
        for gx, gy, gw, gh in goals:
            if gx <= cx < gx + gw and gy <= cy < gy + gh:
                f_counts[k] = f_counts.get(k, 0) + 1
                break
    e_counts = {}
    for k, x, y in enemies:
        cx, cy = x + 5 // 2, y + 4 // 2
        for gx, gy, gw, gh in goals:
            if gx <= cx < gx + gw and gy <= cy < gy + gh:
                e_counts[k] = e_counts.get(k, 0) + 1
                break
    # Spec: [[4,1], ['enemy3',1], [2,1]]
    need_f4 = 1 - f_counts.get(4, 0)
    need_f2 = 1 - f_counts.get(2, 0)
    need_e3 = 1 - e_counts.get(3, 0)
    parts = []
    if need_f4 > 0: parts.append(f"need F4:{need_f4}")
    if need_f2 > 0: parts.append(f"need F2:{need_f2}")
    if need_e3 > 0: parts.append(f"need E3:{need_e3}")
    if not parts:
        return "ALL MET"
    return " ".join(parts)


def run_plan(plan, label):
    print(f"\n{'=' * 70}\n{label}\n{'=' * 70}")
    g = at_l9()
    print(f"  start: {fmt_state(g)}  {goal_status(g)}")
    for i, (cx, cy) in enumerate(plan):
        g.perform_action(ActionInput(id=GameAction.ACTION6, data={'x': cx, 'y': cy}))
        state_name = g._state.name
        level_now = g._current_level_index
        advanced = level_now > 8
        print(f"  {i+1:2d}. ({cx:2d},{cy:2d}) → {fmt_state(g)}  {goal_status(g)}")
        if advanced:
            print(f"      🏆 LEVEL COMPLETE in {i+1} clicks")
            return i + 1
        if state_name == 'GAME_OVER':
            print(f"      ❌ GAME OVER")
            return None
    print(f"  ended without win")
    return None


# =============================================================================
# Plan B: merge enemies FIRST (before fruits scatter them), then merge fruits
# =============================================================================
PLAN_B = [
    (16, 14),  # enemy merge left pair → kind-2 enemy at (14, 12)
    (52, 15),  # vacuum top-right enemy toward lower-right
    (52, 25),  # vacuum it further (chaining)
    (52, 35),  # bring bottom-right enemy into range too
    (52, 30),  # try to merge right pair
]
run_plan(PLAN_B, "Plan B: enemy-first, merge left then try right via chain")

# =============================================================================
# Plan C: probe kind-5 fruit downgrade — does anything downgrade it?
#   Try direct enemy collision, repeated enemy hits, etc.
# =============================================================================
PLAN_C = [
    # Leave everything alone for several clicks so enemies chase into fruits
    (0, 30),   # no-op click (far from anything)
    (0, 30),
    (0, 30),
    (0, 30),
    (0, 30),
    (0, 30),
    (0, 30),
    (0, 30),
]
run_plan(PLAN_C, "Plan C: no-op clicks to observe natural enemy chase evolution")

# =============================================================================
# Plan D: merge kind-1 fruits into goal 3 in TWO clicks
# =============================================================================
PLAN_D = [
    (17, 54),  # merge fruits → kind-2 at (16, 53) center (17, 54)
    (11, 54),  # vacuum kind-2 fruit left into goal 3 (7-15, 51-59)
]
run_plan(PLAN_D, "Plan D: get kind-2 fruit into goal 3")

# =============================================================================
# Plan E: does kind-5 in a goal fulfill the F4 requirement?
#   Vacuum kind-5 fruit toward goal 1 (7-15, 37-45) via chained clicks.
# =============================================================================
PLAN_E = [
    # kind-5 at (35, 48), center (38, 51). Vacuum it leftward and up toward (11, 41).
    (33, 48),  # in range of kind-5 center (38,51), dist √25+9=5.8
    (28, 45),  # continue pulling up-left
    (22, 42),
    (16, 41),
    (11, 41),  # center of goal 1
]
run_plan(PLAN_E, "Plan E: vacuum kind-5 toward goal 1, test if F5 fulfills F4")

# =============================================================================
# Plan F: force many enemy-fruit collisions on kind-5 — does kind ever decrease?
# =============================================================================
PLAN_F = [
    (17, 54),  # merge fruits so only kind-5 remains as chase target for all enemies
] + [(0, 30)] * 25  # many no-ops — watch for kind-3 emergence
run_plan(PLAN_F, "Plan F: flood kind-5 with enemy collisions")

# =============================================================================
# Plan G: does a kind-5 fruit in a goal satisfy the F4 requirement?
#   Chain-vacuum the kind-5 fruit into goal 3.
# =============================================================================
PLAN_G = [
    # Fruit center (38, 51). Vacuum radius ~7. Click must be within 7 of center.
    # Step 1: click at (31, 51) — max distance left, still in range (dist 7)
    (31, 51),  # fruit arrives at (31, 51) → pos (28, 48)
    (24, 51),  # continue leftward (new center ~(31, 51))
    (17, 51),
    (11, 54),  # drop into goal 3 (center 11, 55)
]
run_plan(PLAN_G, "Plan G: chain-vacuum kind-5 into goal 3, test F5→F4 acceptance")

# =============================================================================
# Plan H: chain-vacuum kind-5 fruit directly into goal 3, isolated
# =============================================================================
PLAN_H = [
    (32, 51),  # kind-5 center (38,51) → center dist 6, vacuum works
    (26, 51),
    (20, 51),
    (14, 51),
    (11, 55),  # center of goal 3
]
run_plan(PLAN_H, "Plan H: kind-5 → goal 3, does it satisfy F4?")

# =============================================================================
# Plan I: combine everything. Get F2 and F5-as-F4 and F3-enemy all into goals.
# =============================================================================
# Step 1: deliver kind-2 fruit to goal 3 (Plan D, 2 clicks)
# Step 2: deliver kind-5 fruit to a DIFFERENT goal (so it's not overlapping)
# Step 3: let enemies merge passively
PLAN_I = [
    (24, 51),  # merge kind-1 fruits → kind-2 at (23, 50)
    (11, 54),  # kind-2 into goal 3 — 2 clicks done
    (38, 51),  # click on kind-5 fruit (no-op on it, let enemies chase)
] + [(0, 30)] * 10  # let enemies build up
run_plan(PLAN_I, "Plan I: F2 to goal then wait for enemy merge")

# =============================================================================
# Plan J: does F5 physically inside a goal satisfy the F4 requirement?
#   Take a click sequence that aggressively moves F5 into goal 3.
# =============================================================================
PLAN_J = [
    (32, 51),  # pull F5 left
    (17, 54),  # merge kind-1 fruits simultaneously so they stop being enemy targets
    (24, 51),  # left
    (18, 51),  # left more
    (12, 51),  # into goal 3 x range
    (11, 55),  # center in goal 3
]
run_plan(PLAN_J, "Plan J: F5 into goal 3")

# =============================================================================
# Plan K: what if we vacuum kind-1 fruit onto kind-5 fruit? mixed-kind merge?
# =============================================================================
PLAN_K = [
    (35, 48),  # click directly on F5 — does anything happen to it?
    (29, 49),  # click between F1@(23,52) and F5@(35,48)
    (31, 50),  # click so F1 gets pulled toward F5
]
run_plan(PLAN_K, "Plan K: mixed fruit vacuum experiments")

# =============================================================================
# Plan L: probe the 'dawnpfnkpy' (0,5,12,4) and 'wmivicdntp' (1,1,22,2) sprites
# =============================================================================
PLAN_L = [
    (6, 7),    # click on dawnpfnkpy center
    (12, 2),   # click on wmivicdntp center
    (40, 4),   # click on tixakbqato (the top strip)
]
run_plan(PLAN_L, "Plan L: probe header sprites")

# =============================================================================
# Plan M: pure F5-into-goal test with PROPER click chaining
# Track F5 center as it moves; each click must be within 6 of current center.
# =============================================================================
PLAN_M = [
    (32, 51),  # F5 center (38,51) → arrives (32, 51), pos (29, 48)
    (26, 51),  # → arrives (26, 51), pos (23, 48)
    (20, 51),  # → arrives (20, 51), pos (17, 48)
    (14, 51),  # → arrives (14, 51), pos (11, 48)  center still y=48
    (11, 54),  # → arrives (11, 54), pos (8, 51). center (11, 54) IN goal 3!
]
run_plan(PLAN_M, "Plan M: chain-vacuum F5 → goal 3 center, CHECK F4 STATUS")

# =============================================================================
# Plan N: after F5 in goal, check if placing F2 then waiting wins
# =============================================================================
PLAN_N = [
    (32, 51),  # F5 vacuum
    (26, 51),
    (20, 51),
    (14, 51),
    (11, 54),  # F5 arrives in goal 3
    # Now F1 fruits are still at original positions (vacuumed once but let's see)
    # Actually they may have moved due to vacuum. Let's check then merge.
    (24, 51),  # try to pull F1 fruits together
] + [(0, 30)] * 15  # wait for enemy chain
run_plan(PLAN_N, "Plan N: F5 in goal + wait for enemy merge")
