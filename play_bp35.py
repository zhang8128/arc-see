"""Play BP35 with an arbitrary action sequence, rendering every frame."""
import sys
from pathlib import Path
from PIL import Image
import numpy as np
import arc_agi
from arcengine import GameAction

PALETTE = {
    0: (0, 0, 0), 1: (30, 147, 255), 2: (249, 60, 49),
    3: (79, 204, 48), 4: (255, 220, 0), 5: (100, 100, 100),
    6: (229, 58, 163), 7: (255, 133, 27), 8: (135, 216, 241),
    9: (146, 18, 49), 10: (30, 30, 80), 11: (255, 255, 255),
    12: (76, 76, 76), 13: (255, 100, 150), 14: (255, 224, 135),
    15: (100, 255, 200),
}


def render(pixels, scale=8):
    arr = np.asarray(pixels, dtype=np.int16)
    h, w = arr.shape
    rgb = np.zeros((h, w, 3), dtype=np.uint8)
    for cid, c in PALETTE.items():
        rgb[arr == cid] = c
    rgb[arr < 0] = (60, 60, 60)
    img = Image.fromarray(rgb, mode='RGB')
    return img.resize((w * scale, h * scale), Image.NEAREST) if scale != 1 else img


def parse_action(token):
    """Parse e.g. 'L', 'R', 'C45,33', 'U' -> (GameAction, data, label)."""
    t = token.strip().upper()
    if t == 'L':
        return GameAction.ACTION3, None, 'L'
    if t == 'R':
        return GameAction.ACTION4, None, 'R'
    if t == 'U':
        return GameAction.ACTION7, None, 'U'  # undo
    if t.startswith('C'):
        x, y = t[1:].split(',')
        return GameAction.ACTION6, {'x': int(x), 'y': int(y)}, f'C{x}_{y}'
    raise ValueError(f"Unknown action token: {token}")


def main():
    actions = sys.argv[1:] if len(sys.argv) > 1 else ['R', 'R', 'R', 'R', 'C45,33']
    outdir = Path('/tmp/bp35_play')
    outdir.mkdir(exist_ok=True)
    for f in outdir.glob('*.png'):
        f.unlink()

    arcade = arc_agi.Arcade()
    env = arcade.make('bp35-0a0ad940', render_mode=None)
    obs = env.reset()
    obs = env.reset()

    frame = np.asarray(obs.frame[-1], dtype=np.int16)
    render(frame).save(outdir / 'frame_00_start.png')
    print(f"  00: start state={obs.state.name}")

    for i, tok in enumerate(actions, 1):
        aid, data, label = parse_action(tok)
        obs = env.step(aid, data=data)
        frame = np.asarray(obs.frame[-1], dtype=np.int16)
        render(frame).save(outdir / f'frame_{i:02d}_{label}.png')
        print(f"  {i:02d}: {label} state={obs.state.name}")
        if obs.state.name == 'WIN':
            print("WIN!")
            break


if __name__ == '__main__':
    main()
