"""L7 A* search with heuristic based on piece Manhattan distance + vehicle-relevant positioning.

Heuristic: min distance between regular pieces OR min(dist_to_load_position + dist_to_merge_position).
"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
import heapq
from l7_sim import State, initial_state, move_vehicles, try_chain, next_states, STATIC_SPRITES


def heuristic(state):
    """Lower-bound estimate of actions needed to reach foz=2."""
    foz = state.foz_count()
    if foz <= 2:
        return 0

    # For L7, we need 1 merge of regular pieces.
    # Find positions of regular pieces (in panel or loaded in vehicle)
    regular_positions = []
    for p in state.pieces:
        if not p[2]:
            regular_positions.append(p[:2])
    for (vx, vy, _, loaded) in state.vehicles:
        if loaded is not None and not loaded[2]:
            regular_positions.append((vx, vy))

    if len(regular_positions) < 2:
        return 100  # bad state

    # Min Manhattan distance between any pair
    min_d = float('inf')
    for i in range(len(regular_positions)):
        for j in range(i+1, len(regular_positions)):
            d = abs(regular_positions[i][0] - regular_positions[j][0]) + abs(regular_positions[i][1] - regular_positions[j][1])
            min_d = min(min_d, d)
    # At minimum, we need that many actions to bring pieces together + 1 chain
    return max(1, min_d // 2)


def a_star(max_actions=60):
    start = initial_state()
    target_foz = 2
    print(f'INITIAL: foz={start.foz_count()}, pieces={sorted(start.pieces)}', flush=True)

    # Priority queue: (f, id, state, path)
    counter = 0
    heap = [(heuristic(start), 0, start, [])]
    best_cost = {start: 0}
    best_foz = start.foz_count()
    explored = 0

    while heap:
        f, _, state, path = heapq.heappop(heap)
        g = len(path)
        if g > max_actions:
            continue
        explored += 1
        if explored % 50000 == 0:
            print(f'  explored {explored}, depth {g}, f={f}, best foz {best_foz}', flush=True)

        foz = state.foz_count()
        if foz < best_foz:
            best_foz = foz
            print(f'  New best foz={foz} at depth {g}: {" ".join(path)}', flush=True)
        if foz == target_foz:
            print(f'\nWIN! Depth {g}: {" ".join(path)}')
            return path

        for action, ns in next_states(state):
            new_g = g + 1
            if ns in best_cost and best_cost[ns] <= new_g:
                continue
            best_cost[ns] = new_g
            new_path = path + [action]
            new_f = new_g + heuristic(ns)
            counter += 1
            heapq.heappush(heap, (new_f, counter, ns, new_path))

    print(f'Exhausted. best_foz={best_foz}')
    return None


if __name__ == '__main__':
    a_star(max_actions=60)
