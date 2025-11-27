import sys
import math
import heapq
import time
import random

jobs_by_id = {}

def compute_priority(rule_id, p, r, w):
    if rule_id == 0:
        base = p / float(w)
    elif rule_id == 1:
        base = p
    elif rule_id == 2:
        base = 1.0 / float(w)
    else:
        base = (p / float(w)) + 0.001 * r

    noise = 1.0 + 0.1 * (random.random() - 0.5)
    return base * noise


def schedule_jobs(n, jobs):
    jobs_sorted = sorted(jobs, key=lambda x: x[2])

    rule_id = random.randint(0, 3)

    pq = []
    machine_finish = [0] * 4
    machine_schedule = [[] for _ in range(4)]
    i = 0
    current_time = 0
    scheduled_count = 0

    while scheduled_count < n:
        if not pq:
            if i < n:
                next_release = jobs_sorted[i][2]
                if current_time < next_release:
                    current_time = next_release
                while i < n and jobs_sorted[i][2] <= current_time:
                    job_id, p, r, w = jobs_sorted[i]
                    pri = compute_priority(rule_id, p, r, w)
                    heapq.heappush(pq, (pri, job_id, p, r, w))
                    i += 1
            else:
                break

        free_machines = [m for m in range(4) if machine_finish[m] <= current_time]
        random.shuffle(free_machines)

        for m in free_machines:
            if not pq:
                break
            _, job_id, p, r, w = heapq.heappop(pq)
            start_time_job = max(current_time, r)
            finish_time = start_time_job + p
            machine_finish[m] = finish_time
            machine_schedule[m].append(job_id)
            scheduled_count += 1

        if free_machines:
            continue

        next_finish = min(machine_finish)
        next_release = jobs_sorted[i][2] if i < n else math.inf

        if next_release <= next_finish:
            current_time = next_release
            while i < n and jobs_sorted[i][2] <= current_time:
                job_id, p, r, w = jobs_sorted[i]
                pri = compute_priority(rule_id, p, r, w)
                heapq.heappush(pq, (pri, job_id, p, r, w))
                i += 1
            continue
        else:
            current_time = next_finish
            free_machines = [m for m in range(4) if machine_finish[m] == current_time]
            random.shuffle(free_machines)
            while i < n and jobs_sorted[i][2] <= current_time:
                job_id, p, r, w = jobs_sorted[i]
                pri = compute_priority(rule_id, p, r, w)
                heapq.heappush(pq, (pri, job_id, p, r, w))
                i += 1
            for m in free_machines:
                if not pq:
                    break
                _, job_id, p, r, w = heapq.heappop(pq)
                start_time_job = max(current_time, r)
                finish_time = start_time_job + p
                machine_finish[m] = finish_time
                machine_schedule[m].append(job_id)
                scheduled_count += 1

    total_cost = 0
    for m in range(4):
        time_on_machine = 0
        for job_id in machine_schedule[m]:
            _, p, r, w = jobs_by_id[job_id]
            time_on_machine = max(time_on_machine, r)
            time_on_machine += p
            total_cost += w * (time_on_machine - r)

    return total_cost, machine_schedule


def main():
    if len(sys.argv) != 4:
        print("Usage: python algorithm.py input.txt output.txt time_limit_seconds")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    try:
        user_time_limit = int(sys.argv[3])
    except ValueError:
        print("time_limit_seconds must be a number (int or float)")
        sys.exit(1)

    with open(input_file, 'r') as f:
        data = f.read().strip().split()

    n = int(data[0])
    jobs_list = []
    for j in range(n):
        p = int(data[3 * j + 1])
        r = int(data[3 * j + 2])
        w = int(data[3 * j + 3])
        jobs_list.append((j + 1, p, r, w))

    global jobs_by_id
    jobs_by_id = {job[0]: job for job in jobs_list}

    time_limit = user_time_limit

    start_time = time.time()
    best_cost = None
    best_schedule = None
    iterations = 0

    while True:
        now = time.time()
        if now - start_time >= time_limit*0.9:
            break

        iterations += 1
        cost, schedule = schedule_jobs(n, jobs_list)

        if best_cost is None or cost < best_cost:
            best_cost = cost
            best_schedule = schedule

    with open(output_file, 'w') as f:
        f.write(f"{best_cost}\n")
        for m in range(4):
            line = " ".join(map(str, best_schedule[m])) if best_schedule is not None else ""
            f.write(f"{line}\n")


if __name__ == "__main__":
    main()
