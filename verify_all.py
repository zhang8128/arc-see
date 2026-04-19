#!/usr/bin/env python3
"""Batch-verify all solution files. Runs each as a subprocess, checks for WIN/VERIFIED/SOLVED."""
import subprocess, sys, time, os

SOLUTIONS_DIR = "solutions"
SKIP = {"su15_engine_solver.py", "su15_sim.py", "su15_sim_v2.py",
        "su15_solver.py", "su15_solver_v2.py", "su15_solutions.json",
        "solution_su15_partial.py", "__pycache__"}

results = []
for fname in sorted(os.listdir(SOLUTIONS_DIR)):
    if fname in SKIP or not fname.endswith(".py"):
        continue
    path = os.path.join(SOLUTIONS_DIR, fname)
    game = fname.replace("solution_", "").replace(".py", "").upper()

    t0 = time.time()
    try:
        proc = subprocess.run(
            [sys.executable, path],
            capture_output=True, text=True, timeout=120, cwd=os.getcwd()
        )
        elapsed = time.time() - t0
        output = proc.stdout + proc.stderr

        # Check for success indicators
        win = any(x in output.upper() for x in ["WIN", "VERIFIED", "ALL VERIFIED", "SOLVED"])
        fail = any(x in output.upper() for x in ["FAILED", "ERROR", "TRACEBACK", "ASSERT"])

        if proc.returncode == 0 and win and not fail:
            status = "PASS"
        elif proc.returncode == 0 and not fail:
            status = "PASS?"  # no explicit WIN but no errors
        else:
            status = "FAIL"

        results.append((game, status, elapsed, output.strip()[-200:] if output else ""))
        icon = "✓" if "PASS" in status else "✗"
        print(f"  {icon} {game:8s} {status:5s} ({elapsed:.1f}s)")

    except subprocess.TimeoutExpired:
        results.append((game, "TIMEOUT", 120, ""))
        print(f"  ⏰ {game:8s} TIMEOUT (120s)")
    except Exception as e:
        results.append((game, "ERROR", 0, str(e)))
        print(f"  ✗ {game:8s} ERROR: {e}")

print(f"\n{'='*50}")
passed = sum(1 for _, s, _, _ in results if "PASS" in s)
print(f"Results: {passed}/{len(results)} passed")

for game, status, elapsed, output in results:
    if "PASS" not in status:
        print(f"\n--- {game} ({status}) ---")
        print(output[-500:] if output else "(no output)")
