"""L7 simulator — foz starts at 3, win at foz == 2 (one merge).

L7 adds: `;` (vehicle on up-track, no dgx) and `D` (vehicle + dgx on up-track).
"""
from dataclasses import dataclass
from typing import Tuple, Optional, List, FrozenSet

# STATIC sprites: track + static pivots + panel cells. NOT including mobile hupkpseyuim2/dgx at vehicle spawn positions.
# Extracted from L7 engine dump (vehicles and their carried dgx subtracted to leave only static).
STATIC_SPRITES = {
    (17, 0): ['kraubslpehi-<'],
    (18, 0): ['kraubslpehi'],
    (19, 0): ['kraubslpehi'],
    (20, 0): ['kraubslpehi'],
    (21, 0): ['kraubslpehi->'],
    (0, 1): ['hupkpseyuim'],  # piece here; static = panel
    (6, 1): ['hupkpseyuim'],  # red piece here
    (11, 1): ['kraubslpehi-<'],
    (12, 1): ['kraubslpehi'],
    (13, 1): ['kraubslpehi'],
    (14, 1): ['kraubslpehi->'],
    (17, 1): ['kraubslpehi-up'],
    (21, 1): ['kraubslpehi-up'],
    (0, 2): ['hupkpseyuim', 'dgxfozncuiz'],
    (6, 2): ['hupkpseyuim', 'dgxfozncuiz'],
    (11, 2): ['kraubslpehi-up'],
    (14, 2): ['kraubslpehi-up'],  # vehicle here (;); static = kraubslpehi-up
    (16, 2): ['kraubslpehi-<'],
    (17, 2): ['kraubslpehi-t'],
    (18, 2): ['kraubslpehi-T'],
    (19, 2): ['kraubslpehi'],  # D vehicle here; static = track
    (20, 2): ['kraubslpehi-T'],
    (21, 2): ['kraubslpehi-t'],
    (22, 2): ['kraubslpehi->'],
    (0, 3): ['kraubslpehi-L'],
    (1, 3): ['kraubslpehi'],
    (2, 3): ['kraubslpehi'],
    (3, 3): ['kraubslpehi-T'],
    (4, 3): ['kraubslpehi'],
    (5, 3): ['kraubslpehi'],
    (6, 3): ['kraubslpehi-3'],
    (9, 3): ['kraubslpehi-<'],
    (10, 3): ['kraubslpehi'],
    (11, 3): ['kraubslpehi-t'],
    (12, 3): ['kraubslpehi'],
    (13, 3): ['hupkpseyuim', 'dgxfozncuiz'],
    (14, 3): ['hupkpseyuim'],
    (16, 3): ['kraubslpehi-up'],
    (18, 3): ['kraubslpehi-up'],  # D vehicle; static = track
    (20, 3): ['kraubslpehi-up'],  # D vehicle; static = track
    (22, 3): ['kraubslpehi-up'],
    (3, 4): ['kraubslpehi-up'],
    (9, 4): ['kraubslpehi-up'],
    (14, 4): ['hupkpseyuim'],
    (18, 4): ['kraubslpehi-up'],
    (20, 4): ['kraubslpehi-up'],
    (22, 4): ['kraubslpehi-up'],  # ; vehicle here
    (1, 5): ['kraubslpehi-<'],
    (2, 5): ['kraubslpehi'],
    (3, 5): ['kraubslpehi-t'],
    (4, 5): ['kraubslpehi'],
    (5, 5): ['kraubslpehi'],  # , vehicle here
    (6, 5): ['kraubslpehi->'],
    (8, 5): ['kraubslpehi-<'],
    (9, 5): ['kraubslpehi-t'],
    (10, 5): ['kraubslpehi'],
    (11, 5): ['kraubslpehi->'],
    (14, 5): ['hupkpseyuim'],
    (15, 5): ['hupkpseyuim', 'dgxfozncuiz'],
    (16, 5): ['hupkpseyuim'],
    (17, 5): ['hupkpseyuim', 'dgxfozncuiz'],
    (18, 5): ['hupkpseyuim'],
    (20, 5): ['kraubslpehi-up'],
    (22, 5): ['hupkpseyuim'],
    (1, 6): ['kraubslpehi-up'],
    (6, 6): ['kraubslpehi-up'],
    (8, 6): ['kraubslpehi-up'],
    (11, 6): ['kraubslpehi-up'],
    (14, 6): ['hupkpseyuim'],
    (15, 6): ['hupkpseyuim', 'dgxfozncuiz'],
    (16, 6): ['hupkpseyuim'],
    (17, 6): ['hupkpseyuim', 'dgxfozncuiz'],
    (18, 6): ['hupkpseyuim'],
    (22, 6): ['hupkpseyuim'],  # piece here; static = panel
    (1, 7): ['hupkpseyuim', 'dgxfozncuiz'],
    (6, 7): ['hupkpseyuim', 'dgxfozncuiz'],
    (8, 7): ['kraubslpehi-L'],
    (9, 7): ['kraubslpehi'],
    (10, 7): ['kraubslpehi->'],
    (11, 7): ['hupkpseyuim', 'dgxfozncuiz'],
    (1, 8): ['hupkpseyuim'],
    (2, 8): ['hupkpseyuim', 'dgxfozncuiz'],
    (3, 8): ['hupkpseyuim'],
    (4, 8): ['hupkpseyuim', 'dgxfozncuiz'],
    (5, 8): ['hupkpseyuim'],
    (6, 8): ['hupkpseyuim'],
    (7, 8): ['hupkpseyuim'],
    (8, 8): ['hupkpseyuim'],
    (9, 8): ['hupkpseyuim'],
    (10, 8): ['kraubslpehi-3'],
    (11, 8): ['hupkpseyuim'],
}

