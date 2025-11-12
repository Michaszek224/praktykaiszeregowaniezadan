import sys
import os
import random

n_size = [50, 100, 150,200,250, 300, 350, 400, 450, 500]
przedzial_wag_dol = 101
przedzial_wag_gora = 200

args = sys.argv

if len(args) != 2:
    print("Usage: python generator.py <outout_dir>")
    sys.exit(1)

output_file = args[1]

for n in n_size:
    if not os.path.exists(output_file):
        os.makedirs(output_file)
    with open(f"{output_file}/in_155863_{n}.txt", "w") as f:
        f.write(f"{n}\n")
        for i in range(n):
            waga = random.randint(przedzial_wag_dol, przedzial_wag_gora)
            czas_naprawy = random.randint(n//10, n)
            czas_oddania = random.randint(0, n*n//5)
            f.write(f"{czas_naprawy} {czas_oddania} {waga}\n")
