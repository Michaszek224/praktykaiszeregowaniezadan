import random
import os

# Zakres liczby paczek (zadań)
N_VALUES = range(50, 501, 50)

# Zakres dla czasu przygotowawczego 's' między partiami (batchami)
S_MIN = 5
S_MAX = 25

# Zakres dla czasu pakowania pojedynczego zamówienia 'pj'
P_MIN = 1
P_MAX = 20

# Współczynnik do określania maksymalnego terminu 'dj'.
# dj będzie losowane z przedziału [pj, suma_wszystkich_p * WSPOLCZYNNIK_DJ]
# Wartość < 1.0 tworzy "ciaśniejsze" i trudniejsze problemy.
# Wartość > 1.0 tworzy "luźniejsze" problemy.
WSPOLCZYNNIK_DJ = 0.8

# Nazwa folderu do zapisu wygenerowanych plików
OUTPUT_DIR = "155863Generator"

def generuj_instancje():
    """
    Główna funkcja generująca pliki z danymi wejściowymi.
    """
    # Sprawdzenie, czy folder wyjściowy istnieje, jeśli nie - utwórz go
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Utworzono folder: '{OUTPUT_DIR}'")

    # Pętla generująca pliki dla każdej określonej liczby zadań 'n'
    for n in N_VALUES:
        print(f"Generowanie instancji dla n = {n}...")

        # 1. Losowanie stałego czasu przygotowawczego 's'
        s = random.randint(S_MIN, S_MAX)

        # 2. Generowanie czasów wykonania 'pj' dla wszystkich 'n' zadań
        czasy_p = [random.randint(P_MIN, P_MAX) for _ in range(n)]

        # 3. Obliczenie sumy czasów 'pj' potrzebnej do ustalenia realistycznych terminów 'dj'
        suma_p = sum(czasy_p)
        
        # Ustalenie górnej granicy dla losowania terminów 'dj'
        górna_granica_dj = int(suma_p * WSPOLCZYNNIK_DJ)

        # Lista na przechowywanie par (pj, dj)
        zadania = []
        for p in czasy_p:
            # Termin 'dj' musi być co najmniej równy czasowi wykonania zadania 'pj'
            # Losujemy dj z przedziału [pj, górna_granica_dj]
            # Używamy max(p, ...) aby uniknąć sytuacji, gdyby górna granica była mniejsza od p
            d = random.randint(p, max(p, górna_granica_dj))
            zadania.append((p, d))

        # 4. Zapisywanie danych do pliku
        nazwa_pliku = f"155863_{n}.txt"
        sciezka_pliku = os.path.join(OUTPUT_DIR, nazwa_pliku)

        try:
            with open(sciezka_pliku, 'w') as f:
                # Zapis pierwszej linii: n s
                f.write(f"{n} {s}\n")

                # Zapis kolejnych linii z zadaniami: pj dj
                for p, d in zadania:
                    f.write(f"{p} {d}\n")
            
            print(f"-> Zapisano plik: {sciezka_pliku}")

        except IOError as e:
            print(f"Błąd podczas zapisu do pliku {sciezka_pliku}: {e}")
    
    print("\nZakończono generowanie wszystkich instancji problemu.")


# Uruchomienie generatora
if __name__ == "__main__":
    generuj_instancje()