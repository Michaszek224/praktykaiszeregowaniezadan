import sys
import time
import os


def wczytaj_instancje(plik):
    if not os.path.exists(plik):
        return None, None, None

    try:
        with open(plik, 'r') as f:
            lines = f.read().split()

        iter_lines = iter(lines)
        try:
            n = int(next(iter_lines))
        except StopIteration:
            return None, None, None

        zadania = {}
        for i in range(1, n + 1):
            p1 = int(next(iter_lines))
            p2 = int(next(iter_lines))
            p3 = int(next(iter_lines))
            p4 = int(next(iter_lines))
            r = int(next(iter_lines))
            zadania[i] = {'p': [p1, p2, p3, p4], 'r': r}

        matrix_s = []
        for _ in range(n):
            row = []
            for _ in range(n):
                row.append(int(next(iter_lines)))
            matrix_s.append(row)

        return n, zadania, matrix_s

    except Exception:
        return None, None, None


def zapisz_rozwiazanie(plik, cmax, kolejnosc):
    try:
        with open(plik, 'w') as f:
            f.write(f"{cmax}\n")
            f.write(" ".join(map(str, kolejnosc)) + "\n")
    except IOError as e:
        print(f"Błąd zapisu: {e}")


def oblicz_cmax(n, zadania, matrix_s, kolejnosc):

    czas_wolny_maszyn = [0, 0, 0, 0]
    poprzednie_zadanie_idx = None

    for zad_id in kolejnosc:
        obecne_zadanie_idx = zad_id - 1
        p = zadania[zad_id]['p']
        r = zadania[zad_id]['r']

        setup = 0
        if poprzednie_zadanie_idx is not None:
            setup = matrix_s[poprzednie_zadanie_idx][obecne_zadanie_idx]

        koniec_na_poprzedniej = 0

        for k in range(4):
            dostepnosc_maszyny = czas_wolny_maszyn[k] + setup

            if k == 0:
                start = max(dostepnosc_maszyny, r)
            else:
                start = max(dostepnosc_maszyny, koniec_na_poprzedniej)

            koniec = start + p[k]

            czas_wolny_maszyn[k] = koniec
            koniec_na_poprzedniej = koniec

        poprzednie_zadanie_idx = obecne_zadanie_idx

    return czas_wolny_maszyn[3]


def rozwiazanie_startowe_rj(n, zadania):

    lista_zadan = list(range(1, n + 1))

    lista_zadan.sort(key=lambda id_z: zadania[id_z]['r'])
    return lista_zadan


def deterministyczna_poprawa(n, zadania, matrix_s, kolejnosc_startowa, limit_czasu):

    start_time = time.perf_counter()

    najlepsza_kolejnosc = kolejnosc_startowa[:]
    najlepsze_cmax = oblicz_cmax(n, zadania, matrix_s, najlepsza_kolejnosc)

    ulepszono_cos = True

    while ulepszono_cos:
        ulepszono_cos = False

        if (time.perf_counter() - start_time) > (limit_czasu - 0.5):
            break

        for idx_zrodlo in range(n):

            if (time.perf_counter() - start_time) > limit_czasu:
                break

            obecna_kolejnosc = najlepsza_kolejnosc[:]
            zadanie = obecna_kolejnosc.pop(idx_zrodlo)

            znaleziono_lepsze = False

            for idx_cel in range(n):
                if idx_cel == idx_zrodlo:
                    continue

                obecna_kolejnosc.insert(idx_cel, zadanie)

                nowe_cmax = oblicz_cmax(n, zadania, matrix_s, obecna_kolejnosc)

                if nowe_cmax < najlepsze_cmax:
                    najlepsze_cmax = nowe_cmax
                    najlepsza_kolejnosc = obecna_kolejnosc[:]
                    ulepszono_cos = True
                    znaleziono_lepsze = True
                    break
                obecna_kolejnosc.pop(idx_cel)

            if znaleziono_lepsze:
                break

    return najlepsze_cmax, najlepsza_kolejnosc


def main():
    if len(sys.argv) < 4:
        print("Użycie: python algorytm.py <instancja> <wyjscie> <limit_czasu>")
        sys.exit(1)

    start_programu = time.perf_counter()

    plik_inst = sys.argv[1]
    plik_rozw = sys.argv[2]
    limit_input = float(sys.argv[3])

    limit_czasu = max(0.1, limit_input - 1.0)

    n, zadania, matrix_s = wczytaj_instancje(plik_inst)
    if n is None:
        sys.exit(1)

    kolejnosc_start = rozwiazanie_startowe_rj(n, zadania)
    cmax_start = oblicz_cmax(n, zadania, matrix_s, kolejnosc_start)

    cmax_koniec, kolejnosc_koniec = deterministyczna_poprawa(
        n, zadania, matrix_s, kolejnosc_start, limit_czasu
    )

    zapisz_rozwiazanie(plik_rozw, cmax_koniec, kolejnosc_koniec)

    end_programu = time.perf_counter()
    czas_calosc = end_programu - start_programu

    print(f"Instancja n={n}")
    print(f"Cmax Start (Rj):   {cmax_start}")
    print(f"Cmax Koniec:       {cmax_koniec}")
    print(f"Poprawa:           {cmax_start - cmax_koniec}")
    print(f"Czas obliczeń:     {czas_calosc:.4f} s (Limit: {limit_input}s)")


if __name__ == "__main__":
    main()