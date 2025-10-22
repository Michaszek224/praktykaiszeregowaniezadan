import os
import sys
import time
import threading
import random

min_tardiness = float('inf')
min_batches = []

class Task:
    def __init__(self, id, processing_time, deadline):
        self.id = id
        self.processing_time = processing_time
        self.deadline = deadline

class Batch:
    def __init__(self, tasks):
        self.tasks = tasks
        self.flow_time = sum(task.processing_time for task in tasks)

    def calculate_tardiness(self, ready_time):
        completion_time = ready_time + self.flow_time
        return sum(max(0, completion_time - task.deadline) for task in self.tasks), completion_time

def load_instance():
    input_path = sys.argv[1]
    input = open(input_path, 'r').read().strip().split('\n')
    tasks = []
    n, s = map(int, input[0].split())
    for i in range(1, len(input)):
        p, d = map(int, input[i].split())
        tasks.append(Task(i, p, d))
    tasks.sort(key=lambda x: (x.deadline, -x.processing_time))
    return n, s, tasks

def save_result():
    output_path = sys.argv[2]
    with open(output_path, 'w') as f:
        f.write(f'{min_tardiness}\n')
        f.write(f'{len(min_batches)}\n')
        for batch in min_batches:
            f.write(' '.join(str(task.id) for task in batch.tasks) + '\n')

def main():
    n, setup_time, tasks = load_instance()

    while True:
        batch_ranges = []
        i = 0
        while i < n:
            j = random.randint(i + 1, n)
            batch_ranges.append((i, j))
            i = j

        batches = []
        for i, j in batch_ranges:
            batches.append(Batch(tasks[i:j]))

        current_time = 0
        total_tardiness = 0
        for batch in batches:
            if current_time > 0:
                current_time += setup_time
            tardiness, current_time = batch.calculate_tardiness(current_time)
            total_tardiness += tardiness

        global min_tardiness, min_batches
        if total_tardiness < min_tardiness:
            min_tardiness = total_tardiness
            min_batches = batches

def timeout_thread():
    max_seconds = int(sys.argv[3])
    time.sleep(max_seconds - 1)
    save_result()
    os._exit(0)

if __name__ == '__main__':
    supervisor = threading.Thread(target=timeout_thread, daemon=True)
    supervisor.start()
    main()
