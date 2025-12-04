#!/bin/bash

index=$1
if [ -z "$index" ]
then
    echo "Usage: $0 <index>"
    exit 1
fi
echo "`cat noweCzasy/${index}.txt`"
