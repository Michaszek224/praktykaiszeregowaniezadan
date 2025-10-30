import os
import sys
import time
import random

class Task:
    def __init__(self,taskid, p_time, d_time):
        self.taskid = taskid
        self.p_time = p_time
        self.d_time = d_time

class InputFile:    
    def read(self, filename):
        self.tasks = []
        with open(filename, "r", encoding="utf-8") as plik:
            lines = plik.readlines()
            
            if len(lines) > 0:
                parts = lines[0].strip().split()
                if len(parts) >= 2:
                    self.n = int(parts[0])
                    self.s = int(parts[1])

            taskid = 1
            for i in range(1, len(lines)):
                line = lines[i].strip()
                if line:
                    task = [int(num) for num in line.split()]
                    self.tasks.append(Task(taskid, task[0], task[1]))
                taskid+=1


    @staticmethod
    def write(instance):
        filename = f"in_155888_{instance.n}.txt"
        
        if os.path.exists(filename):
            os.remove(filename)
        
        with open(filename, "w", encoding="utf-8") as plik:
            plik.write(f"{str(instance.n)}\n")
            plik.write(f"{str(instance.s)}\n")
            for i, task in enumerate(instance.tasks):
                if i == len(instance.tasks) - 1:
                    plik.write(f"{task.p_time} {task.d_time}")
                else:
                    plik.write(f"{task.p_time} {task.d_time}\n")
            
class OutputFile:
    def __init__(self):
        self.criterium = None
        self.k = None
        self.batches = []
        self.zero_error = False

    def read(self, filename):
        with open(filename, "r", encoding="utf-8") as plik:
            lines = plik.readlines()
            
            if len(lines) > 0:
                self.criterium = int(lines[0].strip())
            
            if len(lines) > 1:
                self.k = int(lines[1].strip())
            
            for i in range(2, len(lines)):
                line = lines[i].strip() 
                if line:
                    numbers = [int(num) for num in line.split()]  

                    if 0 in numbers:
                        self.zero_error = True
                    else:
                        self.batches.append(numbers)
                

def calc_criterium_with_setup(sequence, inputfile):
    setup = inputfile.s
    total_d = 0
    total_time = 0
    
    valid_sequence = [batch for batch in sequence if batch]
    
    for batch in valid_sequence:
        batch_time = 0
        for task_id in batch:
            task_info = next((t for t in inputfile.tasks if t.taskid == task_id), None)
            if task_info:
                batch_time += task_info.p_time
                
        total_time += batch_time
        for task_id in batch:
            task_info = next((t for t in inputfile.tasks if t.taskid == task_id), None)
            if task_info:
                temp_d = max(0, total_time - task_info.d_time)
                total_d += temp_d
        
        total_time += setup

    return total_d


def decide_task(tsk, curr_batch, sequence, setup):
    def suma_p(batch):
        return sum(task.p_time for task in batch)
    
    def koszt(batch_list, aktualny_batch):
        czas = 0
        total_delay = 0
        
        temp_list = [b for b in batch_list if b]
        for idx, B in enumerate(temp_list):
            if idx > 0:
                czas += setup
            czas += suma_p(B)
            for j in B:
                total_delay += max(0, czas - j.d_time)
        
        if aktualny_batch:
            if temp_list:
                czas += setup
            czas += suma_p(aktualny_batch)
            for j in aktualny_batch:
                total_delay += max(0, czas - j.d_time)
        return total_delay

    temp_batch_A = curr_batch + [tsk]
    koszt_A = koszt(sequence, temp_batch_A)
    
    if curr_batch:
        koszt_B = koszt(sequence + [curr_batch], [tsk])
    else:
        koszt_B = koszt(sequence, [tsk])
    
    return koszt_A <= koszt_B


def generate_solution(inputfile):
    sorted_tasks = sorted(inputfile.tasks, key=lambda x: x.d_time)
    setup = inputfile.s
    sequence = []
    curr_batch = []
    for tsk in sorted_tasks:
        if decide_task(tsk, curr_batch, sequence, setup) == True:
            curr_batch.append(tsk)
        else:
            if curr_batch:
                sequence.append(curr_batch)
            curr_batch = [tsk]

    if curr_batch:
        sequence.append(curr_batch)

    res_sequence = [[t.taskid for t in btc]for btc in sequence]
    return res_sequence


def generate_output_file(batches, crit, output_path):
    final_batches = [batch for batch in batches if batch]
    num_batches = len(final_batches)
    filename = output_path
    
    with open(filename, 'w', encoding='utf-8') as plik:
        plik.write(str(crit) + '\n')
        plik.write(str(num_batches) + '\n')
        linie = [' '.join(map(str, podlista)) for podlista in final_batches]
        plik.write('\n'.join(linie))


def generate_neighbor_swap_tasks(current_solution):
    neighbor = [list(batch) for batch in current_solution if batch]
    
    if len(neighbor) == 0:
        return None

    b1_idx = random.randrange(len(neighbor))
    if not neighbor[b1_idx]:
         return None
    t1_idx = random.randrange(len(neighbor[b1_idx]))

    b2_idx = random.randrange(len(neighbor))
    if not neighbor[b2_idx]:
        return None
    t2_idx = random.randrange(len(neighbor[b2_idx]))

    task1 = neighbor[b1_idx][t1_idx]
    task2 = neighbor[b2_idx][t2_idx]
    
    neighbor[b1_idx][t1_idx] = task2
    neighbor[b2_idx][t2_idx] = task1
    
    return neighbor
        

