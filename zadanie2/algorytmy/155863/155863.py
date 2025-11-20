import random
import sys
import math
import time

class Task:
    def __init__(self, id, p, r, w):
        self.id = id
        self.p = p  # czas przetwarzania
        self.r = r  # data gotowości
        self.w = w  # waga (koszt)

class Solution:
    def __init__(self, machines=4):
        self.machines = [[] for _ in range(machines)]
        self.cost = float('inf')
    
    def copy(self):
        new_sol = Solution(len(self.machines))
        new_sol.machines = [m[:] for m in self.machines]
        new_sol.cost = self.cost
        return new_sol

def read_input(filename):
    tasks = []
    with open(filename, 'r') as f:
        n = int(f.readline().strip())
        for i in range(n):
            line = f.readline().strip().split()
            p, r, w = int(line[0]), int(line[1]), int(line[2])
            tasks.append(Task(i+1, p, r, w))
    return tasks

def calculate_cost(solution, tasks):
    total_cost = 0
    task_dict = {t.id: t for t in tasks}
    
    for machine in solution.machines:
        current_time = 0
        for task_id in machine:
            task = task_dict[task_id]
            # Rozpoczęcie nie wcześniej niż r_j
            start_time = max(current_time, task.r)
            completion_time = start_time + task.p
            flow_time = completion_time - task.r
            total_cost += task.w * flow_time
            current_time = completion_time
    
    return total_cost

def generate_initial_solution(tasks, num_machines=4):
    """Generuje rozwiązanie początkowe - sortowanie po r_j, potem SPT"""
    solution = Solution(num_machines)
    
    # Sortuj zadania po dacie gotowości, potem po czasie przetwarzania
    sorted_tasks = sorted(tasks, key=lambda t: (t.r, t.p))
    
    # Przypisuj zadania do maszyn według strategii LPT (Longest Processing Time)
    machine_loads = [0] * num_machines
    
    for task in sorted_tasks:
        # Znajdź maszynę z najmniejszym obciążeniem
        min_machine = min(range(num_machines), key=lambda i: machine_loads[i])
        solution.machines[min_machine].append(task.id)
        machine_loads[min_machine] += task.p
    
    solution.cost = calculate_cost(solution, tasks)
    return solution

def get_neighbor(solution, tasks):
    new_solution = solution.copy()

    # -- Przygotuj pomocnicze dane --
    task_dict = {t.id: t for t in tasks}

    # Obciążenie każdej maszyny
    machine_loads = []
    for m in new_solution.machines:
        load = sum(task_dict[tid].p for tid in m)
        machine_loads.append(load)

    # Wybór ruchu z priorytetami:
    # 0 = swap między zadaniami na tej samej maszynie (35%)
    # 1 = swap między maszynami (40%)
    # 2 = przeniesienie zadania (25%)
    r = random.random()

    # 1. SWAP NA TEJ SAMEJ MASZYNIE (35%)
    if r < 0.35:
        candidates = [i for i, m in enumerate(new_solution.machines) if len(m) > 1]
        if candidates:
            machine = random.choice(candidates)
            m = new_solution.machines[machine]

            # swap dwóch losowych zadań
            i, j = random.sample(range(len(m)), 2)
            m[i], m[j] = m[j], m[i]

        new_solution.cost = calculate_cost(new_solution, tasks)
        return new_solution

    # 2. SWAP MIĘDZY MASZYNAMI (40%)
    elif r < 0.75:
        # wybierz 2 różne niepuste maszyny
        candidates = [i for i, m in enumerate(new_solution.machines) if len(m) > 0]
        if len(candidates) >= 2:
            m1, m2 = random.sample(candidates, 2)
            L1 = new_solution.machines[m1]
            L2 = new_solution.machines[m2]

            # swap pojedynczych zadań
            idx1 = random.randrange(len(L1))
            idx2 = random.randrange(len(L2))

            L1[idx1], L2[idx2] = L2[idx2], L1[idx1]

        new_solution.cost = calculate_cost(new_solution, tasks)
        return new_solution

    # 3. PRZENIESIENIE ZADANIA (25%)
    else:
        # wybierz maszynę proporcjonalnie do obciążenia
        # → bardziej obciążone maszyny są częściej wybierane
        if sum(machine_loads) > 0:
            m_from = random.choices(
                range(len(new_solution.machines)),
                weights=machine_loads
            )[0]
        else:
            # fallback
            non_empty = [i for i, m in enumerate(new_solution.machines) if len(m) > 0]
            if not non_empty:
                return new_solution
            m_from = random.choice(non_empty)

        if len(new_solution.machines[m_from]) == 0:
            return new_solution

        # losowe zadanie do przeniesienia
        idx = random.randrange(len(new_solution.machines[m_from]))
        task = new_solution.machines[m_from].pop(idx)

        # wybierz inną maszynę
        machines_idx = list(range(len(new_solution.machines)))
        machines_idx.remove(m_from)
        m_to = random.choice(machines_idx)

        # wstaw zadanie w losowe miejsce
        insert_pos = random.randint(0, len(new_solution.machines[m_to]))
        new_solution.machines[m_to].insert(insert_pos, task)

        new_solution.cost = calculate_cost(new_solution, tasks)
        return new_solution

def simulated_annealing(tasks, time_limit, initial_temp=1000, cooling_rate=0.9999, min_temp=0.01):
    start_time = time.time()

    current = generate_initial_solution(tasks)
    best = current.copy()
    temperature = initial_temp

    while time.time() - start_time < time_limit:
        neighbor = get_neighbor(current, tasks)
        delta = neighbor.cost - current.cost
        
        if delta < 0 or random.random() < math.exp(-delta / temperature):
            current = neighbor

            if current.cost < best.cost:
                best = current.copy()

        temperature *= cooling_rate
        if temperature < min_temp:
            temperature = initial_temp  # restart SA (tzw. reheating)

    return best
def save_output(solution, filename):
    with open(filename, 'w') as f:
        f.write(f"{int(solution.cost)}\n")
        for machine in solution.machines:
            f.write(" ".join(map(str, machine)) + "\n")

def main():
    if len(sys.argv) != 4:
        print("python main.py <input_file> <output_file> <time_limit>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    time_limit = float(sys.argv[3])
    
    #print("Wczytywanie danych...")
    tasks = read_input(input_file)
    #print(f"Liczba zadań: {len(tasks)}")
    
    #print("\nUruchamianie algorytmu wyżarzania...")
    best_solution = simulated_annealing(
        tasks,
        time_limit -1,
        initial_temp=1000,
        cooling_rate=0.995,
        min_temp=0.1
    )
    
    #print(f"\nNajlepszy koszt: {best_solution.cost}")
    #print("\nRozłożenie zadań na stanowiska:")
    #for i, machine in enumerate(best_solution.machines, 1):
        #print(f"Stanowisko {i}: {machine}")
    
    save_output(best_solution, output_file)
    #print(f"\nWynik zapisano do {output_file}")

if __name__ == "__main__":
    main()
