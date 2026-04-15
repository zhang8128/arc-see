"""L5 simulator for BFS search.

Models:
- Grid cells with fixed sprites (kraubslpehi variants, hupkpseyuim panels, dgxfozncuiz pivots)
- Vehicles (hupkpseyuim2) as mobile objects, possibly carrying dgxfozncuiz or fozwvlovdui
- Pieces (fozwvlovdui) as primary game objects to reduce

Actions: A1-A4 (move vehicles), chain (click piece + click dest).
Win: foz count == 1.
"""
from dataclasses import dataclass, field
from typing import Tuple, Optional, List, Set, FrozenSet, Dict
import sys
from copy import deepcopy

# Static grid of L5 (from engine dump)
# Each cell: list of static sprite names. Mobile sprites (hupk2, dgx from P, foz) tracked separately.
STATIC_SPRITES = {
    # Row 0
    (1, 0): ['kraubslpehi'],
    (2, 0): ['kraubslpehi'],  # , cell has kraubslpehi too (static); hupkpseyuim2 is mobile
    (3, 0): ['kraubslpehi'],
    (4, 0): ['kraubslpehi-T'],
    (5, 0): ['kraubslpehi'],
    (6, 0): ['kraubslpehi'],  # P cell; dgx and hupkpseyuim2 are mobile
    (7, 0): ['kraubslpehi'],
    (14, 0): ['hupkpseyuim'],
    (15, 0): ['hupkpseyuim'],
    (16, 0): ['hupkpseyuim', 'dgxfozncuiz'],  # static pivot
    (17, 0): ['hupkpseyuim'],
    (18, 0): ['hupkpseyuim'],
    # Row 1
    (4, 1): ['kraubslpehi-up'],
    (13, 1): ['kraubslpehi-<'],
    (14, 1): ['kraubslpehi'],
    (15, 1): ['kraubslpehi'],
    (16, 1): ['kraubslpehi'],
    (17, 1): ['kraubslpehi-T'],
    (18, 1): ['kraubslpehi'],
    (19, 1): ['kraubslpehi'],  # P cell has kraubslpehi (static); dgx/hupk2 mobile
    (20, 1): ['kraubslpehi->'],
    # Row 2
    (1, 2): ['hupkpseyuim'],
    (2, 2): ['hupkpseyuim'],
    (3, 2): ['hupkpseyuim'],
    (4, 2): ['kraubslpehi-up'],
    (7, 2): ['kraubslpehi-<'],
    (8, 2): ['kraubslpehi'],
    (9, 2): ['kraubslpehi'],
    (10, 2): ['kraubslpehi->'],
    (12, 2): ['hupkpseyuim'],
    (13, 2): ['kraubslpehi-up'],
    (14, 2): ['hupkpseyuim'],
    (15, 2): ['hupkpseyuim'],
    (16, 2): ['hupkpseyuim'],
    (17, 2): ['kraubslpehi-up'],
    (18, 2): ['hupkpseyuim'],
    (20, 2): ['kraubslpehi-up'],
    # Row 3
    (2, 3): ['hupkpseyuim', 'dgxfozncuiz'],  # static pivot
    (3, 3): ['hupkpseyuim'],
    (4, 3): ['kraubslpehi-up'],
    (5, 3): ['hupkpseyuim'],
    (7, 3): ['kraubslpehi-up'],
    (10, 3): ['kraubslpehi-L'],
    (12, 3): ['hupkpseyuim'],
    (13, 3): ['kraubslpehi-up'],
    (14, 3): ['hupkpseyuim'],
    (15, 3): ['hupkpseyuim', 'dgxfozncuiz'],  # static pivot
    (16, 3): ['hupkpseyuim'],
    (17, 3): ['kraubslpehi-up'],
    (18, 3): ['hupkpseyuim'],
    (19, 3): ['hupkpseyuim'],
    (20, 3): ['kraubslpehi-up'],
    # Row 4
    (1, 4): ['hupkpseyuim'],
    (2, 4): ['hupkpseyuim'],
    (3, 4): ['hupkpseyuim'],
    (4, 4): ['kraubslpehi-up'],
    (7, 4): ['kraubslpehi-up'],
    (12, 4): ['hupkpseyuim'],
    (13, 4): ['kraubslpehi-up'],
    (14, 4): ['hupkpseyuim'],
    (15, 4): ['hupkpseyuim'],
    (16, 4): ['hupkpseyuim', 'dgxfozncuiz'],  # static pivot
    (17, 4): ['kraubslpehi-up'],
    (19, 4): ['hupkpseyuim'],
    (20, 4): ['kraubslpehi-up'],
    # Row 5
    (4, 5): ['kraubslpehi-up'],
    (7, 5): ['kraubslpehi-up'],
    (13, 5): ['kraubslpehi-L'],
    (14, 5): ['kraubslpehi'],
    (15, 5): ['kraubslpehi'],
    (16, 5): ['kraubslpehi'],
    (17, 5): ['kraubslpehi-t'],
    (18, 5): ['kraubslpehi'],
    (19, 5): ['kraubslpehi'],
    (20, 5): ['kraubslpehi-3'],
    # Row 6
    (2, 6): ['kraubslpehi-<'],
    (3, 6): ['kraubslpehi'],
    (4, 6): ['kraubslpehi-t'],
    (5, 6): ['kraubslpehi'],
    (6, 6): ['kraubslpehi'],
    (7, 6): ['kraubslpehi-3'],
    (15, 6): ['hupkpseyuim'],
    # Row 7
    (2, 7): ['kraubslpehi-up'],
    (15, 7): ['hupkpseyuim', 'dgxfozncuiz'],  # static pivot
    # Row 8
    (2, 8): ['kraubslpehi-up'],
    (14, 8): ['hupkpseyuim'],
    (15, 8): ['hupkpseyuim'],
}

