#!/bin/bash

index=$1
rm -f wynikiKompresja2/$index.txt
if [ -z "$index" ]
then
    echo "Usage: $0 <index>"
    exit 1
fi
for i in {50..500..50}
do
    echo "`cat wyniki2/$index/$i.txt | head -n 1`"
    echo "`cat wyniki2/$index/$i.txt | head -n 1`" >> wynikiKompresja2/$index.txt
done
