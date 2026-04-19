"""Monte Carlo solver — random search for keyboard games.

For games where BFS is too slow due to large state space,
try random action sequences and keep the best ones.
Uses iterative refinement: start with random, then mutate successful prefixes.
"""
import importlib.util, copy, random, sys, time
from arcengine import GameAction, ActionInput

GAME = sys.argv[1] if len(sys.argv) > 1 else "re86"
GAME_ID = {
    "re86": "re86-4e57566e",
    "wa30": "wa30-ee6fef47",
    "g50t": "g50t-5849a774",
}[GAME]

spec = importlib.util.spec_from_file_location(GAME, f'environment_files/{GAME}/{GAME_ID.split("-")[1]}/{GAME}.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

BASELINES = {
    "re86": [28, 38, 198, 57, 84, 117, 328, 221],
    "wa30": [125, 58, 259, 113, 499, 58, 186, 134, 132],
    "g50t": [51, 175, 86, 52, 96, 48, 67],
}[GAME]

CLS = getattr(mod, GAME.capitalize())

# Detect available actions
test_g = CLS()
test_g.set_level(0)
ACTIONS = []
for i in range(1, 8):
    try:
        a = getattr(GameAction, f"ACTION{i}")
        if i in [a.value for a in [getattr(GameAction, f"ACTION{j}") for j in range(1, 8)]]:
            ACTIONS.append(a)
    except:
        pass
# Use the game's available_actions
ACTIONS = [getattr(GameAction, f"ACTION{i}") for i in test_g._available_actions if i <= 5]
NAMES = {GameAction.ACTION1: "U", GameAction.ACTION2: "D", GameAction.ACTION3: "L",
         GameAction.ACTION4: "R", GameAction.ACTION5: "5"}

print(f"Game: {GAME}, Actions: {len(ACTIONS)}", flush=True)


def try_sequence(level_idx, actions):
    """Try a sequence of actions. Returns (won, length_used)."""
    g = CLS()
    g.set_level(level_idx)
    for i, a in enumerate(actions):
        g.perform_action(ActionInput(id=a))
        if g._current_level_index > level_idx or g._state.name == "WIN":
            return True, i + 1
        if g._state.name == "GAME_OVER":
            return False, i + 1
    return False, len(actions)


def random_search(level_idx, max_len, time_limit=60):
    """Random search with mutations."""
    baseline = BASELINES[level_idx]
    best_prefix = []
    attempts = 0
    start = time.time()

    while time.time() - start < time_limit:
        # Generate random sequence
        if best_prefix and random.random() < 0.3:
            # Mutate: keep prefix, randomize suffix
            prefix_len = random.randint(0, len(best_prefix))
            seq = best_prefix[:prefix_len] + [random.choice(ACTIONS) for _ in range(max_len - prefix_len)]
        else:
            seq = [random.choice(ACTIONS) for _ in range(max_len)]

        won, used = try_sequence(level_idx, seq)
        attempts += 1

        if won:
            names = "".join(NAMES.get(a, "?") for a in seq[:used])
            print(f"  WON! {used} moves ({attempts} attempts, {time.time()-start:.1f}s): {names}", flush=True)
            return seq[:used]

        if attempts % 10000 == 0:
            print(f"  {attempts} attempts, {time.time()-start:.1f}s", flush=True)

    print(f"  No solution ({attempts} attempts, {time_limit}s)", flush=True)
    return None


if __name__ == "__main__":
    all_solutions = {}
    for level in range(len(BASELINES)):
        baseline = BASELINES[level]
        max_len = baseline + 10
        print(f"Level {level+1}: baseline={baseline}, max_len={max_len}", flush=True)

        # Try random search with increasing time limits
        for time_limit in [30, 120, 600]:
            result = random_search(level, max_len, time_limit)
            if result:
                all_solutions[level] = result
                break
        else:
            print(f"  FAILED", flush=True)
            break
        print(flush=True)

    print("=" * 60, flush=True)
    total = sum(len(p) for p in all_solutions.values())
    baseline = sum(BASELINES)
    print(f"Solved {len(all_solutions)}/{len(BASELINES)}, Total: {total}, Baseline: {baseline}", flush=True)
