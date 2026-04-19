"""LF52 tool — renderer + snapshot replay for L2 exploration.

Usage:
    uv run python lf52_tool.py initial           # render L1 initial + L2 initial
    uv run python lf52_tool.py seq FILE          # render each state from click seq
    uv run python lf52_tool.py probe FILE        # try clicks, report win/fail
    uv run python lf52_tool.py ascii             # print L2 initial as ascii grid

Click files are JSON: [[x,y], [x,y], ...] applied after L1 replay.
"""
import json
import sys
import copy
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
import numpy as np
import arc_agi
from arcengine import GameAction

# ARC-AGI 16-color palette — tuned for visibility on black
PALETTE = {
    0:  (0, 0, 0),         # black — empty
    1:  (30, 147, 255),    # blue
    2:  (249, 60, 49),     # red — failure hint
    3:  (79, 204, 48),     # green
    4:  (255, 220, 0),     # yellow — selection border
    5:  (100, 100, 100),   # gray — walls
    6:  (229, 58, 163),    # magenta
    7:  (255, 133, 27),    # orange
    8:  (135, 216, 241),   # light blue
    9:  (146, 18, 49),     # dark red — border
    10: (30, 30, 80),      # dark blue
    11: (180, 120, 60),    # brown — transition b-border
    12: (76, 76, 76),      # dark gray — transition c-interior
    13: (255, 100, 150),   # pink
    14: (255, 224, 135),   # tan — e-pieces (player)
    15: (100, 255, 200),   # teal
}

# L1 solve: 8 clicks to reach L2 initial state
L1_CLICKS = [
    (18, 19), (30, 19), (30, 19), (42, 19),
    (42, 19), (42, 31), (42, 31), (42, 43),
]

# L2 solve: 35 actions (after L1) to reach L3 initial state
# Pattern: [('C', (x, y)) for clicks, ('A', n) for ACTION n]
L2_SOLVE = [
    # 2 merges to dead-end
    ('C', (14, 16)), ('C', (26, 16)), ('C', (26, 16)), ('C', (38, 16)),
    # Transition to top-right shortcut (48, 14)
    ('A', 4), ('A', 4), ('A', 4), ('A', 4),
    ('A', 1), ('A', 1), ('A', 1), ('A', 3),
    # Slide B[5]+B[6] into transition (load it)
    ('C', (38, 16)), ('C', (50, 16)),
    # Drive loaded transition to (36, 50) near sub panel
    ('A', 4), ('A', 2), ('A', 2), ('A', 2),
    ('A', 3), ('A', 3), ('A', 3), ('A', 3),
    ('A', 3), ('A', 3), ('A', 3), ('A', 3),
    ('A', 2), ('A', 2), ('A', 2),
    ('A', 4), ('A', 4), ('A', 4), ('A', 4),
    # Final jump: loaded piece + sub[1][0] → sub bottom-right (WIN L2)
    ('C', (38, 52)), ('C', (50, 52)),
]

# L3 solve: 46 actions (after L2) to reach L4 initial state
L3_SOLVE = [
    ('C', (13, 13)), ('C', (13, 25)),
    ('C', (13, 25)), ('C', (25, 25)),
    ('C', (25, 25)), ('C', (25, 13)),
    ('A', 3),
    ('C', (25, 13)), ('C', (37, 13)),
    ('A', 4), ('A', 4),
    ('C', (62, 19)), ('C', (51, 19)),
    ('C', (62, 31)), ('C', (51, 31)),
    ('A', 4),
    ('C', (31, 13)), ('C', (43, 13)),
    ('C', (43, 13)), ('C', (43, 25)),
    ('C', (43, 25)), ('C', (43, 37)),
    ('C', (43, 37)), ('C', (43, 49)),
    ('A', 1), ('A', 1), ('A', 4), ('A', 4), ('A', 2), ('A', 2), ('A', 4),
    ('C', (49, 49)), ('C', (38, 49)),
    ('A', 3), ('A', 1), ('A', 1), ('A', 3), ('A', 3), ('A', 2), ('A', 2), ('A', 3), ('A', 3),
    ('C', (29, 47)), ('C', (19, 49)),
    ('C', (11, 47)), ('C', (25, 49)),
]


GAME_ID = 'lf52-271a04aa'
OUT_DIR = Path('/tmp/lf52_frames')


