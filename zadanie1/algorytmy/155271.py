import sys
import os
import time
import math
import random
import copy
from dataclasses import dataclass
from typing import List



@dataclass
class Job:
    """Reprezentuje pojedyncze zadanie."""
    id: int
    p: int  # Czas przetwarzania
    d: int  # Termin zakończenia


# W Pythonie, harmonogram i paczki można reprezentować jako listy zagnieżdżone.
# Schedule: List[Batch]
# Batch: List[int] (lista ID zadań)
Schedule = List[List[int]]


# --- Implementacje funkcji ---

def read_instance(filename: str) -> tuple[List[Job], int, int]:
    """Wczytuje dane instancji z pliku."""
    try:
        with open(filename, 'r') as f:
            n, s = map(int, f.readline().split())
            jobs = []
            for i in range(n):
                p, d = map(int, f.readline().split())
                jobs.append(Job(id=i + 1, p=p, d=d))
            return jobs, n, s
    except FileNotFoundError:
        print(f"Błąd: Nie można otworzyć pliku wejściowego {filename}", file=sys.stderr)
        return None, 0, 0


def write_solution(filename: str, schedule: Schedule, tardiness: int):
    """Zapisuje rozwiązanie do pliku."""
    try:
        with open(filename, 'w') as f:
            f.write(f"{tardiness}\n")
            f.write(f"{len(schedule)}\n")
            # Filtrujemy puste paczki przed zapisem, jeśli takie powstały
            for batch in schedule:
                if batch:  # Zapisuj tylko niepuste paczki
                    f.write(' '.join(map(str, batch)) + '\n')
    except IOError:
        print(f"Błąd: Nie można zapisać do pliku {filename}", file=sys.stderr)


def calculate_total_tardiness(schedule: Schedule, jobs: List[Job], s: int) -> int:
    """
    Oblicza całkowite opóźnienie dla danego harmonogramu.
    """
    if not schedule:
        return 0

    # Mapa JobID -> Obiekt Job dla szybkiego dostępu
    jobs_map = {job.id: job for job in jobs}

    total_tardiness = 0
    current_completion_time = 0
    is_first_batch = True

    # Iterujemy przez każdy batch DOKŁADNIE w takiej kolejności,
    # w jakiej jest podany w harmonogramie 'schedule'.
    for batch in schedule:
        # Pomiń puste paczki, jeśli takie powstaną w trakcie SA
        if not batch:
            continue

        if not is_first_batch:
            # Dodajemy czas przygotowawczy 's' między batchami
            current_completion_time += s

        # Niezależnie od tego czy dodaliśmy 's', ta paczka już nie jest pierwsza
        is_first_batch = False

        # Czas przetwarzania batcha to suma czasów jego zadań
        # Używamy jobs_map do znalezienia czasu 'p'
        try:
            batch_processing_time = sum(jobs_map[job_id].p for job_id in batch)
        except KeyError as e:
            print(f"Błąd krytyczny w calculate_total_tardiness: Nie znaleziono job_id {e}", file=sys.stderr)
            # To nie powinno się zdarzyć, jeśli SA działa poprawnie
            return sys.maxsize

        current_completion_time += batch_processing_time

        # Czas Ck jest taki sam dla wszystkich zadań w danym batchu
        batch_completion_time_Ck = current_completion_time

        # Obliczamy opóźnienie dla każdego zadania w batchu
        for job_id in batch:
            try:
                due_date = jobs_map[job_id].d
                # Używamy max(0, ...)
                tardiness = max(0, batch_completion_time_Ck - due_date)
                total_tardiness += tardiness
            except KeyError as e:
                print(f"Błąd krytyczny w calculate_total_tardiness (wewnętrzna pętla): Nie znaleziono job_id {e}",
                      file=sys.stderr)
                return sys.maxsize

    return total_tardiness


def generate_initial_solution(jobs: List[Job], n: int) -> Schedule:
    """Generuje proste rozwiązanie startowe (heurystyka oparta na EDD)."""
    if n == 0:
        return []

    sorted_jobs = sorted(jobs, key=lambda job: job.d)

    schedule: Schedule = []
    current_batch: List[int] = []

    batch_size_threshold = 2 * int(math.sqrt(n)) if n > 0 else 1
    if batch_size_threshold == 0:
        batch_size_threshold = 1

    for job in sorted_jobs:
        if len(current_batch) >= batch_size_threshold:
            schedule.append(current_batch)
            current_batch = []
        current_batch.append(job.id)

    if current_batch:
        schedule.append(current_batch)

    return schedule


