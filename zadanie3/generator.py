import sys
import os
import random

n_sizes = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500]

p_min, p_max = 1, 200
r_min, r_max = 0, 2000

s_min, s_max = 0, 50

args = sys.argv

if len(args) != 2:
    print("Usage: python generator.py <output_dir>")
    sys.exit(1)

output_dir = args[1]

for n in n_sizes:
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_path = f"{output_dir}/in_155863_{n}.txt"

    with open(file_path, "w") as f:
        f.write(f"{n}\n")

        for j in range(n):
            p1 = random.randint(p_min, p_max)
            p2 = random.randint(p_min, p_max)
            p3 = random.randint(p_min, p_max)
            p4 = random.randint(p_min, p_max)
            rj = random.randint(r_min, r_max)
            f.write(f"{p1} {p2} {p3} {p4} {rj}\n")

        # macierz Sij
        for i in range(n):
            row = []
            for j in range(n):
                if i == j:
                    row.append(0)
                else:
                    row.append(random.randint(s_min, s_max))
            f.write(" ".join(map(str, row)) + "\n")

print("Instancje wygenerowane!")
