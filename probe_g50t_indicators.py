"""G50T: track drofvwhbxb positions across ALL actions from various positions."""
import copy
import importlib.util
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'g50t', 'environment_files/g50t/5849a774/g50t.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def state(g):
    eng = g.vgwycxsxjz
    p = eng.dzxunlkwxt
    out = {'player': (p.x, p.y)}
    for i, e in enumerate(eng.drofvwhbxb):
        out[f'dro[{i}]'] = (e.x, e.y)
        out[f'dro[{i}].vis'] = e.is_visible
        out[f'dro[{i}].flz'] = e.flzkzvlsvl
    for i, e in enumerate(eng.hamayflsib):
        out[f'ham[{i}]'] = (e.x, e.y)
        out[f'ham[{i}].d'] = e.dijhfchobv
    for i, e in enumerate(eng.uwxkstolmf):
        out[f'uwx[{i}]'] = (e.x, e.y)
        out[f'uwx[{i}].d'] = e.dijhfchobv
    z = eng.zmqoxwsfgh
    if z is not None:
        out['zmq'] = (z.x, z.y)
    out['rlazdofsxb'] = eng.rlazdofsxb
    return out


def diff(a, b):
    return {k: (a.get(k), b.get(k)) for k in b if a.get(k) != b.get(k)}


def act(g, name):
    g.perform_action(ActionInput(id=getattr(GameAction, name)))


def main():
    g = mod.G50t()
    g.set_level(0)
    print(f"initial: {state(g)}")

    # ACTION5 from start with NO prior moves
    g2 = copy.deepcopy(g)
    before = state(g2)
    act(g2, 'ACTION5')
    after = state(g2)
    d = diff(before, after)
    print(f"\n[A5 from (13,7) initial]: changes = {d}")

    # Walk a few steps, then A5
    for path in [['ACTION4'], ['ACTION4', 'ACTION4'],
                 ['ACTION4'] * 4,  # reach (37,7) trigger
                 ['ACTION2'] * 4,  # reach (13,31)
                 ['ACTION4', 'ACTION2'],
                 ]:
        g3 = copy.deepcopy(g)
        for p in path:
            act(g3, p)
        pre = state(g3)
        act(g3, 'ACTION5')
        post = state(g3)
        d = diff(pre, post)
        print(f"\n[{path} then A5]: pos {pre['player']} -> {post['player']}, changes = {d}")

    # Full attribute walk: maybe there are fields I'm not tracking
    print("\n=== ALL game.__dict__ int/bool attrs after A4 then A5 ===")
    g4 = copy.deepcopy(g)
    act(g4, 'ACTION4')
    before_all = {}
    def dump_all(g, prefix=''):
        eng = g.vgwycxsxjz
        out = {}
        for name in dir(eng):
            if name.startswith('_'):
                continue
            try:
                v = getattr(eng, name)
            except Exception:
                continue
            if isinstance(v, (int, float, bool)):
                out[f'eng.{name}'] = v
        # Game-level
        for name in dir(g):
            if name.startswith('_'):
                continue
            try:
                v = getattr(g, name)
            except Exception:
                continue
            if isinstance(v, (int, float, bool)) and name not in ('level_index',):
                out[f'g.{name}'] = v
        return out
    before_all = dump_all(g4)
    act(g4, 'ACTION5')
    after_all = dump_all(g4)
    for k, (b, a_) in diff(before_all, after_all).items():
        print(f"  {k}: {b} -> {a_}")


if __name__ == "__main__":
    main()
