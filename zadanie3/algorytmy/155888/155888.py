import sys
import os
import time
import random
from dataclasses import dataclass

NUM_MACHINES = 4

@dataclass
class Job:
    job_id: int
    m1_time: int
    m2_time: int
    m3_time: int
    m4_time: int
    r_time: int

class InputFile:    
    def read(self, filename):
        self.tasks = []
        self.rearm_matrice = []
        with open(filename, "r", encoding="utf-8") as plik:
            lines = plik.readlines()
            
            if len(lines) > 0: 
                self.n = lines[0]

            taskid = 1
            for i in range(1, int(self.n)+1):      
                line = lines[i].strip()
                if line:
                    task = [int(num) for num in line.split()]
                    self.tasks.append(Job(taskid, task[0], task[1], task[2], task[3], task[4]))
                taskid+=1

            matrice = lines[int(self.n)+1:]
            for m in matrice:
                mspl = m.split()
                self.rearm_matrice.append([int(element) for element in mspl])



def calculate_cost(inputfile, sequence):

        end_m1 = 0
        end_m2 = 0
        end_m3 = 0
        end_m4 = 0
        
        previous_job_idx = None
        for job_id in sequence:
            current_job_idx = job_id - 1
            job = inputfile.tasks[current_job_idx]
            setup_time = 0
            if previous_job_idx is not None:
                setup_time = inputfile.rearm_matrice[previous_job_idx][current_job_idx]
            start_m1 = max(job.r_time, end_m1 + setup_time)
            end_m1 = start_m1 + job.m1_time
            start_m2 = max(end_m1, end_m2 + setup_time)
            end_m2 = start_m2 + job.m2_time
            start_m3 = max(end_m2, end_m3 + setup_time)
            end_m3 = start_m3 + job.m3_time
            start_m4 = max(end_m3, end_m4 + setup_time)
            end_m4 = start_m4 + job.m4_time
            
            previous_job_idx = current_job_idx
            
        calculated_cmax = end_m4
        
        return calculated_cmax

def generate_permutation(n):
    lista_uporzadkowana = list(range(1, n + 1))
    random.shuffle(lista_uporzadkowana)
    return lista_uporzadkowana

def loop(inputfile, timelimit, n):
    start = time.time()
    best_sol = list(range(1, n + 1))
    best_crit = calculate_cost(inputfile, best_sol)
    while (time.time() - start < timelimit - 1):
        new_seq = generate_permutation(n)
        new_crit = calculate_cost(inputfile, new_seq)
        if new_crit < best_crit:
            best_sol = new_seq
            best_crit = new_crit
    return best_sol, best_crit

def generateoutput(best_sol, best_crit, filename):
    solstr = " ".join(map(str, best_sol))
    try:
        with open(filename, 'w') as plik:

            plik.write(str(best_crit) + '\n')
            plik.write(solstr) 
        
        print(f"Pomyślnie zapisano dane do pliku '{filename}'.")

    except IOError as e:
        print(f"Wystąpił błąd podczas zapisu pliku: {e}")


def main():
    
    if len(sys.argv) != 4:
        print("Użycie: python scheduler.py <plik_wejsciowy> <plik_wyjsciowy> <limit_czasowy_w_sekundach>")
        print("Przykład: python scheduler.py in_100.txt out_100.txt 10")
        sys.exit(1)
        
    input_file = sys.argv[1]
    inp = InputFile()
    inp.read(input_file)

    output_file = sys.argv[2]
    
    try:
        time_limit = float(sys.argv[3])
        if time_limit <= 0:
            raise ValueError("Limit czasowy musi być dodatni.")
    except ValueError as e:
        print(f"Błąd argumentu: Nieprawidłowy limit czasowy. {e}")
        sys.exit(1)
    

    sol, crit = loop(inp, time_limit, int(inp.n))
    generateoutput(sol, crit, output_file)        

if __name__ == "__main__":
    main()