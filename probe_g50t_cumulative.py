"""G50T: does zmq shift accumulate over multiple move+reset cycles?
And does it ever affect game state enough to open new paths?"""
import importlib.util
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'g50t', 'environment_files/g50t/5849a774/g50t.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def snap(g):
    eng = g.vgwycxsxjz
    return {
        'player': (eng.dzxunlkwxt.x, eng.dzxunlkwxt.y),
        'zmq': (eng.zmqoxwsfgh.x, eng.zmqoxwsfgh.y),
        'dro0': (eng.drofvwhbxb[0].x, eng.drofvwhbxb[0].y),
        'dro0.vis': eng.drofvwhbxb[0].is_visible,
        'dro1': (eng.drofvwhbxb[1].x, eng.drofvwhbxb[1].y),
        'dro1.vis': eng.drofvwhbxb[1].is_visible,
        'ham': (eng.hamayflsib[0].x, eng.hamayflsib[0].y),
        'uwx': (eng.uwxkstolmf[0].x, eng.uwxkstolmf[0].y),
        'rlaz': eng.rlazdofsxb,
    }


def act(g, name):
    g.perform_action(ActionInput(id=getattr(GameAction, name)))


def main():
    g = mod.G50t()
    g.set_level(0)
    print(f"[0] initial: zmq={snap(g)['zmq']}")

    # Cycle 1: 1 step right then reset
    print("\n=== Cycle 1: 1R, A5 ===")
    act(g, 'ACTION4')
    act(g, 'ACTION5')
    s = snap(g)
    print(f"  after: player={s['player']} zmq={s['zmq']} rlaz={s['rlaz']} dro0={s['dro0']} dro1={s['dro1']}")

    # Cycle 2: 1 step right then reset
    print("\n=== Cycle 2: 1R, A5 ===")
    act(g, 'ACTION4')
    act(g, 'ACTION5')
    s = snap(g)
    print(f"  after: player={s['player']} zmq={s['zmq']} rlaz={s['rlaz']} dro0={s['dro0']} dro1={s['dro1']}")

    # Cycle 3: do many cycles
    for i in range(3, 20):
        act(g, 'ACTION4')
        act(g, 'ACTION5')
        s = snap(g)
        print(f"  cycle {i}: zmq={s['zmq']} rlaz={s['rlaz']} dro0={s['dro0']} dro1={s['dro1']}")
        # Once zmq gets far enough, test if A2 from (13, 7) moves down differently
        if i == 5 or i == 10:
            # Try moving right and see if previously-blocked positions now work
            from copy import deepcopy
            g2 = deepcopy(g)
            # Walk right 5 (previously blocked at 4)
            for _ in range(5):
                act(g2, 'ACTION4')
            s2 = snap(g2)
            print(f"    test 5R: player={s2['player']}")


if __name__ == "__main__":
    main()
