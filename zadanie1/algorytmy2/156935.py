import sys
import time
from pathlib import Path


def load_instance(filepath):
    with open(filepath, "r") as file:
        n, setup_time = map(int, file.readline().split())
        tasks = []
        for i in range(n):
            p, d = map(int, file.readline().split())
            tasks.append((i + 1, p, d))  # (id, p, d)
    return setup_time, tasks


def batch_lateness(batch, completion_time):
    # batch: lista (id, p, d)
    return sum(max(0, completion_time - d) for _, _, d in batch)


def total_lateness(batches, setup_time):
    total = 0
    t = 0
    first = True
    for batch in batches:
        if not batch:
            continue
        if not first:
            t += setup_time
        t += sum(p for _, p, _ in batch)
        total += batch_lateness(batch, t)
        first = False
    return total


def make_batches_greedy_edd(tasks, setup_time):
    """
    Heurystyka:
    - sortujemy EDD (rosnąco po d),
    - po kolei dokładamy zadania; dla każdego zadania porównujemy:
        A) dodać do bieżącej paczki
        B) zamknąć bieżącą paczkę i zacząć nową z tym zadaniem
      Wybieramy wariant o mniejszym natychmiastowym koszcie spóźnień.
    """
    # EDD
    tasks_sorted = sorted(tasks, key=lambda x: x[2])  # po d

    batches = []
    current_batch = []

    t_prev = 0
    first_batch_done = False


    P_B = 0

    for task in tasks_sorted:
        task_id, p_j, d_j = task

        if not current_batch:
            current_batch = [task]
            P_B = p_j
            continue

        C_A = t_prev + P_B + p_j
        lateness_A = batch_lateness(current_batch + [task], C_A)

        C_close = t_prev + P_B
        lateness_close = batch_lateness(current_batch, C_close)


        C_B = C_close + (0 if not batches and not first_batch_done else 0) + setup_time + p_j

        lateness_B = lateness_close + max(0, C_B - d_j)


        if lateness_A <= lateness_B:
            current_batch.append(task)
            P_B += p_j
        else:
            batches.append(current_batch)
            first_batch_done = True
            t_prev = C_close
            current_batch = [task]
            P_B = p_j

    # domknięcie ostatniej paczki
    if current_batch:
        batches.append(current_batch)

    return batches


def save_output(filepath, lateness, batches):
    with open(filepath, "w") as file:
        file.write(f"{int(lateness)}\n")
        file.write(f"{len(batches)}\n")
        for batch in batches:
            file.write(" ".join(str(task[0]) for task in batch) + "\n")


def main():
    if len(sys.argv) != 4:
        print("Użycie: python3 PISZ/ZADANIE1/156935.py <plik_wejściowy> <plik_wyjściowy> <limit_czasu_s>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    time_limit = float(sys.argv[3])

    setup_time, tasks = load_instance(input_path)

    start = time.perf_counter()

    batches = make_batches_greedy_edd(tasks, setup_time)
    lateness = total_lateness(batches, setup_time)

    elapsed = time.perf_counter() - start

    if elapsed > time_limit:
        print(f"Przekroczono limit czasu ({elapsed:.2f}s > {time_limit:.2f}s)")
    else:
        print(f"Czas wykonania: {elapsed:.2f} s")

    print(f"Wynik (całkowite opóźnienie): {lateness:.2f}")

    save_output(output_path, lateness, batches)


if __name__ == "__main__":
    main()
