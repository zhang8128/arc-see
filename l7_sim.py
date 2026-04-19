"""Pure-Python L7 simulator, validated against engine checkpoints.

Rules extracted from environment_files/lf52/271a04aa/lf52.py:

- pymqmlkgzs(cell) — valid chain pivot iff any sprite at cell has
  "fozwvlovdui" or "dgxfozncuiz" substring.
- posalhhmjq(cell) — valid chain target iff exactly 1 sprite with
  "hupkpseyuim" substring, OR exactly 2 sprites and the list contains
  the literal string "hupkpseyuim2".
- Chain exec (cfilhtifcb): source piece moves S → S+2d; if pivot at
  S+d is fozwvlovdui with name == source.name, pivot removed and
  ddaguepwkt drops by 1.
- Vehicle move (tmhxwcojkh): for each hupkpseyuim2, if target cell
  has kraubslpehi and no other hupkpseyuim2, vehicle moves. Any
  non-kraubslpehi sprite at vehicle's pre-move cell moves with it.
- L7 win: ddaguepwkt (count of "fozwvlovdui"-prefix sprites) == 2.

State (mutable):
- piece_pos: dict piece_id → (x,y), piece_id ∈ {'reg1','reg2','red'}
- vehicle_pos: tuple of 6 (x,y)

Static:
- static_cells: dict (x,y) → list of sprite names (no foz, no hup2)
"""
import json
from dataclasses import dataclass, replace
from typing import Dict, Tuple, List, FrozenSet

Pos = Tuple[int, int]
DIRS = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # up, down, left, right

# Engine names (sprite name → conceptual type)
# fozwvlovdui      → regular piece (consumable)
# fozwvlovdui_red  → red piece (not consumable by reg-reg)
# hupkpseyuim      → plain floor
# hupkpseyuim2     → vehicle
# dgxfozncuiz      → DGX pivot (permanent)
# kraubslpehi*     → track variants (vehicle can be here)

PIECE_NAMES = {
    'reg1': 'fozwvlovdui',
    'reg2': 'fozwvlovdui',
    'red': 'fozwvlovdui_red',
}


