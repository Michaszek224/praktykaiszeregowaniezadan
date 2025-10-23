from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple
import time
import sys
import random, copy

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
    p = [0] * (n + 1); d = [0] * (n + 1)
    for i in range(1, n + 1):
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

def modified_order(inst: Instance) -> List[int]:
    tasks = sorted(range(1, inst.n + 1), key=lambda j: inst.d[j])
    on_time, late = [], []
    time_sum = 0
    for j in tasks:
        on_time.append(j)
        time_sum += inst.p[j]
        while on_time and time_sum > inst.d[on_time[-1]]:
            max_p_j = max(on_time, key=lambda x: inst.p[x])
            on_time.remove(max_p_j)
            late.append(max_p_j)
            time_sum -= inst.p[max_p_j]
    return on_time + sorted(late, key=lambda j: inst.p[j])

def dp_optimal_batches_for_order(inst: Instance, order: List[int]) -> Tuple[int, List[List[int]]]:
    n, s, p, d = inst.n, inst.s, inst.p, inst.d
    job = [0] + order[:]
    pref_p = [0] * (n + 1)
    for i in range(1, n + 1):
        pref_p[i] = pref_p[i - 1] + p[job[i]]

    INF = 10 ** 18
    DP = [[INF] * (n + 1) for _ in range(n + 1)]
    PREV = [[-1] * (n + 1) for _ in range(n + 1)]
    DP[0][0] = 0

    for j in range(1, n + 1):
        for b in range(1, j + 1):
            C = pref_p[j] + s * (b - 1)
            roll = 0
            for i in range(b, j + 1):
                tmp = C - d[job[i]]
                if tmp > 0: roll += tmp

            best = INF; best_k = -1
            for k in range(b - 1, j):
                cand = DP[k][b - 1] + roll
                if cand < best:
                    best = cand; best_k = k
                if k + 1 <= j:
                    tmp = C - d[job[k + 1]]
                    if tmp > 0: roll -= tmp

            DP[j][b] = best
            PREV[j][b] = best_k

    best_b = 1; best_val = DP[n][1]
    for b in range(2, n + 1):
        if DP[n][b] < best_val:
            best_val = DP[n][b]; best_b = b

    batches = []
    j = n; b = best_b
    while j > 0 and b > 0:
        k = PREV[j][b]
        assert k >= 0
        B = [job[i] for i in range(k + 1, j + 1)]
        batches.append(B)
        j = k; b -= 1
    batches.reverse()
    return best_val, batches

def local_search(inst: Instance, batches: List[List[int]], time_limit: float, start_time: float) -> Tuple[int, List[List[int]]]:
    best_batches = copy.deepcopy(batches)
    best_val = compute_total_tardiness(inst, best_batches)

    while time.time() - start_time < time_limit * 0.95:
        new_batches = copy.deepcopy(best_batches)
        if len(new_batches) < 2: break
        bi, bj = random.sample(range(len(new_batches)), 2)
        if not new_batches[bi] or not new_batches[bj]: continue
        i, j = random.randrange(len(new_batches[bi])), random.randrange(len(new_batches[bj]))
        new_batches[bi][i], new_batches[bj][j] = new_batches[bj][j], new_batches[bi][i]
        new_val = compute_total_tardiness(inst, new_batches)
        if new_val < best_val:
            best_val, best_batches = new_val, new_batches

    return best_val, best_batches

def solve(inst: Instance, time_limit: float) -> Solution:
    start = time.time()
    order = modified_order(inst)
    obj, batches = dp_optimal_batches_for_order(inst, order)
    obj2, batches2 = local_search(inst, batches, time_limit, start)
    if obj2 < obj:
        obj, batches = obj2, batches2
    return Solution(obj=obj, batches=batches)

def main():
    if len(sys.argv) != 4:
        print("Usage: solver.py <input_file> <output_file> <time_limit>")
        sys.exit(1)

    inst_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])
    time_limit = float(sys.argv[3])

    inst = read_instance(inst_path)
    sol = solve(inst, time_limit)
    write_solution_strict(out_path, sol)
    print(f"K={len(sol.batches)}, sum_T={sol.obj} -> {out_path}.")

if __name__ == "__main__":
    main()
