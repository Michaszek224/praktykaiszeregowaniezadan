import sys
import time
import heapq
from typing import Dict, List, Tuple, Any

JobData = Dict[int, Dict[str, Any]]
Schedule = List[List[int]]

def read_instance(input_path: str) -> Tuple[int, JobData] | None:
    """Wczytuje dane instancji z pliku i oblicza wskaźniki WSPT (ratio)."""
    jobs: JobData = {}
    try:
        with open(input_path, 'r') as f:
            lines = f.read().split()
            if not lines:
                raise ValueError("Pusty plik wejściowy")
            
            n = int(lines[0])
            idx = 1
            for i in range(1, n + 1):
                p = int(lines[idx])
                r = int(lines[idx+1])
                w = int(lines[idx+2])
                
                jobs[i] = {
                    'p': p, 
                    'r': r, 
                    'w': w, 
                    'ratio': w / p if p > 0 else 0,
                    'id': i 
                }
                idx += 3
        return n, jobs
    except Exception as e:
        print(f"Błąd wczytywania danych: {e}")
        return None, None

def simulate_schedule_and_get_cost(n: int, jobs: JobData, schedule: Schedule) -> Tuple[int, Dict[int, int]]:

    calculated_total_cost = 0
    # Słownik do przechowywania czasów zakończenia (Cj)
    completion_times: Dict[int, int] = {} 
    
    for m_idx, machine_jobs in enumerate(schedule):
        machine_finish_time = 0
        
        for job_id in machine_jobs:
            job = jobs[job_id]
            p_j = job['p']
            r_j = job['r']
            w_j = job['w']
            
            # Czas startu S_j = max(maszyna wolna, zadanie gotowe)
            start_t = max(machine_finish_time, r_j)
            
            # Czas zakończenia C_j
            completion_time = start_t + p_j
            completion_times[job_id] = completion_time
            
            # Czas przepływu F_j = C_j - r_j
            flow_time = completion_time - r_j
            
            # Koszt w_j * F_j
            weighted_flow_time = w_j * flow_time
            
            calculated_total_cost += weighted_flow_time
            
            # Następne zadanie na tej maszynie nie może zacząć się przed 'completion_time'
            machine_finish_time = completion_time
            
    return int(round(calculated_total_cost)), completion_times

def wspt_heuristic(n: int, jobs: JobData) -> Schedule:

    num_machines = 4
    # Kolejka priorytetowa maszyn: (czas_wolności_maszyny, indeks_maszyny)
    machine_pq = [(0, i) for i in range(num_machines)]
    
    schedule: Schedule = [[] for _ in range(num_machines)]
    
    jobs_scheduled_count = 0
    
    # Sortujemy wszystkie zadania raz wg r_j
    pending_jobs = sorted(jobs.values(), key=lambda j: j['r'])
    pending_jobs_idx = 0 

    available_jobs_pool: Dict[int, Dict[str, Any]] = {} 

    while jobs_scheduled_count < n:
  
        current_time, current_machine_idx = heapq.heappop(machine_pq)

        while pending_jobs_idx < n and pending_jobs[pending_jobs_idx]['r'] <= current_time:
            job = pending_jobs[pending_jobs_idx]
            available_jobs_pool[job['id']] = job
            pending_jobs_idx += 1
            
        selected_job_id = None
        
        if available_jobs_pool:
            def get_wspt_key(j_id):
                job = available_jobs_pool[j_id]
                return (job['ratio'], job['w'])
                
            selected_job_id = max(available_jobs_pool.keys(), key=get_wspt_key)
            
        else:
            if pending_jobs_idx < n:
                next_release_time = pending_jobs[pending_jobs_idx]['r']
                heapq.heappush(machine_pq, (next_release_time, current_machine_idx))
                continue
            else:
                heapq.heappush(machine_pq, (current_time, current_machine_idx))
                break 

        if selected_job_id is not None:
            job = available_jobs_pool.pop(selected_job_id) 
            
            # Obliczanie czasów zakończenia (potrzebne do aktualizacji machine_pq)
            start_t = max(current_time, job['r']) 
            finish_t = start_t + job['p']
            
            # Aktualizacja harmonogramu
            schedule[current_machine_idx].append(selected_job_id)
            jobs_scheduled_count += 1
            
            heapq.heappush(machine_pq, (finish_t, current_machine_idx))

    return schedule


