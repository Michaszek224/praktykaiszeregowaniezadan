#!/bin/bash

index=$1

if [ -z "$index" ]
then
    echo "Usage: $0 <index>"
    exit 1
fi
echo > wynikiKompresja/$index.txt
for i in {50..500..50}
do
    echo "$i= `cat wyniki/$index/$i.txt | head -n 1`"
    echo "`cat wyniki/$index/$i.txt | head -n 1`" >> wynikiKompresja/$index.txt
done