def render_png(pixels, scale=10, gridlines=True, label=None):
    """Render 64x64 pixel grid as PIL image. scale=10 means 640×640 output."""
    arr = np.asarray(pixels, dtype=np.int16)
    h, w = arr.shape
    rgb = np.zeros((h, w, 3), dtype=np.uint8)
    for cid, rgb_val in PALETTE.items():
        rgb[arr == cid] = rgb_val
    rgb[arr < 0] = (60, 60, 60)
    img = Image.fromarray(rgb, mode='RGB')
    img = img.resize((w * scale, h * scale), Image.NEAREST)

    if gridlines or label:
        draw = ImageDraw.Draw(img)
        if gridlines:
            # Light grid every 1 cell, stronger every 8 cells (tile boundaries)
            for i in range(1, w):
                color = (40, 40, 40) if i % 8 else (120, 120, 120)
                draw.line([(i * scale, 0), (i * scale, h * scale)], fill=color, width=1)
            for j in range(1, h):
                color = (40, 40, 40) if j % 8 else (120, 120, 120)
                draw.line([(0, j * scale), (w * scale, j * scale)], fill=color, width=1)
            # Coordinate axis labels every 8 cells
            try:
                font = ImageFont.load_default()
                for i in range(0, w, 8):
                    draw.text((i * scale + 2, 2), str(i), fill=(200, 200, 0), font=font)
                for j in range(0, h, 8):
                    draw.text((2, j * scale + 2), str(j), fill=(200, 200, 0), font=font)
            except Exception:
                pass
        if label:
            try:
                font = ImageFont.load_default()
                draw.rectangle([0, h * scale - 14, len(label) * 7, h * scale], fill=(0, 0, 0))
                draw.text((2, h * scale - 13), label, fill=(255, 255, 255), font=font)
            except Exception:
                pass
    return img


