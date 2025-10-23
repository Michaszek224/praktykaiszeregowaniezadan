import os
import sys
import time

class Task:
    def __init__(self,taskid, p_time, d_time):
        self.taskid = taskid
        self.p_time = p_time         # processing time
        self.d_time = d_time         # due time of task


class InputFile:    
    def read(self, filename):
        self.tasks = []
        with open(filename, "r", encoding="utf-8") as plik:
            lines = plik.readlines()
            
            if len(lines) > 0:  # odczytaj n i s z jednej linii
                parts = lines[0].strip().split()
                if len(parts) >= 2:
                    self.n = int(parts[0])
                    self.s = int(parts[1])

            taskid = 1
            for i in range(1, len(lines)):      # read all tasks from other lines
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
        self.criterium = None       # criterium value read from file
        self.k = None               # number of batches
        self.batches = []           # list of batches
        self.zero_error = False

    def read(self, filename):
        with open(filename, "r", encoding="utf-8") as plik:
            lines = plik.readlines()
            
            if len(lines) > 0:                  # read criterium value from file
                self.criterium = int(lines[0].strip())
            
            if len(lines) > 1:                  # read k value from file
                self.k = int(lines[1].strip())
            
            for i in range(2, len(lines)):      # read all batches from other lines
                line = lines[i].strip() 
                if line:
                    numbers = [int(num) for num in line.split()]  

                    if 0 in numbers:            # check if task 0 appeared in output files
                        self.zero_error = True
                    else:
                        self.batches.append(numbers)
                

def calc_criterium_with_setup(sequence, inputfile):           # passed sequence form:  [[2, 4],  [1, 5, 6], [7],  [3]]
    setup = inputfile.s
    total_d = 0
    total_time = 0
    for batch in sequence:
        batch_time = 0
        for task in batch:
            task_info = next((t for t in inputfile.tasks if t.taskid == task), None)
            batch_time+=task_info.p_time
        total_time+=batch_time
        for task in batch:
            task_info = next((t for t in inputfile.tasks if t.taskid == task), None)
            temp_d = max(0, total_time - task_info.d_time)
            total_d+=temp_d
        total_time+=setup

    return total_d


def decide_task(tsk, curr_batch, sequence, setup):
    def suma_p(batch):
        return sum(task.p_time for task in batch)
    
    def koszt(batch_list, aktualny_batch):
        czas = 0
        total_delay = 0
        for idx, B in enumerate(batch_list):
            if idx > 0:
                czas += setup
            czas += suma_p(B)
            for j in B:
                total_delay += max(0, czas - j.d_time)
        if aktualny_batch:
            if batch_list:
                czas += setup
            czas += suma_p(aktualny_batch)
            for j in aktualny_batch:
                total_delay += max(0, czas - j.d_time)
        return total_delay

    # Scenariusz A: dodanie zadania do bieżącego batcha
    temp_batch = curr_batch + [tsk]
    koszt_A = koszt(sequence, temp_batch)
    
    # Scenariusz B: rozpoczęcie nowego batcha
    if curr_batch:
        koszt_B = koszt(sequence + [curr_batch], [tsk])
    else:
        koszt_B = koszt(sequence, [tsk])
    
    # Decyzja
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
    num_batches = len(batches)
    filename = output_path
    with open(filename, 'w', encoding='utf-8') as plik:
        plik.write(str(crit) + '\n')
        plik.write(str(num_batches) + '\n')
        linie = [' '.join(map(str, podlista)) for podlista in batches]
        plik.write('\n'.join(linie))
    print(f"output file {filename} has been generated!")


def main():
    if len(sys.argv) != 4:
        print("Użycie algorytmu: python 155888.py <plik_instancji.txt> <plik_wynikowy.txt> <limit_czasu>")
        sys.exit(1)

    instance_file = str(sys.argv[1])
    output_path = str(sys.argv[2])
    time_limit = float(sys.argv[3])

    count_time = time.time()

    start_time = time.perf_counter()
    input_file = InputFile()
    input_file.read(instance_file)

    solution = generate_solution(input_file)


    total_crit = calc_criterium_with_setup(solution,input_file)
    generate_output_file(solution, total_crit, output_path )

    if time.perf_counter() - start_time > time_limit:
        print("Przekroczono limit czasu podczas obliczen")
        sys.exit(1)

    end_time = time.time() - count_time
    end_time = round(end_time, 4)

    print(f"Wynik zapisano do {output_path}")
    print(f"Łączne opóźnienie = {total_crit}")
    print(f"Czas dzialania programu: {end_time}")

if __name__ == "__main__":
    main()