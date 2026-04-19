"""G50T L1: test the ghost-replay solution hypothesis.

Path:
  1. A4 A4 A4 A4  (walk to (37, 7) to record a 4-move path to the trigger)
  2. A5           (undo-save: ghost keeps path, new player at start)
  3. A2 A2 A2 A2  (walk new player down to (13, 31); ghost replays to (37, 7) on moves 1-4)
  4. A2 A2 A2     (walk to (13, 49); ghost stays at (37, 7), uwx stays shifted)
  5. A4 A4 A4 A4 A4  (walk to (43, 49) = WIN)
"""
import importlib.util
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'g50t', 'environment_files/g50t/5849a774/g50t.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def snap(g):
    eng = g.vgwycxsxjz
    p = eng.dzxunlkwxt
    out = {
        'player': (p.x, p.y),
        'uwx': (eng.uwxkstolmf[0].x, eng.uwxkstolmf[0].y),
        'ham.d': eng.hamayflsib[0].dijhfchobv,
        'state': g._state.name,
        'level': g._current_level_index,
        'rloltuowth': len(eng.rloltuowth),
    }
    for i, (ghost, path) in enumerate(eng.rloltuowth.items()):
        out[f'ghost[{i}]'] = (ghost.x, ghost.y)
        out[f'ghost[{i}].path_len'] = len(path)
    return out


def act(g, name):
    g.perform_action(ActionInput(id=getattr(GameAction, name)))


def main():
    g = mod.G50t()
    g.set_level(0)
    print(f"start: {snap(g)}")

    sequence = (
        ['ACTION4'] * 4 +  # walk to (37, 7)
        ['ACTION5'] +      # save ghost, new player at (13, 7)
        ['ACTION2'] * 7 +  # walk new player down to (13, 49)
        ['ACTION4'] * 5    # walk to (43, 49)
    )

    for i, a in enumerate(sequence):
        act(g, a)
        s = snap(g)
        print(f"  [{i+1:2d}] {a}: player={s['player']} uwx={s['uwx']} "
              f"ham.d={s['ham.d']} state={s['state']} lvl={s['level']}")
        if 'ghost[0]' in s:
            print(f"           ghost={s['ghost[0]']} path_len={s['ghost[0].path_len']}")
        if s['state'] != 'NOT_FINISHED' or s['level'] > 0:
            print(f"  >>> GAME EVENT <<<")
            break

    print(f"\nfinal: {snap(g)}")
    print(f"Total actions: {i+1}")


if __name__ == "__main__":
    main()
