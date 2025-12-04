#!/bin/bash

x=$1

if [ -z "$x" ]; then
    echo "Usage: $0 <index>"
    exit 1
fi
./autoGenerowanie.sh $x
./autoWeryfikacja.sh $x
./czytanie.sh $x
./zamiana.sh wynikiCzasy/${x}.txt noweCzasy/${x}.txt 
./pokaczas.sh $x
