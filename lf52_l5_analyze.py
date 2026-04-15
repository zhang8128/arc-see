"""L5 grid analyzer — parse the ASCII grid into panels, tracks, pieces."""
import sys

# L5 grid as read from lf52.py line 4785
GRID5 = [
    " -,-T-P-      ..p..x",
    "    |        <---T-P>",
    " ...|  <--> .|...|. |",
    " xp.|.x|  Lx.|.p.|..|",
    " ...|  |    .|..p|x.|",
    "    |  |     L---t--3",
    "  <-t--3       .",
    "  |            p",
    "  |           ..x",
]

# Cell classifiers (from source)
PANEL_CHARS = set(".xpoP")       # cells walkable by pieces (hupkpseyuim)
PIECE_CHARS = set("xo")          # pieces that count for win (fozwvlovdui variants)
F_PIVOT_CHARS = set("pP")        # f-containers (dgxfozncuiz)
TRACK_CHARS = set("-|L3<>Tt,P?;D")  # kraubslpehi*
VEHICLE_LOAD = set(",P?;D")      # hupkpseyuim2 cells

def char_at(r, c):
    if r < 0 or r >= len(GRID5):
        return ' '
    row = GRID5[r]
    if c < 0 or c >= len(row):
        return ' '
    return row[c]

def print_grid():
    print('L5 grid (rows x cols):')
    # Column headers
    maxw = max(len(r) for r in GRID5)
    print('    ' + ''.join(str(c // 10) if c % 5 == 0 else ' ' for c in range(maxw)))
    print('    ' + ''.join(str(c % 10) if c % 5 == 0 else ' ' for c in range(maxw)))
    for r, row in enumerate(GRID5):
        padded = row.ljust(maxw)
        print(f'{r:2d}: {padded}')

def find_cells(predicate):
    cells = []
    for r, row in enumerate(GRID5):
        for c, ch in enumerate(row):
            if predicate(ch):
                cells.append((c, r, ch))
    return cells

def panel_connected_components():
    """Flood-fill panels (connected `.x p P o` cells)."""
    visited = [[False] * max(len(r) for r in GRID5) for _ in GRID5]
    panels = []
    for r, row in enumerate(GRID5):
        for c, ch in enumerate(row):
            if ch in PANEL_CHARS and not visited[r][c]:
                # BFS
                panel = []
                stack = [(c, r)]
                while stack:
                    cc, rr = stack.pop()
                    if visited[rr][cc]:
                        continue
                    if char_at(rr, cc) not in PANEL_CHARS:
                        continue
                    visited[rr][cc] = True
                    panel.append((cc, rr, char_at(rr, cc)))
                    for dc, dr in [(-1,0),(1,0),(0,-1),(0,1)]:
                        nc, nr = cc+dc, rr+dr
                        if 0 <= nr < len(GRID5) and 0 <= nc < len(GRID5[nr]) and not visited[nr][nc]:
                            stack.append((nc, nr))
                panels.append(panel)
    return panels

def track_connected_components():
    """Flood-fill track cells (connected kraubslpehi cells)."""
    visited = [[False] * max(len(r) for r in GRID5) for _ in GRID5]
    tracks = []
    for r, row in enumerate(GRID5):
        for c, ch in enumerate(row):
            if ch in TRACK_CHARS and not visited[r][c]:
                track = []
                stack = [(c, r)]
                while stack:
                    cc, rr = stack.pop()
                    if visited[rr][cc]:
                        continue
                    if char_at(rr, cc) not in TRACK_CHARS:
                        continue
                    visited[rr][cc] = True
                    track.append((cc, rr, char_at(rr, cc)))
                    for dc, dr in [(-1,0),(1,0),(0,-1),(0,1)]:
                        nc, nr = cc+dc, rr+dr
                        if 0 <= nr < len(GRID5) and 0 <= nc < len(GRID5[nr]) and not visited[nr][nc]:
                            stack.append((nc, nr))
                tracks.append(track)
    return tracks

def main():
    print_grid()
    print()

    pieces = find_cells(lambda c: c in PIECE_CHARS)
    print(f'PIECES (n={len(pieces)}):')
    for c, r, ch in pieces:
        print(f'  ({c}, {r}) = {ch}')
    print()

    f_pivots = find_cells(lambda c: c in F_PIVOT_CHARS)
    print(f'F-PIVOTS (p/P, n={len(f_pivots)}):')
    for c, r, ch in f_pivots:
        print(f'  ({c}, {r}) = {ch}')
    print()

    loads = find_cells(lambda c: c in VEHICLE_LOAD)
    print(f'VEHICLE LOAD POINTS (n={len(loads)}):')
    for c, r, ch in loads:
        print(f'  ({c}, {r}) = {ch}')
    print()

    print('PANELS (walkable regions for pieces):')
    for i, panel in enumerate(panel_connected_components()):
        pieces_in = [(c, r) for c, r, ch in panel if ch in PIECE_CHARS]
        f_in = [(c, r) for c, r, ch in panel if ch in F_PIVOT_CHARS]
        loads_in = [(c, r, ch) for c, r, ch in panel if ch in VEHICLE_LOAD]
        print(f'  Panel #{i}: {len(panel)} cells, pieces={pieces_in}, f_pivots={f_in}, loads={loads_in}')
    print()

    print('TRACKS (vehicle paths, connected components):')
    for i, track in enumerate(track_connected_components()):
        loads_in = [(c, r, ch) for c, r, ch in track if ch in VEHICLE_LOAD]
        print(f'  Track #{i}: {len(track)} cells, loads={loads_in}')
        print(f'    cells: {sorted([(c, r) for c, r, _ in track])}')

if __name__ == '__main__':
    main()
