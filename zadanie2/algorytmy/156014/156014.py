import sys
import time
import heapq
from typing import Dict, List, Tuple, Any

JobData = Dict[int, Dict[str, Any]]
Schedule = List[List[int]]

def read_instance(input_path: str) -> Tuple[int, JobData] | None:
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
                    'scheduled': False, 
                    'id': i 
                }
                idx += 3
        return n, jobs
    except Exception as e:
        print(f"Błąd wczytywania danych: {e}")
        return None, None

def calculate_criterion(n: int, jobs: JobData, schedule: Schedule) -> int:
    calculated_total_cost = 0
    
    for m_idx, machine_jobs in enumerate(schedule):
        machine_finish_time = 0
        
        for job_id in machine_jobs:
            job = jobs[job_id]
            p_j = job['p']
            r_j = job['r']
            w_j = job['w']

            start_t = max(machine_finish_time, r_j)

            completion_time = start_t + p_j
  
            flow_time = completion_time - r_j

            weighted_flow_time = w_j * flow_time
            
            calculated_total_cost += weighted_flow_time

            machine_finish_time = completion_time

    return int(round(calculated_total_cost))

def solve_instance(input_path: str, output_path: str, time_limit: float):
    start_time = time.time()
    n, jobs = read_instance(input_path)
    if not jobs: return

    num_machines = 4
    machine_pq = [(0, i) for i in range(num_machines)]
    
    schedule: Schedule = [[] for _ in range(num_machines)]
    
    jobs_scheduled_count = 0
    
    pending_jobs = sorted(jobs.values(), key=lambda j: j['r'])
    pending_jobs_idx = 0 

    available_jobs_pool: Dict[int, Dict[str, Any]] = {} 

    while jobs_scheduled_count < n:

        if time.time() - start_time > time_limit:
            print(f"OSTRZEŻENIE: Przekroczono limit czasu ({time_limit}s). Zapisuję częściowe rozwiązanie.")
            break 

        current_time, current_machine_idx = heapq.heappop(machine_pq)
        
        # Krok B: Przenieś zadania z 'pending' do 'available'
        # Zwiększamy pulę dostępnych zadań, aż przekroczymy czas maszyny
        while pending_jobs_idx < n and pending_jobs[pending_jobs_idx]['r'] <= current_time:
            job = pending_jobs[pending_jobs_idx]
            available_jobs_pool[job['id']] = job
            pending_jobs_idx += 1
            
        selected_job_id = None
        
        if available_jobs_pool:
            # W tym miejscu stosujemy regułę WSPT
            def get_wspt_key(j_id):
                job = available_jobs_pool[j_id]
                # Klucz: (ratio, w), aby rozstrzygnąć remisy wyższą wagą.
                return (job['ratio'], job['w'])
                
            selected_job_id = max(available_jobs_pool.keys(), key=get_wspt_key)
            
        else:
            
            if pending_jobs_idx < n:
                # Następny r_j, na który musimy czekać
                next_release_time = pending_jobs[pending_jobs_idx]['r']
                
                # Maszyna czeka do czasu nadejścia tego zadania
                heapq.heappush(machine_pq, (next_release_time, current_machine_idx))
                continue # Przejdź do kolejnej maszyny.
            else:
                heapq.heappush(machine_pq, (current_time, current_machine_idx))
                break 

        if selected_job_id is not None:
            
            job = available_jobs_pool.pop(selected_job_id) # Usuń z puli dostępnych
            
            # Oblicz czas startu/końca
            # Czas startu: max(wolna maszyna, gotowe zadanie) -> Tutaj r_j <= current_time, więc start_t = current_time
            start_t = max(current_time, job['r']) 
            finish_t = start_t + job['p']
            
            # Zaktualizuj stan harmonogramu
            schedule[current_machine_idx].append(selected_job_id)
            jobs_scheduled_count += 1
            
            # Włóż maszynę z powrotem do kolejki z nowym czasem zakończenia
            heapq.heappush(machine_pq, (finish_t, current_machine_idx))

    final_criterion_value = calculate_criterion(n, jobs, schedule)

    try:
        with open(output_path, 'w') as f:
            f.write(f"{final_criterion_value}\n")

            for machine_jobs in schedule:
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
        print("Nie podano limitu czasu")
        return 0

    solve_instance(input_file, output_file, time_limit)

if __name__ == "__main__":
    main()