# Initial mobile sprites
# Vehicles: (x, y, has_dgx) — has_dgx True for P-cell vehicles
INIT_VEHICLES = [
    (2, 0, False),   # v1 at ,
    (6, 0, True),    # v2 at P with dgx
    (19, 1, True),   # v3 at P with dgx
]
INIT_PIECES = [(1, 3), (6, 3), (11, 3), (16, 8), (18, 4), (19, 0)]


def has_kraub(sprites: List[str]) -> bool:
    return any('kraubslpehi' in s for s in sprites)

def has_pivot_piece_or_dgx(sprites: List[str]) -> bool:
    return any('fozwvlovdui' in s or 'dgxfozncuiz' in s for s in sprites)

def is_valid_dest(sprites: List[str]) -> bool:
    """posalhhmjq check."""
    return (len(sprites) == 1 and 'hupkpseyuim' in sprites[0]) or \
           (len(sprites) == 2 and 'hupkpseyuim2' in sprites)


@dataclass(frozen=True)
class State:
    vehicles: Tuple[Tuple[int, int, bool, Optional[Tuple[int, int]]], ...]  # (x, y, has_dgx, loaded_piece_orig_pos)
    pieces: FrozenSet[Tuple[int, int]]  # positions of uncarried pieces
    # Note: carried pieces are in vehicles tuple

    def get_sprites_at(self, x: int, y: int) -> List[str]:
        """Static + dynamic sprites at (x, y)."""
        sprites = list(STATIC_SPRITES.get((x, y), []))
        for (vx, vy, has_dgx, loaded) in self.vehicles:
            if vx == x and vy == y:
                sprites.append('hupkpseyuim2')
                if has_dgx:
                    sprites.append('dgxfozncuiz')
                if loaded is not None:
                    sprites.append('fozwvlovdui')
        if (x, y) in self.pieces:
            sprites.append('fozwvlovdui')
        return sprites

    def foz_count(self) -> int:
        # uncarried pieces + carried (loaded) pieces
        return len(self.pieces) + sum(1 for (_, _, _, loaded) in self.vehicles if loaded is not None)

    def __hash__(self):
        # Tuple-based hashing
        return hash((self.vehicles, tuple(sorted(self.pieces))))


def initial_state() -> State:
    return State(
        vehicles=tuple((x, y, has_dgx, None) for x, y, has_dgx in INIT_VEHICLES),
        pieces=frozenset(INIT_PIECES)
    )


def move_vehicles(state: State, dx: int, dy: int) -> State:
    """Apply A-action: move each vehicle by (dx, dy) if target is track."""
    vehicles = list(state.vehicles)
    # Sort: for A3 (dx=-1), sort by x asc (leftmost first). For A4 (dx=1), sort by x desc.
    # For A2 (dy=1), sort by y desc (bottom first). For A1 (dy=-1), sort by y asc.
    if dx < 0:
        order = sorted(range(len(vehicles)), key=lambda i: vehicles[i][0])
    elif dx > 0:
        order = sorted(range(len(vehicles)), key=lambda i: -vehicles[i][0])
    elif dy < 0:
        order = sorted(range(len(vehicles)), key=lambda i: vehicles[i][1])
    else:
        order = sorted(range(len(vehicles)), key=lambda i: -vehicles[i][1])

    # New positions
    new_vehicles = list(vehicles)
    for idx in order:
        vx, vy, has_dgx, loaded = new_vehicles[idx]
        tx, ty = vx + dx, vy + dy
        # Target cell sprites (without the moving vehicle)
        static = STATIC_SPRITES.get((tx, ty), [])
        has_track = any('kraubslpehi' in s for s in static)
        # Also check if any OTHER vehicle occupies target
        other_vehicle_at_target = any(
            (nv_x, nv_y) == (tx, ty) for i, (nv_x, nv_y, _, _) in enumerate(new_vehicles) if i != idx
        )
        if has_track and not other_vehicle_at_target:
            new_vehicles[idx] = (tx, ty, has_dgx, loaded)
    return State(vehicles=tuple(new_vehicles), pieces=state.pieces)


