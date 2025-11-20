import sys
import time
import random
import pathlib

PARALLEL_MACHINES = 4

def load_instance(instance_path):
    instance = instance_path.read_text().strip().split('\n')
    n = int(instance[0])
    tasks = []
    for i in range(1, len(instance)):
        p, r, w = map(int, instance[i].split())
        tasks.append((p, r, w))
    return n, tasks

def save_result(result_path, cost, machine_schedules):
    result = str(cost) + '\n'
    for machine_schedule in machine_schedules:
        line = ' '.join(str(task_index + 1) for task_index in machine_schedule)
        result += line + '\n'
    result_path.write_text(result, newline='\n')

def evaluate(tasks, machine_schedules):
    cost = 0
    for machine_schedule in machine_schedules:
        current_time = 0
        for task_index in machine_schedule:
            p, r, w = tasks[task_index]
            current_time = max(current_time, r) + p
            cost += w * (current_time - r)
    return cost

def main(instance_path, result_path, max_seconds):
    start_time = time.perf_counter()
    n, tasks = load_instance(instance_path)

    sorted_task_indices = list(range(n))
    sorted_task_indices.sort(key=lambda i: (tasks[i][1], -tasks[i][2]))

    TIME_FACTOR = 0.2  # 0.96

    best_cost = float('inf')
    best_machine_schedules = None

    while time.perf_counter() - start_time < max_seconds * TIME_FACTOR:
        machine_schedules = [[] for _ in range(PARALLEL_MACHINES)]
        machine_times = [0] * PARALLEL_MACHINES

        for task_index in sorted_task_indices:
            p, r, _ = tasks[task_index]

            min_machine_time = min(machine_times)
            candidate_machines = [i for i in range(PARALLEL_MACHINES) if machine_times[i] == min_machine_time]

            earliest_machine_index = random.choice(candidate_machines)
            task_start_time = max(machine_times[earliest_machine_index], r)

            machine_schedules[earliest_machine_index].append(task_index)
            machine_times[earliest_machine_index] = task_start_time + p

        cost = evaluate(tasks, machine_schedules)

        if cost < best_cost:
            best_cost = cost
            best_machine_schedules = machine_schedules

    save_result(result_path, best_cost, best_machine_schedules)

if __name__ == '__main__':
    assert len(sys.argv) == 4

    instance_path = pathlib.Path(sys.argv[1])
    result_path = pathlib.Path(sys.argv[2])
    max_seconds = float(sys.argv[3])

    main(instance_path, result_path, max_seconds)
