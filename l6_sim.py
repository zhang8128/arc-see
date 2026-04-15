"""L6 simulator for BFS search.

Differences from L5:
- Red piece (fozwvlovdui_red) at (2, 2) — separate from regular pieces
- L6 wins with foz count == 2 (special case for levels 6-7)
- Additional win trigger: chain dest (16, 2) with non-red piece AND red at (6, 6)
- Grid extends to col ~27 (larger than L5)
- All 3 vehicles are plain (no carried dgx) — v3 at `?` cell
"""
from dataclasses import dataclass, field
from typing import Tuple, Optional, List, FrozenSet

# L6 static sprites (from engine dump)
STATIC_SPRITES = {
    # Panel A (top-left)
    **{(x, 1): ['hupkpseyuim'] for x in range(1, 5)},
    **{(x, 2): ['hupkpseyuim'] for x in [1, 3, 4]},
    **{(x, 3): ['hupkpseyuim'] for x in [1, 3, 4]},
    **{(x, 4): ['hupkpseyuim'] for x in range(1, 5)},
    **{(x, 5): ['hupkpseyuim'] for x in range(1, 7)},
    **{(x, 6): ['hupkpseyuim'] for x in range(1, 7)},
    **{(x, 7): ['hupkpseyuim'] for x in range(1, 7)},
    # piece positions (static panel under them)
    (2, 2): ['hupkpseyuim'],  # red piece here, static panel
    (2, 3): ['hupkpseyuim'],
    (3, 8): ['hupkpseyuim'],
    (1, 7): ['hupkpseyuim'],
    # Panel B (mid)
    **{(x, 1): ['hupkpseyuim'] for x in range(14, 18)},
    **{(x, 2): ['hupkpseyuim'] for x in [14, 15, 16, 17]},
    **{(x, 3): ['hupkpseyuim'] for x in [15, 16]},
    (14, 3): ['hupkpseyuim', 'dgxfozncuiz'],
    (17, 3): ['hupkpseyuim', 'dgxfozncuiz'],
    # Track on col 14 (between panel B and t-junction)
    (14, 4): ['kraubslpehi-up'],
    (14, 5): ['kraubslpehi-up'],
    # Track col 17
    (17, 4): ['kraubslpehi-up'],
    (17, 5): ['kraubslpehi-up'],
    # Track row 6 (main horizontal)
    (7, 6): ['kraubslpehi'],   # , cell
    (8, 6): ['kraubslpehi'],   # , cell
    **{(x, 6): ['kraubslpehi'] for x in range(9, 14)},
    (14, 6): ['kraubslpehi-t'],
    (15, 6): ['kraubslpehi'],
    (16, 6): ['kraubslpehi'],
    (17, 6): ['kraubslpehi-3'],
    # Panel C (top-right)
    **{(x, 2): ['hupkpseyuim'] for x in range(18, 25)},
    (25, 2): ['kraubslpehi->'],
    (26, 2): ['hupkpseyuim'],
    (22, 4): ['hupkpseyuim'],
    (23, 4): ['kraubslpehi-up'],   # ? cell
    (24, 4): ['hupkpseyuim'],
    (25, 4): ['kraubslpehi-up'],
    (26, 4): ['hupkpseyuim'],
    (22, 5): ['hupkpseyuim'],
    (23, 5): ['kraubslpehi-up'],
    (25, 5): ['kraubslpehi-up'],
    (23, 3): ['hupkpseyuim', 'dgxfozncuiz'],
    (25, 3): ['kraubslpehi-up'],
    (26, 3): ['hupkpseyuim'],
    # Track B (col 23, 25, row 6 on right)
    (20, 6): ['hupkpseyuim'],
    (21, 6): ['hupkpseyuim'],
    (22, 6): ['hupkpseyuim'],
    (23, 6): ['kraubslpehi-L'],
    (24, 6): ['kraubslpehi'],
    (25, 6): ['kraubslpehi-3'],
    # Panel D (bottom-right)
    (20, 7): ['hupkpseyuim'],
    (20, 8): ['hupkpseyuim'],
}