def try_chain(state: State, src: Tuple[int, int], direction: Tuple[int, int]) -> Optional[State]:
    """Try to execute a chain. Returns new state or None if invalid.

    Chain source: a piece position (either uncarried or carried in vehicle).
    Chain direction: cardinal unit vector.
    """
    px, py = src
    dx, dy = direction
    pivot = (px + dx, py + dy)
    dest = (px + 2*dx, py + 2*dy)

    # Check source has a piece (either in pieces set or in a vehicle)
    piece_here = src in state.pieces
    vehicle_with_piece_here = None
    for i, (vx, vy, has_dgx, loaded) in enumerate(state.vehicles):
        if vx == px and vy == py and loaded is not None:
            vehicle_with_piece_here = i

    if not piece_here and vehicle_with_piece_here is None:
        return None

    # Check pivot
    pivot_sprites = state.get_sprites_at(*pivot)
    if not has_pivot_piece_or_dgx(pivot_sprites):
        return None

    # Check dest
    dest_sprites = state.get_sprites_at(*dest)
    if not is_valid_dest(dest_sprites):
        return None

    # Execute chain
    new_pieces = set(state.pieces)
    new_vehicles = list(state.vehicles)

    # Remove source piece from its location
    source_piece_is_piece_at_src = src in new_pieces
    if source_piece_is_piece_at_src:
        new_pieces.remove(src)
    else:
        # Source is loaded in vehicle at (px, py)
        vx, vy, has_dgx, loaded = new_vehicles[vehicle_with_piece_here]
        new_vehicles[vehicle_with_piece_here] = (vx, vy, has_dgx, None)

    # Check for piece consumption at pivot
    consumed_pivot = pivot in new_pieces
    if consumed_pivot:
        new_pieces.remove(pivot)
    # Note: pieces in vehicles as pivots — could also happen but rare. Handle later if needed.

    # Place source piece at dest
    # If dest is a vehicle, piece becomes loaded
    dest_vehicle_idx = None
    for i, (vx, vy, has_dgx, loaded) in enumerate(new_vehicles):
        if vx == dest[0] and vy == dest[1]:
            dest_vehicle_idx = i
            break

    if dest_vehicle_idx is not None:
        # Load into vehicle
        vx, vy, has_dgx, loaded = new_vehicles[dest_vehicle_idx]
        if loaded is not None:
            return None  # vehicle already has piece (shouldn't happen if dest check passed?)
        new_vehicles[dest_vehicle_idx] = (vx, vy, has_dgx, src)
    else:
        new_pieces.add(dest)

    return State(vehicles=tuple(new_vehicles), pieces=frozenset(new_pieces))


def all_chains(state: State):
    """Yield (src, direction, new_state) for all valid chains."""
    # All piece positions (uncarried)
    positions = list(state.pieces) + [(vx, vy) for (vx, vy, _, loaded) in state.vehicles if loaded is not None]
    for src in positions:
        for direction in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            new_state = try_chain(state, src, direction)
            if new_state is not None:
                yield src, direction, new_state


def next_states(state: State):
    """Yield (action_description, new_state) for all possible actions."""
    # A-actions
    for a, (dx, dy) in [(1, (0, -1)), (2, (0, 1)), (3, (-1, 0)), (4, (1, 0))]:
        ns = move_vehicles(state, dx, dy)
        if ns != state:
            yield f'A{a}', ns
    # Chains
    for src, direction, ns in all_chains(state):
        dname = {(0, -1): 'U', (0, 1): 'D', (-1, 0): 'L', (1, 0): 'R'}[direction]
        yield f'C{src}{dname}', ns


def bfs(max_depth: int = 40, verbose_best: bool = True):
    start = initial_state()
    print(f'INITIAL: foz={start.foz_count()}, pieces={sorted(start.pieces)}, vehicles={start.vehicles}')

    visited = {start: []}  # state -> path
    queue = [(start, [])]
    best_foz = start.foz_count()
    best_path = []

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
                    if verbose_best:
                        print(f'Depth {len(new_path)}: foz={foz}')
                        print(f'  path: {" ".join(new_path)}')
                        print(f'  state: v={ns.vehicles}, p={sorted(ns.pieces)}')
                if foz == 1:
                    print(f'\nWIN! Depth {len(new_path)}: {" ".join(new_path)}')
                    return new_path
                new_queue.append((ns, new_path))
        queue = new_queue
        if not queue:
            break
    print(f'BFS exhausted. best_foz={best_foz}. Visited {len(visited)} states.')
    return best_path


if __name__ == '__main__':
    bfs(max_depth=40)
