#!/bin/bash

index=$1
rm -f wynikiKompresja/$index.txt
if [ -z "$index" ]
then
    echo "Usage: $0 <index>"
    exit 1
fi
for i in {50..500..50}
do
    echo "`cat wyniki/$index/$i.txt | head -n 1`"
    echo "`cat wyniki/$index/$i.txt | head -n 1`" >> wynikiKompresja/$index.txt
done
