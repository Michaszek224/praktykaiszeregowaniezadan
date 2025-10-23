#! /usr/bin/bash

for i in 50 100 150 200 250 300 350 400 450 500
do
    x=151893
    # echo `python algorytmy/$x.py dane/in_155863_$i.txt out/w$x/$x_$i.txt 5`
    # echo `python czas.py algorytmy2/$x.py dane/in_155863_$i.txt out/w$x/$x_$i.txt 5`
    
    echo `python czas.py algorytmy2/$x.py dane/in_155863_$i.txt 1_$x.txt 50`
    # echo `python algorytmy2/$x.py dane/in_155863_$i.txt out2/$x/$x_$i.txt 5`
    # echo `sudo algorytmy2/./$x dane/in_155863_$i.txt out2/$x/$x_$i.txt 5`
done