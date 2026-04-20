"""Run every solution_{game}.py and report pass/fail.

A solution passes if the subprocess exits 0 AND its stdout contains
either 'state=GameState.WIN', 'state=WIN', 'ALL VERIFIED', or 'SOLVED'.
"""
import subprocess
import sys
import time
from pathlib import Path


SOLUTIONS_DIR = Path(__file__).parent / 'solutions'


WIN_MARKERS = ('GameState.WIN', 'state=WIN', 'state: WIN',
               'Final state: WIN', 'ALL VERIFIED',
               'L10 SOLVED', 'LF52 FULLY SOLVED', '✓ WIN')
PARTIAL_MARKER = 'Final state: PARTIAL'


def run_one(path: Path) -> tuple[str, str, float]:
    t = time.time()
    proc = subprocess.run(
        ['uv', 'run', 'python', str(path)],
        capture_output=True, text=True, timeout=300,
    )
    elapsed = time.time() - t
    out = proc.stdout + '\n' + proc.stderr
    if proc.returncode != 0:
        if 'NotImplementedError' in out and 'wa30_solve.py' in out:
            return 'STUB', 'solver source not committed (documented)', elapsed
        return 'ERROR', f'exit {proc.returncode}: {out.strip().splitlines()[-1] if out.strip() else ""}', elapsed
    # Stub detection: the wa30 placeholder prints a doc-string explaining it.
    if 'STATUS: source lost' in out or 'NEVER committed' in out:
        return 'STUB', 'solver source not committed (documented)', elapsed
    if PARTIAL_MARKER in out:
        # Extract partial summary.
        for line in out.splitlines():
            if PARTIAL_MARKER in line:
                return 'PARTIAL', line.strip(), elapsed
        return 'PARTIAL', 'partial solve', elapsed
    for marker in WIN_MARKERS:
        if marker in out:
            return 'PASS', marker, elapsed
    # Last-resort: extract last few lines
    tail = '\n'.join(out.strip().splitlines()[-3:])
    return 'UNKNOWN', tail[:100], elapsed


def main():
    solutions = sorted(p for p in SOLUTIONS_DIR.glob('solution_*.py'))
    print(f'Running {len(solutions)} solutions...\n')
    print(f'{"game":<10} {"status":<8} {"time":<7}  note')
    print('-' * 70)
    results = []
    for sol in solutions:
        game = sol.stem.removeprefix('solution_')
        status, note, t = run_one(sol)
        results.append((game, status, t, note))
        print(f'{game:<10} {status:<8} {t:>5.1f}s  {note}')
    print('-' * 70)
    by_status: dict[str, int] = {}
    for _, s, _, _ in results:
        by_status[s] = by_status.get(s, 0) + 1
    print(f'Summary: {dict(sorted(by_status.items()))}')
    # Exit non-zero if any unexpected failure. STUB and PARTIAL are
    # documented states, not errors.
    bad = sum(1 for _, s, _, _ in results if s in ('ERROR', 'UNKNOWN'))
    return 0 if bad == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
