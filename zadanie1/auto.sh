#! /usr/bin/bash

for i in 50 100 150 200 250 300 350 400 450 500
do
    x=155863
    # echo `python algorytmy/$x.py dane/in_155863_$i.txt out/w$x/$x_$i.txt 5`
    # echo `python czas.py algorytmy/./$x dane/in_155863_$i.txt out/w$x/$x_$i.txt 5`
    
    echo `python new$x.py dane/in_155863_$i.txt newOut/$x_$i.txt 5`
done