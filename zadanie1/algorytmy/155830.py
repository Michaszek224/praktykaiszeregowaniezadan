import sys
from typing import List, Dict, Tuple

Task = Tuple[int, int, int] 

def load_instance(filename: str) -> Tuple[int, int, List[Task]]:
    try:
        with open(filename, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]

        if not lines:
            raise ValueError("Plik instancji jest pusty.")

        n, s = map(int, lines[0].split())
        
        tasks: List[Task] = []
        for i, line in enumerate(lines[1:], start=1):
            if not line: continue
            p, d = map(int, line.split())
            tasks.append((i, p, d)) 

        if len(tasks) != n:
             raise ValueError(f"Liczba zadań w pliku ({len(tasks)}) nie zgadza się z zadeklarowanym n={n}.")

        return n, s, tasks
    except Exception as e:
        sys.exit(f"Błąd wczytywania instancji: {e}")

def calculate_criterion(s: int, tasks: Dict[int, Dict[str, int]], batches: List[List[int]]) -> int:
    total_tardiness = 0
    current_time = 0

    for batch in batches:

        batch_time = sum(tasks[j]['p'] for j in batch)
        completion_time = current_time + batch_time
        current_time = completion_time + s

        for j in batch:
            tardiness = max(0,completion_time - tasks[j]['d'])
            total_tardiness += tardiness

    return total_tardiness

def solve(n: int, s: int, tasks: List[Task]) -> Tuple[int, List[List[int]]]:
    
    min_batch_size = 5 #TODO zrobić testy dla innych

    sorted_tasks = sorted(tasks, key=lambda x: x[2]) 
    
    tasks_dict = {task[0]: {'p': task[1], 'd': task[2]} for task in tasks}
    
    batches: List[List[int]] = []
    
    current_batch: List[int] = []
    current_time = 0
    current_batch_total_P = 0 
    # total_p = sum(task[1] for task in tasks)
    # p_avg = total_p / n if n > 0 else 1
    
    # total_d = sum(task[2] for task in tasks)
    # d_avg = total_d / n if n > 0 else 1 #samo d_avg nie ma sensu, można próbować koleracje wykryć z indeks ew. 
    split_line = s #TODO powiązać z p_avg, może d z indeks(w niektorych przypadkach jak wykryje korelacje)

    for task in sorted_tasks:
        j_index, p_j, d_j = task
        
        if len(current_batch) < min_batch_size:  #TODO trzeba to jakoś logicznej zrobić, jakoś p_avg powiązać z s i na tym min_batch _size
            current_batch.append(j_index)
            current_batch_total_P += p_j 
            continue
            
        else:
            # P_current = sum(tasks_dict[j]['p'] for j in current_batch) #TODO nie liczyc zawsze tylko w momencie dodania dodaj to current_total, 
            P_current = current_batch_total_P 
            completion_time_if_current = current_time + (P_current + p_j) 
            
            tardiness_if_current = max(0, completion_time_if_current - d_j)
            
            if tardiness_if_current > split_line: #
                batches.append(current_batch)
                current_time = current_time + P_current + s
                current_batch = [j_index]
                current_batch_total_P = p_j
            
            else:
                current_batch.append(j_index)
                current_batch_total_P += p_j
                
    if current_batch:
        batches.append(current_batch)
        
    criterion_value = calculate_criterion(s, tasks_dict, batches)

    return criterion_value, batches


def save_solution(filename: str, criterion_value: int, batches: List[List[int]]):
    try:
        with open(filename, 'w') as f:
            f.write(str(criterion_value) + '\n') 
            f.write(str(len(batches)) + '\n') 
            for batch in batches:
                if batch:
                    f.write(' '.join(map(str, batch)) + '\n') 
    except Exception as e:
        sys.exit(f"błąd zapisu rozwiązania: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Użycie: python 155830.py <plik_instancji> <plik_wynikowy> <limit_czasu_s>")
        sys.exit(1)

    instance_file = sys.argv[1]
    solution_file = sys.argv[2]
    
    try:
        time_limit_s = float(sys.argv[3])
    except ValueError:
        sys.exit("Błąd:ostatni argumnt (limit czasu) should be convertable to float (być liczbą)") #
    n, s, tasks = load_instance(instance_file)
    criterion_value, batches = solve(n, s, tasks)
    save_solution(solution_file, criterion_value, batches)
