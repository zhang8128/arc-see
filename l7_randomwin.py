"""Random play on sim: try many seeds, many steps. Does any reach win?"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
import random, time
from l7_sim import load_init, DIRS
from l7_search import moves


def run_random(seed, max_steps=1000):
    random.seed(seed)
    s = load_init()
    seen_pos = {'reg1': set(), 'reg2': set(), 'red': set()}
    for step in range(max_steps):
        for pid, p in s.piece_pos:
            seen_pos.setdefault(pid, set()).add(p)
        if s.foz_count() < 3:
            return step, s, seen_pos
        mv_list = list(moves(s))
        if not mv_list:
            return None, s, seen_pos
        _, s = random.choice(mv_list)
    return None, s, seen_pos


if __name__ == '__main__':
    all_seen = {'reg1': set(), 'reg2': set(), 'red': set()}
    t = time.time()
    wins = 0
    for seed in range(50):
        got, s, sp = run_random(seed, max_steps=500)
        for k in all_seen:
            all_seen[k] |= sp.get(k, set())
        if got:
            wins += 1
            print(f'seed {seed}: WIN in {got} moves! pieces={s.pieces}')
    print(f'{wins}/50 wins, {time.time()-t:.1f}s')
    print()
    print('Union of all reached piece positions:')
    for k in ('reg1', 'reg2', 'red'):
        cells = sorted(all_seen[k])
        print(f'{k}: {len(cells)} cells')
        print(f'  {cells}')
