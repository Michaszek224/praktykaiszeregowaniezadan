import sys
from copy import deepcopy
from dataclasses import dataclass

@dataclass
class Job:
    p: int
    r: int
    w: int
    def __init__(self, nums: list[int]):
        self.p, self.r, self.w = nums

def read_input(input_file_name) -> list[Job]:
    with open(input_file_name, 'r') as f:
        _ = next(f)
        jobs = [Job([int(x) for x in line.split()]) for line in f if len(line) >= 5]
    return jobs

Machines = tuple[list[int], list[int], list[int], list[int]]

def calc_time_single(jobs: list[Job], machine: list[int]) -> int:
    fsum = 0
    time = 0
    for jobid in machine:
        job = jobs[jobid]
        time = max(time, job.r)
        time += job.p
        fsum += (time - job.r) * job.w
    return fsum

def calc_time(jobs: list[Job], machines: Machines) -> int:
    fsum = 0
    for machine in machines:
        fsum += calc_time_single(jobs, machine)
    return fsum

def initial(jobs: list[Job]) -> Machines:
    sjobs = sorted(range(len(jobs)), key=lambda x: (jobs[x].r, jobs[x].p))
    return tuple([sjobs[i] for i in range(m, len(sjobs), 4)] for m in range(4))

def write(time: int, machines: Machines, output_file_name):
    with open(output_file_name, 'w') as f:
        f.write('{}\n'.format(time))
        for machine in machines:
            for jobid in machine:
                f.write('{} '.format(jobid + 1))
            f.write('\n')

class hill:
    def climb_single(jobs: list[Job], machine: list[int]) -> list[int]:
        best = machine.copy()
        best_time = calc_time_single(jobs, machine)
        current = machine.copy()
        found = True
        while found:
            found = False
            for i in range(len(machine) - 1):
                current[i], current[i+1] = current[i+1], current[i]
                time = calc_time_single(jobs, current)
                if time < best_time:
                    best_time = time
                    best = current.copy()
                    found = True
                current[i], current[i+1] = current[i+1], current[i]
        return best

    def climb_machines_individually(jobs: list[Job], machines: Machines) -> Machines:
        return tuple(hill.climb_single(jobs, machine) for machine in machines)

    def climb_across(jobs: list[Job], machines: Machines) -> Machines:
        best = deepcopy(machines)
        best_time = calc_time(jobs, machines)
        current = deepcopy(machines)
        found = True
        while found:
            found = False
            for machine in current:
                for jobid in range(len(machine) - 1):
                    machine[jobid], machine[jobid+1] = machine[jobid+1], machine[jobid]
                    time = calc_time(jobs, current)
                    if time < best_time:
                        best_time = time
                        best = deepcopy(current)
                        found = True
                    machine[jobid], machine[jobid+1] = machine[jobid+1], machine[jobid]
            for machid in range(3):
                for jobid in range(min(len(current[machid]), len(current[machid+1]))):
                    current[machid][jobid], current[machid+1][jobid] = current[machid+1][jobid], current[machid][jobid]
                    time = calc_time(jobs, current)
                    if time < best_time:
                        best_time = time
                        best = deepcopy(current)
                        found = True
                    current[machid][jobid], current[machid+1][jobid] = current[machid+1][jobid], current[machid][jobid]
        return best

def main(input_file_name, output_file_name, time_limit):
    jobs = read_input(input_file_name)
    machines = hill.climb_across(jobs, initial(jobs))
    time = calc_time(jobs, machines)
    write(time, machines, output_file_name)

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Usage: python 155972.py <input> <output> <time limit>')
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3])