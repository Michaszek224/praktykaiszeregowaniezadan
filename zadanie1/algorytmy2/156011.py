import sys
import random
import time
from typing import List, Tuple

def random_solver(jobs:List[Tuple[int,int]], s:int, time_limit:float) -> Tuple[int, List[List[int]]]:
    n = len(jobs)
    
    best_sum = float('inf')
    best_batches = []
    
    start_time = time.time()
    iterations = 0
    
    while time.time() - start_time < time_limit:
        iterations += 1
        job_indices = list(range(1, n+1))
        
        num_batches = random.randint(1, n)
        
        random.shuffle(job_indices)
        
        batches = [[] for _ in range(num_batches)]
        
        for job_idx in job_indices:
            batch_idx = random.randint(0, num_batches-1)
            batches[batch_idx].append(job_idx)
        
        batches = [batch for batch in batches if batch]
        
        sumDj = compute_sumDj_from_batches(jobs, s, batches)
        
        if sumDj < best_sum:
            best_sum = sumDj
            best_batches = batches.copy()
            print(f"Iteration {iterations}: Found better solution with delay {best_sum}")

    print(f"Total iterations: {iterations}")
    print(f"Best delay found: {best_sum}")
    return best_sum, best_batches

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
    return s, jobs

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
    time_limit = time_limit - 1
    print(f"Running with time limit: {time_limit} seconds")
    s, jobs = read_instance(infile)
    sumDj, batches = random_solver(jobs, s, time_limit)
    write_solution(outfile, sumDj, batches)
    print(f"Final solution written to {outfile} with total delay {sumDj}")

if __name__ == '__main__':
    main()