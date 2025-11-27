from math import inf
import sys
import time

def read_input(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    n = int(lines[0].strip())
    tasks = []
    
    for i in range(1, n + 1):
        parts = lines[i].strip().split()
        p, r, w = int(parts[0]), int(parts[1]), int(parts[2])
        tasks.append({'id': i, 'p': p, 'r': r, 'w': w})
    
    return n, tasks

def calculate_cost(n, tasks, machines):
    actual_objective = 0
    
    for machine_id, sequence in enumerate(machines, 1):
        current_time = 0
        
        for job_id in sequence:
            if job_id < 1 or job_id > n:
                continue
            
            task = tasks[job_id - 1]
            
            start_time = max(current_time, task['r'])
            completion_time = start_time + task['p']
            
            flow_time = completion_time - task['r']
            cost = task['w'] * flow_time
            
            actual_objective += cost
            current_time = completion_time
    return actual_objective

def greedy_schedule(n, tasks, number_of_machines = 4):
    sorted_tasks = sorted(tasks, key=lambda x: x['r'])
    result = [[] for _ in range(number_of_machines)]
    for i in range(n):
        minj = 0
        mini = inf
        for j in range(number_of_machines):
            if result[j]:
                if tasks[result[j][-1] - 1]['r'] + tasks[result[j][-1] - 1]['p'] <= mini:
                    minj = j
                    mini = tasks[result[j][-1] - 1]['r'] + tasks[result[j][-1] - 1]['p']
            else:
                minj = j
                mini = 0
        result[minj].append(sorted_tasks[i]['id'])
    return result

def write_output(filename, result, n, tasks):
    file = open(filename, 'w')
    final_cost = calculate_cost(n, tasks, result)
    file.write(f"{final_cost}\n")
    for machine in result:
        line = ' '.join(str(job_id) for job_id in machine)
        file.write(f"{line}\n")
    return final_cost

def main():
    if len(sys.argv) != 4:
        print("Użycie: python 156011.py [plik_wejściowy] [plik_wynikowy] [limit_czasu]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    time_limit = int(sys.argv[3])

    start_time = time.time()
    n, tasks = read_input(input_file)
    result = greedy_schedule(n, tasks)
    final_cost = write_output(output_file, result, n, tasks)
    elapsed_time = time.time() - start_time
    if elapsed_time > time_limit:
        print("Ostrzeżenie: Przekroczono limit czasu!")
    print(final_cost)

if __name__ == "__main__":
    main()