import sys
import time
import random
import copy
import math

def wczytaj_dane(nazwa_pliku):
    try:
        with open(nazwa_pliku, 'r') as f:
            pierwsza_linia = f.readline().split()
            n = int(pierwsza_linia[0])
            s = int(pierwsza_linia[1])
            zadania_dict = {}
            for i in range(1, n + 1):
                linia = f.readline().split()
                p = int(linia[0])
                d = int(linia[1])
                zadania_dict[i] = {'id': i, 'p': p, 'd': d}
        return n, s, zadania_dict
    except FileNotFoundError:
        print(f"Błąd: Nie znaleziono pliku {nazwa_pliku}")
        sys.exit(1)
    except (ValueError, IndexError):
        print(f"Błąd: Niepoprawny format danych w pliku {nazwa_pliku}")
        sys.exit(1)

def oblicz_sume_opoznien(partie, s, zadania_dict):
    calkowite_opoznienie = 0
    aktualny_czas = 0
    for i, partia_ids in enumerate(partie):
        if not partia_ids: continue
        suma_p = sum(zadania_dict[zad_id]['p'] for zad_id in partia_ids)
        czas_setup = s if i > 0 else 0
        czas_ukonczenia_partii = aktualny_czas + czas_setup + suma_p
        for zad_id in partia_ids:
            opoznienie = max(0, czas_ukonczenia_partii - zadania_dict[zad_id]['d'])
            calkowite_opoznienie += opoznienie
        aktualny_czas = czas_ukonczenia_partii
    return calkowite_opoznienie

def heurystyka_grupowania_edd_z_progiem(n, s, zadania_dict, max_batch_size):
    zadania = list(zadania_dict.values())
    posortowane_zadania = sorted(zadania, key=lambda z: z['d'])
    
    if not posortowane_zadania: return [], 0

    wszystkie_partie_obj = []
    aktualna_partia_obj = []
    czas_ukonczenia_poprzedniej_partii = 0

    for zadanie in posortowane_zadania:
        if not aktualna_partia_obj:
            aktualna_partia_obj.append(zadanie)
        else:
            suma_p_w_partii = sum(z['p'] for z in aktualna_partia_obj)
            hipotetyczny_czas_ukonczenia = (czas_ukonczenia_poprzedniej_partii + s +
                                            suma_p_w_partii + zadanie['p'])

            if (hipotetyczny_czas_ukonczenia <= zadanie['d'] and
                len(aktualna_partia_obj) < max_batch_size):
                aktualna_partia_obj.append(zadanie)
            else:
                wszystkie_partie_obj.append(aktualna_partia_obj)
                czas_ukonczenia_poprzedniej_partii += s + suma_p_w_partii
                aktualna_partia_obj = [zadanie]

    if aktualna_partia_obj:
        wszystkie_partie_obj.append(aktualna_partia_obj)

    partie_ids = [[zad['id'] for zad in partia] for partia in wszystkie_partie_obj]
    return partie_ids

def przeszukiwanie_lokalne(partie_startowe, s, zadania_dict, limit_czasu, start_time):
    najlepsze_partie = [p for p in copy.deepcopy(partie_startowe) if p]
    najlepsze_opoznienie = oblicz_sume_opoznien(najlepsze_partie, s, zadania_dict)

    iteracje = 0
    while time.time() - start_time < limit_czasu * 0.2:
        iteracje += 1
        partie_kandydujace = copy.deepcopy(najlepsze_partie)
        liczba_partii = len(partie_kandydujace)

        mozliwe_ruchy = []
        if liczba_partii >= 2: mozliwe_ruchy.extend(['swap', 'move'])
        if any(len(p) > 1 for p in partie_kandydujace): mozliwe_ruchy.append('split')
        if not mozliwe_ruchy: break

        ruch = random.choice(mozliwe_ruchy)

        if ruch == 'swap':
            idx1, idx2 = random.sample(range(liczba_partii), 2)
            if not partie_kandydujace[idx1] or not partie_kandydujace[idx2]: continue
            zad_idx_1 = random.randrange(len(partie_kandydujace[idx1]))
            zad_idx_2 = random.randrange(len(partie_kandydujace[idx2]))
            zad1, zad2 = partie_kandydujace[idx1][zad_idx_1], partie_kandydujace[idx2][zad_idx_2]
            partie_kandydujace[idx1][zad_idx_1], partie_kandydujace[idx2][zad_idx_2] = zad2, zad1
        elif ruch == 'move':
            idx_zrodlo, idx_cel = random.sample(range(liczba_partii), 2)
            if not partie_kandydujace[idx_zrodlo]: continue
            zad_idx = random.randrange(len(partie_kandydujace[idx_zrodlo]))
            zad = partie_kandydujace[idx_zrodlo].pop(zad_idx)
            partie_kandydujace[idx_cel].append(zad)
            if not partie_kandydujace[idx_zrodlo]:
                partie_kandydujace = [p for p in partie_kandydujace if p]
        elif ruch == 'split':
            mozliwe_do_podzialu = [i for i, p in enumerate(partie_kandydujace) if len(p) > 1]
            if not mozliwe_do_podzialu: continue
            idx_partii_do_podzialu = random.choice(mozliwe_do_podzialu)
            zad_idx_do_wydzielenia = random.randrange(len(partie_kandydujace[idx_partii_do_podzialu]))
            zad_do_wydzielenia = partie_kandydujace[idx_partii_do_podzialu].pop(zad_idx_do_wydzielenia)
            partie_kandydujace.append([zad_do_wydzielenia])

        nowe_opoznienie = oblicz_sume_opoznien(partie_kandydujace, s, zadania_dict)
        if nowe_opoznienie < najlepsze_opoznienie:
            najlepsze_opoznienie = nowe_opoznienie
            najlepsze_partie = partie_kandydujace
    
    return najlepsze_partie, najlepsze_opoznienie

def zapisz_wyniki(nazwa_pliku, partie, suma_opoznien):
    with open(nazwa_pliku, 'w') as f:
        f.write(f"{suma_opoznien}\n")
        f.write(f"{len(partie)}\n")
        for partia in partie:
            ids_partii = [str(zad_id) for zad_id in partia]
            f.write(" ".join(ids_partii) + "\n")

def main():
    if len(sys.argv) < 3:
        print("Użycie: python nazwa_programu.py <plik_wejsciowy> <plik_wyjsciowy>")
        sys.exit(1)

    plik_wejsciowy, plik_wyjsciowy = sys.argv[1], sys.argv[2]
    start_time = time.time()
    n, s, zadania_dict = wczytaj_dane(plik_wejsciowy)
    limit_czasu = n / 10.0
    
    if n > 0:
        max_batch_size = int(2 * math.sqrt(n) + 1)
        partie_startowe = heurystyka_grupowania_edd_z_progiem(n, s, zadania_dict, max_batch_size)
        
        finalne_partie, finalne_opoznienie = przeszukiwanie_lokalne(
            partie_startowe, s, zadania_dict, limit_czasu, start_time)
    else:
        finalne_partie, finalne_opoznienie = [], 0

    czas_wykonania = time.time() - start_time
    zapisz_wyniki(plik_wyjsciowy, finalne_partie, finalne_opoznienie)
    
    print(f"Algorytm zakończył działanie.")
    print(f"Uzyskana suma opóźnień: {finalne_opoznienie}")
    print(f"Czas działania: {czas_wykonania:.2f} s / {limit_czasu:.2f} s")
    if czas_wykonania > limit_czasu:
        print("\nUWAGA: PRZEKROCZONO LIMIT CZASU\n")

if __name__ == "__main__":
    main()