import sys
import time
import pathlib
import random

TIME_FACTOR = 0.1  # 0.95
PARALLEL_MACHINES = 4

def load_instance(instance_path):
    instance = instance_path.read_text().strip().split('\n')
    n = int(instance[0])
    jobs = []
    for i in range(1, n + 1):
        jobs.append(list(map(int, instance[i].split())))
    setups = []
    for i in range(n + 1, 2 * n + 1):
        setups.append(list(map(int, instance[i].split())))
    return n, jobs, setups

def save_result(result_path, completion_time, schedule):
    result = str(completion_time) + '\n'
    result += ' '.join(str(index + 1) for index in schedule) + '\n'
    result_path.write_text(result, newline='\n')

def evaulate(n, jobs, setups, schedule):
    time = [0] * PARALLEL_MACHINES
    prev_job_index = None

    for job_index in schedule:
        p = jobs[job_index][:4]
        r = jobs[job_index][4]
        setup = 0 if prev_job_index is None else setups[prev_job_index][job_index]

        for i in range(PARALLEL_MACHINES):
            time[i] = max(r if i == 0 else time[i - 1], time[i] + setup) + p[i]

        prev_job_index = job_index

    return time[-1]

def main(instance_path, result_path, max_seconds):
    start_time = time.perf_counter()

    n, jobs, setups = load_instance(instance_path)

    completion_time = None
    schedule = None

    while time.perf_counter() - start_time < max_seconds * TIME_FACTOR:
        new_schedule = list(range(n))
        random.shuffle(new_schedule)

        new_completion_time = evaulate(n, jobs, setups, new_schedule)

        if completion_time is None or new_completion_time < completion_time:
            completion_time = new_completion_time
            schedule = new_schedule

    save_result(result_path, completion_time, schedule)

if __name__ == '__main__':
    assert len(sys.argv) == 4

    instance_path = pathlib.Path(sys.argv[1])
    result_path = pathlib.Path(sys.argv[2])
    max_seconds = float(sys.argv[3])

    main(instance_path, result_path, max_seconds)
