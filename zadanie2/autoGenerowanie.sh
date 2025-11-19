#!/bin/bash

index=$1

if [ -z "$index" ]
then
    echo "Usage: $0 <index>"
    exit 1
fi
for i in {50..500..50}
do
    echo "$i"
    python algorytmy/${index}/main.py dane/${index}/in_${index}_${i}.txt wyniki/${index}/${i}.txt
done
