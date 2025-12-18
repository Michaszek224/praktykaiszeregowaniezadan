import argparse
import math
import random
import time
from pathlib import Path


def read_instance(path: Path):
    lines = path.read_text(encoding="utf-8").split()
    idx = 0
    n = int(lines[idx]); idx += 1
    P = []
    R = []
    for _ in range(n):
        p = tuple(map(int, lines[idx:idx+4]))
        r = int(lines[idx+4])
        P.append(p)
        R.append(r)
        idx += 5
    S = []
    for _ in range(n):
        S.append(list(map(int, lines[idx:idx+n])))
        idx += n
    return n, P, R, S


def evaluate(perm, P, R, S):
    end_m = [0, 0, 0, 0]
    prev = None

    for j in perm:
        p1, p2, p3, p4 = P[j]
        rj = R[j]
        setup = S[prev][j] if prev is not None else 0

        t1 = max(rj, end_m[0] + setup)
        e1 = t1 + p1

        t2 = max(e1, end_m[1] + setup)
        e2 = t2 + p2

        t3 = max(e2, end_m[2] + setup)
        e3 = t3 + p3

        t4 = max(e3, end_m[3] + setup)
        e4 = t4 + p4

        end_m = [e1, e2, e3, e4]
        prev = j

    return end_m[3]


def neh_sdst(n, P, R, S):
    weights = [(j, sum(P[j])) for j in range(n)]
    weights.sort(key=lambda x: -x[1])
    ordered = [j for j, _ in weights]

    pi = [ordered[0]]
    for j in ordered[1:]:
        best_pos = None
        best_cmax = float("inf")
        for i in range(len(pi) + 1):
            candidate = pi[:i] + [j] + pi[i:]
            cmax = evaluate(candidate, P, R, S)
            if cmax < best_cmax:
                best_cmax = cmax
                best_pos = i
        pi.insert(best_pos, j)

    return pi, evaluate(pi, P, R, S)


def neighbor_swap(perm, rnd: random.Random):
    n = len(perm)
    if n < 2:
        return perm[:]
    i = rnd.randrange(n)
    j = rnd.randrange(n - 1)
    if j >= i:
        j += 1
    cand = perm[:]
    cand[i], cand[j] = cand[j], cand[i]
    return cand


def neighbor_insert(perm, rnd: random.Random):
    n = len(perm)
    if n < 2:
        return perm[:]
    i = rnd.randrange(n)
    j = rnd.randrange(n)
    while j == i:
        j = rnd.randrange(n)
    cand = perm[:]
    job = cand.pop(i)
    cand.insert(j, job)
    return cand


def estimate_initial_temperature(perm, P, R, S, rnd: random.Random, samples: int = 30):
    base = evaluate(perm, P, R, S)
    deltas = []
    for _ in range(samples):
        cand = neighbor_swap(perm, rnd)
        val = evaluate(cand, P, R, S)
        d = val - base
        if d > 0:
            deltas.append(d)
    if not deltas:
        return 1.0
    return float(sum(deltas)) / len(deltas)


def sa_improve(
    perm0, P, R, S,
    time_limit: float,
    seed: int,
    alpha: float = 0.995,
    move: str = "mix",
    verbose: bool = False
):
    rnd = random.Random(seed)
    start_time = time.time()

    cur_perm = perm0[:]
    cur_val = evaluate(cur_perm, P, R, S)

    best_perm = cur_perm[:]
    best_val = cur_val

    T0 = estimate_initial_temperature(cur_perm, P, R, S, rnd)
    T = T0

    it = 0
    accepted = 0

    while (time.time() - start_time) < time_limit:
        it += 1

        if move == "swap":
            cand_perm = neighbor_swap(cur_perm, rnd)
        elif move == "insert":
            cand_perm = neighbor_insert(cur_perm, rnd)
        else:
            cand_perm = neighbor_insert(cur_perm, rnd) if (rnd.random() < 0.5) else neighbor_swap(cur_perm, rnd)

        cand_val = evaluate(cand_perm, P, R, S)
        delta = cand_val - cur_val

        accept = False
        if delta <= 0:
            accept = True
        else:
            if T > 1e-12:
                x = -delta / T
                if x > -700:
                    accept = (rnd.random() < math.exp(x))

        if accept:
            cur_perm = cand_perm
            cur_val = cand_val
            accepted += 1
            if cur_val < best_val:
                best_val = cur_val
                best_perm = cur_perm[:]

        T *= alpha
        if T < 1e-12:
            T = 1e-12

        if verbose and it % 200 == 0:
            elapsed = time.time() - start_time
            print(f"[SA] t={elapsed:.2f}s it={it} acc={accepted} cur={cur_val} best={best_val} T={T:.4g}")

    return best_perm, best_val


def save_solution(path: Path, perm, cmax):
    line1 = str(cmax)
    line2 = " ".join(str(j + 1) for j in perm)  # 1..n
    path.write_text(f"{line1}\n{line2}\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("time", type=float, nargs="?", default=None)
    args = ap.parse_args()

    n, P, R, S = read_instance(args.input)

    total_time = args.time if args.time is not None else (n / 10.0)
    t0 = time.time()

    perm, cmax = neh_sdst(n, P, R, S)

    elapsed = time.time() - t0
    remaining = total_time - elapsed

    if remaining <= 0:
        save_solution(args.output, perm, cmax)
        return

    perm, cmax = sa_improve(
        perm0=perm, P=P, R=R, S=S,
        time_limit=remaining * 0.95,
        seed=1234,
        alpha=0.995,
        move="mix",
        verbose=False
    )

    save_solution(args.output, perm, cmax)

if __name__ == "__main__":
    main()
