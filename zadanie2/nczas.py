#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import subprocess
import time

def verify_execution(executable_path, instance_path, output_path, time_limit):
    
    # Sprawdź czy to plik .py i dodaj interpreter
    if executable_path.endswith('.py'):
        # Przekazujemy limit czasu jako argument, ale wrapper go nie egzekwuje "siłowo"
        command = ["python3", executable_path, instance_path, output_path, str(int(time_limit))]
    else:
        command = [executable_path, instance_path, output_path, str(time_limit)]
    
    start_time = time.monotonic()

    try:
        # Usunąłem parametr 'timeout'. Teraz wrapper czeka, aż program sam skończy.
        subprocess.run(
            command, 
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Program skończył się (szybko lub wolno) - mierzymy czas
        end_time = time.monotonic()
        duration = end_time - start_time
        print(f"{duration:.2f}")
        
    # Wyjątek TimeoutExpired jest teraz niemożliwy, więc go usunąłem.
        
    except FileNotFoundError:
        print(f"❌ BŁĄD: Nie znaleziono pliku wykonywalnego '{executable_path}'.")
    
    except subprocess.CalledProcessError as e:
        print(f"❌ BŁĄD: Program zakończył działanie z kodem błędu {e.returncode}.")
    
    except Exception as e:
        print(f"❌ Wystąpił nieoczekiwany błąd: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Błąd: Nieprawidłowa liczba argumentów.")
        print("Sposób użycia:")
        print(f"  python {sys.argv[0]} <plik_wykonywalny> <plik_instancji> <plik_wynikowy> <limit_czasu_s>")
        sys.exit(1)
    
    executable = sys.argv[1]
    instance_file = sys.argv[2]
    output_file = sys.argv[3]
    
    try:
        time_limit_seconds = float(sys.argv[4])
    except ValueError:
        print(f"Błąd: Limit czasu '{sys.argv[4]}' musi być liczbą.")
        sys.exit(1)
    
    verify_execution(executable, instance_file, output_file, time_limit_seconds)
