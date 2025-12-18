#!/usr/bin/env python3
import time
import os
import random
import sys

# ==========================================
# ŁADOWANIE DANYCH
# ==========================================

class Instance:
    def __init__(self, n, jobs, setups):
        self.n = n
        self.jobs = jobs      # Lista zadań (słowniki)
        self.setups = setups  # Macierz

def load_instance(filepath):
    try:
        with open(filepath, 'r') as f:
            data = f.read().split()
        
        if not data: return None
        iterator = iter(data)
        
        n = int(next(iterator))
        jobs = []
        for i in range(n):
            p = [int(next(iterator)) for _ in range(4)]
            r = int(next(iterator))
            # Przechowujemy jako prosta krotka dla szybkości: (id, p1, p2, p3, p4, r, original_idx)
            jobs.append({
                'id': i + 1,
                'p': p,
                'r': r,
                'idx': i
            })
            
        setups = []
        for _ in range(n):
            row = [int(next(iterator)) for _ in range(n)]
            setups.append(row)
            
        return Instance(n, jobs, setups)
    except Exception as e:
        print(f"Blad odczytu {filepath}: {e}", file=sys.stderr)
        return None

# ==========================================
# SZYBKA FUNKCJA LICZĄCA CMAX
# ==========================================
def compute_cmax(instance, sequence_indices):
    jobs = instance.jobs
    setups = instance.setups
    
    m0, m1, m2, m3 = 0, 0, 0, 0
    prev_idx = -1
    
    for idx in sequence_indices:
        job = jobs[idx]
        p = job['p']
        r = job['r']
        
        s = 0 if prev_idx == -1 else setups[prev_idx][idx]
        
        # Maszyna 1
        start0 = m0 + s
        if r > start0: start0 = r
        m0 = start0 + p[0]
        
        # Maszyna 2
        start1 = m1 + s
        if m0 > start1: start1 = m0
        m1 = start1 + p[1]
        
        # Maszyna 3
        start2 = m2 + s
        if m1 > start2: start2 = m1
        m2 = start2 + p[2]
        
        # Maszyna 4
        start3 = m3 + s
        if m2 > start3: start3 = m2
        m3 = start3 + p[3]
        
        prev_idx = idx
        
    return m3

# ==========================================
# ALGORYTM GŁÓWNY (Greedy + Local Search)
# ==========================================

def solve(instance, time_limit):
    start_time = time.time()
    n = instance.n
    jobs = instance.jobs
    setups = instance.setups
    
    # ---------------------------------------------------------
    # FAZA 1: Szybki Greedy (Best Fit)
    # ---------------------------------------------------------
    available = set(range(n))
    schedule_indices = []
    
    current_m = [0, 0, 0, 0]
    last_idx = -1
    
    for _ in range(n):
        best_idx = -1
        best_finish = float('inf')
        best_new_m = None
        
        for cand_idx in available:
            job = jobs[cand_idx]
            p = job['p']
            r = job['r']
            
            s = 0 if last_idx == -1 else setups[last_idx][cand_idx]
            
            start0 = current_m[0] + s
            if r > start0: start0 = r
            end0 = start0 + p[0]
            
            start1 = current_m[1] + s
            if end0 > start1: start1 = end0
            end1 = start1 + p[1]
            
            start2 = current_m[2] + s
            if end1 > start2: start2 = end1
            end2 = start2 + p[2]
            
            start3 = current_m[3] + s
            if end2 > start3: start3 = end2
            end3 = start3 + p[3]
            
            if end3 < best_finish:
                best_finish = end3
                best_idx = cand_idx
                best_new_m = [end0, end1, end2, end3]
            elif end3 == best_finish:
                if end0 < best_new_m[0]:
                    best_idx = cand_idx
                    best_new_m = [end0, end1, end2, end3]
        
        schedule_indices.append(best_idx)
        available.remove(best_idx)
        current_m = best_new_m
        last_idx = best_idx

    current_cmax = current_m[3]
    
    # ---------------------------------------------------------
    # FAZA 2: Local Search (Ulepszanie)
    # ---------------------------------------------------------
    # Wykonujemy, dopóki całkowity czas nie przekroczy time_limit
    
    # Małe zabezpieczenie, żeby pętla wykonała się chociaż raz, jeśli limit jest bardzo mały
    # Ale w ogólnym przypadku sprawdzamy czas
    
    while (time.time() - start_time) < time_limit:
        i, j = random.sample(range(n), 2)
        
        # Swap
        schedule_indices[i], schedule_indices[j] = schedule_indices[j], schedule_indices[i]
        
        new_cmax = compute_cmax(instance, schedule_indices)
        
        if new_cmax < current_cmax:
            current_cmax = new_cmax
        else:
            # Revert
            schedule_indices[i], schedule_indices[j] = schedule_indices[j], schedule_indices[i]

    final_ids = [jobs[idx]['id'] for idx in schedule_indices]
    return current_cmax, final_ids

# ==========================================
# ZAPIS I MAIN
# ==========================================

def save_solution(cmax, schedule, filepath):
    # Tworzenie katalogu wyjściowego, jeśli nie istnieje
    out_dir = os.path.dirname(filepath)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir)

    with open(filepath, 'w') as f:
        f.write(f"{cmax}\n")
        f.write(" ".join(map(str, schedule)) + "\n")

def main():
    # Oczekiwane argumenty: skrypt.py input_file output_file time_limit
    if len(sys.argv) < 4:
        print("Uzycie: ./alg <input_file> <output_file> <time_limit>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    try:
        time_limit = min(float(sys.argv[3]),4.0)
    except ValueError:
        print("Limit czasu musi byc liczba.", file=sys.stderr)
        sys.exit(1)
    # Ładowanie instancji
    instance = load_instance(input_path)
    if not instance:
        print(f"Nie udalo sie zaladowac instancji z {input_path}", file=sys.stderr)
        sys.exit(1)
            
    # Rozwiązywanie
    cmax, schedule = solve(instance, time_limit)
    
    # Zapis
    save_solution(cmax, schedule, output_path)
    
    # Opcjonalnie: wypisanie wyniku na stderr (żeby nie psuć stdout testerce)
    # print(f"Instancja n={instance.n}, Cmax={cmax}, TimeLimit={time_limit}s", file=sys.stderr)

if __name__ == "__main__":
    main()