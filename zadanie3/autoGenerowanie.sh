#!/bin/bash

index=$1
rm -rf wyniki2/${index}
mkdir -p wyniki2/${index}
rm -f wynikiCzasy2/${index}.txt
touch wynikiCzasy2/${index}.txt

if [ -z "$index" ]
then
    echo "Usage: $0 <index>"
    exit 1
fi
for i in {50..500..50}
do
    echo "$i"
    val=$((i/10))
    python czas.py algorytmy2/${index}/${index}.py dane/155863/in_155863_${i}.txt wyniki2/${index}/${i}.txt $val >> wynikiCzasy2/${index}.txt
done
