import sys
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
    if not sequence:
        return float('inf')
    
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
def johnson_schedule(A, B):
    left = []
    right = []
    remaining = set(A.keys())

    while remaining:
        job = None
        best = float('inf')

        for j in remaining:
            v = min(A[j], B[j])
            if v < best or (v == best and tasks[j]['r'] < tasks[job]['r']):
                best = v
                job = j



        if A[job] <= B[job]:
            left.append(job)
        else:
            right.append(job)

        remaining.remove(job)

    return left + right[::-1]
def heuristic_H2(tasks, S):
    best_Cmax = float('inf')
    best_schedule = None
##################################
    A1, B1 = {}, {}
    for job, info in tasks.items():
        p = info['p']
        A1[job] = p[0] + p[1]
        B1[job] = p[2] + p[3]

    schedule = johnson_schedule(A1, B1)
    Cmax = calculate_makespan(schedule, tasks, S)
    if Cmax < best_Cmax:
        best_Cmax = Cmax
        best_schedule = schedule
        print("WERJSA 1",best_Cmax)

##################################
    A2, B2 = {}, {}
    for job, info in tasks.items():
        p = info['p']
        A2[job] = p[0] + 2 * p[1]
        B2[job] = 2 * p[2] + p[3]

    schedule = johnson_schedule(A2, B2)
    Cmax = calculate_makespan(schedule, tasks, S)
    if Cmax < best_Cmax:
        best_Cmax = Cmax
        best_schedule = schedule
        print("WERJSA 2",best_Cmax)

##################################
    A3, B3 = {}, {}
    for job, info in tasks.items():
        p = info['p']
        A3[job] = p[0]
        B3[job] = p[1] + p[2] + p[3]

    schedule = johnson_schedule(A3, B3)
    Cmax = calculate_makespan(schedule, tasks, S)
    if Cmax < best_Cmax:
        best_Cmax = Cmax
        best_schedule = schedule
        print("WERJSA 3",best_Cmax)

##################################
    A4, B4 = {}, {}
    for job, info in tasks.items():
        p = info['p']
        A4[job] = p[0] + p[1] + p[2]
        B4[job] = p[3]


    schedule = johnson_schedule(A4, B4)
    Cmax = calculate_makespan(schedule, tasks, S)
    if Cmax < best_Cmax:
        best_Cmax = Cmax
        best_schedule = schedule
        print("WERJSA 4",best_Cmax)



    return best_schedule, best_Cmax

def swap_alg(schedule, tasks, S, max_iter=3):
    best = schedule[:]
    best_Cmax = calculate_makespan(best, tasks, S)

    for _ in range(max_iter):
        improved = False
        for i in range(len(best) - 1):
            candidate = best[:]
            candidate[i], candidate[i + 1] = candidate[i + 1], candidate[i]
            Cmax = calculate_makespan(candidate, tasks, S)

            if Cmax < best_Cmax:
                best = candidate
                best_Cmax = Cmax
                improved = True
        if not improved:
            break

    return best, best_Cmax


def write_output(filename, Cmax, schedule):
    with open(filename, 'w') as f:
        f.write(f"{Cmax}\n")
        f.write(' '.join(map(str, schedule)) + '\n')

x=50
input=sys.argv[1]
output=sys.argv[2]
n, tasks, S = read_input(input)
schedule, Cmax = heuristic_H2(tasks, S)
schedule, Cmax = swap_alg(schedule, tasks, S)
# print("Cmax:", Cmax)
write_output(output,Cmax,schedule)

# is_valid, makespan, message = validator.validate_solution(input, output)


