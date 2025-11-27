import sys
import time
import pathlib
import random
import copy

PARALLEL_MACHINES = 4
TIME_FACTOR = 0.97
SWAP_PROBABILITY = 0.5

class Task:
    def __init__(self, processing_time, ready_time, weight):
        self.processing_time = processing_time
        self.ready_time = ready_time
        self.weight = weight
        self.ratio = self.processing_time / self.weight

def load_instance(instance_path):
    instance = instance_path.read_text().strip().split('\n')
    n = int(instance[0])
    tasks = []
    for i in range(1, len(instance)):
        p, r, w = map(int, instance[i].split())
        tasks.append(Task(p, r, w))
    return n, tasks

def save_result(result_path, schedule, cost):
    result = str(cost) + '\n'
    for sub_schedule in schedule:
        line = ' '.join(str(index + 1) for index in sub_schedule)
        result += line + '\n'
    result_path.write_text(result, newline='\n')

def partial_evaluate(tasks, sub_schedule):
    cost = 0
    current_time = 0
    for index in sub_schedule:
        task = tasks[index]
        current_time = max(current_time, task.ready_time) + task.processing_time
        cost += task.weight * (current_time - task.ready_time)
    return cost

def initialize(n, tasks):
    times = [0] * PARALLEL_MACHINES
    available = [True] * n
    schedule = [[] for _ in range(PARALLEL_MACHINES)]
    partial_costs = [0] * PARALLEL_MACHINES

    sorted_task_indices = sorted(range(n), key=lambda x: tasks[x].ready_time)

    for _ in range(n):
        machine_index = min(range(PARALLEL_MACHINES), key=lambda x: times[x])
        machine_time = times[machine_index]

        candidate_indices = []

        for i in sorted_task_indices:
            task = tasks[i]
            if available[i] and task.ready_time <= machine_time:
                candidate_indices.append(i)
            elif task.ready_time > machine_time:
                break

        if candidate_indices:
            best_task_index = min(candidate_indices, key=lambda x: tasks[x].ratio)
        else:
            best_task_index = min([i for i in range(n) if available[i]],
                                  key=lambda x: (tasks[x].ready_time, tasks[x].ratio))

        selected_task = tasks[best_task_index]
        completion_time = max(machine_time, selected_task.ready_time) + selected_task.processing_time

        times[machine_index] = completion_time
        available[best_task_index] = False
        schedule[machine_index].append(best_task_index)
        partial_costs[machine_index] += selected_task.weight * (completion_time - selected_task.ready_time)

    return schedule, partial_costs

def search(start_time, time_limit, tasks, schedule, partial_costs):
    while time.perf_counter() - start_time < time_limit:
        new_schedule = copy.deepcopy(schedule)

        m1 = random.randrange(PARALLEL_MACHINES)
        m2 = random.randrange(PARALLEL_MACHINES)

        if not new_schedule[m1]:
            continue

        if random.random() < SWAP_PROBABILITY:
            if not new_schedule[m2]:
                continue

            t1 = random.randrange(len(new_schedule[m1]))
            t2 = random.randrange(len(new_schedule[m2]))

            new_schedule[m1][t1], new_schedule[m2][t2] = new_schedule[m2][t2], new_schedule[m1][t1]
        else:
            t1 = random.randrange(len(new_schedule[m1]))
            t2 = random.randrange(len(new_schedule[m2]) + 1)

            task_index = new_schedule[m1].pop(t1)
            new_schedule[m2].insert(t2, task_index)

        new_partial_cost_m1 = partial_evaluate(tasks, new_schedule[m1])
        new_partial_cost_m2 = partial_evaluate(tasks, new_schedule[m2])

        delta = (partial_costs[m1] + partial_costs[m2]) - (new_partial_cost_m1 + new_partial_cost_m2)

        if delta > 0:
            schedule = new_schedule
            partial_costs[m1] = new_partial_cost_m1
            partial_costs[m2] = new_partial_cost_m2

    return schedule, sum(partial_costs)

def main(instance_path, result_path, max_seconds):
    start_time = time.perf_counter()

    n, tasks = load_instance(instance_path)
    schedule, partial_costs = initialize(n, tasks)
    schedule, cost = search(start_time, TIME_FACTOR * max_seconds, tasks, schedule, partial_costs)

    save_result(result_path, schedule, cost)

if __name__ == '__main__':
    assert len(sys.argv) == 4

    instance_path = pathlib.Path(sys.argv[1])
    result_path = pathlib.Path(sys.argv[2])
    max_seconds = float(sys.argv[3])

    main(instance_path, result_path, max_seconds)