def local_search_optimization(n: int, jobs: JobData, initial_schedule: Schedule, time_limit_end: float) -> Schedule:

    current_schedule = [list(m) for m in initial_schedule] 
    current_cost, _ = simulate_schedule_and_get_cost(n, jobs, current_schedule)
    
    best_schedule = current_schedule
    best_cost = current_cost
    
    # print(f"--- Local Search Start ---")
    # print(f"Koszt startowy (WSPT): {best_cost}")

    iterations = 0
    
    while time.time() < time_limit_end:
        
        improvement_found_in_cycle = False
        iterations += 1
        
        # --- 1. RUCH INTRA-MACHINE SWAP (Zamiana sąsiadów na tej samej maszynie) ---
        for m_idx in range(4):
            if time.time() >= time_limit_end: break
            machine_jobs = current_schedule[m_idx]
            if len(machine_jobs) < 2: continue
            
            for i in range(len(machine_jobs) - 1):
                if time.time() >= time_limit_end: break

                # Kopia harmonogramu do testu
                temp_schedule = [list(m) for m in current_schedule]
                
                # Wykonaj ruch (swap) sąsiadów
                temp_schedule[m_idx][i], temp_schedule[m_idx][i+1] = \
                    temp_schedule[m_idx][i+1], temp_schedule[m_idx][i]
                
                new_cost, _ = simulate_schedule_and_get_cost(n, jobs, temp_schedule)
                
                if new_cost < current_cost:
                    current_cost = new_cost
                    current_schedule = temp_schedule
                    improvement_found_in_cycle = True
                    
                    if new_cost < best_cost:
                        best_cost = new_cost
                        best_schedule = [list(m) for m in temp_schedule] 
                        # print(f"  -> POPRAWA (Intra-Swap) w iter. {iterations}, Koszt: {best_cost}")
                    
                    # Akceptacja First Improvement
                    break 

            if improvement_found_in_cycle: break 

        if improvement_found_in_cycle:
            continue 

        # --- 2. RUCH INTER-MACHINE SWAP (Zamiana zadań między różnymi maszynami) ---
        
        for m1 in range(4):
            if time.time() >= time_limit_end: break
            for i in range(len(current_schedule[m1])):
                if time.time() >= time_limit_end: break
                
                for m2 in range(m1 + 1, 4):
                    if time.time() >= time_limit_end: break
                    for j in range(len(current_schedule[m2])):
                        if time.time() >= time_limit_end: break
                        
                        # Kopia harmonogramu do testu
                        temp_schedule = [list(m) for m in current_schedule]
                        
                        # Wykonaj ruch (swap)
                        j1 = temp_schedule[m1][i]
                        j2 = temp_schedule[m2][j]
                        temp_schedule[m1][i] = j2
                        temp_schedule[m2][j] = j1
                        
                        new_cost, _ = simulate_schedule_and_get_cost(n, jobs, temp_schedule)
                        
                        if new_cost < current_cost:
                            current_cost = new_cost
                            current_schedule = temp_schedule
                            improvement_found_in_cycle = True
                            
                            if new_cost < best_cost:
                                best_cost = new_cost
                                best_schedule = [list(m) for m in temp_schedule]
                                # print(f"  -> POPRAWA (Inter-Swap) w iter. {iterations}, Koszt: {best_cost}")
                            
                            # Akceptacja First Improvement
                            break
                    if improvement_found_in_cycle: break
                if improvement_found_in_cycle: break
            if improvement_found_in_cycle: break
        
        # Jeśli nie znaleziono poprawy w całym cyklu (Intra i Inter)
        if not improvement_found_in_cycle:
             pass
             
    # print(f"--- Local Search Koniec ---")
    # print(f"Najlepszy znaleziony koszt: {best_cost} (po {iterations} iteracjach)")
    return best_schedule

def solve_instance(input_path: str, output_path: str, time_limit: float):
    """
    Główna funkcja rozwiązująca problem. 
    Krok 1: WSPT (Konstrukcja). Krok 2: Local Search (Optymalizacja).
    """
    start_time = time.time()
    n, jobs = read_instance(input_path)
    if not jobs: return

    # 1. GENEROWANIE ROZWIĄZANIA STARTOWE (Heurystyka WSPT)
    initial_schedule = wspt_heuristic(n, jobs)
    
    # 2. LOKALNE PRZESZUKIWANIE (wykorzystanie limitu czasu)
    
    # Używamy 90% limitu czasu na optymalizację
    optimization_limit = time_limit * 0.9
    time_limit_end = start_time + optimization_limit
    
    # Uruchamiamy Local Search z pozostałym czasem
    final_schedule = local_search_optimization(n, jobs, initial_schedule, time_limit_end)
            
    # 3. OBLICZENIE KOŃCOWEGO KRYTERIUM (dla najlepszego znalezionego harmonogramu)
    final_criterion_value, _ = simulate_schedule_and_get_cost(n, jobs, final_schedule)
            
    # 4. Zapisywanie wyników
    try:
        with open(output_path, 'w') as f:
            f.write(f"{final_criterion_value}\n")
            
            for machine_jobs in final_schedule:
                line = " ".join(map(str, machine_jobs))
                f.write(f"{line}\n")
                
    except Exception as e:
        print(f"Błąd zapisu wyników: {e}")

def main():
    if len(sys.argv) < 4:
        print(f"Użycie: python {sys.argv[0]} <input_file> <output_file> <time_limit>")
        return

    input_file = sys.argv[1] 
    output_file = sys.argv[2] 
    
    try:
        time_limit = float(sys.argv[3])
    except (ValueError, IndexError):
        print("BŁĄD: Nie podano limitu czasu lub jest on nieprawidłowy.")
        sys.exit(1)

    solve_instance(input_file, output_file, time_limit)

if __name__ == "__main__":
    main()