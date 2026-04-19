"""Trace the L4 winning sequence step-by-step to find where WIN triggers."""
import importlib.util
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'g50t', 'environment_files/g50t/5849a774/g50t.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

ACTION_NAMES = {'U': 'ACTION1', 'D': 'ACTION2', 'L': 'ACTION3', 'R': 'ACTION4'}

SEQ = ['D', 'D', 'R', 'R', 'U', 'U', 'R', 'R', 'D', 'D', 'D', 'ACTION5',
       'D', 'D', 'R', 'D', 'ACTION5', 'L', 'L', 'L', 'D', 'D', 'D', 'D', 'D',
       'R', 'R', 'R', 'L', 'L', 'L']


def fresh():
    g = mod.G50t()
    g.set_level(3)
    return g


def do(g, name):
    full = name if name.startswith('ACTION') else ACTION_NAMES[name]
    g.perform_action(ActionInput(id=getattr(GameAction, full)))


def pos(g):
    p = g.vgwycxsxjz.dzxunlkwxt
    return (p.x, p.y)


def main():
    g = fresh()
    for i, a in enumerate(SEQ):
        do(g, a)
        p = pos(g)
        eng = g.vgwycxsxjz
        ghosts = [(k.x, k.y) for k in eng.rloltuowth]
        ulhh_s = [(len(h.rqxibulywa), len(h.vbqvjbxkfm))
                  for h in eng.hamayflsib if type(h).__name__ == 'ulhhdeoyok']
        sw = [h.dijhfchobv for h in eng.hamayflsib
              if hasattr(h, 'dijhfchobv')]
        doors_ = [(d.x, d.y) for d in eng.uwxkstolmf]
        print(f"step {i+1:2d} {a:7s} player={p} ghosts={ghosts} "
              f"doors={doors_} sw={sw} ulhh={ulhh_s} "
              f"state={g._state.name} lvl={g._current_level_index}")
        if g._state.name == "WIN" or g._current_level_index > 3:
            print(f"\n*** WIN at step {i+1} ***")
            break


if __name__ == "__main__":
    main()
