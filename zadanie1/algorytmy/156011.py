import sys
from typing import List, Tuple
import time

def heuristic_solver(jobs:List[Tuple[int,int]], s:int) -> Tuple[int, List[List[int]]]:
    n = len(jobs)
    indexed = [(i+1, jobs[i][0], jobs[i][1]) for i in range(n)]
    indexed.sort(key=lambda x: x[2])
    batches = []
    cur_batch = []
    for idx,p,d in indexed:
        if not cur_batch:
            cur_batch = [idx]
        else:
            sumA = compute_sumDj_from_batches(jobs, s, batches + [cur_batch + [idx]])
            sumB = compute_sumDj_from_batches(jobs, s, batches + [cur_batch, [idx]])
            if sumA <= sumB:
                cur_batch.append(idx)
            else:
                batches.append(cur_batch)
                cur_batch = [idx]
    if cur_batch:
        batches.append(cur_batch)
    sumDj = compute_sumDj_from_batches(jobs, s, batches)
    return sumDj, batches


def read_instance(filepath: str):
    with open(filepath, 'r') as f:
        parts = f.read().strip().split()
    if len(parts) < 2:
        raise ValueError("Niepoprawny plik wejściowy (brak n i s).")
    n = int(parts[0]); s = int(parts[1])
    if len(parts) != 2 + 2*n:
        raise ValueError(f"Niepoprawna liczba danych w pliku wejściowym (oczekiwano {2+2*n}, jest {len(parts)}).")
    jobs = []
    idx = 2
    for _ in range(n):
        p = int(parts[idx]); d = int(parts[idx+1]); idx += 2
        jobs.append((p, d))
    return n, s, jobs


def write_solution(filepath: str, sumDj: int, batches: List[List[int]]):
    with open(filepath,'w') as f:
        f.write(f"{sumDj}\n")
        f.write(f"{len(batches)}\n")
        for batch in batches:
            if batch:
                f.write(" ".join(str(x) for x in batch) + "\n")
            else:
                f.write("\n")


def compute_sumDj_from_batches(jobs: List[Tuple[int,int]], s: int, batches: List[List[int]]) -> int:
    time = 0
    total = 0
    first = True
    for batch in batches:
        if not first:
            time += s
        first = False
        p_sum = sum(jobs[j-1][0] for j in batch)
        time += p_sum
        for j in batch:
            d = jobs[j-1][1]
            total += max(0, time - d)
    return total


def main():
    if len(sys.argv) != 4:
        print("Użycie: python program.py <plik_wejściowy> <plik_wyjściowy> <limit_czasu>")
        sys.exit(1)
    
    infile = sys.argv[1]
    outfile = sys.argv[2]
    time_limit = float(sys.argv[3])
    
    start = time.time()
    n, s, jobs = read_instance(infile)
    sumDj, batches = heuristic_solver(jobs, s)
    write_solution(outfile, sumDj, batches)
    end = time.time()
    elapsed = end - start
    elapsed = round(elapsed, 2)
    if elapsed > float(time_limit):
        print(f"Przekroczono czas")
    else:   
        print(f"Zapisano: {outfile} sumDj={sumDj} batches={len(batches)} time={elapsed}")


if __name__ == '__main__':
    main()

