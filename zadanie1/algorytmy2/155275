import sys
import time
import random
import copy


def read_input(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    n = int(lines[0])
    p, r, w = [], [], []
    for line in lines[1:n+1]:
        pj, rj, wj = map(int, line.strip().split())
        p.append(pj)
        r.append(rj)
        w.append(wj)
    return n, p, r, w

def calculate_total_delay(machines, p, r, w):
    total = 0
    for m in range(4):
        t = 0
        for j in machines[m]:
            start = max(t, r[j])
            finish = start + p[j]
            F = max(0, finish - r[j])
            total += w[j] * F
            t = finish
    return total


def lookahead_batching(n, p, r, w):
    jobs = sorted(range(n), key=lambda j: r[j]) 

    machines = [[], [], [], []]
    machine_time = [0, 0, 0, 0]

    for job in jobs:
        best_m = None
        best_finish = float("inf")

        for m in range(4):
            start = max(machine_time[m], r[job])
            finish = start + p[job]
            if finish < best_finish:
                best_finish = finish
                best_m = m

        machines[best_m].append(job)
        machine_time[best_m] = best_finish

    total_delay = calculate_total_delay(machines, p, r, w)
    return total_delay, machines


def local_search(machines, p, r, w, time_limit, time_since_start):

    best = copy.deepcopy(machines)
    best_delay = calculate_total_delay(best, p, r, w)

    while time.time() - time_since_start < time_limit:
        new = copy.deepcopy(best)

        # losowa maszyna i pozycja
        m1 = random.randint(0, 3)
        if not new[m1]:
            continue
        pos = random.randint(0, len(new[m1]) - 1)
        job = new[m1].pop(pos)

        # move to inna maszyna
        m2 = random.randint(0, 3)
        new[m2].insert(random.randint(0, len(new[m2])), job)

        #calculate
        new_delay = calculate_total_delay(new, p, r, w)
        if new_delay < best_delay:
            best_delay = new_delay
            best = new

    return best_delay, best


def write_output(file_path, total_delay, machines):
    with open(file_path, 'w') as f:
        f.write(str(total_delay) + "\n")
        for m in range(4):
            f.write(" ".join(str(j + 1) for j in machines[m]) + "\n")



if __name__ == "__main__":
    time_since_start = time.time()
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    time_limit_argv = sys.argv[3]
    time_limit = float(time_limit_argv)

    n, p, r, w = read_input(input_file)

    total_delay_greedy, machines_greedy = lookahead_batching(n, p, r, w)
    print("Greedy:", total_delay_greedy)

    improved_delay, improved_machines = local_search(
        machines_greedy, p, r, w,
        time_limit - 0.5,
        time_since_start
    )
    print("Improved local:", improved_delay)

    if improved_delay < total_delay_greedy:
        best_delay = improved_delay
        best_machines = improved_machines
    else:
        best_delay = total_delay_greedy
        best_machines = machines_greedy

    print("Best:", best_delay)
    write_output(output_file, best_delay, best_machines)
