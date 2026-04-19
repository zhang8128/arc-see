"""True exhaustive: click every viewport cell at init, report ANY pixel change.
This may reveal clickable areas I haven't mapped."""
import copy, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
from lf52_tool import LF52


def main():
    g = LF52(up_to_level=4, verbose=False)
    base_pix = g.pixels().copy()
    snap = (copy.deepcopy(g.env._game), copy.deepcopy(g.obs))

    print('Exhaustive click sweep at L4 init:', flush=True)
    # Categorize by what changes
    by_signature = {}
    for cy in range(64):
        for cx in range(64):
            g.env._game = copy.deepcopy(snap[0])
            g.obs = copy.deepcopy(snap[1])
            g._cached_frame = None
            try:
                g.click(cx, cy)
            except Exception as e:
                continue
            new_pix = g.pixels()
            if int((new_pix != base_pix).sum()) > 1:  # allow 1 cell for turn counter
                # Create a signature: what colors changed from what to what
                diff_mask = new_pix != base_pix
                changes = []
                ys, xs = np.where(diff_mask)
                for y, x in zip(ys.tolist(), xs.tolist()):
                    before = int(base_pix[y, x])
                    after = int(new_pix[y, x])
                    changes.append((before, after))
                changes = sorted(set(changes))
                sig = tuple(changes)
                if sig not in by_signature:
                    by_signature[sig] = []
                by_signature[sig].append((cx, cy))

    print(f'Found {len(by_signature)} distinct change signatures', flush=True)
    for sig, positions in by_signature.items():
        print(f'\n  Signature (color-before→after): {sig}', flush=True)
        print(f'  {len(positions)} click positions, examples: {positions[:5]}', flush=True)


if __name__ == '__main__':
    main()