def ascii_grid(pixels):
    """Pretty-print pixels as ascii — one char per cell."""
    arr = np.asarray(pixels, dtype=np.int16)
    # Map each color to a distinctive character
    chars = {0: '.', 2: 'r', 3: 'g', 4: 'Y', 5: '#', 9: '|',
             11: 'b', 12: 'c', 14: 'e', 15: 'f'}
    lines = []
    h, w = arr.shape
    # Header
    lines.append('    ' + ''.join(str(i // 10) if i % 5 == 0 else ' ' for i in range(w)))
    lines.append('    ' + ''.join(str(i % 10) if i % 5 == 0 else ' ' for i in range(w)))
    for y in range(h):
        row = ''.join(chars.get(int(arr[y, x]), '?') for x in range(w))
        lines.append(f'{y:3d} {row}')
    return '\n'.join(lines)


class LF52:
    """Encapsulates an LF52 env with double-reset + L1 snapshot."""

    def __init__(self, verbose=False, up_to_level=2):
        """Replay known solutions up to (but not beyond) the given level.
        up_to_level=1: reset only (env is at L1 initial).
        up_to_level=2: replay L1 so env is at L2 initial.
        up_to_level=3: replay L1+L2 so env is at L3 initial.
        up_to_level=4: replay L1+L2+L3 so env is at L4 initial.
        """
        self.verbose = verbose
        self.arcade = arc_agi.Arcade()
        self.env = self.arcade.make(GAME_ID, render_mode=None)
        obs0 = self.env.reset()
        obs0 = self.env.reset()  # double-reset for correctness
        self._l1_start_snap = copy.deepcopy(self.env._game)
        self._l1_start_frame = np.array(obs0.frame[-1], dtype=np.int16).copy()
        self.obs = obs0
        if up_to_level >= 2:
            # Replay L1
            for cx, cy in L1_CLICKS:
                self.obs = self.env.step(GameAction.ACTION6, data={'x': cx, 'y': cy})
            self._l2_start_snap = copy.deepcopy(self.env._game)
            self._l2_start_frame = np.array(self.obs.frame[-1], dtype=np.int16).copy()
        # Optionally replay L2
        if up_to_level >= 3:
            for step in L2_SOLVE:
                kind, val = step
                if kind == 'C':
                    self.obs = self.env.step(GameAction.ACTION6, data={'x': val[0], 'y': val[1]})
                else:
                    self.obs = self.env.step(getattr(GameAction, f'ACTION{val}'))
            self._l3_start_snap = copy.deepcopy(self.env._game)
            self._l3_start_frame = np.array(self.obs.frame[-1], dtype=np.int16).copy()
        if up_to_level >= 4:
            for step in L3_SOLVE:
                kind, val = step
                if kind == 'C':
                    self.obs = self.env.step(GameAction.ACTION6, data={'x': val[0], 'y': val[1]})
                else:
                    self.obs = self.env.step(getattr(GameAction, f'ACTION{val}'))
            self._l4_start_snap = copy.deepcopy(self.env._game)
            self._l4_start_frame = np.array(self.obs.frame[-1], dtype=np.int16).copy()
        if up_to_level >= 5:
            from solutions.solution_lf52_l4 import L4_SOLVE
            for step in L4_SOLVE:
                kind, val = step
                if kind == 'C':
                    self.obs = self.env.step(GameAction.ACTION6, data={'x': val[0], 'y': val[1]})
                else:
                    self.obs = self.env.step(getattr(GameAction, f'ACTION{val}'))
            self._l5_start_snap = copy.deepcopy(self.env._game)
            self._l5_start_frame = np.array(self.obs.frame[-1], dtype=np.int16).copy()
        if up_to_level >= 7:
            from solutions.solution_lf52_l5 import SOLUTION as L5_SOLUTION
            from solutions.solution_lf52_l6 import parse_solution as parse_l6
            for step in L5_SOLUTION:
                if isinstance(step, str):
                    self.obs = self.env.step(getattr(GameAction, f'ACTION{int(step[1:])}'))
                else:
                    kind, src, direction = step
                    ox, oy = tuple(self.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
                    sx, sy = src; dx, dy = direction
                    self.env.step(GameAction.ACTION6, data={'x': sx*6+3+ox, 'y': sy*6+3+oy})
                    ox, oy = tuple(self.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
                    self.obs = self.env.step(GameAction.ACTION6, data={'x': (sx+2*dx)*6+3+ox, 'y': (sy+2*dy)*6+3+oy})
            for step in parse_l6():
                if step[0] == 'A':
                    self.obs = self.env.step(getattr(GameAction, f'ACTION{step[1]}'))
                else:
                    _, (sx, sy), (dx, dy) = step
                    ox, oy = tuple(self.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
                    self.env.step(GameAction.ACTION6, data={'x': sx*6+3+ox, 'y': sy*6+3+oy})
                    ox, oy = tuple(self.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
                    self.obs = self.env.step(GameAction.ACTION6, data={'x': (sx+2*dx)*6+3+ox, 'y': (sy+2*dy)*6+3+oy})
            self._l7_start_snap = copy.deepcopy(self.env._game)
            self._l7_start_frame = np.array(self.obs.frame[-1], dtype=np.int16).copy()
        if up_to_level >= 2 and self.obs.levels_completed < 1:
            print(f'WARNING: L1 not solved after replay! levels_completed={self.obs.levels_completed}')

    def reset_to_l2(self):
        """Restore L2 initial state from snapshot. Fast — no L1 replay."""
        self.env._game = copy.deepcopy(self._l2_start_snap)
        self.obs = None
        self._cached_frame = self._l2_start_frame.copy()

    def reset_to_l1(self):
        """Reset to game start (L1). Fast via snapshot."""
        self.env._game = copy.deepcopy(self._l1_start_snap)
        self.obs = None
        self._cached_frame = self._l1_start_frame.copy()

    def reset_to_l3(self):
        """Restore L3 initial state from snapshot. Requires up_to_level=3."""
        if not hasattr(self, '_l3_start_snap'):
            raise RuntimeError('Init LF52 with up_to_level=3 to use reset_to_l3')
        self.env._game = copy.deepcopy(self._l3_start_snap)
        self.obs = None
        self._cached_frame = self._l3_start_frame.copy()

    def reset_to_l4(self):
        """Restore L4 initial state from snapshot. Requires up_to_level=4."""
        if not hasattr(self, '_l4_start_snap'):
            raise RuntimeError('Init LF52 with up_to_level=4 to use reset_to_l4')
        self.env._game = copy.deepcopy(self._l4_start_snap)
        self.obs = None
        self._cached_frame = self._l4_start_frame.copy()

    def _current_pixels(self):
        """Get current 64×64 pixels from game engine, no step required."""
        g = self.env._game
        return np.array(g.get_pixels(0, 0, 64, 64), dtype=np.int16)

    def click(self, x, y):
        self.obs = self.env.step(GameAction.ACTION6, data={'x': x, 'y': y})
        self._cached_frame = None
        return self.obs

    def action(self, a):
        """a: int 1-7 → ACTION1-7"""
        act = getattr(GameAction, f'ACTION{a}')
        if a == 6:
            raise ValueError('Use .click(x,y) for ACTION6')
        self.obs = self.env.step(act)
        self._cached_frame = None
        return self.obs

    def pixels(self):
        if self.obs is not None:
            return np.array(self.obs.frame[-1], dtype=np.int16).copy()
        if hasattr(self, '_cached_frame') and self._cached_frame is not None:
            return self._cached_frame.copy()
        return self._current_pixels()

    def level(self):
        if self.obs is not None:
            return self.obs.levels_completed
        return self.env._game.level_index

    def state_name(self):
        if self.obs is not None:
            return self.obs.state.name
        return self.env._game._state.name

    def e_piece_positions(self):
        """Return (x,y) of all color-14 cells (e-pieces / player)."""
        arr = self.pixels()
        ys, xs = np.where(arr == 14)
        return sorted(set(zip(xs.tolist(), ys.tolist())))

    def transition_position(self):
        """Return bounding box of the transition panel (color 11/12)."""
        arr = self.pixels()
        mask = (arr == 11) | (arr == 12)
        if not mask.any():
            return None
        ys, xs = np.where(mask)
        return (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))

    def failure_active(self):
        """Detect f-key failure state — large blob of color 15."""
        arr = self.pixels()
        return int((arr == 15).sum()) > 30


def cmd_initial():
    OUT_DIR.mkdir(exist_ok=True)
    for f in OUT_DIR.glob('*.png'):
        f.unlink()

    game = LF52()
    print(f'After L1 replay: levels_completed={game.obs.levels_completed} state={game.state_name()}')

    # L1 start (before any click)
    game.reset_to_l1()
    pix = game.pixels()
    render_png(pix, label='L1 initial').save(OUT_DIR / '00_L1_initial.png')
    print(f'Saved L1 initial')

    # L2 start (after L1 solve)
    game.reset_to_l2()
    pix = game.pixels()
    render_png(pix, label='L2 initial').save(OUT_DIR / '01_L2_initial.png')
    print(f'Saved L2 initial')
    print(f'E-piece positions: {game.e_piece_positions()}')
    print(f'Transition bbox: {game.transition_position()}')
    print(f'Output: {OUT_DIR}')


def cmd_seq(filepath):
    """Render each state from a click sequence applied to L2 start."""
    OUT_DIR.mkdir(exist_ok=True)
    for f in OUT_DIR.glob('seq_*.png'):
        f.unlink()

    with open(filepath) as f:
        clicks = json.load(f)

    game = LF52()
    game.reset_to_l2()
    pix = game.pixels()
    render_png(pix, label='L2 initial').save(OUT_DIR / 'seq_00_initial.png')
    print(f'L2 initial: level={game.level()} state={game.state_name()}')

    for i, click in enumerate(clicks, 1):
        if isinstance(click, list) and len(click) == 2 and isinstance(click[0], int):
            x, y = click
            obs = game.click(x, y)
            tag = f'click_{x}_{y}'
        elif isinstance(click, str) and click.startswith('A'):
            a = int(click[1])
            obs = game.action(a)
            tag = click
        else:
            raise ValueError(f'Unknown click spec: {click}')
        pix = game.pixels()
        fail = ' FAIL' if game.failure_active() else ''
        render_png(pix, label=f'{i:02d} {tag}{fail}').save(OUT_DIR / f'seq_{i:02d}_{tag}.png')
        print(f'Step {i} {tag}: level={obs.levels_completed} state={obs.state.name}{fail}')
    print(f'Output: {OUT_DIR}')


def cmd_probe(filepath):
    """Try each click-sequence in FILE, report which wins L2."""
    with open(filepath) as f:
        sequences = json.load(f)

    print(f'Testing {len(sequences)} sequences on L2...')
    wins = []
    game = LF52()
    for i, seq in enumerate(sequences):
        game.reset_to_l2()
        obs = None
        for click in seq:
            if isinstance(click, list):
                obs = game.click(click[0], click[1])
            elif isinstance(click, str) and click.startswith('A'):
                obs = game.action(int(click[1]))
            if obs.levels_completed >= 2:
                wins.append((i, seq))
                print(f'  WIN #{i}: {seq}')
                break
        if i % 100 == 0 and i > 0:
            print(f'  {i}/{len(sequences)} tested, {len(wins)} wins')
    print(f'DONE. {len(wins)} wins of {len(sequences)}.')
    if wins:
        with open('/tmp/lf52_wins.json', 'w') as f:
            json.dump([{'idx': i, 'seq': s} for i, s in wins], f, indent=2)
        print('Wins saved to /tmp/lf52_wins.json')


def cmd_ascii():
    game = LF52()
    game.reset_to_l2()
    print('=== L2 initial state (8×8 tile grid = 64×64 pixel grid) ===')
    print(ascii_grid(game.pixels()))
    print()
    print('Legend: .=empty, e=player piece (color 14), b=trans border, c=trans interior,')
    print('        r=red hint, Y=selection, #=wall, |=panel border, f=f-key failure')


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd = sys.argv[1]
    if cmd == 'initial':
        cmd_initial()
    elif cmd == 'seq':
        cmd_seq(sys.argv[2])
    elif cmd == 'probe':
        cmd_probe(sys.argv[2])
    elif cmd == 'ascii':
        cmd_ascii()
    else:
        print(f'Unknown cmd: {cmd}')
        print(__doc__)


if __name__ == '__main__':
    main()
