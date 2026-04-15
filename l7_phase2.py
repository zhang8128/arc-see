"""L7 Phase 2: continue BFS from post-load state."""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
from l7_sim import State, initial_state, move_vehicles, try_chain, next_states, all_chains, STATIC_SPRITES


def setup_post_load():
    s = initial_state()
    # Move vehicles: A3 A3 A1 A1 A3 A3 A3 (7 actions)
    for a, (dx, dy) in [(3, (-1, 0)), (3, (-1, 0)), (1, (0, -1)), (1, (0, -1)), (3, (-1, 0)), (3, (-1, 0)), (3, (-1, 0))]:
        s = move_vehicles(s, dx, dy)
    # Chain piece (0, 1) D: load into v1 at (0, 3)
    for src, direction, ns in all_chains(s):
        if src == (0, 1) and direction == (0, 1):
            s = ns
            break
    return s


def bfs_from(start, target_foz=2, max_depth=30):
    print(f'START: foz={start.foz_count()}, pieces={sorted(start.pieces)}, vehicles={start.vehicles}', flush=True)

    visited = {start: []}
    queue = [(start, [])]
    best_foz = start.foz_count()
    best_path = []
    d = 0

    while queue:
        new_queue = []
        for state, path in queue:
            if len(path) > max_depth:
                continue
            for action, ns in next_states(state):
                if ns in visited:
                    continue
                new_path = path + [action]
                visited[ns] = new_path
                foz = ns.foz_count()
                if foz < best_foz:
                    best_foz = foz
                    best_path = new_path
                    print(f'Depth {len(new_path)}: foz={foz}', flush=True)
                    print(f'  path: {" ".join(new_path)}', flush=True)
                if foz == target_foz:
                    print(f'\nWIN at depth {len(new_path)}: {" ".join(new_path)}', flush=True)
                    return new_path
                new_queue.append((ns, new_path))
        queue = new_queue
        d += 1
        if d % 5 == 0:
            print(f'Depth {d}: visited={len(visited)}, queue={len(queue)}', flush=True)
    print(f'Exhausted. best_foz={best_foz}')
    return best_path


if __name__ == '__main__':
    s = setup_post_load()
    print(f'Phase 1 done (7 + 2 = 9 actions). piece loaded in v1.')
    path_from_here = bfs_from(s, target_foz=2, max_depth=40)
    if path_from_here:
        full_path = ['A3', 'A3', 'A1', 'A1', 'A3', 'A3', 'A3', 'C(0, 1)D'] + path_from_here
        print(f'\nFull solution ({len(full_path)} actions):')
        print(' '.join(full_path))
