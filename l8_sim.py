"""L8 simulator — need 1 merge (ddaguepwkt = regular+red count, blue ignored).

L8 has 2 regular pieces and 4 blue pieces. Need to merge the 2 regulars.
Win at (regular + red) == 1.
"""
from dataclasses import dataclass
from typing import Tuple, Optional, List, FrozenSet

STATIC_SPRITES = {
    # Panel top rows 2-8
    **{(x, y): ['hupkpseyuim'] for x in range(1, 9) for y in [2, 3, 4, 5, 6, 7]},
    (2, 3): ['hupkpseyuim', 'dgxfozncuiz'],
    (6, 3): ['hupkpseyuim', 'dgxfozncuiz'],
    (7, 4): ['hupkpseyuim', 'dgxfozncuiz'],
    (2, 5): ['hupkpseyuim', 'dgxfozncuiz'],
    (6, 5): ['hupkpseyuim', 'dgxfozncuiz'],
    # Pieces are separate (not static) — so just panel at those cells
    # Tracks on left col 0
    (0, 5): ['kraubslpehi-<'],
    (0, 6): ['kraubslpehi-up'],
    (0, 7): ['kraubslpehi-up'],
    (0, 8): ['kraubslpehi-up'],
    (0, 9): ['kraubslpehi-L'],
    # Row 5 track (just (0, 5) and (1, 5))
    (1, 5): ['kraubslpehi'],
    # Row 9 track (partial)
    (1, 9): ['kraubslpehi'],
    (2, 9): ['kraubslpehi'],  # vehicle spawn (,)
    (3, 9): ['kraubslpehi->'],
    (7, 9): ['kraubslpehi-<'],
    (8, 9): ['kraubslpehi-3'],
    # Col 8 (8-9)
    (8, 8): ['kraubslpehi-up'],
    # Col 3 row 10
    (3, 10): ['kraubslpehi-up'],
    # Col 7 row 10 (; vehicle spawn)
    (7, 10): ['kraubslpehi-up'],
    # Bottom panel row 11
    **{(x, 11): ['hupkpseyuim'] for x in range(1, 9)},
    # Bottom track row 12
    (1, 12): ['kraubslpehi-L'],
    (2, 12): ['kraubslpehi'],
    (3, 12): ['kraubslpehi'],
    (4, 12): ['kraubslpehi'],  # P
    (5, 12): ['kraubslpehi'],  # ,
    (6, 12): ['kraubslpehi'],  # P
    (7, 12): ['kraubslpehi'],
    (8, 12): ['kraubslpehi-3'],
}

# Vehicles: (x, y, has_dgx)
INIT_VEHICLES = [
    (2, 9, False),    # ,
    (7, 10, False),   # ;
    (4, 12, True),    # P (dgx)
    (5, 12, False),   # ,
    (6, 12, True),    # P (dgx)
]
# Pieces: (x, y, color) where color: 0=regular, 1=red, 2=blue
INIT_PIECES = [
    (1, 3, 0), (8, 7, 0),  # regular
    (4, 6, 2), (4, 7, 2), (7, 11, 2), (8, 11, 2),  # blue
]


@dataclass(frozen=True)
class State:
    vehicles: Tuple[Tuple[int, int, bool, Optional[Tuple[int, int, int]]], ...]  # (x, y, has_dgx, (orig_pos, color))
    pieces: FrozenSet[Tuple[int, int, int]]  # (x, y, color)

    def get_sprites_at(self, x, y):
        sprites = list(STATIC_SPRITES.get((x, y), []))
        for (vx, vy, has_dgx, loaded) in self.vehicles:
            if vx == x and vy == y:
                sprites.append('hupkpseyuim2')
                if has_dgx:
                    sprites.append('dgxfozncuiz')
                if loaded is not None:
                    c = loaded[2]
                    name = {0: 'fozwvlovdui', 1: 'fozwvlovdui_red', 2: 'fozwvlovdui_blue'}[c]
                    sprites.append(name)
        for (px, py, color) in self.pieces:
            if px == x and py == y:
                name = {0: 'fozwvlovdui', 1: 'fozwvlovdui_red', 2: 'fozwvlovdui_blue'}[color]
                sprites.append(name)
        return sprites

    def non_blue_foz_count(self):
        """L8 win metric: regular + red count."""
        count = 0
        for p in self.pieces:
            if p[2] != 2:
                count += 1
        for (_, _, _, loaded) in self.vehicles:
            if loaded is not None and loaded[2] != 2:
                count += 1
        return count


def has_pivot(sprites):
    # pymqmlkgzs: any foz (all colors incl blue) or dgx is valid pivot.
    # Consume (cfilhtifcb) excludes blue, but pivot itself is OK.
    return any('fozwvlovdui' in s or 'dgxfozncuiz' in s for s in sprites)


