import sys
import time
import math
from pathlib import Path

def read_instance(file_path: Path):
    #wczytywnie instancj
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.read().strip().splitlines()
    n, s = map(int, lines[0].split())
    tasks = []
    for i, line in enumerate(lines[1:], start=1):
        pj, dj = map(int, line.split())
        tasks.append((i, pj, dj))
    return n, s, tasks

def compute_total_delay(batches, tasks, s):
    task_dict = {i: (pj, dj) for i, pj, dj in tasks}
    total_delay = 0
    time_now = 0
    for batch in batches:
        batch_p = sum(task_dict[i][0] for i in batch)
        batch_c = time_now + batch_p
        for i in batch:
            _, dj = task_dict[i]
            total_delay += max(0, batch_c - dj)
        time_now = batch_c + s
    return total_delay

def schedule_tasks(n, s, tasks):
    #sortowanie paczek po due_day (rosnaco)
    task_sorted = sorted(tasks, key=lambda x: x[2])

    #grupowanie po podobnych deadlinach
    batch_size = max(1, int(math.sqrt(n)))
    batches = []
    for i in range(0, n, batch_size):
        batch = [t[0] for t in task_sorted[i:i + batch_size]]
        batches.append(batch)

    #sortowanie batchy po najmniejszym due-day
    batches.sort(key=lambda b: min(tasks[t-1][2] for t in b))

    return batches

def main():
    if len(sys.argv) != 4:
        print("Użycie algorytmu: python 159087.py <plik_instancji.txt> <plik_wynikowy.txt> <limit_czasu>")
        sys.exit(1)

    instance_file = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    time_limit = float(sys.argv[3])

    start_time = time.perf_counter()
    n, s, tasks = read_instance(instance_file)

    #jesli przekroczono limit czasu juz przy wczytywaniu (na wszelki)
    if time.perf_counter() - start_time > time_limit:
        print("Przekroczono limit czasu podczas wczytywania danych")
        sys.exit(1)

    #harmonogram
    batches = schedule_tasks(n, s, tasks)

    if time.perf_counter() - start_time > time_limit:
        print("Przekroczono limit czasu podczas generowania harmonogramu")
        sys.exit(1)

    total_delay = compute_total_delay(batches, tasks, s)

    if time.perf_counter() - start_time > time_limit:
        print("Przekroczono limit czasu podczas obliczen")
        sys.exit(1)

    #zapis do pliku
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"{total_delay}\n")
        f.write(f"{len(batches)}\n")
        for batch in batches:
            f.write(" ".join(map(str, batch)) + "\n")

    print(f"Wynik zapisano do {output_path.resolve()}")
    print(f"Łączne opóźnienie = {total_delay}")
    print(f"Liczba batchy = {len(batches)}")

if __name__ == "__main__":
    main()

