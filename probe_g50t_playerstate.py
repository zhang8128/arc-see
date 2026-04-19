"""G50T: track ALL player attr changes during exploration to find hidden state."""
import copy
import importlib.util
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'g50t', 'environment_files/g50t/5849a774/g50t.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def player_attrs(g):
    p = g.vgwycxsxjz.dzxunlkwxt
    out = {}
    for name in sorted(dir(p)):
        if name.startswith('_') or callable(getattr(p, name, None)):
            continue
        try:
            v = getattr(p, name)
        except Exception:
            continue
        if isinstance(v, (int, float, bool, str)) or v is None:
            out[name] = v
    return out


def full_engine_ints(g):
    eng = g.vgwycxsxjz
    out = {}
    for name in sorted(dir(eng)):
        if name.startswith('_'):
            continue
        try:
            v = getattr(eng, name)
        except Exception:
            continue
        if isinstance(v, (int, float, bool)):
            out[f'eng.{name}'] = v
    # And nested entity int/bool attrs
    for listname in ('hamayflsib', 'uwxkstolmf', 'drofvwhbxb'):
        for i, e in enumerate(getattr(eng, listname, [])):
            for name in sorted(dir(e)):
                if name.startswith('_'):
                    continue
                try:
                    v = getattr(e, name)
                except Exception:
                    continue
                if isinstance(v, (int, float, bool)):
                    out[f'eng.{listname}[{i}].{name}'] = v
    return out


def diff(a, b):
    return {k: (a.get(k), b.get(k)) for k in b if a.get(k) != b.get(k)}


def act(g, name):
    g.perform_action(ActionInput(id=getattr(GameAction, name)))


def main():
    g = mod.G50t()
    g.set_level(0)

    print("=== Baseline player attrs ===")
    for k, v in player_attrs(g).items():
        print(f"  {k}: {v!r}")

    # Take every action from start, see what changes
    print("\n=== Actions from (13, 7) ===")
    for a in ['ACTION1', 'ACTION2', 'ACTION3', 'ACTION4', 'ACTION5']:
        g2 = copy.deepcopy(g)
        before_p = player_attrs(g2)
        before_e = full_engine_ints(g2)
        try:
            act(g2, a)
        except Exception as e:
            print(f"\n{a}: EXCEPTION {e}")
            continue
        after_p = player_attrs(g2)
        after_e = full_engine_ints(g2)
        pd = diff(before_p, after_p)
        ed = diff(before_e, after_e)
        print(f"\n{a}:")
        for k, (b, a_) in pd.items():
            print(f"  player.{k}: {b!r} -> {a_!r}")
        for k, (b, a_) in ed.items():
            if k.startswith('eng.'):
                # Only show the engine-level ones that changed (not duplicated)
                pass
            print(f"  {k}: {b!r} -> {a_!r}")

    # Try a long path. What if lgwskwmkie = -2 represents "remaining lives" and decrements?
    print("\n=== Long path: 4R, 4D, 4L, 4U ===")
    g3 = mod.G50t()
    g3.set_level(0)
    path = ['ACTION4']*4 + ['ACTION2']*4 + ['ACTION3']*4 + ['ACTION1']*4
    for i, a in enumerate(path):
        before = player_attrs(g3)
        act(g3, a)
        after = player_attrs(g3)
        d = diff(before, after)
        moved = (before['x'], before['y']) != (after['x'], after['y'])
        print(f"  step {i+1} {a}: ({before['x']},{before['y']}) -> ({after['x']},{after['y']}) {'MOVED' if moved else 'BLOCKED'}")
        for k, (b_, a_) in d.items():
            if k not in ('x', 'y'):
                print(f"      player.{k}: {b_!r} -> {a_!r}")

    # What about the ACTIONS coming FROM more positions? Let's probe ACTION5
    # from different tiles.
    print("\n=== ACTION5 from different positions ===")
    for path in [[], ['ACTION4'], ['ACTION4', 'ACTION4'],
                 ['ACTION2'], ['ACTION2', 'ACTION2'],
                 ['ACTION4', 'ACTION4', 'ACTION4', 'ACTION4']]:
        g_t = mod.G50t()
        g_t.set_level(0)
        for p in path:
            act(g_t, p)
        p_before = player_attrs(g_t)
        e_before = full_engine_ints(g_t)
        act(g_t, 'ACTION5')
        p_after = player_attrs(g_t)
        e_after = full_engine_ints(g_t)
        pd = diff(p_before, p_after)
        ed = diff(e_before, e_after)
        print(f"  from {(p_before['x'], p_before['y'])} + ACTION5 -> {(p_after['x'], p_after['y'])}")
        for k, (b, a_) in pd.items():
            if k not in ('x', 'y'):
                print(f"      player.{k}: {b!r} -> {a_!r}")


if __name__ == "__main__":
    main()
