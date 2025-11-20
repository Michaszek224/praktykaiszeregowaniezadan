#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import subprocess
import time

def verify_execution(executable_path, instance_path, output_path, time_limit):
    
    # Sprawdź czy to plik .py i dodaj interpreter
    if executable_path.endswith('.py'):
        command = [sys.executable, executable_path, instance_path, output_path, str(time_limit)]
    else:
        command = [executable_path, instance_path, output_path, str(time_limit)]
    
    try:
        start_time = time.monotonic()
  
        result = subprocess.run(
            command, 
            timeout=time_limit + 1,  # Dodaj trochę bufora
            check=True,
            capture_output=True,  # Zmienione z DEVNULL
            text=True
        )
        end_time = time.monotonic()
        duration = end_time - start_time
        print(f"{duration:.2f}")
        
        # Opcjonalnie: pokaż output tylko jeśli był błąd
        # if result.stderr:
        #     print("STDERR:", result.stderr, file=sys.stderr)
        
    except FileNotFoundError:
        print(f"❌ BŁĄD: Nie znaleziono pliku wykonywalnego '{executable_path}'.")
        print("   Upewnij się, że podałeś poprawną ścieżkę i plik ma uprawnienia do wykonania.")
    
    except subprocess.TimeoutExpired:
        print(f"❌ BŁĄD: Przekroczono limit czasu!")
        print(f"⏱️  Program działał dłużej niż {time_limit} s i został zatrzymany.")
    
    except subprocess.CalledProcessError as e:
        print(f"❌ BŁĄD: Program zakończył działanie z kodem błędu {e.returncode}.")
        print(f"   STDOUT: {e.stdout}")
        print(f"   STDERR: {e.stderr}")
    
    except Exception as e:
        print(f"❌ Wystąpił nieoczekiwany błąd: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Błąd: Nieprawidłowa liczba argumentów.")
        print("Sposób użycia:")
        print(f"  python {sys.argv[0]} <plik_wykonywalny> <plik_instancji> <plik_wynikowy> <limit_czasu_s>")
        print("\nPrzykład:")
        print(f"  python {sys.argv[0]} ./moj_algorytm.py dane/in1.txt wyniki/out1.txt 10.5")
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
