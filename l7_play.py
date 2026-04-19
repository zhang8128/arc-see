"""Interactive L7 harness.

Usage:
  uv run python l7_play.py run CMDS     # CMDS is a string like "3,3,4,C:20,18,1"
                                         # 3,4,1,2,7 = ACTIONn; C:x,y = click(x,y)
  uv run python l7_play.py scan         # scan every ACTION and click at each tile center
  uv run python l7_play.py interactive  # stdin loop: type commands, see state

Renders PNG to /tmp/l7/NNN.png after each step so you can see the whole trace.
"""
import sys, shutil, copy
from pathlib import Path
import numpy as np
from lf52_tool import LF52, render_png

OUT = Path('/tmp/l7')

def find_vehicle(pix):
    """Vehicle = tight square of color-11 border around color-12 interior."""
    h, w = pix.shape
    mask11 = pix == 11
    mask12 = pix == 12
    # Brute force: find 6x6 blocks where top and bottom rows are color 11, interior rows contain 12
    for y in range(h - 5):
        for x in range(w - 5):
            blk = pix[y:y+6, x:x+6]
            if ((blk[0] == 11).sum() >= 5 and (blk[-1] == 11).sum() >= 5
                    and (blk[1:-1, 1:-1] == 12).sum() >= 12):
                return (x, y, x + 5, y + 5)
    return None

def summarize(pix):
    v = find_vehicle(pix)
    colors = {int(c): int(n) for c, n in zip(*np.unique(pix, return_counts=True))}
    return {'vehicle_bbox': v, 'colors': colors}

def parse_cmds(s):
    """Parse comma-separated cmds: '3' = A3, 'C:20,18' = click(20,18)"""
    out = []
    if not s.strip():
        return out
    for tok in s.split(','):
        tok = tok.strip()
        if tok.startswith('C:'):
            x, y = tok[2:].split(',')
            out.append(('C', int(x), int(y)))
        else:
            out.append(('A', int(tok)))
    return out

def apply(g, cmd):
    kind = cmd[0]
    if kind == 'A':
        g.action(cmd[1])
        return f'A{cmd[1]}'
    else:
        g.click(cmd[1], cmd[2])
        return f'C{cmd[1]},{cmd[2]}'

def run(cmds_str):
    shutil.rmtree(OUT, ignore_errors=True)
    OUT.mkdir(parents=True, exist_ok=True)
    g = LF52(up_to_level=7, verbose=False)
    cmds = parse_cmds(cmds_str)
    render_png(g.pixels(), label='00 start').save(OUT / '000_start.png')
    print(f'step 000: start level={g.level()} state={g.state_name()}')
    print(f'  {summarize(g.pixels())}')
    for i, cmd in enumerate(cmds, 1):
        tag = apply(g, cmd)
        pix = g.pixels()
        render_png(pix, label=f'{i:03d} {tag}').save(OUT / f'{i:03d}_{tag}.png')
        lvl = g.level()
        state = g.state_name()
        summ = summarize(pix)
        print(f'step {i:03d} {tag}: level={lvl} state={state} vehicle={summ["vehicle_bbox"]}')
        if state == 'WIN':
            print('WIN!')
            return
        if lvl >= 7:
            print(f'LEVEL UP to {lvl}!')
            return

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'run'
    if cmd == 'run':
        run(sys.argv[2] if len(sys.argv) > 2 else '')
