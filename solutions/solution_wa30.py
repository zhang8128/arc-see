"""WA30 solution — STATUS: source lost, documentation retained.

WA30 was fully solved in the 2026-04-16 session (see engram episodes and
`project_wa30_progress.md`). The solver logic lived in a local scratch
file `wa30_solve.py` at the project root that was NEVER committed. By
the time any cleanup ran, it was already gone from the working tree.

What IS committed:
  - Engine source at `environment_files/wa30/ee6fef47/wa30.py`.
  - Mechanics notes in engram (recall "wa30 mechanics").
  - The per-level strategy table in `project_wa30_progress.md`.

What is NOT committed:
  - The `wa30_solve` module with `solve_with_engine`, `plan_delivery`,
    `bfs_carry`, `extract_level`, etc. Without it, this file cannot run.

Mechanics (from engram):
  - 16×16 grid at 4px per cell.
  - A5 = grab piece (when facing) / kill enemy (when facing enemy) / drop (when carrying).
  - Helpers auto-pathfind pieces toward `fsjjayjoeg` targets.
  - Enemies steal pieces to `zqxwgacnue` — kill them before or after.
  - Win: all geezpjgiyd at fsjjayjoeg AND none in zmqreragji.
  - `_really_set_next_level()` must be called after `next_level()` flags advance.

Per-level actions counts at time of solve:
  L1=26, L2=58, L3=91, L4=73, L5=125, L6=48, L7=62, L8≈?, L9≈70 (baseline 71/119/183/98/368/68/79/442/415).

Reconstruction path:
  1. Re-implement `extract_level(g)` to snapshot player pos, piece positions, targets, NPCs from engine state.
  2. A* on the 16×16 grid for `plan_delivery(player, piece, target, blocked)`.
  3. Greedy driver: while pieces remain, pick next one, plan grab-and-deliver, execute.
  4. L7+ wrappers: kill stuck enemy, retrieve piece, deliver.
"""
BASELINES = [71, 119, 183, 98, 368, 68, 79, 442, 415]


def apply_solution(g=None):
    raise NotImplementedError(
        "WA30 solver source (wa30_solve.py) was never committed to git. "
        "See this module's docstring and engram 'wa30 mechanics' for "
        "reconstruction guidance."
    )


if __name__ == '__main__':
    print(__doc__)