# Vehicles: (x, y, has_dgx)
INIT_VEHICLES = [
    (5, 5, False),    # , plain
    (14, 2, False),   # ; plain
    (18, 3, True),    # D (with dgx)
    (19, 2, True),    # D (with dgx)
    (20, 3, True),    # D (with dgx)
    (22, 4, False),   # ; plain
]
# Pieces: (x, y, is_red)
INIT_PIECES = [
    (0, 1, False), (22, 6, False),
    (6, 1, True),  # red piece
]


@dataclass(frozen=True)
class State:
    vehicles: Tuple[Tuple[int, int, bool, Optional[Tuple[int, int, bool]]], ...]
    pieces: FrozenSet[Tuple[int, int, bool]]

    def get_sprites_at(self, x, y):
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

    def foz_count(self):
        return len(self.pieces) + sum(1 for (_, _, _, l) in self.vehicles if l is not None)


def has_pivot(sprites):
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
    is_red = False
    if piece_here is not None:
        new_pieces.remove(piece_here)
        is_red = piece_here[2]
    else:
        vx, vy, has_dgx, loaded = new_vehicles[vehicle_idx]
        is_red = loaded[2]
        new_vehicles[vehicle_idx] = (vx, vy, has_dgx, None)

    # Consume pivot piece if same color
    pivot_piece = None
    for p in new_pieces:
        if p[:2] == pivot:
            pivot_piece = p
            break
    if pivot_piece is not None and pivot_piece[2] == is_red:
        new_pieces.remove(pivot_piece)

    # Place dest
    dest_vi = None
    for i, (vx, vy, _, _) in enumerate(new_vehicles):
        if (vx, vy) == dest:
            dest_vi = i
            break
    if dest_vi is not None:
        vx, vy, has_dgx, loaded = new_vehicles[dest_vi]
        if loaded is not None:
            return None
        new_vehicles[dest_vi] = (vx, vy, has_dgx, (px, py, is_red))
    else:
        new_pieces.add((dest[0], dest[1], is_red))

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


def bfs(max_depth=60):
    import sys
    start = initial_state()
    print(f'INITIAL: foz={start.foz_count()}, pieces={sorted(start.pieces)}', flush=True)

    visited = {start: []}
    queue = [(start, [])]
    best_foz = start.foz_count()
    best_path = []
    depth = 0

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
                if foz == 2:
                    print(f'\nWIN! Depth {len(new_path)}: {" ".join(new_path)}', flush=True)
                    return new_path
                new_queue.append((ns, new_path))
        queue = new_queue
        depth += 1
        if depth % 5 == 0:
            print(f'Depth {depth} reached, visited {len(visited)} states, queue {len(queue)}', flush=True)
    print(f'Exhausted. best_foz={best_foz}, visited {len(visited)} states.')
    return best_path


if __name__ == '__main__':
    bfs(max_depth=40)
