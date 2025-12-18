import sys
import time
from pathlib import Path


def read_instance(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        content = [line.strip() for line in f if line.strip() != ""]

    if not content:
        raise ValueError(f"Plik instancji {path} jest pusty.")

    n = int(content[0].split()[0])
    if n <= 0:
        raise ValueError("n musi byc > 0.")

    expected_lines = 1 + 2 * n
    if len(content) != expected_lines:
        raise ValueError(
            f"Plik instancji {path} ma {len(content)} linii, ale spodziewano sie {expected_lines}."
        )

    p = []
    r = []
    for idx in range(1, 1 + n):
        parts = content[idx].split()
        if len(parts) != 5:
            raise ValueError(
                f"Linia {idx + 1} instancji powinna miec 5 liczb: p1 p2 p3 p4 r."
            )
        vals = [int(x) for x in parts]
        p.append(vals[:4])
        r.append(vals[4])

    S = []
    for i in range(n):
        line_idx = 1 + n + i
        parts = content[line_idx].split()
        if len(parts) != n:
            raise ValueError(
                f"Linia {line_idx + 1} macierzy S powinna miec {n} liczb."
            )
        row = [int(x) for x in parts]
        S.append(row)

    return n, p, r, S


def compute_Cmax(n: int, p: list[list[int]], r: list[int], S: list[list[int]], perm: list[int]) -> int:
    m = 4
    C = [[0] * n for _ in range(m)]

    for pos in range(n):
        job_id = perm[pos]
        j = job_id - 1

        if pos == 0:
            ready_machine = 0
        else:
            prev_job_id = perm[pos - 1]
            prev_idx = prev_job_id - 1
            ready_machine = C[0][pos - 1] + S[prev_idx][j]

        start0 = max(r[j], ready_machine)
        C[0][pos] = start0 + p[j][0]

        for k in range(1, 4):
            if pos == 0:
                ready_from_machine = 0
            else:
                prev_job_id = perm[pos - 1]
                prev_idx = prev_job_id - 1
                ready_from_machine = C[k][pos - 1] + S[prev_idx][j]

            ready_from_prev_machine = C[k - 1][pos]

            start_k = max(ready_from_machine, ready_from_prev_machine)
            C[k][pos] = start_k + p[j][k]

    return C[3][n - 1]


def main(argv: list[str]):
    if len(argv) != 4:
        print("Uzycie: python alg_3a_beta.py <plik_wejsciowy> <plik_wynikowy> <limit_czasu_s>")
        sys.exit(1)

    inst_path = Path(argv[1])
    out_path = Path(argv[2])
    try:
        time_limit = float(argv[3])
    except ValueError:
        print("Limit czasu musi byc liczba (int/float).")
        sys.exit(1)

    start_t = time.time()

    try:
        n, p, r, S = read_instance(inst_path)
    except Exception as e:
        print(f"Blad wczytywania instancji: {e}")
        sys.exit(1)

    jobs = list(range(1, n + 1))
    jobs.sort(key=lambda j: (r[j - 1], sum(p[j - 1])))

    Cmax = compute_Cmax(n, p, r, S, jobs)

    elapsed = time.time() - start_t
    if elapsed > time_limit:
        print(f"UWAGA: przekroczono limit czasu {time_limit}s (elapsed={elapsed:.4f}s)")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(str(Cmax) + "\n")
        f.write(" ".join(str(j) for j in jobs) + "\n")


if __name__ == "__main__":
    main(sys.argv)