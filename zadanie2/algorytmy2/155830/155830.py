import sys
import time
import heapq
import random
import math
from typing import Dict, List, Tuple, Any


JobData = Dict[int, Dict[str, Any]]
Schedule = List[List[int]]

def read_instance(input_path: str) -> Tuple[int, JobData]:
    jobs: JobData = {}
    try:
        with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read().split()
            if not content: raise ValueError
            n = int(content[0])
            idx = 1
            for i in range(1, n + 1):
                if idx + 2 >= len(content): break
                p, r, w = int(content[idx]), int(content[idx+1]), int(content[idx+2])
                ratio = w/p if p > 0 else float('inf')
                jobs[i] = {'p': p, 'r': r, 'w': w, 'ratio': ratio, 'id': i}
                idx += 3
            return n, jobs
    except:
        sys.exit(1)

def get_machine_cost(jobs: JobData, machine_seq: List[int]) -> int:
    cost = 0
    time_m = 0
    for job_id in machine_seq:
        j = jobs[job_id]
        start = max(time_m, j['r'])
        end = start + j['p']
        cost += j['w'] * (end - j['r'])
        time_m = end
    return cost

def calculate_total_cost(jobs: JobData, schedule: Schedule) -> int:
    return sum(get_machine_cost(jobs, m) for m in schedule)

def greedy_wspt(n: int, jobs: JobData) -> Schedule:
    pq = [(0, i) for i in range(4)]
    heapq.heapify(pq)
    schedule = [[] for _ in range(4)]
    pending = sorted(jobs.values(), key=lambda x: x['r'])
    p_idx = 0
    pool = [] 
    count = 0
    
    while count < n:
        curr_t, m_idx = heapq.heappop(pq)
        while p_idx < n and pending[p_idx]['r'] <= curr_t:
            j = pending[p_idx]
            heapq.heappush(pool, (-j['ratio'], -j['w'], j['id']))
            p_idx += 1
        if not pool:
            if p_idx < n:
                heapq.heappush(pq, (pending[p_idx]['r'], m_idx))
                continue
            else:
                heapq.heappush(pq, (curr_t, m_idx))
                break
        _, _, best_id = heapq.heappop(pool)
        job = jobs[best_id]
        end = max(curr_t, job['r']) + job['p']
        schedule[m_idx].append(best_id)
        count += 1
        heapq.heappush(pq, (end, m_idx))
    return schedule

def sa(n: int, jobs: JobData, start_schedule: Schedule, deadline: float, start_timestamp: float) -> Tuple[int, Schedule]:

    curr_sched = [list(m) for m in start_schedule]
    machine_costs = [get_machine_cost(jobs, m) for m in curr_sched]
    curr_total_cost = sum(machine_costs)
    
    best_sched = [list(m) for m in curr_sched]
    best_total_cost = curr_total_cost

    saturation = 1.0 - math.exp(-n / 200.0)
    insert_prob = 0.5 + (0.45 * saturation) 

    T_base = 120.0
    T_boost = 1000.0 * math.exp(-n / 80.0)
    T_start = T_base + T_boost

    cooling_power = 1.5
    reheat_ratio = 0.15 + (0.2 * math.exp(-n / 100.0))
    
    T = T_start
    T_end = 0.01
    
    total_time = deadline - start_timestamp
    iter_count = 0
    machines_indices = [0, 1, 2, 3]
    last_improvement_time = time.time()
    
    while True:
        iter_count += 1
        
        if iter_count % 100 == 0:
            now = time.time()
            if now >= deadline: break
            
            elapsed = now - start_timestamp
            
            time_since_imp = now - last_improvement_time
            reheat_trigger = max(1.5, total_time * 0.20)
            
            if time_since_imp > reheat_trigger:
                curr_sched = [list(m) for m in best_sched]
                curr_total_cost = best_total_cost
                machine_costs = [get_machine_cost(jobs, m) for m in curr_sched]
                
                T = T_start * reheat_ratio
                last_improvement_time = now
            else:
                progress = elapsed / total_time
                ratio = (1.0 - progress)
                if ratio < 0: ratio = 0
                
                T = T_start * (ratio ** cooling_power)
                if T < T_end: T = T_end
        else:
            if iter_count == 1: T = T_start


        is_insert = (random.random() < insert_prob)
        
        m1 = random.choice(machines_indices)
        if not curr_sched[m1]: continue
        
        new_m1_seq = list(curr_sched[m1])
        new_m2_seq = None
        m2 = -1
        delta = 0
        valid = False
        
        if is_insert:
            m2 = random.choice(machines_indices)
            same_machine = (m1 == m2)
            
            if same_machine:
                new_m2_seq = new_m1_seq
            else:
                new_m2_seq = list(curr_sched[m2])
            
            job = new_m1_seq.pop(random.randint(0, len(new_m1_seq)-1))
            new_m2_seq.insert(random.randint(0, len(new_m2_seq)), job)
            
            if same_machine:
                c1 = get_machine_cost(jobs, new_m1_seq)
                delta = c1 - machine_costs[m1]
            else:
                c1 = get_machine_cost(jobs, new_m1_seq)
                c2 = get_machine_cost(jobs, new_m2_seq)
                delta = (c1 + c2) - (machine_costs[m1] + machine_costs[m2])
            valid = True
            
        else:
            m2 = random.choice(machines_indices)
            if m2 != m1 and curr_sched[m2]:
                new_m2_seq = list(curr_sched[m2])
                idx1 = random.randint(0, len(new_m1_seq)-1)
                idx2 = random.randint(0, len(new_m2_seq)-1)
                new_m1_seq[idx1], new_m2_seq[idx2] = new_m2_seq[idx2], new_m1_seq[idx1]
                
                c1 = get_machine_cost(jobs, new_m1_seq)
                c2 = get_machine_cost(jobs, new_m2_seq)
                delta = (c1 + c2) - (machine_costs[m1] + machine_costs[m2])
                valid = True

        if not valid: continue

        accept = False
        if delta < 0:
            accept = True
        else:
            if T > 0.001:
                if delta / T < 12.0:
                    if random.random() < math.exp(-delta / T):
                        accept = True
        
        if accept:
            curr_sched[m1] = new_m1_seq
            machine_costs[m1] = c1 if m1 == m2 else c1
            if m1 != m2:
                curr_sched[m2] = new_m2_seq
                machine_costs[m2] = c2
            
            curr_total_cost += delta
            
            if curr_total_cost < best_total_cost - 0.5:
                best_total_cost = curr_total_cost
                best_sched = [list(r) for r in curr_sched]
                last_improvement_time = time.time()

    return int(round(best_total_cost)), best_sched


def main():
    if len(sys.argv) < 4: return
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    try:
        time_limit_arg = float(sys.argv[3])
    except:
        time_limit_arg = 10.0

    start_timestamp = time.time()
    deadline = start_timestamp + time_limit_arg - 0.5
    
    n, jobs = read_instance(input_file)
    schedule = greedy_wspt(n, jobs)
    init_cost = calculate_total_cost(jobs, schedule)
    
    if time.time() < deadline:
        best_cost, best_schedule = sa(n, jobs, schedule, deadline, start_timestamp)
    else:
        best_cost = init_cost
        best_schedule = schedule
            
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"{best_cost}\n")
            for machine in best_schedule:
                f.write(" ".join(map(str, machine)) + "\n")
    except Exception:
        pass

if __name__ == "__main__":
    main()