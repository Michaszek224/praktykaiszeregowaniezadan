import sys
import time
from pathlib import Path

def read_instance(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    n = int(lines[0])
    jobs = []
    for line in lines[1:]:
        p, r, w = map(int, line.split())
        jobs.append((p, r, w))
    return n, jobs

def compute_cost(jobs, schedules):
    total = 0
    for seq in schedules:
        time_m = 0
        for j in seq:
            p, r, w = jobs[j - 1]
            start = max(time_m, r)
            completion = start + p
            cost = w * (completion - r)
            total += cost
            time_m = completion
    return total

def solve(n, jobs,  time_limit):
    #sortowanie po rosnacej wartosci r_j/s_j potem p_j
    start_time = time.time()
    indexed = []
    for idx, (p, r, w) in enumerate(jobs, start=1):
        key= (r / max(1, w), p)
        indexed.append((idx, p, r, w, key))

    #sortowanie
    indexed.sort(key=lambda x: x[4])

    #przydzial na 4 maszyny
    machine_times = [0, 0, 0, 0] #aktualny czas na maszynach
    schedules = [[], [], [], []] #numery zadan na maszynach

    for idx, p, r, w, _ in indexed:
        #znajdz nmaszyne, ktora skonczy najwczesniej swoje zadanie
        best_m = min(range(4), key=lambda m: max(machine_times[m], r) + p)

        start = max(machine_times[best_m], r)
        finish = start + p

        machine_times[best_m] = finish
        schedules[best_m].append(idx)

        #sprawdz limit czasu - jesli przekroczony to zwroc co masz
        if time.time() - start_time > time_limit:
            break

    return schedules

def write_solution(path: Path, schedules, jobs):
    value = compute_cost(jobs, schedules)

    with open(path, "w", encoding="utf-8") as f:
        f.write(str(value) + "\n")
        for seq in schedules:
            if seq:
                f.write(" ".join(map(str, seq)) + "\n")
            else:
                f.write("\n")


def main():
    if len(sys.argv) != 4:
        print("Użycie:")
        print(" python algorytm_v1.py <instancja_wejsciowa> <sciezka_na_plik_wynikowy> <limit_czasu>")
        sys.exit(1)

    in_file = Path(sys.argv[1])
    out_file = Path(sys.argv[2])
    time_limit = float(sys.argv[3])

    n, jobs = read_instance(in_file)
    schedules = solve(n, jobs, time_limit)
    write_solution(out_file, schedules, jobs)

    print(f"Zapisano wynik do: {out_file}")

if __name__ == "__main__":
    main()