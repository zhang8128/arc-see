"""Run L8 win plan on real engine."""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
from solutions.solution_lf52_l7 import apply_solution
from l7_harness import L7Harness
from l8_search import bfs


def click_chain(g, src, d):
    vp = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
    sx = src[0]*6+3+vp[0]
    sy = src[1]*6+3+vp[1]
    g.click(sx, sy)
    vp = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
    tx = (src[0]+2*d[0])*6+3+vp[0]
    ty = (src[1]+2*d[1])*6+3+vp[1]
    g.click(tx, ty)


if __name__ == '__main__':
    # Get path from BFS
    from l7_sim import load_init
    s0 = load_init('/tmp/l8_init.json')
    end, path = bfs()
    print(f'Path len: {len(path)}')

    # Execute on engine — need piece positions at each chain
    h = L7Harness(verbose=False)
    h.restore_to('chain8')
    apply_solution(h._base)
    g = h._base
    print(f'Engine at L8 init: levels={g.level()}, whtqurkphir={g.env._game.ikhhdzfmarl.whtqurkphir}')

    # Track piece positions through sim to match engine
    s = s0
    for i, op in enumerate(path):
        if op[0] == 'A':
            d = op[1]
            a = {(0,-1):1,(0,1):2,(-1,0):3,(1,0):4}[d]
            g.action(a)
            s = s.do_action(d)
        else:
            _, pid, d = op
            if pid not in s.pieces:
                print(f'  step {i}: piece {pid} gone, skipping')
                continue
            src = s.pieces[pid]
            click_chain(g, src, d)
            s = s.do_chain(pid, d)
    # Final check
    ik = g.env._game.ikhhdzfmarl
    print(f'FINAL: levels={g.level()}, whtqurkphir={ik.whtqurkphir}, state={g.state_name()}')
    print(f'foz pieces: {[(s.name, tuple(s.chahdtpdoz)) for s in ik.hncnfaqaddg.xpnsbxlatu if "fozwvlovdui" in s.name]}')
