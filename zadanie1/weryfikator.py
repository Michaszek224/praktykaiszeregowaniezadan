import sys
import os

def weryfikuj(plik_problemu, plik_rozwiazania):
    """
    Weryfikuje poprawność pliku rozwiązania na podstawie pliku problemu.
    (Ta funkcja pozostała bez zmian w swojej logice, zmienił się sposób jej wywołania).
    """
    print(f"Plik problemu: '{plik_problemu}'")
    print(f"Plik rozwiązania: '{plik_rozwiazania}'")
    print("-" * 35)

    # --- KROK 1: Wczytywanie pliku problemu ---
    try:
        with open(plik_problemu, 'r') as f:
            lines = f.readlines()
            n, s = map(int, lines[0].strip().split())
            zadania_data = {}
            for i, line in enumerate(lines[1:]):
                if line.strip():
                    p, d = map(int, line.strip().split())
                    zadania_data[i + 1] = (p, d) # Klucz: numer zadania (1-based)
        
        if len(zadania_data) != n:
             print(f"❌ BŁĄD KRYTYCZNY: Zadeklarowana liczba zadań 'n' ({n}) nie zgadza się z liczbą wczytanych zadań ({len(zadania_data)}).")
             return

    except FileNotFoundError:
        print(f"❌ BŁĄD: Nie znaleziono pliku problemu: '{plik_problemu}'")
        return
    except (ValueError, IndexError) as e:
        print(f"❌ BŁĄD: Niepoprawny format pliku problemu '{plik_problemu}': {e}")
        return

    # --- KROK 2: Wczytywanie pliku rozwiązania ---
    try:
        with open(plik_rozwiazania, 'r') as f:
            lines = [line for line in f.readlines() if line.strip()]
            zgłoszone_opóźnienie = int(lines[0].strip())
            k = int(lines[1].strip())
            batche = [list(map(int, line.strip().split())) for line in lines[2:]]

    except FileNotFoundError:
        print(f"❌ Błąd: Nie znaleziono pliku rozwiązania: '{plik_rozwiazania}'")
        return
    except (ValueError, IndexError) as e:
        print(f"❌ BŁĄD: Niepoprawny format pliku rozwiązania '{plik_rozwiazania}': {e}")
        return

    # --- KROK 3: Walidacja struktury rozwiązania ---
    if len(batche) != k:
        print(f"❌ BŁĄD STRUKTURALNY: Zadeklarowana liczba batchy 'k' ({k}) nie zgadza się z faktyczną liczbą ({len(batche)}).")
        return

    wszystkie_zadania_w_rozwiazaniu = [zadanie for batch in batche for zadanie in batch]
    if len(wszystkie_zadania_w_rozwiazaniu) != n:
        print(f"❌ BŁĄD STRUKTURALNY: Łączna liczba zadań w rozwiązaniu ({len(wszystkie_zadania_w_rozwiazaniu)}) nie zgadza się z 'n' ({n}).")
        return
    
    oczekiwany_zbior_zadan = set(range(1, n + 1))
    otrzymany_zbior_zadan = set(wszystkie_zadania_w_rozwiazaniu)
    if oczekiwany_zbior_zadan != otrzymany_zbior_zadan:
        print("❌ BŁĄD STRUKTURALNY: Zadania w pliku rozwiązania nie są poprawne (brakuje zadań lub są duplikaty).")
        return
    
    print("✅ Struktura rozwiązania jest poprawna.")

    # --- KROK 4: Obliczanie całkowitego opóźnienia ---
    czas_bieżący = 0
    obliczone_całkowite_opóźnienie = 0

    for i, batch in enumerate(batche):
        czas_przetwarzania_batcha = sum(zadania_data[nr_zadania][0] for nr_zadania in batch)
        czas_ukończenia_batcha = czas_bieżący + czas_przetwarzania_batcha
        for nr_zadania in batch:
            termin_dj = zadania_data[nr_zadania][1]
            opóźnienie_j = max(0, czas_ukończenia_batcha - termin_dj)
            obliczone_całkowite_opóźnienie += opóźnienie_j
        czas_bieżący = czas_ukończenia_batcha + s

    # --- KROK 5: Porównanie wyników i werdykt ---
    print("\n--- Werdykt ---")
    print(f"Obliczona suma opóźnień (∑Dj): {obliczone_całkowite_opóźnienie}")
    print(f"Zgłoszona suma opóźnień w pliku: {zgłoszone_opóźnienie}")

    if obliczone_całkowite_opóźnienie == zgłoszone_opóźnienie:
        print("\n✅ POPRAWNIE! Wartość funkcji celu zgadza się z obliczeniami.")
    else:
        print("\n❌ BŁĄD! Wartość funkcji celu nie zgadza się.")
        print(f"   Różnica: {abs(obliczone_całkowite_opóźnienie - zgłoszone_opóźnienie)}")
    

if __name__ == "__main__":
    # --- GŁÓWNA PĘTLA STERUJĄCA ---

    # Sprawdzenie argumentów
    if len(sys.argv) != 3:
        print("Błąd: Nieprawidłowa liczba argumentów.")
        print("Sposób użycia: python weryfikator.py <katalog_z_wynikami> <katalog_z_instancjami>")
        sys.exit(1)

    katalog_rozwiazan = sys.argv[1]
    katalog_problemow = sys.argv[2]

    # Sprawdzenie, czy katalogi istnieją
    if not os.path.isdir(katalog_rozwiazan):
        print(f"Błąd: Katalog z rozwiązaniami '{katalog_rozwiazan}' nie istnieje.")
        sys.exit(1)
    if not os.path.isdir(katalog_problemow):
        print(f"Błąd: Katalog z danymi wejściowymi '{katalog_problemow}' nie istnieje.")
        sys.exit(1)

    print(f"🔍 Rozpoczynam weryfikację dla plików w katalogu: '{katalog_rozwiazan}'")
    print("=========================================================")

    # Pętla iterująca po wszystkich rozmiarach problemu (50, 100, ..., 500)
    for n in range(50, 501, 50):
        # Tworzenie nazw plików na podstawie wzorca
        nazwa_pliku_rozwiazania = f"out_{n}.txt"
        nazwa_pliku_problemu = f"problem_n_{n}.txt"

        sciezka_rozwiazania = os.path.join(katalog_rozwiazan, nazwa_pliku_rozwiazania)
        sciezka_problemu = os.path.join(katalog_problemow, nazwa_pliku_problemu)

        print(f"\n--- Sprawdzanie instancji dla n = {n} ---")
        
        # Sprawdzenie, czy oba pliki (problem i rozwiązanie) istnieją
        if not os.path.exists(sciezka_rozwiazania):
            print(f"🟡 POMINIĘTO: Nie znaleziono pliku rozwiązania: '{sciezka_rozwiazania}'")
            print("=========================================================")
            continue 
        
        if not os.path.exists(sciezka_problemu):
            print(f"🟡 POMINIĘTO: Nie znaleziono pliku problemu: '{sciezka_problemu}'")
            print("=========================================================")
            continue

        # Wywołanie funkcji weryfikującej dla znalezionej pary plików
        weryfikuj(sciezka_problemu, sciezka_rozwiazania)
        print("=========================================================")