import sys
import math
import heapq
import time

def schedule_jobs(n, jobs, time_limit, start_time):
    jobs.sort(key=lambda x: x[2])
    pq = []
    machine_finish = [0] * 4
    machine_schedule = [[] for _ in range(4)]
    i = 0
    current_time = 0
    scheduled_count = 0

    while scheduled_count < n:
        if time_limit is not None and (time.time() - start_time) > time_limit:
            return None, None, True

        if not pq:
            if i < n:
                next_release = jobs[i][2]
                if current_time < next_release:
                    current_time = next_release
                while i < n and jobs[i][2] <= current_time:
                    job_id, p, r, w = jobs[i]
                    heapq.heappush(pq, (p / float(w), job_id, p, r, w))
                    i += 1
            else:
                break

        free_machines = [m for m in range(4) if machine_finish[m] <= current_time]
        for m in free_machines:
            if time_limit is not None and (time.time() - start_time) > time_limit:
                return None, None, True

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
        next_release = jobs[i][2] if i < n else math.inf
        if next_release <= next_finish:
            current_time = next_release
            while i < n and jobs[i][2] <= current_time:
                job_id, p, r, w = jobs[i]
                heapq.heappush(pq, (p / float(w), job_id, p, r, w))
                i += 1
            continue
        else:
            current_time = next_finish
            free_machines = [m for m in range(4) if machine_finish[m] == current_time]
            while i < n and jobs[i][2] <= current_time:
                job_id, p, r, w = jobs[i]
                heapq.heappush(pq, (p / float(w), job_id, p, r, w))
                i += 1
            for m in free_machines:
                if time_limit is not None and (time.time() - start_time) > time_limit:
                    return None, None, True

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

    return total_cost, machine_schedule, False


def main():
    if len(sys.argv) != 4:
        print("Usage: python algorithm.py input.txt output.txt time_limit_seconds")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    try:
        time_limit = float(sys.argv[3])
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

    start_time = time.time()
    total_cost, schedule, timeout = schedule_jobs(n, jobs_list, time_limit, start_time)

    with open(output_file, 'w') as f:
        if timeout:
            f.write("TIME_LIMIT_EXCEEDED\n")
        else:
            f.write(f"{total_cost}\n")
            for m in range(4):
                line = " ".join(map(str, schedule[m]))
                f.write(f"{line}\n")


if __name__ == "__main__":
    main()
