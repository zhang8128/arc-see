"""G50T: probe the hidden rloltuowth (path-followers) and kgvnkyaimw (random-movers)
dicts, and test whether uwx position changes with move count."""
import copy
import importlib.util
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'g50t', 'environment_files/g50t/5849a774/g50t.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def act(g, name):
    g.perform_action(ActionInput(id=getattr(GameAction, name)))


def snap(g):
    eng = g.vgwycxsxjz
    out = {
        'player': (eng.dzxunlkwxt.x, eng.dzxunlkwxt.y),
        'uwx[0]': (eng.uwxkstolmf[0].x, eng.uwxkstolmf[0].y),
        'ham[0]': (eng.hamayflsib[0].x, eng.hamayflsib[0].y),
        'move_history': list(eng.areahjypvy),
        'rloltuowth_entities': len(eng.rloltuowth),
        'kgvnkyaimw_entities': len(eng.kgvnkyaimw),
    }
    for i, (ent, path) in enumerate(eng.rloltuowth.items()):
        out[f'rlol[{i}].pos'] = (ent.x, ent.y)
        out[f'rlol[{i}].path'] = path
        out[f'rlol[{i}].type'] = type(ent).__name__
    for i, (ent, hist) in enumerate(eng.kgvnkyaimw.items()):
        out[f'kgv[{i}].pos'] = (ent.x, ent.y)
        out[f'kgv[{i}].hist'] = hist
        out[f'kgv[{i}].type'] = type(ent).__name__
    return out


def main():
    g = mod.G50t()
    g.set_level(0)
    s0 = snap(g)
    print("=== L1 initial state ===")
    for k, v in s0.items():
        print(f"  {k}: {v}")

    # Is uwx in rloltuowth?
    eng = g.vgwycxsxjz
    print("\n=== Entity identification ===")
    uwx_obj = eng.uwxkstolmf[0]
    ham_obj = eng.hamayflsib[0]
    print(f"  uwxkstolmf[0] id: {id(uwx_obj)}")
    print(f"  hamayflsib[0] id: {id(ham_obj)}")
    print(f"  rloltuowth keys: {[id(k) for k in eng.rloltuowth.keys()]}")
    print(f"  kgvnkyaimw keys: {[id(k) for k in eng.kgvnkyaimw.keys()]}")
    for k in eng.rloltuowth.keys():
        print(f"    rloltuowth entity: type={type(k).__name__} pos=({k.x},{k.y})")
    for k in eng.kgvnkyaimw.keys():
        print(f"    kgvnkyaimw entity: type={type(k).__name__} pos=({k.x},{k.y})")

    # Track uwx across a long move sequence
    print("\n=== Track uwx through 8R ===")
    g2 = copy.deepcopy(g)
    for i in range(1, 9):
        before = snap(g2)
        try:
            act(g2, 'ACTION4')
            after = snap(g2)
            print(f"  move {i}: player {before['player']}->{after['player']} "
                  f"uwx {before['uwx[0]']}->{after['uwx[0]']}")
        except Exception as e:
            print(f"  move {i}: ERR {e}")
            break

    # Can player go down from any position and have uwx stay shifted?
    print("\n=== 4R then 4D (walk to (37,7) then try down) ===")
    g3 = copy.deepcopy(g)
    for _ in range(4):
        act(g3, 'ACTION4')
    print(f"  after 4R: player={snap(g3)['player']} uwx={snap(g3)['uwx[0]']}")
    for i in range(4):
        before = snap(g3)
        act(g3, 'ACTION2')
        after = snap(g3)
        print(f"  D{i+1}: player {before['player']}->{after['player']} "
              f"uwx {before['uwx[0]']}->{after['uwx[0]']}")


if __name__ == "__main__":
    main()
