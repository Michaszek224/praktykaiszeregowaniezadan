import sys
import time
from pathlib import Path
from statistics import median



def load_instance(filepath):
    with open(filepath, "r") as file:
        n, setup_time = map(int, file.readline().split())
        tasks = []
        for i in range(n):
            p, d = map(int, file.readline().split())
            tasks.append((i + 1, p, d))
    return setup_time, tasks


def save_output(filepath, lateness, batches):
    with open(filepath, "w") as file:
        file.write(f"{lateness}\n")
        file.write(f"{len(batches)}\n")
        for batch in batches:
            file.write(" ".join(str(task[0]) for task in batch) + "\n")




def total_lateness(batches, setup_time):
    total = 0
    t = 0
    first = True

    for batch in batches:
        if not batch:
            continue
        if not first:
            t += setup_time
        t += sum(task[1] for task in batch)
        for _, _, d in batch:
            total += max(0, t - d)
        first = False
    return total


def initial_batches(tasks, setup_time):
    tasks_sorted = sorted(tasks, key=lambda x: x[2])
    if not tasks_sorted:
        return []

    ps = [p for _, p, _ in tasks_sorted]
    w = max(setup_time, int(median(ps)))
    batches = []
    cur = []
    last_d = None

    for task in tasks_sorted:
        _, p, d = task
        if not cur:
            cur = [task]
            last_d = d
        else:
            if d - last_d <= w:
                cur.append(task)
            else:
                batches.append(cur)
                cur = [task]
                last_d = d
    if cur:
        batches.append(cur)
    return batches


def try_merge(batches, k, setup_time, best_val):
    if k < 0 or k >= len(batches) - 1:
        return None
    merged = batches[:k] + [batches[k] + batches[k + 1]] + batches[k + 2:]
    val = total_lateness(merged, setup_time)
    if val < best_val:
        return merged, val
    return None


def try_split(batches, k, split_idx, setup_time, best_val):
    b = batches[k]
    if split_idx <= 0 or split_idx >= len(b):
        return None
    b1, b2 = b[:split_idx], b[split_idx:]
    split_sol = batches[:k] + [b1, b2] + batches[k + 1:]
    val = total_lateness(split_sol, setup_time)
    if val < best_val:
        return split_sol, val
    return None


def try_swap_adjacent(batches, k, setup_time, best_val):
    if k < 0 or k >= len(batches) - 1:
        return None
    swapped = batches[:k] + [batches[k + 1], batches[k]] + batches[k + 2:]
    val = total_lateness(swapped, setup_time)
    if val < best_val:
        return swapped, val
    return None


def try_move_one(batches, k, direction, setup_time, best_val):
    if k < 0 or k >= len(batches) - 1:
        return None

    left, right = batches[k], batches[k + 1]

    if direction == +1 and len(left) >= 2:
        new_left = left[:-1]
        new_right = [left[-1]] + right
        moved = batches[:k] + [new_left, new_right] + batches[k + 2:]
        val = total_lateness(moved, setup_time)
        if val < best_val:
            return moved, val

    if direction == -1 and len(right) >= 2:
        new_left = left + [right[0]]
        new_right = right[1:]
        moved = batches[:k] + [new_left, new_right] + batches[k + 2:]
        val = total_lateness(moved, setup_time)
        if val < best_val:
            return moved, val

    return None


def improve(batches, setup_time, time_budget_s):
    start = time.perf_counter()
    best = [list(b) for b in batches]
    best_val = total_lateness(best, setup_time)

    while time.perf_counter() - start < time_budget_s:
        improved = False
        for k in range(len(batches) - 1):
            if time.perf_counter() - start >= time_budget_s:
                break
            res = try_merge(batches, k, setup_time, best_val)
            if res:
                batches, best_val = res
                best = [list(b) for b in batches]
                improved = True
                break
        if improved:
            continue

        for k, b in enumerate(batches):
            if time.perf_counter() - start >= time_budget_s:
                break
            if len(b) <= 1:
                continue
            for i in range(1, len(b)):
                res = try_split(batches, k, i, setup_time, best_val)
                if res:
                    batches, best_val = res
                    best = [list(b) for b in batches]
                    improved = True
                    break
            if improved:
                break
        if improved:
            continue

        for k in range(len(batches) - 1):
            if time.perf_counter() - start >= time_budget_s:
                break
            res = try_swap_adjacent(batches, k, setup_time, best_val)
            if res:
                batches, best_val = res
                best = [list(b) for b in batches]
                improved = True
                break
        if improved:
            continue

        for k in range(len(batches) - 1):
            if time.perf_counter() - start >= time_budget_s:
                break
            for direction in (+1, -1):
                res = try_move_one(batches, k, direction, setup_time, best_val)
                if res:
                    batches, best_val = res
                    best = [list(b) for b in batches]
                    improved = True
                    break
            if improved:
                break

        if not improved:
            break

    return best, best_val


def main():
    if len(sys.argv) != 4:
        print("Użycie: python3 solver.py <plik_wejściowy> <plik_wyjściowy> <limit_czasu_s>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    time_limit = float(sys.argv[3])

    setup_time, tasks = load_instance(input_path)

    t0 = time.perf_counter()
    batches = initial_batches(tasks, setup_time)
    best_batches, best_val = improve(batches, setup_time, max(0.0, time_limit - 0.01))
    elapsed = time.perf_counter() - t0

    print(f" Czas wykonania: {elapsed:.3f} s")
    print(f" Wynik (Dj): {best_val}")

    save_output(output_path, best_val, best_batches)


if __name__ == "__main__":
    main()
