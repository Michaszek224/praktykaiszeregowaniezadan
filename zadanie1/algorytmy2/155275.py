import sys
import time
import random
import copy
def read_input(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    n, s = map(int, lines[0].strip().split())
    p, d = [], []
    for line in lines[1:n+1]:
        pj, dj = map(int, line.strip().split())
        p.append(pj)
        d.append(dj)
    return n, s, p, d


def calc_delay(batch, p, d, start_time, setup_time, is_first=False):
    if is_first:
        end_time = start_time + sum(p[j] for j in batch)
    else:
        end_time = start_time + setup_time + sum(p[j] for j in batch)
    delay = sum(max(0, end_time - d[j]) for j in batch)
    return delay, end_time


def calculate_total_delay(batches, p, d, setup_time):
    total_delay = 0
    t = 0
    is_first = True
    for b in batches:
        delay, t = calc_delay(b, p, d, t, setup_time, is_first)
        total_delay += delay
        is_first = False
    return total_delay


def lookahead_batching(n, p, d, setup_time):
    jobs = sorted(range(n), key=lambda j: d[j]) #Daje posortowaną listę indeksów dla d po wartosciach
    batches = []
    current_batch = []
    current_time = 0

    for job in jobs:
        ####### add
        temp_batch = current_batch + [job]
        delay_if_add, _ = calc_delay(temp_batch, p, d, current_time, setup_time)
        ####### add
        
        ####### new
        if current_batch:
            delay_current, new_time = calc_delay(current_batch, p, d, current_time, setup_time)
        else: 
            delay_current = 0
            new_time = current_time
        delay_new_batch, _ = calc_delay([job], p, d, new_time, setup_time)
        delay_if_new = delay_current + delay_new_batch
        ####### new

        ####### decision
        if delay_if_add <= delay_if_new:
            current_batch.append(job)
        else:
            if current_batch:
                batches.append(current_batch)
                _, current_time = calc_delay(current_batch, p, d, current_time, setup_time)
            current_batch = [job]
        ####### decision

    ####### add last batch
    if current_batch:
        batches.append(current_batch)
        _, current_time = calc_delay(current_batch, p, d, current_time, setup_time)

    total_delay = calculate_total_delay(batches, p, d, setup_time)
    ####### add last batch
    return total_delay, batches


def local_search(batches, p, d, setup_time, time_limit,time_since_start):
    
    best_batches = copy.deepcopy(batches)
    best_delay = calculate_total_delay(best_batches, p, d, setup_time)

    while time.time() - time_since_start < time_limit:
        new_batches = copy.deepcopy(best_batches)
        i = random.randint(0, len(new_batches)-1)
        if not new_batches[i]:
            continue
        job = new_batches[i].pop(random.randint(0, len(new_batches[i])-1))
        j = random.randint(0, len(new_batches))
        if j == len(new_batches):
            new_batches.append([job])
        else:
            new_batches[j].append(job)

        new_batches = list(filter(None, new_batches))

        new_delay = calculate_total_delay(new_batches, p, d, setup_time)
        if new_delay < best_delay:
            best_delay = new_delay
            best_batches = copy.deepcopy(new_batches)
    return best_delay, best_batches


def write_output(file_path, total_delay, batches):
    with open(file_path, 'w') as f:
        f.write(str(total_delay) + "\n")
        f.write(str(len(batches)) + "\n")
        for b in batches:
            f.write(" ".join(str(j + 1) for j in b) + "\n")


if __name__ == "__main__":
    time_since_start=time.time()
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    time_limit_argv = sys.argv[3]
    time_limit=float(time_limit_argv)
    n, s, p, d = read_input(input_file)


    total_delay_greedy, batches_greedy = lookahead_batching(n, p, d, s)
    print("Greedy:", total_delay_greedy)
    improved_delay, improved_batches = local_search(batches_greedy, p, d, s, time_limit-0.5,time_since_start)
    print("Improved local:", improved_delay)
    if improved_delay < total_delay_greedy:
        best_delay = improved_delay
        best_batches = improved_batches
    else:
        best_delay = total_delay_greedy
        best_batches = batches_greedy
    print("Best:", best_delay)
    write_output(output_file, best_delay, best_batches)
