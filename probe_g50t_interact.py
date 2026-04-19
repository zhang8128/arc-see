"""G50T: walk to the blocking sprite at (37,7) and try ACTION5 to unlock it."""
import copy
import importlib.util
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'g50t', 'environment_files/g50t/5849a774/g50t.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def snapshot_interesting(g):
    """Everything I think might change during play."""
    eng = g.vgwycxsxjz
    p = eng.dzxunlkwxt
    out = {
        'player': (p.x, p.y),
        'player.amjlzzsesf': p.amjlzzsesf,
        'player.pddqxjztas': p.pddqxjztas,
        'player.qxtpxrcvcd': p.qxtpxrcvcd,
        'player.lgwskwmkie': p.lgwskwmkie,
        'player.quhblunofo': p.quhblunofo,
        'player.ecvzipvalj': p.ecvzipvalj,
        'player.rotation': p.rotation,
    }
    for i, ent in enumerate(eng.hamayflsib):
        out[f'hamayflsib[{i}].pos'] = (ent.x, ent.y)
        out[f'hamayflsib[{i}].dijhfchobv'] = ent.dijhfchobv
        out[f'hamayflsib[{i}].is_visible'] = ent.is_visible
    for i, ent in enumerate(eng.uwxkstolmf):
        out[f'uwxkstolmf[{i}].pos'] = (ent.x, ent.y)
        out[f'uwxkstolmf[{i}].dijhfchobv'] = ent.dijhfchobv
        out[f'uwxkstolmf[{i}].is_visible'] = ent.is_visible
        out[f'uwxkstolmf[{i}].ecvzipvalj'] = ent.ecvzipvalj
    for i, ent in enumerate(eng.drofvwhbxb):
        out[f'drofvwhbxb[{i}].pos'] = (ent.x, ent.y)
        out[f'drofvwhbxb[{i}].flzkzvlsvl'] = ent.flzkzvlsvl
        out[f'drofvwhbxb[{i}].is_visible'] = ent.is_visible
    for name in ('dofntsemri', 'jqpwhiraaj', 'jvtgoshrhq', 'pohkooyzds',
                 'safkknjslo', 'zvuxrhnlcb', 'rlazdofsxb'):
        out[f'eng.{name}'] = getattr(eng, name, None)
    return out


def diff(a, b):
    return {k: (a.get(k), b.get(k)) for k in b if a.get(k) != b.get(k)}


def act(g, name):
    g.perform_action(ActionInput(id=getattr(GameAction, name)))


def main():
    g = mod.G50t()
    g.set_level(0)

    # Walk 4 right
    print("=== Walking right to (37,7) ===")
    base = snapshot_interesting(g)
    print(f"initial: {base['player']}")
    for i in range(4):
        before = snapshot_interesting(g)
        act(g, 'ACTION4')
        after = snapshot_interesting(g)
        d = diff(before, after)
        print(f"  R{i+1}: player {before['player']} -> {after['player']}")
        for k, (b_, a_) in d.items():
            if k != 'player':
                print(f"      {k}: {b_} -> {a_}")

    # Now at (37, 7) next to hamayflsib. Try ACTION5.
    print("\n=== Try ACTION5 at (37,7) next to the obstacle ===")
    before = snapshot_interesting(g)
    act(g, 'ACTION5')
    after = snapshot_interesting(g)
    d = diff(before, after)
    print(f"  player {before['player']} -> {after['player']}")
    if d:
        print("  CHANGES:")
        for k, (b_, a_) in d.items():
            print(f"    {k}: {b_} -> {a_}")
    else:
        print("  NO CHANGES")

    # Try each other action too
    print("\n=== Try each action from (37,7) after one ACTION5 ===")
    for a in ['ACTION1', 'ACTION2', 'ACTION3', 'ACTION4']:
        g2 = copy.deepcopy(g)
        before = snapshot_interesting(g2)
        act(g2, a)
        after = snapshot_interesting(g2)
        d = diff(before, after)
        moved = before['player'] != after['player']
        print(f"  {a}: player {before['player']} -> {after['player']} {'MOVED' if moved else 'BLOCKED'}")
        for k, (b_, a_) in d.items():
            if k != 'player':
                print(f"      {k}: {b_} -> {a_}")

    # Also probe: walk down-left path to (13,31) and try interactions at various points
    print("\n=== Reset, walk to (13, 31) (the far bottom-left of reachable area) ===")
    g3 = mod.G50t()
    g3.set_level(0)
    # 4 down
    for _ in range(4):
        act(g3, 'ACTION2')
    print(f"  after 4D: pos={snapshot_interesting(g3)['player']}")
    # ACTION5 here
    before = snapshot_interesting(g3)
    act(g3, 'ACTION5')
    after = snapshot_interesting(g3)
    d = diff(before, after)
    if d:
        print("  ACTION5 CHANGES:")
        for k, (b_, a_) in d.items():
            print(f"    {k}: {b_} -> {a_}")
    else:
        print("  ACTION5: no changes at (13,31)")


if __name__ == "__main__":
    main()
