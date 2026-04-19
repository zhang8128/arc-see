"""Verify L9 win on engine."""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
from solutions.solution_lf52_l7 import apply_solution as apply_l7
from solutions.solution_lf52_l8 import apply_solution as apply_l8
from l7_harness import L7Harness
from l7_sim import load_init
from l9_search import bfs


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
    h = L7Harness(verbose=False)
    h.restore_to('chain8')
    apply_l7(h._base)
    apply_l8(h._base)
    g = h._base
    print(f'At L9 init: levels={g.level()}, whtqurkphir={g.env._game.ikhhdzfmarl.whtqurkphir}')

    _, path = bfs()
    print(f'L9 path len: {len(path)}')

    s = load_init('/tmp/l9_init.json')
    ops_list = []
    for m in path:
        if m[0] == 'A':
            d = m[1]
            a = {(0,-1):1,(0,1):2,(-1,0):3,(1,0):4}[d]
            g.action(a)
            s = s.do_action(d)
            ops_list.append(('A', a))
        else:
            _, pid, d = m
            src = s.pieces[pid]
            click_chain(g, src, d)
            s = s.do_chain(pid, d)
            ops_list.append(('C', pid, d, src))
    ik = g.env._game.ikhhdzfmarl
    print(f'FINAL: levels={g.level()}, whtqurkphir={ik.whtqurkphir}, state={g.state_name()}')
    print(f'foz: {[(s.name, tuple(s.chahdtpdoz)) for s in ik.hncnfaqaddg.xpnsbxlatu if "fozwvlovdui" in s.name]}')
    # Save ops list
    with open('/tmp/l9_ops.py', 'w') as f:
        f.write('SOLUTION = [\n')
        for op in ops_list:
            f.write(f'    {op!r},\n')
        f.write(']\n')
    print('Ops saved to /tmp/l9_ops.py')