def simulated_annealing(jobs: List[Job], n: int, s: int, time_limit: int) -> Schedule:
    """Główna pętla algorytmu symulowanego wyżarzania z inteligentnym warunkiem stopu."""
    start_time = time.time()

    current_schedule = generate_initial_solution(jobs, n)
    best_schedule = copy.deepcopy(current_schedule)

    current_cost = calculate_total_tardiness(current_schedule, jobs, s)
    best_cost = current_cost

    max_iterations_without_improvement = max(4000, n * 80)
    iterations_without_improvement = 0

    temperature = 1000.0
    cooling_rate = 0.998

    while (time.time() - start_time+0.3 < time_limit) and \
            (iterations_without_improvement < max_iterations_without_improvement):

        # Usuwamy puste paczki z bieżącego harmonogramu, aby uniknąć błędów
        current_schedule = [batch for batch in current_schedule if batch]

        if not current_schedule or n == 0:
            # Jeśli harmonogram jest pusty (co nie powinno się zdarzyć dla n > 0)
            break

        new_schedule = copy.deepcopy(current_schedule)

        move_type = random.random()

        if len(new_schedule) > 1 and move_type < 0.5:
            try:
                b1_idx, b2_idx = random.sample(range(len(new_schedule)), 2)

                if new_schedule[b1_idx] and new_schedule[b2_idx]:
                    job1_idx = random.randrange(len(new_schedule[b1_idx]))
                    job2_idx = random.randrange(len(new_schedule[b2_idx]))

                    job1_id = new_schedule[b1_idx].pop(job1_idx)
                    job2_id = new_schedule[b2_idx].pop(job2_idx)

                    new_schedule[b1_idx].append(job2_id)
                    new_schedule[b2_idx].append(job1_id)
            except ValueError as e:
                # Może się zdarzyć, jeśli paczki stały się puste
                print(f"Ostrzeżenie (Ruch 1): {e}", file=sys.stderr)
                pass  # Pomiń ten ruch

        else:
            try:
                job_to_move = random.choice(jobs)
                job_id_to_move = job_to_move.id

                source_batch_idx = -1
                for i, batch in enumerate(new_schedule):
                    if job_id_to_move in batch:
                        source_batch_idx = i
                        batch.remove(job_id_to_move)
                        break

                # Jeśli paczka źródłowa jest teraz pusta, usuń ją
                if source_batch_idx != -1 and not new_schedule[source_batch_idx]:
                    del new_schedule[source_batch_idx]

                # Jeśli po usunięciu nie ma żadnych paczek, utwórz nową
                if not new_schedule:
                    new_schedule.append([job_id_to_move])
                else:
                    # Dodaj do losowej istniejącej paczki
                    dest_batch_idx = random.randrange(len(new_schedule))
                    new_schedule[dest_batch_idx].append(job_id_to_move)
            except (IndexError, ValueError) as e:
                # Może się zdarzyć, jeśli listy są puste
                print(f"Ostrzeżenie (Ruch 2): {e}", file=sys.stderr)
                pass  # Pomiń ten ruch

        if (time.time() - start_time >= time_limit):
            print(f"   Zakończono z powodu przekroczenia limitu czasu ({time_limit}s).")
            break

        new_cost = calculate_total_tardiness(new_schedule, jobs, s)
        cost_diff = new_cost - current_cost



        if cost_diff < 0 or (temperature > 0 and math.exp(-cost_diff / temperature) > random.random()):
            current_schedule = new_schedule
            current_cost = new_cost

        if current_cost < best_cost:
            best_schedule = copy.deepcopy(current_schedule)
            best_cost = current_cost
            iterations_without_improvement = 0
        else:
            iterations_without_improvement += 1

        temperature *= cooling_rate

    if time.time() - start_time >= time_limit:
        print(f"   Zakończono z powodu przekroczenia limitu czasu ({time_limit}s).")
    else:
        print(f"   Zakończono, ponieważ nie znaleziono poprawy przez {max_iterations_without_improvement} iteracji.")

    # Zwróć najlepszy harmonogram (oczyszczony z pustych paczek)
    best_schedule = [batch for batch in best_schedule if batch]
    return best_schedule


# --- Główna funkcja ---

def main():
    """Główna funkcja programu, obsługująca argumenty i przepływ sterowania."""
    if len(sys.argv) != 4:
        print(f"Użycie: {sys.argv[0]} <zrodlo_instancji><plik_wyjsciowy_txt><limit_czasu_s>", file=sys.stderr)
        print(f"Przykład: {sys.argv[0]} ./instancje/in_155271_50.txt 50 60", file=sys.stderr)
        return 1

    input_file = sys.argv[1]
    # Poprawka: drugi argument to nazwa pliku wyjściowego, a nie tylko liczba 'n'
    output_file_name = sys.argv[2]
    time_limit_per_instance = int(sys.argv[3])

    print(f"--- Rozpoczęto przetwarzanie dla pliku: {input_file} ---")
    print(f"--- Nazwa pliku wyjsciowego: {output_file_name} ---")
    print(f"--- MAKSYMALNY limit czasu: {time_limit_per_instance} sekund ---")

    print(f"\n=> Przetwarzanie instancji: {input_file}")

    jobs, n, s = read_instance(input_file)
    if not jobs:
        return 1

    # Pomiar czasu wykonania samego algorytmu
    algorithm_start_time = time.time()
    best_schedule = simulated_annealing(jobs, n, s, time_limit_per_instance)
    algorithm_end_time = time.time()

    execution_time = algorithm_end_time - algorithm_start_time

    final_tardiness = calculate_total_tardiness(best_schedule, jobs, s)

    print(f"   Czas wykonania algorytmu: {execution_time:.2f} sekund.")
    print(f"   Znalezione opóźnienie (zgodne z ewaluatorem): {final_tardiness}")

    write_solution(output_file_name, best_schedule, final_tardiness)
    print(f"   Wynik zapisano w pliku: {output_file_name}")

    print("\n--- Przetwarzanie zakończone. ---")
    return 0


if __name__ == "__main__":
    sys.exit(main())
