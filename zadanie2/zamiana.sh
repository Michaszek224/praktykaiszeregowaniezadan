#!/bin/bash

# Skrypt zamieniający kropki na przecinki we wszystkich plikach z folderu

# Sprawdź czy podano folder wejściowy
if [ $# -eq 0 ]; then
    echo "Użycie: $0 <folder_wejściowy>"
    exit 1
fi

INPUT_DIR="$1"
OUTPUT_DIR="noweCzasy"

# Sprawdź czy folder wejściowy istnieje
if [ ! -d "$INPUT_DIR" ]; then
    echo "Błąd: Folder '$INPUT_DIR' nie istnieje"
    exit 1
fi

# Utwórz folder wyjściowy jeśli nie istnieje
mkdir -p "$OUTPUT_DIR"

# Licznik przetworzonych plików
count=0

# Przetwórz wszystkie pliki w folderze wejściowym
for file in "$INPUT_DIR"/*; do
    # Pomiń jeśli to folder
    if [ -d "$file" ]; then
        continue
    fi
    
    # Pobierz samą nazwę pliku bez ścieżki
    filename=$(basename "$file")
    
    # Zamień kropki na przecinki i zapisz do nowego folderu
    sed 's/\./,/g' "$file" > "$OUTPUT_DIR/$filename"
    
    echo "Przetworzono: $filename"
    ((count++))
done

echo "Gotowe! Przetworzono $count plików. Wyniki w folderze: $OUTPUT_DIR"
