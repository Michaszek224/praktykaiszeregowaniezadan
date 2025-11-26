#!/bin/bash

# Użycie: ./run_verifier.sh <numer_folderu>
# przykład: ./run_verifier.sh 155863

if [ -z "$1" ]; then
    echo "Użycie: $0 <numer_folderu>"
    exit 1
fi

NUMER="$1"

for ((i=50; i<=500; i+=50)); do
    echo "===> Uruchamiam test: dane/${NUMER}/in_${NUMER}_${i}.txt"
    python weryfikator.py "dane/155863/in_155863_${i}.txt" "wyniki2/${NUMER}/${i}.txt"
done

