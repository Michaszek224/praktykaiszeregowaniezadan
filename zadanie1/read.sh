#! /usr/bin/bash

for i in 50 100 150 200 250 300 350 400 450 500
do
    x=155863

    echo "dla $i: $(head -1 out2/$x/$i.txt)"
done