#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import subprocess
import time

def verify_execution(executable_path, instance_path, output_path, time_limit):
    """
    Uruchamia zewnętrzny program, mierzy jego czas działania i weryfikuje limit czasu.

    Args:
        executable_path (str): Ścieżka do pliku wykonywalnego algorytmu.
        instance_path (str): Ścieżka do pliku z danymi wejściowymi (instancją).
        output_path (str): Ścieżka do pliku, gdzie algorytm zapisze wyniki.
        time_limit (float): Maksymalny dozwolony czas wykonania w sekundach.
    """
    # Budowanie polecenia do uruchomienia.
    # Zakładamy, że algorytm przyjmuje dwa argumenty: plik wejściowy i plik wyjściowy.
    # Jeśli algorytm jest skryptem Pythona, polecenie powinno wyglądać np.:
    # command = ['python', executable_path, instance_path, output_path]
    # Dla skompilowanego programu:
    # command = [executable_path, instance_path, output_path]
    # Poniższa wersja jest uniwersalna, jeśli plik ma uprawnienia do wykonania
    # lub jest skojarzony z odpowiednim interpreterem w systemie.
    command = ['python', executable_path, instance_path, output_path, str(time_limit)]
    
    print(f"--- Weryfikator Czasu Działania ---")
    print(f"▶️  Uruchamiam program: {' '.join(command)}")
    print(f"⏳ Limit czasu: {time_limit} s")
    print("------------------------------------")

    try:
        # Rejestrujemy czas rozpoczęcia
        start_time = time.monotonic()

        # Uruchamiamy proces z zadanym limitem czasu (timeout).
        # stdout=subprocess.DEVNULL i stderr=subprocess.DEVNULL ukrywają wyjście
        # algorytmu, aby nie zaśmiecać konsoli weryfikatora.
        # Jeśli chcesz widzieć, co wypisuje algorytm, usuń te dwa argumenty.
        subprocess.run(
            command, 
            timeout=time_limit, 
            check=True, # Rzuć wyjątek, jeśli program zakończy się błędem (kod wyjścia != 0)
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # Rejestrujemy czas zakończenia
        end_time = time.monotonic()
        duration = end_time - start_time

        print(f"✅ SUKCES!")
        print(f"⏱️  Czas działania: {duration:.4f} s")
        print(f"✔️  Limit ({time_limit} s) nie został przekroczony.")

    except FileNotFoundError:
        print(f"❌ BŁĄD: Nie znaleziono pliku wykonywalnego '{executable_path}'.")
        print("   Upewnij się, że podałeś poprawną ścieżkę i plik ma uprawnienia do wykonania.")
    
    except subprocess.TimeoutExpired:
        print(f"❌ BŁĄD: Przekroczono limit czasu!")
        print(f"⏱️  Program działał dłużej niż {time_limit} s i został zatrzymany.")
    
    except subprocess.CalledProcessError as e:
        print(f"❌ BŁĄD: Program zakończył działanie z kodem błędu {e.returncode}.")
        print("   Oznacza to, że wystąpił błąd w trakcie jego wykonywania (niezwiązany z limitem czasu).")
    
    except Exception as e:
        print(f"❌ Wystąpił nieoczekiwany błąd: {e}")


# === Główna część skryptu ===
if __name__ == "__main__":
    # Sprawdzenie liczby argumentów
    if len(sys.argv) != 5:
        print("Błąd: Nieprawidłowa liczba argumentów.")
        print("Sposób użycia:")
        print(f"  python {sys.argv[0]} <plik_wykonywalny> <plik_instancji> <plik_wynikowy> <limit_czasu_s>")
        print("\nPrzykład:")
        print(f"  python {sys.argv[0]} ./moj_algorytm.py dane/in1.txt wyniki/out1.txt 10.5")
        sys.exit(1)

    # Odczytanie argumentów z linii poleceń
    executable = sys.argv[1]
    instance_file = sys.argv[2]
    output_file = sys.argv[3]
    
    try:
        # Konwersja limitu czasu na liczbę
        time_limit_seconds = float(sys.argv[4])
    except ValueError:
        print(f"Błąd: Limit czasu '{sys.argv[4]}' musi być liczbą.")
        sys.exit(1)

    # Wywołanie głównej funkcji weryfikatora
    verify_execution(executable, instance_file, output_file, time_limit_seconds)