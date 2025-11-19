#!/bin/bash

index=$1
rm -rf wyniki/${index}
mkdir -p wyniki/${index}
rm -f czasy/${index}.txt
touch czasy/${index}.txt
if [ -z "$index" ]
then
    echo "Usage: $0 <index>"
    exit 1
fi
for i in {50..500..50}
do
    echo "$i"
    val=$((i/10))
    python czas.py algorytmy/${index}/${index}.py dane/${index}/in_${index}_${i}.txt wyniki/${index}/${i}.txt $val >> czasy/${index}.txt
done
