import sys
import os
import random
import math
import time

start = time.time()

def wczytaj_instancje(sciezka_pliku):

    if not os.path.isfile(sciezka_pliku):
        print(f"Błąd: Nie znaleziono pliku {sciezka_pliku}")
        return None, None, None

    try:
        with open(sciezka_pliku, "r") as f:
            l = f.readline()
            while l and not l.strip(): l = f.readline()
            if not l: return None, None, None
            n = int(l.strip())

            zadania = {}
            for i in range(1, n + 1):
                l = f.readline()
                parts = list(map(int, l.split()))

                p_times = parts[0:4]
                r_j = parts[4]
                zadania[i] = (p_times, r_j)


            macierz_S = []
            for _ in range(n):
                l = f.readline()
                while l and not l.strip(): l = f.readline()
                row = list(map(int, l.split()))
                macierz_S.append(row)

        return n, zadania, macierz_S

    except Exception as e:
        print(f"Błąd odczytu instancji: {e}")
        return None, None, None


def zapisz_wynik(sciezka_wyjsciowa, cmax, sekwencja):
    with open(sciezka_wyjsciowa, "w") as f:
        f.write(f"{cmax}\n")
        f.write(" ".join(map(str, sekwencja)) + "\n")


def oblicz_cmax(n, zadania, macierz_S, sekwencja):

    machines_free = [0, 0, 0, 0]
    prev_job = None

    for zad_id in sekwencja:
        p_times, r_j = zadania[zad_id]


        setup = 0
        if prev_job is not None:

            setup = macierz_S[prev_job - 1][zad_id - 1]


        m1_ready = machines_free[0] + setup
        start_m1 = max(m1_ready, r_j)
        end_m1 = start_m1 + p_times[0]
        machines_free[0] = end_m1


        m2_ready = machines_free[1] + setup
        start_m2 = max(m2_ready, end_m1)
        end_m2 = start_m2 + p_times[1]
        machines_free[1] = end_m2


        m3_ready = machines_free[2] + setup
        start_m3 = max(m3_ready, end_m2)
        end_m3 = start_m3 + p_times[2]
        machines_free[2] = end_m3


        m4_ready = machines_free[3] + setup
        start_m4 = max(m4_ready, end_m3)
        end_m4 = start_m4 + p_times[3]
        machines_free[3] = end_m4

        prev_job = zad_id


    return machines_free[3]


def rozwiaz(n, zadania, macierz_S, limit_czasu):
    start_time = time.time()


    obecna_sekwencja = sorted(zadania.keys(), key=lambda k: zadania[k][1])
    obecny_cmax = oblicz_cmax(n, zadania, macierz_S, obecna_sekwencja)

    najlepsza_sekwencja = list(obecna_sekwencja)
    najlepszy_cmax = obecny_cmax

    T = 1000.0
    T_min = 0.001
    alpha = 0.99

    iteracja = 0


    while True:

        if iteracja % 100 == 0: #100
            elapsed = time.time() - start_time

            if elapsed >= limit_czasu - 0.1: #0.05
                break



        if T <= T_min:
            T = 1000.0

        nowa_sekwencja = list(obecna_sekwencja)
        i, j = random.sample(range(n), 2)

        if random.random() < 0.5:
            # Swap
            nowa_sekwencja[i], nowa_sekwencja[j] = nowa_sekwencja[j], nowa_sekwencja[i]
        else:
            # Insert
            el = nowa_sekwencja.pop(i)
            nowa_sekwencja.insert(j, el)

        nowy_cmax = oblicz_cmax(n, zadania, macierz_S, nowa_sekwencja)
        delta = nowy_cmax - obecny_cmax


        if delta < 0 or random.random() < math.exp(-delta / T):
            obecna_sekwencja = nowa_sekwencja
            obecny_cmax = nowy_cmax

            if obecny_cmax < najlepszy_cmax:
                najlepszy_cmax = obecny_cmax
                najlepsza_sekwencja = list(obecna_sekwencja)

        T *= alpha
        iteracja += 1

    return najlepszy_cmax, najlepsza_sekwencja


def main():
    if len(sys.argv) < 4:
        print("Użycie: python3 151893.py <plik_instancji> <plik_wynikowy> <limit_czasu>")
        sys.exit(1)

    plik_in = sys.argv[1]
    plik_out = sys.argv[2]

    try:
        limit_czasu = float(sys.argv[3])
    except ValueError:
        print("Błąd: Limit czasu musi być liczbą (sekundy).")
        sys.exit(1)


    n, zadania, macierz_S = wczytaj_instancje(plik_in)
    if n is None:
        sys.exit(1)


    cmax, sekwencja = rozwiaz(n, zadania, macierz_S, limit_czasu)


    zapisz_wynik(plik_out, cmax, sekwencja)


if __name__ == "__main__":
    main()
    print(time.time()-start)