"""G50T: track zmqoxwsfgh across repeated ACTION5 and other moves."""
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
        'ham.d': eng.hamayflsib[0].dijhfchobv,
        'uwx': (eng.uwxkstolmf[0].x, eng.uwxkstolmf[0].y),
        'uwx.d': eng.uwxkstolmf[0].dijhfchobv,
        'rlaz': eng.rlazdofsxb,
        'state': g._state.name,
        'level': g._current_level_index,
    }


def act(g, name):
    g.perform_action(ActionInput(id=getattr(GameAction, name)))


def main():
    g = mod.G50t()
    g.set_level(0)
    print(f"[0] initial: {snap(g)}")

    # Spam ACTION5 until something changes
    for i in range(1, 10):
        act(g, 'ACTION5')
        s = snap(g)
        print(f"[{i}] A5: player={s['player']} zmq={s['zmq']} rlaz={s['rlaz']} state={s['state']}")

    # Now the key test: after shifting zmq, does walking behave differently?
    print("\n=== After multiple A5, walk right to (37,7) and try to go further ===")
    for i in range(4):
        act(g, 'ACTION4')
    s = snap(g)
    print(f"after 4R: {s}")
    # Try A4 again (previously blocked)
    act(g, 'ACTION4')
    s = snap(g)
    print(f"after +1R: {s}")
    # Try A2 down (previously blocked)
    act(g, 'ACTION2')
    s = snap(g)
    print(f"after +1D: {s}")


if __name__ == "__main__":
    main()
