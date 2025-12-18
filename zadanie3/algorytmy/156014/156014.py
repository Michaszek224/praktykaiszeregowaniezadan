import sys
import time
import os

class InstanceData:
    def __init__(self, n, jobs, setup_matrix):
        self.n = n
        # jobs_p[k] -> lista czasów [p1, p2, p3, p4] dla zadania o wewnętrznym indeksie k
        self.jobs_p = [j['p'] for j in jobs]
        self.jobs_r = [j['r'] for j in jobs]
        self.jobs_ids = [j['id'] for j in jobs] # Mapowanie index -> prawdziwe ID
        self.setup_matrix = setup_matrix

def read_instance(filepath):
    """Wczytuje instancję."""
    with open(filepath, 'r') as f:
        # Pomiń puste linie
        line = f.readline()
        while line and not line.strip():
            line = f.readline()
        
        n = int(line.strip())
        
        jobs = []
        for i in range(n):
            parts = [int(x) for x in f.readline().split()]
            job = {
                'id': i + 1,        
                'idx': i,           
                'p': parts[0:4],
                'r': parts[4],
                'total_p': sum(parts[0:4]) # Suma czasów do sortowania
            }
            jobs.append(job)
            
        setup_matrix = []
        for i in range(n):
            row = [int(x) for x in f.readline().split()]
            setup_matrix.append(row)
            
    return n, jobs, setup_matrix

def calculate_makespan_fast(sequence_indices, data):

    m_free = [0, 0, 0, 0]
    
    prev_idx = -1

    jobs_p = data.jobs_p
    jobs_r = data.jobs_r
    setup_matrix = data.setup_matrix
    
    for curr_idx in sequence_indices:
        # Setup time
        setup = 0
        if prev_idx != -1:
            setup = setup_matrix[prev_idx][curr_idx]
        
        # --- Maszyna 1 ---
        # Start = max(M1 wolna + setup, r_j)
        m1_ready = m_free[0] + setup
        r_j = jobs_r[curr_idx]
        
        start_m1 = m1_ready if m1_ready > r_j else r_j
        finish_m1 = start_m1 + jobs_p[curr_idx][0]
        m_free[0] = finish_m1
        
        # --- Maszyny 2, 3, 4 ---
        # Rozpisane ręcznie pętlą dla szybkości (unikanie range w gorącej ścieżce)
        
        # M2
        m2_ready = m_free[1] + setup
        # arrival z M1 to finish_m1 (które jest teraz w m_free[0])
        start_m2 = m2_ready if m2_ready > m_free[0] else m_free[0]
        m_free[1] = start_m2 + jobs_p[curr_idx][1]
        
        # M3
        m3_ready = m_free[2] + setup
        start_m3 = m3_ready if m3_ready > m_free[1] else m_free[1]
        m_free[2] = start_m3 + jobs_p[curr_idx][2]
        
        # M4
        m4_ready = m_free[3] + setup
        start_m4 = m4_ready if m4_ready > m_free[2] else m_free[2]
        m_free[3] = start_m4 + jobs_p[curr_idx][3]
        
        prev_idx = curr_idx

    return m_free[3]

def solve_neh(n, jobs, setup_matrix, time_limit):

    # Algorytm NEH:
    # 1. Posortuj zadania (wg sumy czasów operacji).
    # 2. Wstawiaj kolejne zadania w najlepsze możliwe miejsce w budowanej sekwencji.

    start_time = time.time()

    data = InstanceData(n, jobs, setup_matrix)
    
    sorted_jobs = sorted(jobs, key=lambda x: x['total_p'], reverse=True)
    
    # Lista indeksów zadań w aktualnym rozwiązaniu
    current_seq_indices = []
    
    for i, job in enumerate(sorted_jobs):
        job_idx = job['idx']
        
        # Jeśli to pierwsze zadanie, po prostu dodaj
        if not current_seq_indices:
            current_seq_indices.append(job_idx)
            continue
            
        # Sprawdź czas - jeśli kończy nam się czas,
        # przerywamy szukanie pozycji i po prostu dodajemy resztę na koniec.
        if time.time() - start_time > time_limit - 2.0:
            current_seq_indices.append(job_idx)
            continue

        # Szukamy najlepszej pozycji wstawienia (insertion)
        best_pos = -1
        min_cmax = float('inf')
        
        # Próbujemy wstawić zadanie 'job' na każdą pozycję od 0 do len(current)
        possible_positions = range(len(current_seq_indices) + 1)
        
        for pos in possible_positions:
            # Tworzymy kandydata sekwencji
            candidate_seq = current_seq_indices[:pos] + [job_idx] + current_seq_indices[pos:]
            
            cmax = calculate_makespan_fast(candidate_seq, data)
            
            if cmax < min_cmax:
                min_cmax = cmax
                best_pos = pos
        
        # Wstawiamy w najlepsze znalezione miejsce
        current_seq_indices.insert(best_pos, job_idx)
        
    # Konwersja indeksów wewnętrznych na ID zadań
    final_sequence_ids = [data.jobs_ids[idx] for idx in current_seq_indices]
    final_cmax = calculate_makespan_fast(current_seq_indices, data)
    
    return final_cmax, final_sequence_ids

def main():
    if len(sys.argv) < 3:
        print("Użycie: python neh_solver.py <plik_instancji> <plik_wynikowy> [limit_czasu]")
        return 
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    time_limit = 60.0
    if len(sys.argv) >= 4:
        try:
            time_limit = float(sys.argv[3])
        except:
            pass
        
    # 1. Wczytaj
    if not os.path.exists(input_path):
        print(f"Błąd: Nie znaleziono pliku {input_path}")
        return

    n, jobs, setup_matrix = read_instance(input_path)
    
    # 2. Rozwiąż algorytmem NEH
    cmax, sequence = solve_neh(n, jobs, setup_matrix, time_limit)
    
    # 3. Zapisz
    with open(output_path, 'w') as f:
        f.write(f"{cmax}\n")
        f.write(" ".join(map(str, sequence)) + "\n")
    
    # print(f"Zakończono dla {input_path}. Cmax: {cmax}")

if __name__ == "__main__":
    main()