# Vehicles: (x, y, has_dgx)
INIT_VEHICLES = [
    (7, 6, False),   # v1, plain ,
    (8, 6, False),   # v2, plain ,
    (23, 4, False),  # v3, ? cell (no dgx)
]
# Pieces: (x, y, is_red)
INIT_PIECES = [
    (1, 7, False), (2, 3, False), (3, 8, False), (15, 2, False),
    (20, 7, False), (22, 5, False), (26, 3, False),
    (2, 2, True),  # red piece
]


@dataclass(frozen=True)
class State:
    vehicles: Tuple[Tuple[int, int, bool, Optional[Tuple[int, int, bool]]], ...]  # (x, y, has_dgx, (orig_pos, is_red))
    pieces: FrozenSet[Tuple[int, int, bool]]  # (x, y, is_red)

    def get_sprites_at(self, x: int, y: int) -> List[str]:
        sprites = list(STATIC_SPRITES.get((x, y), []))
        for (vx, vy, has_dgx, loaded) in self.vehicles:
            if vx == x and vy == y:
                sprites.append('hupkpseyuim2')
                if has_dgx:
                    sprites.append('dgxfozncuiz')
                if loaded is not None:
                    sprites.append('fozwvlovdui_red' if loaded[2] else 'fozwvlovdui')
        for (px, py, is_red) in self.pieces:
            if px == x and py == y:
                sprites.append('fozwvlovdui_red' if is_red else 'fozwvlovdui')
        return sprites

    def foz_count(self) -> int:
        return len(self.pieces) + sum(1 for (_, _, _, loaded) in self.vehicles if loaded is not None)

    def is_won(self) -> bool:
        # L6 wins at foz count == 2 OR chain dest specific (handled elsewhere)
        return self.foz_count() == 2

    def red_piece_pos(self) -> Optional[Tuple[int, int]]:
        for (px, py, is_red) in self.pieces:
            if is_red:
                return (px, py)
        for (vx, vy, _, loaded) in self.vehicles:
            if loaded is not None and loaded[2]:
                return (vx, vy)
        return None


def has_pivot_piece_or_dgx(sprites: List[str]) -> bool:
    return any('fozwvlovdui' in s or 'dgxfozncuiz' in s for s in sprites)


def is_valid_dest(sprites: List[str]) -> bool:
    return (len(sprites) == 1 and 'hupkpseyuim' in sprites[0]) or \
           (len(sprites) == 2 and 'hupkpseyuim2' in sprites)


def initial_state() -> State:
    return State(
        vehicles=tuple((x, y, has_dgx, None) for x, y, has_dgx in INIT_VEHICLES),
        pieces=frozenset(INIT_PIECES)
    )


def move_vehicles(state: State, dx: int, dy: int) -> State:
    vehicles = list(state.vehicles)
    if dx < 0:
        order = sorted(range(len(vehicles)), key=lambda i: vehicles[i][0])
    elif dx > 0:
        order = sorted(range(len(vehicles)), key=lambda i: -vehicles[i][0])
    elif dy < 0:
        order = sorted(range(len(vehicles)), key=lambda i: vehicles[i][1])
    else:
        order = sorted(range(len(vehicles)), key=lambda i: -vehicles[i][1])

    new_vehicles = list(vehicles)
    for idx in order:
        vx, vy, has_dgx, loaded = new_vehicles[idx]
        tx, ty = vx + dx, vy + dy
        static = STATIC_SPRITES.get((tx, ty), [])
        has_track = any('kraubslpehi' in s for s in static)
        other_at_target = any(
            (nv_x, nv_y) == (tx, ty) for i, (nv_x, nv_y, _, _) in enumerate(new_vehicles) if i != idx
        )
        if has_track and not other_at_target:
            new_vehicles[idx] = (tx, ty, has_dgx, loaded)
    return State(vehicles=tuple(new_vehicles), pieces=state.pieces)


