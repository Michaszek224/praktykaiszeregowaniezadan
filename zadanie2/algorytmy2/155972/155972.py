import sys
from copy import deepcopy
from dataclasses import dataclass
from time import time as now

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
        time = max(time, job.r) + job.p
        fsum += (time - job.r) * job.w
    return fsum

def calc_times(jobs: list[Job], machines: Machines) -> int:
    return [calc_time_single(jobs, machine) for machine in machines]

def calc_time(jobs: list[Job], machines: Machines) -> int:
    return sum(calc_times(jobs, machines))

def init_ff_wspt(jobs: list[Job], available_tie=lambda _: 1, else_tie=lambda _: 1) -> Machines:
    free_times = [0] * 4
    jobids = [i for i in range(len(jobs))]
    res = tuple([] for _ in range(4))
    while len(jobids) > 0:
        machid = min(range(4), key=lambda x: free_times[x])
        available = [jobid for jobid in jobids if jobs[jobid].r <= free_times[machid]]
        if len(available) > 0:
            jobid = min(available, key=lambda x: (jobs[x].p / jobs[x].w, available_tie(x)))
        else:
            jobid = min(jobids, key=lambda x: (jobs[x].r, else_tie(x)))
        res[machid].append(jobid)
        free_times[machid] = max(free_times[machid], jobs[jobid].r) + jobs[jobid].p 
        jobids.remove(jobid)
    return res

def init_ff_wspt_all(jobs: list[Job]) -> list[Machines]:
    __ = lambda _: 1
    p_ = lambda x: jobs[x].p
    r_ = lambda x: jobs[x].r
    pr = lambda x: (jobs[x].p, jobs[x].r)
    o_ = lambda x: jobs[x].p / jobs[x].w
    w_ = lambda x: jobs[x].w
    op = lambda x: (jobs[x].p / jobs[x].w, jobs[x].p)

    combinations = [
        (__, __, '__:__'),
        (__, p_, '__:p_'),
        (__, o_, '__:o_'),
        (p_, __, 'p_:__'),
        (p_, p_, 'p_:p_'),
        (p_, o_, 'p_:o_'),
        (r_, __, 'r_:__'),
        (r_, p_, 'r_:p_'),
        (r_, o_, 'r_:o_'),
        (pr, __, 'pr:__'),
        (pr, p_, 'pr:p_'),
        (pr, o_, 'pr:o_'),
    ]
    return [init_ff_wspt(jobs, available_tie=comb[0], else_tie=comb[1]) for comb in combinations]

def write(time: int, machines: Machines, output_file_name):
    with open(output_file_name, 'w') as f:
        f.write('{}\n'.format(time))
        for machine in machines:
            for jobid in machine:
                f.write('{} '.format(jobid + 1))
            f.write('\n')

def hill_climb_range(jobs: list[Job], machines: Machines, tlimit, srange=4) -> Machines:
    best = deepcopy(machines)
    best_time = calc_time(jobs, machines)
    current = deepcopy(machines)
    found = True
    while found and now() < tlimit:
        found = False
        for smid in range(4):
            if now() > tlimit:
                return best
            for sid in range(len(current[smid])):
                jobid = current[smid].pop(sid)
                for dmid in range(4):
                    for did in range(max(0, sid-srange), min(len(current[dmid]), sid+srange)):
                        current[dmid].insert(did, jobid)
                        current_time = calc_time(jobs, current)
                        if current_time < best_time:
                            best_time = current_time
                            best = deepcopy(current)
                            found = True
                        assert current[dmid].pop(did) == jobid
                current[smid].insert(sid, jobid)
        current = deepcopy(best)
    return best

from collections import deque
def tabu_search_range(jobs: list[Job], machines: Machines, tlimit, srange=4, max_tabu_list_length=1000) -> Machines:
    best = deepcopy(machines)
    best_time = calc_time(jobs, machines)
    current = deepcopy(machines)
    tabulist = deque([best])
    while now() < tlimit:
        best_candidate = ([], [], [], [])
        best_candidate_time = float('inf')
        for smid in range(4):
            if now() > tlimit:
                return best
            for sid in range(len(current[smid])):
                jobid = current[smid].pop(sid)
                for dmid in range(4):
                    for did in range(max(0, sid-srange), min(len(current[dmid]), sid+srange)):
                        current[dmid].insert(did, jobid)
                        if current not in tabulist:
                            current_time = calc_time(jobs, current)
                            if current_time < best_candidate_time:
                                best_candidate_time = current_time
                                best_candidate = deepcopy(current)
                        assert current[dmid].pop(did) == jobid
                current[smid].insert(sid, jobid)
        if best_candidate_time == float('inf'):
            break
        current = deepcopy(best_candidate)
        if best_candidate_time < best_time:
            best_time = best_candidate_time
            best = deepcopy(best_candidate)
        tabulist.append(best_candidate)
        if len(tabulist) > max_tabu_list_length:
            tabulist.popleft()
    return best

def hill_worker(pid, return_dict, jobs, machines, tlimit):
    return_dict[pid] = hill_climb_range(jobs, machines, tlimit, srange=16)

def tabu_worker(pid, return_dict, jobs, machines, tlimit):
    return_dict[pid] = tabu_search_range(jobs, machines, tlimit, srange=4)

import multiprocessing as mp
def main(input_file_name, output_file_name, time_limit):
    jobs = read_input(input_file_name)
    time_limit = float(time_limit) * 0.90
    tlimit = now() + time_limit
    wspts = init_ff_wspt_all(jobs)
    unique = []
    for wspt in wspts:
        if wspt not in unique:
            unique.append(wspt)

    manager = mp.Manager()
    return_dict = manager.dict()
    processes = [mp.Process(target=hill_worker, args=(i, return_dict, jobs, machines, tlimit)) for i, machines in enumerate(unique)] \
        + [mp.Process(target=tabu_worker, args=(i + len(unique), return_dict, jobs, machines, tlimit)) for i, machines in enumerate(unique)]

    for process in processes:
        process.start()
    
    for process in processes:
        process.join()
    
    best = min(return_dict.values(), key=lambda res: calc_time(jobs, res))
    time = calc_time(jobs, best)
    write(time, best, output_file_name)

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Usage: python 155972.py <input> <output> <time limit>')
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3])