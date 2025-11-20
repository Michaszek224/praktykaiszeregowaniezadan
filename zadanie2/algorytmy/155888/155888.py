import sys
import os
import time
import random
from copy import deepcopy

NUM_MACHINES = 4

class Job:
    def __init__(self, job_id, p, r, w):
        self.id = job_id
        self.p = p  # czas trwania (processing time)
        self.r = r  # czas gotowości (release time)
        self.w = w  # waga/koszt (weight)
        self.ratio = w / p if p > 0 else float('inf')

    def __repr__(self):
        return f"Job(id={self.id}, p={self.p}, r={self.r}, w={self.w})"

def calculate_cost(jobs, schedule):
    job_map = {job.id: job for job in jobs}
    total_cost = 0
    
    for machine_schedule in schedule:
        machine_free_time = 0
        
        for job_id in machine_schedule:
            if job_id not in job_map:
                return float('inf') 

            task = job_map[job_id]
            
            start_time = max(machine_free_time, task.r)
            completion_time = start_time + task.p
            flow_time = completion_time - task.r # Fj = Cj - rj
            weighted_cost = task.w * flow_time
            total_cost += weighted_cost
            
            machine_free_time = completion_time
            
    return total_cost

def _run_greedy_strategy(jobs, priority_key):
    machines_time = [0] * NUM_MACHINES
    machines_schedule = [[] for _ in range(NUM_MACHINES)]
    unscheduled_jobs = jobs.copy()

    while unscheduled_jobs:
        min_time = min(machines_time)
        m_idx = machines_time.index(min_time)
        current_time = machines_time[m_idx]

        available = [j for j in unscheduled_jobs if j.r <= current_time]
        selected_job = None

        if available:
            available.sort(key=priority_key)
            selected_job = available[0]
            start_time = current_time
        else:
            unscheduled_jobs.sort(key=lambda j: (j.r, priority_key(j)))
            selected_job = unscheduled_jobs[0]
            start_time = selected_job.r

        completion_time = start_time + selected_job.p
        machines_time[m_idx] = completion_time
        machines_schedule[m_idx].append(selected_job.id)
        unscheduled_jobs.remove(selected_job)

    initial_cost = calculate_cost(jobs, machines_schedule)
    return machines_schedule, initial_cost


def generate_initial_schedule(jobs):
    best_cost = float('inf')
    best_schedule = None
    key_wspt = lambda j: (-j.ratio, j.p, j.r)
    schedule_wspt, cost_wspt = _run_greedy_strategy(jobs, key_wspt)

    if cost_wspt < best_cost:
        best_cost = cost_wspt
        best_schedule = schedule_wspt

    key_ert = lambda j: (j.r, -j.ratio)
    schedule_ert, cost_ert = _run_greedy_strategy(jobs, key_ert)

    if cost_ert < best_cost:
        best_cost = cost_ert
        best_schedule = schedule_ert
        
    return best_schedule, best_cost

def solve_scheduling(input_path, output_path, time_limit):
    jobs = []
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
            
            if not lines:
                print(f"Błąd: Plik {input_path} jest pusty.")
                return
            try:
                n_from_file = int(lines[0])
            except ValueError:
                n_from_file = 0
            for idx, line in enumerate(lines[1:], start=1):
                try:
                    parts = list(map(int, line.split()))
                    if len(parts) >= 3:
                        jobs.append(Job(idx, parts[0], parts[1], parts[2]))
                except ValueError:
                    print(f"Ostrzeżenie: pominięto linię {idx+1} z powodu błędnego formatu.")

    except FileNotFoundError:
        print(f"Błąd: Nie znaleziono pliku {input_path}")
        return
        
    n = len(jobs)
    if n == 0:
        print("Błąd: Brak zadań do przetworzenia.")
        return

    start_time = time.time()

    initial_schedule, initial_cost = generate_initial_schedule(jobs)
    
    best_schedule = initial_schedule
    best_cost = initial_cost
    
    time_elapsed = time.time() - start_time
    
    print(f"Koszt ostateczny : {best_cost}")
    print(f"Czas obliczeń: {time_elapsed:.4f} s")
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"{best_cost}\n")

            for i, schedule in enumerate(best_schedule):
                line = " ".join(map(str, schedule))
                if i < len(best_schedule) - 1:
                    f.write(line + "\n")  # dla wszystkich oprócz ostatniej
                else:
                    f.write(line)         # ostatnia linia bez \n

        print(f"Sukces! Wynik zapisano w: {output_path}")
    except IOError as e:
        print(f"Błąd zapisu pliku: {e}")

def main():
    
    if len(sys.argv) != 4:
        print("Użycie: python scheduler.py <plik_wejsciowy> <plik_wyjsciowy> <limit_czasowy_w_sekundach>")
        print("Przykład: python scheduler.py in_100.txt out_100.txt 9.5")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    try:
        time_limit = float(sys.argv[3])
        if time_limit <= 0:
            raise ValueError("Limit czasowy musi być dodatni.")
    except ValueError as e:
        print(f"Błąd argumentu: Nieprawidłowy limit czasowy. {e}")
        sys.exit(1)
    
    time_limit-=0.5
        
    solve_scheduling(input_file, output_file, time_limit)

if __name__ == "__main__":
    main()