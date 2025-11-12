def wczytaj_dane_wejsciowe(sciezka):
    with open(sciezka, 'r') as f:
        n = int(f.readline().strip())
        zadania = []
        for i in range(n):
            linia = f.readline().strip().split()
            p, r, w = int(linia[0]), int(linia[1]), int(linia[2])
            zadania.append({'id': i+1, 'p': p, 'r': r, 'w': w})
    return n, zadania

def wczytaj_dane_wyjsciowe(sciezka):
    with open(sciezka, 'r') as f:
        wynik = int(f.readline().strip())
        stanowiska = []
        for i in range(4):
            linia = f.readline().strip()
            if linia:
                zadania_na_stanowisku = list(map(int, linia.split()))
            else:
                zadania_na_stanowisku = []
            stanowiska.append(zadania_na_stanowisku)
    return wynik, stanowiska

def oblicz_kryterium(zadania, stanowiska):
    suma = 0
    
    for nr_stanowiska, sekwencja in enumerate(stanowiska):
        czas = 0
        for nr_zadania in sekwencja:
            zadanie = zadania[nr_zadania - 1]
            
            # Czas rozpoczęcia to max(aktualny czas, czas możliwego rozpoczęcia)
            czas_rozpoczecia = max(czas, zadanie['r'])
            
            # Czas zakończenia
            C_j = czas_rozpoczecia + zadanie['p']
            
            #Flow time
            F_j = C_j - zadanie['r']
            
            # Koszt
            koszt = zadanie['w'] * F_j
            suma += koszt
            
            # Aktualizuj czas na stanowisku
            czas = C_j
    
    return suma

def weryfikuj(plik_wejsciowy, plik_wyjsciowy):
    """Główna funkcja weryfikująca poprawność rozwiązania."""
    # Wczytaj dane
    n, zadania = wczytaj_dane_wejsciowe(plik_wejsciowy)
    wynik_podany, stanowiska = wczytaj_dane_wyjsciowe(plik_wyjsciowy)
    
    bledy = []
    ostrzezenia = []
    
    # Test 1: Sprawdź liczbę zadań
    print("\n[TEST 1] Sprawdzanie liczby zadań...")
    wszystkie_zadania = []
    for stanowisko in stanowiska:
        wszystkie_zadania.extend(stanowisko)
    
    if len(wszystkie_zadania) != n:
        bledy.append(f"Błąd: Liczba zadań w pliku wyjściowym ({len(wszystkie_zadania)}) "
                    f"nie zgadza się z liczbą w pliku wejściowym ({n})")
        print(f"BŁĄD: Znaleziono {len(wszystkie_zadania)} zadań, oczekiwano {n}")
    else:
        print(f"OK: Liczba zadań zgadza się ({n})")
    
    # Test 2: Sprawdź unikalność zadań
    print("\n[TEST 2] Sprawdzanie unikalności zadań...")
    zadania_set = set(wszystkie_zadania)
    
    if len(zadania_set) != len(wszystkie_zadania):
        duplikaty = [x for x in wszystkie_zadania if wszystkie_zadania.count(x) > 1]
        bledy.append(f"Błąd: Znaleziono duplikaty zadań: {set(duplikaty)}")
        print(f"BŁĄD: Zadania nie są unikalne. Duplikaty: {set(duplikaty)}")
    else:
        print(f"OK: Wszystkie zadania są unikalne")
    
    # Test 3: Sprawdź czy wszystkie zadania są w zakresie 1..n
    print("\n[TEST 3] Sprawdzanie poprawności numerów zadań...")
    niepoprawne = [x for x in wszystkie_zadania if x < 1 or x > n]
    
    if niepoprawne:
        bledy.append(f"Błąd: Znaleziono zadania spoza zakresu [1, {n}]: {niepoprawne}")
        print(f"BŁĄD: Zadania spoza zakresu: {niepoprawne}")
    else:
        print(f"OK: Wszystkie numery zadań są w zakresie [1, {n}]")
    
    # Test 4: Sprawdź czy wszystkie zadania występują
    print("\n[TEST 4] Sprawdzanie kompletności zadań...")
    brakujace = set(range(1, n+1)) - zadania_set
    
    if brakujace:
        bledy.append(f"Błąd: Brakujące zadania: {brakujace}")
        print(f"BŁĄD: Brakujące zadania: {sorted(brakujace)}")
    else:
        print(f"OK: Wszystkie zadania występują w harmonogramie")
    
    # Test 5: Oblicz i sprawdź wartość kryterium
    print("\n[TEST 5] Sprawdzanie wartości kryterium...")
    if not bledy:  # Tylko jeśli nie ma błędów w poprzednich testach
        wynik_obliczony = oblicz_kryterium(zadania, stanowiska)
        
        print(f"  Wartość podana:     {wynik_podany}")
        print(f"  Wartość obliczona:  {wynik_obliczony}")
        
        if wynik_podany != wynik_obliczony:
            bledy.append(f"Błąd: Wartość kryterium się nie zgadza. "
                        f"Podano: {wynik_podany}, obliczono: {wynik_obliczony}")
            print(f"BŁĄD: Wartości się nie zgadzają!")
        else:
            print(f"OK: Wartość kryterium jest poprawna")
    else:
        print(f"POMINIĘTO: Nie można obliczyć kryterium z powodu wcześniejszych błędów")
    
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Użycie: python weryfikator.py <plik_wejsciowy> <plik_wyjsciowy>")
        print("\nPrzykład:")
        print("  python weryfikator.py dane.txt wynik.txt")
    else:
        plik_wej = sys.argv[1]
        plik_wyj = sys.argv[2]
        
        try:
            weryfikuj(plik_wej, plik_wyj)
        except FileNotFoundError as e:
            print(f"Błąd: Nie znaleziono pliku: {e.filename}")
        except Exception as e:
            print(f"Błąd: {str(e)}")
