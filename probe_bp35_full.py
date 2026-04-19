"""BP35: holistic state-tracking probe."""
import importlib.util
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'bp35', 'environment_files/bp35/0a0ad940/bp35.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def fresh(level=0):
    g = mod.Bp35()
    g.set_level(level)
    return g


def full_state(g):
    eng = g.oztjzzyqoek
    p = eng.twdpowducb
    # Other potentially-interesting attrs
    return {
        'state': g._state.name,
        'score': g.hbqwwgceeqp,
        'player_xy': (p.x, p.y),
        'camera_xy': (eng.camera.x, eng.camera.y),
        'wjidupyeoa': eng.wjidupyeoa,
        'qswcochjodb': eng.qswcochjodb,
        'hlfdukibtwe': eng.hlfdukibtwe,
        'vivnprldht': eng.vivnprldht,
        'ybmkdxbdko': eng.ybmkdxbdko,
        'jrhqdvdwpsb': eng.jrhqdvdwpsb,
        'nkuphphdgrp': eng.nkuphphdgrp,
        'qycobxllrqj': eng.qycobxllrqj,
        'zfckswusepg': eng.zfckswusepg,
    }


def diff(a, b):
    return {k: (a[k], b[k]) for k in a if a[k] != b[k]}


def main():
    # Try each action from fresh, report diff
    base = fresh()
    base_s = full_state(base)
    print(f"Base state: {base_s}")

    for name in ['ACTION3', 'ACTION4', 'ACTION6', 'ACTION7']:
        g = fresh()
        try:
            if name == 'ACTION6':
                g.perform_action(ActionInput(id=GameAction.ACTION6, data={'x': 18, 'y': 138}))
            else:
                g.perform_action(ActionInput(id=getattr(GameAction, name)))
            s = full_state(g)
            d = diff(base_s, s)
            print(f"\n{name}: diff={d}")
        except Exception as e:
            print(f"\n{name}: error {e}")

    # Try ACTION7 after different moves
    print("\n--- ACTION7 after each other action ---")
    for prev in ['ACTION3', 'ACTION4', 'ACTION6']:
        g = fresh()
        try:
            if prev == 'ACTION6':
                g.perform_action(ActionInput(id=GameAction.ACTION6, data={'x': 18, 'y': 138}))
            else:
                g.perform_action(ActionInput(id=getattr(GameAction, prev)))
            s1 = full_state(g)
            g.perform_action(ActionInput(id=GameAction.ACTION7))
            s2 = full_state(g)
            d = diff(s1, s2)
            print(f"\nafter {prev}+ACTION7: diff={d}")
        except Exception as e:
            print(f"\nafter {prev}+ACTION7: error {e}")

    # Check pjdcytzsmft (rendered grid) — dump a small section
    print("\n--- pjdcytzsmft rendered grid (first 20 rows) ---")
    g = fresh()
    eng = g.oztjzzyqoek
    arr = eng.pjdcytzsmft
    print(f"shape: {arr.shape}, dtype: {arr.dtype}")
    print(f"unique values: {sorted(set(arr.flatten().tolist()))[:20]}")
    # print the grid
    for row in range(32, 50):
        print(''.join(f'{int(arr[row, c]):3d}' for c in range(0, 32)))


if __name__ == "__main__":
    main()
