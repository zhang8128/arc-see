"""Render BP35 frames as PNG images using arc_agi environment."""
from pathlib import Path
from PIL import Image
import numpy as np
import arc_agi

# ARC-AGI palette (standard + adjusted for visibility)
PALETTE = {
    0: (0, 0, 0),          # black — empty
    1: (30, 147, 255),     # blue
    2: (249, 60, 49),      # red
    3: (79, 204, 48),      # green — dots
    4: (255, 220, 0),      # yellow
    5: (100, 100, 100),    # gray — walls
    6: (229, 58, 163),     # magenta
    7: (255, 133, 27),     # orange
    8: (135, 216, 241),    # light blue
    9: (146, 18, 49),      # dark red — player head
    10: (30, 30, 80),      # dark blue — walkable
    11: (255, 255, 255),   # white — player body
    12: (76, 76, 76),      # dark gray
    13: (255, 100, 150),   # pink
    14: (255, 224, 135),   # tan — items
    15: (100, 255, 200),   # teal — turn counter
}


def render_png(pixels, scale=8):
    arr = np.asarray(pixels, dtype=np.int16)
    h, w = arr.shape
    rgb = np.zeros((h, w, 3), dtype=np.uint8)
    for cid, rgb_val in PALETTE.items():
        rgb[arr == cid] = rgb_val
    rgb[arr < 0] = (60, 60, 60)
    img = Image.fromarray(rgb, mode='RGB')
    if scale != 1:
        img = img.resize((w * scale, h * scale), Image.NEAREST)
    return img


def main():
    outdir = Path('/tmp/bp35_frames')
    outdir.mkdir(exist_ok=True)
    for f in outdir.glob('*.png'):
        f.unlink()

    arcade = arc_agi.Arcade()
    env = arcade.make('bp35-0a0ad940', render_mode=None)
    obs = env.reset()
    obs = env.reset()  # double reset

    from arcengine import GameAction, ActionInput

    frame = np.asarray(obs.frame[-1], dtype=np.int16)
    img = render_png(frame)
    img.save(outdir / 'frame_00_initial.png')
    print(f"Saved frame 0")

    sequence = [
        ('A4', GameAction.ACTION4, {}),
        ('A4', GameAction.ACTION4, {}),
        ('A4', GameAction.ACTION4, {}),
        ('A4', GameAction.ACTION4, {}),
        ('click_45_33', GameAction.ACTION6, {'x': 45, 'y': 33}),
        ('A4', GameAction.ACTION4, {}),
        ('A4_blocked', GameAction.ACTION4, {}),
        ('A3', GameAction.ACTION3, {}),
    ]
    for i, (tag, aid, data) in enumerate(sequence, 1):
        obs = env.step(aid, data=data or None)
        frame = np.asarray(obs.frame[-1], dtype=np.int16)
        img = render_png(frame)
        img.save(outdir / f'frame_{i:02d}_{tag}.png')
        print(f"Saved frame {i} ({tag}) state={obs.state.name}")

    print(f"Done. Frames in {outdir}")


if __name__ == '__main__':
    main()
