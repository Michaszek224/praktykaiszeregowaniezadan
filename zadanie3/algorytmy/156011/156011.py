import random
import sys
import time

def read_input(filename):
    with open(filename, 'r') as f:
        n = int(f.readline().strip())
        tasks = {}
        
        for i in range(1, n + 1):
            parts = f.readline().strip().split()
            p1, p2, p3, p4, r = map(int, parts)
            tasks[i] = {'r': r, 'p': [p1, p2, p3, p4]}
        
        setup_matrix = {}
        for i in range(1, n + 1):
            parts = f.readline().strip().split()
            for j in range(1, n + 1):
                setup_matrix[(i, j)] = int(parts[j - 1])
        
        return n, tasks, setup_matrix

def calculate_makespan(sequence, tasks, setup_matrix):
    n = len(sequence)
    num_machines = 4
    
    completion_times = [[0] * num_machines for _ in range(n)]
    
    for i, task_id in enumerate(sequence):
        task = tasks[task_id]
        
        for m in range(num_machines):
            if i == 0 and m == 0:
                completion_times[i][m] = max(0, task['r']) + task['p'][m]
            elif i == 0:
                completion_times[i][m] = completion_times[i][m - 1] + task['p'][m]
            elif m == 0:
                prev_task_id = sequence[i - 1]
                setup_time = setup_matrix[(prev_task_id, task_id)]
                completion_times[i][m] = max(completion_times[i - 1][m] + setup_time, task['r']) + task['p'][m]
            else:
                prev_task_id = sequence[i - 1]
                setup_time = setup_matrix[(prev_task_id, task_id)]
                start_time = max(completion_times[i][m - 1], completion_times[i - 1][m] + setup_time, task['r'])
                completion_times[i][m] = start_time + task['p'][m]
    
    return completion_times[-1][-1]

def save_output(sequence, makespan, filename):
    with open(filename, 'w') as f:
        f.write(f"{makespan}\n")
        for task_id in sequence:
            f.write(f"{task_id} ")

def greedy_solve(tasks, setup_matrix, time_limit):
    sorted_tasks = sorted(tasks.items(), key=lambda x: x[1]['r'])
    sequence = [task[0] for task in sorted_tasks]
    makespan = calculate_makespan(sequence, tasks, setup_matrix)
    #local_search_start_time = time.time()
    #time_limit -= 1
    #n = len(sequence)
    #while time.time() - local_search_start_time < time_limit:
    #    i = random.randint(0, n - 1)
    #    j = random.randint(0, n - 1)
    #    si = sequence[i]
    #    sj = sequence[j]
    #    sequence[i], sequence[j] = sj, si
    #    new_makespan = calculate_makespan(sequence, tasks, setup_matrix)
    #    if new_makespan < makespan:
    #        makespan = new_makespan
    #    else:
    #        sequence[i], sequence[j] = si, sj
    return sequence, makespan

def main():
    if len(sys.argv) < 2:
        print("Usage: python 156011.py <input_file> [output_file] [time_limit]")
        print("Example: python 156011.py in_156011_50.txt out_156011_50.txt 5")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        size_str = input_file.split('_')[-1].replace('.txt', '')
        n_expected = int(size_str)
    except:
        n_expected = None

    time_limit = float(sys.argv[3]) if len(sys.argv) > 3 else n_expected/10
    n, tasks, setup_matrix = read_input(input_file)
    start_time = time.time()
    best_sequence, best_makespan = greedy_solve(tasks, setup_matrix, time_limit)
    elapsed_time = time.time() - start_time
    if elapsed_time > time_limit:
        print(f"\n Time limit exceeded ({time_limit} seconds). No solution found.")
        sys.exit(1)
    
    print(f"{best_makespan}")
    print(f"{elapsed_time:.2f}")
    
    if output_file:
        save_output(best_sequence, best_makespan, output_file)

if __name__ == "__main__":
    main()