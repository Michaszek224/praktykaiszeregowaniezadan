def wczytaj_dane_wejsciowe(sciezka):
    with open(sciezka, "r") as f:
        n = int(f.readline().strip())

        zadania = []
        for _ in range(n):
            p1, p2, p3, p4, r = map(int, f.readline().split())
            zadania.append({"p": [p1, p2, p3, p4], "r": r})

        # macierz Sij
        S = []
        for _ in range(n):
            row = list(map(int, f.readline().split()))
            S.append(row)

    return n, zadania, S


def wczytaj_dane_wyjsciowe(sciezka):
    with open(sciezka, "r") as f:
        Cmax = int(f.readline().strip())
        sekwencja = list(map(int, f.readline().strip().split()))
    return Cmax, sekwencja


def oblicz_Cmax(zadania, S, sekwencja):
    C = [0, 0, 0, 0]

    poprzednie = None

    for _, j in enumerate(sekwencja):
        j -= 1
        rj = zadania[j]["r"]
        p = zadania[j]["p"]

        prev_C = C.copy()

        # setup między poprzednim i bieżącym (0 jeśli pierwsze zadanie)
        setup = 0 if poprzednie is None else S[poprzednie][j]

        # Maszyna 1: musi uwzględnić prev_C[0] + setup oraz rj
        start_M1 = max(prev_C[0] + setup, rj)
        C[0] = start_M1 + p[0]

        # Maszyny 2..4: start = max(czas po poprzedniej maszynie dla tego zadania, poprzednie_zadanie_na_tej_maszynie + setup)
        for m in range(1, 4):
            start_m = max(C[m - 1], prev_C[m] + setup)
            C[m] = start_m + p[m]

        poprzednie = j

    return C[3]  # zakończenie na maszynie 4


def weryfikuj(plik_wejsciowy, plik_wyjsciowy):
    n, zadania, S = wczytaj_dane_wejsciowe(plik_wejsciowy)
    Cmax_podany, sekwencja = wczytaj_dane_wyjsciowe(plik_wyjsciowy)

    bledy = []

    print("\n--- WERYFIKACJA ---")

    # TEST 1: liczba zadań
    if len(sekwencja) != n:
        bledy.append("Błąd: sekwencja nie zawiera dokładnie n zadań.")
        print(f"BŁĄD: Sekwencja ma {len(sekwencja)} zadań, oczekiwano {n}")
    else:
        print("OK: liczba zadań poprawna")

    # TEST 2: unikalność
    if len(set(sekwencja)) != len(sekwencja):
        bledy.append("Błąd: sekwencja zawiera duplikaty.")
        dup = [x for x in sekwencja if sekwencja.count(x) > 1]
        print(f"BŁĄD: Duplikaty: {set(dup)}")
    else:
        print("OK: brak duplikatów")

    # TEST 3: zakres numerów
    niepoprawne = [x for x in sekwencja if not (1 <= x <= n)]
    if niepoprawne:
        bledy.append("Błąd: sekwencja zawiera numery spoza 1..n")
        print(f"BŁĄD: Niepoprawne zadania: {niepoprawne}")
    else:
        print("OK: numery zadań poprawne")

    # TEST 4: kompletność
    brakujace = set(range(1, n + 1)) - set(sekwencja)
    if brakujace:
        bledy.append("Błąd: brakuje zadań w sekwencji.")
        print(f"BŁĄD: Brakujące: {brakujace}")
    else:
        print("OK: wszystkie zadania obecne")

    # TEST 5: wartość Cmax
    if not bledy:
        Cmax_obliczony = oblicz_Cmax(zadania, S, sekwencja)

        print(f"\nPodany Cmax:    {Cmax_podany}")
        print(f"Obliczony Cmax: {Cmax_obliczony}")

        if Cmax_podany != Cmax_obliczony:
            bledy.append("Błąd: wartość Cmax niepoprawna.")
            print("BŁĄD: wartości się różnią!")
        else:
            print("OK: wartość Cmax poprawna")
    else:
        print("\nPOMINIĘTO obliczenie Cmax z powodu wcześniejszych błędów.")

    return bledy


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Użycie: python weryfikator_F4.py <plik_wejściowy> <plik_wyjściowy>")
    else:
        plik_in = sys.argv[1]
        plik_out = sys.argv[2]

        try:
            bledy = weryfikuj(plik_in, plik_out)
            if not bledy:
                print("\n>>> ROZWIĄZANIE JEST POPRAWNE ✔\n")
            else:
                print("\n>>> WYKRYTO BŁĘDY ❌")
                for b in bledy:
                    print(" -", b)
        except Exception as e:
            print("Błąd:", str(e))
