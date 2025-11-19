import random
import sys
import math
import copy

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
    """Oblicza całkowity koszt rozwiązania"""
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
    """Generuje sąsiada przez losową operację"""
    new_solution = solution.copy()
    operation = random.randint(0, 2)
    
    if operation == 0:  # Przenieś zadanie między maszynami
        # Wybierz niepustą maszynę źródłową
        non_empty = [i for i, m in enumerate(new_solution.machines) if len(m) > 0]
        if len(non_empty) < 2:
            return new_solution
        
        machine_from = random.choice(non_empty)
        machine_to = random.randint(0, len(new_solution.machines) - 1)
        
        if machine_from != machine_to and len(new_solution.machines[machine_from]) > 0:
            task_idx = random.randint(0, len(new_solution.machines[machine_from]) - 1)
            task = new_solution.machines[machine_from].pop(task_idx)
            insert_pos = random.randint(0, len(new_solution.machines[machine_to]))
            new_solution.machines[machine_to].insert(insert_pos, task)
    
    elif operation == 1:  # Zamień kolejność dwóch zadań na tej samej maszynie
        non_empty = [i for i, m in enumerate(new_solution.machines) if len(m) > 1]
        if not non_empty:
            return new_solution
        
        machine = random.choice(non_empty)
        if len(new_solution.machines[machine]) > 1:
            idx1, idx2 = random.sample(range(len(new_solution.machines[machine])), 2)
            new_solution.machines[machine][idx1], new_solution.machines[machine][idx2] = \
                new_solution.machines[machine][idx2], new_solution.machines[machine][idx1]
    
    else:  # Przenieś zadanie w obrębie tej samej maszyny
        non_empty = [i for i, m in enumerate(new_solution.machines) if len(m) > 1]
        if not non_empty:
            return new_solution
        
        machine = random.choice(non_empty)
        if len(new_solution.machines[machine]) > 1:
            idx_from = random.randint(0, len(new_solution.machines[machine]) - 1)
            idx_to = random.randint(0, len(new_solution.machines[machine]) - 1)
            task = new_solution.machines[machine].pop(idx_from)
            new_solution.machines[machine].insert(idx_to, task)
    
    new_solution.cost = calculate_cost(new_solution, tasks)
    return new_solution

def simulated_annealing(tasks, initial_temp=1000, cooling_rate=0.995, 
                       min_temp=0.1, max_iterations=50000):
    """Algorytm wyżarzania"""
    current = generate_initial_solution(tasks)
    best = current.copy()
    
    temperature = initial_temp
    iteration = 0
    
    while temperature > min_temp and iteration < max_iterations:
        neighbor = get_neighbor(current, tasks)
        delta = neighbor.cost - current.cost
        
        # Akceptuj rozwiązanie
        if delta < 0 or random.random() < math.exp(-delta / temperature):
            current = neighbor
            
            if current.cost < best.cost:
                best = current.copy()
                print(f"Iteracja {iteration}: Nowy najlepszy koszt = {best.cost}")
        
        temperature *= cooling_rate
        iteration += 1
        
        if iteration % 1000 == 0:
            print(f"Iteracja {iteration}, T={temperature:.2f}, Obecny={current.cost}, Najlepszy={best.cost}")
    
    return best

def save_output(solution, filename):
    """Zapisuje rozwiązanie do pliku"""
    with open(filename, 'w') as f:
        f.write(f"{int(solution.cost)}\n")
        for machine in solution.machines:
            f.write(" ".join(map(str, machine)) + "\n")

def main():
    if len(sys.argv) != 3:
        print("python main.py <input_file> <output_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    print("Wczytywanie danych...")
    tasks = read_input(input_file)
    print(f"Liczba zadań: {len(tasks)}")
    
    print("\nUruchamianie algorytmu wyżarzania...")
    best_solution = simulated_annealing(
        tasks,
        initial_temp=1000,
        cooling_rate=0.995,
        min_temp=0.1,
        max_iterations=50000
    )
    
    print(f"\nNajlepszy koszt: {best_solution.cost}")
    print("\nRozłożenie zadań na stanowiska:")
    for i, machine in enumerate(best_solution.machines, 1):
        print(f"Stanowisko {i}: {machine}")
    
    save_output(best_solution, output_file)
    print(f"\nWynik zapisano do {output_file}")

if __name__ == "__main__":
    main()
