from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple
import time
import sys

@dataclass
class Instance:
    n: int
    s: int
    p: List[int]
    d: List[int]

@dataclass
class Solution:
    obj: int
    batches: List[List[int]]

def read_instance(path: Path) -> Instance:
    raw = [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    n, s = map(int, raw[0].split())
    p = [0]*(n+1); d = [0]*(n+1)
    for i in range(1, n+1):
        pj, dj = map(int, raw[i].split())
        p[i], d[i] = pj, dj
    return Instance(n=n, s=s, p=p, d=d)

def write_solution_strict(path: Path, sol: Solution) -> None:
    lines = [str(sol.obj), str(len(sol.batches))]
    lines += [" ".join(str(j) for j in B) for B in sol.batches]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

def compute_total_tardiness(inst: Instance, batches: List[List[int]]) -> int:
    t = 0; total = 0; seen = set()
    for b_idx, B in enumerate(batches, start=1):
        if b_idx > 1: t += inst.s
        t += sum(inst.p[j] for j in B)
        for j in B:
            total += max(0, t - inst.d[j]); seen.add(j)
    return total

def edd_order(inst: Instance) -> List[int]:
    return sorted(range(1, inst.n + 1), key=lambda j: (inst.d[j], j))

def dp_optimal_batches_for_order(inst: Instance, order: List[int]) -> Tuple[int, List[List[int]]]:
    n, s, p, d = inst.n, inst.s, inst.p, inst.d
    job = [0] + order[:]
    pref_p = [0]*(n+1)
    for i in range(1, n+1):
        pref_p[i] = pref_p[i-1] + p[job[i]]

    INF = 10**18
    DP   = [[INF]*(n+1) for _ in range(n+1)]
    PREV = [[-1]*(n+1) for _ in range(n+1)]
    DP[0][0] = 0

    base_K = min(n, 64)

    for j in range(1, n+1):
        b_max = min(j, base_K)
        for b in range(1, b_max+1):
            C = pref_p[j] + s*(b-1)
            roll = 0
            for i in range(b, j+1):
                tmp = C - d[job[i]]
                if tmp > 0: roll += tmp

            best = INF; best_k = -1
            for k in range(b-1, j):
                cand = DP[k][b-1] + roll
                if cand < best:
                    best = cand; best_k = k
                if k+1 <= j:
                    tmp = C - d[job[k+1]]
                    if tmp > 0: roll -= tmp

            DP[j][b] = best
            PREV[j][b] = best_k

    best_b = 1; best_val = DP[n][1]
    for b in range(2, n+1):
        if DP[n][b] < best_val:
            best_val = DP[n][b]; best_b = b

    batches = []
    j = n; b = best_b
    while j > 0 and b > 0:
        k = PREV[j][b]
        assert k >= 0
        B = [job[i] for i in range(k+1, j+1)]
        batches.append(B)
        j = k; b -= 1
    batches.reverse()
    return best_val, batches

def solve(inst: Instance) -> Solution:
    order = edd_order(inst)
    obj, batches = dp_optimal_batches_for_order(inst, order)
    return Solution(obj=obj, batches=batches)

def main():
    if len(sys.argv) != 4:
        print("Usage: solver.py <input_file> <output_file> <time_limit>")
        sys.exit(1)

    inst_path = Path(sys.argv[1])
    out_path  = Path(sys.argv[2])
    time_limit = float(sys.argv[3])

    inst = read_instance(inst_path)
    start = time.time()
    sol = solve(inst)
    end = time.time()

    write_solution_strict(out_path, sol)
    elapsed = end - start

    print(f"K={len(sol.batches)}, sum_T={sol.obj} -> {out_path}. Time={elapsed:.3f}s")
    if elapsed > time_limit:
        print(f"Error: algorithm took {elapsed:.3f}s, but the limit was {time_limit:.3f}s.")

if __name__ == "__main__":
    main()
