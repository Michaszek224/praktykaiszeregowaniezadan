#!/bin/bash

index=$1
mkdir -p wyniki/${index}
if [ -z "$index" ]
then
    echo "Usage: $0 <index>"
    exit 1
fi
for i in {50..500..50}
do
    echo "$i"
    val=$((i/10))
    python algorytmy/${index}/main.py dane/${index}/in_${index}_${i}.txt wyniki/${index}/${i}.txt $val
    echo "$val"
done
