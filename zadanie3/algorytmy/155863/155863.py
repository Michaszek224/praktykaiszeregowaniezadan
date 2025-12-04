import time
import random
import sys
from typing import List, Tuple


class IteratedGreedy:
    def __init__(self, n, p, r, S, time_limit):
        self.n = n
        self.p = p  # p[j][k] - czas zadania j na maszynie k
        self.r = r  # r[j] - release time
        self.S = S  # S[i][j] - setup z i na j
        self.time_limit = time_limit

    def time_limit_calc(self):
        if self.n == 50:
            self.time_limit -= 1
        elif self.n == 100:
            self.time_limit -= 2
        elif self.n == 150:
            self.time_limit -= 2
        elif self.n == 200:
            self.time_limit -= 2
        elif self.n == 250:
            self.time_limit -= 2
        elif self.n == 300:
            self.time_limit -= 2
        elif self.n == 350:
            self.time_limit -= 2
        elif self.n == 400:
            self.time_limit -= 3
        elif self.n == 450:
            self.time_limit -= 4
        elif self.n == 500:
            self.time_limit -= 5

    def calculate_makespan(self, pi: List[int]) -> int:
        n = len(pi)
        C = [[0] * 4 for _ in range(n)]

        # Pierwsze zadanie (brak setupu, bo nie ma poprzednika)
        j0 = pi[0]
        C[0][0] = self.r[j0] + self.p[j0][0]
        for k in range(1, 4):
            C[0][k] = C[0][k - 1] + self.p[j0][k]

        # Pozostałe zadania
        for i in range(1, n):
            j = pi[i]
            prev_j = pi[i - 1]
            setup = self.S[prev_j][j]
            # Maszyna 1: setup + uwzględnij release time
            C[i][0] = max(C[i - 1][0] + setup, self.r[j]) + self.p[j][0]

            # Maszyny 2-4: każda ma swój setup
            for k in range(1, 4):
                C[i][k] = max(C[i][k - 1], C[i - 1][k] + setup) + self.p[j][k]

        return C[n - 1][3]

    def neh_construction(self) -> List[int]:
        """NEH z modyfikacją dla rj i Sij"""
        jobs = list(range(self.n))

        # Sortuj według sumy czasów przetwarzania
        total_times = [sum(self.p[j]) for j in jobs]
        jobs.sort(key=lambda j: total_times[j], reverse=True)

        # Buduj sekwencję
        pi = [jobs[0]]

        for j in jobs[1:]:
            best_pos = 0
            best_makespan = float("inf")

            # Testuj wszystkie pozycje
            for pos in range(len(pi) + 1):
                test_pi = pi[:pos] + [j] + pi[pos:]
                makespan = self.calculate_makespan(test_pi)

                if makespan < best_makespan:
                    best_makespan = makespan
                    best_pos = pos

            pi.insert(best_pos, j)

        return pi

    def destruction(self, pi: List[int], d: int) -> Tuple[List[int], List[int]]:
        """Usuń d losowych zadań"""
        removed = random.sample(range(len(pi)), d)
        removed.sort(reverse=True)

        removed_jobs = [pi[i] for i in removed]
        partial = [job for i, job in enumerate(pi) if i not in removed]

        return partial, removed_jobs

    def construction(self, partial: List[int], removed: List[int]) -> List[int]:
        """Wstaw usunięte zadania w najlepsze miejsca"""
        pi = partial[:]

        for job in removed:
            best_pos = 0
            best_makespan = float("inf")

            for pos in range(len(pi) + 1):
                test_pi = pi[:pos] + [job] + pi[pos:]
                makespan = self.calculate_makespan(test_pi)

                if makespan < best_makespan:
                    best_makespan = makespan
                    best_pos = pos

            pi.insert(best_pos, job)

        return pi

    def local_search(self, pi: List[int]) -> List[int]:
        """Lokalne przeszukiwanie - swap sąsiadów"""
        improved = True
        best_pi = pi[:]
        best_makespan = self.calculate_makespan(best_pi)

        while improved:
            improved = False

            for i in range(len(best_pi) - 1):
                # Swap sąsiednich zadań
                test_pi = best_pi[:]
                test_pi[i], test_pi[i + 1] = test_pi[i + 1], test_pi[i]

                makespan = self.calculate_makespan(test_pi)

                if makespan < best_makespan:
                    best_pi = test_pi
                    best_makespan = makespan
                    improved = True
                    break

        return best_pi

    def solve(self) -> Tuple[List[int], int]:
        """Główna pętla IG"""
        start_time = time.time()

        self.time_limit_calc()

        # Inicjalizacja przez NEH
        print("Generowanie rozwiązania początkowego (NEH)...")
        best_pi = self.neh_construction()
        best_makespan = self.calculate_makespan(best_pi)

        print(f"Rozwiązanie NEH: Cmax = {best_makespan}")

        current_pi = best_pi[:]

        # Parametry
        d = max(2, self.n // 10)  # Usuń ~10% zadań
        no_improve_count = 0
        max_no_improve = 100

        iterations = 0

        # Główna pętla
        while True:
            if time.time() - start_time >= self.time_limit:
                break
            iterations += 1

            # Destrukcja
            partial, removed = self.destruction(current_pi, d)

            if time.time() - start_time >= self.time_limit:
                break

            # Konstrukcja
            new_pi = self.construction(partial, removed)

            if time.time() - start_time >= self.time_limit:
                break

            # Lokalne przeszukiwanie (co 10 iteracji)
            if iterations % 10 == 0:
                new_pi = self.local_search(new_pi)
                if time.time() - start_time >= self.time_limit:
                    break

            new_makespan = self.calculate_makespan(new_pi)

            # Akceptacja
            if new_makespan < best_makespan:
                best_pi = new_pi
                best_makespan = new_makespan
                current_pi = new_pi[:]
                no_improve_count = 0
                print(f"Iteracja {iterations}: Nowy best Cmax = {best_makespan}")
            elif new_makespan < self.calculate_makespan(current_pi):
                current_pi = new_pi
                no_improve_count = 0
            else:
                no_improve_count += 1

            # Restart jeśli brak poprawy
            if no_improve_count > max_no_improve:
                current_pi = self.neh_construction()
                no_improve_count = 0
                d = max(2, min(self.n // 5, d + 1))  # Zwiększ destrukcję

        print(f"\nZakończono po {iterations} iteracjach")
        print(f"Czas: {time.time() - start_time:.2f}s")

        return best_pi, best_makespan


def read_input(filename: str):
    """Wczytaj dane z pliku"""
    with open(filename, "r") as f:
        lines = f.readlines()

    n = int(lines[0].strip())

    p = []
    r = []
    for i in range(1, n + 1):
        values = list(map(int, lines[i].split()))
        p.append(values[:4])
        r.append(values[4])

    S = []
    for i in range(n + 1, 2 * n + 1):
        S.append(list(map(int, lines[i].split())))

    return n, p, r, S


def write_output(filename: str, pi: List[int], makespan: int):
    """Zapisz wynik"""
    with open(filename, "w") as f:
        f.write(f"{makespan}\n")
        f.write(" ".join(str(j + 1) for j in pi) + "\n")


# Użycie
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Użycie: python3 155863.py <input.txt> <output.txt> <time_limit>")
        exit(1)
    input = sys.argv[1]
    output = sys.argv[2]
    time_limit = float(sys.argv[3])

    # Wczytaj dane
    n, p, r, S = read_input(input)

    # Ustal limit czasu

    print(f"Rozwiązywanie problemu: n={n}, time_limit={time_limit}s")

    # Uruchom IG
    ig = IteratedGreedy(n, p, r, S, time_limit)
    best_pi, best_makespan = ig.solve()

    # Zapisz wynik
    write_output(output, best_pi, best_makespan)

    print(f"\nWynik końcowy: Cmax = {best_makespan}")
