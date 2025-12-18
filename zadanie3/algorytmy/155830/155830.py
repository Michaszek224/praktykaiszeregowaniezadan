import sys
import time
import random

random.seed(42)
N = 0
P = []
R = []
S = []

def calc_cmax(seq):
    t1 = t2 = t3 = t4 = 0
    prev = None
    local_P, local_R, local_S = P, R, S

    for j in seq:
        if prev is not None:
            setup = local_S[prev][j]
            t1 += setup; t2 += setup; t3 += setup; t4 += setup
        
        pj = local_P[j]
        rj = local_R[j]

        if t1 < rj: t1 = rj
        t1 += pj[0]
        if t2 < t1: t2 = t1
        t2 += pj[1]
        if t3 < t2: t3 = t2
        t3 += pj[2]
        if t4 < t3: t4 = t3
        t4 += pj[3]

        prev = j
    return t4

def detect_setup_impact():
    diff_sum = 0
    samples = 5
    for _ in range(samples):
        seq = random.sample(range(N), N)
        c_real = calc_cmax(seq)
        
        setup_total = 0
        prev = None
        for j in seq:
            if prev is not None:
                setup_total += S[prev][j]
            prev = j
        
        if setup_total / c_real > 0.15:
            diff_sum += 1
            
    return diff_sum >= 3

def solve(time_limit):
    start_time = time.time()
    cutoff = time_limit * 0.95
        
    is_setup_heavy = detect_setup_impact()
    indices = list(range(N))
    
    seeds = []
    seeds.append(sorted(indices, key=lambda i: sum(P[i]), reverse=True))
    seeds.append(sorted(indices, key=lambda i: (R[i], sum(P[i]))))
    
    if is_setup_heavy:
        curr = min(indices, key=lambda i: R[i])
        tsp_seq = [curr]
        unvisited = set(indices) - {curr}
        while unvisited:
            nxt = min(unvisited, key=lambda x: (S[curr][x], R[x] * 0.1))
            tsp_seq.append(nxt)
            unvisited.remove(nxt)
            curr = nxt
        seeds.insert(0, tsp_seq) 

    best_seq = []
    best_cmax = float('inf')
    neh_cutoff = start_time + (cutoff - start_time) * 0.15

    for idx, seed in enumerate(seeds):
        if time.time() > neh_cutoff and idx > 0: break
            
        curr_seq = [seed[0]]
        for i in range(1, N):
            job = seed[i]
            best_pos, best_val = -1, float('inf')
            
            for pos in range(len(curr_seq) + 1):
                cand = curr_seq[:pos] + [job] + curr_seq[pos:]
                c = calc_cmax(cand)
                if c < best_val:
                    best_val = c
                    best_pos = pos
            curr_seq.insert(best_pos, job)
        
        c = calc_cmax(curr_seq)
        if c < best_cmax:
            best_cmax = c
            best_seq = curr_seq

    curr_seq = list(best_seq)
    curr_cmax = best_cmax
    
    search_radius = 50
    stagnation = 0
    max_stagnation = 300

    while time.time() - start_time < cutoff:
        d = max(2, min(25, int(N * 0.005)))
        candidate = list(curr_seq)
        removed = []
        
        idxs = sorted(random.sample(range(len(candidate)), d), reverse=True)
        for idx in idxs:
            removed.append(candidate.pop(idx))
            
        for job in removed:
            best_pos, best_val = -1, float('inf')
            for pos in range(len(candidate) + 1):
                cand = candidate[:pos] + [job] + candidate[pos:]
                c = calc_cmax(cand)
                if c < best_val:
                    best_val = c
                    best_pos = pos
            candidate.insert(best_pos, job)
            
        improved = True
        while improved:
            improved = False
            if time.time() - start_time > cutoff: break
            
            target_idx = -1
            if is_setup_heavy:
                try:
                    samp = random.sample(range(1, len(candidate)), min(5, len(candidate)-1))
                    target_idx = max(samp, key=lambda i: S[candidate[i-1]][candidate[i]])
                except ValueError:
                    target_idx = random.randrange(len(candidate))
            else:
                target_idx = random.randrange(len(candidate))
                
            job = candidate.pop(target_idx)
            best_pos = target_idx 
            
            candidate.insert(target_idx, job)
            best_local_c = calc_cmax(candidate) 
            candidate.pop(target_idx)
            
            start = max(0, target_idx - search_radius)
            end = min(len(candidate) + 1, target_idx + search_radius)
            
            for pos in range(start, end):
                if pos == target_idx: continue
                cand = candidate[:pos] + [job] + candidate[pos:]
                c = calc_cmax(cand)
                if c < best_local_c:
                    best_local_c = c
                    best_pos = pos
            
            candidate.insert(best_pos, job)
            
            if best_local_c < curr_cmax:
                curr_cmax = best_local_c
                improved = True
                
            if not improved and is_setup_heavy:
                swap_limit = 30
                for _ in range(swap_limit):
                    i = best_pos
                    j = random.randrange(len(candidate))
                    if i == j: continue
                    
                    candidate[i], candidate[j] = candidate[j], candidate[i]
                    c = calc_cmax(candidate)
                    
                    if c < curr_cmax:
                        curr_cmax = c
                        improved = True
                        break 
                    else:
                        candidate[i], candidate[j] = candidate[j], candidate[i]

        c_final = calc_cmax(candidate)
        if c_final <= curr_cmax:
            curr_cmax = c_final
            curr_seq = list(candidate)
            if c_final < best_cmax:
                best_cmax = c_final
                best_seq = list(candidate)
                stagnation = 0
            else:
                stagnation += 1
        else:
            stagnation += 1
            
        if stagnation > max_stagnation:
            curr_seq = list(best_seq)
            curr_cmax = best_cmax
            stagnation = 0

    return best_cmax, best_seq

def main():
    global N, P, R, S
    if len(sys.argv) < 4: return

    with open(sys.argv[1], 'r') as f:
        data = f.read().split()
    it = iter(data)

    try:
        N = int(next(it))
        for _ in range(N):
            P.append([int(next(it)) for _ in range(4)])
            R.append(int(next(it)))
        
        raw = [int(next(it)) for _ in range(N*N)]
        S = [raw[i*N:(i+1)*N] for i in range(N)]
    except StopIteration: return

    time_limit = N / 10.0
    cmax, seq = solve(time_limit)

    final_ids = [i+1 for i in seq]
    with open(sys.argv[2], 'w') as f:
        f.write(f"{cmax}\n")
        f.write(" ".join(map(str, final_ids)) + "\n")

if __name__ == "__main__":
    main()