def is_valid_dest(sprites):
    return (len(sprites) == 1 and 'hupkpseyuim' in sprites[0]) or \
           (len(sprites) == 2 and 'hupkpseyuim2' in sprites)


def initial_state():
    return State(
        vehicles=tuple((x, y, has_dgx, None) for x, y, has_dgx in INIT_VEHICLES),
        pieces=frozenset(INIT_PIECES),
    )


def move_vehicles(state, dx, dy):
    vehicles = list(state.vehicles)
    if dx < 0:
        order = sorted(range(len(vehicles)), key=lambda i: vehicles[i][0])
    elif dx > 0:
        order = sorted(range(len(vehicles)), key=lambda i: -vehicles[i][0])
    elif dy < 0:
        order = sorted(range(len(vehicles)), key=lambda i: vehicles[i][1])
    else:
        order = sorted(range(len(vehicles)), key=lambda i: -vehicles[i][1])

    new = list(vehicles)
    for idx in order:
        vx, vy, has_dgx, loaded = new[idx]
        tx, ty = vx + dx, vy + dy
        static = STATIC_SPRITES.get((tx, ty), [])
        if not any('kraubslpehi' in s for s in static):
            continue
        if any((nv_x, nv_y) == (tx, ty) for i, (nv_x, nv_y, _, _) in enumerate(new) if i != idx):
            continue
        new[idx] = (tx, ty, has_dgx, loaded)
    return State(vehicles=tuple(new), pieces=state.pieces)


def try_chain(state, src, direction):
    px, py = src
    dx, dy = direction
    pivot = (px + dx, py + dy)
    dest = (px + 2*dx, py + 2*dy)

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

    pivot_sprites = state.get_sprites_at(*pivot)
    if not has_pivot(pivot_sprites):
        return None
    dest_sprites = state.get_sprites_at(*dest)
    if not is_valid_dest(dest_sprites):
        return None

    new_pieces = set(state.pieces)
    new_vehicles = list(state.vehicles)
    src_color = 0
    if piece_here is not None:
        new_pieces.remove(piece_here)
        src_color = piece_here[2]
    else:
        vx, vy, has_dgx, loaded = new_vehicles[vehicle_idx]
        src_color = loaded[2]
        new_vehicles[vehicle_idx] = (vx, vy, has_dgx, None)

    # Consume pivot piece if same color AND not blue (engine excludes blue from consumption)
    pivot_piece = None
    for p in new_pieces:
        if p[:2] == pivot:
            pivot_piece = p
            break
    if pivot_piece is not None and pivot_piece[2] == src_color and pivot_piece[2] != 2:
        new_pieces.remove(pivot_piece)

    # Dest
    dest_vi = None
    for i, (vx, vy, _, _) in enumerate(new_vehicles):
        if (vx, vy) == dest:
            dest_vi = i
            break
    if dest_vi is not None:
        vx, vy, has_dgx, loaded = new_vehicles[dest_vi]
        if loaded is not None:
            return None
        new_vehicles[dest_vi] = (vx, vy, has_dgx, (px, py, src_color))
    else:
        new_pieces.add((dest[0], dest[1], src_color))

    return State(vehicles=tuple(new_vehicles), pieces=frozenset(new_pieces))


def all_chains(state):
    positions = [p[:2] for p in state.pieces] + [(vx, vy) for (vx, vy, _, l) in state.vehicles if l is not None]
    for src in positions:
        for direction in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            ns = try_chain(state, src, direction)
            if ns is not None:
                yield src, direction, ns


def next_states(state):
    for a, (dx, dy) in [(1, (0, -1)), (2, (0, 1)), (3, (-1, 0)), (4, (1, 0))]:
        ns = move_vehicles(state, dx, dy)
        if ns != state:
            yield f'A{a}', ns
    for src, direction, ns in all_chains(state):
        dname = {(0, -1): 'U', (0, 1): 'D', (-1, 0): 'L', (1, 0): 'R'}[direction]
        yield f'C{src}{dname}', ns


def bfs(max_depth=50):
    start = initial_state()
    print(f'INITIAL: non_blue_foz={start.non_blue_foz_count()}, pieces={sorted(start.pieces)}', flush=True)

    visited = {start: []}
    queue = [(start, [])]
    best = start.non_blue_foz_count()
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
                foz = ns.non_blue_foz_count()
                if foz < best:
                    best = foz
                    best_path = new_path
                    print(f'Depth {len(new_path)}: foz={foz}', flush=True)
                    print(f'  path: {" ".join(new_path)}', flush=True)
                if foz == 1:
                    print(f'\nWIN! Depth {len(new_path)}')
                    return new_path
                new_queue.append((ns, new_path))
        queue = new_queue
        d += 1
        if d % 5 == 0:
            print(f'Depth {d}: visited={len(visited)}', flush=True)
    print(f'Exhausted. best={best}')
    return best_path


if __name__ == '__main__':
    bfs(max_depth=40)
