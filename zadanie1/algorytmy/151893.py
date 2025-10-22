import time
import sys

def read_input(filename):
    with open(filename) as f:
        n, s = map(int, f.readline().split())
        tasks = []
        for i in range(n):
            p, d = map(int, f.readline().split())
            tasks.append({'id': i + 1, 'p': p, 'd': d})
    return n, s, tasks


def schedule_batches(tasks, s):
    tasks.sort(key=lambda x: x['d'])
    batches = []
    current_batch = []

    for task in tasks:
        current_batch.append(task)
        if len(current_batch) >= 3:
            batches.append(current_batch)
            current_batch = []

    if current_batch:
        batches.append(current_batch)

    return batches


def compute_total_lateness(batches, s):
    time_now = 0
    total_lateness = 0
    for batch in batches:
        time_now += s + sum(t['p'] for t in batch)
        for t in batch:
            total_lateness += max(0, time_now - t['d'])
    return total_lateness


def write_output(filename, total_lateness, batches):
    with open(filename, 'w') as f:
        f.write(f"{total_lateness}\n")
        f.write(f"{len(batches)}\n")
        for batch in batches:
            f.write(" ".join(str(t['id']) for t in batch) + "\n")


def main():
    if len(sys.argv) != 4:
        print("Użycie: solvera <plik_wejściowy> <plik_wyjściowy> <limit_czasu_s>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    time_limit = float(sys.argv[3])  # limit czasu w sekundach

    n, s, tasks = read_input(input_file)

    start_time = time.perf_counter()

    batches = schedule_batches(tasks, s)
    total_lateness = compute_total_lateness(batches, s)

    end_time = time.perf_counter()
    computation_time = end_time - start_time

    # Sprawdzenie limitu czasu
    if computation_time > time_limit:
        print(f"Ostrzeżenie: przekroczono limit czasu ({computation_time:.2f}s > {time_limit:.2f}s)")

    write_output(output_file, total_lateness, batches)

    # Informacja tylko w konsoli
    print(f"Wynik zapisano do {output_file} (czas obliczeń: {computation_time:.2f} s)")


if __name__ == "__main__":
    main()
