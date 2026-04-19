"""Does L6's chain C(2,2)D work AFTER A2 A2 but not before?"""
import sys, copy
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
sys.path.insert(0, '/Users/kairos/Projects/arc-see/solutions')
from lf52_tool import LF52
from arcengine import GameAction


def foz(g):
    return sum(1 for i in g.env._game.ikhhdzfmarl._sorted_cache
               if getattr(i[1],'name','').startswith('fozwvlovdui'))


def setup_l6():
    g = LF52(up_to_level=1, verbose=False)
    g.env._game.set_level(5)
    g.env._game.on_set_level(g.env._game.current_level)
    g.env.step(GameAction.ACTION6, data={'x': 0, 'y': 0})
    return g


def chain(g, sx, sy, dx, dy):
    """Click src then dest in world-pixel coords using standard formula."""
    ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
    g.env.step(GameAction.ACTION6, data={'x': sx*6+3+ox, 'y': sy*6+3+oy})
    ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
    g.env.step(GameAction.ACTION6, data={'x': dx*6+3+ox, 'y': dy*6+3+oy})


print("=== L6 init, no A-actions ===", flush=True)
g = setup_l6()
print(f"foz before: {foz(g)}")
chain(g, 2, 2, 2, 4)  # chain (2,2) DOWN
print(f"foz after C(2,2)D: {foz(g)}")

print("\n=== L6 + A2 A2, then chain C(2,2)D ===", flush=True)
g = setup_l6()
g.env.step(GameAction.ACTION2)
g.env.step(GameAction.ACTION2)
print(f"foz before: {foz(g)}")
chain(g, 2, 2, 2, 4)
print(f"foz after: {foz(g)}")

# L6 solution runs many chains; let's track foz reduction per step
print("\n=== Run L6 solution step-by-step, track foz ===", flush=True)
import solution_lf52_l6 as L6
g = setup_l6()
steps = L6.parse_solution()
prev_foz = foz(g)
for i, step in enumerate(steps):
    if step[0] == 'A':
        g.env.step(getattr(GameAction, f'ACTION{step[1]}'))
    else:
        _, (sx, sy), (dx, dy) = step
        ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
        g.env.step(GameAction.ACTION6, data={'x': sx*6+3+ox, 'y': sy*6+3+oy})
        ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
        g.env.step(GameAction.ACTION6, data={'x': (sx+2*dx)*6+3+ox, 'y': (sy+2*dy)*6+3+oy})
    cur = foz(g)
    if cur != prev_foz:
        print(f"  step {i} ({step}): foz {prev_foz} → {cur}", flush=True)
        prev_foz = cur
print(f"Final foz: {foz(g)}, level_idx: {g.env._game._current_level_index}", flush=True)
