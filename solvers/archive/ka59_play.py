"""KA59 interactive play — observe what changes each step."""
import sys, copy, importlib.util
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('ka59', 'environment_files/ka59/9f096b4a/ka59.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

U = ActionInput(id=GameAction.ACTION1, data={})
D = ActionInput(id=GameAction.ACTION2, data={})
L = ActionInput(id=GameAction.ACTION3, data={})
R = ActionInput(id=GameAction.ACTION4, data={})
AM = {'U': U, 'D': D, 'L': L, 'R': R}
sys.stdout.reconfigure(line_buffering=True)


def full_state(g):
    """Complete state dump."""
    ps = sorted(g.current_level.get_sprites_by_tag('xlfuqjygey'), key=lambda s: s.name)
    es = sorted(g.current_level.get_sprites_by_tag('nnckfubbhi'), key=lambda s: s.name)
    sel = g.ascpmvdpwj
    z = {k.name: v for k, v in g.zhcrzgpwcp.items()} if g.zhcrzgpwcp else {}

    parts = []
    for i, s in enumerate(ps):
        mark = '*' if s is sel else ''
        parts.append(f"P{i}{mark}({s.x},{s.y})")
    for i, s in enumerate(es):
        parts.append(f"E{i}({s.x},{s.y})")

    state_str = ' '.join(parts)
    extras = []
    if z:
        extras.append(f"z={z}")
    if g.msbtawvatm:
        extras.append(f"m={g.msbtawvatm}")
    if extras:
        state_str += f" [{', '.join(extras)}]"
    return state_str


def play(level_idx, sequence):
    """Play a sequence and show every state change."""
    g = mod.Ka59()
    g.set_level(level_idx)
    print(f"L{level_idx+1} START: {full_state(g)}")

    total = 0
    i = 0
    while i < len(sequence):
        ch = sequence[i]

        if ch in AM:
            old = full_state(g)
            g.perform_action(AM[ch])
            total += 1
            new = full_state(g)
            if new != old:
                print(f"  [{total:3d}] {ch}: {new}")
            else:
                print(f"  [{total:3d}] {ch}: (no change)")
        elif ch == 'C':
            # Click: switch to next piece
            i += 1
            if i < len(sequence) and sequence[i].isdigit():
                idx = int(sequence[i])
                ps = sorted(g.current_level.get_sprites_by_tag('xlfuqjygey'), key=lambda s: s.name)
                if idx < len(ps):
                    s = ps[idx]
                    gx, gy = s.x + s.width // 2, s.y + s.height // 2
                    sc, ox, oy = g.camera._calculate_scale_and_offset()
                    g.perform_action(ActionInput(id=GameAction.ACTION6,
                        data={'x': int(gx*sc+ox), 'y': int(gy*sc+oy)}))
                    total += 1
                    print(f"  [{total:3d}] C{idx}: {full_state(g)}")
        i += 1

    won = g._current_level_index > level_idx
    print(f"\nDONE: {total} actions, WON={won}")
    print(f"Final: {full_state(g)}")
    return g, total, won


if __name__ == '__main__':
    level = int(sys.argv[1])
    seq = sys.argv[2] if len(sys.argv) > 2 else ''
    play(level, seq)
