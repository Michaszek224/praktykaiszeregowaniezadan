import os
import sys
import time

def algorytm(input_path, output_path, czas):
    start = time.time()
    #wczytywanie danyych
    try:
        with open(input_path, 'r') as f:
            lines = f.readlines()
            if not lines:
                print(f"Błąd: Plik wejściowy '{input_path}' jest pusty.")
                return

            n, s = map(int, lines[0].split())
            
            zadania = []
            for i in range(n):
                czas_zamowienia, deadline = map(int, lines[i + 1].split())
                zadania.append({'id': i + 1, 'czas_zamowienia': czas_zamowienia, 'deadline': deadline})

    except FileNotFoundError:
        print(f"Błąd: Nie znaleziono pliku wejściowego '{input_path}'.")
        return
    except (ValueError, IndexError):
        print(f"Błąd: Nieprawidłowy format danych w pliku '{input_path}'.{ValueError}")
        return

    laczny_czas_zamowienai = 0
    laczny_deadline = 0
    counter = 0

    for x in zadania:
        laczny_czas_zamowienai += x["czas_zamowienia"]
        laczny_deadline += x["deadline"]
        counter += 1

    # przetwarzanie po wczytaniu
    if not zadania:
        wszystkie_batche = []
    else:
        # rozne sortowania do wyboru
        sortowania = [
            lambda x: x['deadline'] / max(x['czas_zamowienia'], 0.001),
            lambda x: x['deadline'] - 0.5 * x['czas_zamowienia'],
            lambda x: x['deadline'] - x['czas_zamowienia'],
            lambda x: x['deadline'] / (x['czas_zamowienia'] + 1)
        ]

        najlepsze_opoznienie = float('inf')
        najlepsze_batche = []

        # testujemy każdą heurystykę
        for sortowanie in sortowania:
            zadania_posortowane = sorted(zadania, key=sortowanie)

            wszystkie_batche = []
            obecny_bartch = []
            czas_w_tym_batchu = 0
            obecny_czas = 0

            for zadanie in zadania_posortowane:
                if not obecny_bartch:
                    obecny_bartch.append(zadanie)
                    czas_w_tym_batchu = zadanie['czas_zamowienia']
                    continue

                dynamiczny_prog = (laczny_deadline / counter) * (1.0 + 0.3 * len(wszystkie_batche))

                if obecny_czas + czas_w_tym_batchu > dynamiczny_prog:
                    wszystkie_batche.append(obecny_bartch)
                    obecny_czas += czas_w_tym_batchu + s
                    obecny_bartch = [zadanie]
                    czas_w_tym_batchu = zadanie['czas_zamowienia']
                else:
                    obecny_bartch.append(zadanie)
                    czas_w_tym_batchu += zadanie['czas_zamowienia']

            if obecny_bartch:
                wszystkie_batche.append(obecny_bartch)

            # Obliczenie całkowitego opóźnienia
            opoznienie_calkowite = 0
            czas_ukonczenia = 0

            for i, batch in enumerate(wszystkie_batche):
                batch_p_sum = sum(zadanie['czas_zamowienia'] for zadanie in batch)
                czas_ukonczenia += batch_p_sum

                for zadanie in batch:
                    tardiness = max(0, czas_ukonczenia - zadanie['deadline'])
                    opoznienie_calkowite += tardiness

                if i < len(wszystkie_batche) - 1:
                    czas_ukonczenia += s

            # sprawdzenie, czy to najlepsze rozwiązanie
            if opoznienie_calkowite < najlepsze_opoznienie:
                najlepsze_opoznienie = opoznienie_calkowite
                najlepsze_batche = wszystkie_batche

        # po zakończeniu pętli
        wszystkie_batche = najlepsze_batche
        opoznienie_calkowite = najlepsze_opoznienie

    end = time.time()
    if end-start > czas:
        print("za duzo czasu")
        return 
    #zapis do plilku
    try:
        #sprawdzanie czy folder isstnieje
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        with open(output_path, 'w') as f_out:
            f_out.write(f"{opoznienie_calkowite}\n")
            f_out.write(f"{len(wszystkie_batche)}\n")
            for batch in wszystkie_batche:
                line = ' '.join(str(zadanie['id']) for zadanie in batch)
                f_out.write(f"{line}\n")
        
        # print(f"Przetwarzanie zakończone. Wynik zapisano w pliku: {output_path}")
        print(f"opoznienie: {opoznienie_calkowite}")

    except IOError as e:
        print(f"Błąd podczas zapisu do pliku '{output_path}': {e}")


# === Uruchomienie skryptu ===
if __name__ == "__main__":
    # Definicja ścieżek
    if len(sys.argv) != 4:
        print("Błąd: Nieprawidłowa liczba argumentów.")
        print("Sposób użycia: python 155863.py <plik_wejsciowy> <index> <plik_wyjsciowy> <limit_czasu>")
        sys.exit(1)

    plik_wejsciowy = sys.argv[1]
    wyniki = sys.argv[2]
    czas = float(sys.argv[3])
    
        
    # Wywołanie głównej funkcji
    algorytm(plik_wejsciowy, wyniki, czas)