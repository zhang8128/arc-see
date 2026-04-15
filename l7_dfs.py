"""L7 DFS with iterative deepening + chain priority.

Strategy: since foz=3 and target=2 (only 1 merge), prioritize chains over A-actions.
Also prune: limit consecutive A-actions of same type.
"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
from l7_sim import State, initial_state, move_vehicles, try_chain, all_chains, STATIC_SPRITES


def dfs_iddfs(max_depth=35):
    start = initial_state()
    target_foz = 2

    for depth_limit in range(10, max_depth + 1):
        print(f'\n=== IDDFS depth {depth_limit} ===', flush=True)
        visited = {start: 0}
        stack = [(start, [], set())]
        best_foz = start.foz_count()
        counter = [0]
        found = [None]

        def dfs(state, path, recent_actions):
            counter[0] += 1
            if counter[0] % 500000 == 0:
                print(f'  explored {counter[0]}, depth {len(path)}, best foz {best_foz}', flush=True)
            foz = state.foz_count()
            if foz == target_foz:
                found[0] = path
                return True
            if len(path) >= depth_limit:
                return False

            # Gen moves
            actions = []
            # Prefer chains
            chain_moves = []
            for src, direction, ns in all_chains(state):
                dname = {(0, -1): 'U', (0, 1): 'D', (-1, 0): 'L', (1, 0): 'R'}[direction]
                chain_moves.append((f'C{src}{dname}', ns))
            # A-actions
            a_moves = []
            for a, (dx, dy) in [(3, (-1, 0)), (4, (1, 0)), (1, (0, -1)), (2, (0, 1))]:
                ns = move_vehicles(state, dx, dy)
                if ns != state:
                    a_moves.append((f'A{a}', ns))

            # Limit consecutive same A-actions
            moves = chain_moves + a_moves
            for action, ns in moves:
                if action.startswith('A'):
                    # Check last 3 actions — if all same, skip
                    last_three = path[-3:] if len(path) >= 3 else []
                    if len(last_three) == 3 and all(x == action for x in last_three):
                        continue
                if ns in visited and visited[ns] <= len(path) + 1:
                    continue
                visited[ns] = len(path) + 1
                path.append(action)
                if dfs(ns, path, recent_actions):
                    return True
                path.pop()
            return False

        result = dfs(start, [], set())
        if result:
            print(f'\nWIN found at depth {depth_limit}: {len(found[0])} actions')
            print(' '.join(found[0]))
            return found[0]
        print(f'  No solution at depth {depth_limit}. Visited {len(visited)}.', flush=True)
    return None


if __name__ == '__main__':
    dfs_iddfs(max_depth=30)
