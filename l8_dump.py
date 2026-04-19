"""Dump L8 init state."""
import json
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
from solutions.solution_lf52_l7 import apply_solution
from l7_harness import L7Harness


if __name__ == '__main__':
    h = L7Harness(verbose=False)
    h.restore_to('chain8')
    apply_solution(h._base)
    # Now at L8 init
    ik = h._base.env._game.ikhhdzfmarl
    grid = ik.hncnfaqaddg
    W, H = grid.ksfoftduxiu, grid.kfiapdsgfly
    cells = {}
    for x in range(W):
        for y in range(H):
            names = [s.name for s in grid.ijpoqzvnjt(x, y)]
            if names:
                cells[f'{x},{y}'] = names
    sprites = []
    for s in grid.xpnsbxlatu:
        sprites.append({
            'name': s.name,
            'pos': list(s.chahdtpdoz) if hasattr(s, 'chahdtpdoz') else None,
        })
    out = {
        'grid_size': [W, H],
        'viewport': list(grid.cdpcbbnfdp),
        'level': ik.whtqurkphir,
        'lzoqlpcwzpu': ik.lzoqlpcwzpu,
        'cells': cells,
        'sprites': sprites,
    }
    with open('/tmp/l8_init.json', 'w') as f:
        json.dump(out, f, indent=2)
    print(f'Wrote /tmp/l8_init.json: W={W}, H={H}, lzoqlpcwzpu={ik.lzoqlpcwzpu}, {len(cells)} cells')
