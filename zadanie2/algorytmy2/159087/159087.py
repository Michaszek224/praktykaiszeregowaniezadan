import sys
import time
from pathlib import Path
import random

def read_instance(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    n = int(lines[0])
    jobs = []
    for line in lines[1:]:
        p, r, w = map(int, line.split())
        jobs.append((p, r, w))
    return n, jobs

def compute_cost(jobs, schedules):
    total = 0
    for seq in schedules:
        time_m = 0
        for j in seq:
            p, r, w = jobs[j - 1]
            start = max(time_m, r)
            completion = start + p
            total += w * (completion - r)
            time_m = completion
    return total

def is_valid_schedule(schedules, n):
    flat = []
    for seq in schedules:
        flat.extend(seq)
    return len(flat) == n and len(set(flat)) == n


def build_initial_solution(n, jobs):
    indexed = []
    for idx, (p, r, w) in enumerate(jobs, start = 1):
        key = (r / max(1, w), p)
        indexed.append((idx, p, r, w, key))

    indexed.sort(key=lambda x: x[4])

    schedules = [[], [], [], []]
    machine_times = [0, 0, 0, 0]

    for idx, p, r, w, _ in indexed:
        best_m = min(range(4), key=lambda m: max(machine_times[m], r) + p)
        start = max(machine_times[best_m], r)
        machine_times[best_m] = start + p
        schedules[best_m].append(idx)
    return schedules

def local_imporovement(jobs, schedules, time_limit, time_start):
    best = [list(seq) for seq in schedules]
    best_cost = compute_cost(jobs, best)
    n_jobs = sum(len(seq) for seq in schedules)

    while time.time() - time_start < time_limit:
        cand = [list(seq) for seq in best]
        op = random.randint(1, 3)

        if op == 1:
            #swap
            m = random.randint(0, 3)
            if len(cand[m]) > 1:
                i = random.randint(0, len(cand[m]) - 1)
                j = random.randint(0, len(cand[m]) - 1)
                cand[m][i], cand[m][j] = cand[m][j], cand[m][i]
        elif op == 2:
            #przeniesienie miedzy maszynami
            m_from = random.randint(0, 3)
            if len(cand[m_from]) > 0:
                m_to = random.randint(0, 3)
                idx = random.randrange(len(cand[m_from]))
                task = cand[m_from].pop(idx)
                cand[m_to].append(task)
        elif op == 3:
            #przeniesienie w obrebie maszyny
            m = random.randint(0, 3)
            if len(cand[m]) > 1:
                i = random.randrange(len(cand[m]))
                task = cand[m].pop(i)
                j = random.randrange(len(cand[m]) + 1)
                cand[m].insert(j, task)

        if not is_valid_schedule(cand, n_jobs):
            continue

        c = compute_cost(jobs, cand)
        if c < best_cost:
            best_cost = c
            best = cand

    return best


def compute_seed(n, jobs):
    s = n
    for p, r, w in jobs:
        s = (s * 1315423911) ^ (p * 31 + r * 131 + w * 131071)
        s &= 0xFFFFFFFF
    return s


def write_solutiion(path: Path, schedules, jobs):
    value = compute_cost(jobs, schedules)
    with open(path, "w", encoding="utf-8") as f:
        f.write(str(value) + "\n")
        for seq in schedules:
            if seq:
                f.write(" ".join(map(str, seq)) + "\n")
            else:
                f.write("\n")


def main():
    if len(sys.argv) != 4:
        print("Użycie: python <algorytm.py> <instancja_wejsciowa> <plik_wynikowy> <limit_czasu>")
        sys.exit(1)

    inst_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])
    limit_time = (float(sys.argv[3]) - 0.5)

    n, jobs = read_instance(inst_path)

    base_seed = compute_seed(n, jobs)

    seeds = [base_seed, base_seed ^ 0xA5A5A5A5, base_seed ^ 0x5A5A5A5A]

    best_initial = None
    best_initial_cost = float("inf")

    for sd in seeds:
        random.seed(sd)
        candidate = build_initial_solution(n, jobs)
        c = compute_cost(jobs, candidate)
        if c < best_initial_cost:
            best_initial_cost = c
            best_initial = candidate

    schedules = best_initial

    start_time = time.time()

    schedules = local_imporovement(jobs, schedules, limit_time, start_time)

    write_solutiion(out_path, schedules, jobs)


if __name__ == "__main__":
    main()

#python weryfikator.py 159087.py ./instancje_wejsciowe/in_159087_50.txt ./wyniki_algorytmu/out_159087_50.txt 159087.py ./instancje_wejsciowe/in_159087_100.txt ./wyniki_algorytmu/out_159087_100.txt 159087.py ./instancje_wejsciowe/in_159087_150.txt ./wyniki_algorytmu/out_159087_150.txt 159087.py ./instancje_wejsciowe/in_159087_200.txt ./wyniki_algorytmu/out_159087_200.txt 159087.py ./instancje_wejsciowe/in_159087_250.txt ./wyniki_algorytmu/out_159087_250.txt 159087.py ./instancje_wejsciowe/in_159087_300.txt ./wyniki_algorytmu/out_159087_300.txt 159087.py ./instancje_wejsciowe/in_159087_350.txt ./wyniki_algorytmu/out_159087_350.txt 159087.py ./instancje_wejsciowe/in_159087_400.txt ./wyniki_algorytmu/out_159087_400.txt 159087.py ./instancje_wejsciowe/in_159087_450.txt ./wyniki_algorytmu/out_159087_450.txt 159087.py ./instancje_wejsciowe/in_159087_500.txt ./wyniki_algorytmu/out_159087_500.txt