def generate_neighbor_move_task(current_solution):
    neighbor = [list(batch) for batch in current_solution if batch]
    
    if not neighbor:
        return None 

    b1_idx = random.randrange(len(neighbor))
    if not neighbor[b1_idx]:
        return None
    t1_idx = random.randrange(len(neighbor[b1_idx]))
    
    task_to_move = neighbor[b1_idx].pop(t1_idx)
    
    if not neighbor[b1_idx]:
        neighbor.pop(b1_idx)

    b2_idx = random.randrange(len(neighbor) + 1) 
    
    if b2_idx == len(neighbor):
        neighbor.append([task_to_move])
    else:
        neighbor[b2_idx].append(task_to_move)
    
    return neighbor
        

def generate_neighbor_swap_batches(current_solution):
    neighbor = [list(batch) for batch in current_solution if batch]
    
    if len(neighbor) < 2:
        return None

    b1_idx = random.randrange(len(neighbor))
    b2_idx = random.randrange(len(neighbor))
    
    if len(neighbor) > 1:
        while b1_idx == b2_idx:
            b2_idx = random.randrange(len(neighbor))
        
    neighbor[b1_idx], neighbor[b2_idx] = neighbor[b2_idx], neighbor[b1_idx]
    
    return neighbor
        

def generate_neighbor_merge_batches(current_solution):
    neighbor = [list(batch) for batch in current_solution if batch]
    
    if len(neighbor) < 2:
        return None

    b1_idx = random.randrange(len(neighbor) - 1)
    b2_idx = b1_idx + 1
    
    batch_to_move_and_remove = neighbor.pop(b2_idx)
    neighbor[b1_idx].extend(batch_to_move_and_remove)
    
    return neighbor
        

def generate_neighbor_split_batch(current_solution):
    neighbor = [list(batch) for batch in current_solution if batch]
    
    if not neighbor:
        return None

    splittable_batches_indices = [i for i, b in enumerate(neighbor) if len(b) > 1]
    
    if not splittable_batches_indices:
        return None

    b_idx = random.choice(splittable_batches_indices)
    batch_to_split = neighbor[b_idx]
    
    split_point = random.randint(1, len(batch_to_split) - 1)
    
    batch_part1 = batch_to_split[:split_point]
    batch_part2 = batch_to_split[split_point:]
    
    neighbor[b_idx] = batch_part1
    neighbor.insert(b_idx + 1, batch_part2)
    
    return neighbor
        

def main():
    if len(sys.argv) != 4:
        print("Użycie algorytmu: python 155888.py <plik_instancji.txt> <plik_wynikowy.txt> <limit_czasu>")
        sys.exit(1)

    instance_file = str(sys.argv[1])
    output_path = str(sys.argv[2])
    time_limit = float(sys.argv[3]) - 0.1
    
    start_time = time.perf_counter() 

    input_file = InputFile()
    input_file.read(instance_file)

    solution = generate_solution(input_file)
    total_crit = calc_criterium_with_setup(solution, input_file)

    best_solution = solution
    best_crit = total_crit
    
    current_solution = solution
    current_crit = total_crit

    iteration = 0
    last_improvement_iter = 0
    STAGNATION_KICK_ITER = 30000

    while (time.perf_counter() - start_time) < time_limit:
        iteration += 1

        if iteration - last_improvement_iter > STAGNATION_KICK_ITER:
            kicked_solution = [list(b) for b in current_solution if b]
            num_batches = len(kicked_solution)
            if num_batches >= 2:
                for _ in range(min(3, num_batches // 2)):
                    b1_idx = random.randrange(num_batches)
                    b2_idx = random.randrange(num_batches)
                    if b1_idx == b2_idx: continue
                    kicked_solution[b1_idx], kicked_solution[b2_idx] = kicked_solution[b2_idx], kicked_solution[b1_idx]
            
            current_solution = kicked_solution
            current_crit = calc_criterium_with_setup(current_solution, input_file)
            last_improvement_iter = iteration

        move_type = random.random()
        
        if move_type < 0.25:
            neighbor_solution = generate_neighbor_swap_tasks(current_solution)
        elif move_type < 0.60:
            neighbor_solution = generate_neighbor_move_task(current_solution)
        elif move_type < 0.75:
            neighbor_solution = generate_neighbor_swap_batches(current_solution)
        elif move_type < 0.875:
            neighbor_solution = generate_neighbor_merge_batches(current_solution)
        else:
            neighbor_solution = generate_neighbor_split_batch(current_solution)


        if not neighbor_solution:
            continue

        neighbor_crit = calc_criterium_with_setup(neighbor_solution, input_file)

        delta_crit = neighbor_crit - current_crit

        time_elapsed = time.perf_counter() - start_time
        time_ratio = min(1.0, time_elapsed / time_limit)
        acceptance_prob = 0.1 * (1.0 - time_ratio) 

        if delta_crit <= 0 or random.random() < acceptance_prob:
            current_solution = neighbor_solution
            current_crit = neighbor_crit
            
            if current_crit < best_crit:
                best_solution = current_solution
                best_crit = current_crit
                last_improvement_iter = iteration
        
    generate_output_file(best_solution, best_crit, output_path)

    end_time_total = time.perf_counter() - start_time
    end_time_total = round(end_time_total, 4)

    print(f"Wynik zapisano do {output_path}")
    print(f"Najlepsze znalezione opóźnienie = {best_crit}")
    print(f"Czas dzialania programu: {end_time_total}s")


if __name__ == "__main__":
    main()