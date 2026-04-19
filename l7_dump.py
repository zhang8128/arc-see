"""Dump L7 initial ground-truth state to JSON.

All cells with sprites, named, typed. Used to seed l7_sim.py.
"""
import json
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
from lf52_tool import LF52


def dump_state(g, path):
    game = g.env._game
    ik = game.ikhhdzfmarl
    grid = ik.hncnfaqaddg
    W, H = grid.ksfoftduxiu, grid.kfiapdsgfly
    cells = {}
    for x in range(W):
        for y in range(H):
            names = [s.name for s in grid.ijpoqzvnjt(x, y)]
            if names:
                cells[f'{x},{y}'] = names
    # Also dump mobile sprite positions (pieces and vehicles by name)
    sprites = []
    for s in grid.xpnsbxlatu:
        sprites.append({
            'name': s.name,
            'pos': list(s.chahdtpdoz) if hasattr(s, 'chahdtpdoz') else None,
        })
    out = {
        'grid_size': [W, H],
        'viewport': list(ik.hncnfaqaddg.cdpcbbnfdp),
        'level': ik.whtqurkphir,
        'cells': cells,
        'sprites': sprites,
    }
    with open(path, 'w') as f:
        json.dump(out, f, indent=2)
    print(f'Wrote {path} ({len(cells)} cells, {len(sprites)} sprites)')


if __name__ == '__main__':
    print('Replaying L1-L6 to L7 initial...')
    g = LF52(up_to_level=7, verbose=False)
    dump_state(g, '/tmp/l7_init.json')
