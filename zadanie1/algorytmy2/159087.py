import sys, time, random
from pathlib import Path

#wczytujemy instancje wejsciowe
def read_instance(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        lines = [ln.strip() for ln in f if ln.strip()]
    n, s = map(int, lines[0].split())
    tasks = []
    for i, line in enumerate(lines[1:], start=1):
        p, d = map(int, line.split())
        tasks.append({"idx": i, "p": p, "d": d})
    return n, s, tasks


#obliczanie lacznego opoznienia
def total_delay(batches, jobs, s):
    t = 0
    delay = 0
    for k, batch in enumerate(batches):
        if k > 0:
            t += s
        t += sum(jobs[j]["p"] for j in batch)
        for j in batch:
            delay += max(0, t - jobs[j]["d"])
    return delay


#rozwiazanie startowe wedlug earliest due day
def greedy_start(tasks, s):
    jobs = {t["idx"]: t for t in tasks}
    order = sorted(tasks, key=lambda x: x["d"])
    batches = []
    cur = []
    t = 0
    for job in order:
        if not cur:
            cur = [job["idx"]]
            continue

        #heurystyka: dolozyc zadanie do biezacego batcha czy zamknac go
        #a zadanie wsadzic do nowego po setup-time
        cur_p = sum(jobs[x]["p"] for x in cur)

        C_with = t + cur_p + job["p"]
        tard_with = sum(max(0, C_with - jobs[x]["d"]) for x in cur + [job["idx"]])

        C_close = t + cur_p
        tard_close = sum(max(0, C_close - jobs[x]["d"]) for x in cur)

        C_new = C_close + s + job["p"]
        tard_split = tard_close + max(0, C_new - job["d"])

        if tard_with <= tard_split:
            cur.append(job["idx"])
        else:
            batches.append(cur)
            t = C_close + s
            cur = [job["idx"]]
    if cur:
        batches.append(cur)
    return batches


#losowe swap/move do szukania ulepszen
def random_optimize(batches, jobs, s, time_limit):
    rng = random.Random(20251022)
    best = [b[:] for b in batches]

    #total delay
    best_val = total_delay(best, jobs, s)
    cur = [b[:] for b in best]
    cur_val = best_val

    end = time.monotonic() + max(0, time_limit - 0.5)
    jobcount = len(jobs)

    while time.monotonic() < end:
        #losowy ruch
        new = [list(b) for b in cur]
        move = rng.choice(["move", "swap"])
        if len(new) < 2:
            break

        i, j = rng.sample(range(len(new)), 2)
        if move == "move" and new[i]:
            t = rng.choice(new[i])
            new[i].remove(t)
            if not new[i]:
                del new[i]
            j = min(j, len(new))
            if j == len(new):
                new.append([t])
            else:
                new[j].append(t)
        elif move == "swap" and new[i] and new[j]:
            a = rng.choice(new[i])
            b = rng.choice(new[j])
            new[i].remove(a)
            new[j].remove(b)
            new[i].append(b)
            new[j].append(a)

        flat = [x for b in new for x in b]
        if len(flat) != jobcount:
            continue
        flat.sort()
        for k in range(1, jobcount):
            if flat[k] == flat[k-1]:
                break
        else:
            #total delay
            val = total_delay(new, jobs, s)
            if val <= cur_val or rng.random() < 0.02:
                cur, cur_val = new, val
                if val < best_val:
                    best, best_val = new, val

    return best, best_val


#machina
def main():
    if len(sys.argv) != 4:
        print("Użycie: python algorytm.py <plik_wejściowy> <plik_wyjściowy> <limit_czasu>")
        sys.exit(1)

    in_path, out_path, time_lim = Path(sys.argv[1]), Path(sys.argv[2]), float(sys.argv[3])

    n, s, tasks = read_instance(in_path)
    jobs = {t["idx"]: t for t in tasks}

    plan = greedy_start(tasks, s)

    best_plan, best_val = random_optimize(plan, jobs, s, time_lim)

    #zapis wyniku
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"{int(best_val)}\n")
        f.write(f"{len(best_plan)}\n")
        for b in best_plan:
            f.write(" ".join(map(str, b)) + "\n")

    print(f"Łączne opóźnienie = {int(best_val)} (batchy = {len(best_plan)})")


if __name__ == "__main__":
    main()