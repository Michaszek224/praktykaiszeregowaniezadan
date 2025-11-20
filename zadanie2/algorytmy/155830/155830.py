
import sys
from typing import List, Dict, Tuple, Any

TaskDict = Dict[int, Dict[str, int]]
MachineSchedules = List[List[int]]

def load_instance(filename: str) -> Tuple[int, TaskDict]:
    try:
        with open(filename, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]

        if len(lines) < 1:
            raise ValueError("Plik instancji jest pusty")

        n = int(lines[0])
        if len(lines) - 1 != n:
            raise ValueError(f"Liczba zadań w pliku ({len(lines)-1}) != zadeklarowane n={n}")

        tasks: TaskDict = {}
        for i in range(1, n + 1):
            parts = lines[i].split()
            if len(parts) != 3:
                raise ValueError(f"Linia {i+1}: Oczekiwano 3 wartości, otrzymano {len(parts)}")
            
            p = int(parts[0])
            r = int(parts[1])
            w = int(parts[2])
            tasks[i] = {'p': p, 'r': r, 'w': w}

        return n, tasks
    except Exception as e:
        print(f"Błąd wczytywania instancji: {e}", file=sys.stderr)
        sys.exit(1)

def save_solution(filename: str, criterion_value: int, schedules: MachineSchedules):
    try:
        with open(filename, 'w') as f:
            f.write(str(criterion_value) + '\n')
            for machine_seq in schedules:
                f.write(' '.join(map(str, machine_seq)) + '\n')
            for _ in range(4 - len(schedules)):
                f.write('\n')
    except Exception as e:
        print(f"Błąd zapisu rozwiązania: {e}", file=sys.stderr)
        sys.exit(1)


def calculate_total_cost(tasks: TaskDict, machine_schedules: MachineSchedules) -> int:
    total_weighted_flow_time = 0

    for machine_sequence in machine_schedules:
        current_time = 0
        for job_id in machine_sequence:
            job = tasks[job_id]
            p_j = job['p']
            r_j = job['r']
            w_j = job['w']

            start_time = max(r_j, current_time)
            completion_time_Cj = start_time + p_j
            flow_time_Fj = completion_time_Cj - r_j
            
            total_weighted_flow_time += w_j * flow_time_Fj
            
            current_time = completion_time_Cj

    return total_weighted_flow_time



def get_solution(tasks: TaskDict, m_machines: int = 4) -> MachineSchedules:
    
    jobs_list = []
    for job_id, details in tasks.items():
        p, r, w = details['p'], details['r'], details['w']
        wspt_ratio = (p / w) if w > 0 else p 
        jobs_list.append((job_id, p, r, w, wspt_ratio))
    jobs_list.sort(key=lambda x: x[4])

    schedules: MachineSchedules = [[] for _ in range(m_machines)]
    machine_free_time = [0] * m_machines

    for job_id, p_j, r_j, w_j, _ in jobs_list:
        best_machine_idx = 0
        min_free_time = machine_free_time[0]
        
        for m_idx in range(1, m_machines):
            if machine_free_time[m_idx] < min_free_time:
                min_free_time = machine_free_time[m_idx]
                best_machine_idx = m_idx
        start_time = max(r_j, min_free_time)
        completion_time = start_time + p_j
        machine_free_time[best_machine_idx] = completion_time
        schedules[best_machine_idx].append(job_id)
        
    return schedules


def solve(n: int, tasks: TaskDict) -> Tuple[int, MachineSchedules]:

    schedules = get_solution(tasks)
    criterion_value = calculate_total_cost(tasks, schedules)
    
    return criterion_value, schedules

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Użycie: python 155830.py <plik_instancji> <plik_wynikowy> <limit_czasu_s>")
        sys.exit(1)

    instance_file = sys.argv[1]
    solution_file = sys.argv[2]
    # time_limit_s (sys.argv[3]) #ignoruj
    try:
        time_limit_s = float(sys.argv[3])
    except ValueError:
        print("Błąd: limit czasu musi być liczbą.", file=sys.stderr)
        sys.exit(1)

    n, tasks = load_instance(instance_file)
    criterion_value, schedules = solve(n, tasks)
    save_solution(solution_file, criterion_value, schedules)