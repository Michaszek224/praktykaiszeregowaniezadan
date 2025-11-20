#!/bin/bash

# Skrypt zamieniający kropki na przecinki w pliku
# Sprawdź czy podano nazwę pliku
if [ $# -eq 0 ]; then
    echo "Użycie: $0 <plik_wejściowy> [plik_wyjściowy]"
    exit 1
fi

INPUT_FILE="$1"
OUTPUT_FILE="$2"

rm -f "$OUTPUT_FILE"
touch "$OUTPUT_FILE"
# Sprawdź czy plik istnieje
if [ ! -f "$INPUT_FILE" ]; then
    echo "Błąd: Plik '$INPUT_FILE' nie istnieje"
    exit 1
fi

# Zamień kropki na przecinki
sed 's/\./,/g' "$INPUT_FILE" > "$OUTPUT_FILE"

echo "Gotowe! Wynik zapisano w: $OUTPUT_FILE"
