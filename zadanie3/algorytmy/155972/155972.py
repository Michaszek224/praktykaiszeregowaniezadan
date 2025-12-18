import sys
from random import randrange
from dataclasses import dataclass
from time import time as now

@dataclass
class Job:
    p: tuple[int, int, int, int]
    r: int
    def __init__(self, nums: list[int]):
        self.p, self.r = tuple(nums[i] for i in range(4)), nums[4]

Jobs = list[Job]
Setups = list[list[int]]
Instance = tuple[Jobs, Setups]

def read_input(input_file_name) -> Instance:
    with open(input_file_name, 'r') as f:
        n = int(next(f).split()[0])
        lines = f.readlines()
        jobs = [Job([int(x) for x in lines[i].split()]) for i in range(n)]
        setups = [[int(x) for x in lines[i].split()] for i in range(n, 2*n)]
    return jobs, setups

def write(time: int, schedule: list[int], output_file_name):
    with open(output_file_name, 'w') as f:
        f.write('{}\n'.format(time))
        for jobid in schedule:
            f.write('{} '.format(jobid + 1))
        f.write('\n')

def calculate_time(instance: Instance, schedule: list[int]) -> int:
    times = [0 for _ in range(4)]
    for i, jobid in enumerate(schedule):
        job = instance[0][jobid]
        times[0] = max(times[0], job.r) + job.p[0]
        for t in range(1, 4):
            times[t] = max(times[t], times[t-1]) + job.p[t]
        if i + 1 < len(schedule):
            next_jobid = schedule[i+1]
            for t in range(4):
                times[t] += instance[1][jobid][next_jobid]
    return times[3]

def solve(instance: Instance, deadline: float) -> tuple[list[int], int]:
    n = len(instance[0])
    best = [i for i in range(n)]
    best_time = calculate_time(instance, best)
    current = best.copy()
    while now() < deadline:
        sid, did = randrange(0, n), randrange(0, n)
        current[sid], current[did] = current[did], current[sid]
        current_time = calculate_time(instance, current)
        if current_time < best_time:
            best, best_time = current.copy(), current_time
    return best, best_time

def main(input_file_name, output_file_name, time_limit):
    instance = read_input(input_file_name)
    time_limit = time_limit * 0.9 - 0.5
    schedule, time = solve(instance, now() + time_limit)
    write(time, schedule, output_file_name)

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Usage: 155972.py <input> <output> <time limit>')
    else:
        main(sys.argv[1], sys.argv[2], float(sys.argv[3]))