@dataclass(frozen=True)
class Sim:
    static_cells: Dict[Pos, Tuple[str, ...]]   # kraubslpehi* and plain hupkpseyuim only
    grid_w: int
    grid_h: int
    piece_pos: Tuple[Tuple[str, Pos], ...]  # sorted (piece_id, pos) for live foz pieces
    vehicle_pos: Tuple[Pos, ...]            # sorted vehicle positions
    dgx_pos: Tuple[Pos, ...]                # sorted DGX positions (mobile: dragged by vehicles)

    # --- accessors -------------------------------------------------------
    @property
    def pieces(self) -> Dict[str, Pos]:
        return dict(self.piece_pos)

    def foz_count(self) -> int:
        return len(self.piece_pos)  # every live piece has "fozwvlovdui" prefix

    def cell_sprites(self, pos: Pos) -> List[str]:
        """All sprite names at cell: static + pieces + vehicles + DGX."""
        out = list(self.static_cells.get(pos, ()))
        for pid, p in self.piece_pos:
            if p == pos:
                out.append(PIECE_NAMES[pid])
        for v in self.vehicle_pos:
            if v == pos:
                out.append('hupkpseyuim2')
        for d in self.dgx_pos:
            if d == pos:
                out.append('dgxfozncuiz')
        return out

    # --- rule predicates -------------------------------------------------
    def is_pivot(self, pos: Pos) -> bool:
        """pymqmlkgzs: cell has foz or dgx sprite."""
        names = self.cell_sprites(pos)
        return any(('fozwvlovdui' in n or 'dgxfozncuiz' in n) for n in names)

    def is_target(self, pos: Pos) -> bool:
        """posalhhmjq: len==1 and 'hupkpseyuim' in name, or len==2 with 'hupkpseyuim2' ∈ list."""
        if not (0 <= pos[0] < self.grid_w and 0 <= pos[1] < self.grid_h):
            return False
        names = self.cell_sprites(pos)
        if len(names) == 1 and 'hupkpseyuim' in names[0]:
            return True
        if len(names) == 2 and 'hupkpseyuim2' in names:
            return True
        return False

    # --- chain execution -------------------------------------------------
    def chain_options(self, piece_id: str) -> List[Pos]:
        """Return valid direction offsets for chain from piece."""
        src = self.pieces[piece_id]
        res = []
        for d in DIRS:
            piv = (src[0] + d[0], src[1] + d[1])
            tgt = (src[0] + 2 * d[0], src[1] + 2 * d[1])
            if self.is_pivot(piv) and self.is_target(tgt):
                res.append(d)
        return res

    def do_chain(self, piece_id: str, d: Pos) -> 'Sim':
        """Execute a chain. Returns new Sim.
        Consumes pivot if pivot is a foz piece with matching name."""
        src = self.pieces[piece_id]
        piv = (src[0] + d[0], src[1] + d[1])
        tgt = (src[0] + 2 * d[0], src[1] + 2 * d[1])
        # Find pivot sprite: first fozwvlovdui* (not blue) sprite at piv cell
        pivot_piece = None
        for pid, p in self.piece_pos:
            if p == piv:
                nm = PIECE_NAMES[pid]
                if 'fozwvlovdui' in nm and 'blue' not in nm:
                    pivot_piece = pid
                    break
        # New piece positions
        new_pieces = []
        for pid, p in self.piece_pos:
            if pid == piece_id:
                new_pieces.append((pid, tgt))
            elif pid == pivot_piece and PIECE_NAMES[pid] == PIECE_NAMES[piece_id]:
                # consumed — skip
                continue
            else:
                new_pieces.append((pid, p))
        return replace(self, piece_pos=tuple(sorted(new_pieces)))

    # --- vehicle movement ------------------------------------------------
    def do_action(self, d: Pos) -> 'Sim':
        """Apply A-action direction d ∈ DIRS. All vehicles try to move."""
        dx, dy = d
        # Process vehicles in order: moving right → process rightmost first (so car doesn't
        # collide with the one ahead). Matches engine sort.
        vehicles = list(self.vehicle_pos)
        if dx != 0:
            vehicles.sort(key=lambda v: v[0], reverse=(dx > 0))
        else:
            vehicles.sort(key=lambda v: v[1], reverse=(dy > 0))

        new_vehicle_pos = list(vehicles)
        new_piece_pos = dict(self.piece_pos)
        new_dgx_pos = list(self.dgx_pos)

        veh_cells = set(vehicles)
        for i, v in enumerate(new_vehicle_pos):
            nxt = (v[0] + dx, v[1] + dy)
            if not (0 <= nxt[0] < self.grid_w and 0 <= nxt[1] < self.grid_h):
                continue
            tgt_names = list(self.static_cells.get(nxt, ()))
            has_track = any('kraubslpehi' in n for n in tgt_names)
            if not has_track:
                continue
            if nxt in veh_cells:
                continue
            veh_cells.discard(v)
            veh_cells.add(nxt)
            new_vehicle_pos[i] = nxt
            # Drag co-located mobile sprites (pieces + DGX)
            for pid in list(new_piece_pos.keys()):
                if new_piece_pos[pid] == v:
                    new_piece_pos[pid] = nxt
            for di, dpos in enumerate(new_dgx_pos):
                if dpos == v:
                    new_dgx_pos[di] = nxt

        new_piece_tuple = tuple(sorted(new_piece_pos.items()))
        new_vehicle_tuple = tuple(sorted(new_vehicle_pos))
        new_dgx_tuple = tuple(sorted(new_dgx_pos))
        return replace(self, piece_pos=new_piece_tuple, vehicle_pos=new_vehicle_tuple, dgx_pos=new_dgx_tuple)

    # --- signature for hashing ------------------------------------------
    def sig(self):
        return (self.piece_pos, self.vehicle_pos, self.dgx_pos)


def load_init(path='/tmp/l7_init.json') -> Sim:
    with open(path) as f:
        d = json.load(f)
    W, H = d['grid_size']
    # Build static_cells: drop foz, hup2, AND dgx (all dynamic)
    static = {}
    piece_pos = {}
    vehicle_pos = []
    dgx_pos = []
    for k, names in d['cells'].items():
        x, y = (int(a) for a in k.split(','))
        static_names = tuple(
            n for n in names
            if 'fozwvlovdui' not in n
            and n != 'hupkpseyuim2'
            and n != 'dgxfozncuiz'
        )
        if static_names:
            static[(x, y)] = static_names
    reg_count = 0
    for s in d['sprites']:
        n = s['name']
        pos = tuple(s['pos'])
        if n == 'fozwvlovdui':
            reg_count += 1
            piece_pos[f'reg{reg_count}'] = pos
        elif n == 'fozwvlovdui_red':
            piece_pos['red'] = pos
        elif n == 'fozwvlovdui_blue':
            piece_pos['blue'] = pos
        elif n == 'hupkpseyuim2':
            vehicle_pos.append(pos)
        elif n == 'dgxfozncuiz':
            dgx_pos.append(pos)
    # Sort pieces by initial position for deterministic IDs
    piece_items = sorted(piece_pos.items())
    return Sim(
        static_cells=static,
        grid_w=W,
        grid_h=H,
        piece_pos=tuple(piece_items),
        vehicle_pos=tuple(sorted(vehicle_pos)),
        dgx_pos=tuple(sorted(dgx_pos)),
    )


if __name__ == '__main__':
    s = load_init()
    print('Init pieces:', s.pieces)
    print('Init vehicles:', s.vehicle_pos)
    print('Init foz_count:', s.foz_count())
    # Quick sanity: chain options for each piece
    for pid in s.pieces:
        opts = s.chain_options(pid)
        print(f'  chain from {pid} @ {s.pieces[pid]}: {opts}')
