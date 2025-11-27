import sys
import time
import os


# --- 1. OBSŁUGA PLIKÓW ---
def wczytaj_instancje(plik_instancji):
    if not os.path.exists(plik_instancji):
        print(f"BŁĄD: Plik instancji '{plik_instancji}' nie istnieje.")
        return None, None, None

    zadania = {}
    lista_zadan = []
    try:
        with open(plik_instancji, 'r') as f:
            linia_n = f.readline().strip()
            if not linia_n: return None, None, None
            n = int(linia_n)

            for i in range(1, n + 1):
                linia = f.readline().strip()
                if not linia: break
                p, r, w = map(int, linia.split())

                wspt = p / w if w > 0 else float('inf')

                obj = {'id': i, 'p': p, 'r': r, 'w': w, 'wspt': wspt}
                lista_zadan.append(obj)
                zadania[i] = obj
        return n, lista_zadan, zadania
    except Exception as e:
        print(f"BŁĄD: Nie można wczytać pliku instancji '{plik_instancji}': {e}")
        return None, None, None


def zapisz_rozwiazanie(plik_rozwiazania, koszt, harmonogram):
    try:
        with open(plik_rozwiazania, 'w') as f:
            f.write(f"{int(koszt)}\n")
            for sekwencja in harmonogram:
                linia = ' '.join(map(str, sekwencja))
                f.write(f"{linia}\n")
    except IOError as e:
        print(f"Błąd zapisu do pliku {plik_rozwiazania}: {e}")


# --- 2. LOGIKA OBLICZANIA KOSZTU ---

def oblicz_koszt_harmonogramu(harmonogram, zadania_dict):
    calkowity_koszt = 0
    for sekwencja in harmonogram:
        czas_wolny = 0
        for id_zad in sekwencja:
            z = zadania_dict[id_zad]

            start = max(czas_wolny, z['r'])

            koniec = start + z['p']

            calkowity_koszt += z['w'] * (koniec - z['r'])

            czas_wolny = koniec
    return calkowity_koszt


# --- 3. ALGORYTMY ---

def rozwiazanie_startowe_wspt(n, lista_zadan):
    liczba_maszyn = 4
    czasy_zwolnienia = [0] * liczba_maszyn
    harmonogram = [[] for _ in range(liczba_maszyn)]
    pozostale = lista_zadan[:]

    while pozostale:

        idx_maszyny = min(range(liczba_maszyn), key=lambda i: czasy_zwolnienia[i])
        t_gotowosci = czasy_zwolnienia[idx_maszyny]

        dostepne = [z for z in pozostale if z['r'] <= t_gotowosci]

        if dostepne:

            wybrane = min(dostepne, key=lambda z: z['wspt'])
        else:

            wybrane = min(pozostale, key=lambda z: z['r'])

        p, r, id_z = wybrane['p'], wybrane['r'], wybrane['id']
        start = max(t_gotowosci, r)
        koniec = start + p

        czasy_zwolnienia[idx_maszyny] = koniec
        harmonogram[idx_maszyny].append(id_z)
        pozostale.remove(wybrane)

    return harmonogram


def deterministyczna_poprawa(n, zadania_dict, harmonogram_startowy, limit_czasu):
    start_time = time.perf_counter()

    najlepszy_harmonogram = [wiersz[:] for wiersz in harmonogram_startowy]
    najlepszy_koszt = oblicz_koszt_harmonogramu(najlepszy_harmonogram, zadania_dict)

    ulepszono_cos = True

    while ulepszono_cos:
        ulepszono_cos = False

        if (time.perf_counter() - start_time) > (limit_czasu - 0.2):
            break

        lista_pozycji = []
        for m_idx, maszyna in enumerate(najlepszy_harmonogram):
            for t_idx, id_zad in enumerate(maszyna):
                lista_pozycji.append((m_idx, t_idx, id_zad))

        for stary_m, stara_poz, id_zad in lista_pozycji:

            if (time.perf_counter() - start_time) > limit_czasu:
                break

            obecny_harmonogram = [wiersz[:] for wiersz in najlepszy_harmonogram]
            zadanie = obecny_harmonogram[stary_m].pop(stara_poz)

            znaleziono_lepsze = False

            for nowy_m in range(4):
                dlugosc_maszyny = len(obecny_harmonogram[nowy_m])

                for nowa_poz in range(dlugosc_maszyny + 1):

                    if nowy_m == stary_m and nowa_poz == stara_poz:
                        continue

                    obecny_harmonogram[nowy_m].insert(nowa_poz, zadanie)

                    nowy_koszt = oblicz_koszt_harmonogramu(obecny_harmonogram, zadania_dict)

                    if nowy_koszt < najlepszy_koszt:
                        najlepszy_koszt = nowy_koszt
                        najlepszy_harmonogram = [wiersz[:] for wiersz in obecny_harmonogram]
                        ulepszono_cos = True
                        znaleziono_lepsze = True
                        break

                    obecny_harmonogram[nowy_m].pop(nowa_poz)

                if znaleziono_lepsze:
                    break

            if znaleziono_lepsze:
                break

    return najlepszy_koszt, najlepszy_harmonogram


# --- 4. MAIN ---

def main():
    if len(sys.argv) < 4:
        print("Użycie: python algorytm.py <instancja> <wyjscie> <limit_czasu>")
        sys.exit(1)

    start_programu = time.perf_counter()

    plik_instancji = sys.argv[1]
    plik_rozwiazania = sys.argv[2]

    limit_czasu_input = float(sys.argv[3])
    limit_czasu = max(0.1, limit_czasu_input - 1.0)

    n, lista_zadan, zadania_dict = wczytaj_instancje(plik_instancji)
    if n is None:
        sys.exit(1)

    harmonogram_start = rozwiazanie_startowe_wspt(n, lista_zadan)
    koszt_start = oblicz_koszt_harmonogramu(harmonogram_start, zadania_dict)

    koszt_koncowy, harmonogram_koncowy = deterministyczna_poprawa(
        n, zadania_dict, harmonogram_start, limit_czasu
    )

    zapisz_rozwiazanie(plik_rozwiazania, koszt_koncowy, harmonogram_koncowy)

    end_programu = time.perf_counter()
    czas_calkowity = end_programu - start_programu

    print(f"Koszt startowy: {koszt_start}")
    print(f"Wynik (koszt):  {koszt_koncowy}")
    print(f"Poprawa:        {koszt_start - koszt_koncowy}")
    print(f"Czas obliczeń:  {czas_calkowity:.4f} s (Limit: {limit_czasu_input}s)")


if __name__ == "__main__":
    main()