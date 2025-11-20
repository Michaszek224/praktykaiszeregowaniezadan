#!/usr/bin/env python3
import sys


def read_instance(path):
    with open(path, "r") as f:
        first = f.readline()
        if not first:
            raise ValueError("Pusty plik wejściowy")

        n = int(first.strip())
        jobs = {}

        for idx in range(1, n + 1):
            line = f.readline()
            if not line:
                raise ValueError("Za mało linii w pliku wejściowym")
            p, r, w = map(int, line.split())
            jobs[idx] = (p, r, w)

    return n, jobs


def build_schedule(n, jobs, machines_count=4):

    def order_key(item):
        idx, (p, r, w) = item
        ratio = p / w if w != 0 else float("inf")
        return (r, ratio)

    ordered_jobs = sorted(jobs.items(), key=order_key)

    machine_ready_time = [0] * machines_count
    machine_sequences = [[] for _ in range(machines_count)]#
    total_cost = 0

    for idx, (p, r, w) in ordered_jobs:
        best_machine = 0
        best_increment = None

        for m in range(machines_count):
            start = max(machine_ready_time[m], r)
            finish = start + p
            increment = w * (finish - r)  # w_j * (C_j - r_j)

            if best_increment is None or increment < best_increment:
                best_increment = increment
                best_machine = m

        start = max(machine_ready_time[best_machine], r)
        finish = start + p
        machine_ready_time[best_machine] = finish
        machine_sequences[best_machine].append(idx)
        total_cost += w * (finish - r)

    return total_cost, machine_sequences


def main():
    if len(sys.argv) != 4:
        print("Użycie: python3 solver.py plik_in plik_out czas")
        return

    in_file = sys.argv[1]
    out_file = sys.argv[2]
    _ = sys.argv[3]

    n, jobs = read_instance(in_file)

    total_cost, machine_sequences = build_schedule(n, jobs, machines_count=4)

    with open(out_file, "w") as f:
        f.write(str(total_cost) + "\n")
        for m in range(4):
            if machine_sequences[m]:
                f.write(" ".join(map(str, machine_sequences[m])) + "\n")
            else:
                f.write("\n")


if __name__ == "__main__":
    main()
