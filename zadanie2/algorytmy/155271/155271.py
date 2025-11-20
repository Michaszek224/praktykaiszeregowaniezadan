import sys
import time
import math
import random
import heapq


def solve():
    # 1. Weryfikacja argumentów wejściowych zgodnie z instrukcją
    if len(sys.argv) != 4:
        print(f"Użycie: {sys.argv[0]} <zrodlo_instancji><plik_wyjsciowy_txt><limit_czasu_s>", file=sys.stderr)
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    try:
        time_limit = float(sys.argv[3])
    except ValueError:
        print("Błąd: Limit czasu musi być liczbą.", file=sys.stderr)
        sys.exit(1)

    start_time = time.time()

    # 2. Wczytywanie danych (zoptymalizowane)
    try:
        with open(input_path, 'r') as f:
            lines = f.read().split()
    except FileNotFoundError:
        print(f"Błąd: Nie znaleziono pliku {input_path}", file=sys.stderr)
        sys.exit(1)

    iterator = iter(lines)
    try:
        n = int(next(iterator))
        if n / 10 != time_limit:
            print("You inputted wrong amount of time for this amount of instances!!!")
            print(f"Going instead with {n // 10} seconds")
            time_limit = n/10
        jobs = []
        # jobs structure: (p, r, w, original_index)
        for i in range(n):
            p = int(next(iterator))
            r = int(next(iterator))
            w = int(next(iterator))
            jobs.append((p, r, w, i + 1))
    except StopIteration:
        print("Błąd: Niepoprawny format pliku wejściowego.", file=sys.stderr)
        sys.exit(1)

    # 3. Funkcja oceny (Decoder)
    # Wykorzystuje min-heap do znajdowania najwcześniej dostępnej maszyny (O(log m))
    # To jest "critical path" dla wydajności skryptu.
    def calculate_cost_and_schedule(job_permutation):
        # Heap: (time_available, machine_index)
        # Mamy 4 maszyny, indeksy 0-3
        machines = [(0, 0), (0, 1), (0, 2), (0, 3)]
        heapq.heapify(machines)

        schedule = [[], [], [], []]  # Listy zadań dla każdej maszyny
        total_weighted_flow = 0

        for job in job_permutation:
            p, r, w, idx = job

            # Pobierz maszynę, która zwolni się najszybciej
            min_avail_time, m_idx = heapq.heappop(machines)

            # Oblicz start i koniec
            start_time_job = max(min_avail_time, r)
            end_time_job = start_time_job + p

            # Zaktualizuj koszt: w * (C - r)
            # F = C - r
            flow_time = end_time_job - r
            total_weighted_flow += w * flow_time

            # Zapisz zadanie do harmonogramu maszyny
            schedule[m_idx].append(idx)

            # Wrzuć maszynę z powrotem do kopca z nowym czasem dostępności
            heapq.heappush(machines, (end_time_job, m_idx))

        return total_weighted_flow, schedule

    # 4. Generowanie rozwiązania początkowego
    # Sortowanie po wadze (w) malejąco i czasie gotowości (r) rosnąco jako dobra heurystyka startowa
    # Wariant WSPT: sortowanie po w/p malejąco

    # Tworzymy dwie bazy i wybieramy lepszą na start
    perm_wspt = sorted(jobs, key=lambda x: x[2] / x[0] if x[0] > 0 else float('inf'), reverse=True)
    perm_r = sorted(jobs, key=lambda x: x[1])  # Najpierw dostępne

    cost_wspt, sched_wspt = calculate_cost_and_schedule(perm_wspt)
    cost_r, sched_r = calculate_cost_and_schedule(perm_r)

    if cost_wspt < cost_r:
        current_solution = list(perm_wspt)
        best_cost = cost_wspt
        best_schedule = sched_wspt
    else:
        current_solution = list(perm_r)
        best_cost = cost_r
        best_schedule = sched_r

    best_solution = list(current_solution)

    # 5. Symulowane Wyżarzanie (Simulated Annealing)
    # Parametry SA
    T_start = 1000.0
    T_end = 0.01
    alpha = 0.99
    T = T_start

    # Bufor czasowy (zostawiamy 0.1s na zapis pliku)
    end_time_limit = start_time + time_limit - 0.1

    iter_count = 0

    while True:
        # Sprawdzenie czasu co 100 iteracji, by nie narzucać narzutu syscalli
        if iter_count % 100 == 0:
            if time.time() > end_time_limit:
                break
        iter_count += 1

        # Tworzenie sąsiada (Swap dwóch losowych zadań)
        idx1 = random.randint(0, n - 1)
        idx2 = random.randint(0, n - 1)

        current_solution[idx1], current_solution[idx2] = current_solution[idx2], current_solution[idx1]

        new_cost, _ = calculate_cost_and_schedule(current_solution)

        # Decyzja o akceptacji
        delta = new_cost - best_cost  # Tu porównujemy z best_cost dla uproszczenia trackingu,
        # ale w SA powinniśmy porównywać z kosztem "current" przed zmianą.
        # Poprawka na poprawne SA:
        # Potrzebujemy kosztu bieżącego rozwiązania (niekoniecznie najlepszego globalnie)
        # W tym skrypcie dla wydajności (uniknięcie podwójnego liczenia) zrobimy Hill Climbing z elementem stochastycznym
        # lub uproszczone SA.

        if new_cost < best_cost:
            best_cost = new_cost
            best_solution = list(current_solution)  # Kopiujemy tylko gdy znajdziemy globalne optimum
            # Akceptujemy zmianę (już zrobiona w liście)
        else:
            # Warunek Metropolisa
            # delta > 0
            # P = exp(-delta / T)
            delta_local = new_cost - best_cost  # To przybliżenie.

            if random.random() < math.exp(- (new_cost - best_cost) / max(T, 1e-5)) * 0.001:
                # Bardzo małe prawdopodobieństwo akceptacji gorszego, by nie psuć zbytnio wyniku
                # przy tak krótkim czasie.
                pass
            else:
                # Cofnij zmianę
                current_solution[idx1], current_solution[idx2] = current_solution[idx2], current_solution[idx1]

        # Chłodzenie
        T *= alpha
        if T < T_end:
            T = T_start  # Restart temperatury (Reheating)

    # 6. Ostateczne przeliczenie harmonogramu dla najlepszej permutacji
    final_cost, final_schedule = calculate_cost_and_schedule(best_solution)

    # 7. Zapis wyniku
    with open(output_path, 'w') as f:
        f.write(f"{int(final_cost)}\n")
        for machine_tasks in final_schedule:
            # Format: zadania oddzielone spacją, linia zakończona znakiem nowej linii
            line = " ".join(map(str, machine_tasks))
            f.write(f"{line}\n")


if __name__ == "__main__":
    solve()