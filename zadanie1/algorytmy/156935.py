import sys
import time
from pathlib import Path


def load_instance(filepath):
    with open(filepath, "r") as file:
        n, setup_time = map(int, file.readline().split())
        tasks = []
        for i in range(n):
            p, d = map(int, file.readline().split())
            tasks.append((i + 1, p, d))
    return setup_time, tasks


def make_batches(tasks, batch_size=3):
    sorted_tasks = sorted(tasks, key=lambda x: x[1])  # sortujemy po czasie wykonania p
    batches = [sorted_tasks[i:i + batch_size] for i in range(0, len(sorted_tasks), batch_size)]
    return batches


def total_lateness(batches, setup_time):
    total = 0
    time_now = 0

    for batch in batches:
        batch_duration = sum(task[1] for task in batch)
        time_now += setup_time + batch_duration

        for _, _, d in batch:
            total += max(0, time_now - d)

    return total


def save_output(filepath, lateness, batches):
    with open(filepath, "w") as file:
        file.write(f"{lateness}\n")
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

    batches = make_batches(tasks)
    lateness = total_lateness(batches, setup_time)

    elapsed = time.perf_counter() - start

    if elapsed > time_limit:
        print(f"Przekroczono limit czasu ({elapsed:.3f}s > {time_limit:.3f}s)")

    save_output(output_path, lateness, batches)


if __name__ == "__main__":
    main()
