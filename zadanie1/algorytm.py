import os
import sys

def algorytm(input_path, output_path):
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
        print(f"Błąd: Nieprawidłowy format danych w pliku '{input_path}'.")
        return

    #przetwarzenai po wczytaniu
    if not zadania:
        wszystkie_batche = []
    else:
        #Sortowanie zadań według deadlinu
        zadania.sort(key=lambda x: x['deadline'])

        #Tworzenie partii
        wszystkie_batche = []
        obecny_bartch = []
        czas_w_tym_batchu = 0
        obecny_czas = 0

        #proba minimalizacji zlego deadlinu
        for zadanie in zadania:
            
            if not obecny_bartch:
                obecny_bartch.append(zadanie)
                czas_w_tym_batchu = zadanie['czas_zamowienia']
                continue

            
            if (obecny_czas + czas_w_tym_batchu) > zadanie['deadline']:
                wszystkie_batche.append(obecny_bartch)
                obecny_czas += czas_w_tym_batchu + s
                
                obecny_bartch = [zadanie]
                czas_w_tym_batchu = zadanie['czas_zamowienia']
            else:
                obecny_bartch.append(zadanie)
                czas_w_tym_batchu += zadanie['czas_zamowienia']

        if obecny_bartch:
            wszystkie_batche.append(obecny_bartch)

    #Obliczenie całkowitego opóźnienia
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
        
        print(f"Przetwarzanie zakończone. Wynik zapisano w pliku: {output_path}")

    except IOError as e:
        print(f"Błąd podczas zapisu do pliku '{output_path}': {e}")


# === Uruchomienie skryptu ===
if __name__ == "__main__":
    # Definicja ścieżek
    for n in range(50,501,50):    
        input_file = os.path.join('155863Generator', f'155863_{n}.txt')
        output_file = os.path.join('wyniki', f'155863_{n}_wynik.txt')
        
        # Wywołanie głównej funkcji
        algorytm(input_file, output_file)