def try_chain(state: State, src: Tuple[int, int], direction: Tuple[int, int]) -> Optional[State]:
    px, py = src
    dx, dy = direction
    pivot = (px + dx, py + dy)
    dest = (px + 2*dx, py + 2*dy)

    # Find source
    piece_here = None
    for p in state.pieces:
        if p[:2] == (px, py):
            piece_here = p
            break
    vehicle_idx = None
    if piece_here is None:
        for i, (vx, vy, _, loaded) in enumerate(state.vehicles):
            if vx == px and vy == py and loaded is not None:
                vehicle_idx = i
                break
    if piece_here is None and vehicle_idx is None:
        return None

    # Check pivot
    pivot_sprites = state.get_sprites_at(*pivot)
    if not has_pivot_piece_or_dgx(pivot_sprites):
        return None

    # Check dest
    dest_sprites = state.get_sprites_at(*dest)
    if not is_valid_dest(dest_sprites):
        return None

    # Execute
    new_pieces = set(state.pieces)
    new_vehicles = list(state.vehicles)

    is_red_source = False
    if piece_here is not None:
        new_pieces.remove(piece_here)
        is_red_source = piece_here[2]
    else:
        vx, vy, has_dgx, loaded = new_vehicles[vehicle_idx]
        is_red_source = loaded[2]
        new_vehicles[vehicle_idx] = (vx, vy, has_dgx, None)

    # Consume pivot if it's a piece with SAME color (fozwvlovdui = fozwvlovdui, red = red)
    pivot_piece = None
    for p in new_pieces:
        if p[:2] == pivot:
            pivot_piece = p
            break
    # Source name: 'fozwvlovdui_red' if is_red_source else 'fozwvlovdui'
    # Pivot gets consumed only if same name
    if pivot_piece is not None and pivot_piece[2] == is_red_source:
        new_pieces.remove(pivot_piece)
    # (Carried pivots in vehicles — rare, skip for now)

    # Place source at dest
    dest_vehicle_idx = None
    for i, (vx, vy, _, _) in enumerate(new_vehicles):
        if (vx, vy) == dest:
            dest_vehicle_idx = i
            break
    if dest_vehicle_idx is not None:
        vx, vy, has_dgx, loaded = new_vehicles[dest_vehicle_idx]
        if loaded is not None:
            return None
        new_vehicles[dest_vehicle_idx] = (vx, vy, has_dgx, (px, py, is_red_source))
    else:
        new_pieces.add((dest[0], dest[1], is_red_source))

    return State(vehicles=tuple(new_vehicles), pieces=frozenset(new_pieces))


def all_chains(state: State):
    positions = [p[:2] for p in state.pieces] + [(vx, vy) for (vx, vy, _, loaded) in state.vehicles if loaded is not None]
    for src in positions:
        for direction in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            ns = try_chain(state, src, direction)
            if ns is not None:
                yield src, direction, ns


def next_states(state: State):
    for a, (dx, dy) in [(1, (0, -1)), (2, (0, 1)), (3, (-1, 0)), (4, (1, 0))]:
        ns = move_vehicles(state, dx, dy)
        if ns != state:
            yield f'A{a}', ns
    for src, direction, ns in all_chains(state):
        dname = {(0, -1): 'U', (0, 1): 'D', (-1, 0): 'L', (1, 0): 'R'}[direction]
        yield f'C{src}{dname}', ns


def bfs(max_depth: int = 80, verbose_best: bool = True):
    start = initial_state()
    print(f'INITIAL: foz={start.foz_count()}, pieces={sorted(start.pieces)}, vehicles={start.vehicles}')

    visited = {start: []}
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
                if foz == 2:
                    # Check if red piece is at (6, 6) OR any state with foz==2 is a win
                    # For L6, win at foz==2 is the default
                    print(f'\nWIN candidate (foz=2)! Depth {len(new_path)}: {" ".join(new_path)}')
                    return new_path
                new_queue.append((ns, new_path))
        queue = new_queue
    print(f'BFS exhausted. best_foz={best_foz}. Visited {len(visited)} states.')
    return best_path


if __name__ == '__main__':
    bfs(max_depth=80)
